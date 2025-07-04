"""
Base Agent class that all agents inherit from.

This module provides the core functionality for all agents in the hierarchical system, including:
- File reading and memory management
- Context management (prompt-response history)
- Task processing and API calls
- Personal file management

Manager agents additionally implement:
- Child agent management
- Task delegation
- Directory-level operations

The agent system uses a hierarchical structure where:
- Manager agents control directories and delegate to children
- Coder agents handle individual files
- All agents maintain a personal file (README for managers, code file for coders)
- Memory contains file paths, context contains prompt-response history
"""

# Standard library imports
import os
import json
import asyncio
import uuid
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass
import threading

# Local imports
from src.messages.protocol import (
    Message, TaskMessage, ResultMessage, MessageType
)
from src.llm.base import BaseLLMClient
import src
from src.config import COLLAPSED_DIR_NAMES

# Import for type hints only
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .master_agent import MasterAgent

# Global constants
MAX_CONTEXT_DEPTH = 3
DEFAULT_MAX_CONTEXT_SIZE = 8000
AGENT_TIMEOUT_SECONDS = 600

# ContextEntry ADT for prompt-response pairs
@dataclass
class ContextEntry:
    prompt: str
    response: str

class BaseAgent(ABC):
    '''
    Base agent class providing core functionality for all agents in the hierarchical system.
    
    Each agent has:
    - path: The path this agent is responsible for (file for coder, directory for manager)
    - personal_file: The one file this agent can modify (code file for coder, README for manager)
    - parent: Optional parent agent object
    - children: List of child agent objects
    - llm_client: LLM client for generating responses
    
    The agent maintains:
    - Active state and current task
    - Prompt queue for processing
    - Memory: Dictionary of filenames to file paths
    - Context: List of ContextEntry (prompt-response history)
    - Stall state for managing dependencies
    '''

    def __init__(
        self,
        path: str,
        parent: Optional[Union["BaseAgent", "MasterAgent"]] = None,
        llm_client: Optional[BaseLLMClient] = None,
        max_context_size: int = DEFAULT_MAX_CONTEXT_SIZE
    ) -> None:
        """Initialize a new agent.
        
        Args:
            path: Path this agent is responsible for
            parent: Optional parent agent object
            llm_client: Optional LLM client for generating responses
            max_context_size: Maximum size of context to maintain
        """
        self.path = Path(path).resolve()
        self.parent: Optional[Union["BaseAgent", "MasterAgent"]] = parent

        self.llm_client = llm_client
        self.max_context_size = max_context_size

        # Agent State
        self.is_active = False
        self.prompt_queue: List[str] = []
        self.stall = False

        # Memory: Dictionary of filenames to file paths
        self.memory: Dict[str, Path] = {}
        
        # Context: List of ContextEntry (prompt-response history)
        self.context: List[ContextEntry] = []
        
        # Personal file (always set, never optional)
        self.personal_file: Path = None

        # Task Tracking
        self.active_task = None

        # Ephemeral Agent Tracking (for all agents)
        self.active_ephemeral_agents = []

        # Set personal file based on agent type
        self._set_personal_file()

        self.last_activity = time.time()
        self._watchdog_task = None
        self._watchdog_started = False

    def _set_personal_file(self) -> None:
        '''
        Set the personal file this agent can modify and add it to memory.
        For coders: the code file they manage
        For managers: their README.md in their own directory
        '''
        if self.path.is_file() or not self.path.exists():
            # Coder agent - personal file is the code file
            self.personal_file = self.path
        else:
            # Manager agent - personal file is README in their own directory
            self.personal_file = self.path / f"{self.path.name}_README.md"
        if self.personal_file:
            self.memory[self.personal_file.name] = self.personal_file

    @property
    def scope_path(self) -> Path:
        '''
        Get the path this agent is responsible for.
        '''
        return self.path

    @property
    def is_manager(self) -> bool:
        '''
        Checks if this agent manages a directory.
        '''
        return self.path.is_dir()
    
    @property
    def is_coder(self) -> bool:
        '''
        Checks if this agent manages a file.
        '''
        return self.path.is_file() or not self.path.exists()

    def activate(self, task: TaskMessage) -> None:
        '''
        Activate the agent to work on a task.
        Only works when there is no active task and agent is not active.
        
        Args:
            task: The task to process
            
        Raises:
            RuntimeError: If agent is already active or has an active task
        '''
        if self.is_active or self.active_task is not None:
            raise RuntimeError(
                f"Agent is already active or has an active task"
            )
        # Set personal file and add to memory
        self._set_personal_file()
        # Automatically add documentation.md from project root to memory if it exists
        doc_path = getattr(src, 'ROOT_DIR', None)
        if doc_path is not None:
            doc_file = doc_path / "documentation.md"
            if doc_file.exists():
                self.read_file(str(doc_file))
        self.is_active = True
        self.active_task = task
        self.update_activity()

    def deactivate(self) -> None:
        '''
        Deactivate the agent and clean up memory.
        Manager agents must ensure all children are deactivated first.
        
        Raises:
            RuntimeError: If a child is still active
        '''
        # Check if manager has active children
        if hasattr(self, 'active_children') and self.active_children:
            raise RuntimeError(
                f"Cannot deactivate agent with active children: {list(self.active_children.keys())}"
            )
        
        # Cancel watchdog if running
        if hasattr(self, '_watchdog_task') and self._watchdog_task is not None:
            try:
                if not self._watchdog_task.done():
                    self._watchdog_task.cancel()
            except Exception:
                pass
            self._watchdog_task = None
            self._watchdog_started = False
        
        self.is_active = False
        self.active_task = None
        
        # Clear memory and context
        self.memory.clear()
        self.context.clear()
        self.prompt_queue.clear()
        self.stall = False
        self.update_activity()

    def start_watchdog(self):
        if not self._watchdog_started:
            try:
                loop = asyncio.get_running_loop()
                self._watchdog_task = loop.create_task(self._watchdog_loop())
                self._watchdog_started = True
            except RuntimeError:
                # No running loop, will try again later
                pass

    async def process_task(self, prompt: str) -> None:
        self.start_watchdog()
        self.prompt_queue.append(prompt)
        
        if not self.stall:
            try:
                await self.api_call()
            except Exception as e:
                # Surface the exception immediately so manual testing doesn't appear to hang
                import sys, traceback
                print(f"[BaseAgent] Exception during api_call for agent {self.path}: {e}", file=sys.stderr)
                traceback.print_exc()

                # Ensure the agent doesn't remain stalled forever
                self.stall = False

                # Reprompt with the error message so higher-level logic can react
                error_msg = f"Exception during api_call: {e}"
                # Avoid infinite recursion: only enqueue, let caller decide when to process
                self.prompt_queue.append(error_msg)
        self.update_activity()

    @abstractmethod
    async def api_call(self) -> None:
        self.start_watchdog()
        '''
        Make an API call with current context and memory.
        This method must be implemented by subclasses to handle
        their specific Jinja templates and response processing.
        '''
        pass

    def add_ephemeral_agent(self, ephemeral_agent) -> None:
        '''
        Add an ephemeral agent to the tracking list.
        
        Args:
            ephemeral_agent: The ephemeral agent to track
        '''
        if ephemeral_agent not in self.active_ephemeral_agents:
            self.active_ephemeral_agents.append(ephemeral_agent)
        self.update_activity()

    def remove_ephemeral_agent(self, ephemeral_agent) -> None:
        '''
        Remove an ephemeral agent from the tracking list.
        
        Args:
            ephemeral_agent: The ephemeral agent to remove
        '''
        if ephemeral_agent in self.active_ephemeral_agents:
            self.active_ephemeral_agents.remove(ephemeral_agent)
        self.update_activity()

    def read_file(self, file_path: str) -> None:
        '''
        Add a file to memory for reading.
        The file contents will be automatically loaded during API calls.
        
        Args:
            file_path: Path to the file to add to memory
        '''
        full_path = Path(file_path).resolve()
        filename = full_path.name
        self.memory[filename] = full_path
        self.update_activity()

    def _get_memory_contents(self) -> Dict[str, str]:
        '''
        Read the contents of every file in memory and assemble a dictionary.
        This is called before every API call to ensure up-to-date memory.
        
        Returns:
            Dict[str, str]: Dictionary of filenames to file contents
        '''
        contents = {}
        
        for filename, file_path in self.memory.items():
            try:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents[filename] = f.read()
                else:
                    contents[filename] = f"[File does not exist: {file_path}]"
            except Exception as e:
                contents[filename] = f"[Error reading file: {str(e)}]"
        
        self.update_activity()
        return contents

    def _get_codebase_structure_string(self) -> str:
        '''
        Returns a tree-style ASCII representation of the codebase starting at the project root directory (ROOT_DIR from src).
        '''
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
        '''
        Get current agent status.
        
        Returns:
            Dict[str, Any]: Status information including:
                - Basic agent info (type, path)
                - Active state and current task
                - Memory and context usage
                - Queue and stall state
        '''
        self.update_activity()
        return {
            'agent_type': 'manager' if self.is_manager else 'coder',
            'path': str(self.scope_path),
            'personal_file': str(self.personal_file) if self.personal_file else None,
            'is_active': self.is_active,
            'active_task': str(self.active_task) if self.active_task else None,
            'memory_files': len(self.memory),
            'context_entries': len(self.context),
            'prompt_queue_size': len(self.prompt_queue),
            'stall': self.stall,
            'active_children': getattr(self, 'active_children', {}).__len__() if hasattr(self, 'active_children') else 0,
            'active_ephemeral_agents': len(self.active_ephemeral_agents),
        }
    
    def __repr__(self) -> str:
        '''
        String representation of the agent.
        
        Returns:
            str: Agent representation including type, path, and active state
        '''
        agent_type = 'Manager' if self.is_manager else 'Coder'
        return f"{agent_type}Agent(path={self.scope_path}, active={self.is_active})"

    def update_activity(self):
        self.last_activity = time.time()

    async def _watchdog_loop(self):
        while True:
            await asyncio.sleep(10)
            if self.is_active and not getattr(self, 'active_children', {}) and not self.active_ephemeral_agents:
                if time.time() - self.last_activity > AGENT_TIMEOUT_SECONDS:
                    await self.handle_timeout()
                    break

    async def handle_timeout(self):
        self.deactivate()
        if self.parent:
            await self.parent.process_task(
                f"Agent timed out after {AGENT_TIMEOUT_SECONDS} seconds of inactivity with no active children or ephemeral agents."
            )