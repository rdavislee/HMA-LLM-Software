import * as readline from 'readline';
import { parse } from './src/parser';
import { expressionUtils } from './src/utils';
import { Expression } from './src/expressionInterface';

interface Context {
    [variableName: string]: number;
}

class InteractiveCalculator {
    private rl: readline.Interface;

    constructor() {
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
    }

    private question(prompt: string): Promise<string> {
        return new Promise((resolve) => {
            this.rl.question(prompt, (answer) => {
                resolve(answer.trim());
            });
        });
    }

    private async showMenu(): Promise<string> {
        console.log('\n=== Mathematical Expression Calculator ===');
        console.log('1. Parse expression');
        console.log('2. Differentiate expression');
        console.log('3. Evaluate expression');
        console.log('4. Full workflow (parse → differentiate → evaluate)');
        console.log('5. Exit');
        console.log('==========================================');
        
        return await this.question('Choose an option (1-5): ');
    }

    private async parseExpression(): Promise<Expression | null> {
        try {
            const expressionStr = await this.question('Enter a mathematical expression: ');
            console.log(`\nParsing: "${expressionStr}"`);
            
            const parsedExpr = parse(expressionStr);
            console.log('✓ Successfully parsed!');
            console.log(`Expression structure: ${JSON.stringify(parsedExpr, null, 2)}`);
            console.log(`String representation: ${parsedExpr.toString()}`);
            
            return parsedExpr;
        } catch (error) {
            console.log(`✗ Parse error: ${error.message}`);
            return null;
        }
    }

    private async differentiateExpression(expr?: Expression): Promise<Expression | null> {
        try {
            let expression = expr;
            if (!expression) {
                const expressionStr = await this.question('Enter a mathematical expression: ');
                console.log(`\nParsing: "${expressionStr}"`);
                expression = parse(expressionStr);
                console.log('✓ Successfully parsed!');
            }

            const variable = await this.question('Enter variable to differentiate with respect to (e.g., x): ');
            console.log(`\nDifferentiating with respect to "${variable}"`);
            
            const derivative = expressionUtils.differentiate(expression, variable);
            console.log('✓ Successfully differentiated!');
            console.log(`Original: ${expression.toString()}`);
            console.log(`Derivative: ${derivative.toString()}`);
            
            return derivative;
        } catch (error) {
            console.log(`✗ Differentiation error: ${error.message}`);
            return null;
        }
    }

    private async evaluateExpression(expr?: Expression): Promise<number | null> {
        try {
            let expression = expr;
            if (!expression) {
                const expressionStr = await this.question('Enter a mathematical expression: ');
                console.log(`\nParsing: "${expressionStr}"`);
                expression = parse(expressionStr);
                console.log('✓ Successfully parsed!');
            }

            console.log(`\nExpression to evaluate: ${expression.toString()}`);
            
            // Extract variables from the expression
            const variables = this.extractVariables(expression);
            
            if (variables.length === 0) {
                console.log('No variables found. Evaluating directly...');
                const result = expressionUtils.evaluate(expression, {});
                console.log(`✓ Result: ${result}`);
                return result;
            }

            console.log(`Found variables: ${variables.join(', ')}`);
            const context: Context = {};
            
            for (const variable of variables) {
                const valueStr = await this.question(`Enter value for "${variable}": `);
                const value = parseFloat(valueStr);
                if (isNaN(value)) {
                    throw new Error(`Invalid number: "${valueStr}"`);
                }
                context[variable] = value;
            }
            
            const result = expressionUtils.evaluate(expression, context);
            console.log(`✓ Result: ${result}`);
            console.log(`Evaluation: ${expression.toString()} = ${result}`);
            console.log(`With values: ${Object.entries(context).map(([k, v]) => `${k}=${v}`).join(', ')}`);
            
            return result;
        } catch (error) {
            console.log(`✗ Evaluation error: ${error.message}`);
            return null;
        }
    }

    private extractVariables(expr: Expression): string[] {
        const variables = new Set<string>();
        
        const traverse = (node: Expression) => {
            if (node.type === 'variable') {
                variables.add((node as any).name);
            } else if (node.type === 'binaryOperation') {
                const binOp = node as any;
                traverse(binOp.left);
                traverse(binOp.right);
            } else if (node.type === 'unaryOperation') {
                const unOp = node as any;
                traverse(unOp.operand);
            } else if (node.type === 'functionCall') {
                const funcCall = node as any;
                funcCall.args.forEach(traverse);
            }
        };
        
        traverse(expr);
        return Array.from(variables).sort();
    }

    private async fullWorkflow(): Promise<void> {
        console.log('\n=== Full Workflow: Parse → Differentiate → Evaluate ===');
        
        // Step 1: Parse
        const expression = await this.parseExpression();
        if (!expression) return;
        
        // Step 2: Differentiate
        console.log('\n--- Differentiation Step ---');
        const derivative = await this.differentiateExpression(expression);
        if (!derivative) return;
        
        // Step 3: Evaluate original
        console.log('\n--- Evaluating Original Expression ---');
        await this.evaluateExpression(expression);
        
        // Step 4: Evaluate derivative
        console.log('\n--- Evaluating Derivative ---');
        await this.evaluateExpression(derivative);
    }

    private async showExamples(): Promise<void> {
        console.log('\n=== Expression Examples ===');
        console.log('Basic arithmetic: 2 + 3 * x');
        console.log('Powers: x^2 + 3*x + 1');
        console.log('Functions: sin(x) + cos(y)');
        console.log('Complex: ln(x^2 + 1) / (2*x + 3)');
        console.log('Trigonometry: sin(x) * cos(x) + tan(x/2)');
        console.log('Logarithms: log(10) + ln(e^x)');
        console.log('Nested: sin(cos(x)) + exp(ln(y))');
        console.log('============================\n');
    }

    async run(): Promise<void> {
        console.log('Welcome to the Interactive Mathematical Expression Calculator!');
        await this.showExamples();

        while (true) {
            try {
                const choice = await this.showMenu();
                
                switch (choice.trim()) {
                    case '1':
                        await this.parseExpression();
                        break;
                    case '2':
                        await this.differentiateExpression();
                        break;
                    case '3':
                        await this.evaluateExpression();
                        break;
                    case '4':
                        await this.fullWorkflow();
                        break;
                    case '5':
                        console.log('Goodbye! Thanks for using the calculator.');
                        this.rl.close();
                        return;
                    default:
                        console.log('Invalid choice. Please select 1-5.');
                }

                const continueChoice = await this.question('\nPress Enter to continue...');
            } catch (error) {
                console.log(`\n✗ Unexpected error: ${error.message}`);
                console.log('Please try again.');
            }
        }
    }
}

// Main execution
if (require.main === module) {
    const calculator = new InteractiveCalculator();
    calculator.run().catch(console.error);
} 