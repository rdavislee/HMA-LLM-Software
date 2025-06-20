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

from src.coder_language.interpreter import CoderLanguageInterpreter  # noqa: E402
from src.coder_language.ast import (  # noqa: E402
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

    # Hooks used by interpreter
    def read_file(self, path: str):
        self.read_files.append(path)

    async def deactivate(self):
        self.deactivated = True


# ---------------------- Fixtures ----------------------

@pytest.fixture()
def workspace(tmp_path):
    """Isolated temp directory for file operations."""
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

    CoderLanguageInterpreter(workspace, agent=agent, own_file="x.py").execute(
        ReadDirective(filename="a.txt")
    )

    assert agent.read_files == [str(f)]
    assert any("READ succeeded" in p for p in agent.prompts)


def test_read_failure(workspace):
    agent = StubAgent()
    CoderLanguageInterpreter(workspace, agent=agent, own_file="x.py").execute(
        ReadDirective(filename="missing.txt")
    )

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

    CoderLanguageInterpreter(workspace, agent=agent, own_file="x.py").execute(
        RunDirective(command="pytest")
    )
    assert any("RUN succeeded" in p for p in agent.prompts)


def test_run_invalid_command(workspace):
    agent = StubAgent()
    CoderLanguageInterpreter(workspace, agent=agent, own_file="x.py").execute(
        RunDirective(command="sudo rm -rf /")
    )
    assert any("Invalid command" in p for p in agent.prompts)


def test_run_failure(monkeypatch, workspace):
    agent = StubAgent()

    class _CP:
        def __init__(self):
            self.returncode = 1
            self.stdout = ""
            self.stderr = "boom"

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: _CP())

    CoderLanguageInterpreter(workspace, agent=agent, own_file="x.py").execute(
        RunDirective(command="pytest")
    )
    assert any("RUN failed" in p for p in agent.prompts)


# ---------------------- CHANGE ----------------------

def test_change_success(workspace):
    agent = StubAgent()
    content = "print('x')\n"
    CoderLanguageInterpreter(workspace, agent=agent, own_file="code.py").execute(
        ChangeDirective(content=content)
    )
    changed = workspace / "code.py"
    assert changed.read_text() == content
    assert any("CHANGE succeeded" in p for p in agent.prompts)


def test_change_disallowed(workspace):
    agent = StubAgent()
    CoderLanguageInterpreter(workspace, agent=agent, own_file=None).execute(
        ChangeDirective(content="bad")
    )
    assert list(workspace.iterdir()) == []
    assert any("CHANGE failed" in p for p in agent.prompts)


# ---------------------- FINISH ----------------------

def test_finish(workspace):
    agent = StubAgent()
    CoderLanguageInterpreter(workspace, agent=agent, own_file="x.py").execute(
        FinishDirective(prompt=PromptField(value="done"))
    )
    assert agent.deactivated
    assert any("done" in p for p in agent.prompts) 