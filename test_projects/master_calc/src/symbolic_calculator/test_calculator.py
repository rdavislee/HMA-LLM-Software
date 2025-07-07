import pytest
from sympy import symbols, sin, cos, exp, log, pi, E, integrate, diff, sympify, Add, Abs, sqrt, Basic, Eq, simplify, zoo # Import zoo for complex infinity

# Assuming Calculator and parse_expression are in these paths relative to the project root
from src.symbolic_calculator.calculator import Calculator
from src.symbolic_calculator.parser import parse_expression

# Define symbolic variables for tests
x, y, z, a, b = symbols('x y z a b')
# Define symbolic constants of integration for checking
C, C1, C2, C3 = symbols('C C1 C2 C3') # Added C3 for robustness in constant tests

@pytest.fixture
def calculator_instance():
    """Provides a fresh Calculator instance for each test."""
    return Calculator()

class TestCalculator:
    """
    Comprehensive unit tests for the Calculator module.
    Covers differentiation, indefinite integration, definite integration,
    and expression evaluation with variable substitutions.
    """

    # Test partitions:
    # 1. Differentiation:
    #    - Simple polynomials (x^n, ax+b)
    #    - Complex polynomials (multi-term)
    #    - Trigonometric functions (sin, cos, tan)
    #    - Exponential/Logarithmic functions (exp, log)
    #    - Expressions with multiple variables
    #    - Differentiation with respect to different variables
    #    - Constants
    # 2. Indefinite Integration:
    #    - Simple polynomials
    #    - Trigonometric functions
    #    - Exponential functions
    #    - Crucial handling of integration constant (C, C1, C2...) to avoid collision
    #    - Expressions with multiple variables
    # 3. Definite Integration:
    #    - Numeric bounds
    #    - Symbolic bounds
    #    - Mixed numeric/symbolic bounds
    #    - Upper bound < Lower bound (negative result)
    #    - Bounds as complex expressions
    #    - Expressions with multiple variables
    # 4. Expression Evaluation:
    #    - Numeric substitutions (single, multiple)
    #    - Symbolic substitutions (single, multiple)
    #    - Mixed substitutions
    #    - Expressions with no variables
    #    - Expressions with constants (pi, e)
    #    - Expressions with functions (log, sin)
    #    - Variables not present in expression (should be ignored)
    #    - Complex expressions with multiple variables and functions
    #    - Edge cases like division by zero

    # --- 1. Differentiation Tests ---
    # Covers: Simple polynomials, multi-term polynomials, trigonometric, exponential/logarithmic,
    #         multi-variable expressions, differentiation w.r.t. different variables, constants.
    @pytest.mark.parametrize("expression_str, variable_str, expected_derivative_str", [
        # Simple polynomials
        ("x**2", "x", "2*x"),
        ("3*x", "x", "3"),
        ("5", "x", "0"),
        # Multi-term polynomials
        ("x**3 + 2*x - 1", "x", "3*x**2 + 2"),
        ("y**2 + x*y", "y", "2*y + x"),
        # Trigonometric functions
        ("sin(x)", "x", "cos(x)"),
        ("cos(2*x)", "x", "-2*sin(2*x)"),
        ("tan(x)", "x", "1/cos(x)**2"), # SymPy might return sec(x)**2
        # Exponential/Logarithmic functions
        ("exp(x)", "x", "exp(x)"),
        ("log(x)", "x", "1/x"), # Natural log
        ("ln(x)", "x", "1/x"), # Alias for natural log
        ("log(x, 10)", "x", "1/(x*log(10))"), # Log base 10
        # Expressions with multiple variables
        ("x*y**2 + z", "x", "y**2"),
        ("x*y**2 + z", "y", "2*x*y"),
        ("x*y**2 + z", "z", "1"),
        # Differentiation w.r.t. a variable not present
        ("x**2 + 5", "y", "0"),
        ("sin(z)", "x", "0"),
        # Constants
        (str(pi), "x", "0"),
        (str(E), "x", "0"),
        ("100", "x", "0"),
    ])
    def test_differentiate(self, calculator_instance, expression_str, variable_str, expected_derivative_str):
        expr = parse_expression(expression_str)
        var = symbols(variable_str)
        expected_deriv = parse_expression(expected_derivative_str)
        
        result_deriv = calculator_instance.differentiate(expr, var)
        assert simplify(result_deriv - expected_deriv) == 0, \
            f"Differentiation failed: {expression_str} wrt {variable_str}\n" \
            f"Expected: {expected_deriv}, Got: {result_deriv}"

    # --- 2. Indefinite Integration Tests ---
    # Covers: Simple polynomials, trigonometric, exponential, multi-variable,
    #         and crucial handling of integration constant (C, C1, C2...). The constant of
    #         integration should be chosen to avoid collision with existing variables in the expression.
    @pytest.mark.parametrize("expression_str, variable_str, expected_integral_base_str", [
        # Simple polynomials
        ("x", "x", "x**2/2"),
        ("x**2", "x", "x**3/3"),
        ("3*x**2", "x", "x**3"),
        ("5", "x", "5*x"),
        # Multi-term polynomials
        ("x + x**2", "x", "x**2/2 + x**3/3"),
        ("x*y", "x", "x**2*y/2"), # treat y as constant
        ("x*y", "y", "x*y**2/2"), # treat x as constant
        # Trigonometric functions
        ("cos(x)", "x", "sin(x)"),
        ("sin(x)", "x", "-cos(x)"),
        # Exponential functions
        ("exp(x)", "x", "exp(x)"),
        # Logarithmic functions (integrate(log(x),x) is x*log(x)-x)
        ("log(x)", "x", "x*log(x) - x"),
    ])
    def test_integrate_indefinite_base(self, calculator_instance, expression_str, variable_str, expected_integral_base_str):
        expr = parse_expression(expression_str)
        var = symbols(variable_str)
        expected_base = parse_expression(expected_integral_base_str)
        
        result_integral = calculator_instance.integrate_indefinite(expr, var)
        
        # Differentiate the result and see if it matches the original expression.
        # This implicitly checks if the constant is correctly handled (it differentiates to 0).
        diff_result = calculator_instance.differentiate(result_integral, var)
        assert simplify(diff_result - expr) == 0, \
            f"Indefinite integral differentiation check failed.\n" \
            f"Original: {expression_str}, Var: {variable_str}\n" \
            f"Integral result: {result_integral}\n" \
            f"Differentiated result: {diff_result}\n" \
            f"Expected original: {expr}"
            
        # Also, check that a constant symbol (C, C1, C2, etc.) is present in the result.
        # This is important for the specific requirement of adding 'C'.
        # We check if any of the expected constant symbols are free symbols in the result.
        has_constant = any(sym in result_integral.free_symbols for sym in [C, C1, C2, C3])
        assert has_constant, f"Indefinite integral result {result_integral} does not contain a constant of integration (C, C1, C2, C3)."

    # Test specific constant handling logic for indefinite integration
    def test_integrate_indefinite_constant_handling(self, calculator_instance):
        # First integration of 'x' should use C
        expr1 = parse_expression("x")
        result1 = calculator_instance.integrate_indefinite(expr1, x)
        assert C in result1.free_symbols and simplify(result1 - (x**2/2 + C)) == 0, \
            f"Expected x**2/2 + C, got {result1}"

        # If C is already in the expression, it should use C1
        expr2 = parse_expression("x + C") # C is a symbol here
        result2 = calculator_instance.integrate_indefinite(expr2, x)
        # Expected base integral of "x + C" wrt x is x**2/2 + C*x.
        expected_base_integral_of_expr2 = parse_expression("x**2/2 + C*x")
        result2_diff_base = simplify(result2 - expected_base_integral_of_expr2)
        
        # The difference should be the new constant of integration, which should be C1.
        assert C1 in result2_diff_base.free_symbols and len(result2_diff_base.free_symbols) == 1, \
            f"Expected C1 as the constant when C is in expression, got {result2_diff_base} (free symbols: {result2_diff_base.free_symbols})"
        assert simplify(result2_diff_base - C1) == 0, \
            f"Expected constant C1 when C is in expression, got {result2_diff_base}"

        # If C1 is in the expression, and C is NOT, it should use C (prioritize lowest available C_n)
        expr3 = parse_expression("x + C1") # C1 is a symbol here
        result3 = calculator_instance.integrate_indefinite(expr3, x)
        expected_base_integral_of_expr3 = parse_expression("x**2/2 + C1*x")
        result3_diff_base = simplify(result3 - expected_base_integral_of_expr3)
        
        assert C in result3_diff_base.free_symbols and len(result3_diff_base.free_symbols) == 1, \
            f"Expected C as the constant when C1 is in expression (but C is not), got {result3_diff_base} (free symbols: {result3_diff_base.free_symbols})"
        assert simplify(result3_diff_base - C) == 0, \
            f"Expected constant C when C1 is in expression (but C is not), got {result3_diff_base}"

        # If C and C1 are in the expression, it should use C2
        expr4 = parse_expression("x + C + C1")
        result4 = calculator_instance.integrate_indefinite(expr4, x)
        expected_base_integral_of_expr4 = parse_expression("x**2/2 + C*x + C1*x")
        result4_diff_base = simplify(result4 - expected_base_integral_of_expr4)
        
        assert C2 in result4_diff_base.free_symbols and len(result4_diff_base.free_symbols) == 1, \
            f"Expected C2 as the constant when C and C1 are in expression, got {result4_diff_base} (free symbols: {result4_diff_base.free_symbols})"
        assert simplify(result4_diff_base - C2) == 0, \
            f"Expected constant C2 when C and C1 are in expression, got {result4_diff_base}"

        # Test with C2 already in expression
        expr5 = parse_expression("x + C2")
        result5 = calculator_instance.integrate_indefinite(expr5, x)
        expected_base_integral_of_expr5 = parse_expression("x**2/2 + C2*x")
        result5_diff_base = simplify(result5 - expected_base_integral_of_expr5)
        
        assert C in result5_diff_base.free_symbols and simplify(result5_diff_base - C) == 0, \
            f"Expected C as the constant when C2 is in expression (but C/C1 are not), got {result5_diff_base}"



    # --- 3. Definite Integration Tests ---
    # Covers: Numeric bounds, symbolic bounds, mixed bounds, upper < lower, multi-variable expressions,
    #         bounds as expressions themselves.
    @pytest.mark.parametrize("expression_str, variable_str, lower_bound_str, upper_bound_str, expected_result_str", [
        # Numeric bounds
        ("x", "x", "0", "1", "1/2"),
        ("x**2", "x", "0", "2", "8/3"),
        ("sin(x)", "x", "0", "pi", "2"),
        ("exp(x)", "x", "0", "1", "E - 1"),
        ("1/x", "x", "1", "E", "1"), # integral of 1/x is log(x)
        # Symbolic bounds
        ("x", "x", "a", "b", "b**2/2 - a**2/2"),
        ("y", "y", "0", "a", "a**2/2"),
        ("x*y", "x", "a", "b", "y*(b**2/2 - a**2/2)"), # y treated as constant
        # Mixed bounds
        ("x", "x", "0", "a", "a**2/2"),
        ("x**2", "x", "a", "1", "1/3 - a**3/3"),
        # Upper bound < Lower bound (integral should be negative of normal)
        ("x", "x", "1", "0", "-1/2"),
        ("x**2", "x", "2", "0", "-8/3"),
        # Bounds as expressions themselves
        ("x", "x", "a+1", "a+2", "(a+2)**2/2 - (a+1)**2/2"), # Simplifies to (2a+3)/2
        ("y", "y", "sin(z)", "cos(z)", "(cos(z)**2)/2 - (sin(z)**2)/2"),
    ])
    def test_integrate_definite(self, calculator_instance, expression_str, variable_str, lower_bound_str, upper_bound_str, expected_result_str):
        expr = parse_expression(expression_str)
        var = symbols(variable_str)
        lower = parse_expression(lower_bound_str)
        upper = parse_expression(upper_bound_str)
        expected_result = parse_expression(expected_result_str)
        
        result = calculator_instance.integrate_definite(expr, var, lower, upper)
        
        assert simplify(result - expected_result) == 0, \
            f"Definite integration failed.\n" \
            f"Expression: {expression_str}, Var: {variable_str}, Bounds: [{lower_bound_str}, {upper_bound_str}]\n" \
            f"Expected: {expected_result}, Got: {result}"

    # --- 4. Expression Evaluation Tests ---
    # Covers: Numeric/symbolic substitutions, no variables, constants, functions, multi-variable,
    #         variables not present, complex expressions, division by zero.
    @pytest.mark.parametrize("expression_str, substitutions, expected_result_str", [
        # Numeric substitutions
        ("x + 1", {"x": 5}, "6"),
        ("x**2 + y", {"x": 2, "y": 3}, "7"), # 2^2 + 3 = 7
        ("sin(x)", {"x": pi/2}, "1"),
        ("log(x)", {"x": E}, "1"),
        ("log(x, 10)", {"x": 100}, "2"),
        # Symbolic substitutions
        ("x + y", {"x": z}, "z + y"),
        ("x**2", {"x": a + b}, "(a + b)**2"),
        # Mixed substitutions
        ("x*y + z", {"x": 2, "y": a, "z": 3}, "2*a + 3"),
        # Expressions with no variables
        ("5 + 3", {}, "8"),
        (str(pi) + " + 1", {}, "pi + 1"),
        # Variables not present in expression (should be ignored)
        ("x + 1", {"y": 10}, "x + 1"),
        ("5", {"x": 100}, "5"),
        # Complex expressions
        ("x*sin(y) + z**2", {"x": 2, "y": pi/2, "z": 3}, "2*1 + 3**2"), # 2 + 9 = 11
        ("log(x) + exp(y)", {"x": E, "y": 0}, "1 + 1"), # 2
        ("x / (y - 1)", {"x": 10, "y": 6}, "2"), # 10 / (6-1) = 10/5 = 2
        # Division by zero scenario - SymPy should handle this and return complex infinity (zoo)
        ("1/x", {"x": 0}, "zoo"),
        ("x / (y - z)", {"x": 5, "y": 2, "z": 2}, "zoo"),
    ])
    def test_evaluate(self, calculator_instance, expression_str, substitutions, expected_result_str):
        expr = parse_expression(expression_str)
        
        # Convert substitution dict keys to SymPy symbols if they are strings
        # Convert substitution dict values to SymPy expressions if they are strings/numbers
        sym_substitutions = {symbols(k) if isinstance(k, str) else k: parse_expression(str(v)) if isinstance(v, (int, float, str)) else v for k, v in substitutions.items()}
        
        expected_result = parse_expression(expected_result_str)
        
        result = calculator_instance.evaluate(expr, sym_substitutions)
        
        # For evaluation, direct equality or simplification check is usually sufficient.
        # For cases like 1/0, SymPy returns zoo. We need to compare these specific symbols directly.
        if expected_result == zoo: # Check for specific SymPy constants like zoo
            assert result == expected_result, \
                f"Evaluation failed for {expression_str} with {substitutions}\n" \
                f"Expected: {expected_result}, Got: {result}"
        else:
            assert simplify(result - expected_result) == 0, \
                f"Evaluation failed for {expression_str} with {substitutions}\n" \
                f"Expected: {expected_result}, Got: {result}"

    def test_evaluate_empty_substitutions(self, calculator_instance):
        # Test evaluation when no substitutions are provided
        expr = parse_expression("x + y + 5")
        result = calculator_instance.evaluate(expr, {})
        assert simplify(result - expr) == 0, \
            f"Expected original expression when no substitutions, got {result}"

    def test_evaluate_no_variables_in_expression(self, calculator_instance):
        # Test evaluation of an expression that has no variables
        expr = parse_expression("5 * 3 + 2")
        result = calculator_instance.evaluate(expr, {"x": 10}) # Substitution should be ignored
        assert simplify(result - parse_expression("17")) == 0, \
            f"Expected 17 for constant expression, got {result}"
