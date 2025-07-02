from __future__ import annotations

"""Project initializer utilities.

This module provides two initialization approaches for different scenarios:

1. **initialize_agents**: For existing directory structures with code
2. **initialize_new_project**: For completely new projects from empty directories  

Usage examples
--------------
>>> # For existing projects
>>> from src.initializer import initialize_agents
>>> root_agent, all_agents = initialize_agents("/path/to/existing/project")

>>> # For new projects (async)
>>> from src.initializer import initialize_new_project
>>> master, root_manager, all_agents = await initialize_new_project(
...     "/path/to/empty/dir", 
...     "Create a web application", 
...     human_interface_fn
... )

New Project Initialization (initialize_new_project)
---------------------------------------------------
Three-phase process for creating projects from scratch:

**Phase 1: Product Understanding**
- Creates master agent with no children initially
- Master agent asks clarifying questions to understand requirements
- Human interaction through provided interface function
- Controlled number of clarification rounds

**Phase 2: Structure Stage** 
- Master agent creates optimal directory/file structure
- Constraints: max 8 items per folder, max 1000 lines per file
- Uses mkdir/touch commands for scaffolding

**Phase 3: Agent Creation & Implementation**
- Creates complete agent hierarchy for the structure
- Sets up parent/child relationships with master → root manager
- Creates temporary READMEs for coordination
- Master delegates implementation work through logical phases
- Cleans up READMEs after completion

Existing Project Initialization (initialize_agents)
---------------------------------------------------
The original function for existing codebases:

1. Sets ``src.ROOT_DIR`` to the provided path (using ``src.set_root_dir``).
2. Recursively walks the directory tree.
   • For **every directory** it creates a :class:`~src.agents.manager_agent.ManagerAgent`.
     The directory's personal file is expected to be ``<folder_name>_README.md``. If the
     README is absent it is created automatically (empty file).
   • For **every file** it creates a :class:`~src.agents.coder_agent.CoderAgent` – except
     the manager READMEs which are already owned by the corresponding directory manager.
3. Correctly wires **parent / child** relationships between the agents.
4. Copies all agent tool scripts (e.g., run-mocha.js) from ``scripts/typescript/tools/``
   into the initialized project root's ``tools/`` directory, so agents can use them.
5. Returns **both** the root :class:`ManagerAgent` and a flat ``dict`` mapping
   ``Path`` objects to their associated agents for optional convenience.
"""

from pathlib import Path
from typing import Dict, Tuple, Optional, List, Union, Callable, Awaitable
import subprocess  # NEW: for bootstrapping TypeScript deps
import shutil  # NEW: for cleaning up directories
import time

from src import set_root_dir, ROOT_DIR
from src.agents.base_agent import BaseAgent
from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.agents.master_agent import MasterAgent
from src.llm.base import BaseLLMClient
from src.config import Language, set_global_language
from src.messages.protocol import Task, TaskMessage, MessageType
from src.orchestrator.master_prompter import master_prompter

__all__ = ["initialize_agents", "cleanup_project", "initialize_new_project"]


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
    parent: Optional[Union["ManagerAgent", "MasterAgent"]],
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


# Tool binary paths (populated after _bootstrap_language_environment)
TSC_BIN = ""
TS_NODE_BIN = ""
TSX_BIN = ""
MOCHA_BIN = ""


def _bootstrap_language_environment(language: "Language") -> None:
    """Provision language-specific offline tooling.

    For *typescript* this executes ``scripts/typescript/initializer.py`` which
    installs vendored tarballs into ``.node_deps``. The global *_BIN constants
    are populated afterwards so that other modules can reference them.
    """
    global TSC_BIN, TS_NODE_BIN, TSX_BIN, MOCHA_BIN
    from src import ROOT_DIR
    project_root = Path(ROOT_DIR)

    if language == Language.TYPESCRIPT:
        # Ensure packages are installed (idempotent).
        try:
            subprocess.run(["python", "scripts/typescript/initializer.py", str(project_root)], check=True)
        except subprocess.CalledProcessError as e:
            # In CI or restricted environments 'npm' may be unavailable. Skip installation but continue.
            print(f"[initializer] Warning: TypeScript tooling installation failed ({e}). Continuing assuming tools are pre-bundled.")
        node_deps = project_root / ".node_deps" / "node_modules"
        TSC_BIN = str(node_deps / "typescript" / "bin" / "tsc")
        TS_NODE_BIN = str(node_deps / "ts-node" / "bin" / "ts-node")
        TSX_BIN = str(node_deps / "tsx" / "dist" / "cli.mjs")
        MOCHA_BIN = str(node_deps / "mocha" / "bin" / "mocha")

    else:
        raise ValueError(f"Unsupported language environment: {language}")


