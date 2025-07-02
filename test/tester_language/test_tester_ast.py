"""
Comprehensive test suite for the Tester Language AST classes.

Tests cover all AST classes and their methods using partitioning methods to ensure
complete coverage of AST functionality for tester agent operations.
"""

import pytest
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.languages.tester_language.ast import (
    # Directive classes
    ReadDirective,
    RunDirective,
    ChangeDirective,
    FinishDirective,
    DirectiveType,
    
    # Supporting classes
    Target,
    PromptField,
    
    # AST Node classes
    ActionNode,
    TargetNode,
    PromptFieldNode,
    ParamSetNode,
    DirectiveNode,
    
    # Enums
    TokenType,
    NodeType,
    
    # Base classes
    ASTNode,
    ASTVisitor,
    Directive
)


class TestReadDirective:
    """Test suite for ReadDirective class."""
    
    def test_create_read_directive(self):
        """Test creating a basic ReadDirective."""
        directive = ReadDirective(filename="test.py")
        
        assert directive.filename == "test.py"
        assert isinstance(directive, Directive)
    
    def test_read_directive_str(self):
        """Test string representation of ReadDirective."""
        directive = ReadDirective(filename="src/utils/helper.py")
        
        assert str(directive) == 'READ "src/utils/helper.py"'
    
    def test_read_directive_execute(self):
        """Test executing ReadDirective."""
        directive = ReadDirective(filename="test.py")
        context = {}
        
        result = directive.execute(context)
        
        assert 'reads' in result
        assert len(result['reads']) == 1
        assert result['reads'][0]['filename'] == "test.py"
        assert result['reads'][0]['status'] == 'pending'
    
    def test_read_directive_execute_multiple(self):
        """Test executing multiple ReadDirectives."""
        directive1 = ReadDirective(filename="file1.py")
        directive2 = ReadDirective(filename="file2.py")
        context = {}
        
        context = directive1.execute(context)
        context = directive2.execute(context)
        
        assert len(context['reads']) == 2
        assert context['reads'][0]['filename'] == "file1.py"
        assert context['reads'][1]['filename'] == "file2.py"
    
    def test_read_directive_filename_with_spaces(self):
        """Test ReadDirective with filename containing spaces."""
        directive = ReadDirective(filename="my file with spaces.txt")
        
        assert directive.filename == "my file with spaces.txt"
        assert str(directive) == 'READ "my file with spaces.txt"'


class TestRunDirective:
    """Test suite for RunDirective class."""
    
    def test_create_run_directive(self):
        """Test creating a basic RunDirective."""
        directive = RunDirective(command="python -m pytest")
        
        assert directive.command == "python -m pytest"
        assert isinstance(directive, Directive)
    
    def test_run_directive_str(self):
        """Test string representation of RunDirective."""
        directive = RunDirective(command="echo hello world")
        
        assert str(directive) == 'RUN "echo hello world"'
    
    def test_run_directive_execute(self):
        """Test executing RunDirective."""
        directive = RunDirective(command="pytest tests/")
        context = {}
        
        result = directive.execute(context)
        
        assert 'commands' in result
        assert len(result['commands']) == 1
        assert result['commands'][0]['command'] == "pytest tests/"
        assert result['commands'][0]['status'] == 'pending'
    
    def test_run_directive_execute_multiple(self):
        """Test executing multiple RunDirectives."""
        directive1 = RunDirective(command="pytest")
        directive2 = RunDirective(command="flake8")
        context = {}
        
        context = directive1.execute(context)
        context = directive2.execute(context)
        
        assert len(context['commands']) == 2
        assert context['commands'][0]['command'] == "pytest"
        assert context['commands'][1]['command'] == "flake8"
    
    def test_run_directive_complex_command(self):
        """Test RunDirective with complex command."""
        command = "python -m pytest tests/ -v --tb=short --cov=src"
        directive = RunDirective(command=command)
        
        assert directive.command == command
        assert str(directive) == f'RUN "{command}"'


