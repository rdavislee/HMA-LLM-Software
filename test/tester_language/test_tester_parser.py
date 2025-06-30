"""
Comprehensive test suite for the Tester Language Parser.

Tests cover all functions in parser.py using partitioning methods to ensure
complete coverage of parsing functionality for tester agent operations.
"""

import pytest
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.languages.tester_language.parser import (
    TesterLanguageParser,
    TesterLanguageTransformer,
    parse_directive,
    parse_directives
)
from src.languages.tester_language.ast import (
    ReadDirective,
    RunDirective,
    ChangeDirective,
    FinishDirective,
    PromptField
)


class TestTesterLanguageParser:
    """Test suite for the TesterLanguageParser class."""
    
    def setup_method(self):
        self.parser = TesterLanguageParser()
    
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
    
    def test_parse_read_test_file(self):
        """Test parsing READ directive for test files."""
        directive = 'READ "tests/test_module.py"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ReadDirective)
        assert result.filename == "tests/test_module.py"
    
    # ========== RUN DIRECTIVE PARSING ==========
    
    def test_parse_run_simple(self):
        """Test parsing simple RUN directive."""
        directive = 'RUN "echo hello"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "echo hello"
        assert str(result) == 'RUN "echo hello"'
    
    def test_parse_run_pytest_command(self):
        """Test parsing RUN directive with pytest command."""
        directive = 'RUN "python -m pytest tests/ -v --tb=short"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "python -m pytest tests/ -v --tb=short"
    
    def test_parse_run_coverage_command(self):
        """Test parsing RUN directive with coverage command."""
        directive = 'RUN "python -m pytest --cov=src --cov-report=term-missing"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "python -m pytest --cov=src --cov-report=term-missing"
    
    def test_parse_run_linting_command(self):
        """Test parsing RUN directive with linting command."""
        directive = 'RUN "flake8 src/ --max-line-length=88"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "flake8 src/ --max-line-length=88"
    
    def test_parse_run_type_checking_command(self):
        """Test parsing RUN directive with type checking command."""
        directive = 'RUN "mypy src/ --strict"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "mypy src/ --strict"
    
    # ========== CHANGE DIRECTIVE PARSING ==========
    
    def test_parse_change_simple(self):
        """Test parsing simple CHANGE directive."""
        directive = 'CHANGE CONTENT="print(\'debug\')"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ChangeDirective)
        assert result.content == "print('debug')"
    
    def test_parse_change_multiline_debug_code(self):
        """Test parsing CHANGE directive with multiline debug code."""
        content = "import sys\\nprint('Debugging module')\\nsys.path.append('.')"
        directive = f'CHANGE CONTENT="{content}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ChangeDirective)
        assert "import sys" in result.content
        assert "Debugging module" in result.content
        assert "sys.path.append" in result.content
    
    def test_parse_change_test_helper_function(self):
        """Test parsing CHANGE directive with test helper function."""
        content = "def test_helper():\\n    return {'status': 'ok', 'data': [1, 2, 3]}"
        directive = f'CHANGE CONTENT="{content}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ChangeDirective)
        assert "def test_helper():" in result.content
        assert "return" in result.content
    
    def test_parse_change_empty_content(self):
        """Test parsing CHANGE directive with empty content."""
        directive = 'CHANGE CONTENT=""'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ChangeDirective)
        assert result.content == ""
    
    def test_parse_change_with_imports(self):
        """Test parsing CHANGE directive with import statements."""
        content = "import pytest\\nimport unittest\\nfrom unittest.mock import patch"
        directive = f'CHANGE CONTENT="{content}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ChangeDirective)
        assert "import pytest" in result.content
        assert "import unittest" in result.content
        assert "from unittest.mock import patch" in result.content
    
    # ========== FINISH DIRECTIVE PARSING ==========
    
    def test_parse_finish_simple(self):
        """Test parsing simple FINISH directive."""
        directive = 'FINISH PROMPT="Testing completed"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, FinishDirective)
        assert isinstance(result.prompt, PromptField)
        assert result.prompt.value == "Testing completed"
        assert str(result) == 'FINISH PROMPT="Testing completed"'
    
    def test_parse_finish_test_results(self):
        """Test parsing FINISH directive with test results."""
        message = "Found 3 failing tests in authentication module - see output above"
        directive = f'FINISH PROMPT="{message}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, FinishDirective)
        assert result.prompt.value == message
    
    def test_parse_finish_coverage_report(self):
        """Test parsing FINISH directive with coverage report."""
        message = "Test coverage analysis complete: 85% coverage, 12 uncovered lines"
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
    
    def test_parse_finish_performance_analysis(self):
        """Test parsing FINISH directive with performance analysis."""
        message = "Performance testing complete - average response time: 45ms"
        directive = f'FINISH PROMPT="{message}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, FinishDirective)
        assert result.prompt.value == message
    
    # ========== MULTIPLE DIRECTIVES PARSING ==========
    
    def test_parse_multiple_testing_workflow(self):
        """Test parsing multiple directives for testing workflow."""
        directives_text = '''
        READ "src/auth/user.py"
        READ "tests/test_auth.py"
        RUN "python -m pytest tests/test_auth.py -v"
        CHANGE CONTENT="print('Debug: user authentication')"
        RUN "python scratch_pad.py"
        FINISH PROMPT="Authentication testing complete"
        '''
        
        result = self.parser.parse_multiple(directives_text)
        
        assert len(result) == 6
        assert isinstance(result[0], ReadDirective)
        assert isinstance(result[1], ReadDirective)
        assert isinstance(result[2], RunDirective)
        assert isinstance(result[3], ChangeDirective)
        assert isinstance(result[4], RunDirective)
        assert isinstance(result[5], FinishDirective)
        
        assert result[0].filename == "src/auth/user.py"
        assert result[1].filename == "tests/test_auth.py"
        assert "pytest" in result[2].command
        assert "Debug:" in result[3].content
        assert "scratch_pad.py" in result[4].command
        assert "Authentication testing" in result[5].prompt.value
    
    def test_parse_multiple_code_quality_analysis(self):
        """Test parsing multiple directives for code quality analysis."""
        directives_text = '''
        READ "src/utils/validator.py"
        RUN "flake8 src/utils/validator.py"
        RUN "mypy src/utils/validator.py"
        RUN "python -m pytest tests/test_validator.py --cov=src.utils.validator"
        FINISH PROMPT="Code quality analysis complete - 2 style issues, no type errors"
        '''
        
        result = self.parser.parse_multiple(directives_text)
        
        assert len(result) == 5
        assert isinstance(result[0], ReadDirective)
        assert all(isinstance(result[i], RunDirective) for i in range(1, 4))
        assert isinstance(result[4], FinishDirective)
    
    def test_parse_multiple_with_empty_lines(self):
        """Test parsing multiple directives with empty lines."""
        directives_text = '''
        
        READ "file1.py"
        
        
        RUN "pytest"
        
        FINISH PROMPT="done"
        
        '''
        
        result = self.parser.parse_multiple(directives_text)
        
        assert len(result) == 3
        assert isinstance(result[0], ReadDirective)
        assert isinstance(result[1], RunDirective)
        assert isinstance(result[2], FinishDirective)
    
    def test_parse_multiple_with_comments(self):
        """Test parsing multiple directives with comments."""
        directives_text = '''
        // Read source file to understand implementation
        READ "src/calculator.py"
        // Run tests to see current status
        RUN "python -m pytest tests/test_calculator.py"
        // Create debugging script
        CHANGE CONTENT="print('Testing calculator functions')"
        // Report results
        FINISH PROMPT="Calculator testing complete"
        '''
        
        result = self.parser.parse_multiple(directives_text)
        
        assert len(result) == 4
        assert all(isinstance(result[i], (ReadDirective, RunDirective, ChangeDirective, FinishDirective)) for i in range(4))
    
    # ========== ERROR HANDLING TESTS ==========
    
    def test_parse_invalid_directive(self):
        """Test parsing an invalid directive."""
        directive = 'INVALID "this should fail"'
        
        with pytest.raises(Exception) as exc_info:
            self.parser.parse(directive)
        
        assert "Failed to parse tester directive" in str(exc_info.value)
    
    def test_parse_malformed_read(self):
        """Test parsing malformed READ directive."""
        directive = 'READ'  # Missing filename
        
        with pytest.raises(Exception):
            self.parser.parse(directive)
    
    def test_parse_malformed_run(self):
        """Test parsing malformed RUN directive."""
        directive = 'RUN'  # Missing command
        
        with pytest.raises(Exception):
            self.parser.parse(directive)
    
    def test_parse_malformed_change(self):
        """Test parsing malformed CHANGE directive."""
        directive = 'CHANGE'  # Missing CONTENT
        
        with pytest.raises(Exception):
            self.parser.parse(directive)
    
    def test_parse_malformed_change_no_equals(self):
        """Test parsing malformed CHANGE directive without equals."""
        directive = 'CHANGE CONTENT "code"'  # Missing =
        
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
    
    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only input."""
        with pytest.raises(Exception):
            self.parser.parse("   \n\t  ")
    
    def test_parse_multiple_with_invalid_directive(self):
        """Test parsing multiple directives with one invalid."""
        directives_text = '''
        READ "valid.py"
        INVALID "this should fail"
        RUN "echo test"
        '''
        
        with pytest.raises(Exception) as exc_info:
            self.parser.parse_multiple(directives_text)
        
        assert "Failed to parse tester directives" in str(exc_info.value)
    
    def test_parse_unclosed_quotes(self):
        """Test parsing directive with unclosed quotes."""
        directive = 'READ "unclosed_quote.py'
        
        with pytest.raises(Exception):
            self.parser.parse(directive)


class TestTesterLanguageTransformer:
    """Test suite for the TesterLanguageTransformer class."""
    
    def setup_method(self):
        self.transformer = TesterLanguageTransformer()
    
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
        result = self.transformer._unescape_string('debug \\"info\\" \\n with \\t formatting')
        assert result == 'debug "info" \n with \t formatting'
    
    def test_unescape_string_debug_code(self):
        """Test unescaping strings with debug code patterns."""
        result = self.transformer._unescape_string('print("Debug message")')
        expected = 'print("Debug message")'
        assert result == expected
    
    def test_escape_string_basic(self):
        """Test basic string escaping."""
        result = self.transformer.escape_string("hello world")
        assert result == "hello world"
    
    def test_escape_string_with_quotes(self):
        """Test escaping strings with quotes."""
        result = self.transformer.escape_string('say "hello"')
        assert result == 'say \\"hello\\"'
    
    def test_escape_string_with_newlines(self):
        """Test escaping strings with newlines."""
        result = self.transformer.escape_string("line1\nline2")
        assert result == "line1\\nline2"
    
    def test_escape_string_debug_code(self):
        """Test escaping debug code with multiple special characters."""
        debug_code = 'print("Debug info")\nif True:\n\tpass'
        result = self.transformer.escape_string(debug_code)
        assert '\\"Debug info\\"' in result
        assert '\\n' in result
        assert '\\t' in result
    
    def test_string_transformation(self):
        """Test string token transformation."""
        # Simulate a string token with quotes
        class MockToken:
            def __str__(self):
                return '"hello world"'
        
        result = self.transformer.string(MockToken())
        assert result == "hello world"
    
    def test_string_transformation_with_escapes(self):
        """Test string token transformation with escape sequences."""
        class MockToken:
            def __str__(self):
                return '"test\\nwith\\tescapes"'
        
        result = self.transformer.string(MockToken())
        assert result == "test\nwith\tescapes"
    
    def test_prompt_field_transformation(self):
        """Test prompt field transformation."""
        result = self.transformer.prompt_field("Testing analysis complete")
        assert isinstance(result, PromptField)
        assert result.value == "Testing analysis complete"
    
    def test_filename_transformation(self):
        """Test filename transformation."""
        result = self.transformer.filename("tests/test_module.py")
        assert result == "tests/test_module.py"
    
    def test_command_transformation(self):
        """Test command transformation."""
        result = self.transformer.command("python -m pytest --cov=src")
        assert result == "python -m pytest --cov=src"
    
    def test_content_string_transformation(self):
        """Test content string transformation."""
        content = "import sys\nprint('debug')"
        result = self.transformer.content_string(content)
        assert result == content


class TestConvenienceFunctions:
    """Test suite for convenience parsing functions."""
    
    def test_parse_directive_function_read(self):
        """Test the parse_directive convenience function with READ."""
        directive = 'READ "test.py"'
        result = parse_directive(directive)
        
        assert isinstance(result, ReadDirective)
        assert result.filename == "test.py"
    
    def test_parse_directive_function_run(self):
        """Test the parse_directive convenience function with RUN."""
        directive = 'RUN "pytest tests/"'
        result = parse_directive(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == "pytest tests/"
    
    def test_parse_directive_function_change(self):
        """Test the parse_directive convenience function with CHANGE."""
        directive = 'CHANGE CONTENT="debug_code"'
        result = parse_directive(directive)
        
        assert isinstance(result, ChangeDirective)
        assert result.content == "debug_code"
    
    def test_parse_directive_function_finish(self):
        """Test the parse_directive convenience function with FINISH."""
        directive = 'FINISH PROMPT="Analysis complete"'
        result = parse_directive(directive)
        
        assert isinstance(result, FinishDirective)
        assert result.prompt.value == "Analysis complete"
    
    def test_parse_directives_function(self):
        """Test the parse_directives convenience function."""
        directives_text = '''
        READ "src/module.py"
        RUN "pytest tests/"
        CHANGE CONTENT="print('debug')"
        FINISH PROMPT="Testing done"
        '''
        
        result = parse_directives(directives_text)
        
        assert len(result) == 4
        assert isinstance(result[0], ReadDirective)
        assert isinstance(result[1], RunDirective)
        assert isinstance(result[2], ChangeDirective)
        assert isinstance(result[3], FinishDirective)
    
    def test_parse_directive_function_error(self):
        """Test error handling in parse_directive function."""
        with pytest.raises(Exception):
            parse_directive('INVALID "directive"')
    
    def test_parse_directives_function_error(self):
        """Test error handling in parse_directives function."""
        with pytest.raises(Exception):
            parse_directives('INVALID "directive"')
    
    def test_parse_directives_function_empty_input(self):
        """Test parse_directives function with empty input."""
        result = parse_directives("")
        assert len(result) == 0
    
    def test_parse_directives_function_comments_only(self):
        """Test parse_directives function with only comments."""
        directives_text = '''
        // This is a comment
        // Another comment
        '''
        result = parse_directives(directives_text)
        assert len(result) == 0


class TestSpecialCases:
    """Test suite for special parsing cases."""
    
    def setup_method(self):
        self.parser = TesterLanguageParser()
    
    def test_parse_directive_with_extra_whitespace(self):
        """Test parsing directive with extra whitespace."""
        directive = '   READ    "test.py"   '
        result = self.parser.parse(directive)
        
        assert isinstance(result, ReadDirective)
        assert result.filename == "test.py"
    
    def test_parse_directive_case_sensitivity(self):
        """Test that directive parsing is case sensitive."""
        directive = 'read "test.py"'  # lowercase
        
        with pytest.raises(Exception):
            self.parser.parse(directive)
    
    def test_parse_change_with_code_containing_quotes(self):
        """Test parsing CHANGE directive with code containing quotes."""
        content = 'print(\\"Hello, World!\\")\\nprint(\'Another message\')'
        directive = f'CHANGE CONTENT="{content}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, ChangeDirective)
        assert 'Hello, World!' in result.content
        assert 'Another message' in result.content
    
    def test_parse_run_with_complex_pytest_args(self):
        """Test parsing RUN directive with complex pytest arguments."""
        command = "python -m pytest tests/ -x -v --tb=short --cov=src --cov-report=html:coverage_html"
        directive = f'RUN "{command}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, RunDirective)
        assert result.command == command
    
    def test_parse_finish_with_multiline_message(self):
        """Test parsing FINISH directive with multiline message."""
        message = "Testing complete:\\n- 15 tests passed\\n- 2 tests failed\\n- Coverage: 85%"
        directive = f'FINISH PROMPT="{message}"'
        result = self.parser.parse(directive)
        
        assert isinstance(result, FinishDirective)
        assert "Testing complete:" in result.prompt.value
        assert "15 tests passed" in result.prompt.value 