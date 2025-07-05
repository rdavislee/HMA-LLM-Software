import * as readline from 'readline';
import { tokenize } from '../parser/tokenizer.js';
import { parse } from '../parser/parser.js';
import { evaluate } from '../operations/evaluate.js';
import { differentiate } from '../operations/differentiate.js';
import { integrate } from '../operations/integrate.js';
import { simplify } from '../operations/simplify.js';
import { CalculatorError } from '../utils/error.js';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

export async function run(): Promise<void> {
  console.log("Welcome to the Symbolic Calculator CLI!");
  console.log("Type 'exit' to quit.");

  let lastResult: any = null; // Use 'any' for now, will be more specific with AST types

  while (true) {
    const expression = await askQuestion('> Enter expression: ');

    if (expression.toLowerCase() === 'exit') {
      console.log('Exiting calculator. Goodbye!');
      break;
    }

    if (!expression.trim()) {
      continue;
    }

    try {
      const tokens = tokenize(expression);
      // console.log('Tokens:', tokens); // For debugging

      let ast = parse(tokens);
      // console.log('AST:', JSON.stringify(ast, null, 2)); // For debugging

      // Simple evaluation for now, full CLI logic will be added in Phase 6
      const result = evaluate(ast, new Map()); // No variables for initial test
      console.log('Result:', result);
      lastResult = result;

    } catch (error) {
      if (error instanceof CalculatorError) {
        console.error(`Error: ${error.message}`);
      } else if (error instanceof Error) {
        console.error(`An unexpected error occurred: ${error.message}`);
      } else {
        console.error('An unknown error occurred.');
      }
    }
  }

  rl.close();
}

function askQuestion(query: string): Promise<string> {
  return new Promise(resolve => rl.question(query, resolve));
}
