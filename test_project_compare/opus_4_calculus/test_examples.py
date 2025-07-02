"""
Example usage of the mathematical expression utilities.
"""
from utils import (
    evaluate, derivative, indefinite_integral, definite_integral,
    simplify, get_variables, substitute
)


def main():
    print("=== Mathematical Expression Utilities Demo ===\n")
    
    # 1. Expression Evaluation
    print("1. EXPRESSION EVALUATION")
    print("-" * 40)
    
    # Fully specified expression
    expr1 = "3*x^2 + 2*x - 5"
    vars1 = {"x": 2}
    result1 = evaluate(expr1, vars1)
    print(f"Expression: {expr1}")
    print(f"Variables: {vars1}")
    print(f"Result: {result1}")
    print()
    
    # Partially specified expression
    expr2 = "x^2 + y^2"
    vars2 = {"x": 3}
    result2 = evaluate(expr2, vars2)
    print(f"Expression: {expr2}")
    print(f"Variables: {vars2}")
    print(f"Result: {result2}")
    print()
    
    # Expression with functions
    expr3 = "sin(x) + cos(x)"
    vars3 = {"x": 0}
    result3 = evaluate(expr3, vars3)
    print(f"Expression: {expr3}")
    print(f"Variables: {vars3}")
    print(f"Result: {result3}")
    print()
    
    # 2. Derivatives
    print("\n2. DERIVATIVES")
    print("-" * 40)
    
    expressions = [
        "x^3",
        "sin(x)",
        "x * ln(x)",
        "exp(x) + x^2",
        "1/x",
    ]
    
    for expr in expressions:
        deriv = derivative(expr, "x")
        print(f"d/dx ({expr}) = {deriv}")
    print()
    
    # 3. Indefinite Integrals
    print("\n3. INDEFINITE INTEGRALS")
    print("-" * 40)
    
    integrals = [
        "x^2",
        "sin(x)",
        "cos(x)",
        "1/x",
        "exp(x)",
        "x^3 + 2*x",
    ]
    
    for expr in integrals:
        try:
            integral = indefinite_integral(expr, "x")
            print(f"∫ {expr} dx = {integral}")
        except ValueError as e:
            print(f"∫ {expr} dx = Cannot integrate: {e}")
    print()
    
    # 4. Definite Integrals
    print("\n4. DEFINITE INTEGRALS")
    print("-" * 40)
    
    definite_tests = [
        ("x^2", 0, 1),
        ("sin(x)", 0, 3.14159),
        ("1/x", 1, 2.718),
        ("exp(x)", 0, 1),
    ]
    
    for expr, a, b in definite_tests:
        result = definite_integral(expr, "x", a, b)
        print(f"∫[{a},{b}] {expr} dx = {result:.6f}")
    print()
    
    # 5. Complex Examples
    print("\n5. COMPLEX EXAMPLES")
    print("-" * 40)
    
    # Polynomial integration and differentiation
    poly = "x^4 - 2*x^3 + x^2 - 5*x + 3"
    print(f"Original polynomial: {poly}")
    poly_deriv = derivative(poly, "x")
    print(f"Derivative: {poly_deriv}")
    poly_integral = indefinite_integral(poly, "x")
    print(f"Integral: {poly_integral}")
    
    # Verify fundamental theorem of calculus
    print("\nVerifying d/dx(∫f(x)dx) = f(x):")
    integral_then_deriv = derivative(indefinite_integral("x^2", "x"), "x")
    print(f"d/dx(∫x² dx) = {integral_then_deriv}")
    print()
    
    # 6. Utility Functions
    print("\n6. UTILITY FUNCTIONS")
    print("-" * 40)
    
    # Get variables
    expr = "a*x^2 + b*x + c"
    vars_list = get_variables(expr)
    print(f"Variables in '{expr}': {vars_list}")
    
    # Simplify
    to_simplify = [
        "x + 0",
        "x * 1",
        "x - x",
        "0 * x",
        "x^1",
    ]
    
    print("\nSimplification:")
    for expr in to_simplify:
        simplified = simplify(expr)
        print(f"{expr} → {simplified}")
    
    # Substitute
    print("\nSubstitution:")
    expr = "a*x^2 + b*x + c"
    subs = {"a": 1, "b": -2, "c": 1}
    result = substitute(expr, subs)
    print(f"Expression: {expr}")
    print(f"Substitutions: {subs}")
    print(f"Result: {result}")
    
    # 7. Physics Example
    print("\n\n7. PHYSICS EXAMPLE - Kinematics")
    print("-" * 40)
    
    # Position function
    position = "5*t^3 - 2*t^2 + 3*t + 10"
    print(f"Position: s(t) = {position}")
    
    # Velocity is derivative of position
    velocity = derivative(position, "t")
    print(f"Velocity: v(t) = ds/dt = {velocity}")
    
    # Acceleration is derivative of velocity
    acceleration = derivative(velocity, "t")
    print(f"Acceleration: a(t) = dv/dt = {acceleration}")
    
    # Calculate values at t=2
    t_val = 2
    pos_at_2 = evaluate(position, {"t": t_val})
    vel_at_2 = evaluate(velocity, {"t": t_val})
    acc_at_2 = evaluate(acceleration, {"t": t_val})
    
    print(f"\nAt t = {t_val}:")
    print(f"  Position: {pos_at_2} m")
    print(f"  Velocity: {vel_at_2} m/s")
    print(f"  Acceleration: {acc_at_2} m/s²")
    
    # Calculate distance traveled from t=0 to t=2
    distance = definite_integral(velocity, "t", 0, 2)
    print(f"\nDistance from t=0 to t=2: {distance:.2f} m")


if __name__ == "__main__":
    main()