class TestChangeDirective:
    """Test suite for ChangeDirective class."""
    
    def test_create_change_directive(self):
        """Test creating a basic ChangeDirective."""
        content = "print('Hello, World!')"
        directive = ChangeDirective(content=content)
        
        assert directive.content == content
        assert isinstance(directive, Directive)
    
    def test_change_directive_str_short(self):
        """Test string representation of ChangeDirective with short content."""
        content = "print('hello')"
        directive = ChangeDirective(content=content)
        
        assert str(directive) == f'CHANGE CONTENT="{content}"'
    
    def test_change_directive_str_long(self):
        """Test string representation of ChangeDirective with long content."""
        content = "def very_long_function_name_that_exceeds_fifty_characters():\n    pass"
        directive = ChangeDirective(content=content)
        
        str_repr = str(directive)
        assert str_repr.startswith('CHANGE CONTENT="def very_long_function_name_that_exceeds_fifty_cha...')
        assert "..." in str_repr
    
    def test_change_directive_execute(self):
        """Test executing ChangeDirective."""
        content = "import sys\nprint('Debug info')"
        directive = ChangeDirective(content=content)
        context = {}
        
        result = directive.execute(context)
        
        assert 'changes' in result
        assert len(result['changes']) == 1
        assert result['changes'][0]['content'] == content
        assert result['changes'][0]['status'] == 'pending'
    
    def test_change_directive_execute_multiple(self):
        """Test executing multiple ChangeDirectives."""
        directive1 = ChangeDirective(content="print('first')")
        directive2 = ChangeDirective(content="print('second')")
        context = {}
        
        context = directive1.execute(context)
        context = directive2.execute(context)
        
        assert len(context['changes']) == 2
        assert context['changes'][0]['content'] == "print('first')"
        assert context['changes'][1]['content'] == "print('second')"
    
    def test_change_directive_empty_content(self):
        """Test ChangeDirective with empty content."""
        directive = ChangeDirective(content="")
        
        assert directive.content == ""
        assert str(directive) == 'CHANGE CONTENT=""'
    
    def test_change_directive_multiline_content(self):
        """Test ChangeDirective with multiline content."""
        content = "def debug_function():\n    print('Debug')\n    return True"
        directive = ChangeDirective(content=content)
        
        assert directive.content == content
        assert "\n" in directive.content


class TestFinishDirective:
    """Test suite for FinishDirective class."""
    
    def test_create_finish_directive(self):
        """Test creating a basic FinishDirective."""
        prompt = PromptField(value="Task completed successfully")
        directive = FinishDirective(prompt=prompt)
        
        assert directive.prompt == prompt
        assert directive.prompt.value == "Task completed successfully"
        assert isinstance(directive, Directive)
    
    def test_finish_directive_str(self):
        """Test string representation of FinishDirective."""
        prompt = PromptField(value="Analysis complete")
        directive = FinishDirective(prompt=prompt)
        
        assert str(directive) == 'FINISH PROMPT="Analysis complete"'
    
    def test_finish_directive_execute(self):
        """Test executing FinishDirective."""
        prompt = PromptField(value="Testing finished")
        directive = FinishDirective(prompt=prompt)
        context = {}
        
        result = directive.execute(context)
        
        assert result['finished'] is True
        assert result['completion_prompt'] == "Testing finished"
    
    def test_finish_directive_execute_preserves_context(self):
        """Test that FinishDirective preserves existing context."""
        prompt = PromptField(value="Done")
        directive = FinishDirective(prompt=prompt)
        context = {"existing": "data", "reads": []}
        
        result = directive.execute(context)
        
        assert result['existing'] == "data"
        assert result['reads'] == []
        assert result['finished'] is True
        assert result['completion_prompt'] == "Done"
    
    def test_finish_directive_empty_prompt(self):
        """Test FinishDirective with empty prompt."""
        prompt = PromptField(value="")
        directive = FinishDirective(prompt=prompt)
        
        assert directive.prompt.value == ""
        assert str(directive) == 'FINISH PROMPT=""'


class TestTarget:
    """Test suite for Target class."""
    
    def test_create_target(self):
        """Test creating a basic Target."""
        target = Target(name="test.py")
        
        assert target.name == "test.py"
    
    def test_target_str(self):
        """Test string representation of Target."""
        target = Target(name="src/module.py")
        
        assert str(target) == "file:src/module.py"
    
    def test_target_equality(self):
        """Test Target equality comparison."""
        target1 = Target(name="test.py")
        target2 = Target(name="test.py")
        target3 = Target(name="other.py")
        
        assert target1.name == target2.name
        assert target1.name != target3.name


