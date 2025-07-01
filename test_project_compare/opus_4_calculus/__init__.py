"""
Mathematical Expression Library

A Python library for symbolic mathematics including:
- Expression parsing and evaluation
- Symbolic differentiation
- Symbolic integration (indefinite and definite)
- Expression simplification
"""

# Import main functions from utils
from .utils import (
    evaluate,
    derivative,
    indefinite_integral,
    definite_integral,
    simplify,
    get_variables,
    substitute
)

# Import core classes if users want lower-level access
from .expression import (
    Expression,
    Number,
    Variable,
    Add,
    Subtract,
    Multiply,
    Divide,
    Power,
    Sin,
    Cos,
    Ln,
    Exp
)

# Import parser for direct parsing
from .parser import parse_expression

# Version info
__version__ = "1.0.0"
__author__ = "Mathematical Expression Library"

# Define what's available when using "from math_expr import *"
__all__ = [
    # Main functions
    'evaluate',
    'derivative',
    'indefinite_integral',
    'definite_integral',
    'simplify',
    'get_variables',
    'substitute',
    
    # Core functionality
    'parse_expression',
    
    # Expression classes
    'Expression',
    'Number',
    'Variable',
    'Add',
    'Subtract',
    'Multiply',
    'Divide',
    'Power',
    'Sin',
    'Cos',
    'Ln',
    'Exp'
]