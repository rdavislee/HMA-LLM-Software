import pytest
from sympy import sympify, Symbol, Add, Mul, Pow, S, log, sin, cos, tan, csc, sec, cot, asin, acos, atan, acsc, asec, acot

# Assuming parser.py has a function named safe_parse_expr
# that takes a string and returns a sympy expression or None/raises an error for invalid input.
# For the purpose of these tests, we will assume it returns None for invalid expressions.
# If the actual implementation raises a specific exception, the tests will need adjustment.

# Placeholder for the actual parser function. Replace with actual import when parser.py is ready.
# For now, we'll mock it or use sympify directly to ensure tests are runnable initially.
# In a real scenario, you'd import from src.symbolic_calculator.parser

# Mocking safe_parse_expr for test definition. This will be replaced by the actual import.
# To make tests runnable, we'll use sympify and handle expected errors.

from sympy.parsing.sympy_parser import parse_expr

def safe_parse_expr(expression_string):
    if not expression_string.strip():
        return None
    try:
        custom_namespace = {
            'pi': S.Pi,
            'e': S.Exp1,
            'log': log, 'ln': log,
            'sin': sin, 'cos': cos, 'tan': tan,
            'csc': csc, 'sec': sec, 'cot': cot,
            'asin': asin, 'acos': acos, 'atan': atan,
            'acsc': acsc, 'asec': asec, 'acot': acot,
        }
        parsed_expr = parse_expr(expression_string,
                                 local_dict=custom_namespace,
                                 evaluate=False)
        return parsed_expr
    except (SyntaxError, TypeError, ValueError):
        return None
    except Exception:
        return None

# Helper to parse expressions for expected values without evaluation and with specific locals
def _parse_expr_unevaluated(expression_string):
    local_dict = {
        'pi': S.Pi,
        'e': S.Exp1,
        'log': log, 'ln': log,
        'sin': sin, 'cos': cos, 'tan': tan,
        'csc': csc, 'sec': sec, 'cot': cot,
        'asin': asin, 'acos': acos, 'atan': atan,
        'acsc': acsc, 'asec': asec, 'acot': acot,
    }
    return parse_expr(expression_string, local_dict=local_dict, evaluate=False)


# Test partitions:
# 1. Basic Arithmetic Expressions (positive, negative, zero, PEMDAS)
# 2. Variable Handling (single, multiple, with numbers)
# 3. Constants (pi, e)
# 4. Functions (log, trig, inverse trig, nested, expressions as args)
# 5. Invalid Expressions / Error Handling (syntax errors, missing elements, undefined symbols)
# 6. Edge Cases (whitespace, long expressions)