def initialize_agents(
    root_directory: str | Path,
    *,
    language: Language = Language.TYPESCRIPT,
    llm_client: Optional[BaseLLMClient] = None,
    max_context_size: int = 8000,
) -> Tuple[ManagerAgent, Dict[Path, "BaseAgent"]]:
    """Initialize the full agent hierarchy for *root_directory*.

    Parameters
    ----------
    root_directory:
        Path to the project root that will become ``src.ROOT_DIR``.
    language:
        Programming language environment for the project.
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
    
    # Set global language so that all agents use the correct language settings
    set_global_language(language)

    # Bootstrap language-specific tooling *before* walking the tree so that child
    # agents know binaries exist.
    _bootstrap_language_environment(language)

    # Create scratch_pads directory for tester agents
    scratch_pads_dir = root_path / "scratch_pads"
    scratch_pads_dir.mkdir(exist_ok=True)
    print(f"[Initializer] Created scratch_pads directory: {scratch_pads_dir}")

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


def cleanup_project(root_directory: str | Path) -> None:
    """Clean up project resources including the scratch_pads directory.
    
    Parameters
    ----------
    root_directory:
        Path to the project root that contains the scratch_pads directory.
    """
    root_path = Path(root_directory).resolve()
    scratch_pads_dir = root_path / "scratch_pads"
    
    if scratch_pads_dir.exists():
        try:
            shutil.rmtree(scratch_pads_dir)
            print(f"[Initializer] Cleaned up scratch_pads directory: {scratch_pads_dir}")
        except Exception as e:
            print(f"[Initializer] Warning: Failed to cleanup scratch_pads directory: {e}")


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
        sender="USER",  # String for user, not agent object
        recipient=root_agent,
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
        finished = getattr(root_agent, "final_result", None)
        if finished is not None:
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
    language: Language = Language.TYPESCRIPT,
    llm_client: Optional[BaseLLMClient] = None,
    max_context_size: int = 8000,
) -> str:
    """Full convenience shortcut: build agents then run *initial_prompt*.

    Returns the root agent's textual response.
    """
    try:
        root_agent, _ = initialize_agents(
            root_directory,
            language=language,
            llm_client=llm_client,
            max_context_size=max_context_size,
        )

        return execute_root_prompt(root_agent, initial_prompt)
    finally:
        # Always clean up scratch_pads directory when done
        cleanup_project(root_directory)


async def initialize_new_project(
    root_directory: str | Path,
    initial_prompt: str,
    human_interface_fn: Callable[[str], Awaitable[str]],
    *,
    language: Language = Language.TYPESCRIPT,
    llm_client: Optional[BaseLLMClient] = None,
    max_context_size: int = 8000,
    phase1_iterations: int = 2
) -> Tuple["MasterAgent", ManagerAgent, Dict[Path, "BaseAgent"]]:
    """
    Initialize a completely new project from an empty directory.
    
    Three-phase process:
    1. Product Understanding: Master agent asks clarifying questions
    2. Structure Stage: Master creates directory/file structure  
    3. Agent Creation & Implementation: Create agents and implement project
    
    Args:
        root_directory: Empty root directory for the project
        initial_prompt: User's initial project request
        human_interface_fn: Async function to query human for responses
        language: Programming language for the project
        llm_client: LLM client for agents
        max_context_size: Max context size for agents
        phase1_iterations: Number of clarification rounds in phase 1
        
    Returns:
        (master_agent, root_manager, agent_lookup): The master agent, root manager, and all agents
    """
    root_path = Path(root_directory).resolve()
    if not root_path.exists():
        root_path.mkdir(parents=True, exist_ok=True)
    
    # Ensure directory is empty or nearly empty
    existing_items = list(root_path.iterdir())
    non_hidden_items = [item for item in existing_items if not item.name.startswith('.')]
    if non_hidden_items:
        raise ValueError(f"Directory {root_directory} is not empty. Found: {[item.name for item in non_hidden_items]}")
    
    # Set global configuration
    set_root_dir(str(root_path))
    set_global_language(language)
    
    # Bootstrap language environment
    _bootstrap_language_environment(language)
    
    # Create scratch_pads directory
    scratch_pads_dir = root_path / "scratch_pads"
    scratch_pads_dir.mkdir(exist_ok=True)
    
    # PHASE 1: Product Understanding
    print(f"[Phase 1] Starting product understanding phase...")
    
    # Create master agent with no children initially
    master_agent = MasterAgent(llm_client=llm_client, max_context_size=max_context_size)
    
    # Set human interface function
    master_agent.set_human_interface_fn(human_interface_fn)
    
    # Create and initialize documentation.md
    doc_path = root_path / "documentation.md"
    doc_path.write_text(f"# Project Documentation\n\nInitial Request: {initial_prompt}\n\n")
    
    # Phase 1: First call with task setup
    phase1_task = Task(
        task_id=f"phase1_{int(time.time())}",
        task_string=f"Phase 1: Product Understanding - Learn as much as possible about the human's requirements. Initial idea: {initial_prompt}"
    )
    
    phase1_task_message = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender="HUMAN",
        recipient=master_agent,
        message_id=f"phase1_init_{int(time.time())}",
        task=phase1_task
    )
    
    # First call with task and initial prompt
    print(f"[Phase 1] Initial clarification round")
    await master_prompter(master_agent, initial_prompt, phase1_task_message)
    
    # Wait for master to finish (indicating it used FINISH to ask questions)
    while master_agent.stall or master_agent.prompt_queue:
        await asyncio.sleep(0.1)
    
    # Subsequent iterations without new tasks (task is saved)
    for i in range(1, phase1_iterations):
        print(f"[Phase 1] Clarification round {i+1}/{phase1_iterations}")
        continuation_prompt = "Continue product understanding. Ask any remaining clarifying questions about requirements, scope, technology preferences, or user needs. Use FINISH to engage the human, or if you have sufficient understanding, move to documenting your understanding."
        
        await master_prompter(master_agent, continuation_prompt, message=None)
        
        # Wait for master to finish
        while master_agent.stall or master_agent.prompt_queue:
            await asyncio.sleep(0.1)
    
    print(f"[Phase 1] Product understanding phase complete.")
    
    # PHASE 2: Structure Stage  
    print(f"[Phase 2] Starting structure stage...")
    
    # Phase 2: Task setup
    phase2_task = Task(
        task_id=f"phase2_{int(time.time())}",
        task_string="Phase 2: Structure Stage - Create optimal project structure using mkdir and touch commands for this specific project"
    )
    
    phase2_task_message = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender="HUMAN",
        recipient=master_agent,
        message_id=f"phase2_init_{int(time.time())}",
        task=phase2_task
    )
    
    structure_prompt = """Proceed to structure stage. Use RUN commands with mkdir and touch to create an appropriate codebase structure for this project. 

