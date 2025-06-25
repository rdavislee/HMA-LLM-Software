from __future__ import annotations

"""Project initializer utilities.

This module provides a single convenience function – ``initialize_agents`` – that
turns an *existing* directory structure into an in-memory agent hierarchy that
can immediately be used by the rest of the system.

Usage example
-------------
>>> from src.initializer import initialize_agents
>>> root_agent, all_agents = initialize_agents("/path/to/project")

The function performs the following tasks:
1. Sets ``src.ROOT_DIR`` to the provided path (using ``src.set_root_dir``).
2. Recursively walks the directory tree.
   • For **every directory** it creates a :class:`~src.agents.manager_agent.ManagerAgent`.
     The directory's personal file is expected to be ``<folder_name>_README.md``. If the
     README is absent it is created automatically (empty file).
   • For **every file** it creates a :class:`~src.agents.coder_agent.CoderAgent` – except
     the manager READMEs which are already owned by the corresponding directory manager.
3. Correctly wires **parent / child** relationships between the agents.
4. Returns **both** the root :class:`ManagerAgent` and a flat ``dict`` mapping
   ``Path`` objects to their associated agents for optional convenience.
"""

from pathlib import Path
from typing import Dict, Tuple, Optional, List

from src import set_root_dir, ROOT_DIR
from src.agents.base_agent import BaseAgent
from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.llm.base import BaseLLMClient

__all__ = ["initialize_agents"]


IGNORED_DIR_NAMES = {".git", "__pycache__", ".mypy_cache", ".pytest_cache"}
IGNORED_FILE_NAMES = {"__init__.py"}  # can be extended


def _ensure_readme(dir_path: Path) -> Path:
    """Ensure the manager README exists for *dir_path*.

    Returns the *Path* to the README (newly created or pre-existing).
    """
    readme_name = f"{dir_path.name}_README.md"
    readme_path = dir_path / readme_name
    if not readme_path.exists():
        readme_path.touch()
    return readme_path


def _build_manager(
    dir_path: Path,
    parent: Optional[ManagerAgent],
    llm_client: Optional[BaseLLMClient],
    max_context_size: int,
    agent_lookup: Dict[Path, "BaseAgent"],
) -> ManagerAgent:
    """Recursively construct agents starting at *dir_path* (which **must** be a directory)."""
    # Ensure README exists *before* constructing the agent so that BaseAgent picks it up.
    _ensure_readme(dir_path)

    manager = ManagerAgent(
        path=str(dir_path),
        parent=parent,
        llm_client=llm_client,
        max_content_size=max_context_size,
    )
    agent_lookup[dir_path] = manager

    # First process sub-directories.
    for child_dir in sorted(p for p in dir_path.iterdir() if p.is_dir() and p.name not in IGNORED_DIR_NAMES):
        child_manager = _build_manager(
            child_dir,
            parent=manager,
            llm_client=llm_client,
            max_context_size=max_context_size,
            agent_lookup=agent_lookup,
        )
        manager.children.append(child_manager)

    # Then process files.
    for file_path in sorted(p for p in dir_path.iterdir() if p.is_file()):
        # Skip README – it is personal file for the manager.
        if file_path.name == f"{dir_path.name}_README.md":
            continue
        if file_path.name in IGNORED_FILE_NAMES:
            continue
        coder = CoderAgent(
            path=str(file_path),
            parent=manager,
            llm_client=llm_client,
            max_context_size=max_context_size,
        )
        agent_lookup[file_path] = coder
        manager.children.append(coder)

    return manager


def initialize_agents(
    root_directory: str | Path,
    *,
    llm_client: Optional[BaseLLMClient] = None,
    max_context_size: int = 8000,
) -> Tuple[ManagerAgent, Dict[Path, "BaseAgent"]]:
    """Initialize the full agent hierarchy for *root_directory*.

    Parameters
    ----------
    root_directory:
        Path to the project root that will become ``src.ROOT_DIR``.
    llm_client:
        Optional LLM client instance to share between agents (can be *None* – the
        orchestrator may inject one later).
    max_context_size:
        Maximum context tokens for each agent's ``BaseAgent`` constructor.

    Returns
    -------
    (root_manager, agent_lookup):
        *root_manager* is the :class:`ManagerAgent` for the repository root.
        *agent_lookup* contains **all** agents indexed by their absolute :class:`Path`.
    """
    root_path = Path(root_directory).resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise ValueError(f"Provided root_directory '{root_directory}' is not an existing directory")

    # Set global ROOT_DIR so that all future agents refer to correct path.
    set_root_dir(str(root_path))

    # Maintain lookup so that callers can easily retrieve a particular agent if necessary.
    agent_lookup: Dict[Path, "BaseAgent"] = {}

    root_manager = _build_manager(
        root_path,
        parent=None,
        llm_client=llm_client,
        max_context_size=max_context_size,
        agent_lookup=agent_lookup,
    )

    return root_manager, agent_lookup


# ---------------------------------------------------------------------------
# Prompt execution helpers
# ---------------------------------------------------------------------------
import asyncio
import uuid
import time

from src.messages.protocol import Task, TaskMessage, MessageType
from src.orchestrator.manager_prompter import manager_prompter


async def _async_execute_root_prompt(root_agent: ManagerAgent, prompt: str) -> str:
    """Helper coroutine that activates *root_agent* with *prompt* and returns its response."""
    # Build a synthetic Task/TaskMessage so that the root agent sees a real task.
    task = Task(task_id=str(uuid.uuid4()), task_string=prompt)
    task_message = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender_id="USER",
        recipient_id=str(root_agent.path),
        message_id=str(uuid.uuid4()),
        task=task,
    )

    # Kick-off the manager prompter pipeline.
    await manager_prompter(root_agent, prompt, task_message)

    # Wait until root_agent has completed processing. We consider it done when:
    #   • It is no longer stalled, AND
    #   • Its prompt_queue is empty, AND
    #   • All children have completed (active_children empty)
    while True:
        stalled = getattr(root_agent, "stall", False)
        queue_empty = not getattr(root_agent, "prompt_queue", [])
        children_active = bool(getattr(root_agent, "active_children", {}))
        finished = getattr(root_agent, "final_result", None)
        if (not stalled and queue_empty and not children_active) or finished is not None:
            break
        await asyncio.sleep(0.1)

    # Prefer explicit final_result if set by manager_language
    final_result = getattr(root_agent, "final_result", None)
    if final_result is not None:
        return final_result

    if root_agent.context:
        return root_agent.context[-1].response
    return ""


def execute_root_prompt(root_agent: ManagerAgent, prompt: str) -> str:
    """Synchronously execute *prompt* against the *root_agent* hierarchy and return its response."""
    return asyncio.run(_async_execute_root_prompt(root_agent, prompt))


def initialize_and_run(
    root_directory: str | Path,
    initial_prompt: str,
    *,
    llm_client: Optional[BaseLLMClient] = None,
    max_context_size: int = 8000,
) -> str:
    """Full convenience shortcut: build agents then run *initial_prompt*.

    Returns the root agent's textual response.
    """
    root_agent, _ = initialize_agents(
        root_directory,
        llm_client=llm_client,
        max_context_size=max_context_size,
    )

    return execute_root_prompt(root_agent, initial_prompt) 