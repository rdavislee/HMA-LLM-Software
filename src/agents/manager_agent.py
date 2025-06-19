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
        parent: Optional[BaseAgent] = None,
        children: Optional[List[BaseAgent]] = None,
        llm_client: Optional[BaseLLMClient] = None,
        max_content_size: int = 8000
    ) -> None:
        """
        Initialize a ManagerAgent.

        Args:
            path: Directory path this manager is responsible for
            parent: Optional parent agent object
            children: Optional list of child agent objects
            llm_client: Optional LLM client for generating responses
            max_content_size: Maximum size of context to maintain
        """
        super().__init__(path, parent, llm_client, max_content_size)

        self.children = children or []

        # Manager-specific State
        self.active_children: Dict[BaseAgent, TaskMessage] = {}  # key: child agent, value: Task or task string

        # Ensure path is a directory
        if not self.path.is_dir() and self.path.exists():
            raise ValueError(f"ManagerAgent can only manage directories, not files: {path}")
        
    def delegate_task(self, child: "BaseAgent", task_description: str) -> None:
        """
        Delegates a task to a child agent.

        Args:
            child: Child agent object to delegate to
            task_description: Description of the task being delegated
        """
        if child not in self.children:
            raise ValueError(f"Agent {child} is not a child of this manager.")
        self.active_children[child] = task_description

    def receive_child_result(self, child: "BaseAgent", result: Any) -> None:
        """
        Receive and process a result from a child agent.

        Args:
            child: Child agent object
            result: Result message from the child
        """
        self.active_children.pop(child, None)

    async def api_call(self) -> None:
        '''
        Make an API call with current context and memory for manager agent.
        Uses manager-specific Jinja templates and processes response through manager language.
        '''
        # Set stall to true to prevent concurrent API calls
        self.stall = True
        
        # Load context and memory
        await self._load_context()
        
        # Concatenate all prompts in queue (numbered)
        # TODO: Use Jinja template for manager-specific formatting here
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
            
            # Process response through manager language interpreter
            # TODO: Implement manager-specific response processing here
            # await manager_receive_stage(self, response)  # Will be implemented when prompter is ready
            pass
        
        # Clear prompt queue
        self.prompt_queue.clear()
