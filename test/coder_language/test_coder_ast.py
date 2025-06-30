"""
Comprehensive test suite for the Coder Language AST classes.

Tests cover all AST classes and methods in ast.py using partitioning methods to ensure
complete coverage of abstract syntax tree functionality for autonomous agent file operations.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.languages.coder_language.ast import (
    # Basic data classes
    Target,
    PromptField,
    
    # Directive classes
    Directive,
    ReadDirective,
    RunDirective,
    ChangeDirective,
    FinishDirective,
    DirectiveType,
    
    # AST Node classes
    NodeType,
    ASTNode,
    ASTVisitor,
    ActionNode,
    TargetNode,
    PromptFieldNode,
    ParamSetNode,
    DirectiveNode,
    
    # Grammar imports
    TokenType
)


class TestTarget:
    """Test suite for Target data class."""
    
    def test_target_creation(self):
        """Test creating a target."""
        target = Target(name="test.py")
        
        assert target.name == "test.py"
        assert str(target) == "file:test.py"
    
    def test_target_with_path(self):
        """Test creating target with path."""
        target = Target(name="src/components/Button.js")
        
        assert target.name == "src/components/Button.js"
        assert str(target) == "file:src/components/Button.js"
    
    def test_target_with_complex_filename(self):
        """Test creating target with complex filename."""
        target = Target(name="my-file_v2.test.js")
        
        assert target.name == "my-file_v2.test.js"
        assert str(target) == "file:my-file_v2.test.js"


class TestPromptField:
    """Test suite for PromptField data class."""
    
    def test_prompt_field_creation(self):
        """Test creating a prompt field."""
        prompt = PromptField(value="Task completed successfully")
        
        assert prompt.value == "Task completed successfully"
        assert str(prompt) == 'PROMPT="Task completed successfully"'
    
    def test_prompt_field_with_special_chars(self):
        """Test prompt field with special characters."""
        prompt = PromptField(value='Task with "quotes" and \n newlines')
        
        assert prompt.value == 'Task with "quotes" and \n newlines'
        assert str(prompt) == 'PROMPT="Task with "quotes" and \n newlines"'
    
    def test_prompt_field_empty(self):
        """Test empty prompt field."""
        prompt = PromptField(value="")
        
        assert prompt.value == ""
        assert str(prompt) == 'PROMPT=""'
    
    def test_prompt_field_complex_message(self):
        """Test prompt field with complex completion message."""
        complex_prompt = """Implementation completed successfully!

Features implemented:
1. File reading and parsing
2. Data validation and processing
3. Error handling and logging
4. Unit tests with 100% coverage

