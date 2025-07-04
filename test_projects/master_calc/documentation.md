# Project: Command-Line Mathematical Expression Evaluator

## Product Vision
A command-line tool that allows users to input complex mathematical expressions, provide values for any variables, and receive the calculated result. The tool should be interactive, allowing for repeated calculations with the same or new expressions.

## Architecture Overview
The system will be composed of two main components:
1.  **Parser/Evaluator Module**: A self-contained module responsible for taking a string expression and a scope of variables, and returning a result. It will use the `mathjs` library, which is a powerful and dedicated mathematical parsing and evaluation engine.
2.  **CLI Module**: An interactive command-line interface that handles user input/output. It will use the Parser/Evaluator to evaluate expressions and manage the application loop.

## Modules

### Module 1: Parser/Evaluator
- **Purpose**: To parse, compile, and evaluate mathematical expressions using a dedicated library.
- **Key Interfaces**: A single `evaluate(expression: string, scope: object)` function that returns the calculated number.
- **Dependencies**: `mathjs`.

### Module 2: CLI
- **Purpose**: To manage user interaction, prompt for expressions and variables, and display results or errors.
- **Key Interfaces**: A main `start()` function to begin the interactive loop.
- **Dependencies**: Node.js `readline` module, Parser/Evaluator Module.

## Core Features & Specifications
- **Expression Parsing**: Supports standard arithmetic operations following PEMDAS (Parentheses, Exponents, Multiplication/Division, Addition/Subtraction).
- **Mathematical Functions**:
  - **Logarithms**: `log(value, base)` (logarithm of `value` to the specified `base`). `log(value)` defaults to base 10. `log(value, 'e')` for natural log.
  - **Trigonometry**: `sin`, `cos`, `tan`, `csc`, `sec`, `cot`.
  - **Inverse Trigonometry**: `asin`, `acos`, `atan`, `acsc`, `asec`, `acot`.
- **Constants**: `e`, `pi`.
- **Variables**: Support for user-defined variables (e.g., `x`, `y`) passed via a scope object.
- **Interactive CLI**:
  1. Prompt for an expression.
  2. Identify variables within the expression and prompt the user for their values.
  3. Evaluate the expression and display the result.
  4. If an invalid expression or mathematical error (e.g., division by zero) occurs, display a clear error message and reprompt for a new expression.
  5. After a successful calculation, ask the user if they want to evaluate the same expression with new variables or enter a new expression.
- **Interaction Style**: A simple, standard input/output text loop is sufficient.

## Technical Stack
- **Language**: TypeScript
- **Parser Library**: `mathjs`
- **Core Dependencies**: Node.js standard library for the CLI.

## Environment Guide
- **Language**: TypeScript
- **Build**: `npm run build`
- **Test**: `npm test`
- **Run**: `npm start`
- **Key Libraries**:
  - `mathjs`: For parsing and evaluating mathematical expressions.
  - `typescript`: Core language transpiler.
  - `mocha`: Test runner.
  - `ts-node`: To execute TypeScript directly for testing.