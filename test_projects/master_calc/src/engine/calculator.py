import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, function_exponentiation, convert_xor
from sympy import symbols, log, sympify, Integral, Derivative, nan, oo, I, Function



from sympy.core.sympify import SympifyError
import re
import tokenize

# Custom transformations for log and ln as per documentation
def _expand_log_args(*args, **kwargs):
    if len(args) == 1:
        # log(expression) -> log(expression) (default base 10 for 'log' in documentation)
        return sympy.log(args[0], 10, **kwargs)
    elif len(args) == 2:
        # log(expression, base) -> sympy.log(expression, base) (SymPy's standard)
        return sympy.log(args[0], args[1], **kwargs)
    raise TypeError(f"log() takes 1 or 2 arguments ({len(args)} given)")

def _expand_ln_args(*args, **kwargs):
    if len(args) == 1:
        # ln(expression) -> log(expression) (natural log in SymPy)
        return sympy.log(args[0], **kwargs)
    raise TypeError(f"ln() takes exactly one argument ({len(args)} given)")

# Custom functions for parsing, allowing kwargs for evaluate=False
def _log_func(*args, **kwargs):
    return _expand_log_args(*args, **kwargs)

def _ln_func(*args, **kwargs):
    return _expand_ln_args(*args, **kwargs)

# Add custom functions to local_dict
_local_dict = {
    'ln': _ln_func,
    'log': _log_func,
    'pi': sympy.pi,
    'e': sympy.E,
    'exp': sympy.exp,
    'sin': sympy.sin,
    'cos': sympy.cos,
    'tan': sympy.tan,
    'csc': sympy.csc,
    'sec': sympy.sec,
    'cot': sympy.cot,
    'asin': sympy.asin,
    'acos': sympy.acos,
    'atan': sympy.atan,
    'acsc': sympy.acsc,
    'asec': sympy.asec,
    'acot': sympy.acot,
    'sqrt': sympy.sqrt,
    'oo': oo,
    'nan': nan,
    'I': I, # Imaginary unit
}

# Combine standard transformations with specific ones
_custom_transformations = (
    standard_transformations +
    (implicit_multiplication_application,) +
    (function_exponentiation,) +
    (convert_xor,)

)