All requirements met and tests passing."""
        
        prompt = PromptField(value=complex_prompt)
        
        assert prompt.value == complex_prompt
        assert "Implementation completed" in prompt.value
        assert "100% coverage" in prompt.value


class TestReadDirective:
    """Test suite for ReadDirective class."""
    
    def test_read_directive_creation(self):
        """Test creating a READ directive."""
        directive = ReadDirective(filename="test.py")
        
        assert directive.filename == "test.py"
        assert str(directive) == 'READ "test.py"'
    
    def test_read_directive_execution(self):
        """Test READ directive execution."""
        directive = ReadDirective(filename="config.json")
        
        context = {}
        result = directive.execute(context)
        
        assert 'reads' in result
        assert len(result['reads']) == 1
        assert result['reads'][0]['filename'] == "config.json"
        assert result['reads'][0]['status'] == "pending"
    
    def test_read_directive_with_path(self):
        """Test READ directive with file path."""
        directive = ReadDirective(filename="src/utils/helper.py")
        
        assert directive.filename == "src/utils/helper.py"
        assert str(directive) == 'READ "src/utils/helper.py"'
    
    def test_read_directive_context_preservation(self):
        """Test that READ directive preserves existing context."""
        directive = ReadDirective(filename="new_file.py")
        
        context = {'existing_key': 'existing_value', 'reads': [{'filename': 'old.py'}]}
        result = directive.execute(context)
        
        assert result['existing_key'] == 'existing_value'
        assert len(result['reads']) == 2
        assert result['reads'][0]['filename'] == 'old.py'
        assert result['reads'][1]['filename'] == 'new_file.py'


class TestRunDirective:
    """Test suite for RunDirective class."""
    
    def test_run_directive_creation(self):
        """Test creating a RUN directive."""
        directive = RunDirective(command="python -m pytest")
        
        assert directive.command == "python -m pytest"
        assert str(directive) == 'RUN "python -m pytest"'
    
    def test_run_directive_execution(self):
        """Test RUN directive execution."""
        directive = RunDirective(command="echo hello")
        
        context = {}
        result = directive.execute(context)
        
        assert 'commands' in result
        assert len(result['commands']) == 1
        assert result['commands'][0]['command'] == "echo hello"
        assert result['commands'][0]['status'] == "pending"
    
    def test_run_directive_complex_command(self):
        """Test RUN directive with complex command."""
        complex_command = "python -c \"import sys; print('hello'); sys.exit(0)\""
        directive = RunDirective(command=complex_command)
        
        assert directive.command == complex_command
        assert "python -c" in str(directive)
    
    def test_run_directive_context_preservation(self):
        """Test that RUN directive preserves existing context."""
        directive = RunDirective(command="new command")
        
        context = {'existing_key': 'existing_value', 'commands': [{'command': 'old command'}]}
        result = directive.execute(context)
        
        assert result['existing_key'] == 'existing_value'
        assert len(result['commands']) == 2
        assert result['commands'][0]['command'] == 'old command'
        assert result['commands'][1]['command'] == 'new command'


class TestChangeDirective:
    """Test suite for ChangeDirective class."""
    
    def test_change_directive_creation(self):
        """Test creating a CHANGE directive."""
        content = "def hello(): print('Hello, World!')"
        directive = ChangeDirective(content=content)
        
        assert directive.content == content
        assert str(directive).startswith('CHANGE CONTENT="def hello(): print')
    
    def test_change_directive_execution(self):
        """Test CHANGE directive execution."""
        directive = ChangeDirective(content="print('app')")
        
        context = {}
        result = directive.execute(context)
        
        assert 'changes' in result
        assert len(result['changes']) == 1
        assert result['changes'][0]['content'] == "print('app')"
        assert result['changes'][0]['status'] == "pending"
    
    def test_change_directive_multiline_content(self):
        """Test CHANGE directive with multiline content."""
        content = """def process_data(data):
    if not data:
        return None
    
    processed = []
    for item in data:
        if validate_item(item):
            processed.append(transform_item(item))
    
    return processed"""
        
        directive = ChangeDirective(content=content)
        
        assert directive.content == content
        assert "def process_data" in directive.content
        assert "validate_item" in directive.content
    
    def test_change_directive_empty_content(self):
        """Test CHANGE directive with empty content."""
        directive = ChangeDirective(content="")
        
        assert directive.content == ""
        assert 'CONTENT=""' in str(directive)
    
    def test_change_directive_context_preservation(self):
        """Test that CHANGE directive preserves existing context."""
        directive = ChangeDirective(content="new content")
        
        context = {'existing_key': 'existing_value', 'changes': [{'content': 'old content'}]}
        result = directive.execute(context)
        
        assert result['existing_key'] == 'existing_value'
        assert len(result['changes']) == 2
        assert result['changes'][0]['content'] == 'old content'
        assert result['changes'][1]['content'] == 'new content'


class TestFinishDirective:
    """Test suite for FinishDirective class."""
    
    def test_finish_directive_creation(self):
        """Test creating a FINISH directive."""
        prompt = PromptField(value="Task completed successfully")
        directive = FinishDirective(prompt=prompt)
        
        assert directive.prompt == prompt
        assert directive.prompt.value == "Task completed successfully"
        assert str(directive) == 'FINISH PROMPT="Task completed successfully"'
    
    def test_finish_directive_execution(self):
        """Test FINISH directive execution."""
        prompt = PromptField(value="All done")
        directive = FinishDirective(prompt=prompt)
        
        context = {}
        result = directive.execute(context)
        
        assert result['finished'] is True
        assert result['completion_prompt'] == "All done"
    
    def test_finish_directive_complex_message(self):
        """Test FINISH directive with complex message."""
        complex_message = """Implementation phase completed successfully!

Summary of work completed:
- Implemented core functionality
- Added comprehensive error handling
- Created unit tests with 95% coverage
- Updated documentation

