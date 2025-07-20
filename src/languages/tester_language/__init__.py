"""
Tester Language Module.

This module provides a language for tester agents to communicate their actions.
Tester agents can read files, run commands, change their scratch pad, and finish tasks.

Example usage:
    from src.languages.tester_language import TesterLanguageInterpreter
    
    interpreter = TesterLanguageInterpreter(agent=tester_agent)
    context = interpreter.execute('READ "dependencies.py"')
    context = interpreter.execute('RUN "python -m pytest tests/"')
    context = interpreter.execute('CHANGE CONTENT="print(\'Debug info\')"')
    context = interpreter.execute('FINISH PROMPT="Testing completed - found 3 failing tests"')
"""

from .ast import (
    Directive, ReadDirective, RunDirective, ChangeDirective, ReplaceDirective, ReplaceItem, FinishDirective,
    Target, PromptField, DirectiveType,
    ActionNode, TargetNode, PromptFieldNode, ParamSetNode, DirectiveNode,
    TokenType, NodeType, ASTNode, ASTVisitor
)

from .parser import (
    TesterLanguageParser, TesterLanguageTransformer,
    parse_directive, parse_directives
)

from .interpreter import (
    TesterLanguageInterpreter,
    execute_directive
)

__all__ = [
    # AST classes
    'Directive', 'ReadDirective', 'RunDirective', 'ChangeDirective', 'ReplaceDirective', 'ReplaceItem', 'FinishDirective',
    'Target', 'PromptField', 'DirectiveType',
    'ActionNode', 'TargetNode', 'PromptFieldNode', 'ParamSetNode', 'DirectiveNode',
    'TokenType', 'NodeType', 'ASTNode', 'ASTVisitor',
    
    # Parser classes
    'TesterLanguageParser', 'TesterLanguageTransformer',
    'parse_directive', 'parse_directives',
    
    # Interpreter classes
    'TesterLanguageInterpreter',
    'execute_directive'
]

__version__ = "1.0.0" 