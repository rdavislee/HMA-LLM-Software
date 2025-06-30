"""
Ephemeral Agent base class for temporary agents that perform context-heavy tasks.

This module provides the core functionality for ephemeral agents that are spawned by
regular coder or manager agents to handle specific tasks and report back concise results.

Ephemeral agents are designed to:
- Be created for specific tasks and destroyed after completion
- Handle context-heavy operations without polluting parent agent memory
- Provide concise results back to their spawning parent
- Not maintain persistent state or personal files
"""

# Standard library imports
import os
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass

# Local imports
from src.llm.base import BaseLLMClient
from src.agents.base_agent import BaseAgent
import src
from src.config import COLLAPSED_DIR_NAMES

# ContextEntry ADT for prompt-response pairs
@dataclass
class ContextEntry:
    prompt: str
    response: str

class EphemeralAgent(ABC):
    '''
    Base ephemeral agent class for temporary agents that perform context-heavy tasks.
    
    Ephemeral agents have:
    - parent: The agent that spawned this ephemeral agent
    - parent_path: The path of the parent agent for context
    - llm_client: LLM client for generating responses
    - max_context_size: Maximum size of context to maintain
    - stall: State flag for managing concurrent operations
    - prompt_queue: List of prompts to process
    - memory: Dictionary of filenames to file paths for reading
    - context: List of ContextEntry (prompt-response history)
    - active_task: Current task being processed
    
    These agents are designed to be spawned, execute a task, report results, and be destroyed.
    '''

    def __init__(
        self,
        parent: "BaseAgent",
        parent_path: str,
        llm_client: Optional[BaseLLMClient] = None,
        max_context_size: int = 8000
    ) -> None:
        """Initialize a new ephemeral agent.
        
        Args:
            parent: The agent that spawned this ephemeral agent
            parent_path: The path of the parent agent for context
            llm_client: LLM client for generating responses
            max_context_size: Maximum size of context to maintain
        """
        self.parent = parent
        self.parent_path = Path(parent_path).resolve()
        self.llm_client = llm_client
        self.max_context_size = max_context_size

        # Ephemeral agent state
        self.stall = False
        self.prompt_queue: List[str] = []
        
        # Memory: Dictionary of filenames to file paths for reading
        self.memory: Dict[str, Path] = {}
        
        # Context: List of ContextEntry (prompt-response history)
        self.context: List[ContextEntry] = []
        
        # Task tracking
        self.active_task = None

    async def process_task(self, prompt: str) -> None:
        '''
        Process a task by adding prompt to queue and calling API if not stalled.
        Future-proofing for potential ephemeral agent nesting.
        
        Args:
            prompt: The prompt to process
        '''
        self.prompt_queue.append(prompt)
        
        if not self.stall:
            try:
                await self.api_call()
            except Exception as e:
                # Surface the exception immediately so manual testing doesn't appear to hang
                import sys, traceback
                print(f"[EphemeralAgent] Exception during api_call for agent {self.parent_path}: {e}", file=sys.stderr)
                traceback.print_exc()

                # Ensure the agent doesn't remain stalled forever
                self.stall = False

                # Reprompt with the error message so higher-level logic can react
                error_msg = f"Exception during api_call: {e}"
                # Avoid infinite recursion: only enqueue, let caller decide when to process
                self.prompt_queue.append(error_msg)

    @abstractmethod
    async def api_call(self) -> None:
        '''
        Make an API call with current context and memory.
        This method must be implemented by subclasses to handle
        their specific tasks and response processing.
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
        return "\n".join(lines)

    def get_status(self) -> Dict[str, Any]:
        '''
        Get current ephemeral agent status.
        
        Returns:
            Dict[str, Any]: Status information including:
                - Agent type and parent info
                - Active task and memory usage
                - Context and stall state
        '''
        return {
            'agent_type': 'ephemeral',
            'parent_path': str(self.parent_path),
            'parent_type': 'manager' if self.parent.is_manager else 'coder',
            'active_task': str(self.active_task) if self.active_task else None,
            'memory_files': len(self.memory),
            'context_entries': len(self.context),
            'prompt_queue_size': len(self.prompt_queue),
            'stall': self.stall,
            'max_context_size': self.max_context_size,
        }
    
    def __repr__(self) -> str:
        '''
        String representation of the ephemeral agent.
        
        Returns:
            str: Agent representation including type, parent path, and task status
        '''
        task_status = f"task={str(self.active_task)[:50]}..." if self.active_task else "no_task"
        return f"EphemeralAgent(parent_path={self.parent_path}, {task_status})" 