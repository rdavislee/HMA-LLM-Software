from __future__ import annotations

"""Project initializer for brand-new codebases.

This module exposes a single public coroutine – **initialize_new_project** – that
bootstraps an empty directory into a fully-scaffolded project using an
interactive, three-phase workflow controlled by a master agent:

1. **Product Understanding**: the master agent asks clarifying questions until
   the human approves moving forward.
2. **Structure Stage**: the master agent issues RUN commands to create the
   directory & file scaffold that will host the implementation.
3. **Implementation**: the master agent spawns the full agent hierarchy and
   delegates work to implement, test, and verify the project.

The helper utilities in this file (_ensure_readme, _build_manager, and
_bootstrap_language_environment) exist solely to support the new-project flow.
"""

from pathlib import Path
from typing import Dict, Tuple, Optional, Callable, Awaitable, Union
import subprocess
import asyncio
import time

from src import set_root_dir, ROOT_DIR
from src.agents.base_agent import BaseAgent
from src.agents.manager_agent import ManagerAgent
from src.agents.master_agent import MasterAgent
from src.agents.coder_agent import CoderAgent
from src.llm.base import BaseLLMClient
from src.config import Language, set_global_language, get_global_language
from src.messages.protocol import Task, TaskMessage, MessageType
from src.orchestrator.master_prompter import master_prompter

__all__ = ["initialize_new_project"]

# ---------------------------------------------------------------------------
# Constants & helper functions
# ---------------------------------------------------------------------------

IGNORED_DIR_NAMES = {".git", "__pycache__", ".mypy_cache", ".pytest_cache"}
IGNORED_FILE_NAMES = {"__init__.py"}


def _ensure_readme(dir_path: Path) -> Path:
    """Ensure a README exists for *dir_path* and return its path."""
    readme_name = f"{dir_path.name}_README.md"
    readme_path = dir_path / readme_name
    if not readme_path.exists():
        readme_path.touch()
    return readme_path


def _build_manager(
    dir_path: Path,
    parent: Optional[Union["ManagerAgent", "MasterAgent"]],
    llm_client: Optional[BaseLLMClient],
    max_context_size: int,
    agent_lookup: Dict[Path, "BaseAgent"],
) -> ManagerAgent:
    """Recursively construct agents starting at *dir_path*."""
    _ensure_readme(dir_path)

    manager = ManagerAgent(
        path=str(dir_path),
        parent=parent,
        llm_client=llm_client,
        max_content_size=max_context_size,
    )
    agent_lookup[dir_path] = manager

    # First, process sub-directories.
    for child_dir in sorted(
        p for p in dir_path.iterdir() if p.is_dir() and p.name not in IGNORED_DIR_NAMES
    ):
        child_manager = _build_manager(
            child_dir,
            parent=manager,
            llm_client=llm_client,
            max_context_size=max_context_size,
            agent_lookup=agent_lookup,
        )
        manager.children.append(child_manager)

    # Then, process regular files.
    for file_path in sorted(p for p in dir_path.iterdir() if p.is_file()):
        if file_path.name == f"{dir_path.name}_README.md":
            continue  # Personal file for the directory manager
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


# ---------------------------------------------------------------------------
# Public API – *initialize_new_project*
# ---------------------------------------------------------------------------

