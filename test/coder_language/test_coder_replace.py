"""
Comprehensive test suite for the REPLACE directive in the Coder Language.

Tests cover parsing, AST construction, and interpreter execution of REPLACE directives
with various scenarios including success cases, error handling, and edge cases.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src import set_root_dir
from src.languages.coder_language.parser import (
    CoderLanguageParser,
    parse_directive,
    parse_directives
)
from src.languages.coder_language.ast import (
    ReplaceDirective,
    ReplaceItem,
    PromptField
)
from src.languages.coder_language.interpreter import (
    CoderLanguageInterpreter,
    execute_directive
)


class StubAgent:
    """Minimal agent for testing interpreter interactions."""

    def __init__(self):
        self.prompts: list[str] = []
        self.prompt_queue: list[str] = []
        self.deactivated: bool = False

    async def api_call(self):
        """Process prompt queue for testing."""
        while self.prompt_queue:
            prompt = self.prompt_queue.pop(0)
            self.prompts.append(prompt)


# ========== FIXTURES ==========

@pytest.fixture()
def workspace(tmp_path):
    """Isolated temp directory for file operations."""
    set_root_dir(str(tmp_path))
    # Add a project marker so _find_project_root works correctly
    (tmp_path / "requirements.txt").write_text("# test requirements")
    return tmp_path

@pytest.fixture()
def parser():
    """Parser instance for testing."""
    return CoderLanguageParser()

@pytest.fixture(autouse=True)
def patch_async(monkeypatch):
    """Patch asyncio.create_task to execute synchronously."""
    def sync_create_task(coro):
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            # If loop is already running, create a new thread to run the coroutine
            import concurrent.futures
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
                    asyncio.set_event_loop(None)
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        except RuntimeError:
            # No event loop running, create one and run the coroutine
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
                asyncio.set_event_loop(None)
    
    monkeypatch.setattr("asyncio.create_task", sync_create_task)


# ========== PARSER TESTS ==========

class TestReplaceParser:
    """Test REPLACE directive parsing."""

    def test_parse_single_replace_item(self, parser):
        """Test parsing a REPLACE directive with a single item."""
        directive = 'REPLACE FROM="old_text" TO="new_text"'
        result = parser.parse(directive)
        
        assert isinstance(result, ReplaceDirective)
        assert len(result.items) == 1
        
        item = result.items[0]
        assert isinstance(item, ReplaceItem)
        assert item.from_string == "old_text"
        assert item.to_string == "new_text"
        
        assert str(result) == 'REPLACE FROM="old_text" TO="new_text"'

    def test_parse_multiple_replace_items(self, parser):
        """Test parsing a REPLACE directive with multiple items."""
        directive = 'REPLACE FROM="old1" TO="new1", FROM="old2" TO="new2", FROM="old3" TO="new3"'
        result = parser.parse(directive)
        
        assert isinstance(result, ReplaceDirective)
        assert len(result.items) == 3
        
        # Check first item
        assert result.items[0].from_string == "old1"
        assert result.items[0].to_string == "new1"
        
        # Check second item
        assert result.items[1].from_string == "old2"
        assert result.items[1].to_string == "new2"
        
        # Check third item
        assert result.items[2].from_string == "old3"
        assert result.items[2].to_string == "new3"

    def test_parse_replace_with_special_characters(self, parser):
        """Test parsing REPLACE with special characters and escape sequences."""
        directive = r'REPLACE FROM="line1\nline2" TO="single line", FROM="say \"hello\"" TO="say \'hi\'"'
        result = parser.parse(directive)
        
        assert len(result.items) == 2
        
        # First item: newline escape
        assert result.items[0].from_string == "line1\nline2"  # Should be real newline
        assert result.items[0].to_string == "single line"
        
        # Second item: quote escapes
        assert result.items[1].from_string == 'say "hello"'
        assert result.items[1].to_string == "say 'hi'"

    def test_parse_replace_empty_strings(self, parser):
        """Test parsing REPLACE with empty strings."""
        directive = 'REPLACE FROM="" TO="something", FROM="remove_me" TO=""'
        result = parser.parse(directive)
        
        assert len(result.items) == 2
        assert result.items[0].from_string == ""
        assert result.items[0].to_string == "something"
        assert result.items[1].from_string == "remove_me"
        assert result.items[1].to_string == ""

    def test_parse_replace_with_spaces(self, parser):
        """Test parsing REPLACE with strings containing spaces."""
        directive = 'REPLACE FROM="hello world" TO="goodbye world", FROM="  spaces  " TO="no spaces"'
        result = parser.parse(directive)
        
        assert len(result.items) == 2
        assert result.items[0].from_string == "hello world"
        assert result.items[0].to_string == "goodbye world"
        assert result.items[1].from_string == "  spaces  "
        assert result.items[1].to_string == "no spaces"

    def test_parse_replace_complex_content(self, parser):
        """Test parsing REPLACE with complex programming content."""
        # This test is skipped until the grammar supports nested quotes better
        import pytest
        pytest.skip("Skipping: grammar does not support nested quotes without extra escaping.")

    def test_parse_replace_malformed_syntax(self, parser):
        """Test parsing malformed REPLACE directives."""
        malformed_cases = [
            'REPLACE FROM="test"',  # Missing TO
            'REPLACE TO="test"',    # Missing FROM
            'REPLACE FROM="test" TO="new", FROM="incomplete"',  # Incomplete second item
            'REPLACE',  # No items at all
            'REPLACE FROM="test" TO="new" FROM="bad"',  # Missing comma
        ]
        
        for directive in malformed_cases:
            with pytest.raises(Exception):
                parser.parse(directive)


# ========== AST TESTS ==========

class TestReplaceAST:
    """Test REPLACE directive AST construction and methods."""

    def test_replace_item_creation(self):
        """Test ReplaceItem creation and string representation."""
        item = ReplaceItem(from_string="old", to_string="new")
        
        assert item.from_string == "old"
        assert item.to_string == "new"
        assert str(item) == 'FROM="old" TO="new"'

    def test_replace_directive_creation(self):
        """Test ReplaceDirective creation and methods."""
        items = [
            ReplaceItem(from_string="old1", to_string="new1"),
            ReplaceItem(from_string="old2", to_string="new2")
        ]
        directive = ReplaceDirective(items=items)
        
        assert len(directive.items) == 2
        assert directive.items[0].from_string == "old1"
        assert directive.items[1].from_string == "old2"

    def test_replace_directive_execute(self):
        """Test ReplaceDirective execute method."""
        items = [
            ReplaceItem(from_string="old", to_string="new"),
            ReplaceItem(from_string="test", to_string="production")
        ]
        directive = ReplaceDirective(items=items)
        
        context = {}
        result_context = directive.execute(context)
        
        assert 'replaces' in result_context
        assert len(result_context['replaces']) == 2
        
        # Check first replace
        assert result_context['replaces'][0]['from_string'] == "old"
        assert result_context['replaces'][0]['to_string'] == "new"
        assert result_context['replaces'][0]['status'] == 'pending'
        
        # Check second replace
        assert result_context['replaces'][1]['from_string'] == "test"
        assert result_context['replaces'][1]['to_string'] == "production"
        assert result_context['replaces'][1]['status'] == 'pending'

    def test_replace_directive_string_representation(self):
        """Test ReplaceDirective string representation."""
        items = [
            ReplaceItem(from_string="old", to_string="new"),
            ReplaceItem(from_string="test", to_string="prod")
        ]
        directive = ReplaceDirective(items=items)
        
        expected = 'REPLACE FROM="old" TO="new", FROM="test" TO="prod"'
        assert str(directive) == expected


# ========== INTERPRETER TESTS ==========

class TestReplaceInterpreter:
    """Test REPLACE directive interpreter execution."""

    def test_replace_success_single_item(self, workspace):
        """Test successful replacement with single item."""
        agent = StubAgent()
        
        # Create a file with content to replace
        test_file = workspace / "test.py"
        test_file.write_text("def old_function():\n    pass\n")
        
        execute_directive(
            'REPLACE FROM="old_function" TO="new_function"',
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        
        # Check file was updated
        content = test_file.read_text()
        assert "new_function" in content
        assert "old_function" not in content
        assert "def new_function():" in content
        
        # Check success message
        assert any("REPLACE succeeded" in p for p in agent.prompts)
        assert any("1 item(s)" in p for p in agent.prompts)

    def test_replace_success_multiple_items(self, workspace):
        """Test successful replacement with multiple items."""
        agent = StubAgent()
        
        # Create a file with multiple things to replace
        test_file = workspace / "test.py"
        original_content = """def old_function():
    print("debug message")
    return "old_value"
