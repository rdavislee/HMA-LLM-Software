"""
Main utility functions for mathematical expression evaluation, differentiation, and integration.
"""
from typing import Dict, Union, Optional
from parser import parse_expression
from operations import indefinite_integral as _indefinite_integral, definite_integral as _definite_integral
from expression import Expression


def evaluate(expression_str: str, variables: Optional[Dict[str, float]] = None) -> Union[float, str]:
    """
    Evaluate a mathematical expression with given variable values.
    
    Args:
        expression_str: String representation of the mathematical expression
        variables: Dictionary mapping variable names to their values
    
    Returns:
        float: If all variables are provided
        str: String representation of the simplified expression if some variables are missing
    
    Examples:
        >>> evaluate("2*x + 3", {"x": 5})
        13.0
        
        >>> evaluate("x^2 + y", {"x": 3})
        '(9 + y)'
        
        >>> evaluate("sin(pi/2)")
        1.0
    """
    if variables is None:
        variables = {}
    
    try:
        expr = parse_expression(expression_str)
        result = expr.evaluate(variables)
        
        if isinstance(result, Expression):
            # Simplify and return string representation
            simplified = result.simplify()
            return str(simplified)
        else:
            return float(result)
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {str(e)}")


def derivative(expression_str: str, variable: str) -> str:
    """
    Compute the derivative of an expression with respect to a variable.
    
    Args:
        expression_str: String representation of the mathematical expression
        variable: Variable to differentiate with respect to
    
    Returns:
        String representation of the derivative
    
    Examples:
        >>> derivative("x^2 + 3*x + 1", "x")
        '((2 * x) + 3)'
        
        >>> derivative("sin(x) * cos(x)", "x")
        '((cos(x) * cos(x)) + (sin(x) * (-sin(x))))'
        
        >>> derivative("x^3 + y^2", "x")
        '(3 * (x^2))'
    """
    try:
        expr = parse_expression(expression_str)
        deriv = expr.derivative(variable)
        simplified = deriv.simplify()
        return str(simplified)
    except Exception as e:
        raise ValueError(f"Error computing derivative: {str(e)}")


def indefinite_integral(expression_str: str, variable: str) -> str:
    """
    Compute the indefinite integral of an expression with respect to a variable.
    
    Args:
        expression_str: String representation of the mathematical expression
        variable: Variable to integrate with respect to
    
    Returns:
        String representation of the integral with integration constant +C
    
    Examples:
        >>> indefinite_integral("x^2", "x")
        '((x^3) / 3) + C)'
        
        >>> indefinite_integral("sin(x)", "x")
        '((-1 * cos(x)) + C)'
        
        >>> indefinite_integral("1/x", "x")
        '(ln(x) + C)'
    """
    try:
        expr = parse_expression(expression_str)
        integral = _indefinite_integral(expr, variable)
        return str(integral)
    except Exception as e:
        raise ValueError(f"Error computing indefinite integral: {str(e)}")


def definite_integral(expression_str: str, variable: str, lower_bound: float, upper_bound: float) -> float:
    """
    Compute the definite integral of an expression over a given interval.
    
    Args:
        expression_str: String representation of the mathematical expression
        variable: Variable to integrate with respect to
        lower_bound: Lower bound of integration
        upper_bound: Upper bound of integration
    
    Returns:
        Numerical value of the definite integral
    
    Examples:
        >>> definite_integral("x^2", "x", 0, 1)
        0.3333333333333333
        
        >>> definite_integral("sin(x)", "x", 0, 3.14159)
        2.0
        
        >>> definite_integral("1/x", "x", 1, 2.718)
        0.999896...
    """
    try:
        expr = parse_expression(expression_str)
        result = _definite_integral(expr, variable, lower_bound, upper_bound)
        return float(result)
    except Exception as e:
        raise ValueError(f"Error computing definite integral: {str(e)}")


# Additional utility functions