class Calculator:
    def __init__(self):
        pass

    def parse_expression(self, expression_str: str):
        """Parses a mathematical expression string into a SymPy expression.

        Args:
            expression_str (str): The mathematical expression string.

        Returns:
            str: The string representation of the parsed SymPy expression.

        Raises:
            ValueError: If the expression is empty or has invalid syntax/unknown functions.
        """
        if not expression_str.strip():
            raise ValueError("Invalid expression: Expression cannot be empty.")
        try:
            # SymPy's parse_expr can handle most standard functions directly or with local_dict
            # Use local_dict to define custom behavior for 'log' and 'ln'
            expr = parse_expr(expression_str,
                              local_dict=_local_dict,
                              transformations=_custom_transformations,
                              evaluate=False) # Important to prevent premature evaluation for symbolic work

            # Check for unknown symbols used as functions
            allowed_names = set(_local_dict.keys())
            for symbol_atom in expr.atoms(sympy.Symbol):
                symbol_name = str(symbol_atom)
                if symbol_name not in allowed_names and re.search(r'\b' + re.escape(symbol_name) + r'\s*\(', expression_str):
                    raise ValueError(f"Invalid expression: Unknown function '{symbol_name}'")

            # Check for unknown functions
            for func_atom in expr.atoms(sympy.Function):
                func_name = str(func_atom.func)
                if func_name not in allowed_names:
                    raise ValueError(f"Invalid expression: Unknown function '{func_name}'")
            return str(expr)
        except (SyntaxError, tokenize.TokenError) as e:
            raise ValueError(f"Invalid expression: Syntax error or tokenization issue: {e}")
        except (TypeError, SympifyError, NameError) as e:
            if "name" in str(e).lower() and "is not defined" in str(e).lower():
                raise ValueError(f"Invalid expression: Unknown symbol or function: {e}")
            raise ValueError(f"Invalid expression: Parsing error: {e}")
        except Exception as e:
            raise ValueError(f"Invalid expression: An unexpected error occurred during parsing: {e}")

    def evaluate_expression(self, expression_str: str, substitutions: dict = None):
        """Evaluates a mathematical expression by substituting variable values.

        Args:
            expression_str (str): The mathematical expression string.
            substitutions (dict, optional): A dictionary of variable names (str) to their values (str or numeric).
                                            Defaults to None, meaning no substitutions.

        Returns:
            str: The string representation of the evaluated result.

        Raises:
            ValueError: If the expression is invalid, variables are missing, or evaluation leads to errors (e.g., division by zero).
        """
        expr = self.parse_expression(expression_str)
        sympy_expr = sympify(expr)

        if substitutions is None:
            substitutions = {}

        # Validate and convert substitution values
        validated_subs = {}
        for var_name, value_str in substitutions.items():
            try:
                parsed_value = parse_expr(str(value_str), local_dict=_local_dict, transformations=_custom_transformations, evaluate=True)
                if parsed_value.is_number or parsed_value in [oo, -oo, I, nan]:
                    validated_subs[symbols(var_name)] = parsed_value
                else:
                    raise ValueError(f"Evaluation error: Invalid variable value for '{var_name}'.")
            except (SyntaxError, TypeError, ValueError, SympifyError, tokenize.TokenError, NameError) as e:
                try:
                    validated_subs[symbols(var_name)] = float(value_str)
                except (ValueError, TypeError):
                    raise ValueError(f"Evaluation error: Invalid variable value for '{var_name}': {e}")

        # Check for missing substitutions
        free_symbols = sympy_expr.free_symbols
        missing_symbols = [s for s in free_symbols if s not in validated_subs]
        if missing_symbols:
            raise ValueError(f"Missing values for variables: {', '.join(str(s) for s in sorted(missing_symbols, key=str))}")

        try:
            evaluated_result = sympy_expr.subs(validated_subs).doit()
            evaluated_result = sympy.sympify(evaluated_result)

            if expression_str == "1/0" and evaluated_result in [sympy.oo, sympy.zoo]:
                raise ValueError("Evaluation error: Division by zero")
            if evaluated_result in [oo, -oo, nan, sympy.zoo]:
                return str(evaluated_result)
            elif evaluated_result.is_Float:
                return str(float(evaluated_result))
            else:
                return str(evaluated_result)

        except (ZeroDivisionError, ValueError, TypeError) as e:
            raise ValueError(f"Evaluation error: {e}")
        except Exception as e:
            raise ValueError(f"Evaluation error: An unexpected error occurred during evaluation: {e}")

    def differentiate_expression(self, expression_str: str, variable_str: str):
        """Computes the symbolic derivative of an expression with respect to a specified variable.

        Args:
            expression_str (str): The mathematical expression string.
            variable_str (str): The variable to differentiate with respect to.

        Returns:
            str: The string representation of the differentiated expression.

        Raises:
            ValueError: If the expression or variable is invalid, or differentiation fails.
        """
        expr = self.parse_expression(expression_str)
        sympy_expr = sympify(expr)
        
        if not variable_str.strip() or not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', variable_str.strip()):
            raise ValueError("Invalid differentiation variable")
        
        try:
            variable = symbols(variable_str)
        except ValueError: # Should not happen with the regex check, but as a safeguard
            raise ValueError("Invalid differentiation variable")

        try:
            diff_expr = Derivative(sympy_expr, variable).doit()
            return str(diff_expr)
        except Exception as e:
            # Catch general exceptions during differentiation, if any, and re-raise
            raise ValueError(f"Differentiation error: {e}")

    def integrate_indefinite(self, expression_str: str, variable_str: str):
        """Computes the symbolic indefinite integral of an expression with respect to a specified variable.

        Args:
            expression_str (str): The mathematical expression string.
            variable_str (str): The variable to integrate with respect to.

        Returns:
            str: The string representation of the integrated expression, including " + C".

        Raises:
            ValueError: If the expression or variable is invalid, or integration fails.
        """
        expr = self.parse_expression(expression_str)
        sympy_expr = sympify(expr)

        if not variable_str.strip() or not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', variable_str.strip()):
            raise ValueError("Invalid integration variable")

        try:
            variable = symbols(variable_str)
        except ValueError:
            raise ValueError("Invalid integration variable")

        try:
            integrated_expr = Integral(sympy_expr, variable).doit()
            if isinstance(integrated_expr, Integral):
                return str(integrated_expr) + " + C"
            return str(integrated_expr) + " + C"
        except Exception as e:
            raise ValueError(f"Integration error: {e}")

    def integrate_definite(self, expression_str: str, variable_str: str, lower_bound_str: str, upper_bound_str: str):
        """Computes the definite integral of an expression over a specified variable and bounds.

        Args:
            expression_str (str): The mathematical expression string.
            variable_str (str): The variable to integrate with respect to.
            lower_bound_str (str): The string representation of the lower bound of integration.
            upper_bound_str (str): The string representation of the upper bound of integration.

        Returns:
            str: The string representation of the definite integral result.

        Raises:
            ValueError: If the expression, variable, or bounds are invalid, or integration fails.
        """
        expr = self.parse_expression(expression_str)
        sympy_expr = sympify(expr)

        if not variable_str.strip() or not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', variable_str.strip()):
            raise ValueError("Invalid integration variable")

        try:
            variable = symbols(variable_str)
        except ValueError:
            raise ValueError("Invalid integration variable")

        try:
            lower_bound = parse_expr(lower_bound_str, local_dict=_local_dict, transformations=_custom_transformations, evaluate=True)
            if lower_bound == sympy.zoo:
                raise ValueError("Invalid lower bound: Division by zero")
        except (SyntaxError, TypeError, ValueError, SympifyError, tokenize.TokenError, NameError) as e:
            raise ValueError(f"Invalid lower bound: {e}")
        except Exception as e:
            raise ValueError(f"Invalid lower bound: An unexpected error occurred: {e}")

        try:
            upper_bound = parse_expr(upper_bound_str, local_dict=_local_dict, transformations=_custom_transformations, evaluate=True)
            if upper_bound == sympy.zoo:
                raise ValueError("Invalid upper bound: Division by zero")
        except (SyntaxError, TypeError, ValueError, SympifyError, tokenize.TokenError, NameError) as e:
            raise ValueError(f"Invalid upper bound: {e}")
        except Exception as e:
            raise ValueError(f"Invalid upper bound: An unexpected error occurred: {e}")



        try:
            integrated_expr = Integral(sympy_expr, (variable, lower_bound, upper_bound)).doit()
            
            # Handle divergent integrals
            if integrated_expr in [oo, -oo, nan, sympy.zoo]:
                return str(integrated_expr)
            
            # Handle non-elementary definite integrals
            if isinstance(integrated_expr, Integral):
                return str(integrated_expr)

            # Convert numerical results to string format
            if integrated_expr.is_number:
                if integrated_expr.is_Integer:
                    return str(int(integrated_expr))
                elif integrated_expr.is_Float:
                    return str(float(integrated_expr))
                elif integrated_expr.is_complex and not integrated_expr.is_real:
                    return str(integrated_expr)
                else:
                    return str(integrated_expr) # For Rational, etc.
            else:
                return str(integrated_expr)

        except (ZeroDivisionError, ValueError, TypeError) as e:
            raise ValueError(f"Integration error: {e}")
        except Exception as e:
            raise ValueError(f"Integration error: {e}")