class TestPromptField:
    """Test suite for PromptField class."""
    
    def test_create_prompt_field(self):
        """Test creating a basic PromptField."""
        prompt = PromptField(value="Test message")
        
        assert prompt.value == "Test message"
    
    def test_prompt_field_str(self):
        """Test string representation of PromptField."""
        prompt = PromptField(value="Complete the task")
        
        assert str(prompt) == 'PROMPT="Complete the task"'
    
    def test_prompt_field_empty(self):
        """Test PromptField with empty value."""
        prompt = PromptField(value="")
        
        assert prompt.value == ""
        assert str(prompt) == 'PROMPT=""'
    
    def test_prompt_field_with_quotes(self):
        """Test PromptField with quotes in value."""
        prompt = PromptField(value='Say "hello" to the user')
        
        assert prompt.value == 'Say "hello" to the user'
        assert str(prompt) == 'PROMPT="Say "hello" to the user"'


class TestActionNode:
    """Test suite for ActionNode class."""
    
    def test_create_action_node(self):
        """Test creating a basic ActionNode."""
        node = ActionNode(action_type=TokenType.READ, value="READ")
        
        assert node.action_type == TokenType.READ
        assert node.value == "READ"
        assert node.node_type == NodeType.ACTION
    
    def test_action_node_repr(self):
        """Test string representation of ActionNode."""
        node = ActionNode(action_type=TokenType.RUN, value="RUN")
        
        repr_str = repr(node)
        assert "ActionNode" in repr_str
        assert "RUN" in repr_str
    
    def test_action_node_with_coordinates(self):
        """Test ActionNode with line and column coordinates."""
        node = ActionNode(action_type=TokenType.CHANGE, value="CHANGE", line=5, column=10)
        
        assert node.line == 5
        assert node.column == 10


class TestTargetNode:
    """Test suite for TargetNode class."""
    
    def test_create_target_node(self):
        """Test creating a basic TargetNode."""
        node = TargetNode(target_type=TokenType.FILE, name="test.py")
        
        assert node.target_type == TokenType.FILE
        assert node.name == "test.py"
        assert node.node_type == NodeType.TARGET
    
    def test_target_node_repr(self):
        """Test string representation of TargetNode."""
        node = TargetNode(target_type=TokenType.FILE, name="module.py")
        
        repr_str = repr(node)
        assert "TargetNode" in repr_str
        assert "FILE" in repr_str
        assert "module.py" in repr_str


class TestPromptFieldNode:
    """Test suite for PromptFieldNode class."""
    
    def test_create_prompt_field_node(self):
        """Test creating a basic PromptFieldNode."""
        node = PromptFieldNode(prompt="Complete the analysis")
        
        assert node.prompt == "Complete the analysis"
        assert node.node_type == NodeType.PROMPT_FIELD
    
    def test_prompt_field_node_repr(self):
        """Test string representation of PromptFieldNode."""
        node = PromptFieldNode(prompt="Test prompt")
        
        repr_str = repr(node)
        assert "PromptFieldNode" in repr_str
        assert "Test prompt" in repr_str


class TestParamSetNode:
    """Test suite for ParamSetNode class."""
    
    def test_create_empty_param_set_node(self):
        """Test creating an empty ParamSetNode."""
        node = ParamSetNode()
        
        assert node.target is None
        assert node.prompt_field is None
        assert node.content is None
        assert node.node_type == NodeType.PARAM_SET
    
    def test_create_param_set_node_with_target(self):
        """Test creating ParamSetNode with target."""
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        node = ParamSetNode(target=target)
        
        assert node.target == target
        assert node.get_filename() == "test.py"
    
    def test_create_param_set_node_with_prompt(self):
        """Test creating ParamSetNode with prompt field."""
        prompt = PromptFieldNode(prompt="Test message")
        node = ParamSetNode(prompt_field=prompt)
        
        assert node.prompt_field == prompt
        assert node.get_prompt() == "Test message"
    
    def test_create_param_set_node_with_content(self):
        """Test creating ParamSetNode with content."""
        content = "print('debug')"
        node = ParamSetNode(content=content)
        
        assert node.content == content
        assert node.get_content() == content
    
    def test_param_set_node_get_methods_none(self):
        """Test ParamSetNode get methods return None when fields are empty."""
        node = ParamSetNode()
        
        assert node.get_filename() is None
        assert node.get_prompt() is None
        assert node.get_content() is None
    
    def test_param_set_node_to_dict(self):
        """Test ParamSetNode to_dict method."""
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        prompt = PromptFieldNode(prompt="Test")
        content = "code"
        node = ParamSetNode(target=target, prompt_field=prompt, content=content)
        
        result = node.to_dict()
        
        assert result['target']['type'] == 'FILE'
        assert result['target']['name'] == 'test.py'
        assert result['prompt_field']['prompt'] == 'Test'
        assert result['content'] == 'code'
    
    def test_param_set_node_to_dict_empty(self):
        """Test ParamSetNode to_dict method with empty node."""
        node = ParamSetNode()
        
        result = node.to_dict()
        
        assert result == {}
    
    def test_param_set_node_repr(self):
        """Test ParamSetNode string representation."""
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        node = ParamSetNode(target=target)
        
        repr_str = repr(node)
        assert "ParamSetNode" in repr_str


