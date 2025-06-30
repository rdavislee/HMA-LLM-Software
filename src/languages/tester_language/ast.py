"""
Abstract Syntax Tree classes for the Tester Language.
These classes represent the parsed structure of tester agent directives.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class TokenType(Enum):
    READ = "READ"
    RUN = "RUN"
    CHANGE = "CHANGE"
    FINISH = "FINISH"
    FILE = "FILE"
    IDENTIFIER = "IDENTIFIER"


class NodeType(Enum):
    """Types of AST nodes."""
    DIRECTIVE = "DIRECTIVE"
    ACTION = "ACTION"
    TARGET = "TARGET"
    PROMPT_FIELD = "PROMPT_FIELD"
    PARAM_SET = "PARAM_SET"


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
    """Represents a file target."""
    name: str
    
    def __str__(self) -> str:
        return f"file:{self.name}"


@dataclass
class PromptField:
    """Represents a prompt field with a string value."""
    value: str
    
    def __str__(self) -> str:
        return f'PROMPT="{self.value}"'


class Directive(ABC):
    """Base class for all tester language directives."""
    
    @abstractmethod
    def execute(self, context: dict) -> dict:
        """Execute this directive and return updated context."""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """Return string representation of this directive."""
        pass


@dataclass
class ReadDirective(Directive):
    """Represents a READ directive."""
    filename: str
    
    def execute(self, context: dict) -> dict:
        """Execute read directive by adding file read action to context."""
        if 'reads' not in context:
            context['reads'] = []
        
        context['reads'].append({
            'filename': self.filename,
            'status': 'pending'
        })
        
        return context
    
    def __str__(self) -> str:
        return f'READ "{self.filename}"'


@dataclass
class RunDirective(Directive):
    """Represents a RUN directive."""
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
class ChangeDirective(Directive):
    """Represents a CHANGE directive for modifying the tester's scratch pad."""
    content: str
    
    def execute(self, context: dict) -> dict:
        """Execute change directive by adding scratch pad change action to context."""
        if 'changes' not in context:
            context['changes'] = []
        
        context['changes'].append({
            'content': self.content,
            'status': 'pending'
        })
        
        return context
    
    def __str__(self) -> str:
        if len(self.content) <= 50:
            return f'CHANGE CONTENT="{self.content}"'
        else:
            return f'CHANGE CONTENT="{self.content[:50]}..."'


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


# Type alias for all directive types
DirectiveType = Union[ReadDirective, RunDirective, ChangeDirective, FinishDirective]


@dataclass
class ActionNode(ASTNode):
    """Represents an action in a directive (READ, RUN, CHANGE, FINISH)."""
    
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
    """Represents a target in a directive (filename)."""
    
    target_type: TokenType  # FILE or IDENTIFIER
    name: str  # The filename
    
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
    """Represents a parameter set for directives."""
    
    target: Optional[TargetNode] = None
    prompt_field: Optional[PromptFieldNode] = None
    content: Optional[str] = None
    
    def __init__(self, target: Optional[TargetNode] = None, prompt_field: Optional[PromptFieldNode] = None, content: Optional[str] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.PARAM_SET)
        self.target = target
        self.prompt_field = prompt_field
        self.content = content
        self.line = line
        self.column = column
    
    def get_prompt(self) -> Optional[str]:
        """Get the prompt message if present."""
        if self.prompt_field:
            return self.prompt_field.prompt
        return None
    
    def get_filename(self) -> Optional[str]:
        """Get the filename if present."""
        if self.target:
            return self.target.name
        return None
    
    def get_content(self) -> Optional[str]:
        """Get the content if present."""
        return self.content
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_param_set(self)
    
    def __repr__(self):
        target_str = f"{self.target}, " if self.target else ""
        prompt_str = f"{self.prompt_field}, " if self.prompt_field else ""
        content_str = f"content='{self.content[:20]}...', " if self.content else ""
        return f"ParamSetNode({target_str}{prompt_str}{content_str})"
    
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
        
        if self.content:
            result['content'] = self.content
        
        return result


@dataclass
class DirectiveNode(ASTNode):
    """Represents a complete tester directive."""
    
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
    
    def get_first_filename(self) -> Optional[str]:
        """Get the filename from the first parameter set if present."""
        if self.param_sets and self.param_sets[0]:
            return self.param_sets[0].get_filename()
        return None
    
    def get_first_content(self) -> Optional[str]:
        """Get the content from the first parameter set if present."""
        if self.param_sets and self.param_sets[0]:
            return self.param_sets[0].get_content()
        return None
    
    def is_read_action(self) -> bool:
        """Check if this is a READ action."""
        return self.action.action_type == TokenType.READ
    
    def is_run_action(self) -> bool:
        """Check if this is a RUN action."""
        return self.action.action_type == TokenType.RUN
    
    def is_change_action(self) -> bool:
        """Check if this is a CHANGE action."""
        return self.action.action_type == TokenType.CHANGE
    
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
                directive_str += f' "{param_set.target.name}"'
            
            if param_set.content:
                directive_str += f' CONTENT="{param_set.content}"'
            
            if param_set.prompt_field:
                directive_str += f' PROMPT="{param_set.prompt_field.prompt}"'
        
        return directive_str 