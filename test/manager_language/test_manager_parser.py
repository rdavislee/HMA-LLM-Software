"""
Comprehensive test suite for the Manager Language Parser.

Tests cover all functions in parser.py using partitioning methods to ensure
complete coverage of parsing functionality for autonomous agent coordination.
"""

import pytest
import os
import tempfile
from pathlib import Path
from typing import List

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from manager_language.parser import (
    ManagerLanguageParser,
    ManagerLanguageTransformer,
    parse_directive,
    parse_directives
)
from manager_language.ast import (
    DelegateDirective,
    FinishDirective,
    ActionDirective,
    WaitDirective,
    RunDirective,
    UpdateReadmeDirective,
    DelegateItem,
    Target,
    PromptField
)


class TestManagerLanguageTransformer:
    """Test suite for the Lark transformer that converts parse trees to AST objects."""
    
    def setup_method(self):
        """Set up transformer for each test."""
        self.transformer = ManagerLanguageTransformer()
    
    # String handling tests
    def test_string_unescaping_basic(self):
        """Test basic string unescaping functionality."""
        # Test basic escape sequences
        test_cases = [
            ('hello\\nworld', 'hello\nworld'),
            ('quotes\\"here\\"', 'quotes"here"'),
            ('backslash\\\\test', 'backslash\\test'),
            ('tab\\tseparated', 'tab\tseparated'),
            ('carriage\\rreturn', 'carriage\rreturn'),
        ]
        
        for input_str, expected in test_cases:
            result = self.transformer._unescape_string(input_str)
            assert result == expected, f"Failed for input: {input_str}"
    
    def test_string_unescaping_edge_cases(self):
        """Test edge cases in string unescaping."""
        # Test empty string
        assert self.transformer._unescape_string("") == ""
        
        # Test string with no escapes
        assert self.transformer._unescape_string("plain text") == "plain text"
        
        # Test incomplete escape sequence
        assert self.transformer._unescape_string("test\\") == "test\\"
        
        # Test unknown escape sequence
        assert self.transformer._unescape_string("test\\x") == "test\\x"
    
    # REMOVED: test_string_transformation and test_escape_char_transformation as obsolete


