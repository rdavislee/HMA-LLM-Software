import pytest
from src.engine.calculator import Calculator
from sympy import sympify, symbols, exp, log, sin, cos, tan, pi, E, sqrt, oo, Integral, Derivative, nan, zoo

class TestCalculator:
    def setup_method(self):
        self.calculator = Calculator()

    # Test partitions for parse_expression:
    # - Valid simple expressions
    # - Valid complex expressions with variables
    # - Valid expressions with constants (pi, e)
    # - Valid expressions with various functions
    # - Invalid expressions (syntax errors, unmatched parentheses, unknown symbols, empty/whitespace)

    def test_parse_expression_valid_simple(self):
        # Covers: Valid simple expressions
        assert sympify(self.calculator.parse_expression("x + 1")) == sympify("x + 1")
        assert sympify(self.calculator.parse_expression("2*y - 5")) == sympify("2*y - 5")

    def test_parse_expression_valid_complex_with_variables(self):
        # Covers: Valid complex expressions with variables
        assert sympify(self.calculator.parse_expression("a*x**2 + b*x + c")) == sympify("a*x**2 + b*x + c")
        assert sympify(self.calculator.parse_expression("(sin(x) + cos(y)) / log(z)")) == sympify("(sin(x) + cos(y))/log(z, 10)")

    def test_parse_expression_valid_with_constants(self):
        # Covers: Valid expressions with constants (pi, e)
        assert sympify(self.calculator.parse_expression("2*pi + e")) == sympify("2*pi + E")
        assert sympify(self.calculator.parse_expression("sin(pi/2)")) == sympify("sin(pi/2)")
        assert sympify(self.calculator.parse_expression("exp(1)")) == sympify("exp(1)")

    def test_parse_expression_valid_with_functions(self):
        # Covers: Valid expressions with various functions
        assert sympify(self.calculator.parse_expression("log(x, 2)")) == sympify("log(x, 2)")
        assert sympify(self.calculator.parse_expression("ln(x)")) == sympify("log(x)") # sympy's ln is log
        assert sympify(self.calculator.parse_expression("log(x)")) == sympify("log(x, 10)") # Default base 10 as per documentation
        assert sympify(self.calculator.parse_expression("sin(x) + cos(x)")) == sympify("sin(x) + cos(x)")
        assert sympify(self.calculator.parse_expression("tan(x) + csc(x) + sec(x) + cot(x)")) == sympify("tan(x) + csc(x) + sec(x) + cot(x)")
        assert sympify(self.calculator.parse_expression("asin(x) + acos(x) + atan(x)")) == sympify("asin(x) + acos(x) + atan(x)")
        assert sympify(self.calculator.parse_expression("acsc(x) + asec(x) + acot(x)")) == sympify("acsc(x) + asec(x) + acot(x)")
        assert sympify(self.calculator.parse_expression("sqrt(x)")) == sympify("sqrt(x)")

    def test_parse_expression_invalid_syntax(self):
        # Covers: Invalid expressions (syntax errors, unmatched parentheses, unknown symbols, empty/whitespace)
        with pytest.raises(ValueError, match="Invalid expression:"):
            self.calculator.parse_expression("x + * 1")
        with pytest.raises(ValueError, match="Invalid expression:"):
            self.calculator.parse_expression("(x + 1")
        with pytest.raises(ValueError, match="Invalid expression:"):
            self.calculator.parse_expression("unknown_func(x)")
        with pytest.raises(ValueError, match="Invalid expression:"):
            self.calculator.parse_expression("")
        with pytest.raises(ValueError, match="Invalid expression:"):
            self.calculator.parse_expression("  ")
        with pytest.raises(ValueError, match="log\\(\\)\\ takes 1 or 2 arguments \\(3 given\\)"): # too many arguments, Sympy raises TypeError via custom _log_func
            self.calculator.parse_expression("log(x,y,z)")

    # Test partitions for evaluate_expression:
    # - Simple numerical evaluation
    # - Evaluation with variable substitution (single variable, multiple variables)
    # - Evaluation of expressions with constants (pi, e)
    # - Evaluation of expressions with functions
    # - Edge cases: division by zero, undefined results (e.g., log of non-positive, sqrt of negative)
    # - Error handling: missing variable values, non-numeric variable values (leading to non-numeric eval)

    def test_evaluate_expression_simple_numerical(self):
        # Covers: Simple numerical evaluation
        assert sympify(self.calculator.evaluate_expression("2 + 3 * 4")) == sympify("14")
        assert sympify(self.calculator.evaluate_expression("(5 - 1) / 2")) == sympify("2")
        assert sympify(self.calculator.evaluate_expression("2**3")) == sympify("8")

    def test_evaluate_expression_with_variable_substitution(self):
        # Covers: Evaluation with variable substitution (single variable, multiple variables)
        assert sympify(self.calculator.evaluate_expression("x + 5", {"x": 10})) == sympify("15")
        assert sympify(self.calculator.evaluate_expression("x*y + z", {"x": 2, "y": 3, "z": 4})) == sympify("10")
        assert sympify(self.calculator.evaluate_expression("x**2", {"x": -3})) == sympify("9")
        assert sympify(self.calculator.evaluate_expression("a*x + b", {"a": "2", "x": "3", "b": "1"})) == sympify("7") # Strings should be converted to numbers

    def test_evaluate_expression_with_constants(self):
        # Covers: Evaluation of expressions with constants (pi, e)
        # Use str comparison for float results due to precision
        assert sympify(self.calculator.evaluate_expression("2*pi")) == sympify("2*pi")
        assert sympify(self.calculator.evaluate_expression("e**2")) == sympify("E**2")
        assert sympify(self.calculator.evaluate_expression("pi/2 + e")) == sympify("pi/2 + E")

    def test_evaluate_expression_with_functions(self):
        # Covers: Evaluation of expressions with functions
        assert sympify(self.calculator.evaluate_expression("sin(pi/2)")) == sympify("1")
        assert sympify(self.calculator.evaluate_expression("log(100, 10)")) == sympify("2")
        assert sympify(self.calculator.evaluate_expression("ln(exp(5))")) == sympify("5")
        assert sympify(self.calculator.evaluate_expression("sqrt(9)")) == sympify("3")
        assert sympify(self.calculator.evaluate_expression("tan(0)")) == sympify("0")
        assert sympify(self.calculator.evaluate_expression("log(10)")) == sympify("1") # log(x) is base 10 as per documentation
        assert sympify(self.calculator.evaluate_expression("log(pi, 10)")) == sympify("log(pi, 10)")


    def test_evaluate_expression_edge_cases(self):
        # Covers: Edge cases: division by zero, undefined results
        with pytest.raises(ValueError, match="Evaluation error: Division by zero"): # Sympy raises ZeroDivisionError, which should be caught and re-raised as ValueError
            self.calculator.evaluate_expression("1/0")
        assert sympify(self.calculator.evaluate_expression("log(-1)")) == sympify("I*pi/log(10)")
        assert self.calculator.evaluate_expression("sqrt(-4)") == "2*I"
        assert self.calculator.evaluate_expression("log(0)") == "zoo" # Sympy evaluates log(0) to -oo
        assert self.calculator.evaluate_expression("atan(oo)") == "pi/2" # Sympy handles atan(oo)

    def test_evaluate_expression_error_handling_missing_variables(self):
        # Covers: Error handling: missing variable values
        with pytest.raises(ValueError, match="Missing values for variables: y.*"): # Expect specific variable names in message
            self.calculator.evaluate_expression("x + y", {"x": 1})
        with pytest.raises(ValueError, match="Missing values for variables: x, y.*"): # Expect specific variable names in message
            self.calculator.evaluate_expression("x + y", {})
        with pytest.raises(ValueError, match="Missing values for variables: x.*"):
            self.calculator.evaluate_expression("x + 1", {}) # No variables provided for expression with variables

    def test_evaluate_expression_error_handling_invalid_variable_values(self):
        # Covers: Error handling: invalid variable values (non-numeric, if sympy allows it, it might evaluate to non-numeric)
        with pytest.raises(ValueError, match="Evaluation error: Invalid variable value for 'x'.*"): # Expect specific variable name
            self.calculator.evaluate_expression("x + 1", {"x": "not_a_number"})
        with pytest.raises(ValueError, match="Evaluation error: Invalid variable value for 'y'.*"): # Expect specific variable name
            self.calculator.evaluate_expression("x + y", {"x": 1, "y": "invalid"})
        with pytest.raises(ValueError, match="Evaluation error: Invalid variable value for 'x'.*"): # Symbolic substitution should be caught
            self.calculator.evaluate_expression("x + 1", {"x": "2*a"})

    # Test partitions for differentiate_expression:
    # - Simple differentiation
    # - Differentiation with respect to different variables
    # - Differentiation of complex expressions (product rule, chain rule, etc.)
    # - Differentiation of expressions with constants and functions
    # - Edge cases: differentiating a constant, differentiating an expression without the variable
    # - Error handling: invalid variable (empty, non-symbol), invalid expression

    def test_differentiate_expression_simple(self):
        # Covers: Simple differentiation
        assert sympify(self.calculator.differentiate_expression("x**2", "x")) == sympify("2*x")
        assert sympify(self.calculator.differentiate_expression("3*y", "y")) == sympify("3")
        assert sympify(self.calculator.differentiate_expression("4*z**3", "z")) == sympify("12*z**2")

    def test_differentiate_expression_different_variables(self):
        # Covers: Differentiation with respect to different variables
        assert sympify(self.calculator.differentiate_expression("x*y + z", "x")) == sympify("y")
        assert sympify(self.calculator.differentiate_expression("x*y + z", "y")) == sympify("x")
        assert sympify(self.calculator.differentiate_expression("x*y + z", "z")) == sympify("1")
        assert sympify(self.calculator.differentiate_expression("sin(x*y)", "x")) == sympify("y*cos(x*y)")

    def test_differentiate_expression_complex(self):
        # Covers: Differentiation of complex expressions (product rule, chain rule, etc.)
        assert sympify(self.calculator.differentiate_expression("sin(x**2)", "x")) == sympify("2*x*cos(x**2)")
        assert sympify(self.calculator.differentiate_expression("x*exp(x)", "x")) == sympify("x*exp(x) + exp(x)")
        assert sympify(self.calculator.differentiate_expression("log(x**3)", "x")) == sympify("3/(x*log(10))")
        assert (sympify(self.calculator.differentiate_expression("(x+1)/(x-1)", "x")) - sympify("-(x + 1)/(x - 1)**2 + 1/(x - 1)")).simplify() == 0 # Quotient rule

    def test_differentiate_expression_with_constants_and_functions(self):
        # Covers: Differentiation of expressions with constants and functions
        assert sympify(self.calculator.differentiate_expression("pi*x", "x")) == sympify("pi")
        assert sympify(self.calculator.differentiate_expression("e**x", "x")) == sympify("exp(x)")
        assert sympify(self.calculator.differentiate_expression("tan(x)", "x")) == sympify("tan(x)**2 + 1")
        assert sympify(self.calculator.differentiate_expression("ln(x)", "x")) == sympify("1/x")
        assert sympify(self.calculator.differentiate_expression("log(x, 10)", "x")) == sympify("1/(x*log(10))")

    def test_differentiate_expression_edge_cases(self):
        # Covers: Edge cases: differentiating a constant, differentiating an expression without the variable
        assert sympify(self.calculator.differentiate_expression("5", "x")) == sympify("0")
        assert sympify(self.calculator.differentiate_expression("x + y", "z")) == sympify("0")
        assert sympify(self.calculator.differentiate_expression("pi", "x")) == sympify("0")

    def test_differentiate_expression_error_handling(self):
        # Covers: Error handling: invalid variable, invalid expression
        with pytest.raises(ValueError, match="Invalid differentiation variable"): # Empty string
            self.calculator.differentiate_expression("x**2", "")
        with pytest.raises(ValueError, match="Invalid differentiation variable"): # Number as variable
            self.calculator.differentiate_expression("x**2", "123")
        with pytest.raises(ValueError, match="Invalid expression:"): # Bad expression syntax
            self.calculator.differentiate_expression("x + *", "x")
        with pytest.raises(ValueError, match="Invalid differentiation variable"): # Multi-symbol variable
            self.calculator.differentiate_expression("x", "x + y")

    # Test partitions for integrate_indefinite:
    # - Simple indefinite integration
    # - Integration with respect to different variables
    # - Integration of complex expressions
    # - Integration of expressions with constants and functions
    # - Error handling: invalid variable, invalid expression, non-elementary integral (outputting Integral object string)

    def test_integrate_indefinite_simple(self):
        # Covers: Simple indefinite integration
        result = self.calculator.integrate_indefinite("x", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("x**2/2")
        result = self.calculator.integrate_indefinite("1", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("x")
        result = self.calculator.integrate_indefinite("sin(x)", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("-cos(x)")
        result = self.calculator.integrate_indefinite("cos(x)", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("sin(x)")
        result = self.calculator.integrate_indefinite("exp(x)", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("exp(x)")

    def test_integrate_indefinite_different_variables(self):
        # Covers: Integration with respect to different variables
        result = self.calculator.integrate_indefinite("x*y", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("x**2*y/2")
        result = self.calculator.integrate_indefinite("x*y", "y")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("x*y**2/2")
        result = self.calculator.integrate_indefinite("x + y", "z")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("z*(x + y)") # integrates as a constant

    def test_integrate_indefinite_complex(self):
        # Covers: Integration of complex expressions
        result = self.calculator.integrate_indefinite("x*exp(x)", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("(x - 1)*exp(x)")
        result = self.calculator.integrate_indefinite("1/(x**2 + 1)", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("atan(x)")
        result = self.calculator.integrate_indefinite("log(x)", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("x*log(x, 10) - x/log(10)") # log(x) is base 10 as per documentation

    def test_integrate_indefinite_with_constants_and_functions(self):
        # Covers: Integration of expressions with constants and functions
        result = self.calculator.integrate_indefinite("pi", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("pi*x")
        result = self.calculator.integrate_indefinite("e**x", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("exp(x)")
        result = self.calculator.integrate_indefinite("ln(x)", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("x*log(x) - x") # ln is natural log
        result = self.calculator.integrate_indefinite("log(x, 10)", "x")
        assert result.endswith(" + C")
        assert sympify(result.replace(" + C", "")) == sympify("x*log(x, 10) - x/log(10)") # log(x, 10) is base 10

    def test_integrate_indefinite_non_elementary_integral(self):
        # Covers: Sympy returns Integral object for non-elementary integrals.
        # The Calculator should return the string representation of this.
        result1 = self.calculator.integrate_indefinite("exp(x**2)", "x")
        assert sympify(result1.replace(" + C", "")) == sympify("sqrt(pi)*erfi(x)/2")
        assert result1.endswith(" + C")
        result2 = self.calculator.integrate_indefinite("sin(x)/x", "x")
        assert "Si(x)" in result2
        assert result2.endswith(" + C")


    def test_integrate_indefinite_error_handling(self):
        # Covers: Error handling: invalid variable, invalid expression
        with pytest.raises(ValueError, match="Invalid integration variable"): # Empty string
            self.calculator.integrate_indefinite("x", "")
        with pytest.raises(ValueError, match="Invalid integration variable"): # Number as variable
            self.calculator.integrate_indefinite("x", "123")
        with pytest.raises(ValueError, match="Invalid expression:"): # Bad expression syntax
            self.calculator.integrate_indefinite("x + *", "x")
        with pytest.raises(ValueError, match="Invalid integration variable"): # Multi-symbol variable
            self.calculator.integrate_indefinite("x", "x + y")

    # Test partitions for integrate_definite:
    # - Simple definite integration
    # - Integration with respect to different variables and numerical bounds
    # - Integration with respect to different variables and symbolic bounds
    # - Integration of complex expressions with bounds
    # - Edge cases: bounds are equal, bounds are expressions that evaluate to equal, infinite bounds (if supported by sympy), bounds leading to undefined results
    # - Error handling: invalid bounds, invalid variable, invalid expression, divergent integral (outputting oo/-oo or nan)

    def test_integrate_definite_simple(self):
        # Covers: Simple definite integration
        assert sympify(self.calculator.integrate_definite("x", "x", "0", "1")) == sympify("1/2")
        assert sympify(self.calculator.integrate_definite("sin(x)", "x", "0", "pi")) == sympify("2")
        assert sympify(self.calculator.integrate_definite("cos(x)", "x", "0", "pi/2")) == sympify("1")

    def test_integrate_definite_numerical_bounds(self):
        # Covers: Integration with respect to different variables and numerical bounds
        assert sympify(self.calculator.integrate_definite("x**2", "x", "0", "2")) == sympify("8/3")
        assert sympify(self.calculator.integrate_definite("exp(x)", "x", "0", "1")) == sympify("E - 1")
        assert sympify(self.calculator.integrate_definite("1/x", "x", "1", "exp(1)")) == sympify("1") # ln(e) - ln(1) = 1 - 0 = 1

    def test_integrate_definite_symbolic_bounds(self):
        # Covers: Integration with respect to different variables and symbolic bounds
        assert sympify(self.calculator.integrate_definite("y", "y", "a", "b")) == sympify("-a**2/2 + b**2/2")
        assert sympify(self.calculator.integrate_definite("x", "x", "0", "z")) == sympify("z**2/2")
        assert sympify(self.calculator.integrate_definite("c*x", "x", "0", "d")) == sympify("c*d**2/2")

    def test_integrate_definite_complex_with_bounds(self):
        # Covers: Integration of complex expressions with bounds
        assert sympify(self.calculator.integrate_definite("x*exp(x)", "x", "0", "1")) == sympify("1")
        assert sympify(self.calculator.integrate_definite("1/(x**2 + 1)", "x", "0", "1")) == sympify("pi/4")
        assert sympify(self.calculator.integrate_definite("log(x)", "x", "1", "e")) == sympify("1/log(10)") # log(x) is base 10 as per documentation

    def test_integrate_definite_edge_cases_bounds_equal(self):
        # Covers: Edge cases: bounds are equal
        assert sympify(self.calculator.integrate_definite("x**2", "x", "5", "5")) == sympify("0")
        assert sympify(self.calculator.integrate_definite("x**2", "x", "a", "a")) == sympify("0")
        assert sympify(self.calculator.integrate_definite("x**2", "x", "2*y", "2*y")) == sympify("0")

    def test_integrate_definite_edge_cases_infinite_bounds(self):
        # Covers: Edge cases: infinite bounds (if supported by sympy)
        assert sympify(self.calculator.integrate_definite("exp(-x)", "x", "0", "oo")) == sympify("1")
        assert sympify(self.calculator.integrate_definite("1/x**2", "x", "1", "oo")) == sympify("1")
        assert sympify(self.calculator.integrate_definite("sin(x)/x", "x", "0", "oo")) == sympify("pi/2") # Dirichlet integral

    def test_integrate_definite_error_handling_invalid_bounds(self):
        # Covers: Error handling: invalid bounds (syntax, non-parsable as expression or number)

        with pytest.raises(ValueError, match="Invalid lower bound:"): # Empty string
            self.calculator.integrate_definite("x", "x", "", "1")
        with pytest.raises(ValueError, match="Invalid upper bound:"): # Empty string
            self.calculator.integrate_definite("x", "x", "0", "")
        with pytest.raises(ValueError, match="Invalid lower bound:"): # Division by zero in bound itself
            self.calculator.integrate_definite("x", "x", "1/0", "1")
        with pytest.raises(ValueError, match="Invalid lower bound:"): # Bad syntax
            self.calculator.integrate_definite("x", "x", "a + * b", "1")
        with pytest.raises(ValueError, match="Invalid upper bound:"): # Bad syntax
            self.calculator.integrate_definite("x", "x", "0", "a + * b")

    def test_integrate_definite_error_handling_invalid_variable_or_expression(self):
        # Covers: Error handling: invalid variable, invalid expression
        with pytest.raises(ValueError, match="Invalid integration variable"): # Empty string
            self.calculator.integrate_definite("x", "", "0", "1")
        with pytest.raises(ValueError, match="Invalid integration variable"): # Number as variable
            self.calculator.integrate_definite("x", "123", "0", "1")
        with pytest.raises(ValueError, match="Invalid expression:"): # Bad expression syntax
            self.calculator.integrate_definite("x + *", "x", "0", "1")
        with pytest.raises(ValueError, match="Invalid integration variable"): # Multi-symbol variable
            self.calculator.integrate_definite("x", "x + y", "0", "1")

    def test_integrate_definite_error_handling_divergent_integral(self):
        # Covers: Error handling: bounds that make the integral diverge.
        # Sympy returns oo or -oo or nan for divergent integrals. The Calculator should return this as a string.
        assert sympify(self.calculator.integrate_definite("1/x", "x", "0", "1")) == sympify("oo")
        assert sympify(self.calculator.integrate_definite("1/x", "x", "1", "oo")) == sympify("oo")
        assert sympify(self.calculator.integrate_definite("x", "x", "0", "oo")) == sympify("oo")
        assert sympify(self.calculator.integrate_definite("tan(x)", "x", "0", "pi/2")) == sympify("oo") # Integral of tan(x) from 0 to pi/2 diverges
        assert sympify(self.calculator.integrate_definite("1/(x-1)", "x", "0", "2")) == sympify("nan") # Integral over singularity (Sympy returns NaN by default)

    def test_integrate_definite_non_elementary_integral(self):
        # Covers: Sympy returns Integral object for non-elementary integrals, even for definite.
        assert sympify(self.calculator.integrate_definite("exp(x**2)", "x", "0", "1")) == sympify("sqrt(pi)*erfi(1)/2")
