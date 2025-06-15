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
    execute_directive,
    execute_directives
)

from .ast import (
    Directive,
    DelegateDirective,
    FinishDirective,
    ActionDirective,
    WaitDirective,
    UpdateReadmeDirective,
    DelegateItem,
    Target,
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
    'execute_directives',
    
    # AST Classes
    'Directive',
    'DelegateDirective',
    'FinishDirective',
    'ActionDirective',
    'WaitDirective',
    'UpdateReadmeDirective',
    'DelegateItem',
    'Target',
    'PromptField',
    'DirectiveType'
]

__version__ = "2.0.0" 