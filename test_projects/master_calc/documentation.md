# Project: Sympy Calculator

## Product Vision
To create a small, standalone Windows executable (`.exe`) that functions as an advanced calculator. A user can input a mathematical expression into a single-line text box, select an operation (evaluate, differentiate, integrate), provide any necessary parameters, and see the result replace the original expression in the text box.

## Architecture Overview
The system will be a desktop application built in Python.
- **Frontend (GUI):** A simple graphical user interface built using Python's standard **Tkinter** library.
- **Backend (Engine):** A core logic module using the `sympy` library to parse, evaluate, and manipulate mathematical expressions.
- **Packaging:** The final application will be bundled into a single `.exe` file using **PyInstaller**.

## UI Flow
1.  The main window displays a single-line text entry field for the mathematical expression.
2.  Below the text field, there are four buttons: \"Evaluate\", \"Differentiate\", \"Indefinite Integral\", and \"Definite Integral\".
3.  Clicking one of these buttons makes it the \"active\" operation and reveals specific input fields for that operation's parameters (e.g., clicking \"Differentiate\" shows a text box for the \"variable to differentiate with respect to\").
4.  A final \"Calculate\" button executes the active operation on the expression.
5.  The result of the calculation replaces the expression in the main text entry field.

## Core Features
- **Expression Parsing**: Supports standard mathematical notation (PEMDAS), variables of any length, constants (`pi`, `e`), and a wide range of functions:
    - Logarithms:
        - `log(base, expression)`: Logarithm with a specified base.
        - `ln(expression)`: Natural logarithm (base e).
        - `log(expression)`: Common logarithm (base 10). **Note:** This overrides the `sympy` default, which treats `log` as the natural logarithm. The implementation must handle this conversion.
    - Trigonometry: `sin`, `cos`, `tan`, `csc`, `sec`, `cot`.
    - Inverse Trigonometry: `asin`, `acos`, `atan`, `acsc`, `asec`, `acot`.
- **Operations**:
    - **Evaluate**: Prompts for variable values and substitutes them into the expression, simplifying the result.
    - **Differentiate**: Computes the symbolic derivative with respect to a user-specified variable.
    - **Integrate (Indefinite)**: Computes the symbolic indefinite integral, adding a constant of integration (`+ C`, `+ C1`, etc. to avoid conflicts).
    - **Integrate (Definite)**: Computes the definite integral over a user-specified variable and bounds (which can be expressions).
- **Result Handling**: The output of any successful operation replaces the content of the initial input box, allowing the user to chain calculations by using the result as the next input.
- **Error Handling**: Invalid expressions or operations will trigger a short pop-up message describing the error. The input box will remain unchanged.

## Environment Guide
- **Language**: Python 3.x
- **Key Libraries**:
    - `sympy`: For the core mathematical engine.
    - `tkinter`: For the user interface (standard library).
    - `pyinstaller`: For creating the executable.
- **Test**: `python -m pytest -v`
- **Run**: `python src/main.py`
- **Build**: `pyinstaller --onefile --windowed src/main.py` (Note: This command can only be run by the Master Agent at the end of the project.)

## Development Plan
1. **Phase 1**: Implement the core calculation engine. This will involve creating a class that can parse expressions, and has methods for evaluation, differentiation, and integration. All logic should be self-contained and not rely on any UI components yet. All methods must be thoroughly tested.
2. **Phase 2**: Develop the Tkinter GUI. This will create the main window, input box, and all buttons. The UI will be connected to the calculation engine from Phase 1.
3. **Phase 3**: Package the application into a standalone `.exe` file using PyInstaller and finalize error handling.