"""
Coder Language Module.

This module provides a language for coder agents to communicate their actions.
Coder agents can read files, run commands, change their own file, and finish tasks.

Example usage:
    from src.languages.coder_language import CoderLanguageInterpreter
    
    interpreter = CoderLanguageInterpreter(own_file="my_file.py")
    context = interpreter.execute('READ "dependencies.py"')
    context = interpreter.execute('RUN "python -m pytest tests/"')
    context = interpreter.execute('CHANGE "my_file.py" CONTENT="def new_function(): pass"')
    context = interpreter.execute('FINISH PROMPT="Task completed successfully"')
"""

from .ast import (
    Directive, ReadDirective, RunDirective, ChangeDirective, ReplaceDirective, SpawnDirective, WaitDirective, FinishDirective,
    Target, PromptField, EphemeralType, SpawnItem, DirectiveType,
    ActionNode, TargetNode, PromptFieldNode, ParamSetNode, DirectiveNode,
    TokenType, NodeType, ASTNode, ASTVisitor
)

from .parser import (
    CoderLanguageParser, CoderLanguageTransformer,
    parse_directive, parse_directives
)

from .interpreter import (
    CoderLanguageInterpreter,
    execute_directive
)

__all__ = [
    # AST classes
    'Directive', 'ReadDirective', 'RunDirective', 'ChangeDirective', 'ReplaceDirective', 'SpawnDirective', 'WaitDirective', 'FinishDirective',
    'Target', 'PromptField', 'EphemeralType', 'SpawnItem', 'DirectiveType',
    'ActionNode', 'TargetNode', 'PromptFieldNode', 'ParamSetNode', 'DirectiveNode',
    'TokenType', 'NodeType', 'ASTNode', 'ASTVisitor',
    
    # Parser classes
    'CoderLanguageParser', 'CoderLanguageTransformer',
    'parse_directive', 'parse_directives',
    
    # Interpreter classes
    'CoderLanguageInterpreter',
    'execute_directive'
]

__version__ = "1.0.0" 