"""
Comprehensive test suite for the Master Language AST classes.

Tests cover all AST classes and methods in ast.py using partitioning methods to ensure
complete coverage of abstract syntax tree functionality for master agent coordination.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.languages.master_language.ast import (
    # Basic data classes
    Target,
    PromptField,
    EphemeralType,
    SpawnItem,
    
    # Directive classes
    Directive,
    DelegateDirective,
    SpawnDirective,
    FinishDirective,
    ReadDirective,
    WaitDirective,
    RunDirective,
    UpdateDocumentationDirective,
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
    WaitDirectiveNode,
    
    # Grammar imports
    TokenType
)


class TestTarget:
    """Test suite for Target data class."""
    
    def test_target_creation_file(self):
        """Test creating a file target."""
        target = Target(name="test.py", is_folder=False)
        
        assert target.name == "test.py"
        assert target.is_folder is False
        assert str(target) == "file:test.py"
    
    def test_target_creation_folder(self):
        """Test creating a folder target."""
        target = Target(name="src", is_folder=True)
        
        assert target.name == "src"
        assert target.is_folder is True
        assert str(target) == "folder:src"
    
    def test_target_with_path(self):
        """Test creating target with path."""
        target = Target(name="src/components/Button.js", is_folder=False)
        
        assert target.name == "src/components/Button.js"
        assert str(target) == "file:src/components/Button.js"
    
    def test_target_with_complex_folder_name(self):
        """Test creating target with complex folder name."""
        target = Target(name="my-project_v2", is_folder=True)
        
        assert target.name == "my-project_v2"
        assert str(target) == "folder:my-project_v2"


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
        """Test prompt field with complex coordination message."""
        complex_prompt = """System coordination completed successfully!

Major milestones achieved:
1. Root manager agent established connections
2. All subsystem dependencies resolved
3. Performance monitoring agents deployed
4. Documentation updated system-wide

