"""
Coder Language Interpreter.
Executes parsed coder language directives and performs the described actions.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from .ast import DirectiveType, ReadDirective, RunDirective, ChangeDirective, FinishDirective
from .parser import CoderLanguageParser


class CoderLanguageInterpreter:
    """
    Interpreter for the Coder Language.
    Executes directives and performs file system operations and command execution.
    """
    
    def __init__(self, base_path: str = ".", own_file: str = None):
        """
        Initialize the interpreter.
        
        Args:
            base_path: Base directory for file operations (default: current directory)
            own_file: The file this coder agent is responsible for
        """
        self.base_path = Path(base_path).resolve()
        self.own_file = own_file
        self.parser = CoderLanguageParser()
        self.context: Dict[str, Any] = {
            'reads': [],
            'commands': [],
            'changes': [],
            'finished': False,
            'completion_prompt': None,
            'own_file': own_file
        }
    
    def execute(self, directive_text: str) -> Dict[str, Any]:
        """
        Parse and execute a coder language directive.
        
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
        Parse and execute multiple coder language directives.
        
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
        if isinstance(directive, ReadDirective):
            return self._execute_read(directive)
        elif isinstance(directive, RunDirective):
            return self._execute_run(directive)
        elif isinstance(directive, ChangeDirective):
            return self._execute_change(directive)
        elif isinstance(directive, FinishDirective):
            return self._execute_finish(directive)
        else:
            raise ValueError(f"Unknown directive type: {type(directive)}")
    
    def _execute_read(self, directive: ReadDirective) -> Dict[str, Any]:
        """Execute a READ directive."""
        if 'reads' not in self.context:
            self.context['reads'] = []
        
        read_result = self._read_file(directive.filename)
        read_info = {
            'filename': directive.filename,
            'result': read_result,
            'status': 'completed' if read_result['success'] else 'failed'
        }
        if not read_result['success'] and 'error' in read_result:
            read_info['error'] = read_result['error']
        
        self.context['reads'].append(read_info)
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
    
    def _execute_change(self, directive: ChangeDirective) -> Dict[str, Any]:
        """Execute a CHANGE directive."""
        if 'changes' not in self.context:
            self.context['changes'] = []
        
        # Forbid all changes if own_file is None
        if self.own_file is None:
            change_info = {
                'content': directive.content,
                'status': 'failed',
                'error': f"Cannot modify file. This agent has no assigned file."
            }
            self.context['changes'].append(change_info)
            return self.context
        
        change_result = self._write_file(self.own_file, directive.content)
        change_info = {
            'filename': self.own_file,
            'content': directive.content,
            'result': change_result,
            'status': 'completed' if change_result['success'] else 'failed'
        }
        if not change_result['success'] and 'error' in change_result:
            change_info['error'] = change_result['error']
        
        self.context['changes'].append(change_info)
        return self.context
    
    def _execute_finish(self, directive: FinishDirective) -> Dict[str, Any]:
        """Execute a FINISH directive."""
        self.context['finished'] = True
        self.context['completion_prompt'] = directive.prompt.value
        return self.context
    
    def _read_file(self, filename: str) -> Dict[str, Any]:
        """
        Read a file from the codebase.
        
        Args:
            filename: The filename to read
            
        Returns:
            Dictionary with file read result
        """
        try:
            file_path = self.base_path / filename
            
            # Check if file exists
            if not file_path.exists():
                return {
                    'success': False,
                    'error': f"File not found: {filename}"
                }
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'success': True,
                'content': content,
                'filename': filename,
                'message': f"Successfully read file: {filename}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to read file {filename}: {str(e)}"
            }
    
    def _write_file(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            filename: The filename to write to
            content: The content to write
            
        Returns:
            Dictionary with file write result
        """
        try:
            file_path = self.base_path / filename
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'filename': filename,
                'message': f"Successfully wrote to file: {filename}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to write to file {filename}: {str(e)}"
            }
    
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
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current execution context."""
        return self.context.copy()
    
    def reset_context(self):
        """Reset the execution context."""
        self.context = {
            'reads': [],
            'commands': [],
            'changes': [],
            'finished': False,
            'completion_prompt': None,
            'own_file': self.own_file
        }
    
    def export_context(self, file_path: str):
        """Export the current context to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.context, f, indent=2)
    
    def set_own_file(self, filename: str):
        """Set the file this coder agent is responsible for."""
        self.own_file = filename
        self.context['own_file'] = filename


# Convenience functions for easy execution
def execute_directive(directive_text: str, base_path: str = ".", own_file: str = None) -> Dict[str, Any]:
    """
    Execute a single coder directive.
    
    Args:
        directive_text: The directive string to execute
        base_path: Base directory for file operations
        own_file: The file this coder agent is responsible for
        
    Returns:
        Updated context after execution
    """
    interpreter = CoderLanguageInterpreter(base_path=base_path, own_file=own_file)
    return interpreter.execute(directive_text)


def execute_directives(directives_text: str, base_path: str = ".", own_file: str = None) -> Dict[str, Any]:
    """
    Execute multiple coder directives.
    
    Args:
        directives_text: Text containing multiple directives
        base_path: Base directory for file operations
        own_file: The file this coder agent is responsible for
        
    Returns:
        Updated context after execution
    """
    interpreter = CoderLanguageInterpreter(base_path=base_path, own_file=own_file)
    return interpreter.execute_multiple(directives_text) 