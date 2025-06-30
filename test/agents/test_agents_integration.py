import pytest
import asyncio
import subprocess
from pathlib import Path
from unittest.mock import patch
import inspect

# Core imports
from src import set_root_dir
from src.agents.coder_agent import CoderAgent
from src.agents.manager_agent import ManagerAgent
from src.languages.coder_language.parser import parse_directive as parse_coder
from src.languages.coder_language.interpreter import CoderLanguageInterpreter
from src.languages.manager_language.parser import parse_directive as parse_manager
from src.languages.manager_language.interpreter import ManagerLanguageInterpreter


class DummyLLM:
    """Minimal stub for BaseLLMClient interface used by agents."""

    def __init__(self):
        self.last_prompt = None
        self.last_context = None
        self.call_count = 0

    async def generate_response(self, prompt: str, context: str | None = None, **_) -> str:  # type: ignore[name-defined]
        self.call_count += 1
        self.last_prompt = prompt
        self.last_context = context
        return "stub"

    async def generate_structured_response(self, *_, **__) -> dict:  # type: ignore[override]
        return {}


@pytest.fixture()
def workspace(tmp_path):
    """Isolated project root; sets ROOT_DIR for interpreters."""
    set_root_dir(str(tmp_path))
    # Add a project marker so _find_project_root works correctly
    (tmp_path / "requirements.txt").write_text("# test requirements")
    return tmp_path


@pytest.fixture()
def coder_agent(workspace):
    file_path = workspace / "hello.py"
    file_path.write_text("# placeholder\n")
    return CoderAgent(path=str(file_path), llm_client=DummyLLM())


# ---------------------------------------------------------------------------
# Helper patches so that orchestrator callbacks do not run network code
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_prompters(monkeypatch):
    async def _noop(*_, **__):
        return None

    monkeypatch.setattr("src.orchestrator.coder_prompter.coder_prompter", _noop, raising=False)
    monkeypatch.setattr("src.orchestrator.manager_prompter.manager_prompter", _noop, raising=False)
    # Ensure asyncio.create_task executes immediately in tests for determinism
    def _create_task(coro):
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if inspect.iscoroutine(coro):
            return loop.run_until_complete(coro)
        # if not coroutine just ignore to avoid TypeError
        return None

    monkeypatch.setattr("asyncio.create_task", _create_task)


# ---------------------------------------------------------------------------
# CoderAgent – prompt driven tests via CoderLanguageInterpreter
# ---------------------------------------------------------------------------


def test_coder_change_and_finish(coder_agent, workspace):
    """Coder CHANGE directive alters own file; FINISH deactivates agent."""
    change_content = 'print("hi")\n'
    # Escape inner quotes for the grammar
    change_prompt = 'CHANGE CONTENT = "print(\\"hi\\")\\n"'
    finish_prompt = 'FINISH PROMPT = "done"'

    # Execute CHANGE
    dir_change = parse_coder(change_prompt)
    CoderLanguageInterpreter(base_path=workspace, agent=coder_agent, own_file=coder_agent.path.name).execute(dir_change)
    assert Path(coder_agent.path).read_text() == change_content

    # Agent should still be active (not activated yet), activate manually to test FINISH
    coder_agent.is_active = True
    dir_finish = parse_coder(finish_prompt)
    CoderLanguageInterpreter(base_path=workspace, agent=coder_agent, own_file=coder_agent.path.name).execute(dir_finish)
    assert not coder_agent.is_active  # deactivated


def test_coder_read_success(coder_agent, workspace):
    target = workspace / "readme.md"
    target.write_text("hello")

    read_prompt = 'READ "readme.md"'
    dir_read = parse_coder(read_prompt)
    CoderLanguageInterpreter(base_path=workspace, agent=coder_agent, own_file=coder_agent.path.name).execute(dir_read)

    # memory should now include file
    assert "readme.md" in coder_agent.memory
    assert coder_agent.memory["readme.md"] == target.resolve()


# ---------------------------------------------------------------------------
# ManagerAgent – prompt driven tests via ManagerLanguageInterpreter
# ---------------------------------------------------------------------------


def test_manager_delegate_to_child(coder_agent, workspace):
    set_root_dir(str(workspace))
    dir_path = workspace / "pkg"
    dir_path.mkdir()
    coder_agent.parent = None
    manager_agent = ManagerAgent(path=str(dir_path), children=[coder_agent], llm_client=DummyLLM())
    coder_agent.parent = manager_agent
    delegate_prompt = 'DELEGATE file "' + Path(coder_agent.path).name + '" PROMPT = "Implement foo"'
    directive = parse_manager(delegate_prompt)
    ManagerLanguageInterpreter(agent=manager_agent).execute(directive)
    assert coder_agent in manager_agent.active_children
    assert manager_agent.active_children[coder_agent] == "Implement foo"


