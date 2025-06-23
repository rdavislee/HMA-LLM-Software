import asyncio
from pathlib import Path
from typing import Optional

import pytest

from src.agents.base_agent import BaseAgent, ContextEntry
from src.messages.protocol import TaskMessage, Task, MessageType


class DummyLLMClient:
    """A no-op stub for BaseLLMClient that simply echoes prompts."""

    async def generate(self, *args, **kwargs):
        return "dummy-response"


class DummyAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing purposes."""

    async def api_call(self) -> None:  # pragma: no cover – behaviour verified via side-effects in tests
        # Intentionally minimal: emulate immediate completion of queued prompt
        if self.prompt_queue:
            self.prompt_queue.pop(0)
            # Add a dummy context entry so that we can verify context growth in tests
            self.context.append(ContextEntry(prompt="dummy", response="dummy-response"))


@pytest.fixture()
def tmp_file(tmp_path: Path) -> Path:
    """Create a temporary file and return its path."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello world", encoding="utf-8")
    return file_path


@pytest.fixture()
def coder_agent(tmp_file: Path) -> DummyAgent:
    # Treat the temporary file as the agent's managed file (coder agent)
    return DummyAgent(path=str(tmp_file))


@pytest.fixture()
def manager_agent(tmp_path: Path) -> DummyAgent:
    # Treat the temporary directory as a manager agent
    return DummyAgent(path=str(tmp_path))


# --------------------------- _set_personal_file / role checks ---------------------------

def test_set_personal_file_coder(coder_agent: DummyAgent, tmp_file: Path):
    assert coder_agent.is_coder is True
    assert coder_agent.is_manager is False
    # personal_file should be exactly the managed file
    assert coder_agent.personal_file == tmp_file.resolve()
    # Memory should include the personal file name
    assert tmp_file.name in coder_agent.memory


def test_set_personal_file_manager(manager_agent: DummyAgent, tmp_path: Path):
    assert manager_agent.is_manager is True
    assert manager_agent.is_coder is False
    expected_readme = tmp_path / f"{tmp_path.name}_README.md"
    assert manager_agent.personal_file == expected_readme
    assert expected_readme.name in manager_agent.memory


# --------------------------- activate / deactivate ---------------------------

@pytest.mark.asyncio
async def test_activate_and_deactivate(coder_agent: DummyAgent):
    task = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender_id="tester",
        recipient_id="coder",
        message_id="1",
        task=Task(task_id="t1", task_string="do something")
    )

    # Activate
    coder_agent.activate(task)
    assert coder_agent.is_active is True
    assert coder_agent.active_task == task

    # Deactivate
    coder_agent.deactivate()
    assert coder_agent.is_active is False
    assert coder_agent.active_task is None
    assert coder_agent.memory == {}
    assert coder_agent.context == []
    assert coder_agent.prompt_queue == []


def test_activate_twice_raises(coder_agent: DummyAgent):
    fake_task = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender_id="x",
        recipient_id="y",
        message_id="2",
        task=Task(task_id="t", task_string="foo")
    )
    coder_agent.activate(fake_task)
    with pytest.raises(RuntimeError):
        coder_agent.activate(fake_task)  # activating again should fail


def test_deactivate_with_active_children(tmp_path: Path):
    manager = DummyAgent(path=str(tmp_path))
    manager.active_children = {"child": object()}  # simulate active children
    with pytest.raises(RuntimeError):
        manager.deactivate()


# --------------------------- process_task ---------------------------

@pytest.mark.asyncio
async def test_process_task_calls_api(coder_agent: DummyAgent):
    # Patch api_call to track invocation
    called = False

    async def fake_api():
        nonlocal called
        called = True

    coder_agent.api_call = fake_api  # type: ignore
    await coder_agent.process_task("prompt")
    assert "prompt" in coder_agent.prompt_queue
    assert called is True


@pytest.mark.asyncio
async def test_process_task_stalled_does_not_call_api(coder_agent: DummyAgent):
    called = False

    async def fake_api():
        nonlocal called
        called = True

    coder_agent.api_call = fake_api  # type: ignore
    coder_agent.stall = True
    await coder_agent.process_task("prompt")
    assert called is False


# --------------------------- read_file & _get_memory_contents ---------------------------

def test_read_file_and_get_memory(coder_agent: DummyAgent, tmp_file: Path):
    # Create another file to read
    other_file = tmp_file.parent / "extra.txt"
    other_file.write_text("second", encoding="utf-8")

    coder_agent.read_file(str(other_file))
    contents = coder_agent._get_memory_contents()
    assert other_file.name in contents and contents[other_file.name] == "second"
    # Missing files should produce a placeholder entry
    coder_agent.read_file(str(tmp_file.parent / "missing.txt"))
    missing_contents = coder_agent._get_memory_contents()
    assert "missing.txt" in missing_contents
    assert missing_contents["missing.txt"].startswith("[File does not exist")


# --------------------------- get_status / __repr__ ---------------------------

def test_get_status_and_repr(coder_agent: DummyAgent):
    status = coder_agent.get_status()
    assert status["agent_type"] == "coder"
    assert "path" in status
    # __repr__ should include word 'Coder'
    assert "Coder" in repr(coder_agent)


# --------------------------- _get_codebase_structure_string ---------------------------

def test_codebase_structure_string_non_empty(coder_agent: DummyAgent):
    structure = coder_agent._get_codebase_structure_string()
    # Should include the root directory name and at least one newline
    assert structure
    assert "\n" in structure 