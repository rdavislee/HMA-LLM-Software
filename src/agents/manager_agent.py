"""
Manager Agent - coordinates work within a folder.
Will implement:
- Task breakdown logic
- Delegation to child agents
- Progress tracking
- Result aggregation
"""

import os
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from enum import Enum

from .base_agent import BaseAgent
from ..messages.protocol import (
    Message, TaskMessage, ResultMessage, MessageType
)
from ..llm.base import BaseLLMClient

class ManagerCommand(Enum):
    """Commands that a manager agent can exercise."""
    DELEGATE = "DELEGATE"
    CREATE_FILE = "CREATE_FILE"
    DELETE_FILE = "DELETE_FILE"
    WAIT = "WAIT"
    READ_FILE = "READ_FILE"
    RUN_COMMAND = "RUN_COMMAND"
    COMPLETE = "COMPLETE"
    UPDATE_README = "UPDATE_README"

class ManagerAgent(BaseAgent):
    """
    Manager agent that coordinates work within a directory.

    Extends BaseAgent with capabilities to:
    - Delegate tasks to child agents (files and subdirectories)
    - Create and delete files within the managed directory
    - Manage concurrent task execution
    - Track progress and aggregate results from children
    - Wait for child completion or re-task children
    """

    def __init__(
        self,
        path: str,
        parent_path: Optional[str] = None,
        children_paths: Optional[List[str]] = None,
        llm_client: Optional[BaseLLMClient] = None,
        max_content_size: int = 8000
    ) -> None:
        """
        Initialize a ManagerAgent.

        Args:
            path: Directory path this manager is responsible for
            parent_path: Optional path of the parent agent
            children_paths: Optional list of child agent paths
            llm_client: Optional LLM client for generating responses
            max_content_size: Maximum size of context to maintain
        """
        super.__init__(path, parent_path, children_paths, llm_client, max_content_size)

        # Manager-specific State
        self.delegated_tasks: Dict[str, TaskMessage] = {}
        self.child_results: Dict[str, ResultMessage] = {}
        self.waiting_for_children: Set[str] = set()
        self.completed_children: Set[str] = set()

        # Ensure path is a directory
        if not self.path.is_dir() and self.path.exists():
            raise ValueError(f"ManagerAgent can only manage directories, not files: {path}")
        
    async def delegate_task(self, child_path: str, task_description: str) -> None:
        """
        Delegates a task to a child agent.

        Args:
            child_path: Path of the child agent to delegate to
            task_description: Description of the task being delegated
        """
        child_path_obj = Path(child_path).resolve()

        # Verify child is in our children list
        if child_path_obj not in self.children_paths:
            raise ValueError(f"Path {child_path} is not a child of this manager.")
        
        # Create task message
        task = TaskMessage(
            id=f"{self.active_task.id}-{len(self.delegated_tasks)}",
            type=MessageType.TASK,
            sender=str(self.path),
            receiver=str(child_path_obj),
            content=task_description,
            metadata={"parent_task_id": self.active_task_id}
        )

        # Track delegation
        self.delegated_tasks[str(child_path_obj)] = task
        self.waiting_for_children.add(str(child_path_obj))
        self.active_children.append(str(child_path_obj))

    async def create_file(self, filename: str, initial_content: str = "") -> Path:
        """
        Create a new file in the managed directory.

        Args:
            filename: Name of the file to create
            initial_content: Initial content for the file

        Returns:
            Path: Path to the created file
        """
        file_path = self.path / filename

        # Ensure we're not overwriting the existing file
        if file_path.exists():
            raise FileExistsError(f"File already exists: {file_path}")
        
        # Create the file
        file_path.write_text(initial_content, encoding='utf-8')

        # Add to children paths if it's a code file
        if file_path.suffix in ['.py', '.ts', '.js', '.java', '.cpp', '.c']:
            self.children_paths.append(file_path)

        return file_path
    
    async def delete_file(self, filename: str) -> None:
        """
        Delete a file from the managed directory.
        
        Args:
            filename: Name of the file to delete
        """
        file_path = self.path / filename

        # Ensure file exists and is in our directory
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_relative_to(self.path):
            raise ValueError(f"Cannot delete file outside managed directory: {file_path}")
        
        # Remove from children paths if present
        if file_path in self.children_paths:
            self.children_paths.remove(file_path)

        # Delete the file [Important]
        file_path.unlink()

    async def wait_for_children(self, specific_children: Optional[List[str]] = None) -> None:
        """
        Wait for children agents to complete their tasks.

        Args:
            specific_children: Optional list of specific child paths to wait for.
                If None, waits for all active children.
        """
        if specific_children:
            children_to_wait = set(specific_children)
        else:
            children_to_wait = self.waiting_for_children.copy()

        self.stall = True

    async def receive_child_result(self, child_path: str, result: ResultMessage) -> None:
        """
        Receive and process a result from a child agent.

        Args:
            child_path: Path of the child agent
            result: Result message from the child
        """
        # Store result
        self.child_results[child_path] = result

        # Update tracking
        self.waiting_for_children.discard(child_path)
        self.completed_children.add(child_path)

        if child_path in self.active_children:
            self.active_children.remove(child_path)

        # If no more children to wait for, unstall
        if not self.waiting_for_children:
            self.stall = False

            # If we have prompts queued, process them
            if self.prompt_queue:
                await self.api_call()
    
    async def _process_response(self, response: str) -> None:
        """
        Process the LLM response and execute the manager commands.

        Args:
            response: The LLM response containing commands to execute
        """
        # SIMPLIFIED PARSER
        # NOTE: Use manager language here
        raise NotImplementedError(f"Not implemented yet!")
    
    async def _complete_task(self, summary: str) -> None:
        """
        Complete the current task and prepare the result for parent.

        Args:
            summary: Summary of what was accomplished
        """
        if not self.active_task:
            return
        
        # Aggregate results from children
        aggregated_results = {
            "summary": summary,
            "children_results": {}
        }

        for child_path, result in self.child_results.items():
            aggregated_results["children_results"][child_path] = {
                "status": result.status,
                "content": result.content
            }

        # Create result message
        result = ResultMessage(
            id=f"{self.active_task.id}-result",
            type=MessageType.RESULT,
            sender=str(self.path),
            receiver=str(self.parent_path) if self.parent_path else "system",
            content=json.dumps(aggregated_results),
            status="success",
            metadata={"task_id": self.active_task.id}
        )

        # NOTE: We would want to send the result to the parent
        print(result)

    async def get_context_string(self) -> str:
        """
        Get context string for LLM including manager-specific information.

        Returns:
            str: Formatted context string
        """
        # Start with base context
        context_parts = [
            "You are a Manager Agent responsible for coordinating work within a directory.",
            f"Your directory: {self.path}",
            f"Your personal README file: {self.personal_file}",
            "",
            "Available commands:",
            "- DELEGATE: child_path | task_description",
            "- CREATE_FILE: filename | initial_content",
            "- DELETE_FILE: filename",
            "- WAIT: child_paths (comma-separated) or ALL",
            "- READ_FILE: filepath",
            "- RUN_COMMAND: shell_command",
            "- UPDATE_README: content",
            "- COMPLETE: summary",
            "",
            "Current task:",
            self.active_task.content if self.active_task else "None",
            "",
            "Children in this directory:",
        ]

        # Add childre
        for child in self.children_paths:
            status = "active" if str(child) in self.active_children else "idle"
            context_parts.append(f"  - {child.name} ({status})")
        
        # Add delegated tasks
        if self.delegated_tasks:
            context_parts.extend(["", "Delegated tasks:"])
            for child_path, task in self.delegated_tasks.items():
                status = "completed" if child_path in self.completed_children else "in progress"
                context_parts.append(f"  - {Path(child_path).name}: {task.content} ({status})")