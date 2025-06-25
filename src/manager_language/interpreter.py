"""
Manager Language Interpreter.
Executes parsed manager language directives and performs the described actions.
"""

import os
import json
import asyncio
import subprocess
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from .ast import DirectiveType, DelegateDirective, FinishDirective, ActionDirective, WaitDirective, RunDirective, UpdateReadmeDirective
from src.messages.protocol import TaskMessage, Task, MessageType, ResultMessage
from src.config import ALLOWED_COMMANDS
from .parser import parse_directive
import src


class ManagerLanguageInterpreter:
    """
    Interpreter for the Manager Language.
    Executes directives and performs file system operations.
    """
    
    def __init__(self, agent=None):
        """
        Initialize the interpreter.
        Args:
            agent: The agent that sent the command
        """
        self.agent = agent
        if src.ROOT_DIR is None:
            raise RuntimeError("ROOT_DIR is not set. Please call set_root_dir(path) before using the interpreter.")
        self.root_dir = src.ROOT_DIR
    
    def execute(self, directive: DirectiveType) -> None:
        """
        Execute a single directive.
        
        Args:
            directive: The directive to execute
        """
        try:
            if isinstance(directive, DelegateDirective):
                self._execute_delegate(directive)
            elif isinstance(directive, FinishDirective):
                self._execute_finish(directive)
            elif isinstance(directive, ActionDirective):
                self._execute_action(directive)
            elif isinstance(directive, WaitDirective):
                self._execute_wait(directive)
            elif isinstance(directive, RunDirective):
                self._execute_run(directive)
            elif isinstance(directive, UpdateReadmeDirective):
                self._execute_update_readme(directive)
            else:
                # Unknown directive type, reprompt self with error
                if self.agent:
                    from src.orchestrator.manager_prompter import manager_prompter
                    asyncio.create_task(manager_prompter(self.agent, f"Unknown directive type: {type(directive)}"))
        except Exception as e:
            if self.agent:
                from src.orchestrator.manager_prompter import manager_prompter
                asyncio.create_task(manager_prompter(self.agent, f"Error executing directive {type(directive).__name__}: {str(e)}"))

    def _execute_delegate(self, directive: DelegateDirective) -> None:
        """Execute a DELEGATE directive."""
        if not self.agent:
            return
        if not hasattr(self.agent, 'children'):
            return

        # Build a mapping from child name to child agent object
        child_map = {str(child.path.name): child for child in self.agent.children}

        # Check if all children exist
        for item in directive.items:
            child_name = item.target.name
            if child_name not in child_map:
                return

        # Call appropriate prompter based on child type
        for item in directive.items:
            child_name = item.target.name
            child_agent = child_map[child_name]

            # Create TaskMessage for the child
            task = Task(
                task_id=str(hash(child_name + item.prompt.value)),
                task_string=item.prompt.value
            )
            task_message = TaskMessage(
                message_type=MessageType.DELEGATION,
                sender_id=str(self.agent.path),
                recipient_id=str(child_agent.path),
                message_id=str(hash(task.task_id)),
                task=task
            )
            # Call appropriate prompter based on child type
            if hasattr(child_agent, 'is_manager') and child_agent.is_manager:
                from src.orchestrator.manager_prompter import manager_prompter
                asyncio.create_task(manager_prompter(child_agent, item.prompt.value, task_message))
            else:
                from src.orchestrator.coder_prompter import coder_prompter
                asyncio.create_task(coder_prompter(child_agent, item.prompt.value, task_message))
            # Track delegation in agent (call delegate_task)
            self.agent.delegate_task(child_agent, item.prompt.value)

        return None
    
    def _execute_finish(self, directive: FinishDirective) -> None:
        """Execute a FINISH directive."""
        if not self.agent:
            return
        try:
            self.agent.deactivate()
            # Notify parent with ResultMessage
            parent = getattr(self.agent, 'parent', None)
            if parent:
                task = getattr(self.agent, 'active_task', None)
                if task is None:
                    # Fallback: create a dummy task
                    task = Task(task_id=str(hash(str(self.agent.path))), task_string="Task finished")
                result_message = ResultMessage(
                    message_type=MessageType.RESULT,
                    sender_id=str(self.agent.path),
                    recipient_id=str(parent.path),
                    timestamp=time.time(),
                    message_id=str(hash(str(self.agent.path) + str(time.time()))),
                    task=task,
                    result=directive.prompt.value
                )
                from src.orchestrator.manager_prompter import manager_prompter
                asyncio.create_task(manager_prompter(parent, directive.prompt.value, result_message))
            else:
                # Root agent – bubble the result back by attaching it to the agent so callers can access it
                setattr(self.agent, "final_result", directive.prompt.value)
        except Exception as e:
            # Reprompt self with error
            if self.agent:
                from src.orchestrator.manager_prompter import manager_prompter
                asyncio.create_task(manager_prompter(self.agent, f"Failed to finish: {str(e)}"))
    
    def _execute_action(self, directive: ActionDirective) -> None:
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
        # Reprompt self with action results
        if self.agent:
            from src.orchestrator.manager_prompter import manager_prompter
            prompt = f"Action {directive.action_type} completed:\n" + "\n".join(results)
            asyncio.create_task(manager_prompter(self.agent, prompt))
    
    def _execute_wait(self, directive: WaitDirective) -> None:
        """Execute a WAIT directive."""
        # Wait doesn't need to do anything, just pass
        return None
    
    def _execute_run(self, directive: RunDirective) -> None:
        command = directive.command
        command_start = command.split()[0]
        if not any(command.startswith(allowed) for allowed in ALLOWED_COMMANDS):
            result = "Invalid command"
        else:
            try:
                result_obj = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.root_dir,
                    timeout=300
                )
                if result_obj.returncode == 0:
                    result = result_obj.stdout
                else:
                    result = f"Command failed: {result_obj.stderr}"
            except subprocess.TimeoutExpired:
                result = f"Command timed out after 5 minutes: {command}"
            except Exception as e:
                result = f"Failed to execute command '{command}': {str(e)}"
        # Reprompt self with run result
        if self.agent:
            from src.orchestrator.manager_prompter import manager_prompter
            prompt = f"Run command result:\n{result}"
            asyncio.create_task(manager_prompter(self.agent, prompt))
    
    def _execute_update_readme(self, directive: UpdateReadmeDirective) -> None:
        if not self.agent or not hasattr(self.agent, 'path'):
            result = "No agent path available"
        else:
            agent_path = Path(self.agent.path)
            agent_path = self.root_dir / agent_path.relative_to(self.root_dir)
            if not agent_path.is_dir():
                result = "Agent path is not a directory"
            else:
                folder_name = agent_path.name
                readme_filename = f"{folder_name}_readme.md"
                readme_path = agent_path / readme_filename
                try:
                    readme_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(directive.content)
                    result = f"Successfully updated {readme_filename}"
                except Exception as e:
                    result = f"Failed to update readme: {str(e)}"
        # Reprompt self with update readme result
        if self.agent:
            from src.orchestrator.manager_prompter import manager_prompter
            prompt = f"Update README result:\n{result}"
            asyncio.create_task(manager_prompter(self.agent, prompt))
    
    def _create_target(self, target) -> str:
        """Create a file or folder from the home directory of the agent's path."""
        if not self.agent or not hasattr(self.agent, 'path'):
            return "No agent path available"
        
        agent_path = Path(self.agent.path)
        agent_path = self.root_dir / agent_path.relative_to(self.root_dir)
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
        agent_path = self.root_dir / agent_path.relative_to(self.root_dir)
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
        """Read a file and add it to the agent's memory using the agent's read_file method."""
        if not self.agent or not hasattr(self.agent, 'read_file'):
            return "No agent or read_file method available"

        # Helper to search for a path (file or directory) within root_dir
        def _search_path(name: str, expect_folder: bool = False) -> Optional[Path]:
            candidate = self.root_dir / name
            if candidate.exists() and (candidate.is_dir() if expect_folder else True):
                return candidate
            for root, dirs, files in os.walk(self.root_dir):
                if expect_folder:
                    for d in dirs:
                        if d == name:
                            return Path(root) / d
                else:
                    for f in files:
                        if f == name:
                            return Path(root) / f
            return None

        if target.is_folder:
            # Locate the folder first
            folder_path = _search_path(target.name, expect_folder=True)
            if not folder_path or not folder_path.exists():
                return f"Folder {target.name} was not added to memory: folder not found"

            # Determine README filename(s)
            folder_name = Path(folder_path).name
            candidate_names = [f"{folder_name}_README.md"]
            readme_path = None
            for cname in candidate_names:
                potential = folder_path / cname
                if potential.exists():
                    readme_path = potential
                    break

            if not readme_path:
                return f"Folder {target.name} has no README file to add to memory"

            try:
                self.agent.read_file(str(readme_path))
                return f"Folder {target.name} README ({readme_path.name}) was added to memory"
            except Exception as e:
                return f"Folder {target.name} README was not added to memory: {str(e)}"
        else:
            # It's a file target. Search for the file regardless of scope.
            found_path = _search_path(target.name, expect_folder=False)
            if not found_path or not found_path.exists():
                return f"File {target.name} was not added to memory: file not found"
            try:
                self.agent.read_file(str(found_path))
                return f"File {target.name} was added to memory"
            except Exception as e:
                return f"File {target.name} was not added to memory: {str(e)}"


# Convenience function
def execute_directive(directive_text: str, agent=None) -> None:
    """
    Convenience function to parse and execute a single directive string.
    After execution, sets agent.stall to False if agent is provided.
    
    Args:
        directive_text: The directive string to parse and execute
        base_path: Base directory for file operations
        agent: The agent that sent the command
    """
    interpreter = ManagerLanguageInterpreter(agent)
    directive = parse_directive(directive_text)
    interpreter.execute(directive)

    if agent is not None:
        # Only unstall the agent if it no longer has active children
        should_unstall = not getattr(agent, 'active_children', {})
        if should_unstall:
            agent.stall = False

        # Trigger follow-up api_call only if agent is not stalled and has queued prompts
        if (not agent.stall) and getattr(agent, 'prompt_queue', []):
            if hasattr(agent, 'api_call'):
                try:
                    asyncio.create_task(agent.api_call())
                except Exception:
                    pass