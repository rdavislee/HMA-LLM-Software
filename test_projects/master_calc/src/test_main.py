import pytest
from unittest.mock import patch, call
from src.main import main

# Test partitions:
# - CLI Flow: successful sequence, reuse previous result
# - Exit/Quit: from expression prompt, from continue prompt
# - Error Handling: invalid expression, invalid operation, invalid variable
# - Operation Specific Flows: evaluate, differentiate, indefinite integrate, definite integrate
# - Input Validation: variable input, substitution input, bounds input

@patch('builtins.print')
class TestMainCLI:

    def test_exit_from_expression_input(self, mock_print):
        """Tests that the CLI exits gracefully when 'exit' is entered at the expression prompt."""
        with patch('builtins.input', side_effect=['exit', 'no']): # 'no' for the follow-up continue prompt
            main()
            # Verify that the exit message is printed or that the process terminates.
            # We check the last expected print call from the 'main' function's exit path.
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_basic_evaluate_flow(self, mock_print):
        """Tests a basic successful evaluation flow."""
        with patch('builtins.input', side_effect=[
            'x**2 + 1',
            '1', # Evaluate
            'x=2',
            'no' # Exit
        ]):
            main()
            # Check for the expected output, specifically the result and the exit message.
            assert call('\nResult: 5') in mock_print.call_args_list
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_reuse_previous_result_flow(self, mock_print):
        """Tests the functionality to reuse a previous result."""
        with patch('builtins.input', side_effect=[
            '2*y',
            '1', # Evaluate
            'y=3', # Result: 6
            'yes', # Continue
            '',    # Use previous result (6)
            '1', # Evaluate (no new substitutions, so result should still be 6)
            '', # Skip substitutions
            'no' # Exit
        ]):
            main()
            mock_print.assert_any_call("Using previous result: 6")
            mock_print.assert_any_call('\nResult: 6') # Verify the result is indeed 6
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_invalid_expression_then_valid_flow(self, mock_print):
        """Tests that the CLI handles an invalid expression gracefully and allows retry."""
        with patch('builtins.input', side_effect=[
            'invalid_syntax@#$', # Invalid expression
            'x+5',               # Valid expression
            '2',                 # Differentiate
            'x',                 # Differentiate wrt x
            'no'                 # Exit
        ]):
            main()
            mock_print.assert_any_call("Error: Could not parse expression. Please check syntax and try again.")
            mock_print.assert_any_call('\nResult: 1') # d/dx (x+5) = 1
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_invalid_operation_choice_then_valid(self, mock_print):
        """Tests that the CLI handles an invalid operation choice gracefully and allows retry."""
        with patch('builtins.input', side_effect=[
            'x',
            '5', # Invalid operation choice
            '1', # Valid operation: Evaluate
            'x=1', # Substitution
            'no' # Exit
        ]):
            main()
            mock_print.assert_any_call("Invalid choice. Please enter a number between 1 and 4.")
            mock_print.assert_any_call('\nResult: 1')
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_invalid_variable_input_then_valid(self, mock_print):
        """Tests handling of invalid variable input during differentiation/integration."""
        with patch('builtins.input', side_effect=[
            'x**2',
            '2', # Differentiate
            '', # Invalid variable (empty)
            'y=z', # Invalid variable (not a symbol)
            'x', # Valid variable
            'no' # Exit
        ]):
            main()
            mock_print.assert_any_call("Variable cannot be empty. Please enter a variable.")
            mock_print.assert_any_call("Error parsing variable 'y=z'. Please ensure it's a valid symbol name.")
            mock_print.assert_any_call('\nResult: 2*x')
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_exit_from_continue_prompt(self, mock_print):
        """Tests exiting from the 'Do you want to perform another operation?' prompt."""
        with patch('builtins.input', side_effect=[
            '1',
            '1', # Evaluate
            '', # Skip substitutions
            'quit', # Exit at continue prompt
            'no' # Final input to gracefully exit the invalid choice loop
        ]):
            main()
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_indefinite_integration_flow(self, mock_print):
        """Tests a successful indefinite integration flow."""
        with patch('builtins.input', side_effect=[
            '2*x',
            '3', # Integrate (indefinite)
            'x', # Integrate wrt x
            'no' # Exit
        ]):
            main()
            # SymPy adds a constant, typically C, C1, etc.
            assert any(call_item == call('\nResult: x**2 + C1') for call_item in mock_print.call_args_list) or \
                   any(call_item == call('\nResult: x**2 + C') for call_item in mock_print.call_args_list)
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_definite_integration_flow(self, mock_print):
        """Tests a successful definite integration flow."""
        with patch('builtins.input', side_effect=[
            'x',
            '4', # Integrate (definite)
            'x', # Integrate wrt x
            '0', # Lower bound
            '2', # Upper bound
            'no' # Exit
        ]):
            main()
            assert call('\nResult: 2') in mock_print.call_args_list # Integral of x from 0 to 2 is [x^2/2] from 0 to 2 = 2
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_skip_substitutions_flow(self, mock_print):
        """Tests skipping substitutions for evaluation."""
        with patch('builtins.input', side_effect=[
            'x + y',
            '1', # Evaluate
            '',  # Skip substitutions
            'no' # Exit
        ]):
            main()
            assert call('\nResult: x + y') in mock_print.call_args_list # Result should be the original expression
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_substitution_invalid_format_then_valid(self, mock_print):
        """Tests handling of invalid substitution format."""
        with patch('builtins.input', side_effect=[
            'x + y',
            '1', # Evaluate
            'x=, y', # Invalid format
            'x=1, y=2', # Valid format
            'no' # Exit
        ]):
            main()
            assert call("Error in substitution input: Invalid substitution format: 'x='. Expected 'var=value'.") in mock_print.call_args_list
            assert call("Error in substitution input: Invalid substitution format: 'y'. Expected 'var=value'.") in mock_print.call_args_list
            assert call('\nResult: 3') in mock_print.call_args_list
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_substitution_unparseable_value_then_valid(self, mock_print):
        """Tests handling of unparseable substitution value."""
        with patch('builtins.input', side_effect=[
            'x + y',
            '1', # Evaluate
            'x=invalid_value', # Unparseable value
            'x=1', # Valid
            'no' # Exit
        ]):
            main()
            assert call("Error in substitution input: Could not parse value 'invalid_value' for variable 'x'.") in mock_print.call_args_list
            assert call('\nResult: 1 + y') in mock_print.call_args_list
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_substitution_variable_not_in_expression_then_valid(self, mock_print):
        """Tests handling of substitution for a variable not in the expression."""
        with patch('builtins.input', side_effect=[
            'x**2',
            '1', # Evaluate
            'y=5, z=10', # y and z not in expression
            'x=3', # Valid
            'no' # Exit
        ]):
            main()
            assert call("Warning: Variable 'y' not found in the expression. It will be ignored.") in mock_print.call_args_list
            assert call("Warning: Variable 'z' not found in the expression. It will be ignored.") in mock_print.call_args_list
            assert call('\nResult: 9') in mock_print.call_args_list
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_substitution_multiple_valid(self, mock_print):
        """Tests multiple valid substitutions in one go."""
        with patch('builtins.input', side_effect=[
            'x + y + z',
            '1', # Evaluate
            'x=1, y=2, z=3', # Multiple valid
            'no' # Exit
        ]):
            main()
            assert call('\nResult: 6') in mock_print.call_args_list
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_bounds_input_unparseable_then_valid(self, mock_print):
        """Tests handling of unparseable bounds for definite integration."""
        with patch('builtins.input', side_effect=[
            'x',
            '4', # Integrate (definite)
            'x', # Integrate wrt x
            'invalid_lower', # Unparseable lower
            '0', # Valid lower
            'invalid_upper', # Unparseable upper
            '1', # Valid upper
            'no' # Exit
        ]):
            main()
            assert call("Error parsing bounds: Could not parse lower bound. Please try again.") in mock_print.call_args_list
            assert call("Error parsing bounds: Could not parse upper bound. Please try again.") in mock_print.call_args_list
            assert call('\nResult: 0.5') in mock_print.call_args_list # Integral of x from 0 to 1 is 0.5
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_bounds_input_with_expressions(self, mock_print):
        """Tests handling of bounds that are themselves expressions."""
        with patch('builtins.input', side_effect=[
            'y',
            '4', # Integrate (definite)
            'y', # Integrate wrt y
            'a', # Lower bound as expression
            'b', # Upper bound as expression
            'no' # Exit
        ]):
            main()
            assert call('\nResult: -a**2/2 + b**2/2') in mock_print.call_args_list
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_error_clears_previous_result(self, mock_print):
        """Tests that previous_result is cleared after an error."""
        with patch('builtins.input', side_effect=[
            'x+1', # Valid initial expression
            '1', # Evaluate
            'x=1', # Substitution, Result: 2
            'yes', # Continue
            'invalid_expression@#$', # Invalid expression, should cause error and clear prev result
            'x+2', # Valid expression for next round
            '1', # Evaluate
            '', # Skip substitution, should not use '2' from first round
            'no' # Exit
        ]):
            main()
            assert call('\nResult: 2') in mock_print.call_args_list
            assert call("Error: Could not parse expression. Please check syntax and try again.") in mock_print.call_args_list
            # Verify that the result of x+2 with no subs is x+2, not a number from previous_result
            assert call('\nResult: x + 2') in mock_print.call_args_list
            mock_print.assert_any_call("Exiting calculator. Goodbye!")

    def test_no_previous_result_empty_input_then_valid(self, mock_print):
        """Tests behavior when no previous result exists and user presses Enter for expression."""
        with patch('builtins.input', side_effect=[
            '', # Empty input, no previous result
            'x+1', # Valid expression
            '1', # Evaluate
            '', # Skip subs
            'no' # Exit
        ]):
            main()
            assert call("No previous result to use. Please enter an expression.") in mock_print.call_args_list
            assert call('\nResult: x + 1') in mock_print.call_args_list
            mock_print.assert_any_call("Exiting calculator. Goodbye!")