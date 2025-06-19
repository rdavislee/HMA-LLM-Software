"""
Manager Language Interpreter.
Executes parsed manager language directives and performs the described actions.
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
from .ast import DirectiveType, DelegateDirective, FinishDirective, ActionDirective, WaitDirective, RunDirective, UpdateReadmeDirective
from .parser import ManagerLanguageParser


class ManagerLanguageInterpreter:
    """
    Interpreter for the Manager Language.
    Executes directives and performs file system operations.
    """
    
    def __init__(self, base_path: str = ".", agent=None):
        """
        Initialize the interpreter.
        
        Args:
            base_path: Base directory for file operations (default: current directory)
            agent: The agent that sent the command
        """
        self.base_path = Path(base_path).resolve()
        self.parser = ManagerLanguageParser()
        self.agent = agent
        self.context: Dict[str, Any] = {
            'actions': [],
            'delegations': [],
            'commands': [],
            'readme_updates': [],
            'finished': False,
            'waiting': False,
            'completion_prompt': None
        }
    
    def execute(self, directive_text: str) -> str:
        """
        Parse and execute a manager language directive.
        
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
    
    def execute_multiple(self, directives_text: str) -> str:
        """
        Parse and execute multiple manager language directives.
        
        Args:
            directives_text: Text containing multiple directives (one per line)
            
        Returns:
            Combined string result of all executions
        """
        try:
            directives = self.parser.parse_multiple(directives_text)
            results = []
            for directive in directives:
                result = self._execute_directive(directive)
                if result:
                    results.append(result)
            return "\n".join(results) if results else None
        except Exception as e:
            return f"Error executing directives: {str(e)}"
    
    def _execute_directive(self, directive: DirectiveType) -> str:
        """
        Execute a single directive.
        
        Args:
            directive: The directive to execute
            
        Returns:
            String result of the execution
        """
        if isinstance(directive, DelegateDirective):
            return self._execute_delegate(directive)
        elif isinstance(directive, FinishDirective):
            return self._execute_finish(directive)
        elif isinstance(directive, ActionDirective):
            return self._execute_action(directive)
        elif isinstance(directive, WaitDirective):
            return self._execute_wait(directive)
        elif isinstance(directive, RunDirective):
            return self._execute_run(directive)
        elif isinstance(directive, UpdateReadmeDirective):
            return self._execute_update_readme(directive)
        else:
            return f"Unknown directive type: {type(directive)}"
    
    def _execute_delegate(self, directive: DelegateDirective) -> str:
        """Execute a DELEGATE directive."""
        # TODO: This will add the children that were delegated to the active children
        # For now, just return None since base agent doesn't have the capacity for this
        return None
    
    def _execute_finish(self, directive: FinishDirective) -> str:
        """Execute a FINISH directive."""
        # Remove the agent from its parent's active children and deactivate the agent
        if self.agent and hasattr(self.agent, 'parent_id') and self.agent.parent_id:
            # TODO: Remove from parent's active children
            pass
        
        if self.agent:
            # TODO: Deactivate the agent
            pass
        
        return directive.prompt.value
    
    def _execute_action(self, directive: ActionDirective) -> str:
        """Execute a CREATE, DELETE, or READ action directive."""
        results = []
        
        for target in directive.targets:
            if directive.action_type == "CREATE":
                result = self._create_target(target)
            elif directive.action_type == "DELETE":
                result = self._delete_target(target)
            elif directive.action_type == "READ":
                result = self._read_target(target)
            else:
                result = f"Unknown action type: {directive.action_type}"
            
            results.append(result)
        
        return "\n".join(results)
    
    def _execute_wait(self, directive: WaitDirective) -> str:
        """Execute a WAIT directive."""
        # Wait doesn't need to do anything, just pass
        return None
    
    def _execute_run(self, directive: RunDirective) -> str:
        """Execute a RUN directive."""
        command = directive.command
        
        # Check if command is allowed
        allowed_commands = {
            'ls', 'dir', 'cat', 'type', 'grep', 'find', 'git status', 'git log',
            'python -m py_compile', 'npm test', 'pytest', 'flake8', 'black --check'
        }
        
        command_start = command.split()[0]
        if not any(command.startswith(allowed) for allowed in allowed_commands):
            return "Invalid command"
        
        try:
            # Execute the command and capture output
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.base_path,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Command failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"Command timed out after 5 minutes: {command}"
        except Exception as e:
            return f"Failed to execute command '{command}': {str(e)}"
    
    def _execute_update_readme(self, directive: UpdateReadmeDirective) -> str:
        """Execute an UPDATE_README directive."""
        if not self.agent or not hasattr(self.agent, 'path'):
            return "No agent path available"
        
        agent_path = Path(self.agent.path)
        if not agent_path.is_dir():
            return "Agent path is not a directory"
        
        # Look for a file named *folder name*_readme.md in the folder of the agent
        folder_name = agent_path.name
        readme_filename = f"{folder_name}_readme.md"
        readme_path = agent_path / readme_filename
        
        try:
            # Create the readme file if it doesn't exist
            readme_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the content to the readme
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(directive.content)
            
            return f"Successfully updated {readme_filename}"
            
        except Exception as e:
            return f"Failed to update readme: {str(e)}"
    
    def _create_target(self, target) -> str:
        """Create a file or folder from the home directory of the agent's path."""
        if not self.agent or not hasattr(self.agent, 'path'):
            return "No agent path available"
        
        agent_path = Path(self.agent.path)
        target_path = agent_path / target.name
        
        # Check if destination is out of scope (outside agent's directory)
        try:
            target_path.resolve().relative_to(agent_path.resolve())
        except ValueError:
            return f"Action failed: Destination {target.name} is out of scope"
        
        try:
            if target.is_folder:
                if target_path.exists():
                    return f"Action failed: Folder {target.name} already exists"
                target_path.mkdir(parents=True, exist_ok=True)
                return f"Action succeeded: Created folder {target.name}"
            else:
                if target_path.exists():
                    return f"Action failed: File {target.name} already exists"
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.touch()
                return f"Action succeeded: Created file {target.name}"
        except Exception as e:
            return f"Action failed: {str(e)}"
    
    def _delete_target(self, target) -> str:
        """Delete a file or folder from the home directory of the agent's path."""
        if not self.agent or not hasattr(self.agent, 'path'):
            return "No agent path available"
        
        agent_path = Path(self.agent.path)
        target_path = agent_path / target.name
        
        # Check if destination is out of scope (outside agent's directory)
        try:
            target_path.resolve().relative_to(agent_path.resolve())
        except ValueError:
            return f"Action failed: Destination {target.name} is out of scope"
        
        try:
            if not target_path.exists():
                return f"Action failed: {target.name} does not exist"
            
            if target.is_folder:
                import shutil
                shutil.rmtree(target_path)
                return f"Action succeeded: Deleted folder {target.name}"
            else:
                target_path.unlink()
                return f"Action succeeded: Deleted file {target.name}"
        except Exception as e:
            return f"Action failed: {str(e)}"
    
    def _read_target(self, target) -> str:
        """Read a file and add it to the agent's memory."""
        # Look for the file regardless of scope
        target_path = Path(target.name)
        
        # Try to find the file in the current directory and subdirectories
        found_path = None
        if target_path.exists():
            found_path = target_path
        else:
            # Search in subdirectories
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    if file == target.name:
                        found_path = Path(root) / file
                        break
                if found_path:
                    break
        
        if not found_path or not found_path.exists():
            return f"File {target.name} was not added to memory: file not found"
        
        try:
            # Read the file content
            with open(found_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add to agent's memory
            if self.agent and hasattr(self.agent, 'memory'):
                if 'files' not in self.agent.memory:
                    self.agent.memory['files'] = {}
                self.agent.memory['files'][target.name] = content
            
            return f"File {target.name} was added to memory"
            
        except Exception as e:
            return f"File {target.name} was not added to memory: {str(e)}"
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current execution context."""
        return self.context.copy()
    
    def reset_context(self):
        """Reset the execution context."""
        self.context = {
            'actions': [],
            'delegations': [],
            'commands': [],
            'readme_updates': [],
            'finished': False,
            'waiting': False,
            'completion_prompt': None
        }
    
    def export_context(self, file_path: str):
        """Export the current context to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.context, f, indent=2, default=str)


# Convenience functions
def execute_directive(directive_text: str, base_path: str = ".", agent=None) -> str:
    """
    Convenience function to execute a single directive.
    
    Args:
        directive_text: The directive string to execute
        base_path: Base directory for file operations
        agent: The agent that sent the command
        
    Returns:
        String result of the execution
    """
    interpreter = ManagerLanguageInterpreter(base_path, agent)
    return interpreter.execute(directive_text)


def execute_directives(directives_text: str, base_path: str = ".", agent=None) -> str:
    """
    Convenience function to execute multiple directives.
    
    Args:
        directives_text: Text containing multiple directives
        base_path: Base directory for file operations
        agent: The agent that sent the command
        
    Returns:
        String result of the execution
    """
    interpreter = ManagerLanguageInterpreter(base_path, agent)
    return interpreter.execute_multiple(directives_text) 