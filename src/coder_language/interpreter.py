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

# Global constants
ALLOWED_COMMANDS = {
    'ls', 'dir', 'cat', 'type', 'grep', 'find', 'git status', 'git log',
    'python -m py_compile', 'npm test', 'pytest', 'flake8', 'black --check',
    'ripgrep', 'rg'
}

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
        
        # Find project root for command execution
        self.project_root = self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = self.base_path
        while current.parent != current:
            if any((current / marker).exists() for marker in ['.git', 'requirements.txt', 'package.json', 'Cargo.toml']):
                break
            current = current.parent
        return current

    def execute(self, directive: DirectiveType) -> Optional[str]:
        """
        Execute a single directive.
        
        Args:
            directive: The directive to execute
        Returns:
            String result of the execution, or None if no result
        """
        if isinstance(directive, ReadDirective):
            return self._execute_read(directive)
        elif isinstance(directive, RunDirective):
            return self._execute_run(directive)
        elif isinstance(directive, ChangeDirective):
            return self._execute_change(directive)
        elif isinstance(directive, FinishDirective):
            return self._execute_finish(directive)
        else:
            return f"Unknown directive type: {type(directive)}"

    def _execute_read(self, directive: ReadDirective) -> str:
        """Execute a READ directive."""
        filename = directive.filename
        file_path = self.base_path / filename
        try:
            if not file_path.exists():
                return f"READ failed: File not found: {filename}"
            # Add file path to agent's memory for up-to-date reads
            if self.agent and hasattr(self.agent, 'memory'):
                if 'read_files' not in self.agent.memory:
                    self.agent.memory['read_files'] = []
                if filename not in self.agent.memory['read_files']:
                    self.agent.memory['read_files'].append(filename)
            return f"READ succeeded: {filename} was added to memory for future reads"
        except Exception as e:
            return f"READ failed: {filename} could not be added to memory: {str(e)}"

    def _execute_run(self, directive: RunDirective) -> str:
        """Execute a RUN directive."""
        command = directive.command
        command_start = command.split()[0]
        if not any(command.startswith(allowed) for allowed in ALLOWED_COMMANDS):
            return f"RUN failed: Invalid command: {command}"
        try:
            # Execute the command from project root
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300  # 5 minute timeout
            )
            if result.returncode == 0:
                return f"RUN succeeded: Output:\n{result.stdout.strip()}"
            else:
                return f"RUN failed: {result.stderr.strip() or f'Command failed with return code {result.returncode}'}"
        except subprocess.TimeoutExpired:
            return f"RUN failed: Command timed out after 5 minutes: {command}"
        except Exception as e:
            return f"RUN failed: {str(e)}"

    def _execute_change(self, directive: ChangeDirective) -> str:
        """Execute a CHANGE directive."""
        if self.own_file is None:
            return "CHANGE failed: This agent has no assigned file."
        file_path = self.base_path / self.own_file
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(directive.content)
            # Optionally update agent's memory
            if self.agent and hasattr(self.agent, 'memory'):
                if 'files' not in self.agent.memory:
                    self.agent.memory['files'] = {}
                self.agent.memory['files'][str(self.own_file)] = directive.content
            return f"CHANGE succeeded: {self.own_file} was replaced with new content"
        except Exception as e:
            return f"CHANGE failed: Could not write to {self.own_file}: {str(e)}"

    def _execute_finish(self, directive: FinishDirective) -> str:
        """Execute a FINISH directive."""
        if not self.agent:
            raise ValueError("No agent available for finish")
        
        # Try to deactivate the agent
        # This will raise an error if there are still active children
        asyncio.create_task(self.agent.deactivate())
        
        return directive.prompt.value


# Convenience function
def execute_directive(directive: DirectiveType, base_path: str = ".", agent=None, own_file: str = None) -> Optional[str]:
    """
    Execute a single coder directive.
    
    Args:
        directive: The directive to execute
        base_path: Base directory for file operations
        agent: The agent that sent the command
        own_file: The file this coder agent is responsible for
    Returns:
        String result of the execution, or None if no result
    """
    interpreter = CoderLanguageInterpreter(base_path=base_path, agent=agent, own_file=own_file)
    return interpreter.execute(directive) 