"""
Comprehensive test suite for the Coder Language Parser.

Tests cover all functions in parser.py using partitioning methods to ensure
complete coverage of parsing functionality for autonomous agent file operations.
"""

import pytest
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.languages.coder_language.parser import (
    CoderLanguageParser,
    CoderLanguageTransformer,
    parse_directive,
    parse_directives
)
from src.languages.coder_language.ast import (
    ReadDirective,
    RunDirective,
    ChangeDirective,
    FinishDirective,
    PromptField
)


class TestCoderLanguageParser:
    """Test suite for the CoderLanguageParser class."""
    
    def setup_method(self):
        self.parser = CoderLanguageParser()
    
    # ========== READ DIRECTIVE PARSING ==========
    
    def test_parse_read_simple(self):
        """Test parsing simple READ directive."""
        directive = 'READ "test.py"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ReadDirective)
        assert result.filename == "test.py"
        assert str(result) == 'READ "test.py"'
    
    def test_parse_read_with_path(self):
        """Test parsing READ directive with file path."""
        directive = 'READ "src/utils/helper.py"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ReadDirective)
        assert result.filename == "src/utils/helper.py"
    
    def test_parse_read_with_spaces(self):
        """Test parsing READ directive with spaces in filename."""
        directive = 'READ "my file with spaces.txt"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ReadDirective)
        assert result.filename == "my file with spaces.txt"
    
    # ========== RUN DIRECTIVE PARSING ==========
    
    def test_parse_run_simple(self):
        """Test parsing simple RUN directive."""
        directive = 'RUN "echo hello"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "echo hello"
        assert str(result) == 'RUN "echo hello"'
    
    def test_parse_run_complex_command(self):
        """Test parsing RUN directive with complex command."""
        directive = 'RUN "python -m pytest tests/ -v --tb=short"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "python -m pytest tests/ -v --tb=short"
    
    # ========== CHANGE DIRECTIVE PARSING ==========
    
    def test_parse_change_simple(self):
        """Test parsing simple CHANGE directive."""
        directive = 'CHANGE CONTENT="print(\'hello\')"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ChangeDirective)
        assert result.content == "print('hello')"
    
    def test_parse_change_multiline_content(self):
        """Test parsing CHANGE directive with multiline content."""
        content = "def hello():\\n    print('Hello, World!')\\n    return True"
        directive = f'CHANGE CONTENT="{content}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ChangeDirective)
        assert "def hello():" in result.content
        assert "Hello, World!" in result.content
    
    def test_parse_change_empty_content(self):
        """Test parsing CHANGE directive with empty content."""
        directive = 'CHANGE CONTENT=""'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ChangeDirective)
        assert result.content == ""
    
    # ========== FINISH DIRECTIVE PARSING ==========
    
    def test_parse_finish_simple(self):
        """Test parsing simple FINISH directive."""
        directive = 'FINISH PROMPT="Task completed"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, FinishDirective)
        assert isinstance(result.prompt, PromptField)
        assert result.prompt.value == "Task completed"
        assert str(result) == 'FINISH PROMPT="Task completed"'
    
    def test_parse_finish_complex_message(self):
        """Test parsing FINISH directive with complex message."""
        message = "Successfully implemented the user authentication system"
        directive = f'FINISH PROMPT="{message}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, FinishDirective)
        assert result.prompt.value == message
    
    def test_parse_finish_empty_message(self):
        """Test parsing FINISH directive with empty message."""
        directive = 'FINISH PROMPT=""'
        result = self.parser.parse(directive)
        
        assert isinstance(result, FinishDirective)
        assert result.prompt.value == ""
    
    # ========== MULTIPLE DIRECTIVES PARSING ==========
    
    def test_parse_multiple_simple(self):
        """Test parsing multiple simple directives."""
        directives_text = '''
        READ "file1.py"
        READ "file2.py"
        RUN "echo test"
        '''
        
        result = self.parser.parse_multiple(directives_text)
        
        assert len(result) == 3
        assert isinstance(result[0], ReadDirective)
        assert isinstance(result[1], ReadDirective)
        assert isinstance(result[2], RunDirective)
        assert result[0].filename == "file1.py"
        assert result[1].filename == "file2.py"
        assert result[2].command == "echo test"
    
    def test_parse_multiple_mixed_types(self):
        """Test parsing multiple directives of different types."""
        directives_text = '''
        READ "config.py"
        RUN "python -m pytest"
        CHANGE CONTENT="def hello(): pass"
        FINISH PROMPT="All done"
        '''
        
        result = self.parser.parse_multiple(directives_text)
        
        assert len(result) == 4
        assert isinstance(result[0], ReadDirective)
        assert isinstance(result[1], RunDirective)
        assert isinstance(result[2], ChangeDirective)
        assert isinstance(result[3], FinishDirective)
    
    def test_parse_multiple_with_empty_lines(self):
        """Test parsing multiple directives with empty lines."""
        directives_text = '''
        
        READ "file1.py"
        
        
        READ "file2.py"
        
        '''
        
        result = self.parser.parse_multiple(directives_text)
        
        assert len(result) == 2
        assert all(isinstance(d, ReadDirective) for d in result)
    
    def test_parse_multiple_with_comments(self):
        """Test parsing multiple directives with comments."""
        directives_text = '''
        // This is a comment
        READ "file1.py"
        // Another comment
        READ "file2.py"
        // Final comment
        '''
        
        result = self.parser.parse_multiple(directives_text)
        
        assert len(result) == 2
        assert all(isinstance(d, ReadDirective) for d in result)
    
    # ========== ERROR HANDLING TESTS ==========
    
    def test_parse_invalid_directive(self):
        """Test parsing an invalid directive."""
        directive = 'INVALID "this should fail"'
        
        with pytest.raises(Exception) as exc_info:
            self.parser.parse(directive)
        
        assert "Failed to parse coder directive" in str(exc_info.value)
    
    def test_parse_malformed_read(self):
        """Test parsing malformed READ directive."""
        directive = 'READ'  # Missing filename
        
        with pytest.raises(Exception):
            self.parser.parse(directive)
    
    def test_parse_malformed_change(self):
        """Test parsing malformed CHANGE directive."""
        directive = 'CHANGE'  # Missing CONTENT
        
        with pytest.raises(Exception):
            self.parser.parse(directive)
    
    def test_parse_malformed_finish(self):
        """Test parsing malformed FINISH directive."""
        directive = 'FINISH'  # Missing PROMPT
        
        with pytest.raises(Exception):
            self.parser.parse(directive)
    
    def test_parse_empty_input(self):
        """Test parsing empty input."""
        with pytest.raises(Exception):
            self.parser.parse("")
    
    def test_parse_multiple_with_invalid_directive(self):
        """Test parsing multiple directives with one invalid."""
        directives_text = '''
        READ "valid.py"
        INVALID "this should fail"
        RUN "echo test"
        '''
        
        with pytest.raises(Exception) as exc_info:
            self.parser.parse_multiple(directives_text)
        
        assert "Failed to parse coder directives" in str(exc_info.value)


