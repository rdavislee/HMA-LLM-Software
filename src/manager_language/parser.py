"""
Manager Language Parser using Lark.
Parses manager agent directives and converts them to AST objects.
"""

import os
from typing import List, Union
from lark import Lark, Transformer, v_args
from .ast import (
    Directive, DelegateDirective, FinishDirective, ActionDirective, WaitDirective, RunDirective, UpdateReadmeDirective,
    DelegateItem, Target, PromptField, DirectiveType
)


class ManagerLanguageTransformer(Transformer):
    """
    Lark transformer that converts parse trees to AST objects.
    """
    
    @v_args(inline=True)
    def directive(self, directive):
        """Transform any directive to its AST representation."""
        return directive
    
    @v_args(inline=True)
    def delegate(self, first_item, *other_items):
        """Transform delegate directive."""
        items = [first_item] + list(other_items)
        return DelegateDirective(items=items)
    
    @v_args(inline=True)
    def delegate_item(self, target, prompt_field):
        """Transform delegate item."""
        return DelegateItem(target=target, prompt=prompt_field)
    
    @v_args(inline=True)
    def finish(self, prompt_field):
        """Transform finish directive."""
        return FinishDirective(prompt=prompt_field)
    
    @v_args(inline=True)
    def action(self, action_type, *targets):
        """Transform action directive."""
        return ActionDirective(action_type=action_type, targets=list(targets))
    
    @v_args(inline=True)
    def action_type(self, action):
        """Transform action type."""
        return str(action)
    
    @v_args(inline=True)
    def CREATE(self, token):
        """Transform CREATE token."""
        return "CREATE"
    
    @v_args(inline=True)
    def DELETE(self, token):
        """Transform DELETE token."""
        return "DELETE"
    
    @v_args(inline=True)
    def READ(self, token):
        """Transform READ token."""
        return "READ"
    
    @v_args(inline=True)
    def RUN(self, token):
        """Transform RUN token."""
        return "RUN"
    
    @v_args(inline=True)
    def UPDATE_README(self, token):
        """Transform UPDATE_README token."""
        return "UPDATE_README"
    
    @v_args(inline=True)
    def wait(self):
        """Transform wait directive."""
        return WaitDirective()
    
    @v_args(inline=True)
    def target(self, target):
        """Transform target."""
        return target
    
    @v_args(inline=True)
    def file(self, filename):
        """Transform file target."""
        return Target(name=filename, is_folder=False)
    
    @v_args(inline=True)
    def folder(self, filename):
        """Transform folder target."""
        return Target(name=filename, is_folder=True)
    
    @v_args(inline=True)
    def filename(self, value):
        """Transform filename."""
        return value
    
    @v_args(inline=True)
    def command(self, value):
        """Transform command."""
        return value
    
    @v_args(inline=True)
    def prompt_field(self, string):
        """Transform prompt field."""
        return PromptField(value=string)
    
    @v_args(inline=True)
    def string(self, token):
        """Transform string literal from STRING terminal."""
        raw_string = str(token)
        if raw_string.startswith('"') and raw_string.endswith('"'):
            raw_string = raw_string[1:-1]
        return self._unescape_string(raw_string)
    
    def _unescape_string(self, s: str) -> str:
        """Unescape string literals."""
        escape_map = {
            '\\': '\\',
            '"': '"',
            '/': '/',
            'b': '\b',
            'f': '\f',
            'n': '\n',
            'r': '\r',
            't': '\t',
            'v': '\v'
        }
        
        result = []
        i = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                next_char = s[i + 1]
                if next_char in escape_map:
                    result.append(escape_map[next_char])
                    i += 2
                else:
                    result.append(s[i])
                    i += 1
            else:
                result.append(s[i])
                i += 1
        
        return ''.join(result)
    
    @v_args(inline=True)
    def run(self, run_token, command):
        """Transform run directive."""
        return RunDirective(command=command)
    
    @v_args(inline=True)
    def update_readme(self, content_string):
        """Transform update_readme directive."""
        return UpdateReadmeDirective(content=content_string)
    
    @v_args(inline=True)
    def content_string(self, string):
        """Transform content_string field."""
        return string


class ManagerLanguageParser:
    """
    Main parser class for the Manager Language.
    Uses Lark to parse directives and convert them to AST objects.
    """
    
    def __init__(self):
        """Initialize the parser with the grammar."""
        # Get the path to the grammar file
        grammar_path = os.path.join(os.path.dirname(__file__), 'grammar.lark')
        
        # Read the grammar file
        with open(grammar_path, 'r') as f:
            grammar = f.read()
        
        # Create the Lark parser
        self.parser = Lark(
            grammar,
            parser='lalr',
            transformer=ManagerLanguageTransformer(),
            start='directive'
        )
    
    def parse(self, text: str) -> DirectiveType:
        """
        Parse a manager language directive string.
        
        Args:
            text: The directive string to parse
            
        Returns:
            An AST object representing the parsed directive
            
        Raises:
            Exception: If parsing fails
        """
        try:
            result = self.parser.parse(text.strip())
            return result
        except Exception as e:
            raise Exception(f"Failed to parse manager directive: {text}\nError: {str(e)}")
    
    def parse_multiple(self, text: str) -> List[DirectiveType]:
        """
        Parse multiple directives from a text block.
        Each directive should be on a separate line.
        
        Args:
            text: The text containing multiple directives
            
        Returns:
            List of AST objects representing the parsed directives
        """
        directives = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//'):  # Skip empty lines and comments
                directive = self.parse(line)
                directives.append(directive)
        
        return directives


# Convenience function for quick parsing
def parse_directive(text: str) -> DirectiveType:
    """
    Convenience function to parse a single directive.
    
    Args:
        text: The directive string to parse
        
    Returns:
        An AST object representing the parsed directive
    """
    parser = ManagerLanguageParser()
    return parser.parse(text)


def parse_directives(text: str) -> List[DirectiveType]:
    """
    Convenience function to parse multiple directives.
    
    Args:
        text: The text containing multiple directives
        
    Returns:
        List of AST objects representing the parsed directives
    """
    parser = ManagerLanguageParser()
    return parser.parse_multiple(text) 