"""
Parser for converting string expressions into Expression AST.
"""
import re
from typing import List, Optional, Tuple
from expression import (
    Expression, Number, Variable, Add, Subtract, Multiply, Divide, 
    Power, Sin, Cos, Ln, Exp
)


class Token:
    """Represents a token in the expression."""
    
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    """Tokenizes mathematical expressions."""
    
    TOKEN_PATTERNS = [
        ('NUMBER', r'\d+\.?\d*'),
        ('VARIABLE', r'[a-zA-Z_]\w*'),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        ('MULTIPLY', r'\*'),
        ('DIVIDE', r'/'),
        ('POWER', r'\^'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('COMMA', r','),
        ('WHITESPACE', r'\s+'),
    ]
    
    FUNCTIONS = {'sin', 'cos', 'ln', 'exp', 'log'}
    
    def __init__(self, expression: str):
        self.expression = expression
        self.position = 0
        self.tokens = []
        self._tokenize()
    
    def _tokenize(self):
        """Convert expression string into tokens."""
        while self.position < len(self.expression):
            match_found = False
            
            for token_type, pattern in self.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(self.expression, self.position)
                
                if match:
                    value = match.group(0)
                    if token_type != 'WHITESPACE':
                        # Check if it's a function
                        if token_type == 'VARIABLE' and value in self.FUNCTIONS:
                            self.tokens.append(Token('FUNCTION', value))
                        else:
                            self.tokens.append(Token(token_type, value))
                    
                    self.position = match.end()
                    match_found = True
                    break
            
            if not match_found:
                raise ValueError(f"Invalid character at position {self.position}: '{self.expression[self.position]}'")


class Parser:
    """Recursive descent parser for mathematical expressions."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def parse(self) -> Expression:
        """Parse tokens into an Expression AST."""
        if not self.tokens:
            raise ValueError("Empty expression")
        
        expr = self._parse_expression()
        
        if self.position < len(self.tokens):
            raise ValueError(f"Unexpected token: {self.tokens[self.position]}")
        
        return expr
    
    def _current_token(self) -> Optional[Token]:
        """Get current token without consuming it."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def _consume_token(self) -> Optional[Token]:
        """Consume and return current token."""
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        return None
    
    def _parse_expression(self) -> Expression:
        """Parse addition and subtraction (lowest precedence)."""
        left = self._parse_term()
        
        while self._current_token() and self._current_token().type in ('PLUS', 'MINUS'):
            op = self._consume_token()
            right = self._parse_term()
            
            if op.type == 'PLUS':
                left = Add(left, right)
            else:
                left = Subtract(left, right)
        
        return left
    
    def _parse_term(self) -> Expression:
        """Parse multiplication and division."""
        left = self._parse_factor()
        
        while self._current_token() and self._current_token().type in ('MULTIPLY', 'DIVIDE'):
            op = self._consume_token()
            right = self._parse_factor()
            
            if op.type == 'MULTIPLY':
                left = Multiply(left, right)
            else:
                left = Divide(left, right)
        
        return left
    
    def _parse_factor(self) -> Expression:
        """Parse power operations (right associative)."""
        base = self._parse_unary()
        
        if self._current_token() and self._current_token().type == 'POWER':
            self._consume_token()
            exponent = self._parse_factor()  # Right associative
            return Power(base, exponent)
        
        return base
    
    def _parse_unary(self) -> Expression:
        """Parse unary operations (negation)."""
        if self._current_token() and self._current_token().type == 'MINUS':
            self._consume_token()
            expr = self._parse_unary()
            return Multiply(Number(-1), expr)
        
        return self._parse_atom()
    
    def _parse_atom(self) -> Expression:
        """Parse atomic expressions (numbers, variables, functions, parentheses)."""
        token = self._current_token()
        
        if not token:
            raise ValueError("Unexpected end of expression")
        
        # Number
        if token.type == 'NUMBER':
            self._consume_token()
            return Number(float(token.value))
        
        # Variable
        elif token.type == 'VARIABLE':
            self._consume_token()
            return Variable(token.value)
        
        # Function
        elif token.type == 'FUNCTION':
            return self._parse_function()
        
        # Parentheses
        elif token.type == 'LPAREN':
            self._consume_token()
            expr = self._parse_expression()
            
            if not self._current_token() or self._current_token().type != 'RPAREN':
                raise ValueError("Missing closing parenthesis")
            
            self._consume_token()
            return expr
        
        else:
            raise ValueError(f"Unexpected token: {token}")
    
    def _parse_function(self) -> Expression:
        """Parse function calls."""
        func_token = self._consume_token()
        func_name = func_token.value
        
        if not self._current_token() or self._current_token().type != 'LPAREN':
            raise ValueError(f"Expected '(' after function {func_name}")
        
        self._consume_token()  # Consume '('
        
        # Parse argument
        arg = self._parse_expression()
        
        if not self._current_token() or self._current_token().type != 'RPAREN':
            raise ValueError(f"Expected ')' after function argument")
        
        self._consume_token()  # Consume ')'
        
        # Create appropriate function expression
        if func_name == 'sin':
            return Sin(arg)
        elif func_name == 'cos':
            return Cos(arg)
        elif func_name == 'ln' or func_name == 'log':
            return Ln(arg)
        elif func_name == 'exp':
            return Exp(arg)
        else:
            raise ValueError(f"Unknown function: {func_name}")


def parse_expression(expression_str: str) -> Expression:
    """Parse a string expression into an Expression AST."""
    # Handle special constants
    expression_str = expression_str.replace('e', str(math.e))
    expression_str = expression_str.replace('pi', str(math.pi))
    expression_str = expression_str.replace('π', str(math.pi))
    
    lexer = Lexer(expression_str)
    parser = Parser(lexer.tokens)
    return parser.parse()


# Import math for constants
import math