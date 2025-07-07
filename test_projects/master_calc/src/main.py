from src.symbolic_calculator.parser import parse_expression
from src.symbolic_calculator.calculator import Calculator
import sympy
from sympy.abc import symbols # Needed for creating symbols for differentiation/integration variables and evaluation substitutions

def get_expression_input(previous_result=None):
    """Prompts the user for an expression, optionally reusing a previous result."""
    while True:
        prompt = "Enter a mathematical expression (e.g., 'x**2 + 2*x + 1')"
        if previous_result is not None:
            prompt += f" or press Enter to use previous result '{previous_result}'"
        prompt += ": "
        
        user_input = input(prompt).strip()

        if not user_input and previous_result is not None:
            print(f"Using previous result: {previous_result}")
            return previous_result
        elif not user_input and previous_result is None:
            print("No previous result to use. Please enter an expression.")
            continue

        # Check for exit command
        if user_input.lower() in ['exit', 'quit']:
            return user_input # Return string to be handled by main loop for exit

        expr_obj = parse_expression(user_input)
        if expr_obj is None:
            print("Error: Could not parse expression. Please check syntax and try again.")
        else:
            return expr_obj

def get_operation_input():
    """Prompts the user to choose an operation."""
    while True:
        print("\nChoose an operation:")
        print("  1. Evaluate (substitute values for variables)")
        print("  2. Differentiate")
        print("  3. Integrate (indefinite)")
        print("  4. Integrate (definite)")
        operation_choice = input("Enter choice (1-4): ").strip()
        if operation_choice in ['1', '2', '3', '4']:
            return operation_choice
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

def get_variable_input(prompt_message):
    """Prompts the user for a variable and returns a SymPy Symbol."""
    while True:
        var_str = input(prompt_message).strip()
        if not var_str:
            print("Variable cannot be empty. Please enter a variable.")
            continue
        try:
            var_sym = sympy.sympify(var_str)
            if not isinstance(var_sym, sympy.Symbol):
                print(f"Error parsing variable '{var_str}'. Please ensure it's a valid symbol name.")
                continue
            return var_sym
        except (sympy.SympifyError, ValueError):
            print(f"Error parsing variable '{var_str}'. Please ensure it's a valid symbol name.")
            continue

def get_substitutions_input(expression_obj):
    """
    Prompts the user for substitutions for evaluation.
    Returns a dictionary of {SymPy.Symbol: SymPy.Expr}.
    """
    free_symbols = expression_obj.free_symbols
    if not free_symbols:
        print("The expression has no free variables to substitute.")
        return {}

    substitutions = {}
    print(f"\nExpression has free variables: {', '.join(str(s) for s in free_symbols)}")
    print("Enter substitutions in 'var=value' format, separated by commas (e.g., 'x=5, y=pi/2').")
    print("Press Enter without input to skip substitution.")

    while True:
        user_input = input("Substitutions: ").strip()
        if not user_input:
            return {} # User chose to skip

        temp_subs = {}
        errors = [] # Initialize error list for current input line
        parts = user_input.split(',')
        
        for part in parts:
            stripped_part = part.strip() # Strip the part early
            # Process each part, collecting errors specific to this part
            # No immediate 'raise'
            
            if '=' not in stripped_part: # Use stripped_part here
                errors.append(f"Invalid substitution format: '{stripped_part}'. Expected 'var=value'.")
                continue # Move to next part
            
            var_str, value_str = stripped_part.split('=', 1) # Use stripped_part here
            var_str = var_str.strip()
            value_str = value_str.strip()
            
            if not var_str or not value_str:
                errors.append(f"Invalid substitution format: '{stripped_part}'. Expected 'var=value'.") # Use stripped_part here
                continue
            
            try:
                var_sym = sympy.sympify(var_str)
                if not isinstance(var_sym, sympy.Symbol):
                    errors.append(f"'{var_str}' is not a valid symbolic variable.")
                    continue
                
                if var_sym not in free_symbols:
                    print(f"Warning: Variable '{var_sym}' not found in the expression. It will be ignored.")
                    continue

                value_expr = parse_expression(value_str) 
                if value_expr is None:
                    errors.append(f"Could not parse value '{value_str}' for variable '{var_str}'.")
                    continue
                
                # If no errors for this part so far, add to temp_subs
                temp_subs[var_sym] = value_expr

            except sympy.SympifyError as e:
                errors.append(f"Error parsing variable '{var_str}': {e}")
            except Exception as e:
                errors.append(f"An unexpected error occurred processing '{stripped_part}': {e}")
        
        # After processing all parts:
        if errors:
            for error_msg in errors:
                print(f"Error in substitution input: {error_msg}")
            print("Please try entering substitutions again.")
            continue
        else:
            return temp_subs # If no errors, return the collected substitutions

