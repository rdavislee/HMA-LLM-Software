"""
Abstract Syntax Tree classes for the Master Language.
These classes represent the parsed structure of master agent directives.
Based on the manager language but simplified for top-level coordination.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class TokenType(Enum):
    READ = "READ"
    DELEGATE = "DELEGATE"
    SPAWN = "SPAWN"
    FINISH = "FINISH"
    WAIT = "WAIT"
    UPDATE_DOCUMENTATION = "UPDATE_DOCUMENTATION"
    RUN = "RUN"
    MESSAGE = "MESSAGE"
    FILE = "FILE"
    FOLDER = "FOLDER"
    IDENTIFIER = "IDENTIFIER"
    TESTER = "TESTER"


class NodeType(Enum):
    """Types of AST nodes."""
    DIRECTIVE = "DIRECTIVE"
    ACTION = "ACTION"
    TARGET = "TARGET"
    PROMPT_FIELD = "PROMPT_FIELD"
    PARAM_SET = "PARAM_SET"
    WAIT_DIRECTIVE = "WAIT_DIRECTIVE"


class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    def __init__(self, node_type: NodeType):
        self.node_type = node_type
        self.line: int = 0
        self.column: int = 0
    
    @abstractmethod
    def accept(self, visitor: 'ASTVisitor') -> Any:
        """Accept a visitor for traversal."""
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"


class ASTVisitor(ABC):
    """Visitor pattern for AST traversal."""
    
    @abstractmethod
    def visit_directive(self, node: 'DirectiveNode') -> Any:
        pass
    
    @abstractmethod
    def visit_wait_directive(self, node: 'WaitDirectiveNode') -> Any:
        pass
    
    @abstractmethod
    def visit_action(self, node: 'ActionNode') -> Any:
        pass
    
    @abstractmethod
    def visit_target(self, node: 'TargetNode') -> Any:
        pass
    
    @abstractmethod
    def visit_prompt_field(self, node: 'PromptFieldNode') -> Any:
        pass
    
    @abstractmethod
    def visit_param_set(self, node: 'ParamSetNode') -> Any:
        pass


@dataclass
class Target:
    """Represents a file or folder target."""
    name: str
    is_folder: bool = False
    
    def __str__(self) -> str:
        return f"{'folder' if self.is_folder else 'file'}:{self.name}"


@dataclass
class EphemeralType:
    """Represents an ephemeral agent type."""
    type_name: str
    
    def __str__(self) -> str:
        return f"ephemeral_type:{self.type_name}"


@dataclass
class PromptField:
    """Represents a prompt field with a string value."""
    value: str
    
    def __str__(self) -> str:
        return f'PROMPT="{self.value}"'


@dataclass
class SpawnItem:
    """Represents a single spawn item with ephemeral type and prompt."""
    ephemeral_type: EphemeralType
    prompt: PromptField
    
    def __str__(self) -> str:
        return f"{self.ephemeral_type} {self.prompt}"


class Directive(ABC):
    """Base class for all master language directives."""
    
    @abstractmethod
    def execute(self, context: dict) -> dict:
        """Execute this directive and return updated context."""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """Return string representation of this directive."""
        pass


@dataclass
class DelegateDirective(Directive):
    """Represents a DELEGATE directive (no target needed - always delegates to root agent)."""
    prompt: PromptField
    
    def execute(self, context: dict) -> dict:
        """Execute delegate directive by adding delegation task to context."""
        if 'delegations' not in context:
            context['delegations'] = []
        
        context['delegations'].append({
            'target': 'root',  # Always delegates to root agent
            'prompt': self.prompt.value
        })
        
        return context
    
    def __str__(self) -> str:
        return f"DELEGATE {self.prompt}"


@dataclass
class SpawnDirective(Directive):
    """Represents a SPAWN directive for ephemeral agents."""
    items: List[SpawnItem]
    
    def execute(self, context: dict) -> dict:
        """Execute spawn directive by adding spawn tasks to context."""
        if 'spawns' not in context:
            context['spawns'] = []
        
        for item in self.items:
            context['spawns'].append({
                'ephemeral_type': item.ephemeral_type.type_name,
                'prompt': item.prompt.value
            })
        
        return context
    
    def __str__(self) -> str:
        items_str = ", ".join(str(item) for item in self.items)
        return f"SPAWN {items_str}"


@dataclass
class FinishDirective(Directive):
    """Represents a FINISH directive."""
    prompt: PromptField
    
    def execute(self, context: dict) -> dict:
        """Execute finish directive by setting completion status."""
        context['finished'] = True
        context['completion_prompt'] = self.prompt.value
        return context
    
    def __str__(self) -> str:
        return f"FINISH {self.prompt}"


@dataclass
class ReadDirective(Directive):
    """Represents a READ directive (only action directive available for master)."""
    targets: List[Target]
    
    def execute(self, context: dict) -> dict:
        """Execute read directive by adding read actions to context."""
        if 'reads' not in context:
            context['reads'] = []
        
        for target in self.targets:
            context['reads'].append({
                'target': target.name,
                'is_folder': target.is_folder
            })
        
        return context
    
    def __str__(self) -> str:
        targets_str = ", ".join(str(target) for target in self.targets)
        return f"READ {targets_str}"


@dataclass
class WaitDirective(Directive):
    """Represents a WAIT directive."""
    
    def execute(self, context: dict) -> dict:
        """Execute wait directive by setting wait status."""
        context['waiting'] = True
        return context
    
    def __str__(self) -> str:
        return "WAIT"


@dataclass
class RunDirective(Directive):
    """Represents a RUN directive for executing command prompt commands."""
    command: str
    
    def execute(self, context: dict) -> dict:
        """Execute run directive by adding command execution to context."""
        if 'commands' not in context:
            context['commands'] = []
        
        context['commands'].append({
            'command': self.command,
            'status': 'pending'
        })
        
        return context
    
    def __str__(self) -> str:
        return f'RUN "{self.command}"'


@dataclass
class UpdateDocumentationDirective(Directive):
    """Represents an UPDATE_DOCUMENTATION directive for updating master's documentation."""
    content: str
    
    def execute(self, context: dict) -> dict:
        """Execute update documentation directive by adding documentation update to context."""
        if 'documentation_updates' not in context:
            context['documentation_updates'] = []
        
        context['documentation_updates'].append({
            'content': self.content,
            'status': 'pending'
        })
        
        return context
    
    def __str__(self) -> str:
        return f'UPDATE_DOCUMENTATION CONTENT="{self.content}"'