class TestDirectiveNode:
    """Test suite for DirectiveNode class."""
    
    def test_create_directive_node(self):
        """Test creating a basic DirectiveNode."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        param_set = ParamSetNode()
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.action == action
        assert node.param_sets == [param_set]
        assert node.node_type == NodeType.DIRECTIVE
    
    def test_directive_node_is_methods(self):
        """Test DirectiveNode is_* methods."""
        read_action = ActionNode(action_type=TokenType.READ, value="READ")
        run_action = ActionNode(action_type=TokenType.RUN, value="RUN")
        change_action = ActionNode(action_type=TokenType.CHANGE, value="CHANGE")
        finish_action = ActionNode(action_type=TokenType.FINISH, value="FINISH")
        
        read_node = DirectiveNode(action=read_action, param_sets=[])
        run_node = DirectiveNode(action=run_action, param_sets=[])
        change_node = DirectiveNode(action=change_action, param_sets=[])
        finish_node = DirectiveNode(action=finish_action, param_sets=[])
        
        assert read_node.is_read_action() is True
        assert read_node.is_run_action() is False
        assert read_node.is_change_action() is False
        assert read_node.is_finish_action() is False
        
        assert run_node.is_run_action() is True
        assert run_node.is_read_action() is False
        
        assert change_node.is_change_action() is True
        assert change_node.is_read_action() is False
        
        assert finish_node.is_finish_action() is True
        assert finish_node.is_read_action() is False
    
    def test_directive_node_get_first_methods(self):
        """Test DirectiveNode get_first_* methods."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        prompt = PromptFieldNode(prompt="Test prompt")
        param_set = ParamSetNode(target=target, prompt_field=prompt, content="code")
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.get_first_filename() == "test.py"
        assert node.get_first_prompt() == "Test prompt"
        assert node.get_first_content() == "code"
    
    def test_directive_node_get_first_methods_empty(self):
        """Test DirectiveNode get_first_* methods with empty param sets."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.get_first_filename() is None
        assert node.get_first_prompt() is None
        assert node.get_first_content() is None
    
    def test_directive_node_to_dict(self):
        """Test DirectiveNode to_dict method."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        param_set = ParamSetNode(target=target)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_dict()
        
        assert result['action']['type'] == 'READ'
        assert result['action']['value'] == 'READ'
        assert len(result['param_sets']) == 1
        assert result['param_sets'][0]['target']['name'] == 'test.py'
    
    def test_directive_node_to_string(self):
        """Test DirectiveNode to_string method."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        param_set = ParamSetNode(target=target)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_string()
        
        assert result == 'READ "test.py"'
    
    def test_directive_node_to_string_with_content_and_prompt(self):
        """Test DirectiveNode to_string method with content and prompt."""
        action = ActionNode(action_type=TokenType.CHANGE, value="CHANGE")
        prompt = PromptFieldNode(prompt="Test")
        param_set = ParamSetNode(prompt_field=prompt, content="code")
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_string()
        
        assert 'CHANGE' in result
        assert 'CONTENT="code"' in result
        assert 'PROMPT="Test"' in result
    
    def test_directive_node_repr(self):
        """Test DirectiveNode string representation."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        node = DirectiveNode(action=action, param_sets=[])
        
        repr_str = repr(node)
        assert "DirectiveNode" in repr_str


