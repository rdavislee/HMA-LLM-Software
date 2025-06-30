"""
Manager Language Module.

A complete implementation of the Manager Language for autonomous agent coordination.
Uses Lark for parsing and provides a clean API for executing manager directives.
"""

from .parser import (
    ManagerLanguageParser,
    parse_directive,
    parse_directives
)

from .interpreter import (
    ManagerLanguageInterpreter,
    execute_directive
)

from .ast import (
    Directive,
    DelegateDirective,
    SpawnDirective,
    FinishDirective,
    ActionDirective,
    WaitDirective,
    UpdateReadmeDirective,
    DelegateItem,
    SpawnItem,
    Target,
    EphemeralType,
    PromptField,
    DirectiveType
)

__all__ = [
    # Parser
    'ManagerLanguageParser',
    'parse_directive',
    'parse_directives',
    
    # Interpreter
    'ManagerLanguageInterpreter',
    'execute_directive',
    
    # AST Classes
    'Directive',
    'DelegateDirective',
    'SpawnDirective',
    'FinishDirective',
    'ActionDirective',
    'WaitDirective',
    'UpdateReadmeDirective',
    'DelegateItem',
    'SpawnItem',
    'Target',
    'EphemeralType',
    'PromptField',
    'DirectiveType'
]

__version__ = "2.0.0" 