async def initialize_new_project(
    root_directory: str | Path,
    initial_prompt: str,
    human_interface_fn: Callable[[str], Awaitable[str]],
    *,
    language: Language = Language.TYPESCRIPT,
    master_llm_client: Optional[BaseLLMClient] = None,
    base_llm_client: Optional[BaseLLMClient] = None,
    max_context_size: int = 80000,
) -> Tuple["MasterAgent", ManagerAgent, Dict[Path, "BaseAgent"]]:
    """Interactive three-phase bootstrapping for brand-new projects.

    The coroutine drives a full project lifecycle:
    1. *Product understanding* – clarify requirements with the user.
    2. *Structure stage* – create the optimal directory & file scaffold via RUN commands.
    3. *Implementation* – build agent hierarchy and coordinate implementation.
    """

    root_path = Path(root_directory).resolve()
    if not root_path.exists():
        root_path.mkdir(parents=True, exist_ok=True)

    # Guard against accidental use on non-empty directories.
    existing_items = [item for item in root_path.iterdir() if not item.name.startswith(".")]
    if existing_items:
        raise ValueError(
            f"Directory {root_directory} is not empty. Found: {[item.name for item in existing_items]}"
        )

    # Global configuration & language toolchain.
    set_root_dir(str(root_path))
    set_global_language(language)

    # Workspace scratch dir for tester agents.
    scratch_pads_dir = root_path / "scratch_pads"
    scratch_pads_dir.mkdir(exist_ok=True)

    # Master agent orchestrates the process; manager/coder agents are created later.
    master_agent = MasterAgent(
        llm_client=master_llm_client,
        max_context_size=max_context_size,
    )

    # Bidirectional handshake between master agent FINISH directives and this initializer.
    completion_event: asyncio.Event = asyncio.Event()
    completion_data: Dict[str, Optional[str | asyncio.Event | Dict[str, str]]] = {"message": None}

    async def phase_communication_fn(completion_message: str) -> str:  # noqa: D401 – simple lambda-like helper
        completion_data["message"] = completion_message
        completion_event.set()
        response_event: asyncio.Event = asyncio.Event()
        response_holder: Dict[str, str] = {"response": ""}
        completion_data["response_event"] = response_event
        completion_data["response_holder"] = response_holder
        await response_event.wait()
        return response_holder["response"]

    master_agent.set_human_interface_fn(phase_communication_fn)

    # Persistent project documentation.
    (root_path / "documentation.md").write_text(
        f"# Project Documentation\n\nInitial Request: {initial_prompt}\n\n"
    )

    # ---------------------------- Phase 1 – Product understanding ----------------------------
    print("[Phase 1] Starting product understanding phase…")
    language_name = str(get_global_language().name) if hasattr(get_global_language(), 'name') else str(get_global_language())
    phase1_task = Task(
        task_id=f"phase1_{int(time.time())}",
        task_string=(
            f"[LANGUAGE: {language_name}] "
            "Phase 1: Product Understanding – Learn as much as possible about the human's "
            f"requirements. Initial idea: {initial_prompt}"
        ),
    )
    phase1_task_msg = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender="HUMAN",
        recipient=master_agent,
        message_id=f"phase1_init_{int(time.time())}",
        task=phase1_task,
    )

    await master_prompter(master_agent, initial_prompt, phase1_task_msg)

    # Approval loop – wait until the human types "Approved".
    while True:
        await completion_event.wait()
        completion_event.clear()
        completion_message = completion_data["message"]
        print(f"[Phase 1] Master completed with: {completion_message}")
        approval = await human_interface_fn(
            "Type 'Approved' to move to Phase 2 (Structure), or provide additional feedback:"
        )
        if approval.strip().lower() == "approved":
            completion_data["response_holder"]["response"] = "approved"
            completion_data["response_event"].set()
            break
        # Otherwise send additional feedback and continue phase 1.
        completion_data["response_holder"]["response"] = (
            f"Additional feedback from human: {approval}. Continue product understanding and use FINISH when ready."
        )
        completion_data["response_event"].set()

    # ---------------------------- Phase 2 – Structure stage ----------------------------
    print("[Phase 2] Starting structure stage…")
    language_name = str(get_global_language().name) if hasattr(get_global_language(), 'name') else str(get_global_language())
    phase2_task = Task(
        task_id=f"phase2_{int(time.time())}",
        task_string=(
            f"[LANGUAGE: {language_name}] "
            "Phase 2: Structure Stage – Create optimal project structure using RUN commands. "
            "CONSTRAINTS: No folder should have more than 8 items (files + subdirectories); "
            "Design the structure so each file remains under 1000 lines; Provide placeholder files for all major components; "
            "Follow best practices for the chosen tech stack; Separate interfaces, implementations, tests, and configs appropriately."
        ),
    )
    phase2_msg = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender="HUMAN",
        recipient=master_agent,
        message_id=f"phase2_init_{int(time.time())}",
        task=phase2_task,
    )

    structure_prompt = (
        "Proceed to structure stage. Use RUN commands to scaffold the codebase.\n\n"
        "CONSTRAINTS:\n"
        "- No folder should have more than 8 items (files + subdirectories)\n"
        "- Design the structure so each file remains under 1000 lines\n"
        "- Provide placeholder files for all major components\n"
        "- Follow best practices for the chosen tech stack\n"
        "- Separate interfaces, implementations, tests, and configs appropriately\n\n"
        "When finished, use FINISH to report completion."
    )

    await master_prompter(master_agent, structure_prompt, phase2_msg)

    while True:
        await completion_event.wait()
        completion_event.clear()
        completion_message = completion_data["message"]
        print(f"[Phase 2] Master completed with: {completion_message}")
        approval = await human_interface_fn(
            "Type 'Approved' to approve the structure and move to Phase 3 (Implementation), or give feedback:"
        )
        if approval.strip().lower() == "approved":
            completion_data["response_holder"]["response"] = "approved"
            completion_data["response_event"].set()
            break
        completion_data["response_holder"]["response"] = (
            f"Human feedback on structure: {approval}. Please refine and use FINISH when ready."
        )
        completion_data["response_event"].set()

    # ---------------------------- Phase 3 – Implementation ----------------------------
    print("[Phase 3] Creating agent hierarchy…")
    agent_lookup: Dict[Path, "BaseAgent"] = {}
    root_manager = _build_manager(
        root_path,
        parent=None,  # Will be assigned to master_agent below.
        llm_client=base_llm_client,
        max_context_size=max_context_size,
        agent_lookup=agent_lookup,
    )
    master_agent.set_root_agent(root_manager)
    root_manager.parent = master_agent

    print(f"[Phase 3] Created {len(agent_lookup)} agents.")

    # Create README stubs for all manager agents.
    for agent in agent_lookup.values():
        if getattr(agent, "is_manager", False):
            readme_path = agent.personal_file
            if not readme_path.exists():
                readme_path.write_text(
                    f"# {readme_path.parent.name}\n\nFolder managed by agent.\n"
                )

    language_name = str(get_global_language().name) if hasattr(get_global_language(), 'name') else str(get_global_language())
    phase3_task = Task(
        task_id=f"phase3_{int(time.time())}",
        task_string=(
            f"[LANGUAGE: {language_name}] "
            "Phase 3: Implementation – Coordinate development via delegation to the root manager. "
            "Delegate work in logical phases and use FINISH to report progress."
        ),
    )
    phase3_msg = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender="HUMAN",
        recipient=master_agent,
        message_id=f"phase3_init_{int(time.time())}",
        task=phase3_task,
    )

    implementation_prompt = (
        "Proceed to project implementation. Delegate work to the root manager in logical phases and "
        "use FINISH to report progress."
    )

    await master_prompter(master_agent, implementation_prompt, phase3_msg)

    while True:
        await completion_event.wait()
        completion_event.clear()
        completion_message = completion_data["message"]
        print(f"[Phase 3] Master completed with: {completion_message}")
        approval = await human_interface_fn(
            "Type 'Approved' to finish the project, or provide additional implementation requests:"
        )
        if approval.strip().lower() == "approved":
            completion_data["response_holder"]["response"] = "approved"
            completion_data["response_event"].set()
            break
        completion_data["response_holder"]["response"] = (
            f"Additional human request: {approval}. Please delegate tasks and use FINISH when ready."
        )
        completion_data["response_event"].set()

    # Optional: remove manager README stubs (clean-up step).
    for agent in agent_lookup.values():
        if getattr(agent, "is_manager", False):
            readme_path = agent.personal_file
            if readme_path.exists():
                readme_path.unlink()

    print("[Complete] New project initialization finished successfully!")
    return master_agent, root_manager, agent_lookup 