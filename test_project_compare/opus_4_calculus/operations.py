"""
Mathematical operations for expressions, including integration.
"""
from typing import Optional, Tuple, Union
from expression import (
    Expression, Number, Variable, Add, Subtract, Multiply, Divide, 
    Power, Sin, Cos, Ln, Exp
)


class IntegrationConstant(Variable):
    """Represents the constant of integration (+C)."""
    
    def __init__(self):
        super().__init__("C")
    
    def __str__(self):
        return "C"


def integrate_expression(expr: Expression, var: str) -> Optional[Expression]:
    """
    Compute the indefinite integral of an expression with respect to a variable.
    Returns None if the integral cannot be computed.
    """
    expr = expr.simplify()
    
    # Constant rule: ∫c dx = cx
    if isinstance(expr, Number):
        return Multiply(expr, Variable(var))
    
    # Variable rule: ∫x dx = x²/2
    if isinstance(expr, Variable):
        if expr.name == var:
            return Divide(Power(expr, Number(2)), Number(2))
        else:
            # Treat as constant
            return Multiply(expr, Variable(var))
    
    # Sum rule: ∫(f + g) dx = ∫f dx + ∫g dx
    if isinstance(expr, Add):
        left_integral = integrate_expression(expr.left, var)
        right_integral = integrate_expression(expr.right, var)
        if left_integral and right_integral:
            return Add(left_integral, right_integral)
        return None
    
    # Difference rule: ∫(f - g) dx = ∫f dx - ∫g dx
    if isinstance(expr, Subtract):
        left_integral = integrate_expression(expr.left, var)
        right_integral = integrate_expression(expr.right, var)
        if left_integral and right_integral:
            return Subtract(left_integral, right_integral)
        return None
    
    # Constant multiple rule: ∫cf dx = c∫f dx
    if isinstance(expr, Multiply):
        # Check if one side is constant w.r.t. var
        left_vars = expr.left.get_variables()
        right_vars = expr.right.get_variables()
        
        if var not in left_vars:
            # Left is constant
            right_integral = integrate_expression(expr.right, var)
            if right_integral:
                return Multiply(expr.left, right_integral)
        elif var not in right_vars:
            # Right is constant
            left_integral = integrate_expression(expr.left, var)
            if left_integral:
                return Multiply(expr.right, left_integral)
    
    # Power rule: ∫x^n dx = x^(n+1)/(n+1) for n ≠ -1
    if isinstance(expr, Power):
        if isinstance(expr.left, Variable) and expr.left.name == var:
            if isinstance(expr.right, Number):
                n = expr.right.value
                if n == -1:
                    # ∫x^(-1) dx = ln|x|
                    return Ln(expr.left)
                else:
                    # ∫x^n dx = x^(n+1)/(n+1)
                    return Divide(
                        Power(expr.left, Number(n + 1)),
                        Number(n + 1)
                    )
    
    # Exponential rule: ∫e^x dx = e^x
    if isinstance(expr, Exp):
        if isinstance(expr.expr, Variable) and expr.expr.name == var:
            return expr
        # Chain rule for e^(ax): ∫e^(ax) dx = (1/a)e^(ax)
        if isinstance(expr.expr, Multiply):
            if isinstance(expr.expr.left, Number) and isinstance(expr.expr.right, Variable):
                if expr.expr.right.name == var:
                    a = expr.expr.left.value
                    return Divide(expr, Number(a))
    
    # Trigonometric rules
    if isinstance(expr, Sin):
        if isinstance(expr.expr, Variable) and expr.expr.name == var:
            # ∫sin(x) dx = -cos(x)
            return Multiply(Number(-1), Cos(expr.expr))
        # Chain rule for sin(ax): ∫sin(ax) dx = -(1/a)cos(ax)
        if isinstance(expr.expr, Multiply):
            if isinstance(expr.expr.left, Number) and isinstance(expr.expr.right, Variable):
                if expr.expr.right.name == var:
                    a = expr.expr.left.value
                    return Multiply(Number(-1/a), Cos(expr.expr))
    
    if isinstance(expr, Cos):
        if isinstance(expr.expr, Variable) and expr.expr.name == var:
            # ∫cos(x) dx = sin(x)
            return Sin(expr.expr)
        # Chain rule for cos(ax): ∫cos(ax) dx = (1/a)sin(ax)
        if isinstance(expr.expr, Multiply):
            if isinstance(expr.expr.left, Number) and isinstance(expr.expr.right, Variable):
                if expr.expr.right.name == var:
                    a = expr.expr.left.value
                    return Multiply(Number(1/a), Sin(expr.expr))
    
    # Division by x: ∫(1/x) dx = ln|x|
    if isinstance(expr, Divide):
        if isinstance(expr.left, Number) and isinstance(expr.right, Variable):
            if expr.right.name == var and expr.left.value == 1:
                return Ln(expr.right)
    
    # If we can't integrate, return None
    return None