CONSTRAINTS:
- No folder should have more than 8 items (files + subdirectories)
- Design the structure so each file can stay under 1000 lines of code
- Create placeholder files for all major components
- Follow best practices for the chosen technology stack
- Separate interfaces, implementations, tests, and configurations appropriately

Use RUN commands like:
- RUN "mkdir -p src/components src/services src/types"
- RUN "touch src/types/user.interface.ts"
- RUN "touch test/user.test.ts"

When done, use FINISH to confirm structure creation is complete."""
    
    await master_prompter(master_agent, structure_prompt, phase2_task_message)
    
    # Wait for master to finish structure creation
    while master_agent.stall or master_agent.prompt_queue:
        await asyncio.sleep(0.1)
        
    print(f"[Phase 2] Structure stage complete.")
    
    # PHASE 3: Agent Creation & Implementation
    print(f"[Phase 3] Creating agent hierarchy...")
    
    # Create all agents by walking the created structure
    agent_lookup: Dict[Path, "BaseAgent"] = {}
    
    # Create root manager first
    root_manager = _build_manager(
        root_path,
        parent=None,  # Will be set to master later
        llm_client=llm_client,
        max_context_size=max_context_size,
        agent_lookup=agent_lookup,
    )
    
    # Set root manager as master's child
    master_agent.set_root_agent(root_manager)
    root_manager.parent = master_agent
    
    print(f"[Phase 3] Created {len(agent_lookup)} agents in hierarchy.")
    
    # Create READMEs for all manager agents (folders)
    readme_count = 0
    for agent in agent_lookup.values():
        if hasattr(agent, 'is_manager') and agent.is_manager:
            readme_path = agent.personal_file
            if not readme_path.exists():
                readme_path.write_text(f"# {readme_path.parent.name}\n\nFolder managed by agent.\n")
                readme_count += 1
    
    print(f"[Phase 3] Created {readme_count} README files.")
    
    # Now instruct master to implement the project
    print(f"[Phase 3] Starting project implementation...")
    
    # Phase 3: Task setup
    phase3_task = Task(
        task_id=f"phase3_{int(time.time())}",
        task_string="Phase 3: Project Implementation - Orchestrate development through logical phases using delegation to root manager"
    )
    
    phase3_task_message = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender="HUMAN",
        recipient=master_agent,
        message_id=f"phase3_init_{int(time.time())}",
        task=phase3_task
    )
    
    implementation_prompt = """Proceed to project implementation phase. Delegate work to your root manager agent to implement the project according to your documentation. 

Break the work into logical phases:
1. Core interfaces and data models
2. Foundation utilities and services  
3. Business logic implementation
4. Integration and testing
5. Final verification

Use DELEGATE commands to assign work phases. Use WAIT between phases as needed. When the entire project is implemented and working, use FINISH to confirm completion."""
    
    await master_prompter(master_agent, implementation_prompt, phase3_task_message)
    
    # Wait for master to complete implementation
    print(f"[Phase 3] Waiting for implementation to complete...")
    while (master_agent.stall or 
           master_agent.prompt_queue or 
           master_agent.child_active_boolean or 
           master_agent.active_ephemeral_agents):
        await asyncio.sleep(0.5)
        
    print(f"[Phase 3] Project implementation complete.")
    
    # Clean up READMEs as requested
    print(f"[Cleanup] Removing README files...")
    readme_removed = 0
    for agent in agent_lookup.values():
        if hasattr(agent, 'is_manager') and agent.is_manager:
            readme_path = agent.personal_file
            if readme_path.exists():
                readme_path.unlink()
                readme_removed += 1
                
    print(f"[Cleanup] Removed {readme_removed} README files.")
    print(f"[Complete] New project initialization finished successfully!")
    
    return master_agent, root_manager, agent_lookup 