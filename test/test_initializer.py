import asyncio
from pathlib import Path
import types

import pytest

from src.initializer import (
    initialize_agents,
    execute_root_prompt,
    initialize_and_run,
)
from src.agents.manager_agent import ManagerAgent


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_dir_structure(tmp_path: Path):
    """Create a temporary nested directory structure for testing."""
    # root/
    #   a.py
    #   sub/
    #       b.py
    root = tmp_path
    (root / "a.py").write_text("print('a')\n")
    sub = root / "sub"
    sub.mkdir()
    (sub / "b.py").write_text("print('b')\n")
    return root


# ---------------------------------------------------------------------------
# Tests for initialize_agents
# ---------------------------------------------------------------------------

def test_initialize_agents_success(sample_dir_structure: Path):
    root_agent, lookup = initialize_agents(sample_dir_structure)

    # ROOT_DIR should be set inside initializer – verify mapping.
    from src import ROOT_DIR
    assert ROOT_DIR == sample_dir_structure.resolve()

    # The root agent must be a ManagerAgent managing the root path.
    assert isinstance(root_agent, ManagerAgent)
    assert Path(root_agent.path) == sample_dir_structure.resolve()

    # README files should exist for each directory.
    assert (sample_dir_structure / f"{sample_dir_structure.name}_README.md").exists()
    assert (sample_dir_structure / "sub" / "sub_README.md").exists()

    # Agent lookup should include all created paths.
    expected_paths = {
        sample_dir_structure.resolve(),
        (sample_dir_structure / "a.py").resolve(),
        (sample_dir_structure / "sub").resolve(),
        (sample_dir_structure / "sub" / "b.py").resolve(),
    }
    assert expected_paths.issubset(set(lookup.keys()))


def test_initialize_agents_invalid_path(tmp_path: Path):
    # Provide non-existent path.
    non_existent = tmp_path / "does_not_exist"
    with pytest.raises(ValueError):
        initialize_agents(non_existent)


# ---------------------------------------------------------------------------
# Tests for execute_root_prompt & initialize_and_run
# ---------------------------------------------------------------------------

def _patch_manager_api(monkeypatch):
    """Patch ManagerAgent.api_call so that it immediately finishes with a known result."""

    async def _fake_api(self):  # noqa: D401
        # Simulate a FINISH directive result propagation.
        self.final_result = "SIMULATED_RESULT"
        self.stall = False
        self.prompt_queue.clear()
        return None

    monkeypatch.setattr(ManagerAgent, "api_call", _fake_api, raising=True)


def test_execute_root_prompt_returns_final_result(sample_dir_structure: Path, monkeypatch):
    _patch_manager_api(monkeypatch)
    root_agent, _ = initialize_agents(sample_dir_structure)
    result = execute_root_prompt(root_agent, "Do something")
    assert result == "SIMULATED_RESULT"


def test_initialize_and_run_convenience(sample_dir_structure: Path, monkeypatch):
    _patch_manager_api(monkeypatch)
    result = initialize_and_run(sample_dir_structure, "Kick off")
    assert result == "SIMULATED_RESULT" 