# Project: CLI Adder

## Product Vision
A simple command-line interface (CLI) application, built in Python, that prompts a user for two numbers and then prints their sum to the console.

## Architecture Overview
The application will be separated into two main components:
1.  **`main.py`**: Handles user interaction (prompts, input reading, output printing).
2.  **`calculator.py`**: Contains the core logic for adding numbers. This separation allows for easier testing of the business logic.

## Confirmed Requirements
- **Input Method**: Interactive prompts ("Enter first number:", "Enter second number:").
- **Number Types**: The application will support both integers and floating-point (decimal) numbers.
- **Error Handling**: If the user enters non-numeric text, the application will print a clear error message and exit gracefully.
- **Output Format**: The result will be displayed in a descriptive sentence, e.g., `The sum of 5.0 and 3.0 is: 8.0`.

## Development Plan
1.  **Phase 1 (Setup)**: Create the project structure, install dependencies, and define test/run commands. (This is the current phase)
2.  **Phase 2 (Core Logic)**: Implement the `add` function in `calculator.py` with full test coverage in `test_calculator.py`.
3.  **Phase 3 (CLI)**: Implement the user-facing CLI in `main.py` that uses the calculator module.

## Environment Guide
- **Language**: Python 3.x
- **Test**: `python -m pytest -v`
- **Run**: `python src/main.py`
- **Key Libraries**:
    - `pytest`: For running unit tests.