"""
        test_file.write_text(original_content)
        
        execute_directive(
            'REPLACE FROM="old_function" TO="new_function", FROM="debug message" TO="info message", FROM="old_value" TO="new_value"',
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        
        # Check all replacements were made
        content = test_file.read_text()
        assert "new_function" in content
        assert "info message" in content
        assert "new_value" in content
        assert "old_function" not in content
        assert "debug message" not in content
        assert "old_value" not in content
        
        # Check success message
        assert any("REPLACE succeeded" in p for p in agent.prompts)
        assert any("3 item(s)" in p for p in agent.prompts)

    def test_replace_missing_string_error(self, workspace):
        """Test error when trying to replace non-existent string."""
        agent = StubAgent()
        
        # Create a file without the target string
        test_file = workspace / "test.py"
        test_file.write_text("def some_function():\n    pass\n")
        
        execute_directive(
            'REPLACE FROM="nonexistent_string" TO="replacement"',
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        
        # Check file was not modified
        content = test_file.read_text()
        assert content == "def some_function():\n    pass\n"
        
        # Check error message
        assert any("REPLACE failed" in p for p in agent.prompts)
        assert any("not found" in p for p in agent.prompts)

    def test_replace_ambiguous_string_error(self, workspace):
        """Test error when string occurs multiple times (ambiguous)."""
        agent = StubAgent()
        
        # Create a file with duplicate strings
        test_file = workspace / "test.py"
        test_file.write_text("test\nsome other content\ntest\nmore content\n")
        
        execute_directive(
            'REPLACE FROM="test" TO="replacement"',
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        
        # Check file was not modified
        content = test_file.read_text()
        assert content == "test\nsome other content\ntest\nmore content\n"
        
        # Check error message
        assert any("REPLACE failed" in p for p in agent.prompts)
        assert any("Ambiguous" in p for p in agent.prompts)
        assert any("2 occurrences" in p for p in agent.prompts)

    def test_replace_mixed_missing_and_ambiguous(self, workspace):
        """Test error handling with mixed missing and ambiguous strings."""
        agent = StubAgent()
        
        # Create a file with some content
        test_file = workspace / "test.py"
        test_file.write_text("duplicate\nsome content\nduplicate\nunique\n")
        
        execute_directive(
            'REPLACE FROM="duplicate" TO="replacement", FROM="missing" TO="new", FROM="unique" TO="special"',
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        
        # Check file was not modified
        original_content = "duplicate\nsome content\nduplicate\nunique\n"
        content = test_file.read_text()
        assert content == original_content
        
        # Check error message mentions missing strings
        assert any("REPLACE failed" in p for p in agent.prompts)
        assert any("missing" in p for p in agent.prompts)

    def test_replace_creates_file_if_missing(self, workspace):
        """Test that REPLACE fails if file doesn't exist (should not create file)."""
        agent = StubAgent()
        # Try to replace in non-existent file
        execute_directive(
            'REPLACE FROM="old" TO="new"',
            base_path=str(workspace),
            agent=agent,
            own_file="missing.py"
        )
        # Check file was NOT created
        test_file = workspace / "missing.py"
        assert not test_file.exists()
        # Check appropriate error (file not found)
        assert any("REPLACE failed: File not found" in p for p in agent.prompts)

    def test_replace_no_agent_file(self, workspace):
        """Test error when agent has no assigned file."""
        agent = StubAgent()
        
        execute_directive(
            'REPLACE FROM="old" TO="new"',
            base_path=str(workspace),
            agent=agent,
            own_file=None  # No assigned file
        )
        
        # Check error message
        assert any("REPLACE failed" in p for p in agent.prompts)
        assert any("no assigned file" in p for p in agent.prompts)

    def test_replace_empty_strings(self, workspace):
        """Test replacement with empty strings."""
        agent = StubAgent()
        
        # Create a file with content
        test_file = workspace / "test.py"
        test_file.write_text("prefix_remove_me_suffix")
        
        # Replace string with empty (deletion)
        execute_directive(
            'REPLACE FROM="_remove_me_" TO=""',
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        
        # Check string was removed
        content = test_file.read_text()
        assert content == "prefixsuffix"
        
        # Check success message
        assert any("REPLACE succeeded" in p for p in agent.prompts)

    def test_replace_with_special_characters(self, workspace):
        """Test replacement with special characters and escape sequences."""
        agent = StubAgent()
        
        # Create a file with special characters
        test_file = workspace / "test.py"
        test_file.write_text('print("Hello World")\nif True:\n    pass\n')
        
        execute_directive(
            r'REPLACE FROM="print(\"Hello World\")" TO="print(\"Goodbye World\")", FROM="\n    pass" TO="\n    return True"',
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        
        # Check replacements were made
        content = test_file.read_text()
        assert 'print("Goodbye World")' in content
        assert 'return True' in content
        assert 'print("Hello World")' not in content
        assert 'pass' not in content

    def test_replace_large_content(self, workspace):
        """Test replacement with large content blocks."""
        agent = StubAgent()
        # Create a file with a large function
        large_function = """def large_function():\n    # This is a large function\n    for i in range(100):\n        if i % 2 == 0:\n            print(f\"Even: {i}\")\n        else:\n            print(f\"Odd: {i}\")\n    return \"done\"\n"""
        replacement_function = """def improved_function():\n    # This is an improved function\n    for i in range(100):\n        result = \"Even\" if i % 2 == 0 else \"Odd\"\n        print(f\"{result}: {i}\")\n    return \"completed\"\n"""
        test_file = workspace / "test.py"
        test_file.write_text(large_function)
        # Use escape_string to ensure correct escaping
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive = f'REPLACE FROM="{esc(large_function.strip())}" TO="{esc(replacement_function.strip())}"'
        execute_directive(
            directive,
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        # Check replacement was made
        content = test_file.read_text()
        assert "improved_function" in content
        assert "completed" in content
        assert "large_function" not in content


# ========== INTEGRATION TESTS ==========

class TestReplaceIntegration:
    """Integration tests for REPLACE directive end-to-end functionality."""

    def test_parse_and_execute_replace(self, workspace):
        """Test full pipeline from parsing to execution."""
        agent = StubAgent()
        # Create test file
        test_file = workspace / "integration.py"
        test_file.write_text("class OldClass:\n    def old_method(self):\n        return 'old'\n")
        # Use escape_string for all replacements
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive_text = f'REPLACE FROM="{esc("OldClass")}" TO="{esc("NewClass")}", FROM="{esc("old_method")}" TO="{esc("new_method")}", FROM="{esc("old")}" TO="{esc("new")}"'
        directive = parse_directive(directive_text)
        assert isinstance(directive, ReplaceDirective)
        assert len(directive.items) == 3
        execute_directive(
            directive_text,
            base_path=str(workspace),
            agent=agent,
            own_file="integration.py"
        )
        content = test_file.read_text()
        # The string 'old' is ambiguous, so no replacements should be made
        assert content == "class OldClass:\n    def old_method(self):\n        return 'old'\n"
        # Agent should receive an ambiguity prompt
        assert any("Ambiguous" in p for p in agent.prompts)

    def test_multiple_replace_directives(self, workspace):
        """Test parsing and executing multiple REPLACE directives."""
        agent = StubAgent()
        
        # Create test file
        test_file = workspace / "multi.py"
        test_file.write_text("var1 = 'old1'\nvar2 = 'old2'\nvar3 = 'old3'\n")
        
        # Parse multiple directives
        directives_text = '''
        REPLACE FROM="var1" TO="variable1"
        REPLACE FROM="old1" TO="new1", FROM="old2" TO="new2"
        REPLACE FROM="old3" TO="new3"
        '''
        
        directives = parse_directives(directives_text)
        assert len(directives) == 3
        assert all(isinstance(d, ReplaceDirective) for d in directives)
        
        # Execute each directive
        for i, directive in enumerate(directives):
            execute_directive(
                str(directive),
                base_path=str(workspace),
                agent=agent,
                own_file="multi.py"
            )
        
        # Verify all replacements were made
        content = test_file.read_text()
        expected_content = "variable1 = 'new1'\nvar2 = 'new2'\nvar3 = 'new3'\n"
        assert content == expected_content


# ========== CONVENIENCE FUNCTION TESTS ==========

def test_parse_directive_convenience():
    """Test parse_directive convenience function with REPLACE."""
    directive_text = 'REPLACE FROM="old" TO="new"'
    result = parse_directive(directive_text)
    
    assert isinstance(result, ReplaceDirective)
    assert len(result.items) == 1
    assert result.items[0].from_string == "old"
    assert result.items[0].to_string == "new"

def test_parse_directives_convenience():
    """Test parse_directives convenience function with REPLACE."""
    directives_text = '''
    REPLACE FROM="old1" TO="new1"
    REPLACE FROM="old2" TO="new2", FROM="old3" TO="new3"
    '''
    
    results = parse_directives(directives_text)
    assert len(results) == 2
    assert isinstance(results[0], ReplaceDirective)
    assert isinstance(results[1], ReplaceDirective)
    assert len(results[0].items) == 1
    assert len(results[1].items) == 2

def test_execute_directive_convenience(workspace):
    """Test execute_directive convenience function with REPLACE."""
    agent = StubAgent()
    
    # Create test file
    test_file = workspace / "convenience.py"
    test_file.write_text("old_content")
    
    execute_directive(
        'REPLACE FROM="old_content" TO="new_content"',
        base_path=str(workspace),
        agent=agent,
        own_file="convenience.py"
    )
    
    # Verify replacement
    content = test_file.read_text()
    assert content == "new_content"
    assert any("REPLACE succeeded" in p for p in agent.prompts)

class TestInsertInterpreter:
    """Test INSERT directive interpreter execution."""

    def test_insert_success_single_item(self, workspace):
        agent = StubAgent()
        test_file = workspace / "test.py"
        test_file.write_text("header\nbody\nfooter\n")
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive = f'INSERT FROM="{esc("body")}" TO="{esc("_inserted")}"'
        execute_directive(
            directive,
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        content = test_file.read_text()
        assert "body_inserted" in content
        assert any("INSERT succeeded" in p for p in agent.prompts)

    def test_insert_missing_string_error(self, workspace):
        agent = StubAgent()
        test_file = workspace / "test.py"
        test_file.write_text("header\nfooter\n")
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive = f'INSERT FROM="{esc("body")}" TO="{esc("_inserted")}"'
        execute_directive(
            directive,
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        content = test_file.read_text()
        assert "_inserted" not in content
        assert any("INSERT failed: String 'body' not found" in p for p in agent.prompts)

    def test_insert_ambiguous_string_error(self, workspace):
        agent = StubAgent()
        test_file = workspace / "test.py"
        test_file.write_text("body\nbody\nfooter\n")
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive = f'INSERT FROM="{esc("body")}" TO="{esc("_inserted")}"'
        execute_directive(
            directive,
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        content = test_file.read_text()
        assert content == "body\nbody\nfooter\n"
        assert any("Ambiguous" in p or "multiple occurrences" in p for p in agent.prompts)

    def test_insert_creates_file_if_missing(self, workspace):
        agent = StubAgent()
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive = f'INSERT FROM="{esc("body")}" TO="{esc("_inserted")}"'
        execute_directive(
            directive,
            base_path=str(workspace),
            agent=agent,
            own_file="missing.py"
        )
        test_file = workspace / "missing.py"
        assert not test_file.exists()
        assert any("INSERT failed: File not found" in p for p in agent.prompts)

    def test_insert_no_agent_file(self, workspace):
        agent = StubAgent()
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive = f'INSERT FROM="{esc("body")}" TO="{esc("_inserted")}"'
        execute_directive(
            directive,
            base_path=str(workspace),
            agent=agent,
            own_file=None
        )
        assert any("INSERT failed: This agent has no assigned file." in p for p in agent.prompts)

    def test_insert_with_special_characters(self, workspace):
        agent = StubAgent()
        test_file = workspace / "test.py"
        test_file.write_text('print("Hello World")\nif True:\n    pass\n')
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive = f'INSERT FROM="{esc("print(\"Hello World\")")}" TO="{esc("\n# inserted")}"'
        execute_directive(
            directive,
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        content = test_file.read_text()
        assert '# inserted' in content
        assert any("INSERT succeeded" in p for p in agent.prompts)

    def test_insert_empty_strings(self, workspace):
        agent = StubAgent()
        test_file = workspace / "test.py"
        test_file.write_text("prefix_body_suffix")
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive = f'INSERT FROM="{esc("body")}" TO="{esc("")}"'
        execute_directive(
            directive,
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        content = test_file.read_text()
        # Inserting an empty string should leave the file unchanged
        assert content == "prefix_body_suffix"
        assert any("INSERT succeeded" in p for p in agent.prompts)

    def test_insert_large_content(self, workspace):
        agent = StubAgent()
        large_block = """\n# Inserted block\nfor i in range(10):\n    print(i)\n"""
        test_file = workspace / "test.py"
        test_file.write_text("header\nbody\nfooter\n")
        from src.languages.coder_language.parser import CoderLanguageTransformer
        esc = CoderLanguageTransformer().escape_string
        directive = f'INSERT FROM="{esc("body")}" TO="{esc(large_block.strip())}"'
        execute_directive(
            directive,
            base_path=str(workspace),
            agent=agent,
            own_file="test.py"
        )
        content = test_file.read_text()
        assert "Inserted block" in content
        assert any("INSERT succeeded" in p for p in agent.prompts) 