/**
 * @file src/parser.interface.ts
 * @brief Defines the interface for the expression parser.
 *
 * This file specifies the contract for a parser that converts a string
 * representation of a mathematical expression into an abstract data type (ADT)
 * representing the expression.
 *
 * The parser must adhere to the standard order of operations (PEMDAS/BODMAS)
 * and support a defined set of mathematical constructs.
 */

import { Expression } from './expressionInterface'; // Assuming Expression ADT is defined here

/**
 * Custom error class for parsing failures.
 * This error is thrown when the input string does not represent a valid
 * mathematical expression according to the parser's grammar rules.
 */
export class ParseError extends Error {
    constructor(message: string) {
        super(`ParseError: ${message}`);
        this.name = 'ParseError';
    }
}

/**
 * Defines the interface for an expression parser.
 *
 * This parser is responsible for converting a string expression into an
 * Expression ADT, respecting PEMDAS rules and supporting various mathematical
 * elements.
 */
export interface IExpressionParser {
    /**
     * Parses a string representation of a mathematical expression into an
     * Expression Abstract Data Type (ADT).
     *
     * @param expressionString The string containing the mathematical expression.
     *                         Examples: "2 + x * sin(y)", "log(100) / (5 - z^2)", "e^x + pi * cos(0)".
     *
     * @precondition
     *   - `expressionString` must be a non-empty string.
     *   - `expressionString` must consist only of supported characters:
     *     - Digits (0-9)
     *     - Decimal point (.)
     *     - Variables (alphanumeric, case-sensitive, e.g., 'x', 'var1')
     *     - Operators: '+', '-', '*', '/', '^'
     *     - Parentheses: '(', ')'
     *     - Functions: 'sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'asin', 'acos', 'atan', 'asec', 'acsc', 'acot', 'log', 'ln'
     *     - Constants: 'e', 'pi'
     *     - Whitespace characters (which should be ignored or handled by the parser).
     *   - Function arguments must be enclosed in parentheses (e.g., 'sin(x)', not 'sinx').
     *   - Operators must be binary (e.g., '2 + 3', not '2+'). Unary minus is supported (e.g., '-5', '-(x+y)').
     *
     * @postcondition
     *   - If the `expressionString` is syntactically valid and conformant,
     *     returns an `Expression` ADT representing the parsed expression tree.
     *     The Expression ADT will correctly reflect the order of operations (PEMDAS/BODMAS).
     *
     * @throws {ParseError}
     *   - If `expressionString` is empty or null/undefined.
     *   - If `expressionString` contains syntax errors (e.g., unmatched parentheses,
     *     unrecognized tokens, invalid function calls, malformed numbers).
     *   - If `expressionString` contains unsupported operations or functions.
     *
     * @constraints
     *   - **PEMDAS/BODMAS Adherence**: The parser must correctly interpret and
     *     build the expression tree according to the standard order of operations
     *     (Parentheses/Brackets, Exponents/Orders, Multiplication/Division, Addition/Subtraction).
     *   - **Numbers**: Supports integers and floating-point numbers.
     *   - **Constants**: Supports mathematical constants 'e' (Euler's number) and 'pi' (Archimedes' constant).
     *   - **Variables**: Supports single or multi-character alphanumeric variable names.
     *   - **Arithmetic Operations**: Supports addition (+), subtraction (-),
     *     multiplication (*), division (/), and exponentiation (^). 'e^x' should be parsed as exponentiation with base 'e'.
     *   - **Logarithms**: Supports natural logarithm (ln) and base-10 logarithm (log).
     *     For `log(x)`, base 10 is implied. Custom base logarithms are not required.
     *   - **Trigonometric Functions**: Supports sine (sin), cosine (cos), tangent (tan),
     *     secant (sec), cosecant (csc), and cotangent (cot).
     *   - **Inverse Trigonometric Functions**: Supports arcsine (asin), arccosine (acos), arctangent (atan),
     *     arcsecant (asec), arccosecant (acsc), and arccotangent (acot).
     *   - **Whitespace**: Whitespace characters should be ignored.
     *   - **Unary Minus**: Unary minus operator (e.g., "-5", "-(x+y)") should be correctly handled.
     */
    parse(expressionString: string): Expression;
}