class TestCoderLanguageTransformer:
    """Test suite for the CoderLanguageTransformer class."""
    
    def setup_method(self):
        self.transformer = CoderLanguageTransformer()
    
    def test_unescape_string_basic(self):
        """Test basic string unescaping."""
        result = self.transformer._unescape_string("hello world")
        assert result == "hello world"
    
    def test_unescape_string_with_quotes(self):
        """Test unescaping strings with quotes."""
        result = self.transformer._unescape_string('say \\"hello\\"')
        assert result == 'say "hello"'
    
    def test_unescape_string_with_newlines(self):
        """Test unescaping strings with newlines."""
        result = self.transformer._unescape_string("line1\\nline2")
        assert result == "line1\nline2"
    
    def test_unescape_string_with_tabs(self):
        """Test unescaping strings with tabs."""
        result = self.transformer._unescape_string("col1\\tcol2")
        assert result == "col1\tcol2"
    
    def test_unescape_string_with_backslashes(self):
        """Test unescaping strings with backslashes."""
        result = self.transformer._unescape_string("path\\\\to\\\\file")
        assert result == "path\\to\\file"
    
    def test_unescape_string_with_mixed_escapes(self):
        """Test unescaping strings with mixed escape sequences."""
        result = self.transformer._unescape_string('text \\"with\\" \\n newline \\t tab')
        assert result == 'text "with" \n newline \t tab'
    
    def test_string_transformation(self):
        """Test string token transformation."""
        # Simulate a string token with quotes
        class MockToken:
            def __str__(self):
                return '"hello world"'
        
        result = self.transformer.string(MockToken())
        assert result == "hello world"
    
    def test_prompt_field_transformation(self):
        """Test prompt field transformation."""
        result = self.transformer.prompt_field("Create a new file")
        assert isinstance(result, PromptField)
        assert result.value == "Create a new file"
    
    def test_filename_transformation(self):
        """Test filename transformation."""
        result = self.transformer.filename("test.py")
        assert result == "test.py"
    
    def test_command_transformation(self):
        """Test command transformation."""
        result = self.transformer.command("python -m pytest")
        assert result == "python -m pytest"


class TestConvenienceFunctions:
    """Test suite for convenience parsing functions."""
    
    def test_parse_directive_function(self):
        """Test the parse_directive convenience function."""
        directive = 'READ "test.py"'
        result = parse_directive(directive)
        
        assert isinstance(result, ReadDirective)
        assert result.filename == "test.py"
    
    def test_parse_directives_function(self):
        """Test the parse_directives convenience function."""
        directives_text = '''
        READ "file1.py"
        RUN "echo test"
        FINISH PROMPT="Done"
        '''
        
        result = parse_directives(directives_text)
        
        assert len(result) == 3
        assert isinstance(result[0], ReadDirective)
        assert isinstance(result[1], RunDirective)
        assert isinstance(result[2], FinishDirective)
    
    def test_parse_directive_function_error(self):
        """Test error handling in parse_directive function."""
        with pytest.raises(Exception):
            parse_directive('INVALID "directive"')
    
    def test_parse_directives_function_error(self):
        """Test error handling in parse_directives function."""
        with pytest.raises(Exception):
            parse_directives('INVALID "directive"')


def test_change_content_multiline_newlines():
    # LLM outputs single-backslash \n in quoted string
    directive = 'CHANGE CONTENT = "line1\nline2\nline3"'
    result = parse_directive(directive)
    assert result.content == "line1\nline2\nline3"
    # Should be real newlines after parsing
    assert result.content.split("\n") == ["line1", "line2", "line3"]


def test_change_content_real_newlines():
    # LLM outputs real newlines in quoted string (should also work)
    directive = 'CHANGE CONTENT = "line1\nline2\nline3"'.replace("\\n", "\n")
    result = parse_directive(directive)
    assert result.content == "line1\nline2\nline3"
    assert result.content.split("\n") == ["line1", "line2", "line3"]


def test_change_content_double_backslash():
    # LLM outputs double-backslash \n (should NOT be treated as newline)
    directive = r'CHANGE CONTENT = "line1\\nline2\\nline3"'
    result = parse_directive(directive)
    # Should be literal backslash-n, not a newline
    assert result.content == "line1\\nline2\\nline3"
    assert "\n" not in result.content  # No real newlines
    assert "\\n" in result.content 