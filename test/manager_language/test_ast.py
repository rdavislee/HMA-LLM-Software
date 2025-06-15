"""
Comprehensive test suite for the Manager Language AST classes.

Tests cover all AST classes and methods in ast.py using partitioning methods to ensure
complete coverage of abstract syntax tree functionality for autonomous agent coordination.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from manager_language.ast import (
    # Basic data classes
    Target,
    PromptField,
    DelegateItem,
    
    # Directive classes
    Directive,
    DelegateDirective,
    FinishDirective,
    ActionDirective,
    WaitDirective,
    RunDirective,
    DirectiveType,
    
    # AST Node classes
    NodeType,
    ASTNode,
    ASTVisitor,
    ActionNode,
    TargetNode,
    PromptFieldNode,
    ParamSetNode,
    WaitDirectiveNode,
    DirectiveNode,
    
    # Grammar imports
    TokenType
)


class TestTarget:
    """Test suite for Target data class."""
    
    def test_target_file_creation(self):
        """Test creating a file target."""
        target = Target(name="test.txt", is_folder=False)
        
        assert target.name == "test.txt"
        assert not target.is_folder
        assert str(target) == "file:test.txt"
    
    def test_target_folder_creation(self):
        """Test creating a folder target."""
        target = Target(name="my_folder", is_folder=True)
        
        assert target.name == "my_folder"
        assert target.is_folder
        assert str(target) == "folder:my_folder"
    
    def test_target_with_path(self):
        """Test creating target with path."""
        target = Target(name="src/components/Button.js", is_folder=False)
        
        assert target.name == "src/components/Button.js"
        assert not target.is_folder
        assert str(target) == "file:src/components/Button.js"
    
    def test_target_default_is_folder(self):
        """Test default is_folder parameter."""
        target = Target(name="test")
        
        assert target.name == "test"
        assert not target.is_folder  # Default should be False


class TestPromptField:
    """Test suite for PromptField data class."""
    
    def test_prompt_field_creation(self):
        """Test creating a prompt field."""
        prompt = PromptField(value="Create a new file")
        
        assert prompt.value == "Create a new file"
        assert str(prompt) == 'PROMPT="Create a new file"'
    
    def test_prompt_field_with_special_chars(self):
        """Test prompt field with special characters."""
        prompt = PromptField(value='Create file with "quotes" and \n newlines')
        
        assert prompt.value == 'Create file with "quotes" and \n newlines'
        assert str(prompt) == 'PROMPT="Create file with "quotes" and \n newlines"'
    
    def test_prompt_field_empty(self):
        """Test empty prompt field."""
        prompt = PromptField(value="")
        
        assert prompt.value == ""
        assert str(prompt) == 'PROMPT=""'
    
    def test_prompt_field_complex_instruction(self):
        """Test prompt field with complex agent instruction."""
        complex_prompt = """Create a REST API with the following features:
