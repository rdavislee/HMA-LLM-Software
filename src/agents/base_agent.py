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
from ..messages.protocol import (
    Message, TaskMessage, ResultMessage, MessageType
)
from ..llm.base import BaseLLMClient

# Global constants
MAX_CONTEXT_DEPTH = 3
DEFAULT_MAX_CONTEXT_SIZE = 8000

class BaseAgent(ABC):
    '''
    Base agent class providing core functionality for all agents in the hierarchical system.
    
    Each agent has:
    - path: The path this agent is responsible for (file for coder, directory for manager)
    - personal_file: The one file this agent can modify (code file for coder, README for manager)
    - parent_path: Path of the parent agent (None for root)
    - children_paths: List of child agent paths (for managers)
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
        parent_path: Optional[str] = None,
        children_paths: Optional[List[str]] = None,
        llm_client: Optional[BaseLLMClient] = None,
        max_context_size: int = DEFAULT_MAX_CONTEXT_SIZE
    ) -> None:
        """Initialize a new agent.
        
        Args:
            path: Path this agent is responsible for
            parent_path: Optional path of the parent agent
            children_paths: Optional list of child agent paths
            llm_client: Optional LLM client for generating responses
            max_context_size: Maximum size of context to maintain
        """
        self.path = Path(path).resolve()
        self.parent_path = Path(parent_path).resolve() if parent_path else None
        self.children_paths = [Path(p).resolve() for p in (children_paths or [])]
        self.active_children = []

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
        Set the personal file this agent can modify.
        For coders: the code file they manage
        For managers: their README.md in the parent directory
        '''
        if self.path.is_file() or not self.path.exists():
            # Coder agent - personal file is the code file
            self.personal_file = self.path
        else:
            # Manager agent - personal file is README in parent directory
            self.personal_file = self.path.parent / f"{self.path.name}_README.md"

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

    async def activate(self, task: TaskMessage) -> None:
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
        
        self.is_active = True
        self.active_task = task

    async def deactivate(self) -> None:
        '''
        Deactivate the agent and clean up memory.
        Manager agents must ensure all children are deactivated first.
        
        Raises:
            RuntimeError: If a child is still active
        '''
        if self.active_children:
            raise RuntimeError("Cannot deactivate agent with active children")
        
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

    async def api_call(self) -> None:
        '''
        Make an API call with current context and memory.
        This is the core method that handles LLM interaction.
        '''
        # Set stall to true to prevent concurrent API calls
        self.stall = True
        
        # Load context and memory
        await self._load_context()
        
        # Concatenate all prompts in queue (numbered)
        # NOTE: Use Jinja here!!
        numbered_prompts = []
        for i, prompt in enumerate(self.prompt_queue, 1):
            numbered_prompts.append(f"{i}. {prompt}")
        
        full_prompt = "\n".join(numbered_prompts)
        
        # Get context string for LLM
        context_string = await self.get_context_string()
        
        # Make API call
        if self.llm_client:
            response = await self.llm_client.generate_response(
                prompt=full_prompt,
                context=context_string
            )
            
            # Add to context (prompt -> response)
            self.context[full_prompt] = response
            
            # Process response through prompter
            await self._process_response(response)
        
        # Clear prompt queue
        self.prompt_queue.clear()

    async def _process_response(self, response: str) -> None:
        '''
        Process the LLM response through the prompter.
        This will be implemented by subclasses.
        
        Args:
            response: The LLM response to process
        '''
        # This will be implemented by subclasses to handle specific response processing
        pass

    async def read_file(self, file_path: str) -> None:
        '''
        Add a file to memory for reading.
        The file contents will be automatically loaded during API calls.
        
        Args:
            file_path: Path to the file to add to memory
        '''
        full_path = Path(file_path).resolve()
        filename = full_path.name
        self.memory[filename] = full_path

    async def _load_context(self) -> None:
        '''
        Load relevant context for the current task.
        Always includes personal file and codebase structure.
        '''
        # Always add personal file to memory
        if self.personal_file:
            self.memory['personal_file'] = self.personal_file

    async def _get_memory_contents(self) -> Dict[str, str]:
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

    async def _get_codebase_structure_string(self) -> str:
        '''
        Gets a string representation of the codebase structure that LLMs can understand.
        
        Returns:
            str: Tree-like representation of the codebase structure
        '''
        # Find project root
        current = self.scope_path
        while current.parent != current:
            if any((current / marker).exists() for marker in ['.git', 'requirements.txt', 'package.json', 'Cargo.toml']):
                break
            current = current.parent
        
        project_root = current
        
        def build_tree_string(
            path: Path,
            prefix: str = "",
            max_depth: int = MAX_CONTEXT_DEPTH,
            current_depth: int = 0
        ) -> str:
            '''
            Build a tree-like string representation of directory structure.
            
            Args:
                path: Current directory path
                prefix: Current indentation prefix
                max_depth: Maximum directory depth to traverse
                current_depth: Current directory depth
                
            Returns:
                str: Tree-like string representation
            '''
            if current_depth >= max_depth:
                return f"{prefix}...\n"
            
            result = ""
            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                for i, item in enumerate(items):
                    if item.name.startswith('.'):
                        continue
                    
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    
                    if item.is_dir():
                        result += f"{prefix}{current_prefix}{item.name}/\n"
                        result += build_tree_string(item, next_prefix, max_depth, current_depth + 1)
                    else:
                        # Include file size for context
                        size = item.stat().st_size
                        size_str = f"{size:,}" if size < 1024 else f"{size/1024:.1f}K"
                        result += f"{prefix}{current_prefix}{item.name} ({size_str})\n"
            
            except PermissionError:
                result += f"{prefix}[Permission Denied]\n"
            
            return result
        
        structure = f"Project Structure (root: {project_root.name}):\n"
        structure += build_tree_string(project_root)
        
        # Add current agent's location in the structure
        try:
            rel_path = self.scope_path.relative_to(project_root)
            structure += f"\nCurrent agent location: {rel_path}"
        except ValueError:
            structure += f"\nCurrent agent location: {self.scope_path}"
        
        return structure

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
            'active_children': len(self.active_children)
        }
    
    def __repr__(self) -> str:
        '''
        String representation of the agent.
        
        Returns:
            str: Agent representation including type, path, and active state
        '''
        agent_type = 'Manager' if self.is_manager else 'Coder'
        return f"{agent_type}Agent(path={self.scope_path}, active={self.is_active})"