def test_manager_create_delete_read_files(coder_agent, workspace):
    set_root_dir(str(workspace))
    dir_path = workspace / "pkg"
    dir_path.mkdir()
    coder_agent.parent = None
    manager_agent = ManagerAgent(path=str(dir_path), children=[coder_agent], llm_client=DummyLLM())
    coder_agent.parent = manager_agent
    # CREATE file within manager's scope
    create_str = 'CREATE file "pkg/data.txt"'
    ManagerLanguageInterpreter(agent=manager_agent).execute(parse_manager(create_str))
    created_path = Path(manager_agent.path) / "data.txt"
    assert created_path.exists()
    # READ file (adds to memory)
    read_str = 'READ file "pkg/data.txt"'
    ManagerLanguageInterpreter(agent=manager_agent).execute(parse_manager(read_str))
    assert "data.txt" in manager_agent.memory
    # DELETE file
    delete_str = 'DELETE file "pkg/data.txt"'
    ManagerLanguageInterpreter(agent=manager_agent).execute(parse_manager(delete_str))
    assert not created_path.exists()


def test_manager_create_duplicate_fails(coder_agent, workspace):
    set_root_dir(str(workspace))
    dir_path = workspace / "pkg"
    dir_path.mkdir()
    coder_agent.parent = None
    manager_agent = ManagerAgent(path=str(dir_path), children=[coder_agent], llm_client=DummyLLM())
    coder_agent.parent = manager_agent
    # first creation within manager's scope
    ManagerLanguageInterpreter(agent=manager_agent).execute(parse_manager('CREATE file "pkg/dup.txt"'))
    # second creation (duplicate)
    ManagerLanguageInterpreter(agent=manager_agent).execute(parse_manager('CREATE file "pkg/dup.txt"'))
    # file still exists
    assert (Path(manager_agent.path) / 'dup.txt').exists()


def test_manager_delete_missing_fails(coder_agent, workspace):
    set_root_dir(str(workspace))
    dir_path = workspace / "pkg"
    dir_path.mkdir()
    coder_agent.parent = None
    manager_agent = ManagerAgent(path=str(dir_path), children=[coder_agent], llm_client=DummyLLM())
    coder_agent.parent = manager_agent
    missing_path = Path(manager_agent.path) / 'ghost.txt'
    assert not missing_path.exists()
    # Should not raise - trying to delete a file within manager's scope
    ManagerLanguageInterpreter(agent=manager_agent).execute(parse_manager('DELETE file "pkg/ghost.txt"'))
    assert not missing_path.exists()


def test_manager_deactivate_with_children_error(coder_agent):
    from src.messages.protocol import Task, TaskMessage, MessageType
    task = Task(task_id='t', task_string='do')
    tm = TaskMessage(message_type=MessageType.DELEGATION, sender_id='p', recipient_id='m', message_id='mid', task=task)
    coder_agent.activate(tm)
    # Inject fake parent with children attribute
    class DummyParent:
        def __init__(self, children):
            self.children = children
    dummy_parent = DummyParent([coder_agent])
    coder_agent.parent = dummy_parent
    # Inject fake active child
    coder_agent.active_children = {coder_agent.parent.children[0]: 'something'}
    with pytest.raises(RuntimeError):
        coder_agent.deactivate()
    # cleanup
    coder_agent.active_children = {}
    coder_agent.deactivate()


# ---------------------------------------------------------------------------
# BaseAgent – minimal behaviour tests (non prompt)
# ---------------------------------------------------------------------------


def test_base_agent_activation_deactivation(coder_agent):
    """activate + deactivate workflow without children."""
    from src.messages.protocol import Task, TaskMessage, MessageType
    task = Task(task_id="1", task_string="demo")
    msg = TaskMessage(message_type=MessageType.DELEGATION, sender_id="p", recipient_id="c", message_id="m", task=task)

    coder_agent.activate(msg)
    assert coder_agent.is_active
    coder_agent.deactivate()
    assert not coder_agent.is_active


def test_base_agent_read_and_memory(coder_agent, workspace):
    file_ = workspace / "x.txt"
    file_.write_text("yo")
    coder_agent.read_file(str(file_))
    assert "x.txt" in coder_agent.memory
    contents = coder_agent._get_memory_contents()
    assert contents["x.txt"] == "yo" 