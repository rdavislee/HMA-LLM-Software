import * as readline from 'readline';
import { evaluate } from './evaluator';
import { parse, MathNode, SymbolNode } from 'mathjs';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

/**
 * Prompts the user with a question and returns their input.
 * @param query The question to ask.
 * @returns A Promise that resolves with the user's input string.
 */
function promptQuestion(query: string): Promise<string> {
  return new Promise((resolve) => rl.question(query, resolve));
}

/**
 * Checks if a given string can be parsed into a valid, finite number.
 * @param input The string to check.
 * @returns True if the string represents a valid finite number, false otherwise.
 */
export function isValidNumericInput(input: string): boolean {
  const value = parseFloat(input);
  return !isNaN(value) && isFinite(value);
}

/**
 * Extracts unique variable names from a mathematical expression string.
 * Uses mathjs.parse to build an AST and then recursively finds SymbolNodes.
 * @param expression The mathematical expression string.
 * @returns An array of unique variable names (strings).
 */
export function extractVariables(expression: string): string[] {
  try {
    const node = parse(expression);
    const variables = new Set<string>();

    node.filter(function (node: MathNode) {
      if (node.type === 'SymbolNode') {
        const symbolNode = node as SymbolNode;
        // Filter out built-in constants like 'pi' and 'e', and common functions
        if (!['pi', 'e', 'log', 'sin', 'cos', 'tan', 'sqrt', 'abs', 'exp', 'round', 'floor', 'ceil', 'fix', 'gamma', 'lgamma', 'factorial', 'permutations', 'combinations', 'gcd', 'lcm', 'mod', 'pow', 'nthRoot', 'hypot'].includes(symbolNode.name)) {
          variables.add(symbolNode.name);
        }
      }
      return true;
    });
    return Array.from(variables);
  } catch (error) {
    // If parsing fails (e.g., malformed expression), an error is thrown and caught by the caller.
    // Here, we re-throw to indicate a parsing issue.
    throw new Error(`Invalid expression syntax: ${(error as Error).message}`);
  }
}

/**
 * Starts the interactive command-line interface for expression evaluation.
 * Handles prompting for expressions, variables, evaluation, and error display.
 */
export async function start(): Promise<void> {
  console.log('Welcome to the Command-Line Mathematical Expression Evaluator!');
  console.log('Type \'exit\' or \'quit\' to stop at any time.');

  while (true) { // Loop indefinitely until an explicit return
    let expression = '';
    let variables: string[] = [];
    let scope: { [key: string]: number } = {};

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
      } catch (error: any) {
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
        } else {
          console.error('Invalid number. Please enter a numeric value.');
        }
      }
    }

    // 3. Evaluate the expression
    try {
      const result = evaluate(expression, scope);
      console.log(`Result: ${expression} = ${result}`);

      // 4. Ask to continue (only after successful evaluation)
      const continueChoice = await promptQuestion('\nEvaluate another expression? (yes/no): ');
      if (continueChoice.toLowerCase() !== 'yes' && continueChoice.toLowerCase() !== 'y') {
        rl.close();
        console.log('Thank you for using the evaluator. Goodbye!');
        return; // Exit the start function
      }
      // If 'yes', the main `while(true)` loop continues, prompting for a new expression.
    } catch (error: any) {
      console.error(`Evaluation Error: ${error.message}`);
      // If error, loop continues directly to prompt for a new expression (fulfilling "reprompt for a new expression").
    }
  }
}

// To run the CLI when the script is executed directly
// if (require.main === module) {
//   start();
// }