class TestManagerLanguageParser:
    """Test suite for the main parser class."""
    
    def setup_method(self):
        """Set up parser for each test."""
        self.parser = ManagerLanguageParser()
    
    # CREATE directive tests
    def test_parse_create_file(self):
        """Test parsing CREATE file directive."""
        directive = 'CREATE file "test.txt"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ActionDirective)
        assert result.action_type == "CREATE"
        assert len(result.targets) == 1
        assert result.targets[0].name == "test.txt"
        assert not result.targets[0].is_folder
    
    def test_parse_create_folder(self):
        """Test parsing CREATE folder directive."""
        directive = 'CREATE folder "my_folder"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ActionDirective)
        assert result.action_type == "CREATE"
        assert len(result.targets) == 1
        assert result.targets[0].name == "my_folder"
        assert result.targets[0].is_folder
    
    def test_parse_create_multiple_targets(self):
        """Test parsing CREATE with multiple targets."""
        directive = 'CREATE file "file1.txt", file "file2.txt", folder "folder1"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ActionDirective)
        assert result.action_type == "CREATE"
        assert len(result.targets) == 3
        assert result.targets[0].name == "file1.txt" and not result.targets[0].is_folder
        assert result.targets[1].name == "file2.txt" and not result.targets[1].is_folder
        assert result.targets[2].name == "folder1" and result.targets[2].is_folder
    
    # DELETE directive tests
    def test_parse_delete_file(self):
        """Test parsing DELETE file directive."""
        directive = 'DELETE file "test.txt"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ActionDirective)
        assert result.action_type == "DELETE"
        assert len(result.targets) == 1
        assert result.targets[0].name == "test.txt"
        assert not result.targets[0].is_folder
    
    def test_parse_delete_folder(self):
        """Test parsing DELETE folder directive."""
        directive = 'DELETE folder "my_folder"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ActionDirective)
        assert result.action_type == "DELETE"
        assert len(result.targets) == 1
        assert result.targets[0].name == "my_folder"
        assert result.targets[0].is_folder
    
    # READ directive tests
    def test_parse_read_file(self):
        """Test parsing READ file directive."""
        directive = 'READ file "test.txt"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ActionDirective)
        assert result.action_type == "READ"
        assert len(result.targets) == 1
        assert result.targets[0].name == "test.txt"
        assert not result.targets[0].is_folder
    
    def test_parse_read_folder(self):
        """Test parsing READ folder directive."""
        directive = 'READ folder "my_folder"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ActionDirective)
        assert result.action_type == "READ"
        assert len(result.targets) == 1
        assert result.targets[0].name == "my_folder"
        assert result.targets[0].is_folder
    
    # DELEGATE directive tests
    def test_parse_delegate_single(self):
        """Test parsing single DELEGATE directive."""
        directive = 'DELEGATE file "test.txt" PROMPT="Create this file"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, DelegateDirective)
        assert len(result.items) == 1
        assert result.items[0].target.name == "test.txt"
        assert not result.items[0].target.is_folder
        assert result.items[0].prompt.value == "Create this file"
    
    def test_parse_delegate_multiple(self):
        """Test parsing multiple DELEGATE items."""
        directive = 'DELEGATE file "file1.txt" PROMPT="Create file1", file "file2.txt" PROMPT="Create file2"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, DelegateDirective)
        assert len(result.items) == 2
        assert result.items[0].target.name == "file1.txt"
        assert result.items[0].prompt.value == "Create file1"
        assert result.items[1].target.name == "file2.txt"
        assert result.items[1].prompt.value == "Create file2"
    
    def test_parse_delegate_mixed_targets(self):
        """Test parsing DELEGATE with mixed file and folder targets."""
        directive = 'DELEGATE file "config.json" PROMPT="Create config", folder "src" PROMPT="Create source folder"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, DelegateDirective)
        assert len(result.items) == 2
        assert result.items[0].target.name == "config.json" and not result.items[0].target.is_folder
        assert result.items[1].target.name == "src" and result.items[1].target.is_folder
    
    # FINISH directive tests
    def test_parse_finish(self):
        """Test parsing FINISH directive."""
        directive = 'FINISH PROMPT="Task completed successfully"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, FinishDirective)
        assert result.prompt.value == "Task completed successfully"
    
    def test_parse_finish_with_escaped_chars(self):
        """Test parsing FINISH directive with escaped characters."""
        directive = 'FINISH PROMPT="Task completed\\nwith newlines\\tand tabs"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, FinishDirective)
        assert result.prompt.value == "Task completed\nwith newlines\tand tabs"
    
    # WAIT directive tests
    def test_parse_wait(self):
        """Test parsing WAIT directive."""
        directive = 'WAIT'
        result = self.parser.parse(directive)
        
        assert isinstance(result, WaitDirective)
    
    # RUN directive tests
    def test_parse_run_simple_command(self):
        """Test parsing RUN directive with simple command."""
        directive = 'RUN "echo hello world"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "echo hello world"
    
    def test_parse_run_complex_command(self):
        """Test parsing RUN directive with complex command."""
        directive = 'RUN "npm install && npm run build"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "npm install && npm run build"
    
    def test_parse_run_command_with_quotes(self):
        """Test parsing RUN directive with command containing quotes."""
        directive = 'RUN "git commit -m \\"Initial commit\\""'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "git commit -m \"Initial commit\""
    
    def test_parse_run_command_with_escaped_chars(self):
        """Test parsing RUN directive with escaped characters."""
        directive = 'RUN "echo \\"Hello\\nWorld\\""'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "echo \"Hello\nWorld\""
    
    def test_parse_run_command_with_paths(self):
        """Test parsing RUN directive with file paths."""
        directive = 'RUN "python src/main.py --config config.json"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "python src/main.py --config config.json"
    
    # UPDATE_README directive tests
    def test_parse_update_readme_simple(self):
        """Test parsing simple UPDATE_README directive."""
        directive = 'UPDATE_README CONTENT_STRING="This is the new README content"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, UpdateReadmeDirective)
        assert result.content == "This is the new README content"
    
    def test_parse_update_readme_with_escaped_quotes(self):
        """Test parsing UPDATE_README directive with escaped quotes."""
        directive = 'UPDATE_README CONTENT_STRING="README with \\"quotes\\" inside"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, UpdateReadmeDirective)
        assert result.content == 'README with "quotes" inside'
    
    def test_parse_update_readme_with_newlines(self):
        """Test parsing UPDATE_README directive with newlines."""
        directive = 'UPDATE_README CONTENT_STRING="README\\nwith\\nmultiple\\nlines"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, UpdateReadmeDirective)
        assert result.content == "README\nwith\nmultiple\nlines"
    
    def test_parse_update_readme_with_tabs(self):
        """Test parsing UPDATE_README directive with tabs."""
        directive = 'UPDATE_README CONTENT_STRING="README\\twith\\ttabs"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, UpdateReadmeDirective)
        assert result.content == "README\twith\ttabs"
    
    def test_parse_update_readme_empty_content(self):
        """Test parsing UPDATE_README directive with empty content."""
        directive = 'UPDATE_README CONTENT_STRING=""'
        result = self.parser.parse(directive)
        
        assert isinstance(result, UpdateReadmeDirective)
        assert result.content == ""
    
    def test_parse_update_readme_complex_content(self):
        """Test parsing UPDATE_README directive with complex markdown content."""
        complex_content = """# Agent Documentation

This agent is responsible for:
- File operations (CREATE, DELETE, READ)
- Task delegation to child agents
- Documentation updates

## Usage Examples
```bash
CREATE file "config.json"
DELEGATE file "src/main.py" PROMPT="Create main function"
UPDATE_README CONTENT_STRING="Updated documentation"
```

## Configuration
The agent uses the following directives:
- CREATE: Create files and folders
- DELETE: Remove files and folders
- READ: Read file contents or list folder contents
- DELEGATE: Assign tasks to child agents
- FINISH: Mark task completion
- WAIT: Wait for child agents
- RUN: Execute shell commands
- UPDATE_README: Update agent's personal README
"""
        # Escape the content for the directive
        escaped_content = complex_content.replace('"', '\\"').replace('\n', '\\n')
        directive = f'UPDATE_README CONTENT_STRING="{escaped_content}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, UpdateReadmeDirective)
        assert "# Agent Documentation" in result.content
        assert "File operations" in result.content
        assert "UPDATE_README" in result.content
    
    def test_parse_update_readme_with_special_chars(self):
        """Test parsing UPDATE_README directive with various special characters."""
        directive = 'UPDATE_README CONTENT_STRING="README with \\n newlines, \\t tabs, \\"quotes\\", and \\\\ backslashes"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, UpdateReadmeDirective)
        assert result.content == "README with \n newlines, \t tabs, \"quotes\", and \\ backslashes"
    
    def test_parse_update_readme_malformed(self):
        """Test parsing malformed UPDATE_README directive."""
        with pytest.raises(Exception):
            self.parser.parse('UPDATE_README')
        
        with pytest.raises(Exception):
            self.parser.parse('UPDATE_README CONTENT_STRING')
        
        with pytest.raises(Exception):
            self.parser.parse('UPDATE_README CONTENT_STRING=')
    
    # String escaping tests
    def test_parse_with_escaped_quotes(self):
        """Test parsing directives with escaped quotes in strings."""
        directive = 'DELEGATE file "config.json" PROMPT="Create JSON with \\"quotes\\" inside"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, DelegateDirective)
        assert result.items[0].prompt.value == 'Create JSON with "quotes" inside'
    
    def test_parse_with_newlines_in_prompt(self):
        """Test parsing directives with newlines in prompts."""
        directive = 'DELEGATE file "readme.md" PROMPT="Create a README\\nwith multiple\\nlines"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, DelegateDirective)
        assert result.items[0].prompt.value == "Create a README\nwith multiple\nlines"
    
    # Error handling tests
    def test_parse_invalid_directive(self):
        """Test parsing invalid directive raises exception."""
        with pytest.raises(Exception):
            self.parser.parse('INVALID file "test.txt"')
    
    def test_parse_malformed_delegate(self):
        """Test parsing malformed DELEGATE directive."""
        with pytest.raises(Exception):
            self.parser.parse('DELEGATE file "test.txt"')
    
    def test_parse_malformed_finish(self):
        """Test parsing malformed FINISH directive."""
        with pytest.raises(Exception):
            self.parser.parse('FINISH')
    
    def test_parse_empty_string(self):
        """Test parsing empty string raises exception."""
        with pytest.raises(Exception):
            self.parser.parse('')
    
    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only string raises exception."""
        with pytest.raises(Exception):
            self.parser.parse('   \n\t   ')
    
    # Multiple directive parsing tests
    def test_parse_multiple_directives(self):
        """Test parsing multiple directives from text block."""
        directives_text = """
        CREATE folder "project"
        CREATE file "project/README.md"
        DELEGATE file "project/README.md" PROMPT="Create project documentation"
        WAIT
        FINISH PROMPT="Project setup complete"
        """
        
        results = self.parser.parse_multiple(directives_text)
        
        assert len(results) == 5
        assert isinstance(results[0], ActionDirective) and results[0].action_type == "CREATE"
        assert isinstance(results[1], ActionDirective) and results[1].action_type == "CREATE"
        assert isinstance(results[2], DelegateDirective)
        assert isinstance(results[3], WaitDirective)
        assert isinstance(results[4], FinishDirective)
    
    def test_parse_multiple_with_comments(self):
        """Test parsing multiple directives with comments."""
        directives_text = """
        // Create project structure
        CREATE folder "project"
        CREATE file "project/config.json"  // Configuration file
        DELEGATE file "project/config.json" PROMPT="Create JSON config"
        // Wait for completion
        WAIT
        FINISH PROMPT="Setup complete"
        """
        
        results = self.parser.parse_multiple(directives_text)
        
        assert len(results) == 5  # Comments should be ignored
        assert isinstance(results[0], ActionDirective)
        assert isinstance(results[1], ActionDirective)
        assert isinstance(results[2], DelegateDirective)
        assert isinstance(results[3], WaitDirective)
        assert isinstance(results[4], FinishDirective)
    
    def test_parse_multiple_with_empty_lines(self):
        """Test parsing multiple directives with empty lines."""
        directives_text = """
        CREATE folder "project"
        
        CREATE file "project/main.py"
        
        DELEGATE file "project/main.py" PROMPT="Create main function"
        
        WAIT
        
        FINISH PROMPT="Done"
        """
        
        results = self.parser.parse_multiple(directives_text)
        
        assert len(results) == 5  # Empty lines should be ignored
        assert all(isinstance(result, (ActionDirective, DelegateDirective, WaitDirective, FinishDirective)) 
                  for result in results)
    
    # Edge cases for autonomous agent coordination
    def test_parse_delegate_with_complex_prompt(self):
        """Test parsing DELEGATE with complex prompt for agent coordination."""
        directive = 'DELEGATE folder "api" PROMPT="Create REST API with authentication, user management, and post CRUD operations. Coordinate with database agent for schema."'
        result = self.parser.parse(directive)
        
        assert isinstance(result, DelegateDirective)
        assert result.items[0].target.name == "api"
        assert result.items[0].target.is_folder
        assert "REST API" in result.items[0].prompt.value
        assert "authentication" in result.items[0].prompt.value
    
    def test_parse_concurrent_delegation(self):
        """Test parsing multiple concurrent delegations."""
        directive = 'DELEGATE file "frontend/index.html" PROMPT="Create HTML structure", file "frontend/styles.css" PROMPT="Create CSS styles", file "frontend/script.js" PROMPT="Create JavaScript functionality"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, DelegateDirective)
        assert len(result.items) == 3
        assert all(item.target.name in ["frontend/index.html", "frontend/styles.css", "frontend/script.js"] 
                  for item in result.items)
    
    def test_parse_readme_creation(self):
        """Test parsing README creation directive."""
        directive = 'CREATE file "README.md"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ActionDirective)
        assert result.action_type == "CREATE"
        assert result.targets[0].name == "README.md"
        assert not result.targets[0].is_folder


class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    def test_parse_directive_function(self):
        """Test the parse_directive convenience function."""
        directive = 'CREATE file "test.txt"'
        result = parse_directive(directive)
        
        assert isinstance(result, ActionDirective)
        assert result.action_type == "CREATE"
        assert result.targets[0].name == "test.txt"
    
    def test_parse_directives_function(self):
        """Test the parse_directives convenience function."""
        directives_text = """
        CREATE folder "project"
        CREATE file "project/main.py"
        DELEGATE file "project/main.py" PROMPT="Create main function"
        """
        
        results = parse_directives(directives_text)
        
        assert len(results) == 3
        assert isinstance(results[0], ActionDirective)
        assert isinstance(results[1], ActionDirective)
        assert isinstance(results[2], DelegateDirective)
    
    def test_parse_directive_function_error_handling(self):
        """Test error handling in parse_directive function."""
        with pytest.raises(Exception):
            parse_directive('INVALID directive')
    
    def test_parse_directives_function_error_handling(self):
        """Test error handling in parse_directives function."""
        with pytest.raises(Exception):
            parse_directives('CREATE file "test.txt"\nINVALID directive')


class TestParserIntegration:
    """Integration tests for parser with autonomous agent scenarios."""
    
    def setup_method(self):
        """Set up parser for integration tests."""
        self.parser = ManagerLanguageParser()
    
    def test_hierarchical_delegation_parsing(self):
        """Test parsing hierarchical delegation scenario."""
        directives = [
            'CREATE folder "api"',
            'CREATE folder "api/auth"',
            'CREATE folder "api/posts"',
            'DELEGATE folder "api/auth" PROMPT="Implement authentication system"',
            'DELEGATE folder "api/posts" PROMPT="Implement post management"',
            'WAIT',
            'FINISH PROMPT="API modules created"'
        ]
        
        results = []
        for directive in directives:
            result = self.parser.parse(directive)
            results.append(result)
        
        assert len(results) == 7
        assert all(isinstance(result, (ActionDirective, DelegateDirective, WaitDirective, FinishDirective)) 
                  for result in results)
    
    def test_concurrent_task_parsing(self):
        """Test parsing concurrent task delegation."""
        concurrent_directive = 'DELEGATE file "frontend/index.html" PROMPT="Create HTML", file "frontend/styles.css" PROMPT="Create CSS", file "frontend/script.js" PROMPT="Create JS"'
        result = self.parser.parse(concurrent_directive)
        
        assert isinstance(result, DelegateDirective)
        assert len(result.items) == 3
        assert all("frontend" in item.target.name for item in result.items)
    
    def test_readme_generation_parsing(self):
        """Test parsing README generation workflow."""
        directives = [
            'CREATE file "README.md"',
            'DELEGATE file "README.md" PROMPT="Create comprehensive documentation for this module"',
            'WAIT',
            'FINISH PROMPT="Documentation complete"'
        ]
        
        results = []
        for directive in directives:
            result = self.parser.parse(directive)
            results.append(result)
        
        assert len(results) == 4
        assert results[0].action_type == "CREATE"
        assert isinstance(results[1], DelegateDirective)
        assert isinstance(results[2], WaitDirective)
        assert isinstance(results[3], FinishDirective) 