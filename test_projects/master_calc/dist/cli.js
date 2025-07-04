"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.isValidNumericInput = isValidNumericInput;
exports.extractVariables = extractVariables;
exports.start = start;
const readline = __importStar(require("readline"));
const evaluator_1 = require("./evaluator");
const mathjs_1 = require("mathjs");
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});
/**
 * Prompts the user with a question and returns their input.
 * @param query The question to ask.
 * @returns A Promise that resolves with the user's input string.
 */
function promptQuestion(query) {
    return new Promise((resolve) => rl.question(query, resolve));
}
/**
 * Checks if a given string can be parsed into a valid, finite number.
 * @param input The string to check.
 * @returns True if the string represents a valid finite number, false otherwise.
 */
function isValidNumericInput(input) {
    const value = parseFloat(input);
    return !isNaN(value) && isFinite(value);
}
/**
 * Extracts unique variable names from a mathematical expression string.
 * Uses mathjs.parse to build an AST and then recursively finds SymbolNodes.
 * @param expression The mathematical expression string.
 * @returns An array of unique variable names (strings).
 */
function extractVariables(expression) {
    try {
        const node = (0, mathjs_1.parse)(expression);
        const variables = new Set();
        node.filter(function (node) {
            if (node.type === 'SymbolNode') {
                const symbolNode = node;
                // Filter out built-in constants like 'pi' and 'e', and common functions
                if (!['pi', 'e', 'log', 'sin', 'cos', 'tan', 'sqrt', 'abs', 'exp', 'round', 'floor', 'ceil', 'fix', 'gamma', 'lgamma', 'factorial', 'permutations', 'combinations', 'gcd', 'lcm', 'mod', 'pow', 'nthRoot', 'hypot'].includes(symbolNode.name)) {
                    variables.add(symbolNode.name);
                }
            }
            return true;
        });
        return Array.from(variables);
    }
    catch (error) {
        // If parsing fails (e.g., malformed expression), an error is thrown and caught by the caller.
        // Here, we re-throw to indicate a parsing issue.
        throw new Error(`Invalid expression syntax: ${error.message}`);
    }
}
/**
 * Starts the interactive command-line interface for expression evaluation.
 * Handles prompting for expressions, variables, evaluation, and error display.
 */
async function start() {
    console.log('Welcome to the Command-Line Mathematical Expression Evaluator!');
    console.log('Type \'exit\' or \'quit\' to stop at any time.');
    while (true) { // Loop indefinitely until an explicit return
        let expression = '';
        let variables = [];
        let scope = {};
        // 1. Prompt for expression and validate syntax
        while (true) { // Loop until valid expression input or exit
            expression = await promptQuestion('\nEnter a mathematical expression (e.g., \'x + y * sin(pi/2)\' ): ');
            if (expression.toLowerCase() === 'exit' || expression.toLowerCase() === 'quit') {
                rl.close();
                console.log('Thank you for using the evaluator. Goodbye!');
                return; // Exit the start function
            }
            try {
                variables = extractVariables(expression); // This also validates expression syntax implicitly
                break; // Valid expression, break from inner loop
            }
            catch (error) {
                console.error(`Error: ${error.message}. Please try again.`);
            }
        }
        // 2. Prompt for variable values
        for (const variable of variables) {
            while (true) { // Loop until valid value or exit
                const valueStr = await promptQuestion(`Enter value for variable '${variable}': `);
                if (valueStr.toLowerCase() === 'exit' || valueStr.toLowerCase() === 'quit') {
                    rl.close();
                    console.log('Thank you for using the evaluator. Goodbye!');
                    return; // Exit the start function
                }
                if (isValidNumericInput(valueStr)) {
                    const value = parseFloat(valueStr);
                    scope[variable] = value;
                    break; // Valid value, break from inner loop
                }
                else {
                    console.error('Invalid number. Please enter a numeric value.');
                }
            }
        }
        // 3. Evaluate the expression
        try {
            const result = (0, evaluator_1.evaluate)(expression, scope);
            console.log(`Result: ${expression} = ${result}`);
            // 4. Ask to continue (only after successful evaluation)
            const continueChoice = await promptQuestion('\nEvaluate another expression? (yes/no): ');
            if (continueChoice.toLowerCase() !== 'yes' && continueChoice.toLowerCase() !== 'y') {
                rl.close();
                console.log('Thank you for using the evaluator. Goodbye!');
                return; // Exit the start function
            }
            // If 'yes', the main `while(true)` loop continues, prompting for a new expression.
        }
        catch (error) {
            console.error(`Evaluation Error: ${error.message}`);
            // If error, loop continues directly to prompt for a new expression (fulfilling "reprompt for a new expression").
        }
    }
}
// To run the CLI when the script is executed directly
// if (require.main === module) {
//   start();
// }
