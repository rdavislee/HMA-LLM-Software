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
from jinja2 import Environment, FileSystemLoader

from .base_agent import BaseAgent, ContextEntry
from src.messages.protocol import (
    Message, TaskMessage, ResultMessage, MessageType
)
from src.llm.base import BaseLLMClient
from src.llm.providers import (
    GPT41Client, O3Client, O3ProClient,
    ClaudeSonnet4Client, ClaudeOpus4Client,
    Gemini25FlashClient, Gemini25ProClient,
    DeepSeekV3Client, DeepSeekR1Client
)
from src.llm.providers import get_llm_client

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
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader('prompts'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
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
        
        # Get current prompt from queue
        current_prompt = "\n".join(self.prompt_queue) if self.prompt_queue else ""
        
        # Get memory contents
        memory_contents = self._get_memory_contents()
        
        # Get personal file content
        personal_file_name = ""
        if self.personal_file and self.personal_file.exists():
            personal_file_name = self.personal_file.name
        
        # Get codebase structure
        codebase_structure = self._get_codebase_structure_string()
        
        # Load Lark grammar
        lark_grammar = ""
        try:
            with open('src/manager_language/grammar.lark', 'r', encoding='utf-8') as f:
                lark_grammar = f.read()
        except Exception as e:
            lark_grammar = f"[Error reading Lark grammar: {str(e)}]"
        
        # Load language examples
        language_examples = ""
        try:
            with open('prompts/manager/language_examples.md', 'r', encoding='utf-8') as f:
                language_examples = f.read()
        except Exception as e:
            language_examples = f"[Error reading language examples: {str(e)}]"
        
        # Load agent role description from markdown file
        try:
            with open('prompts/manager/agent_role.md', 'r', encoding='utf-8') as f:
                agent_role = f.read()
        except Exception as e:
            agent_role = f"[Error reading agent role: {str(e)}]"
        
        # Define available terminal commands and utilities
        try:
            with open('prompts/manager/available_commands.md', 'r', encoding='utf-8') as f:
                available_commands = f.read()
        except Exception as e:
            available_commands = f"[Error reading available commands: {str(e)}]"

        # Make API call using message list
        if self.llm_client:
            if self.llm_client.supports_system_role:
                # Render split templates
                system_template = self.jinja_env.get_template('system_template.j2')
                user_template = self.jinja_env.get_template('user_template.j2')

                system_prompt = system_template.render(
                    agent_role=agent_role,
                    available_commands=available_commands,
                    lark_grammar=lark_grammar,
                    language_examples=language_examples
                )

                user_prompt = user_template.render(
                    active_task=str(self.active_task) if self.active_task else None,
                    context=self.context,
                    memory_contents=memory_contents,
                    personal_file_name=personal_file_name,
                    codebase_structure=codebase_structure,
                    current_prompt=current_prompt
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
                    active_task=str(self.active_task) if self.active_task else None,
                    context=self.context,
                    memory_contents=memory_contents,
                    personal_file_name=personal_file_name,
                    codebase_structure=codebase_structure,
                    available_commands=available_commands,
                    lark_grammar=lark_grammar,
                    language_examples=language_examples,
                    current_prompt=current_prompt
                )
                response = await self.llm_client.generate_response(formatted_prompt)

            # Save context (only store current prompt -> response)
            self.context.append(ContextEntry(prompt=current_prompt, response=response))

            # TODO: Process response via manager language interpreter
        
        # Clear prompt queue
        self.prompt_queue.clear()
