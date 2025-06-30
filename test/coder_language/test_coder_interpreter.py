"""
Tests for CoderLanguageInterpreter.
Each test partition matches an interpreter operation and asserts both success and failure behaviours.
"""

from __future__ import annotations

import asyncio
from pathlib import Path as _P
import subprocess
import sys

import pytest

# Ensure the src package is importable
sys.path.insert(0, str(_P(__file__).parent.parent.parent))

from src import set_root_dir  # noqa: E402
from src.languages.coder_language.interpreter import CoderLanguageInterpreter, execute_directive  # noqa: E402
from src.languages.coder_language.ast import (  # noqa: E402
    ReadDirective,
    RunDirective,
    ChangeDirective,
    FinishDirective,
    PromptField,
)


class StubAgent:
    """Minimal agent capturing interpreter callbacks."""

    def __init__(self):
        self.read_files: list[str] = []
        self.prompts: list[str] = []
        self.deactivated: bool = False
        self.prompt_queue: list[str] = []

    # Hooks used by interpreter
    def read_file(self, path: str):
        self.read_files.append(path)

    def deactivate(self):
        self.deactivated = True

    async def api_call(self):
        """Process prompt queue for testing."""
        while self.prompt_queue:
            prompt = self.prompt_queue.pop(0)
            self.prompts.append(prompt)


# ---------------------- Fixtures ----------------------

@pytest.fixture()
def workspace(tmp_path):
    """Isolated temp directory for file operations."""
    set_root_dir(str(tmp_path))  # Set the root directory for the interpreter
    # Add a project marker so _find_project_root works correctly
    (tmp_path / "requirements.txt").write_text("# test requirements")
    return tmp_path


@pytest.fixture(autouse=True)
def patch_async(monkeypatch):
    """Patch prompt + asyncio.create_task to execute synchronously."""

    async def _fake_prompt(agent, msg, *_a, **_kw):
        if hasattr(agent, "prompts"):
            agent.prompts.append(msg)
        return None

    monkeypatch.setattr(
        "src.orchestrator.coder_prompter.coder_prompter", _fake_prompt, raising=False
    )
    monkeypatch.setattr(
        "asyncio.create_task", lambda coro: asyncio.get_event_loop().run_until_complete(coro)
    )


# ---------------------- READ ----------------------

def test_read_success(workspace):
    agent = StubAgent()
    f = workspace / "a.txt"
    f.write_text("hi")

    execute_directive('READ "a.txt"', base_path=str(workspace), agent=agent, own_file="x.py")

    assert agent.read_files == [str(f)]
    assert any("READ succeeded" in p for p in agent.prompts)


def test_read_failure(workspace):
    agent = StubAgent()
    execute_directive('READ "missing.txt"', base_path=str(workspace), agent=agent, own_file="x.py")

    assert agent.read_files == []
    assert any("READ failed" in p for p in agent.prompts)


# ---------------------- RUN ----------------------

def test_run_success(monkeypatch, workspace):
    agent = StubAgent()

    class _CP:
        def __init__(self):
            self.returncode = 0
            self.stdout = "ok\n"
            self.stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: _CP())

    execute_directive('RUN "pytest"', base_path=str(workspace), agent=agent, own_file="x.py")
    assert any("RUN succeeded" in p for p in agent.prompts)


def test_run_invalid_command(workspace):
    agent = StubAgent()
    execute_directive('RUN "sudo rm -rf /"', base_path=str(workspace), agent=agent, own_file="x.py")
    assert any("Invalid command" in p for p in agent.prompts)


def test_run_failure(monkeypatch, workspace):
    agent = StubAgent()

    class _CP:
        def __init__(self):
            self.returncode = 1
            self.stdout = ""
            self.stderr = "boom"

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: _CP())

    execute_directive('RUN "pytest"', base_path=str(workspace), agent=agent, own_file="x.py")
    assert any("RUN failed" in p for p in agent.prompts)


# ---------------------- CHANGE ----------------------

def test_change_success(workspace):
    agent = StubAgent()
    content = "print('x')\n"
    execute_directive('CHANGE CONTENT = "print(\'x\')\\n"', base_path=str(workspace), agent=agent, own_file="code.py")
    changed = workspace / "code.py"
    assert changed.read_text() == content
    assert any("CHANGE succeeded" in p for p in agent.prompts)


def test_change_disallowed(workspace):
    agent = StubAgent()
    execute_directive('CHANGE CONTENT = "bad"', base_path=str(workspace), agent=agent, own_file=None)
    assert list(workspace.iterdir()) == [workspace / "requirements.txt"]  # Only the project marker file
    assert any("CHANGE failed" in p for p in agent.prompts)


# ---------------------- FINISH ----------------------

def test_finish(workspace):
    agent = StubAgent()
    execute_directive('FINISH PROMPT = "done"', base_path=str(workspace), agent=agent, own_file="x.py")
    assert agent.deactivated
    assert hasattr(agent, "final_result") and agent.final_result == "done" 