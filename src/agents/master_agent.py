"""
Master Agent - the top-level agent that orchestrates the entire system.

This agent is independent and doesn't inherit from any existing agents.
It manages the overall workflow and coordinates all other agents.
"""

import os
import asyncio
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader

# Local imports
from src.llm.base import BaseLLMClient
import src
from src.config import COLLAPSED_DIR_NAMES

# Global constants
AGENT_TIMEOUT_SECONDS = 600
DEFAULT_MAX_CONTEXT_SIZE = 8000

# ContextEntry ADT for prompt-response pairs
@dataclass
class ContextEntry:
    prompt: str
    response: str

class MasterAgent:
    """
    Master agent that orchestrates the entire system.
    
    This is a standalone agent that doesn't inherit from any existing agents.
    It coordinates all other agents and manages the overall workflow.
    """
    
    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        max_context_size: int = DEFAULT_MAX_CONTEXT_SIZE
    ) -> None:
        """Initialize the master agent.
        
        Args:
            llm_client: Optional LLM client for generating responses
            max_context_size: Maximum size of context to maintain
        """
        # Core attributes
        self.llm_client = llm_client
        self.max_context_size = max_context_size
        
        # Agent state
        self.prompt_queue: List[str] = []
        self.stall = False
        
        # Memory: Dictionary of filenames to file paths
        self.memory: Dict[str, Path] = {}
        
        # Context: List of ContextEntry (prompt-response history)
        self.context: List[ContextEntry] = []
        
        # Personal file management
        self.personal_file: Optional[Path] = None
        
        # Task tracking
        self.active_task = None
        
        # Child management - Master has one child: the root manager agent
        self.root: Optional[Any] = None  # The root manager agent
        self.child_active_boolean: bool = False  # Flag to track if the root agent is active
        
        # Ephemeral agent tracking
        self.active_ephemeral_agents: List[Any] = []
        
        # Watchdog attributes
        self.last_activity = time.time()
        self._watchdog_task = None
        self._watchdog_started = False
        
        # Human interface function for FINISH directive
        self.human_interface_fn = None
        
        # Initialize Jinja2 environment – resolve the absolute path to the
        # project-level "prompts" directory so the templates are found
        # regardless of the script's current working directory.
        project_root = Path(__file__).resolve().parent.parent.parent
        templates_dir = project_root / "prompts"

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Set personal file (documentation.md in root)
        self.set_personal_file()
    
    def set_personal_file(self) -> None:
        """Set the personal file for this master agent.
        
        Master agent's personal file is documentation.md in the project root.
        """
        if src.ROOT_DIR is not None:
            self.personal_file = src.ROOT_DIR / "documentation.md"
            if self.personal_file:
                self.memory[self.personal_file.name] = self.personal_file
    
    def start_watchdog(self):
        """Start the watchdog task for monitoring agent activity."""
        if not self._watchdog_started:
            try:
                loop = asyncio.get_running_loop()
                self._watchdog_task = loop.create_task(self._watchdog_loop())
                self._watchdog_started = True
            except RuntimeError:
                # No running loop, will try again later
                pass
    
    async def process_task(self, prompt: str) -> None:
        """Process a task by adding prompt to queue and calling API if not stalled.
        
        Args:
            prompt: The prompt to process
        """
        self.start_watchdog()
        self.prompt_queue.append(prompt)
        
        if not self.stall:
            try:
                await self.api_call()
            except Exception as e:
                # Surface the exception immediately so manual testing doesn't appear to hang
                import sys, traceback
                print(f"[MasterAgent] Exception during api_call: {e}", file=sys.stderr)
                traceback.print_exc()

                # Ensure the agent doesn't remain stalled forever
                self.stall = False

                # Reprompt with the error message so higher-level logic can react
                error_msg = f"Exception during api_call: {e}"
                # Avoid infinite recursion: only enqueue, let caller decide when to process
                self.prompt_queue.append(error_msg)
        
        self.update_activity()
    
    async def api_call(self) -> None:
        """Make an API call with current context and memory for master agent.
        
        Uses master-specific Jinja templates and processes response through master language.
        """
        # Set stall to true to prevent concurrent API calls
        self.stall = True
        
        # Get current prompt from queue
        current_prompt = "\n".join(self.prompt_queue) if self.prompt_queue else ""
        
        # Get memory contents
        memory_contents = self.get_memory_contents()
        
        # Get personal file content
        personal_file_name = ""
        if self.personal_file and self.personal_file.exists():
            personal_file_name = self.personal_file.name
        
        # Get codebase structure
        codebase_structure = self.get_codebase_structure_string()
        
        # Load Lark grammar (act like prompts/master/ exists)
        lark_grammar = ""
        try:
            with open('prompts/master/master_grammar.lark', 'r', encoding='utf-8') as f:
                lark_grammar = f.read()
        except Exception as e:
            lark_grammar = f"[Error reading Lark grammar: {str(e)}]"
        
        # Load language examples
        language_examples = ""
        try:
            with open('prompts/master/language_examples.md', 'r', encoding='utf-8') as f:
                language_examples = f.read()
        except Exception as e:
            language_examples = f"[Error reading language examples: {str(e)}]"
        
        # Load agent role description from markdown file
        try:
            with open('prompts/master/agent_role.md', 'r', encoding='utf-8') as f:
                agent_role = f.read()
        except Exception as e:
            agent_role = f"[Error reading agent role: {str(e)}]"

        # Master agent doesn't have a personal path - it operates at system level
        if src.ROOT_DIR is None:
            raise RuntimeError("ROOT_DIR is not set. Please initialize it with src.set_root_dir(<project_root_path>) before creating agents.")

        # Master agent tracks root agent directly via self.root and self.child_active_boolean

        # Define available terminal commands and utilities
        try:
            with open('prompts/master/available_commands.md', 'r', encoding='utf-8') as f:
                available_commands = f.read()
        except Exception as e:
            available_commands = f"[Error reading available commands: {str(e)}]"

        # Make API call using message list
        if self.llm_client:
            if self.llm_client.supports_system_role:
                # Render split templates
                system_template = self.jinja_env.get_template('system_template.j2')
                user_template = self.jinja_env.get_template('master_template.j2')  # Act like this exists

                system_prompt = system_template.render(
                    agent_role=agent_role,
                    available_commands=available_commands,
                    lark_grammar=lark_grammar,
                    language_examples=language_examples
                )

                # Only show the task string, not the full TaskMessage repr
                task_string = None
                if self.active_task is not None:
                    if hasattr(self.active_task, 'task') and hasattr(self.active_task.task, 'task_string'):
                        task_string = self.active_task.task.task_string
                    else:
                        task_string = str(self.active_task)
                
                user_prompt = user_template.render(
                    active_task=task_string,
                    context=self.context,
                    memory_contents=memory_contents,
                    personal_file_name=personal_file_name,
                    codebase_structure=codebase_structure,
                    current_prompt=current_prompt,
                    root_agent=self.root,
                    child_active_boolean=self.child_active_boolean,
                    active_ephemeral_agents=self.active_ephemeral_agents
                )

                messages = [
                    {"role": "user", "content": user_prompt}
                ]
                response = await self.llm_client.generate_response(messages, system_prompt=system_prompt)
            else:
                # Fallback to original monolithic template
                template = self.jinja_env.get_template('agent_template.j2')
                formatted_prompt = template.render(
                    agent_role=agent_role,
                    active_task=task_string,
                    context=self.context,
                    memory_contents=memory_contents,
                    personal_file_name=personal_file_name,
                    codebase_structure=codebase_structure,
                    available_commands=available_commands,
                    lark_grammar=lark_grammar,
                    language_examples=language_examples,
                    current_prompt=current_prompt,
                    root_agent=self.root,
                    child_active_boolean=self.child_active_boolean,
                    active_ephemeral_agents=self.active_ephemeral_agents
                )
                response = await self.llm_client.generate_response(formatted_prompt)

            # Save context (only store current prompt -> response)
            action = response.split()[0] if response.strip() else "NO_ACTION"
            print(f"[Master] Prompt: {current_prompt} | Output: {response}")
            self.context.append(ContextEntry(prompt=current_prompt, response=response))

            # Clear prompt queue
            self.prompt_queue.clear()

            # Process response via master language interpreter
            from src.languages.master_language.interpreter import execute_directive
            execute_directive(response, agent=self)
    
    def add_ephemeral_agent(self, ephemeral_agent) -> None:
        """Add an ephemeral agent to the tracking list.
        
        Args:
            ephemeral_agent: The ephemeral agent to track
        """
        if ephemeral_agent not in self.active_ephemeral_agents:
            self.active_ephemeral_agents.append(ephemeral_agent)
        self.update_activity()
    
    def remove_ephemeral_agent(self, ephemeral_agent) -> None:
        """Remove an ephemeral agent from the tracking list.
        
        Args:
            ephemeral_agent: The ephemeral agent to remove
        """
        if ephemeral_agent in self.active_ephemeral_agents:
            self.active_ephemeral_agents.remove(ephemeral_agent)
        self.update_activity()
    
    def read_file(self, file_path: str) -> None:
        """Add a file to memory for reading.
        
        The file contents will be automatically loaded during API calls.
        
        Args:
            file_path: Path to the file to add to memory
        """
        full_path = Path(file_path).resolve()
        filename = full_path.name
        self.memory[filename] = full_path
        self.update_activity()
    
    def get_memory_contents(self) -> Dict[str, str]:
        """Read the contents of every file in memory and assemble a dictionary.
        
        This is called before every API call to ensure up-to-date memory.
        
        Returns:
            Dict[str, str]: Dictionary of filenames to file contents
        """
        contents = {}
        
        for filename, file_path in self.memory.items():
            try:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        contents[filename] = f.read()
                else:
                    contents[filename] = f"[File does not exist: {file_path}]"
            except Exception as e:
                contents[filename] = f"[Error reading file: {str(e)}]"
        
        self.update_activity()
        return contents
    
    def get_codebase_structure_string(self) -> str:
        """Returns a tree-style ASCII representation of the codebase.
        
        Starts at the project root directory (ROOT_DIR from src).
        
        Returns:
            str: Tree-style representation of the codebase
        """
        def tree(dir_path: Path, prefix: str = "") -> list:
            entries = []
            try:
                children = sorted(list(dir_path.iterdir()), key=lambda p: (not p.is_dir(), p.name.lower()))
            except Exception as e:
                return [f"{prefix}[Error reading directory: {e}]"]
            for idx, child in enumerate(children):
                connector = "└── " if idx == len(children) - 1 else "├── "
                if child.is_dir():
                    if child.name in COLLAPSED_DIR_NAMES:
                        # Show the folder but collapse its contents to keep output concise
                        entries.append(f"{prefix}{connector}{child.name}/...")
                    else:
                        entries.append(f"{prefix}{connector}{child.name}/")
                        extension = "    " if idx == len(children) - 1 else "│   "
                        entries.extend(tree(child, prefix + extension))
                else:
                    entries.append(f"{prefix}{connector}{child.name}")
            return entries
        
        root = src.ROOT_DIR if getattr(src, 'ROOT_DIR', None) is not None else Path('.').resolve()
        lines = [f"{root.name}/"]
        if root.is_dir():
            lines.extend(tree(root))
        else:
            lines.append(f"└── {root.name}")
        
        self.update_activity()
        return "\n".join(lines)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current master agent status.
        
        Returns:
            Dict[str, Any]: Status information including:
                - Agent type and configuration
                - Active state and current task
                - Memory and context usage
                - Child and ephemeral agent counts
                - Queue and stall state
        """
        self.update_activity()
        return {
            'agent_type': 'master',
            'llm_client': str(self.llm_client) if self.llm_client else None,
            'max_context_size': self.max_context_size,
            'personal_file': str(self.personal_file) if self.personal_file else None,
            'active_task': str(self.active_task) if self.active_task else None,
            'memory_files': len(self.memory),
            'context_entries': len(self.context),
            'prompt_queue_size': len(self.prompt_queue),
            'stall': self.stall,
            'root_agent': str(self.root) if self.root else None,
            'child_active_boolean': self.child_active_boolean,
            'active_ephemeral_agents': len(self.active_ephemeral_agents),
            'watchdog_started': self._watchdog_started,
            'last_activity': self.last_activity,
        }
    
    def __repr__(self) -> str:
        """String representation of the master agent.
        
        Returns:
            str: Agent representation including type and active state
        """
        root_status = "present" if self.root else "none"
        return f"MasterAgent(root={root_status}, ephemeral={len(self.active_ephemeral_agents)}, stall={self.stall})"
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = time.time()
    
    async def _watchdog_loop(self):
        """Watchdog loop that monitors agent activity and handles timeouts."""
        while True:
            await asyncio.sleep(10)
            if not self.child_active_boolean and not self.active_ephemeral_agents:
                if time.time() - self.last_activity > AGENT_TIMEOUT_SECONDS:
                    await self.handle_timeout()
                    break
    
    async def handle_timeout(self):
        """Handle timeout when the agent has been inactive for too long."""
        # Log the timeout
        print(f"[MasterAgent] Timeout after {AGENT_TIMEOUT_SECONDS} seconds of inactivity")
        
        # Cancel watchdog if running
        if hasattr(self, '_watchdog_task') and self._watchdog_task is not None:
            try:
                if not self._watchdog_task.done():
                    self._watchdog_task.cancel()
            except Exception:
                pass
            self._watchdog_task = None
            self._watchdog_started = False
        
        # Reset state
        self.stall = False
        self.prompt_queue.clear()
        
        self.update_activity()
    
    def set_root_agent(self, root_agent) -> None:
        """Set the root manager agent.
        
        Args:
            root_agent: The root manager agent to set
        """
        self.root = root_agent
        self.child_active_boolean = getattr(root_agent, 'is_active', False)
        self.update_activity()
    
    def set_human_interface_fn(self, human_interface_fn) -> None:
        """Set the human interface function for FINISH directive interactions.
        
        Args:
            human_interface_fn: Async function that takes completion message and returns human response
                               Signature: async def fn(completion_message: str) -> str
        """
        self.human_interface_fn = human_interface_fn
        self.update_activity()
    

    def delegate_task(self, child_agent, task_description: str) -> None:
        """Delegate a task to the root agent.
        
        Args:
            child_agent: The root agent to delegate to
            task_description: Description of the task to delegate
        """
        # Set child as active when delegating work
        self.child_active_boolean = True
        self.update_activity()
    
    def receive_child_result(self, child_agent, result: Any) -> None:
        """Receive and process a result from the root agent.
        
        Args:
            child_agent: The root agent that completed a task
            result: The result from the root agent
        """
        # Set child as inactive when receiving result
        self.child_active_boolean = False
        self.update_activity() 