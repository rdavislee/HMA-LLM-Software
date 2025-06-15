"""
Comprehensive test suite for the Manager Language Interpreter.

Tests cover all functions in interpreter.py using partitioning methods to ensure
complete coverage of interpreter functionality for autonomous agent coordination.
"""

import pytest
import os
import tempfile
from pathlib import Path
import shutil

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from manager_language.interpreter import (
    ManagerLanguageInterpreter,
    execute_directive,
    execute_directives
)
from manager_language.ast import (
    DelegateDirective,
    FinishDirective,
    ActionDirective,
    WaitDirective,
    RunDirective,
    DelegateItem,
    Target,
    PromptField
)


def temp_workspace():
    """Context manager for a temporary workspace directory."""
    d = tempfile.mkdtemp()
    try:
        yield d
    finally:
        shutil.rmtree(d)


class TestManagerLanguageInterpreter:
    """Test suite for the Manager Language Interpreter class."""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.interpreter = ManagerLanguageInterpreter(base_path=self.temp_dir)
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    # CREATE file/folder
    def test_execute_create_file(self):
        directive = 'CREATE file "test.txt"'
        result = self.interpreter.execute(directive)
        file_path = Path(self.temp_dir) / "test.txt"
        assert file_path.exists() and file_path.is_file()
        assert result['actions'][-1]['type'] == "CREATE"
        assert result['actions'][-1]['target'] == "test.txt"
        assert result['actions'][-1]['status'] == "completed"
    
    def test_execute_create_folder(self):
        directive = 'CREATE folder "my_folder"'
        result = self.interpreter.execute(directive)
        folder_path = Path(self.temp_dir) / "my_folder"
        assert folder_path.exists() and folder_path.is_dir()
        assert result['actions'][-1]['type'] == "CREATE"
        assert result['actions'][-1]['target'] == "my_folder"
        assert result['actions'][-1]['status'] == "completed"
    
    def test_execute_create_nested_file(self):
        directive = 'CREATE file "nested/dir/test.txt"'
        result = self.interpreter.execute(directive)
        file_path = Path(self.temp_dir) / "nested/dir/test.txt"
        assert file_path.exists() and file_path.is_file()
        assert result['actions'][-1]['type'] == "CREATE"
        assert result['actions'][-1]['target'] == "nested/dir/test.txt"
    
    # DELETE file/folder
    def test_execute_delete_file(self):
        file_path = Path(self.temp_dir) / "delete_me.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("to be deleted")
        directive = 'DELETE file "delete_me.txt"'
        result = self.interpreter.execute(directive)
        assert not file_path.exists()
        assert result['actions'][-1]['type'] == "DELETE"
        assert result['actions'][-1]['status'] == "completed"
    
    def test_execute_delete_folder(self):
        folder_path = Path(self.temp_dir) / "delete_folder"
        folder_path.mkdir(parents=True, exist_ok=True)
        (folder_path / "file.txt").write_text("test")
        directive = 'DELETE folder "delete_folder"'
        result = self.interpreter.execute(directive)
        assert not folder_path.exists()
        assert result['actions'][-1]['type'] == "DELETE"
        assert result['actions'][-1]['status'] == "completed"
    
    def test_execute_delete_nonexistent(self):
        directive = 'DELETE file "no_such_file.txt"'
        result = self.interpreter.execute(directive)
        assert result['actions'][-1]['status'] == "failed"
        assert "does not exist" in result['actions'][-1]['error']
    
    # READ file/folder
    def test_execute_read_file(self):
        file_path = Path(self.temp_dir) / "readme.txt"
        file_path.write_text("hello world")
        directive = 'READ file "readme.txt"'
        result = self.interpreter.execute(directive)
        assert result['actions'][-1]['type'] == "READ"
        assert result['actions'][-1]['target'] == "readme.txt"
        assert result['actions'][-1]['result']['content'] == "hello world"
        assert result['actions'][-1]['status'] == "completed"
    
    def test_execute_read_folder(self):
        folder_path = Path(self.temp_dir) / "folder"
        folder_path.mkdir()
        (folder_path / "a.txt").write_text("A")
        (folder_path / "b.txt").write_text("B")
        directive = 'READ folder "folder"'
        result = self.interpreter.execute(directive)
        assert result['actions'][-1]['type'] == "READ"
        assert result['actions'][-1]['target'] == "folder"
        assert result['actions'][-1]['result']['success']
        contents = result['actions'][-1]['result']['contents']
        assert any(item['name'] == "a.txt" for item in contents)
        assert any(item['name'] == "b.txt" for item in contents)
    
    def test_execute_read_nonexistent(self):
        directive = 'READ file "no_such_file.txt"'
        result = self.interpreter.execute(directive)
        assert result['actions'][-1]['status'] == "failed"
        assert "does not exist" in result['actions'][-1]['error']
    
    # DELEGATE
    def test_execute_delegate_single(self):
        directive = 'DELEGATE file "test.txt" PROMPT="Create this file"'
        result = self.interpreter.execute(directive)
        assert 'delegations' in result
        assert len(result['delegations']) == 1
        assert result['delegations'][0]['target'] == "test.txt"
        assert result['delegations'][0]['prompt'] == "Create this file"
        assert result['delegations'][0]['status'] == "pending"
    
    def test_execute_delegate_multiple(self):
        directive = 'DELEGATE file "a.txt" PROMPT="A", file "b.txt" PROMPT="B"'
        result = self.interpreter.execute(directive)
        assert len(result['delegations']) == 2
        assert result['delegations'][0]['target'] == "a.txt"
        assert result['delegations'][1]['target'] == "b.txt"
    
    # FINISH
    def test_execute_finish(self):
        directive = 'FINISH PROMPT="All done"'
        result = self.interpreter.execute(directive)
        assert result['finished'] is True
        assert result['completion_prompt'] == "All done"
    
    # WAIT
    def test_execute_wait(self):
        directive = 'WAIT'
        result = self.interpreter.execute(directive)
        assert result['waiting'] is True
    
    # RUN
    def test_execute_run_simple_command(self):
        """Test executing a simple RUN directive."""
        directive = 'RUN "echo hello world"'
        result = self.interpreter.execute(directive)
        
        assert 'commands' in result
        assert len(result['commands']) == 1
        assert result['commands'][0]['command'] == "echo hello world"
        assert result['commands'][0]['status'] == "completed"
        assert result['commands'][0]['result']['success'] is True
        assert "hello world" in result['commands'][0]['result']['stdout']
    
    def test_execute_run_complex_command(self):
        """Test executing a complex RUN directive."""
        # Use a cross-platform command that does not rely on complex quoting
        directive = 'RUN "echo hello world again"'
        result = self.interpreter.execute(directive)

        assert 'commands' in result
        assert len(result['commands']) == 1
        assert result['commands'][0]['command'] == "echo hello world again"
        assert result['commands'][0]['status'] == "completed"
        assert result['commands'][0]['result']['success'] is True
        assert "hello world again" in result['commands'][0]['result']['stdout']
    
    def test_execute_run_failing_command(self):
        """Test executing a RUN directive that fails."""
        directive = 'RUN "nonexistent_command_that_fails"'
        result = self.interpreter.execute(directive)
        
        assert 'commands' in result
        assert len(result['commands']) == 1
        assert result['commands'][0]['command'] == "nonexistent_command_that_fails"
        assert result['commands'][0]['status'] == "failed"
        assert result['commands'][0]['result']['success'] is False
        assert 'error' in result['commands'][0]['result']
    
    def test_execute_run_multiple_commands(self):
        """Test executing multiple RUN directives."""
        directives = '''
        RUN "echo first"
        RUN "echo second"
        '''
        result = self.interpreter.execute_multiple(directives)
        
        assert 'commands' in result
        assert len(result['commands']) == 2
        assert result['commands'][0]['command'] == "echo first"
        assert result['commands'][1]['command'] == "echo second"
        assert result['commands'][0]['status'] == "completed"
        assert result['commands'][1]['status'] == "completed"
    
    def test_execute_run_with_file_operations(self):
        """Test RUN directive combined with file operations."""
        directives = '''
        CREATE file "test.txt"
        RUN "echo content > test.txt"
        READ file "test.txt"
        '''
        result = self.interpreter.execute_multiple(directives)
        
        assert 'actions' in result and len(result['actions']) == 2
        assert 'commands' in result and len(result['commands']) == 1
        assert result['commands'][0]['status'] == "completed"
    
    # Multiple directives
    def test_execute_multiple(self):
        directives = '''
        CREATE folder "proj"
        CREATE file "proj/readme.md"
        DELEGATE file "proj/readme.md" PROMPT="Write documentation"
        RUN "echo 'Project created'"
        WAIT
        FINISH PROMPT="Done"
        '''
        result = self.interpreter.execute_multiple(directives)
        assert 'actions' in result and len(result['actions']) == 2
        assert 'delegations' in result and len(result['delegations']) == 1
        assert 'commands' in result and len(result['commands']) == 1
        assert result['waiting'] is True or result['finished'] is True
    
    # Error handling
    def test_execute_invalid_directive(self):
        directive = 'INVALID file "test.txt"'
        result = self.interpreter.execute(directive)
        assert 'error' in result
        assert "Failed to parse" in result['error'] or "Unknown directive" in result['error']
    
    def test_execute_multiple_with_error(self):
        directives = '''
        CREATE file "a.txt"
        INVALID file "b.txt"
        '''
        result = self.interpreter.execute_multiple(directives)
        assert 'error' in result
    
    # Context management
    def test_get_and_reset_context(self):
        directive = 'CREATE file "test.txt"'
        self.interpreter.execute(directive)
        context = self.interpreter.get_context()
        assert 'actions' in context and len(context['actions']) == 1
        self.interpreter.reset_context()
        context2 = self.interpreter.get_context()
        assert context2['actions'] == []
        assert context2['delegations'] == []
        assert context2['finished'] is False
        assert context2['waiting'] is False
        assert context2['completion_prompt'] is None
    
    # Export context
    def test_export_context(self):
        directive = 'CREATE file "test.txt"'
        self.interpreter.execute(directive)
        export_path = Path(self.temp_dir) / "context.json"
        self.interpreter.export_context(str(export_path))
        assert export_path.exists()
        with open(export_path) as f:
            data = f.read()
            assert 'actions' in data


class TestConvenienceFunctions:
    """Test suite for convenience functions in interpreter.py."""
    
    def test_execute_directive_function(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directive = 'CREATE file "test.txt"'
            result = execute_directive(directive, base_path=temp_dir)
            file_path = Path(temp_dir) / "test.txt"
            assert file_path.exists()
            assert result['actions'][-1]['type'] == "CREATE"
    
    def test_execute_directives_function(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directives = '''
            CREATE folder "proj"
            CREATE file "proj/readme.md"
            '''
            result = execute_directives(directives, base_path=temp_dir)
            folder_path = Path(temp_dir) / "proj"
            file_path = Path(temp_dir) / "proj/readme.md"
            assert folder_path.exists() and folder_path.is_dir()
            assert file_path.exists() and file_path.is_file()
    
    def test_execute_directive_function_error_handling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directive = 'INVALID file "test.txt"'
            result = execute_directive(directive, base_path=temp_dir)
            assert 'error' in result
    
    def test_execute_directives_function_error_handling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directives = '''
            CREATE file "a.txt"
            INVALID file "b.txt"
            '''
            result = execute_directives(directives, base_path=temp_dir)
            assert 'error' in result 