@dataclass
class MessageDirective(Directive):
    """Represents a MESSAGE directive for sending regular messages to human during conversation."""
    prompt: PromptField
    
    def execute(self, context: dict) -> dict:
        """Execute message directive by adding message to context."""
        if 'messages' not in context:
            context['messages'] = []
        
        context['messages'].append({
            'message': self.prompt.value,
            'status': 'pending'
        })
        
        return context
    
    def __str__(self) -> str:
        return f"MESSAGE {self.prompt}"


# Type alias for any directive
DirectiveType = Union[DelegateDirective, SpawnDirective, FinishDirective, ReadDirective, WaitDirective, RunDirective, UpdateDocumentationDirective, MessageDirective]


@dataclass
class ActionNode(ASTNode):
    """Represents an action in a directive (READ, DELEGATE, FINISH)."""
    
    action_type: TokenType
    value: str
    
    def __init__(self, action_type: TokenType, value: str, line: int = 0, column: int = 0):
        super().__init__(NodeType.ACTION)
        self.action_type = action_type
        self.value = value
        self.line = line
        self.column = column
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_action(self)
    
    def __repr__(self):
        return f"ActionNode({self.action_type}, '{self.value}')"


@dataclass
class TargetNode(ASTNode):
    """Represents a target in a directive (FILE, FOLDER, or child agent name)."""
    
    target_type: TokenType  # FILE, FOLDER, or IDENTIFIER
    name: str  # The name/identifier of the target
    
    def __init__(self, target_type: TokenType, name: str, line: int = 0, column: int = 0):
        super().__init__(NodeType.TARGET)
        self.target_type = target_type
        self.name = name
        self.line = line
        self.column = column
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_target(self)
    
    def __repr__(self):
        return f"TargetNode({self.target_type}, '{self.name}')"


@dataclass
class PromptFieldNode(ASTNode):
    """Represents a prompt field for agent communication."""
    
    prompt: str  # The prompt message
    
    def __init__(self, prompt: str, line: int = 0, column: int = 0):
        super().__init__(NodeType.PROMPT_FIELD)
        self.prompt = prompt
        self.line = line
        self.column = column
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_prompt_field(self)
    
    def __repr__(self):
        return f"PromptFieldNode('{self.prompt}')"


