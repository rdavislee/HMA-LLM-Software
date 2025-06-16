"""
Base Agent class that all agents inherit from.
Will implement:
- Message handling loop
- File reading/writing capabilities  
- Communication with parent/children
- Context management
"""

import os
import json
import asyncio
import uuid
import time
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

from ..messages.protocol import (
    Message, TaskMessage, ResultMessage, QueryMessage, StatusMessage, 
    MessageType, TaskType
)
from ..llm.base import BaseLLMClient

class BaseAgent(ABC):
    '''
    Base agent class providing core functionality for all agents in the system.
    '''

    def __init__(
        self,
        agent_id: str,
        path: str,
        parent_id: Optional[str] = None,
        llm_client: Optional[BaseLLMClient] = None,
        max_context_size: int = 8000
    ):
        self.agent_id = agent_id
        self.path = Path(path).resolve()
        self.parent_id = parent_id
        self.llm_client = llm_client
        self.max_context_size = max_context_size

        # Agent State
        self.is_active = False
        self.current_task_id: Optional[str] = None
        self.children: Dict[str, 'BaseAgent'] = {}
        self.message_queue: List[Message] = []

        # Short-term Memory (cleared after task completion)
        self.memory: Dict[str, Any] = {}
        self.context_cache: Dict[str, str] = {}

        # Task Tracking
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[str] = []

        # Initialize README path for this agent
        self.readme_path = self.path / "README.md" if self.path.is_dir() else self.path.parent / f"{self.path.stem}_README.md"

    @property
    def scope_path(self) -> Path:
        '''
        Get the poath this agent is responsible for.
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
    

    # -------------------------------------------------
    # CORE AGENT LIFECYCLE
    # -------------------------------------------------

    async def activate(self, task: TaskMessage) -> None:
        '''
        Activate the agent to work on a task.
        '''
        self.is_active = True
        self.current_task_id = task.task_id
        self.active_tasks[task.task_id] = {
            'task': task,
            'start_time': time.time(),
            'status': 'active'
        }

        # Load context for this task, then process the task
        await self._load_context()

        try:
            result = await self.process_task(task)
            await self._send_result(task, result, success=True)
        
        except Exception as e:
            await self._send_result(task, str(e), success=False)

        finally:
            await self.deactivate()

    async def deactivate(self) -> None:
        '''
        Deactivate the agent and clean up memory
        '''
        self.is_active = False

        # Update README
        if self.current_task_id:
            await self._update_readme()
            self.completed_tasks.append(self.current_task_id)
            if self.current_task_id in self.active_tasks:
                del self.active_tasks[self.current_task_id]
        
        # Clear short-term memory
        self.memory.clear()
        self.context_cache.clear()
        self.current_task_id = None

    @abstractmethod
    async def process_task(self, task: TaskMessage) -> Any:
        '''
        Process a task -> implemented in subclasses
        '''
        pass


    # -------------------------------------------------
    # FILE OPERATIONS
    # -------------------------------------------------

    async def read_file(self, file_path: str) -> str:
        '''
        Read any file in the codebase for context
        '''
        try:
            full_path = Path(file_path).resolve()

            cache_key = str(full_path)
            if cache_key in self.context_cache:
                return self.context_cache[cache_key]

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.context_cache[cache_key] = content
            return content
        
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {str(e)}")
        
    async def write_file(self, file_path: str, content: str) -> None:
        '''
        Write to a file within this agent's scope
        '''
        target_path = Path(file_path).resolve()

        if not self._is_within_scope(target_path):
            raise PermissionError(f"Agent {self.agent_id} cannot write outside its scope: {file_path}")
        
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)

    async def delete_file(self, file_path: str) -> None:
        '''
        Delete a file within this agent's scope
        '''
        target_path = Path(file_path).resolve()

        if not self._is_within_scope(target_path):
            raise PermissionError(f"Agent {self.agent_id} cannot delete outside its scope: {file_path}")
        
        if target_path.exists():
            target_path.unlink()

    def _is_within_scope(self, target_path: str) -> bool:
        '''
        Check if a path is within the scope of this agent
        '''
        try:
            if self.is_manager:
                target_path.relative_to(self.scope_path)
                return True
            else:
                return target_path == self.scope_path
        
        except ValueError:
            return False
        

    # -------------------------------------------------
    # TERMINAL OPERATIONS
    # -------------------------------------------------

    async def run_command(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        '''
        Run a terminal command with limited permissions
        '''
        allowed_commands = {
            'ls', 'dir', 'cat', 'type', 'grep', 'find', 'git status', 'git log',
            'python -m py_compile', 'npm test', 'pytest', 'flake8', 'black --check'
        }

        command_start = command.split()[0]
        if not any(command.startswith(allowed) for allowed in allowed_commands):
            raise PermissionError(f"Command not allowed: {command}")
        
        try:
            cwd = cwd or str(self.scope_path.parent if self.is_coder else self.scope_path)
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
            raise Exception(f"Command timed out: {command}")
        
        except Exception as e:
            raise Exception(f"Command failed: {str(e)}")
        

    # -------------------------------------------------
    # Communication
    # -------------------------------------------------

    async def send_message(self, recipient_id: str, message: Message) -> None:
        '''
        Send a message to another agent.
        '''
        # NOTE: In real implementation, this would be a message broker
        self.message_queue.append(message)
    
    async def receive_messages(self) -> List[Message]:
        '''
        Receive and process pending messages.
        '''
        messages = self.message_queue.copy()
        self.message_queue.clear()
        return messages
    
    async def delegate_task(self, child_id: str, task: TaskMessage) -> ResultMessage:
        '''
        Delegate a task to a child agent.
        '''
        if child_id not in self.children:
            raise ValueError(f"Unknown child agent: {child_id}")
        
        child_agent = self.children[child_id]
        await child_agent.activate(task)

        return ResultMessage(
            message_type=MessageType.RESULT,
            sender_id=child_id,
            recipient_id=self.agent_id,
            content={},
            timestamp=time.time(),
            message_id=str(uuid.uuid4()),
            task_id=task.task_id,
            success=True,
            result_data="Task completed"
        )
    
    async def _send_result(self, task: TaskMessage, result: Any, success: bool) -> None:
        '''
        Send result back to parent agent.
        '''
        if self.parent_id:
            result_message = ResultMessage(
                message_type=MessageType.RESULT,
                sender_id=self.agent_id,
                recipient_id=self.parent_id,
                content={},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                task_id=task.task_id,
                success=success,
                result_data=result
            )
            await self.send_message(self.parent_id, result_message)


    # -------------------------------------------------
    # CONTEXT MANAGEMENT
    # -------------------------------------------------

    async def _load_context(self) -> None:
        '''
        Load relevant context for the current task.
        '''
        if self.readme_path.exists():
            self.memory['readme'] = await self.read_file(str(self.readme_path))

        self.memory['codebase_structure'] = await self._get_codebase_structure()

    async def _get_codebase_structure(self) -> Dict[str, Any]:
        '''
        Gets the structure of the codebase.
        '''
        structure = {}

        # Start from project root
        current = self.scope_path
        while current.parent != current:
            if any((current / marker).exists() for marker in ['.git', 'requirements.txt', 'package.json', 'Cargo.toml']):
                break
            current = current.parent
        
        def build_structure(path: Path, max_depth: int = 3) -> Dict[str, Any]:
            '''
            Recursive function to help retrieve the codebase structure.
            '''
            if max_depth <= 0:
                return {}
            
            items = {}
            try:
                for item in path.iterdir():
                    if item.name.startswith('.'):
                        continue

                    if item.is_dir():
                        items[item.name] = {
                            'type': 'directory',
                            'children': build_structure(item, max_depth - 1)
                        }
                    
                    else:
                        items[item.name] = {
                            'type': 'file',
                            'size': item.stat().st_size
                        }
            
            except PermissionError:
                pass

            return items
        
        return build_structure(current)
    

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------

    async def _update_readme(self) -> None:
        '''
        Update the README with information about completed work.
        '''
        if not self.current_task_id or self.current_task_id not in self.active_tasks:
            return
        
        task_info = self.active_tasks[self.current_task_id]
        task = task_info['task']

        # Generate update using LLM if available
        if self.llm_client:
            readme_content = ""
            if self.readme_path.exists():
                readme_content = await self.read_file(str(self.readme_path))

            system_prompt = """You are updating a README file for an AI agent.
            Add a brief entry about what was accomplished, following this format:
            
            ## Recent Work
            - [TIMESTAMP] [TASK_TYPE]: Brief description of what was done

            Keep it concise and focused on the outcome."""

            messages = [
                {"role": "user", "content": f"""
                Current README content:
                 {readme_content}

                Task completed:
                - Type: {task.task_type.value}
                - Content: {task.content}
                - Agent: {self.agent_id}

                Please update the README with this information.
                """}
            ]

            try:
                updated_content = await self.llm_client.generate_response(
                    messages, system_prompt, temperature=0.3
                )
                await self.write_file(str(self.readme_path), updated_content)

            except Exception as e:
                await self._simple_readme_update(task)

        else:
            await self._simple_readme_update(task)

    async def _simple_readme_update(self, task: TaskMessage) -> None:
        '''
        Simple README update without LLM.
        '''
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"- [{timestamp}] {task.task_type.value}: {task.content.get('description', 'Task completed')}\n"

        try:
            if self.readme_path.exists():
                content = await self.read_file(str(self.readme_path))
                if "## Recent Work" in content:
                    # Add to existing section
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip() == "## Recent Work":
                            lines.insert(i + 1, entry)
                            break
                        content = '\n'.join(lines)
                else:
                    # Add to new section
                    content += f"\n\n## Recent Work\n{entry}"
            else:
                # Create new README
                content = f"# {self.agent_id}\n\nAgent responsible for: {self.scope_path}\n\n## Recent Work\n{entry}"
            
            await self.write_file(str(self.readme_path), content)
        
        except Exception as e:
            print(f"Failed to update README: {e}")
    
    # -------------------------------------------------
    # AGENT MANAGEMENT
    # -------------------------------------------------

    def add_child(self, child_agent: 'BaseAgent') -> None:
        '''
        Add a child agent.
        '''
        self.children[child_agent.agent_id] = child_agent
        child_agent.parent_id = self.agent_id
    
    def remove_child(self, child_id: str) -> None:
        '''
        Remove a child agent.
        '''
        if child_id in self.children:
            self.children[child_id].parent_id = None
            del self.children[child_id]
    

    # -------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        '''
        Get current agent status.
        '''
        return {
            'agent_id': self.agent_id,
            'path': str(self.scope_path),
            'is_active': self.is_active,
            'current_task': self.current_task_id,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'children_count': len(self.children),
            'memory_size': len(self.memory)
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, path={self.scope_path}, active={self.is_active})"