System ready for production deployment."""
        
        prompt = PromptField(value=complex_prompt)
        
        assert prompt.value == complex_prompt
        assert "System coordination completed" in prompt.value
        assert "production deployment" in prompt.value


class TestEphemeralType:
    """Test suite for EphemeralType data class."""
    
    def test_ephemeral_type_creation(self):
        """Test creating an ephemeral type."""
        ephemeral_type = EphemeralType(type_name="tester")
        
        assert ephemeral_type.type_name == "tester"
        assert str(ephemeral_type) == "ephemeral_type:tester"
    
    def test_ephemeral_type_custom(self):
        """Test creating custom ephemeral type."""
        ephemeral_type = EphemeralType(type_name="monitor")
        
        assert ephemeral_type.type_name == "monitor"
        assert str(ephemeral_type) == "ephemeral_type:monitor"


class TestSpawnItem:
    """Test suite for SpawnItem data class."""
    
    def test_spawn_item_creation(self):
        """Test creating a spawn item."""
        ephemeral_type = EphemeralType(type_name="tester")
        prompt = PromptField(value="Monitor system performance")
        spawn_item = SpawnItem(ephemeral_type=ephemeral_type, prompt=prompt)
        
        assert spawn_item.ephemeral_type == ephemeral_type
        assert spawn_item.prompt == prompt
        assert str(spawn_item) == 'ephemeral_type:tester PROMPT="Monitor system performance"'
    
    def test_spawn_item_complex_prompt(self):
        """Test spawn item with complex prompt."""
        ephemeral_type = EphemeralType(type_name="tester")
        complex_prompt = "Analyze system bottlenecks and generate performance report"
        prompt = PromptField(value=complex_prompt)
        spawn_item = SpawnItem(ephemeral_type=ephemeral_type, prompt=prompt)
        
        assert spawn_item.prompt.value == complex_prompt
        assert "Analyze system bottlenecks" in str(spawn_item)


class TestDelegateDirective:
    """Test suite for DelegateDirective class."""
    
    def test_delegate_directive_creation(self):
        """Test creating a DELEGATE directive."""
        prompt = PromptField(value="Create a web application")
        directive = DelegateDirective(prompt=prompt)
        
        assert directive.prompt == prompt
        assert str(directive) == 'DELEGATE PROMPT="Create a web application"'
    
    def test_delegate_directive_execution(self):
        """Test DELEGATE directive execution."""
        prompt = PromptField(value="Build microservices architecture")
        directive = DelegateDirective(prompt=prompt)
        
        context = {}
        result = directive.execute(context)
        
        assert 'delegations' in result
        assert len(result['delegations']) == 1
        assert result['delegations'][0]['target'] == 'root'
        assert result['delegations'][0]['prompt'] == "Build microservices architecture"
    
    def test_delegate_directive_context_preservation(self):
        """Test that DELEGATE directive preserves existing context."""
        prompt = PromptField(value="New task")
        directive = DelegateDirective(prompt=prompt)
        
        context = {'existing_key': 'existing_value', 'delegations': [{'target': 'root', 'prompt': 'old task'}]}
        result = directive.execute(context)
        
        assert result['existing_key'] == 'existing_value'
        assert len(result['delegations']) == 2
        assert result['delegations'][0]['prompt'] == 'old task'
        assert result['delegations'][1]['prompt'] == 'New task'


class TestSpawnDirective:
    """Test suite for SpawnDirective class."""
    
    def test_spawn_directive_single_item(self):
        """Test creating a SPAWN directive with single item."""
        ephemeral_type = EphemeralType(type_name="tester")
        prompt = PromptField(value="Monitor system resources")
        spawn_item = SpawnItem(ephemeral_type=ephemeral_type, prompt=prompt)
        directive = SpawnDirective(items=[spawn_item])
        
        assert len(directive.items) == 1
        assert directive.items[0] == spawn_item
        assert str(directive) == 'SPAWN ephemeral_type:tester PROMPT="Monitor system resources"'
    
    def test_spawn_directive_multiple_items(self):
        """Test creating a SPAWN directive with multiple items."""
        item1 = SpawnItem(
            ephemeral_type=EphemeralType(type_name="tester"),
            prompt=PromptField(value="Performance monitoring")
        )
        item2 = SpawnItem(
            ephemeral_type=EphemeralType(type_name="tester"),
            prompt=PromptField(value="Security analysis")
        )
        directive = SpawnDirective(items=[item1, item2])
        
        assert len(directive.items) == 2
        assert "Performance monitoring" in str(directive)
        assert "Security analysis" in str(directive)
    
    def test_spawn_directive_execution(self):
        """Test SPAWN directive execution."""
        item1 = SpawnItem(
            ephemeral_type=EphemeralType(type_name="tester"),
            prompt=PromptField(value="Task 1")
        )
        item2 = SpawnItem(
            ephemeral_type=EphemeralType(type_name="tester"),
            prompt=PromptField(value="Task 2")
        )
        directive = SpawnDirective(items=[item1, item2])
        
        context = {}
        result = directive.execute(context)
        
        assert 'spawns' in result
        assert len(result['spawns']) == 2
        assert result['spawns'][0]['ephemeral_type'] == 'tester'
        assert result['spawns'][0]['prompt'] == 'Task 1'
        assert result['spawns'][1]['ephemeral_type'] == 'tester'
        assert result['spawns'][1]['prompt'] == 'Task 2'


class TestReadDirective:
    """Test suite for ReadDirective class."""
    
    def test_read_directive_single_target(self):
        """Test creating a READ directive with single target."""
        target = Target(name="big_picture.md", is_folder=False)
        directive = ReadDirective(targets=[target])
        
        assert len(directive.targets) == 1
        assert directive.targets[0] == target
        assert str(directive) == 'READ file:big_picture.md'
    
    def test_read_directive_multiple_targets(self):
        """Test creating a READ directive with multiple targets."""
        file_target = Target(name="config.py", is_folder=False)
        folder_target = Target(name="src", is_folder=True)
        directive = ReadDirective(targets=[file_target, folder_target])
        
        assert len(directive.targets) == 2
        assert directive.targets[0] == file_target
        assert directive.targets[1] == folder_target
        assert "file:config.py" in str(directive)
        assert "folder:src" in str(directive)
    
    def test_read_directive_execution(self):
        """Test READ directive execution."""
        file_target = Target(name="README.md", is_folder=False)
        folder_target = Target(name="docs", is_folder=True)
        directive = ReadDirective(targets=[file_target, folder_target])
        
        context = {}
        result = directive.execute(context)
        
        assert 'reads' in result
        assert len(result['reads']) == 2
        assert result['reads'][0]['target'] == 'README.md'
        assert result['reads'][0]['is_folder'] is False
        assert result['reads'][1]['target'] == 'docs'
        assert result['reads'][1]['is_folder'] is True


class TestFinishDirective:
    """Test suite for FinishDirective class."""
    
    def test_finish_directive_creation(self):
        """Test creating a FINISH directive."""
        prompt = PromptField(value="System coordination completed")
        directive = FinishDirective(prompt=prompt)
        
        assert directive.prompt == prompt
        assert str(directive) == 'FINISH PROMPT="System coordination completed"'
    
    def test_finish_directive_execution(self):
        """Test FINISH directive execution."""
        prompt = PromptField(value="All tasks completed")
        directive = FinishDirective(prompt=prompt)
        
        context = {}
        result = directive.execute(context)
        
        assert result['finished'] is True
        assert result['completion_prompt'] == "All tasks completed"
    
    def test_finish_directive_complex_message(self):
        """Test FINISH directive with complex completion message."""
        complex_message = """Master coordination phase completed successfully!

