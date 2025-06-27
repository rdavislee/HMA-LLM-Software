"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.evaluateExpression = void 0;
const parser_1 = require("./parser");
/**
 * @function evaluateExpression
 * @description
 * Parses and evaluates a mathematical expression string given a set of variable values.
 * This function acts as an orchestrator, integrating the Parser and Expression evaluation logic.
 *
 * @param expressionString The mathematical expression as a string (e.g., "x + 2 * y").
 * @param variables An object mapping variable names to their numeric values (e.g., { x: 10, y: 5 }).
 * @returns The numeric result of the evaluated expression.
 * @throws {Error} Propagates errors from parsing (Syntax Error) or evaluation (Undefined variable, Division by zero).
 *
 * @precondition
 * - `expressionString` must be a non-empty string representing a valid mathematical expression
 *   parsable by the `Parser` class.
 * - `variables` must be an object where keys are variable names (strings) and values are numbers.
 *
 * @postcondition
 * - If the expression is valid and all variables are defined, returns the correct numeric result.
 * - If parsing fails, a `Syntax Error` is thrown.
 * - If an undefined variable is encountered during evaluation, an `Undefined variable` error is thrown.
 * - If a division by zero occurs during evaluation, a `Division by zero` error is thrown.
 * - The function ensures a clean separation of concerns: parsing is handled by `Parser`,
 *   and evaluation is handled by the AST nodes themselves.
 */
function evaluateExpression(expressionString, variables) {
    try {
        const parser = new parser_1.Parser();
        const ast = parser.parse(expressionString);
        return ast.evaluate(variables);
    }
    catch (error) {
        // Re-throw any errors that occur during parsing or evaluation
        throw error;
    }
}
exports.evaluateExpression = evaluateExpression;
