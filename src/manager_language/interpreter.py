"""
Manager Language Interpreter.
Executes parsed manager language directives and performs the described actions.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from .ast import DirectiveType, DelegateDirective, FinishDirective, ActionDirective, WaitDirective, RunDirective
from .parser import ManagerLanguageParser


class ManagerLanguageInterpreter:
    """
    Interpreter for the Manager Language.
    Executes directives and performs file system operations.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the interpreter.
        
        Args:
            base_path: Base directory for file operations (default: current directory)
        """
        self.base_path = Path(base_path).resolve()
        self.parser = ManagerLanguageParser()
        self.context: Dict[str, Any] = {
            'actions': [],
            'delegations': [],
            'commands': [],
            'finished': False,
            'waiting': False,
            'completion_prompt': None
        }
    
    def execute(self, directive_text: str) -> Dict[str, Any]:
        """
        Parse and execute a manager language directive.
        
        Args:
            directive_text: The directive string to execute
            
        Returns:
            Updated context after execution
        """
        try:
            directive = self.parser.parse(directive_text)
            return self._execute_directive(directive)
        except Exception as e:
            self.context['error'] = str(e)
            return self.context
    
    def execute_multiple(self, directives_text: str) -> Dict[str, Any]:
        """
        Parse and execute multiple manager language directives.
        
        Args:
            directives_text: Text containing multiple directives (one per line)
            
        Returns:
            Updated context after execution
        """
        try:
            directives = self.parser.parse_multiple(directives_text)
            for directive in directives:
                self._execute_directive(directive)
            return self.context
        except Exception as e:
            self.context['error'] = str(e)
            return self.context
    
    def _execute_directive(self, directive: DirectiveType) -> Dict[str, Any]:
        """
        Execute a single directive.
        
        Args:
            directive: The directive to execute
            
        Returns:
            Updated context
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
        else:
            raise ValueError(f"Unknown directive type: {type(directive)}")
    
    def _execute_delegate(self, directive: DelegateDirective) -> Dict[str, Any]:
        """Execute a DELEGATE directive."""
        if 'delegations' not in self.context:
            self.context['delegations'] = []
        
        for item in directive.items:
            delegation = {
                'target': item.target.name,
                'is_folder': item.target.is_folder,
                'prompt': item.prompt.value,
                'status': 'pending'
            }
            self.context['delegations'].append(delegation)
        
        return self.context
    
    def _execute_finish(self, directive: FinishDirective) -> Dict[str, Any]:
        """Execute a FINISH directive."""
        self.context['finished'] = True
        self.context['completion_prompt'] = directive.prompt.value
        return self.context
    
    def _execute_action(self, directive: ActionDirective) -> Dict[str, Any]:
        """Execute a CREATE, DELETE, or READ action directive."""
        if 'actions' not in self.context:
            self.context['actions'] = []
        
        for target in directive.targets:
            action_result = self._perform_file_action(directive.action_type, target)
            action = {
                'type': directive.action_type,
                'target': target.name,
                'is_folder': target.is_folder,
                'result': action_result,
                'status': 'completed' if action_result['success'] else 'failed'
            }
            if not action_result['success'] and 'error' in action_result:
                action['error'] = action_result['error']
            self.context['actions'].append(action)
        
        return self.context
    
    def _execute_wait(self, directive: WaitDirective) -> Dict[str, Any]:
        """Execute a WAIT directive."""
        self.context['waiting'] = True
        return self.context
    
    def _execute_run(self, directive: RunDirective) -> Dict[str, Any]:
        """Execute a RUN directive."""
        if 'commands' not in self.context:
            self.context['commands'] = []
        
        command_result = self._execute_command(directive.command)
        command_info = {
            'command': directive.command,
            'result': command_result,
            'status': 'completed' if command_result['success'] else 'failed'
        }
        if not command_result['success'] and 'error' in command_result:
            command_info['error'] = command_result['error']
        
        self.context['commands'].append(command_info)
        return self.context
    
    def _execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a command prompt command.
        
        Args:
            command: The command string to execute
            
        Returns:
            Dictionary with command execution result
        """
        import subprocess
        import sys
        
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
            
            res = {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'message': f"Command executed: {command}"
            }
            if result.returncode != 0:
                # Always include an 'error' key for failed commands
                res['error'] = result.stderr.strip() or f"Command failed with return code {result.returncode}"
            return res
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Command timed out after 5 minutes: {command}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to execute command '{command}': {str(e)}"
            }
    
    def _perform_file_action(self, action_type: str, target) -> Dict[str, Any]:
        """
        Perform a file system action.
        
        Args:
            action_type: Type of action (CREATE, DELETE, READ)
            target: Target object with name and is_folder attributes
            
        Returns:
            Dictionary with action result
        """
        target_path = self.base_path / target.name
        
        try:
            if action_type == "CREATE":
                return self._create_target(target_path, target.is_folder)
            elif action_type == "DELETE":
                return self._delete_target(target_path, target.is_folder)
            elif action_type == "READ":
                return self._read_target(target_path, target.is_folder)
            else:
                return {
                    'success': False,
                    'error': f"Unknown action type: {action_type}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_target(self, target_path: Path, is_folder: bool) -> Dict[str, Any]:
        """Create a file or folder."""
        try:
            if is_folder:
                target_path.mkdir(parents=True, exist_ok=True)
                return {
                    'success': True,
                    'message': f"Created folder: {target_path}"
                }
            else:
                # Create parent directories if they don't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)
                # Create empty file
                target_path.touch(exist_ok=True)
                return {
                    'success': True,
                    'message': f"Created file: {target_path}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create {target_path}: {str(e)}"
            }
    
    def _delete_target(self, target_path: Path, is_folder: bool) -> Dict[str, Any]:
        """Delete a file or folder."""
        try:
            if not target_path.exists():
                return {
                    'success': False,
                    'error': f"Target does not exist: {target_path}"
                }
            
            if is_folder:
                import shutil
                shutil.rmtree(target_path)
                return {
                    'success': True,
                    'message': f"Deleted folder: {target_path}"
                }
            else:
                target_path.unlink()
                return {
                    'success': True,
                    'message': f"Deleted file: {target_path}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to delete {target_path}: {str(e)}"
            }
    
    def _read_target(self, target_path: Path, is_folder: bool) -> Dict[str, Any]:
        """Read a file or list folder contents."""
        try:
            if not target_path.exists():
                return {
                    'success': False,
                    'error': f"Target does not exist: {target_path}"
                }
            
            if is_folder:
                # List folder contents
                contents = []
                for item in target_path.iterdir():
                    item_info = {
                        'name': item.name,
                        'type': 'folder' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else None
                    }
                    contents.append(item_info)
                
                return {
                    'success': True,
                    'message': f"Listed folder contents: {target_path}",
                    'contents': contents
                }
            else:
                # Read file contents
                content = target_path.read_text(encoding='utf-8')
                return {
                    'success': True,
                    'message': f"Read file: {target_path}",
                    'content': content,
                    'size': len(content)
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to read {target_path}: {str(e)}"
            }
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current execution context."""
        return self.context.copy()
    
    def reset_context(self):
        """Reset the execution context."""
        self.context = {
            'actions': [],
            'delegations': [],
            'commands': [],
            'finished': False,
            'waiting': False,
            'completion_prompt': None
        }
    
    def export_context(self, file_path: str):
        """Export the current context to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.context, f, indent=2, default=str)


# Convenience functions
def execute_directive(directive_text: str, base_path: str = ".") -> Dict[str, Any]:
    """
    Convenience function to execute a single directive.
    
    Args:
        directive_text: The directive string to execute
        base_path: Base directory for file operations
        
    Returns:
        Execution context
    """
    interpreter = ManagerLanguageInterpreter(base_path)
    return interpreter.execute(directive_text)


def execute_directives(directives_text: str, base_path: str = ".") -> Dict[str, Any]:
    """
    Convenience function to execute multiple directives.
    
    Args:
        directives_text: Text containing multiple directives
        base_path: Base directory for file operations
        
    Returns:
        Execution context
    """
    interpreter = ManagerLanguageInterpreter(base_path)
    return interpreter.execute_multiple(directives_text) 