# Project: Python CLI Symbolic Calculator

## Product Vision
A command-line interface (CLI) tool that allows users to perform symbolic mathematical operations on algebraic expressions. The tool will support evaluation, differentiation, and integration, providing a simple, interactive way to work with math expressions.

## Architecture Overview
The system will be a monolithic CLI application built in Python. The core logic for parsing, calculus, and simplification will be handled by the `SymPy` library, which is a powerful tool for symbolic mathematics. This approach will accelerate development and ensure robust handling of mathematical operations.

## Core Features
- **Expression Parsing**: Handles standard mathematical expressions including:
  - PEMDAS (Order of Operations)
  - Variables (e.g., `x`, `y`, `alpha`)
  - Constants: `pi`, `e`
  - Functions:
    - Logarithms: `log(expression, base)`, `ln(expression)`, `log(expression)` (defaults to base 10)
    - Trigonometric: `sin`, `cos`, `tan`, `csc`, `sec`, `cot`
    - Inverse Trigonometric: `asin`, `acos`, `atan`, `acsc`, `asec`, `acot`
- **Operations**:
  - **Evaluate**: Substitute user-provided values for variables and simplify the expression.
  - **Differentiate**: Compute the derivative with respect to a specified variable. The system will leverage `SymPy`'s full capabilities.
  - **Indefinite Integral**: Compute the indefinite integral with respect to a specified variable. The constant of integration will be added dynamically, starting with `C` and incrementing (`C1`, `C2`, etc.) to avoid collision with existing variables in the expression.
  - **Definite Integral**: Compute the definite integral between specified bounds, which can themselves be expressions.
- **Interactive CLI Flow**: The application will follow a clear loop: `Get Expression -> Get Operation -> Get Parameters -> Show Result -> Ask to reuse result? -> Repeat`.
- **Error Handling**: Gracefully catch and report syntax or mathematical errors from `SymPy` and prompt the user for a new expression.

## Development Plan
1.  **Phase 1: Environment & Core Setup**:
    - Set up the Python environment with `pip` and `venv`.
    - Install `sympy` and `pytest`.
    - Create the file structure (`src/main.py`, `src/calculator.py`, `src/parser.py`, and corresponding test files).
    - Implement placeholder tests to ensure the test runner is configured correctly.
2.  **Phase 2: Parser and Calculator Implementation**:
    - **Parser**: Implement the `parser.py` module to safely parse user input strings into `SymPy` expression objects. Add comprehensive tests for valid and invalid expressions.
    - **Calculator**: Implement the core `calculator.py` module containing functions for differentiation, integration, and evaluation. This module will wrap `SymPy`'s functionalities and include the logic for the dynamic integration constant. Add unit tests for each mathematical operation.
3.  **Phase 3: CLI Implementation**:
    - Implement the main user interaction loop in `main.py`.
    - Connect the CLI to the `Parser` and `Calculator` modules.
    - Implement the full interactive flow, including prompts, error handling, and the feature to reuse previous results.

## Environment Guide
- **Language**: Python
- **Test**: `python -m pytest`
- **Run**: `python src/main.py`
- **Key Libraries**:
  - `sympy`: For symbolic mathematics.
  - `pytest`: For testing.