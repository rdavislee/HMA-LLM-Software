"""
Coder Language Interpreter.
Executes parsed coder language directives and performs the described actions.
"""

import os
import asyncio
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
from .ast import DirectiveType, ReadDirective, RunDirective, ChangeDirective, FinishDirective
from src import ROOT_DIR
from src.config import ALLOWED_COMMANDS
from .parser import parse_directive

class CoderLanguageInterpreter:
    """
    Interpreter for the Coder Language.
    Executes directives and performs file system operations and command execution.
    """
    
    def __init__(self, base_path: str = ".", agent=None, own_file: str = None):
        """
        Initialize the interpreter.
        
        Args:
            base_path: Base directory for file operations (default: current directory)
            agent: The agent that sent the command
            own_file: The file this coder agent is responsible for
        """
        self.base_path = Path(base_path).resolve()
        self.agent = agent
        self.own_file = own_file
        
        # Use ROOT_DIR if set, else find project root
        self.project_root = ROOT_DIR if ROOT_DIR is not None else self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = self.base_path
        while current.parent != current:
            if any((current / marker).exists() for marker in ['.git', 'requirements.txt', 'package.json', 'Cargo.toml']):
                break
            current = current.parent
        return current

    def execute(self, directive: DirectiveType) -> None:
        """
        Execute a single directive. Only reprompt agent if an exception is raised.
        Args:
            directive: The directive to execute
        """
        try:
            if isinstance(directive, ReadDirective):
                self._execute_read(directive)
            elif isinstance(directive, RunDirective):
                self._execute_run(directive)
            elif isinstance(directive, ChangeDirective):
                self._execute_change(directive)
            elif isinstance(directive, FinishDirective):
                self._execute_finish(directive)
            else:
                if self.agent:
                    from src.orchestrator.coder_prompter import coder_prompter
                    asyncio.create_task(coder_prompter(self.agent, f"Unknown directive type: {type(directive)}"))
        except Exception as e:
            if self.agent:
                from src.orchestrator.coder_prompter import coder_prompter
                asyncio.create_task(coder_prompter(self.agent, f"Exception during execution: {str(e)}"))
        return None

    def _execute_read(self, directive: ReadDirective) -> None:
        """Execute a READ directive."""
        filename = directive.filename
        file_path = self.base_path / filename
        prompt = None
        try:
            if file_path.exists():
                if self.agent and hasattr(self.agent, 'read_file'):
                    self.agent.read_file(str(file_path))
                    prompt = f"READ succeeded: {filename} was added to memory for future reads"
                else:
                    prompt = f"READ failed: No agent or read_file method available"
            else:
                prompt = f"READ failed: File not found: {filename}"
        except Exception as e:
            if self.agent:
                from src.orchestrator.coder_prompter import coder_prompter
                asyncio.create_task(coder_prompter(self.agent, f"READ failed: {filename} could not be added to memory: {str(e)}"))
            return
        if self.agent and prompt:
            from src.orchestrator.coder_prompter import coder_prompter
            asyncio.create_task(coder_prompter(self.agent, prompt))

    def _execute_run(self, directive: RunDirective) -> None:
        """Execute a RUN directive and reprompt with the result string."""
        command = directive.command
        prompt = None
        try:
            if any(command.startswith(allowed) for allowed in ALLOWED_COMMANDS):
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=300
                )
                if result.returncode == 0:
                    prompt = f"RUN succeeded: Output:\n{result.stdout.strip()}"
                else:
                    prompt = f"RUN failed: {result.stderr.strip() or f'Command failed with return code {result.returncode}'}"
            else:
                prompt = f"RUN failed: Invalid command: {command}"
        except subprocess.TimeoutExpired:
            prompt = f"RUN failed: Command timed out after 5 minutes: {command}"
        except Exception as e:
            if self.agent:
                from src.orchestrator.coder_prompter import coder_prompter
                asyncio.create_task(coder_prompter(self.agent, f"RUN failed: {str(e)}"))
            return
        if self.agent and prompt:
            from src.orchestrator.coder_prompter import coder_prompter
            asyncio.create_task(coder_prompter(self.agent, prompt))

    def _execute_change(self, directive: ChangeDirective) -> None:
        """Execute a CHANGE directive."""
        prompt = None
        try:
            if self.own_file is not None:
                file_path = self.base_path / self.own_file
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(directive.content)
                prompt = f"CHANGE succeeded: {self.own_file} was replaced with new content"
            else:
                prompt = "CHANGE failed: This agent has no assigned file."
        except Exception as e:
            if self.agent:
                from src.orchestrator.coder_prompter import coder_prompter
                asyncio.create_task(coder_prompter(self.agent, f"CHANGE failed: Could not write to {self.own_file}: {str(e)}"))
            return
        if self.agent and prompt:
            from src.orchestrator.coder_prompter import coder_prompter
            asyncio.create_task(coder_prompter(self.agent, prompt))

    def _execute_finish(self, directive: FinishDirective) -> None:
        """Execute a FINISH directive."""
        if self.agent:
            try:
                asyncio.create_task(self.agent.deactivate())
            except Exception as e:
                from src.orchestrator.coder_prompter import coder_prompter
                asyncio.create_task(coder_prompter(self.agent, f"FINISH failed: {str(e)}"))
                return
            from src.orchestrator.coder_prompter import coder_prompter
            asyncio.create_task(coder_prompter(self.agent, directive.prompt.value))


# Convenience function
def execute_directive(directive_text: str, base_path: str = ".", agent=None, own_file: str = None) -> None:
    """
    Convenience function to parse and execute a single directive string.
    After execution, sets agent.stall to False if agent is provided.
    
    Args:
        directive_text: The directive string to parse and execute
        base_path: Base directory for file operations
        agent: The agent that sent the command
        own_file: The file this coder agent is responsible for
    """
    interpreter = CoderLanguageInterpreter(base_path=base_path, agent=agent, own_file=own_file)
    directive = parse_directive(directive_text)
    interpreter.execute(directive)
    if agent is not None:
        agent.stall = False
        # Check agent prompt queue and if not empty, call api_call
        if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
            try:
                asyncio.create_task(agent.api_call())
            except Exception:
                pass 