def simplify(expression_str: str) -> str:
    """
    Simplify a mathematical expression.
    
    Args:
        expression_str: String representation of the mathematical expression
    
    Returns:
        String representation of the simplified expression
    
    Examples:
        >>> simplify("x + 0")
        'x'
        
        >>> simplify("x * 1")
        'x'
        
        >>> simplify("x - x")
        '0'
    """
    try:
        expr = parse_expression(expression_str)
        simplified = expr.simplify()
        return str(simplified)
    except Exception as e:
        raise ValueError(f"Error simplifying expression: {str(e)}")


def get_variables(expression_str: str) -> list:
    """
    Get all variables in an expression.
    
    Args:
        expression_str: String representation of the mathematical expression
    
    Returns:
        List of variable names in the expression
    
    Examples:
        >>> get_variables("x^2 + y*z")
        ['x', 'y', 'z']
        
        >>> get_variables("sin(theta) + cos(phi)")
        ['theta', 'phi']
    """
    try:
        expr = parse_expression(expression_str)
        return sorted(list(expr.get_variables()))
    except Exception as e:
        raise ValueError(f"Error parsing expression: {str(e)}")


def substitute(expression_str: str, substitutions: Dict[str, Union[float, str]]) -> str:
    """
    Substitute values or expressions for variables.
    
    Args:
        expression_str: String representation of the mathematical expression
        substitutions: Dictionary mapping variable names to values or expressions
    
    Returns:
        String representation of the expression after substitution
    
    Examples:
        >>> substitute("x^2 + y", {"x": 3})
        '(9 + y)'
        
        >>> substitute("a*x + b", {"a": 2, "b": 5})
        '((2 * x) + 5)'
    """
    try:
        expr = parse_expression(expression_str)
        
        # Apply substitutions
        for var, value in substitutions.items():
            if isinstance(value, str):
                value_expr = parse_expression(value)
                result = expr.evaluate({var: value})
            else:
                result = expr.evaluate({var: float(value)})
            
            if isinstance(result, Expression):
                expr = result
            else:
                # All variables substituted
                return str(result)
        
        return str(expr.simplify())
    except Exception as e:
        raise ValueError(f"Error substituting values: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    # Test evaluation
    print("Evaluation tests:")
    print(f"evaluate('2*x + 3', {{'x': 5}}) = {evaluate('2*x + 3', {'x': 5})}")
    print(f"evaluate('x^2 + y', {{'x': 3}}) = {evaluate('x^2 + y', {'x': 3})}")
    print(f"evaluate('sin(0)') = {evaluate('sin(0)')}")
    print()
    
    # Test derivatives
    print("Derivative tests:")
    print(f"derivative('x^2', 'x') = {derivative('x^2', 'x')}")
    print(f"derivative('x^3 + 2*x^2 + x + 1', 'x') = {derivative('x^3 + 2*x^2 + x + 1', 'x')}")
    print(f"derivative('sin(x)', 'x') = {derivative('sin(x)', 'x')}")
    print(f"derivative('ln(x)', 'x') = {derivative('ln(x)', 'x')}")
    print()
    
    # Test indefinite integrals
    print("Indefinite integral tests:")
    print(f"indefinite_integral('x^2', 'x') = {indefinite_integral('x^2', 'x')}")
    print(f"indefinite_integral('sin(x)', 'x') = {indefinite_integral('sin(x)', 'x')}")
    print(f"indefinite_integral('1/x', 'x') = {indefinite_integral('1/x', 'x')}")
    print()
    
    # Test definite integrals
    print("Definite integral tests:")
    print(f"definite_integral('x^2', 'x', 0, 1) = {definite_integral('x^2', 'x', 0, 1)}")
    print(f"definite_integral('sin(x)', 'x', 0, 3.14159) = {definite_integral('sin(x)', 'x', 0, 3.14159)}")
    print()
    
    # Test utilities
    print("Utility tests:")
    print(f"get_variables('x^2 + y*z') = {get_variables('x^2 + y*z')}")
    print(f"simplify('x + 0') = {simplify('x + 0')}")
    print(f"substitute('a*x + b', {{'a': 2, 'b': 5}}) = {substitute('a*x + b', {'a': 2, 'b': 5})}")