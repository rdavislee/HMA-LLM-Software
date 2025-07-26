import tkinter as _tk # Alias tkinter to _tk to avoid conflicts with mocks
from tkinter import messagebox
from unittest.mock import MagicMock, patch
import pytest
from src.ui.main_window import MainWindow

# Assuming MainWindow and Calculator are importable from their respective paths
# Adjust imports based on the actual project structure if necessary
# From root: src/ui/main_window.py and src/engine/calculator.py

# The Calculator class itself will be mocked, but its path is needed for patching
from src.engine.calculator import Calculator 

# Test partitions:
# - UI Initialization: Verify correct initial widget states.
# - Operation Selection: Verify parameter field visibility changes based on selected operation.
# - Calculation Flow (Success): Verify expression entry updates after successful calculation for each operation type.
# - Calculation Flow (Error): Verify error popup on calculation failure and no change to expression entry.
# - Input Validation: Verify calculate button state based on expression entry content.

@pytest.fixture
def app_and_mocks():
    """Fixture to set up the Tkinter app and mock the Calculator and Tkinter widgets."""

    # Helper to simulate a Tkinter widget's basic behavior for testing
    def create_mock_widget(*args, is_mapped_initially=False, **kwargs):
        mock_widget = MagicMock()
        mock_widget.winfo_ismapped.return_value = is_mapped_initially
        mock_widget.winfo_exists.return_value = True # Assume widgets exist once created
        # Simulate grid/pack methods affecting visibility
        mock_widget.grid.side_effect = lambda *args, **kwargs: setattr(mock_widget, 'winfo_ismapped.return_value', True)
        mock_widget.grid_forget.side_effect = lambda: setattr(mock_widget, 'winfo_ismapped.return_value', False)
        mock_widget.pack.side_effect = lambda *args, **kwargs: setattr(mock_widget, 'winfo_ismapped.return_value', True)
        mock_widget.pack_forget.side_effect = lambda: setattr(mock_widget, 'winfo_ismapped.return_value', False)
        return mock_widget

    # Helper to simulate an Entry widget's behavior
    def create_mock_entry_widget(*args, **kwargs):
        mock_entry = create_mock_widget()
        mock_entry._text_content = ""
        mock_entry.get.side_effect = lambda: mock_entry._text_content
        mock_entry.insert.side_effect = lambda index, text: setattr(mock_entry, '_text_content', mock_entry._text_content + text)
        mock_entry.delete.side_effect = lambda start, end: setattr(mock_entry, '_text_content', "")
        return mock_entry

    # Helper to simulate a Button widget's behavior
    def create_mock_button_widget(*args, initial_state=_tk.DISABLED, **kwargs):
        mock_button = create_mock_widget(*args, **kwargs)
        mock_button._state = initial_state
        mock_button.__getitem__.side_effect = lambda key: mock_button._state if key == 'state' else MagicMock()
        mock_button.__setitem__.side_effect = lambda key, value: setattr(mock_button, '_state', value) if key == 'state' else None
        mock_button.invoke.return_value = None # Simulate click
        return mock_button

    # Helper to simulate StringVar behavior
    def create_mock_stringvar(*args, **kwargs):
        mock_sv = MagicMock(*args, **kwargs)
        mock_sv._value = ""
        mock_sv.get.side_effect = lambda: mock_sv._value
        mock_sv.set.side_effect = lambda value: setattr(mock_sv, '_value', value)
        return mock_sv

    # Patch Tkinter components in the scope where MainWindow uses them
    # This ensures that when MainWindow instantiates these, it gets our mocks.
    with patch('src.ui.main_window.tk.Tk') as MockTk, \
         patch('src.ui.main_window.tk.Frame') as MockFrame, \
         patch('src.ui.main_window.tk.Label') as MockLabel, \
         patch('src.ui.main_window.tk.Entry') as MockEntry, \
         patch('src.ui.main_window.tk.Button') as MockButton, \
         patch('src.ui.main_window.tk.StringVar') as MockStringVar, \
         patch('src.ui.main_window.messagebox') as MockMessagebox, \
         patch('src.ui.main_window.Calculator') as MockCalculator:

        # Configure the return values for the mocked Tkinter classes
        MockTk.return_value = create_mock_widget() # The root Tk instance

        MockFrame.return_value = create_mock_widget()
        MockLabel.return_value = create_mock_widget()
        MockEntry.side_effect = create_mock_entry_widget # Each Entry call returns a unique mock
        MockButton.side_effect = create_mock_button_widget # Each Button call returns a unique mock
        MockStringVar.side_effect = create_mock_stringvar # Each StringVar call returns a unique mock
        
        # Mock messagebox functions
        MockMessagebox.showerror.return_value = None

        # Mock the Calculator instance that MainWindow instantiates
        mock_calculator_instance = MockCalculator.return_value
        # Corrected method names for the Calculator mock as used in tests
        mock_calculator_instance.evaluate.return_value = "Mocked Eval Result"
        mock_calculator_instance.differentiate.return_value = "Mocked Diff Result"
        mock_calculator_instance.integrate_indefinite.return_value = "Mocked Indef Int Result"
        mock_calculator_instance.integrate_definite.return_value = "Mocked Def Int Result"

        with patch('src.ui.main_window.tk.Tk.__init__', return_value=None):
            main_window = MainWindow()
        
        # Mock methods that Tkinter calls internally (like update_idletasks, withdraw, destroy)
        # These are methods of the MainWindow instance itself (which is now a real MainWindow object)
        main_window.update_idletasks = MagicMock()
        main_window.withdraw = MagicMock()
        main_window.destroy = MagicMock()

        # The attributes on main_window (like expression_entry, evaluate_button)
        # are created by MainWindow's __init__ using the patched Tkinter classes.
        # So, they will already be the mock objects returned by MockEntry, MockButton etc.
        # We just need to ensure they are accessible via the main_window object
        # and configured correctly if specific test interactions require it beyond default.

        yield main_window, main_window, mock_calculator_instance
        
        # Teardown: Destroy the Tkinter root window (which is main_window itself)
        main_window.destroy()