1. User authentication with JWT tokens
2. CRUD operations for posts
3. File upload functionality
4. Rate limiting
Coordinate with database agent for schema design."""
        
        prompt = PromptField(value=complex_prompt)
        
        assert prompt.value == complex_prompt
        assert "REST API" in prompt.value
        assert "authentication" in prompt.value


class TestDelegateItem:
    """Test suite for DelegateItem data class."""
    
    def test_delegate_item_creation(self):
        """Test creating a delegate item."""
        target = Target(name="test.txt", is_folder=False)
        prompt = PromptField(value="Create this file")
        item = DelegateItem(target=target, prompt=prompt)
        
        assert item.target == target
        assert item.prompt == prompt
        assert str(item) == 'file:test.txt PROMPT="Create this file"'
    
    def test_delegate_item_folder(self):
        """Test creating delegate item for folder."""
        target = Target(name="src", is_folder=True)
        prompt = PromptField(value="Create source folder structure")
        item = DelegateItem(target=target, prompt=prompt)
        
        assert item.target.is_folder
        assert str(item) == 'folder:src PROMPT="Create source folder structure"'


class TestActionDirective:
    """Test suite for ActionDirective class."""
    
    def test_create_directive_execution(self):
        """Test CREATE directive execution."""
        target = Target(name="test.txt", is_folder=False)
        directive = ActionDirective(action_type="CREATE", targets=[target])
        
        context = {}
        result = directive.execute(context)
        
        assert 'actions' in result
        assert len(result['actions']) == 1
        assert result['actions'][0]['type'] == "CREATE"
        assert result['actions'][0]['target'] == "test.txt"
        assert not result['actions'][0]['is_folder']
    
    def test_delete_directive_execution(self):
        """Test DELETE directive execution."""
        target = Target(name="old_file.txt", is_folder=False)
        directive = ActionDirective(action_type="DELETE", targets=[target])
        
        context = {}
        result = directive.execute(context)
        
        assert 'actions' in result
        assert len(result['actions']) == 1
        assert result['actions'][0]['type'] == "DELETE"
        assert result['actions'][0]['target'] == "old_file.txt"
    
    def test_read_directive_execution(self):
        """Test READ directive execution."""
        target = Target(name="config.json", is_folder=False)
        directive = ActionDirective(action_type="READ", targets=[target])
        
        context = {}
        result = directive.execute(context)
        
        assert 'actions' in result
        assert len(result['actions']) == 1
        assert result['actions'][0]['type'] == "READ"
        assert result['actions'][0]['target'] == "config.json"
    
    def test_multiple_targets_execution(self):
        """Test action directive with multiple targets."""
        targets = [
            Target(name="file1.txt", is_folder=False),
            Target(name="file2.txt", is_folder=False),
            Target(name="folder1", is_folder=True)
        ]
        directive = ActionDirective(action_type="CREATE", targets=targets)
        
        context = {}
        result = directive.execute(context)
        
        assert 'actions' in result
        assert len(result['actions']) == 3
        assert all(action['type'] == "CREATE" for action in result['actions'])
    
    def test_action_directive_string_representation(self):
        """Test string representation of action directive."""
        targets = [
            Target(name="file1.txt", is_folder=False),
            Target(name="folder1", is_folder=True)
        ]
        directive = ActionDirective(action_type="CREATE", targets=targets)
        
        expected = "CREATE file:file1.txt, folder:folder1"
        assert str(directive) == expected
    
    def test_action_directive_context_preservation(self):
        """Test that action directive preserves existing context."""
        target = Target(name="test.txt", is_folder=False)
        directive = ActionDirective(action_type="CREATE", targets=[target])
        
        context = {
            'existing_data': 'value',
            'actions': [{'type': 'READ', 'target': 'existing.txt'}]
        }
        result = directive.execute(context)
        
        assert result['existing_data'] == 'value'
        assert len(result['actions']) == 2
        assert result['actions'][0]['type'] == 'READ'
        assert result['actions'][1]['type'] == 'CREATE'


class TestDelegateDirective:
    """Test suite for DelegateDirective class."""
    
    def test_delegate_directive_execution(self):
        """Test delegate directive execution."""
        target = Target(name="test.txt", is_folder=False)
        prompt = PromptField(value="Create this file")
        item = DelegateItem(target=target, prompt=prompt)
        directive = DelegateDirective(items=[item])
        
        context = {}
        result = directive.execute(context)
        
        assert 'delegations' in result
        assert len(result['delegations']) == 1
        assert result['delegations'][0]['target'] == "test.txt"
        assert result['delegations'][0]['prompt'] == "Create this file"
        assert not result['delegations'][0]['is_folder']
    
    def test_multiple_delegations_execution(self):
        """Test delegate directive with multiple items."""
        items = [
            DelegateItem(
                target=Target(name="frontend/index.html", is_folder=False),
                prompt=PromptField(value="Create HTML structure")
            ),
            DelegateItem(
                target=Target(name="frontend/styles.css", is_folder=False),
                prompt=PromptField(value="Create CSS styles")
            ),
            DelegateItem(
                target=Target(name="api", is_folder=True),
                prompt=PromptField(value="Create API structure")
            )
        ]
        directive = DelegateDirective(items=items)
        
        context = {}
        result = directive.execute(context)
        
        assert 'delegations' in result
        assert len(result['delegations']) == 3
        assert result['delegations'][0]['target'] == "frontend/index.html"
        assert result['delegations'][1]['target'] == "frontend/styles.css"
        assert result['delegations'][2]['target'] == "api"
        assert result['delegations'][2]['is_folder']
    
    def test_delegate_directive_string_representation(self):
        """Test string representation of delegate directive."""
        items = [
            DelegateItem(
                target=Target(name="file1.txt", is_folder=False),
                prompt=PromptField(value="Create file1")
            ),
            DelegateItem(
                target=Target(name="file2.txt", is_folder=False),
                prompt=PromptField(value="Create file2")
            )
        ]
        directive = DelegateDirective(items=items)
        
        expected = 'DELEGATE file:file1.txt PROMPT="Create file1", file:file2.txt PROMPT="Create file2"'
        assert str(directive) == expected
    
    def test_delegate_directive_context_preservation(self):
        """Test that delegate directive preserves existing context."""
        target = Target(name="test.txt", is_folder=False)
        prompt = PromptField(value="Create this file")
        item = DelegateItem(target=target, prompt=prompt)
        directive = DelegateDirective(items=[item])
        
        context = {
            'existing_data': 'value',
            'delegations': [{'target': 'existing.txt', 'prompt': 'existing task'}]
        }
        result = directive.execute(context)
        
        assert result['existing_data'] == 'value'
        assert len(result['delegations']) == 2
        assert result['delegations'][0]['target'] == 'existing.txt'
        assert result['delegations'][1]['target'] == 'test.txt'


class TestFinishDirective:
    """Test suite for FinishDirective class."""
    
    def test_finish_directive_execution(self):
        """Test finish directive execution."""
        prompt = PromptField(value="Task completed successfully")
        directive = FinishDirective(prompt=prompt)
        
        context = {}
        result = directive.execute(context)
        
        assert result['finished'] is True
        assert result['completion_prompt'] == "Task completed successfully"
    
    def test_finish_directive_string_representation(self):
        """Test string representation of finish directive."""
        prompt = PromptField(value="All tasks completed")
        directive = FinishDirective(prompt=prompt)
        
        expected = 'FINISH PROMPT="All tasks completed"'
        assert str(directive) == expected
    
    def test_finish_directive_context_preservation(self):
        """Test that finish directive preserves existing context."""
        prompt = PromptField(value="Task completed")
        directive = FinishDirective(prompt=prompt)
        
        context = {
            'existing_data': 'value',
            'actions': [{'type': 'CREATE', 'target': 'test.txt'}],
            'delegations': [{'target': 'test.txt', 'prompt': 'create'}]
        }
        result = directive.execute(context)
        
        assert result['existing_data'] == 'value'
        assert len(result['actions']) == 1
        assert len(result['delegations']) == 1
        assert result['finished'] is True
        assert result['completion_prompt'] == "Task completed"


class TestWaitDirective:
    """Test suite for WaitDirective class."""
    
    def test_wait_directive_execution(self):
        """Test wait directive execution."""
        directive = WaitDirective()
        
        context = {}
        result = directive.execute(context)
        
        assert result['waiting'] is True
    
    def test_wait_directive_string_representation(self):
        """Test string representation of wait directive."""
        directive = WaitDirective()
        
        assert str(directive) == "WAIT"
    
    def test_wait_directive_context_preservation(self):
        """Test that WAIT directive preserves existing context."""
        directive = WaitDirective()
        
        # Set up existing context
        context = {
            'actions': [{'type': 'CREATE', 'target': 'test.txt'}],
            'delegations': [{'target': 'test.txt', 'prompt': 'Create file'}],
            'finished': False
        }
        
        result = directive.execute(context)
        
        # Check that existing context is preserved
        assert 'actions' in result and len(result['actions']) == 1
        assert 'delegations' in result and len(result['delegations']) == 1
        assert result['finished'] is False
        
        # Check that waiting is set
        assert result['waiting'] is True


class TestRunDirective:
    """Test suite for RunDirective class."""
    
    def test_run_directive_execution(self):
        """Test RUN directive execution."""
        directive = RunDirective(command="echo hello world")
        
        context = {}
        result = directive.execute(context)
        
        assert 'commands' in result
        assert len(result['commands']) == 1
        assert result['commands'][0]['command'] == "echo hello world"
        assert result['commands'][0]['status'] == "pending"
    
    def test_run_directive_multiple_execution(self):
        """Test multiple RUN directives execution."""
        directive1 = RunDirective(command="npm install")
        directive2 = RunDirective(command="npm run build")
        
        context = {}
        result1 = directive1.execute(context)
        result2 = directive2.execute(result1)
        
        assert 'commands' in result2
        assert len(result2['commands']) == 2
        assert result2['commands'][0]['command'] == "npm install"
        assert result2['commands'][1]['command'] == "npm run build"
    
    def test_run_directive_string_representation(self):
        """Test RUN directive string representation."""
        directive = RunDirective(command="python main.py")
        
        assert str(directive) == 'RUN "python main.py"'
    
    def test_run_directive_complex_command(self):
        """Test RUN directive with complex command."""
        complex_command = "git add . && git commit -m \"Update code\" && git push"
        directive = RunDirective(command=complex_command)
        
        context = {}
        result = directive.execute(context)
        
        assert result['commands'][0]['command'] == complex_command
    
    def test_run_directive_context_preservation(self):
        """Test that RUN directive preserves existing context."""
        directive = RunDirective(command="echo test")
        
        # Set up existing context
        context = {
            'actions': [{'type': 'CREATE', 'target': 'test.txt'}],
            'delegations': [{'target': 'test.txt', 'prompt': 'Create file'}],
            'finished': False
        }
        
        result = directive.execute(context)
        
        # Check that existing context is preserved
        assert 'actions' in result and len(result['actions']) == 1
        assert 'delegations' in result and len(result['delegations']) == 1
        assert result['finished'] is False
        
        # Check that command is added
        assert 'commands' in result and len(result['commands']) == 1
        assert result['commands'][0]['command'] == "echo test"


class TestActionNode:
    """Test suite for ActionNode class."""
    
    def test_action_node_creation(self):
        """Test creating an action node."""
        node = ActionNode(TokenType.CREATE, "CREATE", line=1, column=0)
        
        assert node.action_type == TokenType.CREATE
        assert node.value == "CREATE"
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.ACTION
    
    def test_action_node_representation(self):
        """Test string representation of action node."""
        node = ActionNode(TokenType.DELEGATE, "DELEGATE", line=1, column=0)
        
        assert repr(node) == "ActionNode(TokenType.DELEGATE, 'DELEGATE')"
    
    def test_action_node_visitor_acceptance(self):
        """Test action node accepts visitors."""
        class MockVisitor(ASTVisitor):
            def visit_directive(self, node): pass
            def visit_wait_directive(self, node): pass
            def visit_action(self, node): 
                return "visited_action"
            def visit_target(self, node): pass
            def visit_prompt_field(self, node): pass
            def visit_param_set(self, node): pass
        
        node = ActionNode(TokenType.CREATE, "CREATE")
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        assert result == "visited_action"


class TestTargetNode:
    """Test suite for TargetNode class."""
    
    def test_target_node_file_creation(self):
        """Test creating a file target node."""
        node = TargetNode(TokenType.FILE, "test.txt", line=1, column=0)
        
        assert node.target_type == TokenType.FILE
        assert node.name == "test.txt"
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.TARGET
    
    def test_target_node_folder_creation(self):
        """Test creating a folder target node."""
        node = TargetNode(TokenType.FOLDER, "src", line=1, column=0)
        
        assert node.target_type == TokenType.FOLDER
        assert node.name == "src"
        assert node.node_type == NodeType.TARGET
    
    def test_target_node_identifier_creation(self):
        """Test creating an identifier target node (for child agents)."""
        node = TargetNode(TokenType.IDENTIFIER, "child_agent", line=1, column=0)
        
        assert node.target_type == TokenType.IDENTIFIER
        assert node.name == "child_agent"
        assert node.node_type == NodeType.TARGET
    
    def test_target_node_representation(self):
        """Test string representation of target node."""
        node = TargetNode(TokenType.FILE, "test.txt", line=1, column=0)
        
        assert repr(node) == "TargetNode(TokenType.FILE, 'test.txt')"
    
    def test_target_node_visitor_acceptance(self):
        """Test target node accepts visitors."""
        class MockVisitor(ASTVisitor):
            def visit_directive(self, node): pass
            def visit_wait_directive(self, node): pass
            def visit_action(self, node): pass
            def visit_target(self, node): 
                return "visited_target"
            def visit_prompt_field(self, node): pass
            def visit_param_set(self, node): pass
        
        node = TargetNode(TokenType.FILE, "test.txt")
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        assert result == "visited_target"


class TestPromptFieldNode:
    """Test suite for PromptFieldNode class."""
    
    def test_prompt_field_node_creation(self):
        """Test creating a prompt field node."""
        node = PromptFieldNode("Create this file", line=1, column=0)
        
        assert node.prompt == "Create this file"
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.PROMPT_FIELD
    
    def test_prompt_field_node_representation(self):
        """Test string representation of prompt field node."""
        node = PromptFieldNode("Create this file", line=1, column=0)
        
        assert repr(node) == "PromptFieldNode('Create this file')"
    
    def test_prompt_field_node_visitor_acceptance(self):
        """Test prompt field node accepts visitors."""
        class MockVisitor(ASTVisitor):
            def visit_directive(self, node): pass
            def visit_wait_directive(self, node): pass
            def visit_action(self, node): pass
            def visit_target(self, node): pass
            def visit_prompt_field(self, node): 
                return "visited_prompt"
            def visit_param_set(self, node): pass
        
        node = PromptFieldNode("Create this file")
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        assert result == "visited_prompt"


class TestParamSetNode:
    """Test suite for ParamSetNode class."""
    
    def test_param_set_node_with_target_and_prompt(self):
        """Test creating param set node with both target and prompt."""
        target = TargetNode(TokenType.FILE, "test.txt")
        prompt = PromptFieldNode("Create this file")
        node = ParamSetNode(target=target, prompt_field=prompt, line=1, column=0)
        
        assert node.target == target
        assert node.prompt_field == prompt
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.PARAM_SET
    
    def test_param_set_node_with_target_only(self):
        """Test creating param set node with target only."""
        target = TargetNode(TokenType.FILE, "test.txt")
        node = ParamSetNode(target=target, line=1, column=0)
        
        assert node.target == target
        assert node.prompt_field is None
    
    def test_param_set_node_with_prompt_only(self):
        """Test creating param set node with prompt only."""
        prompt = PromptFieldNode("Task completed")
        node = ParamSetNode(prompt_field=prompt, line=1, column=0)
        
        assert node.target is None
        assert node.prompt_field == prompt
    
    def test_param_set_node_empty(self):
        """Test creating empty param set node."""
        node = ParamSetNode(line=1, column=0)
        
        assert node.target is None
        assert node.prompt_field is None
    
    def test_get_prompt_with_prompt(self):
        """Test get_prompt method when prompt field exists."""
        prompt = PromptFieldNode("Create this file")
        node = ParamSetNode(prompt_field=prompt)
        
        assert node.get_prompt() == "Create this file"
    
    def test_get_prompt_without_prompt(self):
        """Test get_prompt method when no prompt field exists."""
        node = ParamSetNode()
        
        assert node.get_prompt() is None
    
    def test_get_next_agent_finish(self):
        """Test get_next_agent for FINISH action."""
        node = ParamSetNode()
        
        result = node.get_next_agent(TokenType.FINISH)
        assert result == "PARENT"
    
    def test_get_next_agent_delegate(self):
        """Test get_next_agent for DELEGATE action."""
        target = TargetNode(TokenType.IDENTIFIER, "child_agent")
        node = ParamSetNode(target=target)
        
        result = node.get_next_agent(TokenType.DELEGATE)
        assert result == "child_agent"
    
    def test_get_next_agent_other_actions(self):
        """Test get_next_agent for other actions."""
        node = ParamSetNode()
        
        for action_type in [TokenType.CREATE, TokenType.DELETE, TokenType.READ]:
            result = node.get_next_agent(action_type)
            assert result == "SELF"
    
    def test_is_child_agent_selection_delegate(self):
        """Test is_child_agent_selection for DELEGATE action."""
        node = ParamSetNode()
        
        assert node.is_child_agent_selection(TokenType.DELEGATE) is True
    
    def test_is_child_agent_selection_other_actions(self):
        """Test is_child_agent_selection for other actions."""
        node = ParamSetNode()
        
        for action_type in [TokenType.CREATE, TokenType.DELETE, TokenType.READ, TokenType.FINISH]:
            assert node.is_child_agent_selection(action_type) is False
    
    def test_is_parent_selection_finish(self):
        """Test is_parent_selection for FINISH action."""
        node = ParamSetNode()
        
        assert node.is_parent_selection(TokenType.FINISH) is True
    
    def test_is_parent_selection_other_actions(self):
        """Test is_parent_selection for other actions."""
        node = ParamSetNode()
        
        for action_type in [TokenType.CREATE, TokenType.DELETE, TokenType.READ, TokenType.DELEGATE]:
            assert node.is_parent_selection(action_type) is False
    
    def test_param_set_node_representation(self):
        """Test string representation of param set node."""
        target = TargetNode(TokenType.FILE, "test.txt")
        prompt = PromptFieldNode("Create this file")
        node = ParamSetNode(target=target, prompt_field=prompt)
        expected = "ParamSetNode(TargetNode(TokenType.FILE, 'test.txt'), PromptFieldNode('Create this file'))"
        assert repr(node) == expected
    
    def test_param_set_node_to_dict_with_target_and_prompt(self):
        """Test to_dict method with both target and prompt."""
        target = TargetNode(TokenType.FILE, "test.txt")
        prompt = PromptFieldNode("Create this file")
        node = ParamSetNode(target=target, prompt_field=prompt)
        
        result = node.to_dict()
        
        assert 'target' in result
        assert result['target']['type'] == 'FILE'
        assert result['target']['name'] == 'test.txt'
        assert 'prompt_field' in result
        assert result['prompt_field']['prompt'] == 'Create this file'
    
    def test_param_set_node_to_dict_with_target_only(self):
        """Test to_dict method with target only."""
        target = TargetNode(TokenType.FOLDER, "src")
        node = ParamSetNode(target=target)
        
        result = node.to_dict()
        
        assert 'target' in result
        assert result['target']['type'] == 'FOLDER'
        assert result['target']['name'] == 'src'
        assert 'prompt_field' not in result
    
    def test_param_set_node_to_dict_with_prompt_only(self):
        """Test to_dict method with prompt only."""
        prompt = PromptFieldNode("Task completed")
        node = ParamSetNode(prompt_field=prompt)
        
        result = node.to_dict()
        
        assert 'target' not in result
        assert 'prompt_field' in result
        assert result['prompt_field']['prompt'] == 'Task completed'
    
    def test_param_set_node_to_dict_empty(self):
        """Test to_dict method with empty node."""
        node = ParamSetNode()
        
        result = node.to_dict()
        
        assert result == {}


class TestWaitDirectiveNode:
    """Test suite for WaitDirectiveNode class."""
    
    def test_wait_directive_node_creation(self):
        """Test creating a wait directive node."""
        node = WaitDirectiveNode(line=1, column=0)
        
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.WAIT_DIRECTIVE
    
    def test_wait_directive_node_representation(self):
        """Test string representation of wait directive node."""
        node = WaitDirectiveNode()
        
        assert repr(node) == "WaitDirectiveNode()"
    
    def test_wait_directive_node_to_dict(self):
        """Test to_dict method."""
        node = WaitDirectiveNode()
        
        result = node.to_dict()
        
        assert result == {'type': 'WAIT'}
    
    def test_wait_directive_node_to_string(self):
        """Test to_string method."""
        node = WaitDirectiveNode()
        
        result = node.to_string()
        
        assert result == "WAIT"
    
    def test_wait_directive_node_visitor_acceptance(self):
        """Test wait directive node accepts visitors."""
        class MockVisitor(ASTVisitor):
            def visit_directive(self, node): pass
            def visit_wait_directive(self, node): 
                return "visited_wait"
            def visit_action(self, node): pass
            def visit_target(self, node): pass
            def visit_prompt_field(self, node): pass
            def visit_param_set(self, node): pass
        
        node = WaitDirectiveNode()
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        assert result == "visited_wait"


class TestDirectiveNode:
    """Test suite for DirectiveNode class."""
    
    def test_directive_node_creation(self):
        """Test creating a directive node."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        param_set = ParamSetNode(
            target=TargetNode(TokenType.FILE, "test.txt"),
            prompt_field=PromptFieldNode("Create this file")
        )
        node = DirectiveNode(action=action, param_sets=[param_set], line=1, column=0)
        
        assert node.action == action
        assert len(node.param_sets) == 1
        assert node.param_sets[0] == param_set
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.DIRECTIVE
    
    def test_directive_node_multiple_param_sets(self):
        """Test creating directive node with multiple param sets."""
        action = ActionNode(TokenType.DELEGATE, "DELEGATE")
        param_sets = [
            ParamSetNode(
                target=TargetNode(TokenType.FILE, "file1.txt"),
                prompt_field=PromptFieldNode("Create file1")
            ),
            ParamSetNode(
                target=TargetNode(TokenType.FILE, "file2.txt"),
                prompt_field=PromptFieldNode("Create file2")
            )
        ]
        node = DirectiveNode(action=action, param_sets=param_sets)
        
        assert len(node.param_sets) == 2
        assert node.param_sets[0].target.name == "file1.txt"
        assert node.param_sets[1].target.name == "file2.txt"
    
    def test_get_first_prompt_with_prompt(self):
        """Test get_first_prompt when first param set has prompt."""
        action = ActionNode(TokenType.DELEGATE, "DELEGATE")
        param_set = ParamSetNode(
            target=TargetNode(TokenType.FILE, "test.txt"),
            prompt_field=PromptFieldNode("Create this file")
        )
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.get_first_prompt()
        assert result == "Create this file"
    
    def test_get_first_prompt_without_prompt(self):
        """Test get_first_prompt when first param set has no prompt."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        param_set = ParamSetNode(target=TargetNode(TokenType.FILE, "test.txt"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.get_first_prompt()
        assert result is None
    
    def test_get_first_prompt_empty_param_sets(self):
        """Test get_first_prompt with empty param sets."""
        action = ActionNode(TokenType.WAIT, "WAIT")
        node = DirectiveNode(action=action, param_sets=[])
        
        result = node.get_first_prompt()
        assert result is None
    
    def test_get_first_next_agent_delegate(self):
        """Test get_first_next_agent for DELEGATE action."""
        action = ActionNode(TokenType.DELEGATE, "DELEGATE")
        param_set = ParamSetNode(target=TargetNode(TokenType.IDENTIFIER, "child_agent"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.get_first_next_agent()
        assert result == "child_agent"
    
    def test_get_first_next_agent_finish(self):
        """Test get_first_next_agent for FINISH action."""
        action = ActionNode(TokenType.FINISH, "FINISH")
        param_set = ParamSetNode(prompt_field=PromptFieldNode("Task completed"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.get_first_next_agent()
        assert result == "PARENT"
    
    def test_get_first_next_agent_other_actions(self):
        """Test get_first_next_agent for other actions."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        param_set = ParamSetNode(target=TargetNode(TokenType.FILE, "test.txt"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.get_first_next_agent()
        assert result == "SELF"
    
    def test_is_child_agent_selection_delegate(self):
        """Test is_child_agent_selection for DELEGATE action."""
        action = ActionNode(TokenType.DELEGATE, "DELEGATE")
        param_set = ParamSetNode(target=TargetNode(TokenType.IDENTIFIER, "child_agent"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.is_child_agent_selection() is True
    
    def test_is_child_agent_selection_other_actions(self):
        """Test is_child_agent_selection for other actions."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        param_set = ParamSetNode(target=TargetNode(TokenType.FILE, "test.txt"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.is_child_agent_selection() is False
    
    def test_is_parent_selection_finish(self):
        """Test is_parent_selection for FINISH action."""
        action = ActionNode(TokenType.FINISH, "FINISH")
        param_set = ParamSetNode(prompt_field=PromptFieldNode("Task completed"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.is_parent_selection() is True
    
    def test_is_parent_selection_other_actions(self):
        """Test is_parent_selection for other actions."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        param_set = ParamSetNode(target=TargetNode(TokenType.FILE, "test.txt"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert node.is_parent_selection() is False
    
    def test_is_delegate_action_true(self):
        """Test is_delegate_action for DELEGATE action."""
        action = ActionNode(TokenType.DELEGATE, "DELEGATE")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_delegate_action() is True
    
    def test_is_delegate_action_false(self):
        """Test is_delegate_action for other actions."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_delegate_action() is False
    
    def test_is_finish_action_true(self):
        """Test is_finish_action for FINISH action."""
        action = ActionNode(TokenType.FINISH, "FINISH")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_finish_action() is True
    
    def test_is_finish_action_false(self):
        """Test is_finish_action for other actions."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        node = DirectiveNode(action=action, param_sets=[])
        
        assert node.is_finish_action() is False
    
    def test_directive_node_representation(self):
        """Test string representation of directive node."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        param_set = ParamSetNode(target=TargetNode(TokenType.FILE, "test.txt"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        expected = "DirectiveNode(ActionNode(TokenType.CREATE, 'CREATE'), [ParamSetNode(TargetNode(TokenType.FILE, 'test.txt'), )])"
        assert repr(node) == expected
    
    def test_directive_node_to_dict(self):
        """Test to_dict method."""
        action = ActionNode(TokenType.DELEGATE, "DELEGATE")
        param_sets = [
            ParamSetNode(
                target=TargetNode(TokenType.FILE, "test.txt"),
                prompt_field=PromptFieldNode("Create this file")
            )
        ]
        node = DirectiveNode(action=action, param_sets=param_sets)
        
        result = node.to_dict()
        
        assert 'action' in result
        assert result['action']['type'] == 'DELEGATE'
        assert result['action']['value'] == 'DELEGATE'
        assert 'param_sets' in result
        assert len(result['param_sets']) == 1
        assert result['param_sets'][0]['target']['name'] == 'test.txt'
    
    def test_directive_node_to_string(self):
        """Test to_string method."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        param_set = ParamSetNode(
            target=TargetNode(TokenType.FILE, "test.txt"),
            prompt_field=PromptFieldNode("Create this file")
        )
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_string()
        
        expected = 'CREATE FILE "test.txt" PROMPT="Create this file"'
        assert result == expected
    
    def test_directive_node_to_string_without_prompt(self):
        """Test to_string method without prompt."""
        action = ActionNode(TokenType.CREATE, "CREATE")
        param_set = ParamSetNode(target=TargetNode(TokenType.FILE, "test.txt"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_string()
        
        expected = 'CREATE FILE "test.txt"'
        assert result == expected
    
    def test_directive_node_visitor_acceptance(self):
        """Test directive node accepts visitors."""
        class MockVisitor(ASTVisitor):
            def visit_directive(self, node): 
                return "visited_directive"
            def visit_wait_directive(self, node): pass
            def visit_action(self, node): pass
            def visit_target(self, node): pass
            def visit_prompt_field(self, node): pass
            def visit_param_set(self, node): pass
        
        action = ActionNode(TokenType.CREATE, "CREATE")
        node = DirectiveNode(action=action, param_sets=[])
        visitor = MockVisitor()
        
        result = node.accept(visitor)
        assert result == "visited_directive"


class TestASTIntegration:
    """Integration tests for AST classes with autonomous agent scenarios."""
    
    def test_hierarchical_delegation_ast(self):
        """Test AST construction for hierarchical delegation scenario."""
        # Create AST for: DELEGATE folder "api" PROMPT="Create API structure"
        action = ActionNode(TokenType.DELEGATE, "DELEGATE")
        target = TargetNode(TokenType.FOLDER, "api")
        prompt = PromptFieldNode("Create API structure")
        param_set = ParamSetNode(target=target, prompt_field=prompt)
        directive_node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert directive_node.is_delegate_action() is True
        assert directive_node.get_first_next_agent() == "api"
        assert directive_node.get_first_prompt() == "Create API structure"
        assert directive_node.to_string() == 'DELEGATE FOLDER "api" PROMPT="Create API structure"'
    
    def test_concurrent_delegation_ast(self):
        """Test AST construction for concurrent delegation."""
        # Create AST for multiple concurrent delegations
        action = ActionNode(TokenType.DELEGATE, "DELEGATE")
        param_sets = [
            ParamSetNode(
                target=TargetNode(TokenType.FILE, "frontend/index.html"),
                prompt_field=PromptFieldNode("Create HTML structure")
            ),
            ParamSetNode(
                target=TargetNode(TokenType.FILE, "frontend/styles.css"),
                prompt_field=PromptFieldNode("Create CSS styles")
            ),
            ParamSetNode(
                target=TargetNode(TokenType.FILE, "frontend/script.js"),
                prompt_field=PromptFieldNode("Create JavaScript functionality")
            )
        ]
        directive_node = DirectiveNode(action=action, param_sets=param_sets)
        
        assert directive_node.is_delegate_action() is True
        assert len(directive_node.param_sets) == 3
        assert all("frontend" in param_set.target.name for param_set in param_sets)
    
    def test_finish_with_readme_ast(self):
        """Test AST construction for finish with README creation."""
        # Create AST for: FINISH PROMPT="Create README and finish"
        action = ActionNode(TokenType.FINISH, "FINISH")
        prompt = PromptFieldNode("Create README and finish")
        param_set = ParamSetNode(prompt_field=prompt)
        directive_node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert directive_node.is_finish_action() is True
        assert directive_node.get_first_next_agent() == "PARENT"
        assert directive_node.get_first_prompt() == "Create README and finish"
        assert directive_node.to_string() == 'FINISH PROMPT="Create README and finish"'
    
    def test_file_operation_ast(self):
        """Test AST construction for file operations."""
        # Create AST for: CREATE file "README.md"
        action = ActionNode(TokenType.CREATE, "CREATE")
        target = TargetNode(TokenType.FILE, "README.md")
        param_set = ParamSetNode(target=target)
        directive_node = DirectiveNode(action=action, param_sets=[param_set])
        
        assert directive_node.is_delegate_action() is False
        assert directive_node.is_finish_action() is False
        assert directive_node.get_first_next_agent() == "SELF"
        assert directive_node.to_string() == 'CREATE FILE "README.md"' 