@dataclass
class ParamSetNode(ASTNode):
    """Represents a parameter set: TARGET [PROMPT_FIELD] (agent selection is implicit)."""
    
    target: Optional[TargetNode] = None  # None for FINISH action
    prompt_field: Optional[PromptFieldNode] = None
    
    def __init__(self, target: Optional[TargetNode] = None, prompt_field: Optional[PromptFieldNode] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.PARAM_SET)
        self.target = target
        self.prompt_field = prompt_field
        self.line = line
        self.column = column
    
    def get_prompt(self) -> Optional[str]:
        """Get the prompt message if present."""
        if self.prompt_field:
            return self.prompt_field.prompt
        return None
    
    def get_next_agent(self, action_type: TokenType) -> str:
        """Get the next agent based on implicit agent selection rules."""
        if action_type == TokenType.FINISH:
            return "PARENT"
        elif action_type == TokenType.DELEGATE and self.target:
            return self.target.name  # Child agent name
        else:
            return "SELF"  # READ
    
    def is_child_agent_selection(self, action_type: TokenType) -> bool:
        """Check if the agent selection is a child agent."""
        return action_type == TokenType.DELEGATE
    
    def is_parent_selection(self, action_type: TokenType) -> bool:
        """Check if the agent selection is PARENT."""
        return action_type == TokenType.FINISH
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_param_set(self)
    
    def __repr__(self):
        target_str = f"{self.target}, " if self.target else ""
        prompt_str = f"{self.prompt_field}" if self.prompt_field else ""
        return f"ParamSetNode({target_str}{prompt_str})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the parameter set to a dictionary representation."""
        result = {}
        
        if self.target:
            result['target'] = {
                'type': self.target.target_type.value,
                'name': self.target.name
            }
        
        if self.prompt_field:
            result['prompt_field'] = {
                'prompt': self.prompt_field.prompt
            }
        
        return result


@dataclass
class WaitDirectiveNode(ASTNode):
    """Represents a WAIT directive that waits for child agents to complete."""
    
    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(NodeType.WAIT_DIRECTIVE)
        self.line = line
        self.column = column
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_wait_directive(self)
    
    def __repr__(self):
        return "WaitDirectiveNode()"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the wait directive to a dictionary representation."""
        return {
            'type': 'WAIT'
        }
    
    def to_string(self) -> str:
        """Convert the wait directive back to a string representation."""
        return "WAIT"


@dataclass
class DirectiveNode(ASTNode):
    """Represents a complete master directive with parameter sets."""
    
    action: ActionNode
    param_sets: List[ParamSetNode]
    
    def __init__(self, action: ActionNode, param_sets: List[ParamSetNode], line: int = 0, column: int = 0):
        super().__init__(NodeType.DIRECTIVE)
        self.action = action
        self.param_sets = param_sets
        self.line = line
        self.column = column
    
    def get_first_prompt(self) -> Optional[str]:
        """Get the prompt message from the first parameter set if present."""
        if self.param_sets and self.param_sets[0]:
            return self.param_sets[0].get_prompt()
        return None
    
    def get_first_next_agent(self) -> str:
        """Get the next agent from the first parameter set based on implicit rules."""
        if self.param_sets and self.param_sets[0]:
            return self.param_sets[0].get_next_agent(self.action.action_type)
        return "SELF"  # Default fallback
    
    def is_child_agent_selection(self) -> bool:
        """Check if the first parameter set has a child agent selection."""
        if self.param_sets and self.param_sets[0]:
            return self.param_sets[0].is_child_agent_selection(self.action.action_type)
        return False
    
    def is_parent_selection(self) -> bool:
        """Check if the first parameter set has a PARENT selection."""
        if self.param_sets and self.param_sets[0]:
            return self.param_sets[0].is_parent_selection(self.action.action_type)
        return False
    
    def is_delegate_action(self) -> bool:
        """Check if this is a DELEGATE action."""
        return self.action.action_type == TokenType.DELEGATE
    
    def is_finish_action(self) -> bool:
        """Check if this is a FINISH action."""
        return self.action.action_type == TokenType.FINISH
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_directive(self)
    
    def __repr__(self):
        param_str = ", ".join([str(param) for param in self.param_sets])
        return f"DirectiveNode({self.action}, [{param_str}])"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the directive to a dictionary representation."""
        result = {
            'action': {
                'type': self.action.action_type.value,
                'value': self.action.value
            },
            'param_sets': [param_set.to_dict() for param_set in self.param_sets]
        }
        return result
    
    def to_string(self) -> str:
        """Convert the directive back to a string representation."""
        directive_str = self.action.value
        
        for param_set in self.param_sets:
            if param_set.target:
                directive_str += f" {param_set.target.target_type.value} \"{param_set.target.name}\""
            
            if param_set.prompt_field:
                directive_str += f' PROMPT="{param_set.prompt_field.prompt}"'
        
        return directive_str 