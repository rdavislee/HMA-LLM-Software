"""
Base Agent class that all agents inherit from.

This module provides the core functionality for all agents in the system, including:
- Message handling and communication
- File reading and writing capabilities
- Context management
- Task processing
- Terminal command execution

Manager agents additionally implement:
- Child agent management
- Task delegation
- Directory-level operations
"""

# Standard library imports
import os
import json
import asyncio
import uuid
import time
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union

# Local imports
from ..messages.protocol import (
    Message, TaskMessage, ResultMessage, MessageType
)
from ..llm.base import BaseLLMClient

# Global constants
ALLOWED_COMMANDS = {
    'ls', 'dir', 'cat', 'type', 'grep', 'find', 'git status', 'git log',
    'python -m py_compile', 'npm test', 'pytest', 'flake8', 'black --check'
}

MAX_CONTEXT_DEPTH = 3
DEFAULT_MAX_CONTEXT_SIZE = 8000

class BaseAgent(ABC):
    '''
    Base agent class providing core functionality for all agents in the system.
    
    Each agent has:
    - agent_id: Unique identifier for this agent
    - path: The path this agent is responsible for (file for coder, directory for manager)
    - personal_file: The one file this agent can modify (code file for coder, README for manager)
    - parent_id: ID of the parent agent (None for root)
    - llm_client: LLM client for generating responses
    
    The agent maintains:
    - Active state and current task
    - Message queue for communication
    - Short-term memory and context cache
    - Task tracking (active and completed)
    '''

    def __init__(
        self,
        path: str,
        task: TaskMessage,
        parent_path: Optional[str] = None,
        children_paths: Optional[List[str]] = None,
        llm_client: Optional[BaseLLMClient] = None,
        max_context_size: int = DEFAULT_MAX_CONTEXT_SIZE
    ) -> None:
        """Initialize a new agent.
        
        Args:
            path: Path this agent is responsible for
            parent_id: Optional ID of the parent agent
            llm_client: Optional LLM client for generating responses
            max_context_size: Maximum size of context to maintain
        """
        self.path = path
        self.parent_path = parent_path
        self.children_paths = children_paths
        self.active_children = [] # consider Set

        self.llm_client = llm_client
        self.max_context_size = max_context_size

        # Agent State
        self.is_active = False
        self.prompt_queue: List[str] = []
        self.stall = False

        # Short-term Memory (cleared after task completion)
        self.memory: Dict[str, Path] = {}
        self.context_cache: Dict[str, str] = {}
        self.personal_file: Optional[Path] = None

        # Task Tracking
        self.active_task = task

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
        
        Args:
            task: The task to process
            
        Raises:
            RuntimeError: If agent is already active
            ValueError: If task is invalid
        '''
        async with self._activation_lock:
            if self.is_active:
                raise RuntimeError(
                    f"Agent {self.agent_id} is already active with task {self.current_task_id}"
                )
            
            self.is_active = True
            self.current_task_id = task.task_id
            self.active_tasks[task.task_id] = {
                'task': task,
                'start_time': time.time(),
                'status': 'active'
            }

            # Load context for this task
            await self._load_context()

            try:
                result = await self.process_task(task)
                await self._send_result(task, result, success=True)
            
            except Exception as e:
                self.error_count += 1
                await self._send_result(task, str(e), success=False)

    async def deactivate(self) -> None:
        '''
        Deactivate the agent and clean up memory.
        Manager agents must ensure all children are deactivated first.
        '''
        self.is_active = False

        # Mark task as completed
        if self.current_task_id:
            self.completed_tasks.append(self.current_task_id)
            if self.current_task_id in self.active_tasks:
                self.active_tasks[self.current_task_id]['status'] = 'completed'
                del self.active_tasks[self.current_task_id]
        
        # Clear short-term memory
        self.memory.clear()
        self.context_cache.clear()
        self.current_task_id = None

    @abstractmethod
    async def process_task(self, task: TaskMessage) -> Any:
        '''
        Process a task -> implemented in subclasses.
        
        Args:
            task: The task to process
            
        Returns:
            Any: The result of processing the task
            
        Raises:
            Exception: If task processing fails
        '''
        pass

    async def read_file(self, file_path: str) -> str:
        '''
        Read any file in the codebase for context.
        Results are cached during the active period.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            str: The file contents
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
            Exception: For other errors
        '''
        try:
            full_path = Path(file_path).resolve()

            # Check cache first
            cache_key = str(full_path)
            if cache_key in self.context_cache:
                return self.context_cache[cache_key]

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cache for this activation period
            self.context_cache[cache_key] = content
            return content
        
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {str(e)}")
        
    async def update_personal_file(self, content: str) -> None:
        '''
        Update this agent's personal file with new content.
        This is the ONLY file the agent can modify.
        
        Args:
            content: The new content to write
            
        Raises:
            RuntimeError: If agent has no personal file
            PermissionError: If file cannot be written
            Exception: For other errors
        '''
        if not self.personal_file:
            raise RuntimeError(f"Agent {self.agent_id} has no personal file to update")
        
        try:
            # Ensure parent directory exists
            self.personal_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.personal_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update cache if we have it cached
            cache_key = str(self.personal_file)
            if cache_key in self.context_cache:
                self.context_cache[cache_key] = content
                
        except PermissionError:
            raise PermissionError(f"Permission denied writing to file: {self.personal_file}")
        
        except Exception as e:
            raise Exception(f"Failed to update personal file: {str(e)}")

    async def run_command(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        '''
        Run a terminal command with limited permissions.
        Only commands in ALLOWED_COMMANDS are permitted.
        
        Args:
            command: The command to run
            cwd: Optional working directory
            
        Returns:
            Dict[str, Any]: Command output with stdout, stderr, and return code
            
        Raises:
            PermissionError: If command is not allowed
            subprocess.TimeoutExpired: If command times out
            Exception: For other errors
        '''
        command_start = command.split()[0]
        if not any(command.startswith(allowed) for allowed in ALLOWED_COMMANDS):
            raise PermissionError(f"Command not allowed: {command}")
        
        try:
            # Default working directory is the agent's scope
            if cwd is None:
                cwd = str(self.scope_path.parent if self.is_coder else self.scope_path)
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        
        except subprocess.TimeoutExpired:
            raise subprocess.TimeoutExpired(command, 30)
        except Exception as e:
            raise Exception(f"Command failed: {str(e)}")

    async def send_message(self, recipient_id: str, message: Message) -> None:
        '''
        Send a message to another agent (typically the parent).
        
        Args:
            recipient_id: ID of the recipient agent
            message: The message to send
        '''
        self.prompt_queue.append(message)
    
    async def receive_messages(self) -> List[Message]:
        '''
        Receive and process pending messages in order they were received.
        
        Returns:
            List[Message]: List of pending messages
        '''
        messages = self.prompt_queue.copy()
        self.prompt_queue.clear()
        return messages
    
    async def _send_result(self, task: TaskMessage, result: Any, success: bool) -> None:
        '''
        Send result back to parent agent and deactivate.
        
        Args:
            task: The completed task
            result: The task result
            success: Whether the task succeeded
        '''
        if self.parent_id:
            result_message = ResultMessage(
                message_type=MessageType.RESULT,
                sender_id=self.agent_id,
                recipient_id=self.parent_id,
                content={'result': result},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                task_id=task.task_id,
                success=success,
                result_data=result
            )
            await self.send_message(self.parent_id, result_message)
        
        # Always deactivate after sending result
        await self.deactivate()

    async def _load_context(self) -> None:
        '''
        Load relevant context for the current task.
        Always includes personal file and codebase structure.
        '''
        # Load personal file content
        if self.personal_file and self.personal_file.exists():
            self.memory['personal_file_content'] = await self.read_file(str(self.personal_file))
        else:
            self.memory['personal_file_content'] = ""

        # Load codebase structure
        self.memory['codebase_structure'] = await self._get_codebase_structure_string()
        
        # Store allowed commands for reference
        self.memory['allowed_commands'] = list(ALLOWED_COMMANDS)

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

    async def get_context_string(self) -> str:
        '''
        Get a formatted string of all context for LLM consumption.
        
        Returns:
            str: Formatted context string
        '''
        context_parts = [
            f"Agent ID: {self.agent_id}",
            f"Agent Type: {'Manager' if self.is_manager else 'Coder'}",
            f"Scope Path: {self.scope_path}",
            f"Personal File: {self.personal_file}",
            "",
            "Allowed Terminal Commands:",
            "\n".join(f"  - {cmd}" for cmd in sorted(ALLOWED_COMMANDS)),
            "",
            "Codebase Structure:",
            self.memory.get('codebase_structure', 'Not loaded'),
            "",
            "Personal File Content:",
            self.memory.get('personal_file_content', 'No content'),
        ]
        
        return "\n".join(context_parts)

    def get_status(self) -> Dict[str, Any]:
        '''
        Get current agent status.
        
        Returns:
            Dict[str, Any]: Status information including:
                - Basic agent info (ID, type, path)
                - Active state and current task
                - Task statistics
                - Memory usage
                - Error count
        '''
        return {
            'agent_id': self.agent_id,
            'agent_type': 'manager' if self.is_manager else 'coder',
            'path': str(self.scope_path),
            'personal_file': str(self.personal_file) if self.personal_file else None,
            'is_active': self.is_active,
            'current_task': self.current_task_id,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'memory_size': len(self.memory),
            'cached_files': len(self.context_cache),
            'error_count': self.error_count
        }
    
    def __repr__(self) -> str:
        '''
        String representation of the agent.
        
        Returns:
            str: Agent representation including ID, path, and active state
        '''
        agent_type = 'Manager' if self.is_manager else 'Coder'
        return f"{agent_type}Agent(id={self.agent_id}, path={self.scope_path}, active={self.is_active})"