# Helper to simulate button clicks
def click_button(button):
    """Simulates a button click."""
    button.invoke() # Tkinter method to simulate a click

# Helper to check if a Tkinter widget is currently mapped (visible on screen)
def is_mapped(widget):
    try:
        return widget.winfo_ismapped()
    except tk.TclError:
        return False

# Helper to check if a Tkinter widget has been created and exists in the Tkinter hierarchy
def is_created(widget):
    try:
        # winfo_exists() returns 1 if the widget exists, 0 otherwise
        return bool(widget.winfo_exists())
    except tk.TclError:
        return False

class TestMainWindowUI:

    def test_initial_ui_state(self, app_and_mocks):
        """
        Test partition: UI Initialization
        Verifies the initial state of UI elements upon window creation.
        """
        root, main_window, _ = app_and_mocks

        # Check main expression entry
        assert main_window.expression_entry.get() == ""
        assert is_mapped(main_window.expression_entry)

        # Check operation buttons visibility
        assert is_mapped(main_window.evaluate_button)
        assert is_mapped(main_window.diff_button)
        assert is_mapped(main_window.int_indef_button)
        assert is_mapped(main_window.int_def_button)

        # Check "Calculate" button visibility and initial state
        assert is_mapped(main_window.calculate_button)
        assert main_window.calculate_button['state'] == _tk.DISABLED 

        # Check parameter fields initial hidden state
        assert not is_mapped(main_window.param_label)
        assert not is_mapped(main_window.param_entry)
        assert not is_mapped(main_window.lower_bound_label)
        assert not is_mapped(main_window.lower_bound_entry)
        assert not is_mapped(main_window.upper_bound_label)
        assert not is_mapped(main_window.upper_bound_entry)
        
        # Check active operation is None initially
        assert main_window.active_operation is None

    @pytest.mark.parametrize("button_name, expected_param_visibility", [
        ("evaluate", "variable_only"),
        ("differentiate", "variable_only"),
        ("integrate_indefinite", "variable_only"),
        ("integrate_definite", "all_bounds")
    ])
    def test_operation_button_clicks(self, app_and_mocks, button_name, expected_param_visibility):
        """
        Test partition: Operation Selection
        Verifies that clicking operation buttons correctly shows/hides parameter fields
        and enables the Calculate button.
        """
        root, main_window, _ = app_and_mocks

        # Set an expression to enable the calculate button after operation selection
        main_window.expression_entry.insert(0, "x+1")
        
        button = getattr(main_window, f"{button_name}_button")
        click_button(button)
        root.update_idletasks() # Process pending Tkinter events

        # Check calculate button is enabled after selecting an operation (and expression is present)
        assert main_window.calculate_button['state'] == _tk.NORMAL
        
        # Check variable parameter visibility
        if expected_param_visibility in ["variable_only", "all_bounds"]:
                        assert is_mapped(main_window.param_label)
                        assert is_mapped(main_window.param_entry)
        else:
            assert not is_mapped(main_window.param_label)
            assert not is_mapped(main_window.param_entry)

        # Check definite integral bounds visibility
        if expected_param_visibility == "all_bounds":
                        assert is_mapped(main_window.lower_bound_label)
                        assert is_mapped(main_window.lower_bound_entry)
                        assert is_mapped(main_window.upper_bound_label)
                        assert is_mapped(main_window.upper_bound_entry)
        else:
            assert not is_mapped(main_window.lower_bound_label)
            assert not is_mapped(main_window.lower_bound_entry)
            assert not is_mapped(main_window.upper_bound_label)
            assert not is_mapped(main_window.upper_bound_entry)
            
        # Verify active_operation is set correctly
        assert main_window.active_operation == button_name

    def test_successful_evaluation(self, app_and_mocks):
        """
        Test partition: Calculation Flow (Success)
        Verifies that the expression entry updates with the result on successful evaluation.
        """
        root, main_window, mock_calculator = app_and_mocks

        # Set initial expression
        main_window.expression_entry.insert(0, "x + 1")

        # Select evaluate operation
        click_button(main_window.evaluate_button)
        root.update_idletasks()

        # Set parameter
        main_window.param_entry.insert(0, "x=5")

        # Mock the evaluate method to return a specific result
        mock_calculator.evaluate.return_value = "6"

        # Click calculate
        click_button(main_window.calculate_button)
        root.update_idletasks()

        # Verify expression entry is updated with the result
        assert main_window.expression_entry.get() == "6"
        # Verify the correct calculator method was called with correct arguments
        mock_calculator.evaluate.assert_called_with("x + 1", "x=5")
        
    def test_successful_differentiation(self, app_and_mocks):
        """
        Test partition: Calculation Flow (Success)
        Verifies that the expression entry updates with the result on successful differentiation.
        """
        root, main_window, mock_calculator = app_and_mocks

        main_window.expression_entry.insert(0, "x**2")
        click_button(main_window.diff_button)
        root.update_idletasks()
        main_window.param_entry.insert(0, "x")

        mock_calculator.differentiate.return_value = "2*x"
        click_button(main_window.calculate_button)
        root.update_idletasks()

        assert main_window.expression_entry.get() == "2*x"
        mock_calculator.differentiate.assert_called_with("x**2", "x")

    def test_successful_indefinite_integration(self, app_and_mocks):
        """
        Test partition: Calculation Flow (Success)
        Verifies that the expression entry updates with the result on successful indefinite integration.
        """
        root, main_window, mock_calculator = app_and_mocks

        main_window.expression_entry.insert(0, "x")
        click_button(main_window.int_indef_button)
        root.update_idletasks()
        main_window.param_entry.insert(0, "x")

        mock_calculator.integrate_indefinite.return_value = "x**2/2 + C1"
        click_button(main_window.calculate_button)
        root.update_idletasks()

        assert main_window.expression_entry.get() == "x**2/2 + C1"
        mock_calculator.integrate_indefinite.assert_called_with("x", "x")

    def test_successful_definite_integration(self, app_and_mocks):
        """
        Test partition: Calculation Flow (Success)
        Verifies that the expression entry updates with the result on successful definite integration.
        """
        root, main_window, mock_calculator = app_and_mocks

        main_window.expression_entry.insert(0, "x")
        click_button(main_window.int_def_button)
        root.update_idletasks()
        main_window.param_entry.insert(0, "x")
        main_window.lower_bound_entry.insert(0, "0")
        main_window.upper_bound_entry.insert(0, "2")

        mock_calculator.integrate_definite.return_value = "2"
        click_button(main_window.calculate_button)
        root.update_idletasks()

        assert main_window.expression_entry.get() == "2"
        mock_calculator.integrate_definite.assert_called_with("x", "x", "0", "2")

    def test_calculation_error_handling(self, app_and_mocks):
        """
        Test partition: Calculation Flow (Error)
        Verifies that an error popup appears and expression entry remains unchanged on calculation error.
        """
        root, main_window, mock_calculator = app_and_mocks

        initial_expression = "invalid_expression"
        main_window.expression_entry.insert(0, initial_expression)

        click_button(main_window.evaluate_button)
        root.update_idletasks()

        # Mock the evaluate method to raise an exception
        mock_calculator.evaluate.side_effect = ValueError("Syntax Error!")

        # Mock messagebox.showerror to prevent actual pop-up during test
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            click_button(main_window.calculate_button)
            root.update_idletasks()

            # Verify error message box was called
            mock_showerror.assert_called_once_with("Calculation Error", "Syntax Error!")

            # Verify expression entry remains unchanged
            assert main_window.expression_entry.get() == initial_expression

    def test_empty_expression_calculate_button_disabled(self, app_and_mocks):
        """
        Test partition: Input Validation
        Verifies that the calculate button is disabled if the expression entry is empty.
        """
        root, main_window, _ = app_and_mocks

        # Ensure expression entry is empty
        main_window.expression_entry.delete(0, _tk.END)

        # Select an operation (which would normally enable the button if expression was present)
        click_button(main_window.evaluate_button)
        root.update_idletasks()

        # The button should immediately become disabled because the expression is empty
        assert main_window.calculate_button['state'] == _tk.DISABLED
        
        # Enter something and check it becomes enabled
        main_window.expression_entry.insert(0, "x+1")
        root.update_idletasks() # Force Tkinter to process updates
        assert main_window.calculate_button['state'] == _tk.NORMAL
        
        # Delete it again and check it becomes disabled
        main_window.expression_entry.delete(0, _tk.END)
        root.update_idletasks() # Force Tkinter to process updates
        assert main_window.calculate_button['state'] == _tk.DISABLED
