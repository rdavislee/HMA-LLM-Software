from sympy import sympify, SympifyError, Symbol, Pow, Integer, Float, Rational
from sympy.functions import log, ln, sin, cos, tan, csc, sec, cot, asin, acos, atan, acsc, asec, acot, Abs, exp, sqrt
from sympy.abc import pi, E
from sympy.core.expr import Expr
from sympy.core.function import UndefinedFunction
from typing import Union

def parse_expression(expression_string: str) -> Union[Expr, None]:
    """
    Safely parses a string input into a SymPy expression.

    Args:
        expression_string (str): The string representation of the mathematical expression.

    Returns:
        Union[Expr, None]: A SymPy expression object if parsing is successful, otherwise None.
    """
    if not expression_string.strip():
        return None
        
    try:
        # Evaluate=False is good for preventing automatic simplification that might obscure the original intent
        # Provide 'e' explicitly in locals to ensure it's parsed as SymPy's E constant, not a generic symbol
        expr = sympify(expression_string, evaluate=False, locals={'e': E})
        
        # Check if sympify created an UndefinedFunction for unrecognized functions
        # This occurs when evaluate=False and a function name is not known to sympify
        if isinstance(expr, UndefinedFunction):
            return None
            
        return expr
    except SympifyError:
        # SymPy's specific parsing error
        return None
    except (SyntaxError, TypeError, ValueError):
        # Other potential Python errors during interpretation
        return None
    except Exception:
        # Catch any other unexpected errors
        return None