def indefinite_integral(expr: Expression, var: str) -> Expression:
    """
    Compute the indefinite integral of an expression.
    Adds the integration constant +C.
    """
    integral = integrate_expression(expr, var)
    
    if integral is None:
        raise ValueError(f"Cannot integrate expression: {expr}")
    
    # Add integration constant
    return Add(integral, IntegrationConstant())


def definite_integral(expr: Expression, var: str, lower: float, upper: float) -> float:
    """
    Compute the definite integral of an expression from lower to upper bound.
    Uses the fundamental theorem of calculus: F(b) - F(a).
    """
    # Get the antiderivative (without +C)
    antiderivative = integrate_expression(expr, var)
    
    if antiderivative is None:
        # Try numerical integration as fallback
        return numerical_integration(expr, var, lower, upper)
    
    # Evaluate at upper and lower bounds
    upper_val = antiderivative.evaluate({var: upper})
    lower_val = antiderivative.evaluate({var: lower})
    
    if isinstance(upper_val, Expression) or isinstance(lower_val, Expression):
        # If we can't evaluate, use numerical integration
        return numerical_integration(expr, var, lower, upper)
    
    return upper_val - lower_val


def numerical_integration(expr: Expression, var: str, lower: float, upper: float, 
                         n_intervals: int = 1000) -> float:
    """
    Perform numerical integration using Simpson's rule.
    Fallback for when symbolic integration fails.
    """
    if n_intervals % 2 != 0:
        n_intervals += 1
    
    h = (upper - lower) / n_intervals
    x = lower
    sum_val = 0.0
    
    # Evaluate at endpoints
    vars_lower = {var: lower}
    vars_upper = {var: upper}
    
    f_lower = expr.evaluate(vars_lower)
    f_upper = expr.evaluate(vars_upper)
    
    if isinstance(f_lower, Expression) or isinstance(f_upper, Expression):
        raise ValueError("Cannot evaluate expression numerically - contains undefined variables")
    
    sum_val = f_lower + f_upper
    
    # Simpson's rule
    for i in range(1, n_intervals):
        x = lower + i * h
        f_x = expr.evaluate({var: x})
        
        if isinstance(f_x, Expression):
            raise ValueError("Cannot evaluate expression numerically - contains undefined variables")
        
        if i % 2 == 0:
            sum_val += 2 * f_x
        else:
            sum_val += 4 * f_x
    
    return (h / 3) * sum_val


def substitute(expr: Expression, var: str, value: Union[float, Expression]) -> Expression:
    """Substitute a value for a variable in an expression."""
    if isinstance(value, (int, float)):
        return expr.evaluate({var: value})
    
    # For Expression substitution, we need to implement a proper substitution method
    # This is a simplified version
    if isinstance(expr, Variable):
        if expr.name == var:
            return value
        return expr
    elif isinstance(expr, Number):
        return expr
    elif isinstance(expr, Add):
        return Add(substitute(expr.left, var, value), substitute(expr.right, var, value))
    elif isinstance(expr, Subtract):
        return Subtract(substitute(expr.left, var, value), substitute(expr.right, var, value))
    elif isinstance(expr, Multiply):
        return Multiply(substitute(expr.left, var, value), substitute(expr.right, var, value))
    elif isinstance(expr, Divide):
        return Divide(substitute(expr.left, var, value), substitute(expr.right, var, value))
    elif isinstance(expr, Power):
        return Power(substitute(expr.left, var, value), substitute(expr.right, var, value))
    elif isinstance(expr, Sin):
        return Sin(substitute(expr.expr, var, value))
    elif isinstance(expr, Cos):
        return Cos(substitute(expr.expr, var, value))
    elif isinstance(expr, Ln):
        return Ln(substitute(expr.expr, var, value))
    elif isinstance(expr, Exp):
        return Exp(substitute(expr.expr, var, value))
    
    return expr