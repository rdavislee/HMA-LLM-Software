import sympy
from sympy.abc import symbols, C, pi, E

class Calculator:
    # These helper methods are designed to ensure inputs are SymPy objects.
    # They can handle both strings (by sympifying them) and pre-existing SymPy objects.
    def _sympify_expression(self, expression_input):
        if isinstance(expression_input, (sympy.Expr, sympy.Symbol, sympy.Integer, sympy.Float)):
            return expression_input
        if not isinstance(expression_input, str):
            raise TypeError("Expression must be a string or a SymPy object.")
        try:
            # Use evaluate=False to prevent immediate evaluation, allowing for more control
            return sympy.sympify(expression_input, evaluate=False)
        except (sympy.SympifyError, SyntaxError) as e:
            raise sympy.SympifyError(f"Could not sympify expression '{expression_input}': {e}")

    def _sympify_variable(self, var_input):
        if isinstance(var_input, sympy.Symbol):
            return var_input
        if not isinstance(var_input, str):
            raise TypeError("Variable must be a string or a SymPy Symbol.")
        try:
            return sympy.sympify(var_input)
        except (sympy.SympifyError, SyntaxError) as e:
            raise sympy.SympifyError(f"Could not sympify variable '{var_input}': {e}")

    def differentiate(self, expr_obj, var_obj):
        """
        Computes the derivative of an expression with respect to a variable.
        Args:
            expr_obj (sympy.Expr): The expression to differentiate.
            var_obj (sympy.Symbol): The variable to differentiate with respect to.
        Returns:
            sympy.Expr: The derivative of the expression.
        """
        if isinstance(expr_obj, sympy.log) and len(expr_obj.args) == 2:
            arg = expr_obj.args[0]
            base = expr_obj.args[1]
            d_arg_dx = sympy.diff(arg, var_obj)
            if d_arg_dx != 0:
                return d_arg_dx / (arg * sympy.log(base))
            else:
                return sympy.Integer(0)
        result = sympy.diff(expr_obj, var_obj)
        return result

    def integrate_indefinite(self, expr_obj, var_obj):
        """
        Computes the indefinite integral of an expression with respect to a variable,
        adding a dynamic constant of integration (C, C1, C2, etc.) to avoid collision.
        Args:
            expr_obj (sympy.Expr): The expression to integrate.
            var_obj (sympy.Symbol): The variable to integrate with respect to.
        Returns:
            sympy.Expr: The indefinite integral including the constant of integration.
        """
        integral_result = sympy.integrate(expr_obj, var_obj)

        # Determine suitable constant of integration (C, C1, C2, etc.)
        # Get all free symbols in the integral result and the original expression
        all_symbols = set(integral_result.free_symbols) | set(expr_obj.free_symbols)

        constant_name = "C"
        i = 0
        # Check for 'C', then 'C1', 'C2', etc., until a non-conflicting name is found
        while symbols(constant_name) in all_symbols:
            i += 1
            constant_name = f"C{i}"
        
        constant = symbols(constant_name)
        
        return constant + integral_result

    def integrate_definite(self, expr_obj, var_obj, lower_bound_obj, upper_bound_obj):
        """
        Computes the definite integral of an expression with respect to a variable
        between specified lower and upper bounds.
        Args:
            expr_obj (sympy.Expr): The expression to integrate.
            var_obj (sympy.Symbol): The variable to integrate with respect to.
            lower_bound_obj (sympy.Expr): The lower bound of integration.
            upper_bound_obj (sympy.Expr): The upper bound of integration.
        Returns:
            sympy.Expr: The result of the definite integral.
        """
        result = sympy.integrate(expr_obj, (var_obj, lower_bound_obj, upper_bound_obj))
        return result

    def evaluate(self, expr_obj, substitutions_dict):
        """
        Evaluates an expression by substituting given values for variables.
        Args:
            expr_obj (sympy.Expr): The expression to evaluate.
            substitutions_dict (dict): A dictionary mapping sympy.Symbol objects
                                       to their substitution values (sympy.Expr or numbers).
        Returns:
            sympy.Expr: The evaluated expression.
        """
        if not isinstance(substitutions_dict, dict):
            raise TypeError("Substitutions must be a dictionary.")
        
        # The substitutions_dict is expected to already contain SymPy symbols as keys
        # and SymPy expressions/numbers as values, as prepared by test_calculator.py.
        result = expr_obj.subs(substitutions_dict)
        return result
