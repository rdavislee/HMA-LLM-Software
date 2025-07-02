"""
Coder Language Parser using Lark.
Parses coder agent directives and converts them to AST objects.
"""

import os
from typing import List, Union
from lark import Lark, Transformer, v_args
from .ast import (
    Directive, ReadDirective, RunDirective, ChangeDirective, ReplaceDirective, ReplaceItem, InsertDirective, SpawnDirective, WaitDirective, FinishDirective,
    Target, PromptField, EphemeralType, SpawnItem, DirectiveType
)


class CoderLanguageTransformer(Transformer):
    """
    Lark transformer that converts parse trees to AST objects.
    """
    
    @v_args(inline=True)
    def directive(self, directive):
        """Transform any directive to its AST representation."""
        return directive
    
    @v_args(inline=True)
    def read(self, filename):
        """Transform read directive."""
        return ReadDirective(filename=filename)
    
    @v_args(inline=True)
    def run(self, command):
        """Transform run directive."""
        return RunDirective(command=command)
    
    @v_args(inline=True)
    def change(self, content):
        """Transform change directive."""
        return ChangeDirective(content=content)
    
    @v_args(inline=True)
    def replace(self, first_item, *other_items):
        """Transform replace directive."""
        items = [first_item] + list(other_items)
        return ReplaceDirective(items=items)
    
    @v_args(inline=True)
    def replace_item(self, from_string, to_string):
        """Transform replace item."""
        return ReplaceItem(from_string=from_string, to_string=to_string)
    
    @v_args(inline=True)
    def insert(self, from_string, to_string):
        """Transform insert directive."""
        return InsertDirective(from_string=from_string, to_string=to_string)
    
    @v_args(inline=True)
    def spawn(self, first_item, *other_items):
        """Transform spawn directive."""
        items = [first_item] + list(other_items)
        return SpawnDirective(items=items)
    
    @v_args(inline=True)
    def spawn_item(self, ephemeral_type, prompt_field):
        """Transform spawn item."""
        return SpawnItem(ephemeral_type=ephemeral_type, prompt=prompt_field)
    
    @v_args(inline=True)
    def wait(self):
        """Transform wait directive."""
        return WaitDirective()
    
    @v_args(inline=True)
    def finish(self, prompt_field):
        """Transform finish directive."""
        return FinishDirective(prompt=prompt_field)
    
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
    def content_string(self, string):
        """Transform content string."""
        return string
    
    @v_args(inline=True)
    def from_string(self, string):
        """Transform from string."""
        return string
    
    @v_args(inline=True)
    def to_string(self, string):
        """Transform to string."""
        return string
    
    @v_args(inline=True)
    def ephemeral_type(self, type_name):
        """Transform ephemeral type."""
        return EphemeralType(type_name=type_name)
    
    @v_args(inline=True)
    def TESTER(self, token):
        """Transform TESTER token."""
        return "tester"
    
    @v_args(inline=True)
    def string(self, token):
        """Transform string literal from STRING terminal."""
        raw_string = str(token)
        if raw_string.startswith('"') and raw_string.endswith('"'):
            raw_string = raw_string[1:-1]
        return self._unescape_string(raw_string)
    
    def _unescape_string(self, s: str) -> str:
        """Unescape string literals, handling double-backslash and both quote types correctly."""
        # First, replace double-backslash with a placeholder
        placeholder = "\0BACKSLASH\0"
        s = s.replace('\\\\', placeholder)
        escape_map = {
            '\\': '\\',
            '"': '"',
            "'": "'",
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
        # Restore double-backslash
        return ''.join(result).replace(placeholder, '\\')
    
    def escape_string(self, s: str) -> str:
        """Escape string literals for use in directives."""
        escape_map = {
            '\\': '\\\\',
            '"': '\\"',
            '\n': '\\n',
            '\r': '\\r',
            '\t': '\\t',
            '\b': '\\b',
            '\f': '\\f',
            '\v': '\\v'
        }
        
        result = []
        for char in s:
            if char in escape_map:
                result.append(escape_map[char])
            else:
                result.append(char)
        
        return ''.join(result)


class CoderLanguageParser:
    """
    Main parser class for the Coder Language.
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
            transformer=CoderLanguageTransformer(),
            start='directive'
        )
    
    def parse(self, text: str) -> DirectiveType:
        """
        Parse a coder language directive string.
        
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
            raise Exception(f"Failed to parse coder directive: {text}\nError: {str(e)}")
    
    def parse_multiple(self, text: str) -> List[DirectiveType]:
        """
        Parse multiple directives from a text block.
        Each directive should be on a separate line.
        
        Args:
            text: The text containing multiple directives
            
        Returns:
            List of AST objects representing the parsed directives
            
        Raises:
            Exception: If parsing fails
        """
        try:
            lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
            directives = []
            
            for line in lines:
                if line and not line.startswith('//'):  # Skip empty lines and comments
                    directive = self.parse(line)
                    directives.append(directive)
            
            return directives
        except Exception as e:
            raise Exception(f"Failed to parse coder directives: {text}\nError: {str(e)}")


# Convenience functions for easy parsing
def parse_directive(text: str) -> DirectiveType:
    """
    Parse a single coder directive.
    
    Args:
        text: The directive string to parse
        
    Returns:
        An AST object representing the parsed directive
    """
    parser = CoderLanguageParser()
    return parser.parse(text)


def parse_directives(text: str) -> List[DirectiveType]:
    """
    Parse multiple coder directives.
    
    Args:
        text: The text containing multiple directives
        
    Returns:
        List of AST objects representing the parsed directives
    """
    parser = CoderLanguageParser()
    return parser.parse_multiple(text)


def escape_content(content: str) -> str:
    """
    Escape content for use in CHANGE directives.
    
    Args:
        content: The content to escape
        
    Returns:
        Escaped content string
    """
    transformer = CoderLanguageTransformer()
    return transformer.escape_string(content) 