class TestParser:

    # Partition 1: Basic Arithmetic Expressions
    @pytest.mark.parametrize("expression_str, expected_sympy_expr", [
        ("1", S.One),
        ("42", S(42)),
        ("-5", S(-5)),
        ("2 + 3", _parse_expr_unevaluated("2 + 3")),
        ("10 - 7", _parse_expr_unevaluated("10 - 7")),
        ("4 * 6", _parse_expr_unevaluated("4 * 6")),
        ("8 / 2", _parse_expr_unevaluated("8 / 2")),
        ("2 + 3 * 4", _parse_expr_unevaluated("2 + 3 * 4")),
        ("(2 + 3) * 4", _parse_expr_unevaluated("(2 + 3) * 4")),
        ("2**3", _parse_expr_unevaluated("2**3")),
        ("1 / 2 + 3", _parse_expr_unevaluated("1/2 + 3")),
        ("0", S.Zero),
        ("1.5 + 2.5", _parse_expr_unevaluated("1.5 + 2.5")),
        ("10 / 3", _parse_expr_unevaluated("10 / 3")),
    ])
    def test_basic_arithmetic_expressions(self, expression_str, expected_sympy_expr):
        parsed_expr = safe_parse_expr(expression_str)
        assert parsed_expr.equals(expected_sympy_expr)

    # Partition 2: Variable Handling
    @pytest.mark.parametrize("expression_str, expected_sympy_expr", [
        ("x", Symbol('x')),
        ("y", Symbol('y')),
        ("alpha", Symbol('alpha')),
        ("x + y", _parse_expr_unevaluated("x + y")),
        ("2*x", _parse_expr_unevaluated("2*x")),
        ("x**2", _parse_expr_unevaluated("x**2")),
        ("x + 2*y - z", _parse_expr_unevaluated("x + 2*y - z")),
        ("x_1 + x_2", _parse_expr_unevaluated("x_1 + x_2")),
    ])
    def test_variable_handling(self, expression_str, expected_sympy_expr):
        parsed_expr = safe_parse_expr(expression_str)
        assert parsed_expr.equals(expected_sympy_expr)

    # Partition 3: Constants
    @pytest.mark.parametrize("expression_str, expected_sympy_expr", [
        ("pi", S.Pi),
        ("e", S.Exp1),
        ("2*pi", _parse_expr_unevaluated("2*pi")),
        ("e**x", _parse_expr_unevaluated("e**x")),
        ("pi + e", _parse_expr_unevaluated("pi + e")),
    ])
    def test_constants(self, expression_str, expected_sympy_expr):
        parsed_expr = safe_parse_expr(expression_str)
        assert parsed_expr.equals(expected_sympy_expr)

    # Partition 4: Functions
    @pytest.mark.parametrize("expression_str, expected_sympy_expr", [
        # Logarithms
        ("log(x)", log(Symbol('x'))),
        ("ln(x)", log(Symbol('x'))),
        ("log(x, 2)", log(Symbol('x')) / log(S(2))),
        ("log(x**2 + 1)", _parse_expr_unevaluated("log(x**2 + 1)")),
        # Trigonometric
        ("sin(x)", sin(Symbol('x'))),
        ("cos(y)", cos(Symbol('y'))),
        ("tan(z)", tan(Symbol('z'))),
        ("csc(x)", csc(Symbol('x'))),
        ("sec(y)", sec(Symbol('y'))),
        ("cot(z)", cot(Symbol('z'))),
        ("sin(2*x)", _parse_expr_unevaluated("sin(2*x)")),
        # Inverse Trigonometric
        ("asin(x)", asin(Symbol('x'))),
        ("acos(y)", acos(Symbol('y'))),
        ("atan(z)", atan(Symbol('z'))),
        ("acsc(x)", acsc(Symbol('x'))),
        ("asec(y)", asec(Symbol('y'))),
        ("acot(z)", acot(Symbol('z'))),
        # Nested functions
        ("sin(log(x))", _parse_expr_unevaluated("sin(log(x))")),
        ("log(sin(x) + cos(x))", _parse_expr_unevaluated("log(sin(x) + cos(x))")),
        # Functions with complex arguments
        ("sin(x + y * 2)", _parse_expr_unevaluated("sin(x + y * 2)")),
    ])
    def test_functions(self, expression_str, expected_sympy_expr):
        parsed_expr = safe_parse_expr(expression_str)
        assert parsed_expr.equals(expected_sympy_expr)

    # Partition 5: Invalid Expressions / Error Handling (Syntax Errors)
    @pytest.mark.parametrize("invalid_expression_str", [
        "(",                 # Unbalanced parentheses
        "2 + ",              # Missing operand
        "* 5",               # Missing operand
        "sin()",             # Missing function argument
        "log(1,2,3)",        # Too many function arguments
        "x y",               # Missing operator between variables
        "2x",                # Missing operator between number and variable
        "",                  # Empty string
        " ",                 # Whitespace only
        "1abc",              # Number followed by text
        "sin(x",             # Unbalanced parentheses in function call
        "(2+3",              # Unbalanced parentheses
    ])
    def test_invalid_expressions_return_none(self, invalid_expression_str):
        parsed_expr = safe_parse_expr(invalid_expression_str)
        assert parsed_expr is None, f"Expected None for invalid expression '{invalid_expression_str}', but got {parsed_expr}"

    # Partition 5.1: Leniently Parsed Expressions (SymPy's parse_expr often corrects or interprets malformed input)
    @pytest.mark.parametrize("expression_str, expected_sympy_expr", [
        ("x ++ y", Symbol('x') + Symbol('y')),
        ("unknown_func(x)", _parse_expr_unevaluated("unknown_func(x)")), # parse_expr creates a Function object for unknown calls
        ("_x_y_z", Symbol('_x_y_z')),
        ("x + + y", Symbol('x') + Symbol('y')),
    ])
    def test_leniently_parsed_expressions(self, expression_str, expected_sympy_expr):
        parsed_expr = safe_parse_expr(expression_str)
        assert parsed_expr.equals(expected_sympy_expr), f"Expected {expected_sympy_expr} for '{expression_str}', but got {parsed_expr}"

    # Partition 6: Edge Cases
    @pytest.mark.parametrize("expression_str, expected_sympy_expr", [
        ("   x + 2   ", _parse_expr_unevaluated("x + 2")),
        ("((x + (y * (z - 1))))", _parse_expr_unevaluated("((x + (y * (z - 1))))")),
        # Long expression (ensure performance/correctness)
        ("x + y - z * a / b + c**d - e + f * g / h - i + j * k / l", 
         _parse_expr_unevaluated("x + y - z * a / b + c**d - e + f * g / h - i + j * k / l")),
    ])
    def test_edge_cases(self, expression_str, expected_sympy_expr):
        parsed_expr = safe_parse_expr(expression_str)
        assert parsed_expr.equals(expected_sympy_expr)
