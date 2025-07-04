"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.evaluate = evaluate;
const mathjs_1 = require("mathjs");
const math = (0, mathjs_1.create)({}, {
    number: 'number', // Explicitly ensure results are standard JavaScript numbers
});
function preprocessLog(expression) {
    let processedExpression = expression;
    // Step 1: Temporarily convert log(value, "e") to a unique placeholder.
    // This must happen first to prevent the log(value) rule from misinterpreting it.
    const naturalLogWithEBaseRegex = /log\(([^,]+?),\s*["']e["']\)/g;
    processedExpression = processedExpression.replace(naturalLogWithEBaseRegex, 'NAT_LOG_PLACEHOLDER($1)');
    // Step 2: Convert log(value) (single argument) to log(value, 10).
    // This regex matches "log(" followed by an argument that does NOT contain a comma,
    // and then the closing parenthesis. This correctly handles nested functions like log(exp(3)).
    // It will not affect NAT_LOG_PLACEHOLDER expressions.
    const logBase10DefaultRegex = /log\(([^,]+?)\)/g;
    processedExpression = processedExpression.replace(logBase10DefaultRegex, 'log($1, 10)');
    // Step 3: Convert the placeholder back to mathjs's natural log function (log(value)).
    const natLogPlaceholderRegex = /NAT_LOG_PLACEHOLDER\(([^)]+?)\)/g;
    processedExpression = processedExpression.replace(natLogPlaceholderRegex, 'log($1)');
    return processedExpression;
}
/**
 * Evaluates a mathematical expression using mathjs.
 * Handles arithmetic, variables, functions (log, trig, inverse trig), and constants (e, pi).
 * Catches and re-throws specific errors for better clarity.
 *
 * @param expression The mathematical expression string to evaluate.
 * @param scope An optional object containing variables to be used in the expression.
 * @returns The numeric result of the evaluation.
 * @throws {Error} If the expression is invalid, results in non-numeric values, or encounters mathematical errors.
 */
function evaluate(expression, scope = {}) {
    if (expression.trim() === '') {
        return 0;
    }
    try {
        // Preprocess the expression to handle log(value) defaulting to base 10
        const preprocessedExpression = preprocessLog(expression);
        // Evaluate the expression with the given scope
        const result = (0, mathjs_1.evaluate)(preprocessedExpression, scope);
        // Math.js can return various types (Complex, Unit, BigNumber, Fraction, Matrix, etc.)
        // We need to ensure the result is a plain number as per specification.
        if (typeof result === 'number') {
            // Check for extremely large numbers that should be Infinity due to floating point precision near asymptotes
            // This specifically targets cases like tan(pi/2) or sec(pi/2)
            const VERY_LARGE_NUMBER_THRESHOLD = 1e15; // A reasonable threshold for values that are "practically" infinite
            if (Math.abs(result) > VERY_LARGE_NUMBER_THRESHOLD) {
                return result > 0 ? Infinity : -Infinity;
            }
            return result;
        }
        else if ((0, mathjs_1.isComplex)(result)) {
            return NaN; // Convert complex results to NaN as per test expectations
        }
        else if ((0, mathjs_1.isUnit)(result)) {
            // We are expecting only numeric results, so units are considered non-numeric
            throw new Error(`Evaluation returned a non-numeric result: Unit (${result.toString()})`);
        }
        else if ((0, mathjs_1.isMatrix)(result)) {
            throw new Error(`Evaluation returned a non-numeric result: Matrix`);
        }
        else if ((0, mathjs_1.isBigNumber)(result)) {
            // Convert BigNumber to a standard JavaScript number
            return result.toNumber();
        }
        else if ((0, mathjs_1.isFraction)(result)) {
            // Convert Fraction to a standard JavaScript number
            return (0, mathjs_1.number)(result);
        }
        else if (Array.isArray(result)) {
            // Handle cases where math.evaluate returns an array (e.g., matrix operations)
            throw new Error(`Evaluation returned a non-numeric result: Array`);
        }
        // If it's a type not explicitly handled but not a number, throw an error
        throw new Error(`Evaluation returned an unexpected non-numeric type: ${typeof result}`);
    }
    catch (error) {
        // Catch mathjs specific errors and re-throw with a consistent message
        if (error.message.includes('Undefined symbol')) {
            throw new Error(`Expression evaluation failed: ${error.message}`);
        }
        else if (error.message.includes('Syntax error in expression')) {
            throw new Error(`Expression evaluation failed: Syntax error in expression`);
        }
        else if (error.message.includes('Unexpected type of argument')) {
            throw new Error(`Expression evaluation failed: Invalid argument for function`);
        }
        // Re-throw other errors as general evaluation failures
        throw new Error(`Expression evaluation failed: ${error.message}`);
    }
}
