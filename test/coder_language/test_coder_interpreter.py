"""
Comprehensive test suite for the Coder Language Interpreter.

Tests cover all functions in interpreter.py using partitioning methods to ensure
complete coverage of interpreter functionality for autonomous agent file management.
"""

import pytest
import os
import tempfile
from pathlib import Path
import shutil
import subprocess

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from coder_language.interpreter import (
    CoderLanguageInterpreter,
    execute_directive,
    execute_directives
)
from coder_language.ast import (
    ReadDirective,
    RunDirective,
    ChangeDirective,
    FinishDirective,
    PromptField
)
from coder_language.parser import escape_content


def temp_workspace():
    """Context manager for a temporary workspace directory."""
    d = tempfile.mkdtemp()
    try:
        yield d
    finally:
        shutil.rmtree(d)


class TestCoderLanguageInterpreter:
    """Test suite for the Coder Language Interpreter class."""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.own_file = "my_file.py"
        self.interpreter = CoderLanguageInterpreter(base_path=self.temp_dir, own_file=self.own_file)
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    # ========== READ DIRECTIVE TESTS ==========
    
    def test_execute_read_existing_file(self):
        """Test reading an existing file - basic success case."""
        test_file = Path(self.temp_dir) / "test.txt" 
        test_content = "Hello, world!"
        test_file.write_text(test_content)
        
        directive = 'READ "test.txt"'
        result = self.interpreter.execute(directive)
        
        assert 'reads' in result
        assert len(result['reads']) == 1
        assert result['reads'][0]['filename'] == "test.txt"
        assert result['reads'][0]['status'] == "completed"
        assert result['reads'][0]['result']['success'] is True
        assert result['reads'][0]['result']['content'] == test_content
    
    def test_execute_read_nonexistent_file(self):
        """Test reading a file that doesn't exist - error case."""
        directive = 'READ "nonexistent.txt"'
        result = self.interpreter.execute(directive)
        
        assert 'reads' in result
        assert len(result['reads']) == 1
        assert result['reads'][0]['filename'] == "nonexistent.txt"
        assert result['reads'][0]['status'] == "failed"
        assert result['reads'][0]['result']['success'] is False
        assert "File not found" in result['reads'][0]['result']['error']
    
    def test_execute_read_nested_file(self):
        """Test reading a file in nested directory - path handling."""
        nested_dir = Path(self.temp_dir) / "src" / "utils"
        nested_dir.mkdir(parents=True)
        nested_file = nested_dir / "helper.py"
        nested_content = "def helper(): pass"
        nested_file.write_text(nested_content)
        
        directive = 'READ "src/utils/helper.py"'
        result = self.interpreter.execute(directive)
        
        assert result['reads'][0]['status'] == "completed"
        assert result['reads'][0]['result']['content'] == nested_content
    
    def test_execute_read_large_file(self):
        """Test reading a large file."""
        # Create large file
        large_file = Path(self.temp_dir) / "large.txt"
        large_content = "This is line {}\n" * 1000
        large_file.write_text(large_content.format(*range(1000)))
        
        directive = 'READ "large.txt"'
        result = self.interpreter.execute(directive)
        
        assert result['reads'][0]['status'] == "completed"
        assert len(result['reads'][0]['result']['content']) > 10000
    
    def test_execute_read_empty_file(self):
        """Test reading an empty file - edge case."""
        empty_file = Path(self.temp_dir) / "empty.txt"
        empty_file.touch()
        
        directive = 'READ "empty.txt"'
        result = self.interpreter.execute(directive)
        
        assert result['reads'][0]['status'] == "completed"
        assert result['reads'][0]['result']['content'] == ""
    
    def test_execute_read_binary_file(self):
        """Test reading a binary file (should handle gracefully)."""
        binary_file = Path(self.temp_dir) / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03\xFF')
        
        directive = 'READ "binary.bin"'
        result = self.interpreter.execute(directive)
        
        # Should either succeed or fail gracefully
        assert result['reads'][0]['filename'] == "binary.bin"
        assert result['reads'][0]['status'] in ["completed", "failed"]
    
    def test_execute_multiple_reads(self):
        """Test executing multiple READ directives - accumulation."""
        for i in range(3):
            test_file = Path(self.temp_dir) / f"test{i}.txt"
            test_file.write_text(f"Content {i}")
        
        for i in range(3):
            directive = f'READ "test{i}.txt"'
            self.interpreter.execute(directive)
        
        result = self.interpreter.get_context()
        assert len(result['reads']) == 3
        for i in range(3):
            assert result['reads'][i]['filename'] == f"test{i}.txt"
            assert result['reads'][i]['status'] == "completed"
    
    # ========== RUN DIRECTIVE TESTS ==========
    
    def test_execute_run_simple_command(self):
        """Test executing a simple command - basic success case."""
        directive = 'RUN "echo hello world"'
        result = self.interpreter.execute(directive)
        
        assert 'commands' in result
        assert len(result['commands']) == 1
        assert result['commands'][0]['command'] == "echo hello world"
        assert result['commands'][0]['status'] == "completed"
        assert result['commands'][0]['result']['success'] is True
        assert "hello world" in result['commands'][0]['result']['stdout']
    
    def test_execute_run_failing_command(self):
        """Test executing a command that fails - error case."""
        directive = 'RUN "nonexistent_command_12345"'
        result = self.interpreter.execute(directive)
        
        assert 'commands' in result
        assert len(result['commands']) == 1
        assert result['commands'][0]['status'] == "failed"
        assert result['commands'][0]['result']['success'] is False
    
    def test_execute_run_test_command(self):
        """Test executing a typical test command."""
        # Create a simple Python file to test
        test_file = Path(self.temp_dir) / "test_example.py"
        test_file.write_text("def test_pass(): assert True")
        
        directive = f'RUN "python -c \\"import sys; sys.exit(0)\\""'
        result = self.interpreter.execute(directive) 
        
        assert result['commands'][0]['command'] == 'python -c "import sys; sys.exit(0)"'
        assert result['commands'][0]['status'] == "completed"
    
    def test_execute_run_with_output(self):
        """Test command that produces output - output handling."""
        directive = 'RUN "python -c \\"print(\'test output\')\\""'
        result = self.interpreter.execute(directive)
        assert result['commands'][0]['status'] == "completed"
        assert "test output" in result['commands'][0]['result']['stdout']
    
    def test_execute_run_with_stderr(self):
        """Test command that produces stderr output."""
        directive = 'RUN "python -c \\"import sys; print(\'error\', file=sys.stderr); sys.exit(1)\\""'
        result = self.interpreter.execute(directive)
        assert result['commands'][0]['status'] == "failed"
        assert result['commands'][0]['result']['success'] is False
    
    def test_execute_multiple_commands(self):
        """Test executing multiple commands - accumulation."""
        commands = [
            'RUN "echo first"',
            'RUN "echo second"',
            'RUN "echo third"'
        ]
        
        for cmd in commands:
            self.interpreter.execute(cmd)
        
        result = self.interpreter.get_context()
        assert len(result['commands']) == 3
        for i, cmd in enumerate(["first", "second", "third"]):
            assert cmd in result['commands'][i]['result']['stdout']
    
    # ========== CHANGE DIRECTIVE TESTS ==========
    
    def test_execute_change_own_file(self):
        """Test changing the agent's own file - basic success case."""
        new_content = "def my_function():\n    return 'Hello, World!'"
        escaped_content = escape_content(new_content)
        directive = f'CHANGE CONTENT="{escaped_content}"'
        result = self.interpreter.execute(directive)
        
        assert 'changes' in result
        assert len(result['changes']) == 1
        assert result['changes'][0]['filename'] == self.own_file
        assert result['changes'][0]['status'] == "completed"
        assert result['changes'][0]['result']['success'] is True
        
        # Verify file was actually created/changed
        changed_file = Path(self.temp_dir) / self.own_file
        assert changed_file.exists()
        assert changed_file.read_text() == new_content
    
    def test_execute_change_no_own_file(self):
        """Test trying to change file when no own_file is set - security boundary."""
        interpreter_no_file = CoderLanguageInterpreter(base_path=self.temp_dir, own_file=None)
        new_content = "print('unauthorized change')"
        directive = f'CHANGE CONTENT="{new_content}"'
        result = interpreter_no_file.execute(directive)
        
        assert 'changes' in result
        assert len(result['changes']) == 1
        assert result['changes'][0]['status'] == "failed"
        assert "Cannot modify file" in result['changes'][0]['error']
        assert "no assigned file" in result['changes'][0]['error']
    
    def test_execute_change_with_special_characters(self):
        """Test changing file with special characters - content handling."""
        special_content = 'def func():\n    return "quotes", \'apostrophes\', and\nnewlines'
        escaped_content = escape_content(special_content)
        directive = f'CHANGE CONTENT="{escaped_content}"'
        result = self.interpreter.execute(directive)
        
        assert result['changes'][0]['status'] == "completed"
        changed_file = Path(self.temp_dir) / self.own_file
        assert changed_file.read_text() == special_content
    
    def test_execute_change_large_content(self):
        """Test changing file with large content."""
        large_content = "# Large file\n" + ("def func{}(): pass\n" * 1000).format(*range(1000))
        escaped_content = escape_content(large_content)
        directive = f'CHANGE CONTENT="{escaped_content}"'
        result = self.interpreter.execute(directive)
        
        assert result['changes'][0]['status'] == "completed"
        changed_file = Path(self.temp_dir) / self.own_file
        assert len(changed_file.read_text()) > 10000
    
    def test_execute_change_empty_content(self):
        """Test changing file to empty content - edge case."""
        directive = f'CHANGE CONTENT=""'
        result = self.interpreter.execute(directive)
        
        assert result['changes'][0]['status'] == "completed"
        changed_file = Path(self.temp_dir) / self.own_file
        assert changed_file.read_text() == ""
    
    def test_execute_change_nested_own_file(self):
        """Test changing own file when it's in a nested path."""
        nested_own_file = "src/components/MyComponent.js"
        nested_interpreter = CoderLanguageInterpreter(
            base_path=self.temp_dir, 
            own_file=nested_own_file
        )
        
        content = "export default function MyComponent() { return null; }"
        escaped_content = escape_content(content)
        directive = f'CHANGE CONTENT="{escaped_content}"'
        result = nested_interpreter.execute(directive)
        
        assert result['changes'][0]['status'] == "completed"
        changed_file = Path(self.temp_dir) / nested_own_file
        assert changed_file.exists()
        assert changed_file.read_text() == content
    
    def test_execute_multiple_changes(self):
        """Test executing multiple changes to the same file - overwriting."""
        contents = [
            "# Version 1",
            "# Version 2\ndef func(): pass",
            "# Final version\ndef func():\n    return 'done'"
        ]
        
        for content in contents:
            escaped_content = escape_content(content)
            directive = f'CHANGE CONTENT="{escaped_content}"'
            self.interpreter.execute(directive)
        
        result = self.interpreter.get_context()
        assert len(result['changes']) == 3
        
        # Verify final file state
        final_file = Path(self.temp_dir) / self.own_file
        assert final_file.read_text() == contents[-1]
    
    # ========== FINISH DIRECTIVE TESTS ==========
    
    def test_execute_finish_simple(self):
        """Test executing a simple FINISH directive - basic success."""
        directive = 'FINISH PROMPT="Task completed successfully"'
        result = self.interpreter.execute(directive)
        
        assert result['finished'] is True
        assert result['completion_prompt'] == "Task completed successfully"
    
    def test_execute_finish_complex_message(self):
        """Test FINISH directive with complex message - message handling."""
        complex_message = """Task completed successfully!

Implemented features:
1. User authentication
2. Data validation
3. Error handling

All tests are passing."""
        
        directive = f'FINISH PROMPT="{complex_message}"'
        result = self.interpreter.execute(directive)
        
        assert result['finished'] is True
        assert result['completion_prompt'] == complex_message
    
    def test_execute_finish_empty_message(self):
        """Test FINISH directive with empty message - edge case."""
        directive = 'FINISH PROMPT=""'
        result = self.interpreter.execute(directive)
        
        assert result['finished'] is True
        assert result['completion_prompt'] == ""
    
    def test_execute_finish_with_special_characters(self):
        """Test FINISH directive with special characters."""
        special_message = 'Done with "quotes", \'apostrophes\', and\nnewlines!'
        escaped_message = escape_content(special_message)
        directive = f'FINISH PROMPT="{escaped_message}"'
        result = self.interpreter.execute(directive)
        
        assert result['finished'] is True
        assert result['completion_prompt'] == special_message
    
    # ========== CONTEXT MANAGEMENT TESTS ==========
    
    def test_get_context_initial(self):
        """Test getting initial context - initialization."""
        context = self.interpreter.get_context()
        
        assert 'reads' in context
        assert 'commands' in context
        assert 'changes' in context
        assert context['finished'] is False
        assert context['completion_prompt'] is None
        assert context['own_file'] == self.own_file
        assert len(context['reads']) == 0
        assert len(context['commands']) == 0
        assert len(context['changes']) == 0
    
    def test_get_context_after_operations(self):
        """Test getting context after operations - state tracking."""
        self.interpreter.execute('RUN "echo test"')
        self.interpreter.execute(f'CHANGE CONTENT="test"')
        
        context = self.interpreter.get_context()
        
        assert len(context['commands']) == 1
        assert len(context['changes']) == 1
        assert context['finished'] is False
    
    def test_reset_context(self):
        """Test resetting context - state cleanup."""
        self.interpreter.execute('RUN "echo test"')
        self.interpreter.execute(f'CHANGE CONTENT="test"')
        
        self.interpreter.reset_context()
        
        context = self.interpreter.get_context()
        assert len(context['reads']) == 0
        assert len(context['commands']) == 0
        assert len(context['changes']) == 0
        assert context['finished'] is False
        assert context['completion_prompt'] is None
    
    def test_export_context(self):
        """Test exporting context to file - persistence."""
        self.interpreter.execute('RUN "echo test"')
        self.interpreter.execute('FINISH PROMPT="Done"')
        
        export_file = Path(self.temp_dir) / "context.json"
        self.interpreter.export_context(str(export_file))
        
        assert export_file.exists()
        import json
        with open(export_file) as f:
            exported_context = json.load(f)
        
        assert exported_context['finished'] is True
        assert exported_context['completion_prompt'] == "Done"
        assert len(exported_context['commands']) == 1
    
    def test_set_own_file(self):
        """Test setting the own file after initialization - configuration."""
        new_own_file = "new_file.py"
        self.interpreter.set_own_file(new_own_file)
        
        context = self.interpreter.get_context()
        assert context['own_file'] == new_own_file
        
        # Test that CHANGE now works with new file
        content = "new content"
        escaped_content = escape_content(content)
        directive = f'CHANGE CONTENT="{escaped_content}"'
        result = self.interpreter.execute(directive)
        assert result['changes'][0]['status'] == "completed"
    
    # ========== MULTIPLE DIRECTIVES TESTS ==========
    
    def test_execute_multiple_mixed_directives(self):
        """Test executing multiple different types of directives - workflow."""
        directives_text = f'''
        RUN "echo starting work"
        CHANGE CONTENT="print('hello')"
        RUN "echo work complete"
        FINISH PROMPT="All tasks completed"
        '''
        
        result = self.interpreter.execute_multiple(directives_text)
        
        assert len(result['commands']) == 2
        assert len(result['changes']) == 1
        assert result['finished'] is True
        assert result['completion_prompt'] == "All tasks completed"
    
    def test_execute_multiple_with_errors(self):
        """Test executing multiple directives with errors - error handling."""
        directives_text = f'''
        RUN "invalid_command_12345"
        CHANGE CONTENT="valid content"
        FINISH PROMPT="Done with errors"
        '''
        
        result = self.interpreter.execute_multiple(directives_text)
        
        assert len(result['commands']) == 1
        assert result['commands'][0]['status'] == "failed"
        assert len(result['changes']) == 1
        assert result['changes'][0]['status'] == "completed"
        assert result['finished'] is True
    
    # ========== ERROR HANDLING TESTS ==========
    
    def test_execute_invalid_directive(self):
        """Test executing an invalid directive - parsing error."""
        directive = 'INVALID "this should fail"'
        result = self.interpreter.execute(directive)
        
        assert 'error' in result
        assert "Failed to parse coder directive" in result['error']
    
    def test_execute_empty_directive(self):
        """Test executing empty directive - edge case."""
        directive = ''
        result = self.interpreter.execute(directive)
        
        assert 'error' in result
    
    def test_execute_malformed_directive(self):
        """Test executing a malformed directive - syntax error."""
        directive = 'READ'  # Missing filename
        result = self.interpreter.execute(directive)
        
        assert 'error' in result
    
    # ========== INTEGRATION TESTS ==========
    
    def test_typical_coder_workflow(self):
        """Test a typical coder agent workflow - realistic scenario."""
        # Step 1: Read dependencies
        dep_file = Path(self.temp_dir) / "utils.py"
        dep_file.write_text("def helper(): return 'help'")
        
        # Step 2: Read tests to understand requirements
        test_file = Path(self.temp_dir) / "test_my_file.py"
        test_file.write_text("def test_my_function(): assert my_function() == 'hello'")
        
        # Execute workflow
        self.interpreter.execute('READ "utils.py"')
        self.interpreter.execute('READ "test_my_file.py"')
        self.interpreter.execute('RUN "echo understanding requirements"')
        self.interpreter.execute(f'CHANGE CONTENT="from utils import helper\\n\\ndef my_function():\\n    return \'hello\'"')
        self.interpreter.execute('RUN "echo tests would run here"')
        self.interpreter.execute('FINISH PROMPT="Successfully implemented my_function"')
        
        result = self.interpreter.get_context()
        
        assert len(result['reads']) == 2
        assert len(result['commands']) == 2
        assert len(result['changes']) == 1
        assert result['finished'] is True
        assert "Successfully implemented" in result['completion_prompt']
    
    def test_file_ownership_boundary(self):
        """Test that file ownership boundaries are properly enforced - security."""
        # Set up interpreter without own_file (should reject all changes)
        no_file_interpreter = CoderLanguageInterpreter(base_path=self.temp_dir)
        
        directive = 'CHANGE CONTENT="should fail"'
        result = no_file_interpreter.execute(directive)
        
        # Should still record the attempt but mark as failed
        assert result['changes'][0]['status'] == "failed"


class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_execute_directive_function(self):
        """Test the execute_directive convenience function."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        result = execute_directive('READ "test.txt"', base_path=self.temp_dir)
        
        assert result['reads'][0]['status'] == "completed"
        assert result['reads'][0]['result']['content'] == "test content"
    
    def test_execute_directives_function(self):
        """Test the execute_directives convenience function."""
        directives_text = '''
        RUN "echo first"
        RUN "echo second"
        FINISH PROMPT="Done"
        '''
        
        result = execute_directives(directives_text, base_path=self.temp_dir)
        
        assert len(result['commands']) == 2
        assert result['finished'] is True
        assert result['completion_prompt'] == "Done"
    
    def test_execute_directive_function_error_handling(self):
        """Test error handling in convenience functions."""
        result = execute_directive('INVALID "directive"', base_path=self.temp_dir)
        
        assert 'error' in result
    
    def test_execute_directives_function_error_handling(self):
        """Test error handling in execute_directives function."""
        result = execute_directives('INVALID "directive"', base_path=self.temp_dir)
        
        assert 'error' in result 