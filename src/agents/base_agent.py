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

# Local imports
from src.messages.protocol import (
    Message, TaskMessage, ResultMessage, MessageType
)
from src.llm.base import BaseLLMClient

# Global constants
MAX_CONTEXT_DEPTH = 3
DEFAULT_MAX_CONTEXT_SIZE = 8000

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
    - Context: Dictionary of prompts to responses (API call history)
    - Stall state for managing dependencies
    '''

    def __init__(
        self,
        path: str,
        parent: Optional["BaseAgent"] = None,
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
        self.parent = parent

        self.llm_client = llm_client
        self.max_context_size = max_context_size

        # Agent State
        self.is_active = False
        self.prompt_queue: List[str] = []
        self.stall = False

        # Memory: Dictionary of filenames to file paths
        self.memory: Dict[str, Path] = {}
        
        # Context: Dictionary of prompts to responses (API call history)
        self.context: Dict[str, str] = {}
        
        # Personal file (always set, never optional)
        self.personal_file: Path = None

        # Task Tracking
        self.active_task = None

        # Set personal file based on agent type
        self._set_personal_file()

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
        self.is_active = True
        self.active_task = task

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
        
        self.is_active = False
        self.active_task = None
        
        # Clear memory and context
        self.memory.clear()
        self.context.clear()
        self.prompt_queue.clear()
        self.stall = False

    async def process_task(self, prompt: str) -> None:
        '''
        Process a task by adding prompt to queue and calling API if not stalled.
        
        Args:
            prompt: The prompt to process
        '''
        self.prompt_queue.append(prompt)
        
        if not self.stall:
            await self.api_call()

    @abstractmethod
    async def api_call(self) -> None:
        '''
        Make an API call with current context and memory.
        This method must be implemented by subclasses to handle
        their specific Jinja templates and response processing.
        '''
        pass

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
        
        return contents

    def _get_codebase_structure_string(self) -> str:
        '''
        TODO: Implement a function that returns the codebase structure from the root directory in string form.
        This should provide a tree-like or otherwise useful representation of the project for LLM context.
        '''
        return "[Codebase structure not implemented yet]"

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
        }
    
    def __repr__(self) -> str:
        '''
        String representation of the agent.
        
        Returns:
            str: Agent representation including type, path, and active state
        '''
        agent_type = 'Manager' if self.is_manager else 'Coder'
        return f"{agent_type}Agent(path={self.scope_path}, active={self.is_active})"