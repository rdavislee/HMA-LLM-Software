"""
Coder Language Interpreter.
Executes parsed coder language directives and performs the described actions.
"""

import os
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
from .ast import DirectiveType, ReadDirective, RunDirective, ChangeDirective, FinishDirective
from .parser import CoderLanguageParser


ALLOWED_COMMANDS = {
    'ls', 'dir', 'cat', 'type', 'grep', 'find', 'git status', 'git log',
    'python -m py_compile', 'npm test', 'pytest', 'flake8', 'black --check'
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
        self.parser = CoderLanguageParser()

    def execute(self, directive_text: str) -> str:
        """
        Parse and execute a coder language directive.
        
        Args:
            directive_text: The directive string to execute
        Returns:
            String result of the execution
        """
        try:
            directive = self.parser.parse(directive_text)
            return self._execute_directive(directive)
        except Exception as e:
            return f"Error executing directive: {str(e)}"

    def _execute_directive(self, directive: DirectiveType) -> str:
        """
        Execute a single directive.
        
        Args:
            directive: The directive to execute
        Returns:
            String result of the execution
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
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.base_path,
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
        # Remove this agent from parent's active children and deactivate
        msg = directive.prompt.value
        # Remove from parent's active children if possible
        if self.agent and hasattr(self.agent, 'parent_id') and hasattr(self.agent, 'agent_id'):
            parent = getattr(self.agent, 'parent_id', None)
            if parent and hasattr(parent, 'active_tasks'):
                if self.agent.agent_id in parent.active_tasks:
                    del parent.active_tasks[self.agent.agent_id]
        # Deactivate this agent if possible
        if self.agent and hasattr(self.agent, 'deactivate'):
            try:
                # If deactivate is async, call it properly
                import asyncio
                if asyncio.iscoroutinefunction(self.agent.deactivate):
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import nest_asyncio
                        nest_asyncio.apply()
                        loop.create_task(self.agent.deactivate())
                    else:
                        loop.run_until_complete(self.agent.deactivate())
                else:
                    self.agent.deactivate()
            except Exception:
                pass
        return f"FINISH: {msg}"

    def get_context(self) -> Dict[str, Any]:
        """Get the current execution context."""
        # Not used in this refactor, but kept for compatibility
        return {}

    def reset_context(self):
        """Reset the execution context."""
        # Not used in this refactor, but kept for compatibility
        pass

    def export_context(self, file_path: str):
        """Export the current context to a JSON file."""
        # Not used in this refactor, but kept for compatibility
        pass

# Convenience functions for easy execution

def execute_directive(directive_text: str, base_path: str = ".", agent=None, own_file: str = None) -> str:
    """
    Execute a single coder directive.
    
    Args:
        directive_text: The directive string to execute
        base_path: Base directory for file operations
        agent: The agent that sent the command
        own_file: The file this coder agent is responsible for
    Returns:
        String result of the execution
    """
    interpreter = CoderLanguageInterpreter(base_path=base_path, agent=agent, own_file=own_file)
    return interpreter.execute(directive_text) 