class TestEnums:
    """Test suite for enum classes."""
    
    def test_token_type_enum(self):
        """Test TokenType enum values."""
        assert TokenType.READ.value == "READ"
        assert TokenType.RUN.value == "RUN"
        assert TokenType.CHANGE.value == "CHANGE"
        assert TokenType.FINISH.value == "FINISH"
        assert TokenType.FILE.value == "FILE"
        assert TokenType.IDENTIFIER.value == "IDENTIFIER"
    
    def test_node_type_enum(self):
        """Test NodeType enum values."""
        assert NodeType.DIRECTIVE.value == "DIRECTIVE"
        assert NodeType.ACTION.value == "ACTION"
        assert NodeType.TARGET.value == "TARGET"
        assert NodeType.PROMPT_FIELD.value == "PROMPT_FIELD"
        assert NodeType.PARAM_SET.value == "PARAM_SET"


class MockVisitor(ASTVisitor):
    """Mock visitor implementation for testing."""
    
    def __init__(self):
        self.visited = []
    
    def visit_directive(self, node):
        self.visited.append(('directive', node))
        return "directive_result"
    
    def visit_action(self, node):
        self.visited.append(('action', node))
        return "action_result"
    
    def visit_target(self, node):
        self.visited.append(('target', node))
        return "target_result"
    
    def visit_prompt_field(self, node):
        self.visited.append(('prompt_field', node))
        return "prompt_field_result"
    
    def visit_param_set(self, node):
        self.visited.append(('param_set', node))
        return "param_set_result"


class TestVisitorPattern:
    """Test suite for AST Visitor pattern."""
    
    def test_action_node_accept(self):
        """Test ActionNode accept method."""
        node = ActionNode(action_type=TokenType.READ, value="READ")
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        
        assert result == "action_result"
        assert len(visitor.visited) == 1
        assert visitor.visited[0] == ('action', node)
    
    def test_target_node_accept(self):
        """Test TargetNode accept method."""
        node = TargetNode(target_type=TokenType.FILE, name="test.py")
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        
        assert result == "target_result"
        assert len(visitor.visited) == 1
        assert visitor.visited[0] == ('target', node)
    
    def test_prompt_field_node_accept(self):
        """Test PromptFieldNode accept method."""
        node = PromptFieldNode(prompt="Test")
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        
        assert result == "prompt_field_result"
        assert len(visitor.visited) == 1
        assert visitor.visited[0] == ('prompt_field', node)
    
    def test_param_set_node_accept(self):
        """Test ParamSetNode accept method."""
        node = ParamSetNode()
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        
        assert result == "param_set_result"
        assert len(visitor.visited) == 1
        assert visitor.visited[0] == ('param_set', node)
    
    def test_directive_node_accept(self):
        """Test DirectiveNode accept method."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        node = DirectiveNode(action=action, param_sets=[])
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        
        assert result == "directive_result"
        assert len(visitor.visited) == 1
        assert visitor.visited[0] == ('directive', node)


class TestDirectiveType:
    """Test suite for DirectiveType union."""
    
    def test_directive_type_instances(self):
        """Test that all directive classes are valid DirectiveType instances."""
        read_directive = ReadDirective(filename="test.py")
        run_directive = RunDirective(command="pytest")
        change_directive = ChangeDirective(content="code")
        finish_directive = FinishDirective(prompt=PromptField(value="done"))
        
        # These should all be valid DirectiveType instances
        directives = [read_directive, run_directive, change_directive, finish_directive]
        
        for directive in directives:
            assert isinstance(directive, Directive)
            assert hasattr(directive, 'execute')
            assert hasattr(directive, '__str__')


class TestAbstractMethods:
    """Test suite for abstract method enforcement."""
    
    def test_directive_abstract_methods(self):
        """Test that Directive abstract methods are enforced."""
        # This should raise TypeError because Directive is abstract
        with pytest.raises(TypeError):
            Directive()  # type: ignore
    
    def test_ast_node_abstract_methods(self):
        """Test that ASTNode abstract methods are enforced."""
        # This should raise TypeError because ASTNode is abstract
        with pytest.raises(TypeError):
            ASTNode(NodeType.ACTION)  # type: ignore
    
    def test_ast_visitor_abstract_methods(self):
        """Test that ASTVisitor abstract methods are enforced."""
        # This should raise TypeError because ASTVisitor is abstract
        with pytest.raises(TypeError):
            ASTVisitor()  # type: ignore 