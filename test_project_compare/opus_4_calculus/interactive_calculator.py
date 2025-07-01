#!/usr/bin/env python3
"""
Interactive Mathematical Expression Calculator
A command-line interface for testing the opus 4 calculus implementation.
"""

import sys
import traceback
from utils import (
    evaluate, derivative, indefinite_integral, definite_integral,
    simplify, get_variables, substitute
)


class InteractiveCalculator:
    def __init__(self):
        self.last_expression = None
        self.last_result = None
    
    def show_menu(self):
        print('\n=== Mathematical Expression Calculator (Opus 4) ===')
        print('1. Parse and evaluate expression')
        print('2. Differentiate expression')
        print('3. Integrate indefinite')
        print('4. Integrate definite')
        print('5. Simplify expression')
        print('6. Get variables from expression')
        print('7. Substitute values in expression')
        print('8. Full workflow (evaluate → differentiate → integrate)')
        print('9. Show examples')
        print('0. Exit')
        print('======================================================')
        
        return input('Choose an option (0-9): ').strip()
    
    def get_input(self, prompt):
        """Get user input with proper handling."""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)
    
    def parse_and_evaluate(self):
        """Parse and evaluate an expression."""
        print('\n--- Parse and Evaluate Expression ---')
        
        expression_str = self.get_input('Enter a mathematical expression: ')
        if not expression_str:
            print('✗ No expression provided.')
            return None
        
        self.last_expression = expression_str
        print(f'\nExpression: "{expression_str}"')
        
        try:
            # Get variables in the expression
            variables = get_variables(expression_str)
            
            if not variables:
                print('No variables found. Evaluating directly...')
                result = evaluate(expression_str)
                print(f'✓ Result: {result}')
                self.last_result = result
                return result
            
            print(f'Found variables: {", ".join(variables)}')
            
            # Get values for variables
            var_values = {}
            for var in variables:
                while True:
                    value_str = self.get_input(f'Enter value for "{var}" (or press Enter to skip): ')
                    if not value_str:
                        break
                    try:
                        var_values[var] = float(value_str)
                        break
                    except ValueError:
                        print(f'✗ Invalid number: "{value_str}". Please try again.')
            
            if var_values:
                result = evaluate(expression_str, var_values)
                print(f'✓ Result: {result}')
                print(f'With values: {", ".join(f"{k}={v}" for k, v in var_values.items())}')
                self.last_result = result
                return result
            else:
                result = evaluate(expression_str)
                print(f'✓ Symbolic result: {result}')
                self.last_result = result
                return result
                
        except Exception as e:
            print(f'✗ Error: {str(e)}')
            return None
    
    def differentiate_expression(self):
        """Differentiate an expression."""
        print('\n--- Differentiate Expression ---')
        
        expression_str = self.get_input('Enter expression (or press Enter to use last): ')
        if not expression_str and self.last_expression:
            expression_str = self.last_expression
            print(f'Using last expression: "{expression_str}"')
        elif not expression_str:
            print('✗ No expression provided.')
            return None
        
        variable = self.get_input('Enter variable to differentiate with respect to (e.g., x): ')
        if not variable:
            print('✗ No variable provided.')
            return None
        
        try:
            result = derivative(expression_str, variable)
            print(f'✓ Original: {expression_str}')
            print(f'✓ Derivative d/d{variable}: {result}')
            self.last_result = result
            return result
        except Exception as e:
            print(f'✗ Error: {str(e)}')
            return None
    
    def integrate_indefinite(self):
        """Compute indefinite integral."""
        print('\n--- Indefinite Integration ---')
        
        expression_str = self.get_input('Enter expression (or press Enter to use last): ')
        if not expression_str and self.last_expression:
            expression_str = self.last_expression
            print(f'Using last expression: "{expression_str}"')
        elif not expression_str:
            print('✗ No expression provided.')
            return None
        
        variable = self.get_input('Enter variable to integrate with respect to (e.g., x): ')
        if not variable:
            print('✗ No variable provided.')
            return None
        
        try:
            result = indefinite_integral(expression_str, variable)
            print(f'✓ Original: {expression_str}')
            print(f'✓ Indefinite integral ∫{expression_str} d{variable}: {result}')
            self.last_result = result
            return result
        except Exception as e:
            print(f'✗ Error: {str(e)}')
            print('This expression may require more advanced integration techniques.')
            return None
    
    def integrate_definite(self):
        """Compute definite integral."""
        print('\n--- Definite Integration ---')
        
        expression_str = self.get_input('Enter expression (or press Enter to use last): ')
        if not expression_str and self.last_expression:
            expression_str = self.last_expression
            print(f'Using last expression: "{expression_str}"')
        elif not expression_str:
            print('✗ No expression provided.')
            return None
        
        variable = self.get_input('Enter variable to integrate with respect to (e.g., x): ')
        if not variable:
            print('✗ No variable provided.')
            return None
        
        try:
            lower_str = self.get_input('Enter lower bound: ')
            upper_str = self.get_input('Enter upper bound: ')
            
            lower_bound = float(lower_str)
            upper_bound = float(upper_str)
            
            result = definite_integral(expression_str, variable, lower_bound, upper_bound)
            print(f'✓ Original: {expression_str}')
            print(f'✓ Definite integral from {lower_bound} to {upper_bound}: {result}')
            self.last_result = result
            return result
            
        except ValueError as e:
            print(f'✗ Invalid bounds: {str(e)}')
            return None
        except Exception as e:
            print(f'✗ Error: {str(e)}')
            return None
    
    def simplify_expression(self):
        """Simplify an expression."""
        print('\n--- Simplify Expression ---')
        
        expression_str = self.get_input('Enter expression (or press Enter to use last): ')
        if not expression_str and self.last_expression:
            expression_str = self.last_expression
            print(f'Using last expression: "{expression_str}"')
        elif not expression_str:
            print('✗ No expression provided.')
            return None
        
        try:
            result = simplify(expression_str)
            print(f'✓ Original: {expression_str}')
            print(f'✓ Simplified: {result}')
            self.last_result = result
            return result
        except Exception as e:
            print(f'✗ Error: {str(e)}')
            return None
    
    def get_variables_from_expression(self):
        """Get all variables in an expression."""
        print('\n--- Get Variables ---')
        
        expression_str = self.get_input('Enter expression (or press Enter to use last): ')
        if not expression_str and self.last_expression:
            expression_str = self.last_expression
            print(f'Using last expression: "{expression_str}"')
        elif not expression_str:
            print('✗ No expression provided.')
            return None
        
        try:
            variables = get_variables(expression_str)
            print(f'✓ Expression: {expression_str}')
            if variables:
                print(f'✓ Variables found: {", ".join(variables)}')
            else:
                print('✓ No variables found (expression contains only constants)')
            self.last_result = variables
            return variables
        except Exception as e:
            print(f'✗ Error: {str(e)}')
            return None
    
    def substitute_values(self):
        """Substitute values for variables in an expression."""
        print('\n--- Substitute Values ---')
        
        expression_str = self.get_input('Enter expression (or press Enter to use last): ')
        if not expression_str and self.last_expression:
            expression_str = self.last_expression
            print(f'Using last expression: "{expression_str}"')
        elif not expression_str:
            print('✗ No expression provided.')
            return None
        
        try:
            # Get variables first
            variables = get_variables(expression_str)
            if not variables:
                print('✓ No variables found in expression.')
                return expression_str
            
            print(f'Available variables: {", ".join(variables)}')
            
            substitutions = {}
            for var in variables:
                value_str = self.get_input(f'Enter value for "{var}" (or press Enter to skip): ')
                if value_str:
                    try:
                        substitutions[var] = float(value_str)
                    except ValueError:
                        print(f'✗ Invalid number for {var}: "{value_str}". Skipping.')
            
            if not substitutions:
                print('✓ No substitutions made.')
                return expression_str
            
            result = substitute(expression_str, substitutions)
            print(f'✓ Original: {expression_str}')
            print(f'✓ Substitutions: {", ".join(f"{k}={v}" for k, v in substitutions.items())}')
            print(f'✓ Result: {result}')
            self.last_result = result
            return result
            
        except Exception as e:
            print(f'✗ Error: {str(e)}')
            return None
    
    def full_workflow(self):
        """Demonstrate full workflow: evaluate → differentiate → integrate."""
        print('\n=== Full Workflow Demo ===')
        
        expression_str = self.get_input('Enter expression for full workflow: ')
        if not expression_str:
            print('✗ No expression provided.')
            return
        
        print(f'\nWorking with expression: "{expression_str}"')
        
        # Step 1: Parse and show variables
        print('\n1. Analysis:')
        try:
            variables = get_variables(expression_str)
            if variables:
                print(f'   Variables: {", ".join(variables)}')
            else:
                print('   No variables (constant expression)')
        except Exception as e:
            print(f'   ✗ Error getting variables: {e}')
        
        # Step 2: Simplify
        print('\n2. Simplification:')
        try:
            simplified = simplify(expression_str)
            print(f'   Simplified: {simplified}')
        except Exception as e:
            print(f'   ✗ Error simplifying: {e}')
        
        # Step 3: Differentiate
        print('\n3. Differentiation:')
        variable = self.get_input('   Enter variable to differentiate with respect to: ')
        if variable:
            try:
                deriv = derivative(expression_str, variable)
                print(f'   d/d{variable}: {deriv}')
            except Exception as e:
                print(f'   ✗ Error differentiating: {e}')
        
        # Step 4: Indefinite Integration
        print('\n4. Indefinite Integration:')
        if variable:
            try:
                indef = indefinite_integral(expression_str, variable)
                print(f'   ∫{expression_str} d{variable}: {indef}')
            except Exception as e:
                print(f'   ✗ Error integrating: {e}')
        
        # Step 5: Definite Integration
        print('\n5. Definite Integration:')
        if variable:
            try:
                lower_str = self.get_input('   Enter lower bound (or press Enter to skip): ')
                upper_str = self.get_input('   Enter upper bound (or press Enter to skip): ')
                
                if lower_str and upper_str:
                    lower = float(lower_str)
                    upper = float(upper_str)
                    definite = definite_integral(expression_str, variable, lower, upper)
                    print(f'   ∫[{lower},{upper}] {expression_str} d{variable}: {definite}')
                else:
                    print('   Skipping definite integration.')
            except Exception as e:
                print(f'   ✗ Error with definite integration: {e}')
        
        # Step 6: Evaluation
        print('\n6. Evaluation:')
        try:
            variables = get_variables(expression_str)
            if variables:
                print(f'   Variables found: {", ".join(variables)}')
                var_values = {}
                for var in variables:
                    value_str = self.get_input(f'   Enter value for {var} (or press Enter to skip): ')
                    if value_str:
                        try:
                            var_values[var] = float(value_str)
                        except ValueError:
                            print(f'   ✗ Invalid value for {var}')
                
                if var_values:
                    result = evaluate(expression_str, var_values)
                    print(f'   Result: {result}')
                else:
                    result = evaluate(expression_str)
                    print(f'   Symbolic result: {result}')
            else:
                result = evaluate(expression_str)
                print(f'   Result: {result}')
        except Exception as e:
            print(f'   ✗ Error evaluating: {e}')
        
        print('\n=== Workflow Complete ===')
    
    def show_examples(self):
        """Show example expressions and usage."""
        print('\n=== Expression Examples ===')
        print('Basic arithmetic: 2*x + 3, x^2 + 3*x + 1')
        print('Trigonometric: sin(x), cos(x), tan(x)')
        print('Logarithmic: ln(x), log(x) (base 10)')
        print('Exponential: exp(x), e^x')
        print('Mixed: x^2 + sin(x) + ln(x)')
        print('Complex: (x + 1) * (x - 1), sin(x)^2 + cos(x)^2')
        print('')
        print('Constants: e (Euler\'s number), pi')
        print('Variables: any letter(s), e.g., x, y, theta, var1')
        print('')
        print('Integration examples:')
        print('  - Polynomials: x^2, x^3 + 2*x')
        print('  - Trigonometric: sin(x), cos(x)')
        print('  - Exponential: exp(x), e^x')
        print('  - Logarithmic: 1/x → ln(x)')
        print('')
        print('Differentiation examples:')
        print('  - Power rule: x^n → n*x^(n-1)')
        print('  - Trig: sin(x) → cos(x), cos(x) → -sin(x)')
        print('  - Chain rule: sin(x^2) → cos(x^2)*2*x')
        print('=============================\n')
    
    def run(self):
        """Main calculator loop."""
        print('Welcome to the Opus 4 Mathematical Expression Calculator!')
        print('This calculator supports parsing, evaluation, differentiation, and integration.')
        
        self.show_examples()
        
        while True:
            try:
                choice = self.show_menu()
                
                if choice == '0':
                    print('Goodbye! Thanks for using the calculator.')
                    break
                elif choice == '1':
                    self.parse_and_evaluate()
                elif choice == '2':
                    self.differentiate_expression()
                elif choice == '3':
                    self.integrate_indefinite()
                elif choice == '4':
                    self.integrate_definite()
                elif choice == '5':
                    self.simplify_expression()
                elif choice == '6':
                    self.get_variables_from_expression()
                elif choice == '7':
                    self.substitute_values()
                elif choice == '8':
                    self.full_workflow()
                elif choice == '9':
                    self.show_examples()
                else:
                    print('Invalid choice. Please select 0-9.')
                
                if choice != '0':
                    input('\nPress Enter to continue...')
                    
            except KeyboardInterrupt:
                print('\n\nGoodbye!')
                break
            except Exception as e:
                print(f'\n✗ Unexpected error: {str(e)}')
                print('Please try again.')
                input('\nPress Enter to continue...')


if __name__ == '__main__':
    calculator = InteractiveCalculator()
    calculator.run() 