System-wide accomplishments:
- All subsystems initialized and operational
- Cross-system communication established
- Performance monitoring deployed
- Documentation updated across all modules

System ready for production deployment and monitoring."""
        
        prompt = PromptField(value=complex_message)
        directive = FinishDirective(prompt=prompt)
        
        assert directive.prompt.value == complex_message
        assert "Master coordination phase completed" in str(directive)


class TestWaitDirective:
    """Test suite for WaitDirective class."""
    
    def test_wait_directive_creation(self):
        """Test creating a WAIT directive."""
        directive = WaitDirective()
        
        assert str(directive) == "WAIT"
    
    def test_wait_directive_execution(self):
        """Test WAIT directive execution."""
        directive = WaitDirective()
        
        context = {}
        result = directive.execute(context)
        
        assert result['waiting'] is True


class TestRunDirective:
    """Test suite for RunDirective class."""
    
    def test_run_directive_creation(self):
        """Test creating a RUN directive."""
        directive = RunDirective(command="find . -name '*.py' | wc -l")
        
        assert directive.command == "find . -name '*.py' | wc -l"
        assert str(directive) == 'RUN "find . -name \'*.py\' | wc -l"'
    
    def test_run_directive_execution(self):
        """Test RUN directive execution."""
        directive = RunDirective(command="echo 'System status check'")
        
        context = {}
        result = directive.execute(context)
        
        assert 'commands' in result
        assert len(result['commands']) == 1
        assert result['commands'][0]['command'] == "echo 'System status check'"
        assert result['commands'][0]['status'] == 'pending'


class TestUpdateDocumentationDirective:
    """Test suite for UpdateDocumentationDirective class."""
    
    def test_update_documentation_directive_creation(self):
        """Test creating an UPDATE_DOCUMENTATION directive."""
        content = "System architecture now supports microservices"
        directive = UpdateDocumentationDirective(content=content)
        
        assert directive.content == content
        assert str(directive) == 'UPDATE_DOCUMENTATION CONTENT="System architecture now supports microservices"'
    
    def test_update_documentation_directive_execution(self):
        """Test UPDATE_DOCUMENTATION directive execution."""
        content = "Updated system documentation with new features"
        directive = UpdateDocumentationDirective(content=content)
        
        context = {}
        result = directive.execute(context)
        
        assert 'documentation_updates' in result
        assert len(result['documentation_updates']) == 1
        assert result['documentation_updates'][0]['content'] == content
        assert result['documentation_updates'][0]['status'] == 'pending'


class TestActionNode:
    """Test suite for ActionNode class."""
    
    def test_action_node_creation(self):
        """Test creating an ActionNode."""
        node = ActionNode(action_type=TokenType.DELEGATE, value="DELEGATE", line=1, column=0)
        
        assert node.action_type == TokenType.DELEGATE
        assert node.value == "DELEGATE"
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.ACTION
    
    def test_action_node_representation(self):
        """Test ActionNode string representation."""
        node = ActionNode(action_type=TokenType.READ, value="READ")
        
        assert "ActionNode" in repr(node)
        assert "READ" in repr(node)
    
    def test_action_node_visitor_acceptance(self):
        """Test ActionNode visitor acceptance."""
        class MockVisitor(ASTVisitor):
            def visit_action(self, node): 
                return f"visited_{node.value}"
            def visit_directive(self, node): pass
            def visit_wait_directive(self, node): pass
            def visit_target(self, node): pass
            def visit_prompt_field(self, node): pass
            def visit_param_set(self, node): pass
        
        node = ActionNode(action_type=TokenType.SPAWN, value="SPAWN")
        visitor = MockVisitor()
        result = node.accept(visitor)
        
        assert result == "visited_SPAWN"


class TestTargetNode:
    """Test suite for TargetNode class."""
    
    def test_target_node_creation(self):
        """Test creating a TargetNode."""
        node = TargetNode(target_type=TokenType.FILE, name="config.py", line=1, column=5)
        
        assert node.target_type == TokenType.FILE
        assert node.name == "config.py"
        assert node.line == 1
        assert node.column == 5
        assert node.node_type == NodeType.TARGET
    
    def test_target_node_folder(self):
        """Test creating a folder TargetNode."""
        node = TargetNode(target_type=TokenType.FOLDER, name="src")
        
        assert node.target_type == TokenType.FOLDER
        assert node.name == "src"
    
    def test_target_node_representation(self):
        """Test TargetNode string representation."""
        node = TargetNode(target_type=TokenType.FILE, name="app.js")
        
        assert "TargetNode" in repr(node)
        assert "FILE" in repr(node)
        assert "app.js" in repr(node)


class TestPromptFieldNode:
    """Test suite for PromptFieldNode class."""
    
    def test_prompt_field_node_creation(self):
        """Test creating a PromptFieldNode."""
        node = PromptFieldNode(prompt="System coordination task", line=1, column=10)
        
        assert node.prompt == "System coordination task"
        assert node.line == 1
        assert node.column == 10
        assert node.node_type == NodeType.PROMPT_FIELD
    
    def test_prompt_field_node_representation(self):
        """Test PromptFieldNode string representation."""
        node = PromptFieldNode(prompt="Master task completed")
        
        assert "PromptFieldNode" in repr(node)
        assert "Master task completed" in repr(node)


class TestWaitDirectiveNode:
    """Test suite for WaitDirectiveNode class."""
    
    def test_wait_directive_node_creation(self):
        """Test creating a WaitDirectiveNode."""
        node = WaitDirectiveNode(line=1, column=0)
        
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.WAIT_DIRECTIVE
    
    def test_wait_directive_node_to_dict(self):
        """Test converting WaitDirectiveNode to dictionary."""
        node = WaitDirectiveNode()
        
        result = node.to_dict()
        
        assert result['type'] == 'WAIT'
    
    def test_wait_directive_node_to_string(self):
        """Test converting WaitDirectiveNode to string."""
        node = WaitDirectiveNode()
        
        result = node.to_string()
        
        assert result == "WAIT"


class TestParamSetNode:
    """Test suite for ParamSetNode class."""
    
    def test_param_set_node_with_target_and_prompt(self):
        """Test ParamSetNode with target and prompt field."""
        target = TargetNode(target_type=TokenType.FILE, name="test.py")
        prompt_field = PromptFieldNode(prompt="Complete the coordination task")
        node = ParamSetNode(target=target, prompt_field=prompt_field, line=1, column=0)
        
        assert node.target == target
        assert node.prompt_field == prompt_field
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.PARAM_SET
    
    def test_get_prompt_with_prompt_field(self):
        """Test get_prompt when prompt field is present."""
        prompt_field = PromptFieldNode(prompt="Master coordination task")
        node = ParamSetNode(prompt_field=prompt_field)
        
        assert node.get_prompt() == "Master coordination task"
    
    def test_get_prompt_without_prompt_field(self):
        """Test get_prompt when prompt field is not present."""
        node = ParamSetNode()
        
        assert node.get_prompt() is None
    
    def test_get_next_agent_delegate(self):
        """Test get_next_agent for DELEGATE action."""
        target = TargetNode(target_type=TokenType.IDENTIFIER, name="root")
        node = ParamSetNode(target=target)
        
        result = node.get_next_agent(TokenType.DELEGATE)
        
        assert result == "root"
    
    def test_get_next_agent_finish(self):
        """Test get_next_agent for FINISH action."""
        node = ParamSetNode()
        
        result = node.get_next_agent(TokenType.FINISH)
        
        assert result == "PARENT"
    
    def test_get_next_agent_read(self):
        """Test get_next_agent for READ action."""
        node = ParamSetNode()
        
        result = node.get_next_agent(TokenType.READ)
        
        assert result == "SELF"
    
    def test_is_child_agent_selection_delegate(self):
        """Test is_child_agent_selection for DELEGATE action."""
        node = ParamSetNode()
        
        result = node.is_child_agent_selection(TokenType.DELEGATE)
        
        assert result is True
    
    def test_is_child_agent_selection_other(self):
        """Test is_child_agent_selection for non-DELEGATE action."""
        node = ParamSetNode()
        
        result = node.is_child_agent_selection(TokenType.READ)
        
        assert result is False
    
    def test_is_parent_selection_finish(self):
        """Test is_parent_selection for FINISH action."""
        node = ParamSetNode()
        
        result = node.is_parent_selection(TokenType.FINISH)
        
        assert result is True
    
    def test_is_parent_selection_other(self):
        """Test is_parent_selection for non-FINISH action."""
        node = ParamSetNode()
        
        result = node.is_parent_selection(TokenType.DELEGATE)
        
        assert result is False
    
    def test_param_set_node_to_dict(self):
        """Test converting ParamSetNode to dictionary."""
        target = TargetNode(target_type=TokenType.FILE, name="config.py")
        prompt_field = PromptFieldNode(prompt="System task")
        node = ParamSetNode(target=target, prompt_field=prompt_field)
        
        result = node.to_dict()
        
        assert result['target']['type'] == 'FILE'
        assert result['target']['name'] == 'config.py'
        assert result['prompt_field']['prompt'] == 'System task'


class TestDirectiveNode:
    """Test suite for DirectiveNode class."""
    
    def test_directive_node_creation(self):
        """Test creating a DirectiveNode."""
        action = ActionNode(action_type=TokenType.DELEGATE, value="DELEGATE")
        param_set = ParamSetNode(prompt_field=PromptFieldNode(prompt="Master task"))
        node = DirectiveNode(action=action, param_sets=[param_set], line=1, column=0)
        
        assert node.action == action
        assert len(node.param_sets) == 1
        assert node.param_sets[0] == param_set
        assert node.line == 1
        assert node.column == 0
        assert node.node_type == NodeType.DIRECTIVE
    
    def test_get_first_prompt_with_prompt(self):
        """Test get_first_prompt when prompt is present."""
        action = ActionNode(action_type=TokenType.DELEGATE, value="DELEGATE")
        param_set = ParamSetNode(prompt_field=PromptFieldNode(prompt="System coordination"))
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.get_first_prompt()
        
        assert result == "System coordination"
    
    def test_get_first_prompt_without_prompt(self):
        """Test get_first_prompt when no prompt is present."""
        action = ActionNode(action_type=TokenType.WAIT, value="WAIT")
        node = DirectiveNode(action=action, param_sets=[])
        
        result = node.get_first_prompt()
        
        assert result is None
    
    def test_is_delegate_action_true(self):
        """Test is_delegate_action when action is DELEGATE."""
        action = ActionNode(action_type=TokenType.DELEGATE, value="DELEGATE")
        node = DirectiveNode(action=action, param_sets=[])
        
        result = node.is_delegate_action()
        
        assert result is True
    
    def test_is_delegate_action_false(self):
        """Test is_delegate_action when action is not DELEGATE."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        node = DirectiveNode(action=action, param_sets=[])
        
        result = node.is_delegate_action()
        
        assert result is False
    
    def test_is_finish_action_true(self):
        """Test is_finish_action when action is FINISH."""
        action = ActionNode(action_type=TokenType.FINISH, value="FINISH")
        node = DirectiveNode(action=action, param_sets=[])
        
        result = node.is_finish_action()
        
        assert result is True
    
    def test_is_finish_action_false(self):
        """Test is_finish_action when action is not FINISH."""
        action = ActionNode(action_type=TokenType.DELEGATE, value="DELEGATE")
        node = DirectiveNode(action=action, param_sets=[])
        
        result = node.is_finish_action()
        
        assert result is False
    
    def test_directive_node_to_dict(self):
        """Test converting DirectiveNode to dictionary."""
        action = ActionNode(action_type=TokenType.DELEGATE, value="DELEGATE")
        target = TargetNode(target_type=TokenType.IDENTIFIER, name="root")
        prompt_field = PromptFieldNode(prompt="Master coordination")
        param_set = ParamSetNode(target=target, prompt_field=prompt_field)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_dict()
        
        assert result['action']['type'] == 'DELEGATE'
        assert result['action']['value'] == 'DELEGATE'
        assert len(result['param_sets']) == 1
        assert result['param_sets'][0]['target']['name'] == 'root'
        assert result['param_sets'][0]['prompt_field']['prompt'] == 'Master coordination'
    
    def test_directive_node_to_string(self):
        """Test converting DirectiveNode to string."""
        action = ActionNode(action_type=TokenType.READ, value="READ")
        target = TargetNode(target_type=TokenType.FILE, name="config.py")
        param_set = ParamSetNode(target=target)
        node = DirectiveNode(action=action, param_sets=[param_set])
        
        result = node.to_string()
        
        assert result == 'READ FILE "config.py"'