Ready for code review and integration testing."""
        
        prompt = PromptField(value=complex_message)
        directive = FinishDirective(prompt=prompt)
        
        assert directive.prompt.value == complex_message
        assert "Implementation phase completed" in str(directive)
    
    def test_finish_directive_context_preservation(self):
        """Test that FINISH directive preserves existing context."""
        prompt = PromptField(value="Done")
        directive = FinishDirective(prompt=prompt)
        
        context = {'existing_key': 'existing_value', 'some_data': [1, 2, 3]}
        result = directive.execute(context)
        
        assert result['existing_key'] == 'existing_value'
        assert result['some_data'] == [1, 2, 3]
        assert result['finished'] is True
        assert result['completion_prompt'] == "Done"


class TestActionNode:
    """Test suite for ActionNode class."""
    
    def test_action_node_creation(self):
        """Test creating an ActionNode."""
        node = ActionNode(action_type=TokenType.READ, value="READ", line=1, column=0)
        
        assert node.action_type == TokenType.READ
        assert node.value == "READ"
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.ACTION
    
    def test_action_node_representation(self):
        """Test ActionNode string representation."""
        node = ActionNode(action_type=TokenType.RUN, value="RUN")
        
        assert "ActionNode" in repr(node)
        assert "RUN" in repr(node)
    
    def test_action_node_visitor_acceptance(self):
        """Test ActionNode visitor acceptance."""
        class MockVisitor(ASTVisitor):
            def visit_action(self, node): 
                return f"visited_{node.value}"
            def visit_directive(self, node): pass
            def visit_target(self, node): pass
            def visit_prompt_field(self, node): pass
            def visit_param_set(self, node): pass
        
        node = ActionNode(action_type=TokenType.CHANGE, value="CHANGE")
        visitor = MockVisitor()
        result = node.accept(visitor)
        
        assert result == "visited_CHANGE"


class TestTargetNode:
    """Test suite for TargetNode class."""
    
    def test_target_node_creation(self):
        """Test creating a TargetNode."""
        node = TargetNode(target_type=TokenType.FILE, name="test.py", line=1, column=5)
        
        assert node.target_type == TokenType.FILE
        assert node.name == "test.py"
        assert node.line == 1
        assert node.column == 5
        assert node.node_type == NodeType.TARGET
    
    def test_target_node_representation(self):
        """Test TargetNode string representation."""
        node = TargetNode(target_type=TokenType.FILE, name="app.js")
        
        assert "TargetNode" in repr(node)
        assert "FILE" in repr(node)
        assert "app.js" in repr(node)
    
    def test_target_node_visitor_acceptance(self):
        """Test TargetNode visitor acceptance."""
        class MockVisitor(ASTVisitor):
            def visit_target(self, node): 
                return f"visited_{node.name}"
            def visit_action(self, node): pass
            def visit_directive(self, node): pass
            def visit_prompt_field(self, node): pass
            def visit_param_set(self, node): pass
        
        node = TargetNode(target_type=TokenType.FILE, name="test.py")
        visitor = MockVisitor()
        result = node.accept(visitor)
        
        assert result == "visited_test.py"


class TestPromptFieldNode:
    """Test suite for PromptFieldNode class."""
    
    def test_prompt_field_node_creation(self):
        """Test creating a PromptFieldNode."""
        node = PromptFieldNode(prompt="Task completed", line=1, column=10)
        
        assert node.prompt == "Task completed"
        assert node.line == 1
        assert node.column == 10
        assert node.node_type == NodeType.PROMPT_FIELD
    
    def test_prompt_field_node_representation(self):
        """Test PromptFieldNode string representation."""
        node = PromptFieldNode(prompt="Done with work")
        
        assert "PromptFieldNode" in repr(node)
        assert "Done with work" in repr(node)
    
    def test_prompt_field_node_visitor_acceptance(self):
        """Test PromptFieldNode visitor acceptance."""
        class MockVisitor(ASTVisitor):
            def visit_prompt_field(self, node): 
                return f"visited_{node.prompt}"
            def visit_action(self, node): pass
            def visit_directive(self, node): pass
            def visit_target(self, node): pass
            def visit_param_set(self, node): pass
        
        node = PromptFieldNode(prompt="All tasks completed")
        visitor = MockVisitor()
        result = node.accept(visitor)
        
        assert result == "visited_All tasks completed"


class TestParamSetNode:
    """Test suite for ParamSetNode class."""
    
    def test_param_set_node_with_target_and_prompt(self):
        """Test ParamSetNode with target and prompt field."""
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        prompt_field = PromptFieldNode(prompt="Complete the task")
        node = ParamSetNode(target=target, prompt_field=prompt_field, line=1, column=0)
        
        assert node.target == target
        assert node.prompt_field == prompt_field
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.PARAM_SET
    
    def test_param_set_node_with_content(self):
        """Test ParamSetNode with content."""
        content = "def hello(): print('Hello, World!')"
        node = ParamSetNode(content=content)
        
        assert node.content == content
        assert node.target is None
        assert node.prompt_field is None
    
    def test_get_filename_with_target(self):
        """Test get_filename when target is present."""
        target = TargetNode(target_type=TokenType.FILE, name="app.py")
        node = ParamSetNode(target=target)
        
        assert node.get_filename() == "app.py"
    
    def test_get_filename_without_target(self):
        """Test get_filename when target is not present."""
        node = ParamSetNode()
        
        assert node.get_filename() is None
    
    def test_get_prompt_with_prompt_field(self):
        """Test get_prompt when prompt field is present."""
        prompt_field = PromptFieldNode(prompt="Task completed")
        node = ParamSetNode(prompt_field=prompt_field)
        
        assert node.get_prompt() == "Task completed"
    
    def test_get_prompt_without_prompt_field(self):
        """Test get_prompt when prompt field is not present."""
        node = ParamSetNode()
        
        assert node.get_prompt() is None
    
    def test_get_content_with_content(self):
        """Test get_content when content is present."""
        content = "print('test')"
        node = ParamSetNode(content=content)
        
        assert node.get_content() == content
    
    def test_get_content_without_content(self):
        """Test get_content when content is not present."""
        node = ParamSetNode()
        
        assert node.get_content() is None
    
    def test_param_set_node_to_dict(self):
        """Test converting ParamSetNode to dictionary."""
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        prompt_field = PromptFieldNode(prompt="Task done")
        content = "print('hello')"
        node = ParamSetNode(target=target, prompt_field=prompt_field, content=content)
        
        result = node.to_dict()
        
        assert result['target']['type'] == 'FILE'
        assert result['target']['name'] == 'test.py'
        assert result['prompt_field']['prompt'] == 'Task done'
        assert result['content'] == content
    
    def test_param_set_node_to_dict_empty(self):
        """Test converting empty ParamSetNode to dictionary."""
        node = ParamSetNode()
        
        result = node.to_dict()
        
        assert result == {}


class TestDirectiveNode:
    """Test suite for DirectiveNode class."""
    
    def test_directive_node_creation(self):
        """Test creating a DirectiveNode."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        param_set = ParamSetNode(target=target)
        node = DirectiveNode(action=action, param_sets=[param_set], line=1, column=0)
        
        assert node.action == action
        assert len(node.param_sets) == 1
        assert node.param_sets[0] == param_set
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.DIRECTIVE
    
    def test_directive_node_multiple_param_sets(self):
        """Test DirectiveNode with multiple parameter sets."""
        action = ActionNode(action_type=TokenType.RUN, value="RUN")
        param_set1 = ParamSetNode()
        param_set2 = ParamSetNode()
        node = DirectiveNode(action=action, param_sets=[param_set1, param_set2])
        
        assert len(node.param_sets) == 2
        assert node.param_sets[0] == param_set1
        assert node.param_sets[1] == param_set2
    
    def test_get_first_filename_with_filename(self):
        """Test get_first_filename when filename is present."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        target = TargetNode(target_type=TokenType.FILE, name="config.py")
        param_set = ParamSetNode(target=target)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.get_first_filename() == "config.py"
    
    def test_get_first_filename_without_filename(self):
        """Test get_first_filename when filename is not present."""
        action = ActionNode(action_type=TokenType.FINISH, value="FINISH")
        param_set = ParamSetNode()
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.get_first_filename() is None
    
    def test_get_first_prompt_with_prompt(self):
        """Test get_first_prompt when prompt is present."""
        action = ActionNode(action_type=TokenType.FINISH, value="FINISH")
        prompt_field = PromptFieldNode(prompt="All done")
        param_set = ParamSetNode(prompt_field=prompt_field)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.get_first_prompt() == "All done"
    
    def test_get_first_prompt_without_prompt(self):
        """Test get_first_prompt when prompt is not present."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        param_set = ParamSetNode()
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.get_first_prompt() is None
    
    def test_get_first_content_with_content(self):
        """Test get_first_content when content is present."""
        action = ActionNode(action_type=TokenType.CHANGE, value="CHANGE")
        content = "def hello(): pass"
        param_set = ParamSetNode(content=content)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.get_first_content() == content
    
    def test_get_first_content_without_content(self):
        """Test get_first_content when content is not present."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        param_set = ParamSetNode()
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.get_first_content() is None
    
    def test_is_read_action_true(self):
        """Test is_read_action returns True for READ action."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_read_action() is True
    
    def test_is_read_action_false(self):
        """Test is_read_action returns False for non-READ action."""
        action = ActionNode(action_type=TokenType.RUN, value="RUN")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_read_action() is False
    
    def test_is_run_action_true(self):
        """Test is_run_action returns True for RUN action."""
        action = ActionNode(action_type=TokenType.RUN, value="RUN")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_run_action() is True
    
    def test_is_run_action_false(self):
        """Test is_run_action returns False for non-RUN action."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_run_action() is False
    
    def test_is_change_action_true(self):
        """Test is_change_action returns True for CHANGE action."""
        action = ActionNode(action_type=TokenType.CHANGE, value="CHANGE")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_change_action() is True
    
    def test_is_change_action_false(self):
        """Test is_change_action returns False for non-CHANGE action."""
        action = ActionNode(action_type=TokenType.FINISH, value="FINISH")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_change_action() is False
    
    def test_is_finish_action_true(self):
        """Test is_finish_action returns True for FINISH action."""
        action = ActionNode(action_type=TokenType.FINISH, value="FINISH")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_finish_action() is True
    
    def test_is_finish_action_false(self):
        """Test is_finish_action returns False for non-FINISH action."""
        action = ActionNode(action_type=TokenType.CHANGE, value="CHANGE")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_finish_action() is False
    
    def test_directive_node_to_dict(self):
        """Test converting DirectiveNode to dictionary."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        param_set = ParamSetNode(target=target)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_dict()
        
        assert result['action']['type'] == 'READ'
        assert result['action']['value'] == 'READ'
        assert len(result['param_sets']) == 1
        assert result['param_sets'][0]['target']['name'] == 'test.py'
    
    def test_directive_node_to_string_read(self):
        """Test converting READ DirectiveNode to string."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        param_set = ParamSetNode(target=target)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_string()
        
        assert result == 'READ "test.py"'
    
    def test_directive_node_to_string_change(self):
        """Test converting CHANGE DirectiveNode to string."""
        action = ActionNode(action_type=TokenType.CHANGE, value="CHANGE")
        content = "print('hello')"
        param_set = ParamSetNode(content=content)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_string()
        
        assert result == 'CHANGE CONTENT="print(\'hello\')"'
    
    def test_directive_node_to_string_finish(self):
        """Test converting FINISH DirectiveNode to string."""
        action = ActionNode(action_type=TokenType.FINISH, value="FINISH")
        prompt_field = PromptFieldNode(prompt="Task completed")
        param_set = ParamSetNode(prompt_field=prompt_field)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_string()
        
        assert result == 'FINISH PROMPT="Task completed"'


class TestASTIntegration:
    """Integration tests for AST classes working together."""
    
    def test_complete_read_directive_workflow(self):
        """Test complete READ directive workflow."""
        # Create READ directive
        directive = ReadDirective(filename="src/models/user.py")
        
        # Execute and verify
        context = {}
        result = directive.execute(context)
        
        assert 'reads' in result
        assert result['reads'][0]['filename'] == "src/models/user.py"
        assert result['reads'][0]['status'] == "pending"
        assert str(directive) == 'READ "src/models/user.py"'
    
    def test_complete_change_directive_workflow(self):
        """Test complete CHANGE directive workflow."""
        # Create CHANGE directive
        content = """def authenticate(username, password):
    user = User.find_by_username(username)
    if user and user.check_password(password):
        return user.generate_token()
    return None"""
        
        directive = ChangeDirective(content=content)
        
        # Execute and verify
        context = {}
        result = directive.execute(context)
        
        assert 'changes' in result
        assert result['changes'][0]['content'] == content
        assert "def authenticate" in result['changes'][0]['content']
        assert str(directive).startswith('CHANGE CONTENT="def authenticate')
    
    def test_complete_finish_directive_workflow(self):
        """Test complete FINISH directive workflow."""
        # Create FINISH directive
        prompt = PromptField(value="Successfully implemented user authentication with JWT tokens and password hashing. All tests are passing.")
        directive = FinishDirective(prompt=prompt)
        
        # Execute and verify
        context = {}
        result = directive.execute(context)
        
        assert result['finished'] is True
        assert result['completion_prompt'] == "Successfully implemented user authentication with JWT tokens and password hashing. All tests are passing."
        assert str(directive) == 'FINISH PROMPT="Successfully implemented user authentication with JWT tokens and password hashing. All tests are passing."'
    
    def test_directive_workflow_sequence(self):
        """Test sequence of different directives working together."""
        context = {}
        
        # READ directive
        read_directive = ReadDirective(filename="requirements.txt")
        context = read_directive.execute(context)
        
        # RUN directive
        run_directive = RunDirective(command="python -m pytest")
        context = run_directive.execute(context)
        
        # CHANGE directive
        change_directive = ChangeDirective(content="print('Hello World')")
        context = change_directive.execute(context)
        
        # FINISH directive
        finish_directive = FinishDirective(prompt=PromptField(value="All tasks completed"))
        context = finish_directive.execute(context)
        
        # Verify final context
        assert len(context['reads']) == 1
        assert len(context['commands']) == 1
        assert len(context['changes']) == 1
        assert context['finished'] is True
        assert context['completion_prompt'] == "All tasks completed" 