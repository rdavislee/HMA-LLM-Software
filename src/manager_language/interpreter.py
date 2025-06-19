"""
Manager Language Interpreter.
Executes parsed manager language directives and performs the described actions.
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
from .ast import DirectiveType, DelegateDirective, FinishDirective, ActionDirective, WaitDirective, RunDirective, UpdateReadmeDirective
from ..messages.protocol import TaskMessage, Task, MessageType
from ..orchestrator.manager_prompter import manager_prompt_stage
from ..orchestrator.coder_prompter import coder_prompt_stage

# Global constants
ALLOWED_COMMANDS = {
    'ls', 'dir', 'cat', 'type', 'grep', 'find', 'git status', 'git log',
    'python -m py_compile', 'npm test', 'pytest', 'flake8', 'black --check',
    'ripgrep', 'rg'
}


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
        self.agent = agent
        
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
    
    def _execute_delegate(self, directive: DelegateDirective) -> None:
        """Execute a DELEGATE directive."""
        if not self.agent:
            raise ValueError("No agent available for delegation")
        
        # Check if all children exist
        for item in directive.items:
            child_name = item.target.name
            child_path = self.agent.path / child_name
            
            if not child_path.exists():
                raise ValueError(f"Child '{child_name}' does not exist")
        
        # Add all delegated children to active children list
        for item in directive.items:
            child_name = item.target.name
            child_path = self.agent.path / child_name
            
            # Create TaskMessage for the child
            task = Task(
                task_id=str(hash(child_name + item.prompt.value)),
                task_string=item.prompt.value
            )
            task_message = TaskMessage(
                message_type=MessageType.DELEGATION,
                sender_id=str(self.agent.path),
                recipient_id=str(child_path),
                timestamp=0,  # Will be set by the prompter
                message_id=str(hash(task.task_id))
            )
            task_message.task = task
            
            # Add to active children
            self.agent.active_children.append(child_path)
            
            # Call appropriate prompter based on child type
            if child_path.is_dir():
                # Child is a manager
                from ..agents.manager_agent import ManagerAgent
                child_agent = ManagerAgent(str(child_path), parent_path=str(self.agent.path))
                asyncio.create_task(manager_prompt_stage(child_agent, item.prompt.value, task_message))
            else:
                # Child is a coder
                from ..agents.coder_agent import CoderAgent
                child_agent = CoderAgent(str(child_path), parent_path=str(self.agent.path))
                asyncio.create_task(coder_prompt_stage(child_agent, item.prompt.value, task_message))
        
        return None
    
    def _execute_finish(self, directive: FinishDirective) -> str:
        """Execute a FINISH directive."""
        if not self.agent:
            raise ValueError("No agent available for finish")
        
        # Try to deactivate the agent
        # This will raise an error if there are still active children
        asyncio.create_task(self.agent.deactivate())
        
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
    
    def _execute_wait(self, directive: WaitDirective) -> None:
        """Execute a WAIT directive."""
        # Wait doesn't need to do anything, just pass
        return None
    
    def _execute_run(self, directive: RunDirective) -> str:
        """Execute a RUN directive."""
        command = directive.command
        
        # Check if command is allowed
        command_start = command.split()[0]
        if not any(command.startswith(allowed) for allowed in ALLOWED_COMMANDS):
            return "Invalid command"
        
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


# Convenience function
def execute_directive(directive: DirectiveType, base_path: str = ".", agent=None) -> Optional[str]:
    """
    Convenience function to execute a single directive.
    
    Args:
        directive: The directive to execute
        base_path: Base directory for file operations
        agent: The agent that sent the command
        
    Returns:
        String result of the execution, or None if no result
    """
    interpreter = ManagerLanguageInterpreter(base_path, agent)
    return interpreter.execute(directive) 