class TestMasterLanguageIntegration:
    """Test suite for integrated Master Language AST functionality."""
    
    def test_complete_delegate_directive_workflow(self):
        """Test complete workflow for DELEGATE directive."""
        # Create directive
        prompt = PromptField(value="Orchestrate microservices deployment")
        directive = DelegateDirective(prompt=prompt)
        
        # Execute directive
        context = {}
        result = directive.execute(context)
        
        # Verify results
        assert 'delegations' in result
        assert len(result['delegations']) == 1
        assert result['delegations'][0]['target'] == 'root'
        assert result['delegations'][0]['prompt'] == "Orchestrate microservices deployment"
        assert str(directive) == 'DELEGATE PROMPT="Orchestrate microservices deployment"'
    
    def test_complete_spawn_directive_workflow(self):
        """Test complete workflow for SPAWN directive."""
        # Create spawn items
        item1 = SpawnItem(
            ephemeral_type=EphemeralType(type_name="tester"),
            prompt=PromptField(value="Performance monitoring")
        )
        item2 = SpawnItem(
            ephemeral_type=EphemeralType(type_name="tester"),
            prompt=PromptField(value="Security analysis")
        )
        
        # Create directive
        directive = SpawnDirective(items=[item1, item2])
        
        # Execute directive
        context = {}
        result = directive.execute(context)
        
        # Verify results
        assert 'spawns' in result
        assert len(result['spawns']) == 2
        assert result['spawns'][0]['ephemeral_type'] == 'tester'
        assert result['spawns'][0]['prompt'] == 'Performance monitoring'
        assert result['spawns'][1]['ephemeral_type'] == 'tester'
        assert result['spawns'][1]['prompt'] == 'Security analysis'
    
    def test_complete_read_directive_workflow(self):
        """Test complete workflow for READ directive."""
        # Create targets
        file_target = Target(name="big_picture.md", is_folder=False)
        folder_target = Target(name="src", is_folder=True)
        
        # Create directive
        directive = ReadDirective(targets=[file_target, folder_target])
        
        # Execute directive
        context = {}
        result = directive.execute(context)
        
        # Verify results
        assert 'reads' in result
        assert len(result['reads']) == 2
        assert result['reads'][0]['target'] == 'big_picture.md'
        assert result['reads'][0]['is_folder'] is False
        assert result['reads'][1]['target'] == 'src'
        assert result['reads'][1]['is_folder'] is True
    
    def test_directive_workflow_sequence(self):
        """Test executing a sequence of master directives."""
        # Initial context
        context = {}
        
        # 1. Read system documentation
        read_directive = ReadDirective(targets=[Target(name="big_picture.md", is_folder=False)])
        context = read_directive.execute(context)
        
        # 2. Delegate main task
        delegate_directive = DelegateDirective(prompt=PromptField(value="Build the system"))
        context = delegate_directive.execute(context)
        
        # 3. Spawn monitoring
        spawn_directive = SpawnDirective(items=[
            SpawnItem(
                ephemeral_type=EphemeralType(type_name="tester"),
                prompt=PromptField(value="Monitor progress")
            )
        ])
        context = spawn_directive.execute(context)
        
        # 4. Wait for completion
        wait_directive = WaitDirective()
        context = wait_directive.execute(context)
        
        # 5. Finish coordination
        finish_directive = FinishDirective(prompt=PromptField(value="System coordination complete"))
        context = finish_directive.execute(context)
        
        # Verify final context
        assert 'reads' in context
        assert 'delegations' in context
        assert 'spawns' in context
        assert context['waiting'] is True
        assert context['finished'] is True
        assert context['completion_prompt'] == "System coordination complete"
        assert len(context['reads']) == 1
        assert len(context['delegations']) == 1
        assert len(context['spawns']) == 1 