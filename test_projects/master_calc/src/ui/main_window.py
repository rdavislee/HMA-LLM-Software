import tkinter as tk
import sys
import os

# Add the project root to the Python path
# Assuming main_window.py is in src/ui/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

from tkinter import messagebox
from src.engine.calculator import Calculator

class MainWindow(tk.Tk):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Sympy Calculator")
        self.geometry("600x400") # Set initial window size
        self.calculator = Calculator()
        self.active_operation = None

        self._create_widgets()
        self._hide_all_param_fields() # Ensure all param fields are hidden initially
        self._update_calculate_button_state() # Initial state check

    def _create_widgets(self):
        # Expression Input
        self.expression_label = tk.Label(self, text="Expression:")
        self.expression_label.pack(pady=(10, 0))
        self.expression_entry = tk.Entry(self, width=60)
        self.expression_entry.pack(pady=(0, 10))
        # Bind expression entry changes to update calculate button state
        self.expression_entry.bind("<KeyRelease>", self._update_calculate_button_state)
        self.expression_entry.bind("<ButtonRelease-1>", self._update_calculate_button_state) # For mouse paste

        # Operation Buttons Frame
        operation_frame = tk.Frame(self)
        operation_frame.pack(pady=5)

        self.evaluate_button = tk.Button(operation_frame, text="Evaluate", command=lambda: self._select_operation("evaluate"))
        self.evaluate_button.pack(side=tk.LEFT, padx=5)

        self.diff_button = tk.Button(operation_frame, text="Differentiate", command=lambda: self._select_operation("differentiate"))
        self.diff_button.pack(side=tk.LEFT, padx=5)

        self.int_indef_button = tk.Button(operation_frame, text="Indefinite Integral", command=lambda: self._select_operation("integrate_indefinite"))
        self.int_indef_button.pack(side=tk.LEFT, padx=5)

        self.int_def_button = tk.Button(operation_frame, text="Definite Integral", command=lambda: self._select_operation("integrate_definite"))
        self.int_def_button.pack(side=tk.LEFT, padx=5)

        # Parameter Input Fields (initially hidden)
        self.param_frame = tk.Frame(self)
        self.param_frame.pack(pady=5)
        self.param_label = tk.Label(self.param_frame, text="Variable/Substitutions (e.g., 'x' or 'x=5, y=2'):")
        self.param_label.pack(side=tk.LEFT, padx=5)
        self.param_entry = tk.Entry(self.param_frame, width=30)
        self.param_entry.pack(side=tk.LEFT, padx=5)
        self.param_entry.bind("<KeyRelease>", self._update_calculate_button_state)
        self.param_entry.bind("<ButtonRelease-1>", self._update_calculate_button_state)

        self.lower_bound_label = tk.Label(self.param_frame, text="Lower Bound:")
        self.lower_bound_label.pack(side=tk.LEFT, padx=5)
        self.lower_bound_entry = tk.Entry(self.param_frame, width=10)
        self.lower_bound_entry.pack(side=tk.LEFT, padx=5)
        self.lower_bound_entry.bind("<KeyRelease>", self._update_calculate_button_state)
        self.lower_bound_entry.bind("<ButtonRelease-1>", self._update_calculate_button_state)

        self.upper_bound_label = tk.Label(self.param_frame, text="Upper Bound:")
        self.upper_bound_label.pack(side=tk.LEFT, padx=5)
        self.upper_bound_entry = tk.Entry(self.param_frame, width=10)
        self.upper_bound_entry.pack(side=tk.LEFT, padx=5)
        self.upper_bound_entry.bind("<KeyRelease>", self._update_calculate_button_state)
        self.upper_bound_entry.bind("<ButtonRelease-1>", self._update_calculate_button_state)



        # Calculate Button
        self.calculate_button = tk.Button(self, text="Calculate", command=self._on_calculate, state=tk.DISABLED)
        self.calculate_button.pack(pady=10)

    def _hide_all_param_fields(self):
        # Hide all parameter-related widgets
        self.param_label.pack_forget()
        self.param_entry.pack_forget()
        self.lower_bound_label.pack_forget()
        self.lower_bound_entry.pack_forget()
        self.upper_bound_label.pack_forget()
        self.upper_bound_entry.pack_forget()
        self.param_frame.pack_forget() # Hide the frame itself if no children are packed

    def _show_params(self, operation_type):
        self._hide_all_param_fields()
        self.param_frame.pack(pady=5) # Show the frame

        if operation_type in ["evaluate", "differentiate", "integrate_indefinite"]:
            self.param_label.config(text="Variable/Substitutions (e.g., 'x' or 'x=5, y=2'):" if operation_type == "evaluate" else "Variable (e.g., 'x'):")
            self.param_label.pack(side=tk.LEFT, padx=5)
            self.param_entry.pack(side=tk.LEFT, padx=5)
        elif operation_type == "integrate_definite":
            self.param_label.config(text="Variable (e.g., 'x'):")
            self.param_label.pack(side=tk.LEFT, padx=5)
            self.param_entry.pack(side=tk.LEFT, padx=5)
            self.lower_bound_label.pack(side=tk.LEFT, padx=5)
            self.lower_bound_entry.pack(side=tk.LEFT, padx=5)
            self.upper_bound_label.pack(side=tk.LEFT, padx=5)
            self.upper_bound_entry.pack(side=tk.LEFT, padx=5)

    def _select_operation(self, operation):
        self.active_operation = operation
        self._show_params(operation)
        self._update_calculate_button_state()

    def _update_calculate_button_state(self, event=None):
        expression = self.expression_entry.get().strip()
        
        # Base condition: expression must not be empty and an operation must be selected
        if not expression or self.active_operation is None:
            self.calculate_button.config(state=tk.DISABLED)
            return

        # Additional checks based on active operation
        if self.active_operation == "integrate_definite":
            variable_str = self.param_entry.get().strip()
            lower_bound_str = self.lower_bound_entry.get().strip()
            upper_bound_str = self.upper_bound_entry.get().strip()
            if not variable_str or not lower_bound_str or not upper_bound_str:
                self.calculate_button.config(state=tk.DISABLED)
                return
        # For other operations (evaluate, differentiate, indefinite integral),
        # the variable field is optional or its validity is checked by the engine.
        # So, if we reach here, and it's not definite integral, the button can be enabled.

        self.calculate_button.config(state=tk.NORMAL)

    def _parse_substitutions(self, subs_str: str) -> dict:
        """Parses a string like 'x=5, y=2' into a dictionary {'x': '5', 'y': '2'}."""
        if not subs_str.strip():
            return {}
        
        substitutions = {}
        pairs = subs_str.split(',')
        for pair in pairs:
            if '=' not in pair:
                raise ValueError(f"Invalid substitution format: '{pair}'. Expected 'var=value'.")
            
            parts = pair.split('=', 1)
            var_name = parts[0].strip()
            value = parts[1].strip()
            
            if not var_name:
                raise ValueError("Variable name cannot be empty in substitution.")
            
            substitutions[var_name] = value
        return substitutions

    def _on_calculate(self):
        expression_str = self.expression_entry.get().strip()
        variable_str = self.param_entry.get().strip()
        lower_bound_str = self.lower_bound_entry.get().strip()
        upper_bound_str = self.upper_bound_entry.get().strip()
        
        if not expression_str:
            messagebox.showerror("Input Error", "Please enter a mathematical expression.")
            return

        if self.active_operation is None:
            messagebox.showinfo("No Operation Selected", "Please select an operation (Evaluate, Differentiate, Integral) first.")
            return

        result = ""
        try:
            if self.active_operation == "evaluate":
                substitutions = self._parse_substitutions(variable_str)
                result = self.calculator.evaluate_expression(expression_str, substitutions)
            elif self.active_operation == "differentiate":
                result = self.calculator.differentiate_expression(expression_str, variable_str)
            elif self.active_operation == "integrate_indefinite":
                result = self.calculator.integrate_indefinite(expression_str, variable_str)
            elif self.active_operation == "integrate_definite":
                result = self.calculator.integrate_definite(expression_str, variable_str, lower_bound_str, upper_bound_str)
            
            self.expression_entry.delete(0, tk.END)
            self.expression_entry.insert(0, result)

        except ValueError as e:
            messagebox.showerror("Calculation Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()