def get_bounds_input():
    """Prompts the user for lower and upper bounds for definite integration."""
    while True:
        lower_str = input("Enter lower bound (e.g., '0' or 'a'): ").strip()
        upper_str = input("Enter upper bound (e.g., '1' or 'b'): ").strip()

        try:
            # Use parse_expression as bounds can be expressions (e.g., 'a', 'x+1')
            lower_bound_obj = parse_expression(lower_str)
            upper_bound_obj = parse_expression(upper_str)

            if lower_bound_obj is None:
                raise ValueError("Could not parse lower bound.")
            if upper_bound_obj is None:
                raise ValueError("Could not parse upper bound.")
            
            return lower_bound_obj, upper_bound_obj
        except ValueError as e:
            print(f"Error parsing bounds: {e}. Please try again.")
        except Exception as e:
            print(f"An unexpected error occurred while parsing bounds: {e}")

def main():
    calculator = Calculator()
    previous_result = None

    print("Welcome to the Symbolic Calculator CLI!")
    print("Type 'exit' or 'quit' at any prompt to exit.")

    while True:
        try:
            # 1. Get Expression
            expression = get_expression_input(previous_result)
            if isinstance(expression, str) and expression.lower() in ['exit', 'quit']:
                print("Exiting calculator. Goodbye!")
                return
            if expression is None: # Should not happen if get_expression_input handles it, but as a safeguard
                continue
            
            # 2. Get Operation
            operation_choice = get_operation_input()
            if operation_choice is None: # Should not happen if get_operation_input handles it, but as safeguard
                continue

            # 3. Get Parameters and Perform Calculation
            result = None
            if operation_choice == '1':  # Evaluate
                substitutions = get_substitutions_input(expression)
                if substitutions is not None: # get_substitutions_input returns {} if skipped, not None
                    result = calculator.evaluate(expression, substitutions)
            elif operation_choice == '2':  # Differentiate
                diff_var = get_variable_input("Differentiate with respect to variable (e.g., 'x'): ")
                if diff_var is not None:
                    result = calculator.differentiate(expression, diff_var)
            elif operation_choice == '3':  # Integrate (indefinite)
                int_var = get_variable_input("Integrate with respect to variable (e.g., 'x'): ")
                if int_var is not None:
                    result = calculator.integrate_indefinite(expression, int_var)
            elif operation_choice == '4':  # Integrate (definite)
                int_var = get_variable_input("Integrate with respect to variable (e.g., 'x'): ")
                if int_var is not None:
                    lower_bound, upper_bound = get_bounds_input()
                    if lower_bound is not None and upper_bound is not None:
                        result = calculator.integrate_definite(expression, int_var, lower_bound, upper_bound)
            
            if result is not None:
                print(f"\nResult: {result}")
                previous_result = result
            else:
                print("Operation could not be completed, or no result was generated.")

        except sympy.SymPyError as e:
            print(f"SymPy Error: {e}. Please check your input and try again.")
            previous_result = None # Clear previous result on error to avoid propagating bad state
        except TypeError as e:
            print(f"Input Type Error: {e}. Please ensure correct types for operations.")
            previous_result = None
        except ValueError as e:
            print(f"Input Value Error: {e}. Please check your input values.")
            previous_result = None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            previous_result = None # Clear previous result on error

        # 4. Ask to reuse result? -> Repeat
        while True:
            continue_choice = input("Do you want to perform another operation? (yes/no): ").strip().lower()
            if continue_choice in ['no', 'n']:
                print("Exiting calculator. Goodbye!")
                return
            elif continue_choice in ['yes', 'y']:
                break
            elif continue_choice in ['exit', 'quit']:
                print("Exiting calculator. Goodbye!")
                return
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()