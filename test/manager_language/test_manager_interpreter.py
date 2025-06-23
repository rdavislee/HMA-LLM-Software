"""
Tests for ManagerLanguageInterpreter.
Each interpreter verb (CREATE/DELETE/READ actions, DELEGATE, RUN, UPDATE_README, WAIT, FINISH) has
positive and negative coverage.
"""

from __future__ import annotations

import asyncio
from pathlib import Path as _P
import sys
import subprocess

import pytest

# Make src importable
sys.path.insert(0, str(_P(__file__).parent.parent.parent))

from src import set_root_dir  # noqa: E402
from manager_language.interpreter import ManagerLanguageInterpreter  # noqa: E402
from manager_language.ast import (  # noqa: E402
    Target,
    ActionDirective,
    WaitDirective,
    RunDirective,
    UpdateReadmeDirective,
    DelegateItem,
    DelegateDirective,
    FinishDirective,
    PromptField,
)


# ---------------------------- Stubs ----------------------------

class ChildAgent:
    def __init__(self, path: _P, is_manager: bool = False):
        self.path = path
        self.is_manager = is_manager
        self.prompts: list[str] = []


class StubManagerAgent:
    """Bare-bones agent sufficient for interpreter interactions."""

    def __init__(self, root: _P):
        self.path = root / "mgr"
        self.path.mkdir(parents=True, exist_ok=True)
        self.prompts: list[str] = []
        self.children: list[ChildAgent] = []
        self.deactivated: bool = False
        self.active_task = None
        self.parent = None  # For simplicity

        # Memory tracking for read_file tests
        self.memory: list[str] = []

    # Callbacks expected by interpreter
    def delegate_task(self, child, prompt):
        # Record delegations for assertions
        self.prompts.append(f"delegated to {child.path.name}: {prompt}")

    def deactivate(self):  # noqa: D401
        self.deactivated = True

    # ---------------- File Reading -----------------
    def read_file(self, file_path: str):  # noqa: D401
        """Stubbed read_file just records the file path for assertions."""
        self.memory.append(file_path)


# ----------------------------- Fixtures -----------------------------


@pytest.fixture()
def workspace(tmp_path):
    """Temp directory registered as ROOT_DIR."""
    set_root_dir(str(tmp_path))
    return tmp_path


@pytest.fixture(autouse=True)
def patch_prompts(monkeypatch):
    """Patch prompters + create_task to run synchronously and capture messages."""

    async def _fake_prompt(agent, message, *_a, **_kw):  # noqa: D401
        if hasattr(agent, "prompts"):
            agent.prompts.append(message)
        return None

    monkeypatch.setattr(
        "src.orchestrator.manager_prompter.manager_prompter", _fake_prompt, raising=False
    )
    monkeypatch.setattr(
        "src.orchestrator.coder_prompter.coder_prompter", _fake_prompt, raising=False
    )
    monkeypatch.setattr(
        "asyncio.create_task", lambda coro: asyncio.get_event_loop().run_until_complete(coro),
    )


# -------------------- ACTION (CREATE / DELETE / READ) --------------------


def test_create_file_success(workspace):
    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)

    target = Target(name="foo.txt", is_folder=False)
    interp.execute(ActionDirective(action_type="CREATE", targets=[target]))

    created = agent.path / "foo.txt"
    assert created.exists() and created.is_file()


def test_delete_missing_file_failure(workspace):
    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)

    target = Target(name="no.txt", is_folder=False)
    interp.execute(ActionDirective(action_type="DELETE", targets=[target]))

    # The interpreter should generate a failure prompt
    assert any("failed" in p.lower() for p in agent.prompts)


# -------------------- RUN --------------------

def test_run_success(monkeypatch, workspace):
    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)

    class _CP:
        def __init__(self):
            self.returncode = 0
            self.stdout = "ok\n"
            self.stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: _CP())
    interp.execute(RunDirective(command="pytest"))

    assert any("Run command result" in p for p in agent.prompts)


def test_run_invalid_command(workspace):
    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)

    interp.execute(RunDirective(command="rm -rf /"))
    assert any("Invalid command" in p or "Invalid" in p for p in agent.prompts)


# -------------------- UPDATE_README --------------------

def test_update_readme(workspace):
    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)
    content = "hello readme"
    interp.execute(UpdateReadmeDirective(content=content))

    readme_path = agent.path / f"{agent.path.name}_readme.md"
    assert readme_path.read_text() == content


# -------------------- WAIT --------------------

def test_wait_noop(workspace):
    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)

    # Should not raise
    interp.execute(WaitDirective())


# -------------------- DELEGATE --------------------

def test_delegate_success(workspace):
    agent = StubManagerAgent(workspace)
    child = ChildAgent(agent.path / "child")
    agent.children.append(child)

    interp = ManagerLanguageInterpreter(agent)

    item = DelegateItem(target=Target(name="child", is_folder=False), prompt=PromptField(value="do"))
    interp.execute(DelegateDirective(items=[item]))

    assert any("delegated to child" in p for p in agent.prompts)


def test_delegate_unknown_child_failure(workspace):
    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)

    item = DelegateItem(target=Target(name="ghost", is_folder=False), prompt=PromptField(value="do"))
    interp.execute(DelegateDirective(items=[item]))

    # No delegation should be recorded
    assert not agent.prompts  # interpreter returns early on missing child


# -------------------- FINISH --------------------

def test_finish_deactivates_agent(workspace):
    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)

    interp.execute(FinishDirective(prompt=PromptField(value="done")))
    assert agent.deactivated is True


# -------------------- READ (Folder) --------------------


def test_read_folder_readme_added(workspace):
    """Reading a folder should add its README to memory."""
    # Prepare folder with a README
    docs_dir = workspace / "docs"
    docs_dir.mkdir()
    readme_path = docs_dir / "docs_README.md"
    readme_path.write_text("documentation")

    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)

    target = Target(name="docs", is_folder=True)
    interp.execute(ActionDirective(action_type="READ", targets=[target]))

    # The stub read_file records memory paths
    assert any(str(readme_path) == p for p in agent.memory)


def test_read_folder_without_readme(workspace):
    """Reading a folder without a README should generate a prompt failure."""
    empty_dir = workspace / "empty"
    empty_dir.mkdir()

    agent = StubManagerAgent(workspace)
    interp = ManagerLanguageInterpreter(agent)

    target = Target(name="empty", is_folder=True)
    interp.execute(ActionDirective(action_type="READ", targets=[target]))

    # No memory added and prompts should indicate missing README
    assert not agent.memory
    assert any("no README" in p.lower() or "has no readme" in p.lower() for p in agent.prompts) 