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

Since agents automatically create their children when they don't exist, we only
need to create the root manager agent and let the hierarchy build itself dynamically.
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

__all__ = ["initialize_new_project", "initialize_ongoing_project"]

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

    # Documents folder for important project documentation.
    documents_dir = root_path / "documents"
    documents_dir.mkdir(exist_ok=True)

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
    # Set master agent to phase 1
    master_agent.set_phase("phase1")
    
    language_name = str(get_global_language().name) if hasattr(get_global_language(), 'name') else str(get_global_language())
    phase1_task = Task(
        task_id=f"phase1_{int(time.time())}",
        task_string=(
            f"[LANGUAGE: {language_name}] "
            "Phase 1: Product Understanding – Learn as much as possible about the human's "
            f"requirements. Initial idea: {initial_prompt}\n\n"
            "NOTE: A 'documents' folder has been created in the project root. Please encourage the human "
            "to add any important documentation files (specifications, requirements, design docs, etc.) "
            "to this folder during the planning phase."
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
    # Set master agent to phase 2
    master_agent.set_phase("phase2")
    
    language_name = str(get_global_language().name) if hasattr(get_global_language(), 'name') else str(get_global_language())
    phase2_task = Task(
        task_id=f"phase2_{int(time.time())}",
        task_string=(
            f"[LANGUAGE: {language_name}] "
            "Phase 2: Structure Stage – Create optimal project structure using RUN commands. "
            "CONSTRAINTS: No folder should have more than 8 items (files + subdirectories); "
            "Design the structure so each file remains under 1000 lines; Provide placeholder files for all major components; "
            "Follow best practices for the chosen tech stack; Separate interfaces, implementations, tests, and configs appropriately.\n\n"
            "IMPORTANT: Add any necessary information that may only be applicable to specific tasks to separate "
            ".md files in the documents folder. Create well-organized documentation files (e.g., api-guidelines.md, "
            "testing-requirements.md, deployment-notes.md) to help future agents understand task-specific requirements."
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
    print("[Phase 3] Creating root manager agent…")
    # Set master agent to phase 3
    master_agent.set_phase("phase3")
    
    # Create only the root manager agent - it will create its children dynamically as needed
    root_manager = ManagerAgent(
        path=str(root_path),
        parent=None,  # Will be assigned to master_agent below
        llm_client=base_llm_client,
        max_content_size=max_context_size,
    )
    master_agent.set_root_agent(root_manager)
    root_manager.parent = master_agent

    # Initialize agent lookup with just the root manager
    agent_lookup: Dict[Path, "BaseAgent"] = {root_path: root_manager}

    print(f"[Phase 3] Created root manager agent - children will be created dynamically as needed.")

    language_name = str(get_global_language().name) if hasattr(get_global_language(), 'name') else str(get_global_language())
    phase3_task = Task(
        task_id=f"phase3_{int(time.time())}",
        task_string=(
            f"[LANGUAGE: {language_name}] "
            "Phase 3: Implementation – Coordinate development via delegation to the root manager. "
            "Delegate work in logical phases and use FINISH to report progress.\n\n"
            "IMPORTANT: Always check the documents folder for any files that have been added. Read all "
            "documentation files thoroughly and ensure you understand their contents. When delegating tasks "
            "to child agents, be sure to inform them about any documents in the documents folder that are "
            "relevant to their specific tasks and encourage them to read those files before proceeding."
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

    print("[Complete] New project initialization finished successfully!")
    return master_agent, root_manager, agent_lookup 

# ----------------------------
# Public API – *initialize_ongoing_project*
# ----------------------------


async def initialize_ongoing_project(
    root_directory: str | Path,
    project_goal: str,
    human_interface_fn: Callable[[str], Awaitable[str]],
    *,
    language: Language = Language.TYPESCRIPT,
    master_llm_client: Optional[BaseLLMClient] = None,
    base_llm_client: Optional[BaseLLMClient] = None,
    max_context_size: int = 80000,
) -> Tuple["MasterAgent", ManagerAgent, Dict[Path, "BaseAgent"]]:
    """Bootstraps agents for an *existing* project and coordinates change requests.

    The coroutine follows a two-phase workflow:

    1. *Understanding & Documentation* – The master agent (a) clarifies the human's
       overall goal for the project, (b) recursively asks every agent in the
       hierarchy to summarise its scope so README files and `documentation.md`
       reflect the current state of the codebase, and (c) installs any missing
       environment prerequisites via RUN commands.
    2. *Change Phase* – Once the human approves the documentation, the master
       agent coordinates implementation of the requested changes via
       delegation to the root manager agent.
    """

    root_path = Path(root_directory).resolve()
    if not root_path.exists():
        raise ValueError(f"Directory {root_directory} does not exist – cannot initialise ongoing project.")

    # Ensure the directory is not empty (otherwise `initialize_new_project` should be used)
    existing_items = [item for item in root_path.iterdir() if not item.name.startswith(".")]
    if not existing_items:
        raise ValueError(
            f"Directory {root_directory} appears to be empty – use `initialize_new_project` instead."
        )

    # Global configuration & language toolchain.
    set_root_dir(str(root_path))
    set_global_language(language)

    # Documents folder for important project documentation.
    documents_dir = root_path / "documents"
    documents_dir.mkdir(exist_ok=True)

    # ---------------------------------------------------------------------
    # Create master agent upfront so we can build the child hierarchy.
    # ---------------------------------------------------------------------
    master_agent = MasterAgent(
        llm_client=master_llm_client,
        max_context_size=max_context_size,
    )

    # Bidirectional handshake for FINISH messages, identical to the helper in
    # `initialize_new_project`.
    completion_event: asyncio.Event = asyncio.Event()
    completion_data: Dict[str, Optional[str | asyncio.Event | Dict[str, str]]] = {"message": None}

    async def phase_communication_fn(completion_message: str) -> str:  # noqa: D401
        completion_data["message"] = completion_message
        completion_event.set()
        response_event: asyncio.Event = asyncio.Event()
        response_holder: Dict[str, str] = {"response": ""}
        completion_data["response_event"] = response_event
        completion_data["response_holder"] = response_holder

        await response_event.wait()
        return response_holder["response"]

    master_agent.set_human_interface_fn(phase_communication_fn)

    # ---------------------------------------------------------------------
    # Create only the root manager agent - children will be created dynamically
    # ---------------------------------------------------------------------
    print("[Init] Creating root manager agent for existing project…")
    
    root_manager = ManagerAgent(
        path=str(root_path),
        parent=None,  # will be set after creation
        llm_client=base_llm_client,
        max_content_size=max_context_size,
    )
    master_agent.set_root_agent(root_manager)
    root_manager.parent = master_agent

    # Initialize agent lookup with just the root manager
    agent_lookup: Dict[Path, "BaseAgent"] = {root_path: root_manager}

    print(f"[Init] Created root manager agent - children will be created dynamically as needed.")

    # Persistent high-level documentation.
    documentation_path = root_path / "documentation.md"
    if not documentation_path.exists():
        documentation_path.write_text("# Project Documentation\n\n")
    documentation_path.write_text(
        documentation_path.read_text(encoding="utf-8", errors="ignore")
        + f"\n## Ongoing Initialisation\n\nHuman goal: {project_goal}\n\n",
        encoding="utf-8",
    )

    # ---------------------- Phase 1 – Understanding & Docs ----------------------
    print("[Phase 1&2] Starting understanding & documentation phase…")
    # Set master agent to phase 2 (structure/docs phase for ongoing projects)
    master_agent.set_phase("phase2")
    
    language_name = str(get_global_language().name) if hasattr(get_global_language(), "name") else str(get_global_language())
    phase1_task = Task(
        task_id=f"ongoing_phase1_{int(time.time())}",
        task_string=(
            f"[LANGUAGE: {language_name}] "
            "Phase 1&2: Documentation & Project Understanding – Clarify the human's goal using finish, recursively summarise each agent's scope to populate README files, "
            "and install any missing environment dependencies using RUN commands. DO NOT TRY TO FIX EVERYTHING YOURSELF, THIS STAGE IS FOR UNDERSTANDING ONLY. "
            f"Human goal: {project_goal}\n\n"
            "NOTE: A 'documents' folder has been created in the project root. Please encourage the human "
            "to add any important documentation files (specifications, requirements, design docs, etc.) "
            "to this folder during the planning phase."
        ),
    )
    phase1_msg = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender="HUMAN",
        recipient=master_agent,
        message_id=f"ongoing_phase1_init_{int(time.time())}",
        task=phase1_task,
    )

    # Kick-off Phase 1.
    phase1_prompt = (
        "Proceed with documentation & understanding. Recursively delegate to build README summaries for every directory and file. "
        "Install any required environment dependencies using RUN commands. Use FINISH to prompt the human for approval."
    )

    await master_prompter(master_agent, phase1_prompt, phase1_msg)

    # Wait for approval / feedback loop.
    while True:
        await completion_event.wait()
        completion_event.clear()
        completion_message = completion_data["message"]
        print(f"[Phase 1&2] Master completed with: {completion_message}")
        approval = await human_interface_fn(
            "Type 'Approved' to move to Phase 3 (Implementation), or provide additional feedback:"
        )
        if approval.strip().lower() == "approved":
            completion_data["response_holder"]["response"] = "approved"
            completion_data["response_event"].set()
            break
        # Otherwise send feedback and continue Phase 1.
        completion_data["response_holder"]["response"] = (
            f"Human feedback: {approval}. Please refine documentation and use FINISH when ready."
        )
        completion_data["response_event"].set()

    # ----------------------------- Phase 2 – Change -----------------------------
    print("[Phase 2] Starting change phase…")
    # Set master agent to phase 3 (implementation phase for ongoing projects)
    master_agent.set_phase("phase3")

    # Collect change request from human.
    change_request = await human_interface_fn(
        "Describe the changes you would like to implement across the project:"
    )

    language_name = str(get_global_language().name) if hasattr(get_global_language(), "name") else str(get_global_language())
    phase2_task = Task(
        task_id=f"ongoing_phase3_{int(time.time())}",
        task_string=(
            f"[LANGUAGE: {language_name}] "
            "Phase 3: Change Phase – Implement the requested modifications across the project. "
            f"Change request: {change_request}\n\n"
            "IMPORTANT: Always check the documents folder for any files that have been added. Read all "
            "documentation files thoroughly and ensure you understand their contents. When delegating tasks "
            "to child agents, be sure to inform them about any documents in the documents folder that are "
            "relevant to their specific tasks and encourage them to read those files before proceeding."
        ),
    )
    phase2_msg = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender="HUMAN",
        recipient=master_agent,
        message_id=f"ongoing_phase3_init_{int(time.time())}",
        task=phase2_task,
    )

    change_prompt = (
        "Proceed to implement the requested changes. Delegate work to the root manager in logical phases and use FINISH to report progress."
    )

    await master_prompter(master_agent, change_prompt, phase2_msg)

    while True:
        await completion_event.wait()
        completion_event.clear()
        completion_message = completion_data["message"]
        print(f"[Phase 3] Master completed with: {completion_message}")
        approval = await human_interface_fn(
            "Type 'Approved' to finish the change phase, or provide additional change requests:"
        )
        if approval.strip().lower() == "approved":
            completion_data["response_holder"]["response"] = "approved"
            completion_data["response_event"].set()
            break
        completion_data["response_holder"]["response"] = (
            f"Additional change request from human: {approval}. Please address and use FINISH when ready."
        )
        completion_data["response_event"].set()

    # Final cleanup (e.g. remove temporary README stubs if desired – we keep them for ongoing projects).
    print("[Complete] Ongoing project initialisation finished successfully!")
    return master_agent, root_manager, agent_lookup 