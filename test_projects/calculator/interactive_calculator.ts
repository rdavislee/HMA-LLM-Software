import { evaluateExpression } from './src/utils';
import * as readline from 'readline';

// Create readline interface for user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Store variables that persist across expressions
let variables: { [key: string]: number } = {};

console.log('🧮 Interactive Expression Calculator');
console.log('=====================================');
console.log('Enter mathematical expressions to evaluate them.');
console.log('You can use: +, -, *, /, ^, parentheses, and variables');
console.log('');
console.log('Commands:');
console.log('  - Type an expression (e.g., "2 + 3 * 4")');
console.log('  - Set variables with "var_name = value" (e.g., "x = 10")');
console.log('  - Type "vars" to see current variables');
console.log('  - Type "clear" to clear all variables');
console.log('  - Type "help" for examples');
console.log('  - Type "exit" to quit');
console.log('');

function showHelp(): void {
    console.log('\n📚 Examples:');
    console.log('  Basic math:     2 + 3 * 4');
    console.log('  Parentheses:    (2 + 3) * 4'); 
    console.log('  Exponents:      2 ^ 3');
    console.log('  Decimals:       3.14 * 2');
    console.log('  Variables:      x + y * 2');
    console.log('  Set variable:   x = 5');
    console.log('  Complex:        (x + y) ^ 2 / z');
    console.log('  Unary minus:    -x + 10');
    console.log('');
}

function showVariables(): void {
    if (Object.keys(variables).length === 0) {
        console.log('📊 No variables set yet. Set them with: variable_name = value');
    } else {
        console.log('📊 Current variables:');
        for (const [name, value] of Object.entries(variables)) {
            console.log(`  ${name} = ${value}`);
        }
    }
    console.log('');
}

function setVariable(input: string): boolean {
    // Match pattern: variable_name = number
    const match = input.match(/^\s*([a-zA-Z][a-zA-Z0-9]*)\s*=\s*(-?\d+\.?\d*)\s*$/);
    if (match) {
        const varName = match[1];
        const value = parseFloat(match[2]);
        variables[varName] = value;
        console.log(`✅ Set ${varName} = ${value}`);
        return true;
    }
    return false;
}

function processInput(input: string): void {
    const trimmed = input.trim().toLowerCase();
    
    // Handle commands
    if (trimmed === 'exit' || trimmed === 'quit') {
        console.log('👋 Goodbye!');
        rl.close();
        return;
    }
    
    if (trimmed === 'help') {
        showHelp();
        promptUser();
        return;
    }
    
    if (trimmed === 'vars' || trimmed === 'variables') {
        showVariables();
        promptUser();
        return;
    }
    
    if (trimmed === 'clear') {
        variables = {};
        console.log('🗑️  All variables cleared.\n');
        promptUser();
        return;
    }
    
    // Try to set a variable
    if (setVariable(input)) {
        promptUser();
        return;
    }
    
    // Try to evaluate as expression
    try {
        const result = evaluateExpression(input, variables);
        console.log(`📈 Result: ${result}`);
        
        // If it's a simple number, also show it in a more readable format
        if (result !== Math.floor(result)) {
            console.log(`   (≈ ${result.toFixed(6)})`);
        }
        console.log('');
        
    } catch (error: any) {
        console.log(`❌ Error: ${error.message}`);
        
        // Check if it might be an undefined variable and suggest setting it
        if (error.message.includes('Undefined variable:')) {
            const varMatch = error.message.match(/Undefined variable: (\w+)/);
            if (varMatch) {
                console.log(`💡 Hint: Set the variable with "${varMatch[1]} = some_number"`);
            }
        }
        console.log('');
    }
    
    promptUser();
}

// Main application interactive loop:
// 1. Prompts the user for input.
// 2. Processes the input:
//    - Checks for special commands (exit, help, vars, clear).
//    - Attempts to set a variable if the input matches 'var_name = value'.
//    - If not a command or variable assignment, attempts to evaluate as a mathematical expression.
// 3. Displays the result or an error message.
// 4. Recursively calls itself to prompt for the next input, continuing the loop until 'exit' is entered.
function promptUser(): void {
    rl.question('🧮 Enter expression: ', (input) => {
        if (input.trim() === '') {
            promptUser();
            return;
        }
        processInput(input);
    });
}

// Start the interactive session
console.log('Type "help" for examples or start entering expressions!');
console.log('');
promptUser();

// Handle Ctrl+C gracefully
rl.on('SIGINT', () => {
    console.log('\n👋 Goodbye!');
    process.exit(0);
}); 