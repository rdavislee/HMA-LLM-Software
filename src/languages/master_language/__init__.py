"""
Master Language Module.

A language for master agents that orchestrate the entire system.
Based on the manager language but simplified for top-level coordination.
"""

from .parser import (
    MasterLanguageParser,
    parse_directive,
    parse_directives
)

from .interpreter import (
    MasterLanguageInterpreter,
    execute_directive
)

from .ast import (
    Directive,
    DelegateDirective,
    SpawnDirective,
    FinishDirective,
    ReadDirective,
    WaitDirective,
    RunDirective,
    UpdateDocumentationDirective,
    SpawnItem,
    Target,
    EphemeralType,
    PromptField,
    DirectiveType
)

__all__ = [
    # Parser
    'MasterLanguageParser',
    'parse_directive',
    'parse_directives',
    
    # Interpreter
    'MasterLanguageInterpreter',
    'execute_directive',
    
    # AST Classes
    'Directive',
    'DelegateDirective',
    'SpawnDirective',
    'FinishDirective',
    'ReadDirective',
    'WaitDirective',
    'RunDirective',
    'UpdateDocumentationDirective',
    'SpawnItem',
    'Target',
    'EphemeralType',
    'PromptField',
    'DirectiveType'
]

__version__ = "1.0.0" 