import * as readline from 'readline';
import { parse } from './src/parser';
import { ExpressionUtils } from './src/utils';
import { ExpressionNode } from './src/expressionInterface';
import { IntegrationResult } from './src/utils.interface';

interface Context {
    [variableName: string]: number;
}

class InteractiveCalculator {
    private rl: readline.Interface;
    private expressionUtils: ExpressionUtils;

    constructor() {
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        this.expressionUtils = new ExpressionUtils();
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
        console.log('3. Integrate indefinite');
        console.log('4. Integrate definite');
        console.log('5. Evaluate expression');
        console.log('6. Full workflow (parse → differentiate → integrate → evaluate)');
        console.log('7. Exit');
        console.log('==========================================');
        
        return await this.question('Choose an option (1-7): ');
    }

    private async parseExpression(): Promise<ExpressionNode | null> {
        try {
            const expressionStr = await this.question('Enter a mathematical expression: ');
            console.log(`\nParsing: "${expressionStr}"`);
            
            const parsedExpr = parse(expressionStr) as ExpressionNode;
            console.log('✓ Successfully parsed!');
            console.log(`Expression structure: ${JSON.stringify(parsedExpr, null, 2)}`);
            console.log(`String representation: ${parsedExpr.toString()}`);
            
            return parsedExpr;
        } catch (error) {
            console.log(`✗ Parse error: ${error.message}`);
            return null;
        }
    }

    private async differentiateExpression(expr?: ExpressionNode): Promise<ExpressionNode | null> {
        try {
            let expression = expr;
            if (!expression) {
                const expressionStr = await this.question('Enter a mathematical expression: ');
                console.log(`\nParsing: "${expressionStr}"`);
                expression = parse(expressionStr) as ExpressionNode;
                console.log('✓ Successfully parsed!');
            }

            const variable = await this.question('Enter variable to differentiate with respect to (e.g., x): ');
            console.log(`\nDifferentiating with respect to "${variable}"`);
            
            const derivative = this.expressionUtils.differentiate(expression, variable);
            console.log('✓ Successfully differentiated!');
            console.log(`Original: ${expression.toString()}`);
            console.log(`Derivative: ${derivative.toString()}`);
            
            return derivative;
        } catch (error) {
            console.log(`✗ Differentiation error: ${error.message}`);
            return null;
        }
    }

    private async integrateIndefinite(expr?: ExpressionNode): Promise<ExpressionNode | null> {
        try {
            let expression = expr;
            if (!expression) {
                const expressionStr = await this.question('Enter a mathematical expression: ');
                console.log(`\nParsing: "${expressionStr}"`);
                expression = parse(expressionStr) as ExpressionNode;
                console.log('✓ Successfully parsed!');
            }

            const variable = await this.question('Enter variable to integrate with respect to (e.g., x): ');
            console.log(`\nIntegrating with respect to "${variable}"`);
            
            const result: IntegrationResult = this.expressionUtils.integrateIndefinite(expression, variable);
            
            if (result.unintegratable) {
                console.log('✗ Integration failed: Expression cannot be integrated with current rules');
                console.log(`Original: ${expression.toString()}`);
                console.log('This expression requires more advanced integration techniques not yet implemented.');
                return null;
            } else {
                console.log('✓ Successfully integrated!');
                console.log(`Original: ${expression.toString()}`);
                console.log(`Indefinite integral: ${(result.integratedExpression as ExpressionNode).toString()}`);
                console.log(`Constant of integration: ${result.constantOfIntegration}`);
                return result.integratedExpression as ExpressionNode;
            }
        } catch (error) {
            console.log(`✗ Integration error: ${error.message}`);
            return null;
        }
    }

    private async integrateDefinite(expr?: ExpressionNode): Promise<number | null> {
        try {
            let expression = expr;
            if (!expression) {
                const expressionStr = await this.question('Enter a mathematical expression: ');
                console.log(`\nParsing: "${expressionStr}"`);
                expression = parse(expressionStr) as ExpressionNode;
                console.log('✓ Successfully parsed!');
            }

            const variable = await this.question('Enter variable to integrate with respect to (e.g., x): ');
            const lowerBoundStr = await this.question('Enter lower bound: ');
            const upperBoundStr = await this.question('Enter upper bound: ');
            
            const lowerBound = parseFloat(lowerBoundStr);
            const upperBound = parseFloat(upperBoundStr);
            
            if (isNaN(lowerBound) || isNaN(upperBound)) {
                throw new Error('Invalid bounds: must be numbers');
            }

            console.log(`\nIntegrating with respect to "${variable}" from ${lowerBound} to ${upperBound}`);
            
            // Ask if they want to use numerical integration
            const useNumerical = await this.question('Use numerical integration? (y/N): ');
            let options = {};
            
            if (useNumerical.toLowerCase() === 'y' || useNumerical.toLowerCase() === 'yes') {
                const numRectanglesStr = await this.question('Enter number of rectangles (default 1000): ');
                const numRectangles = numRectanglesStr ? parseInt(numRectanglesStr) : 1000;
                
                if (isNaN(numRectangles) || numRectangles <= 0) {
                    throw new Error('Number of rectangles must be a positive integer');
                }
                
                options = { numRectangles };
                console.log(`Using numerical integration with ${numRectangles} rectangles...`);
            } else {
                console.log('Using symbolic integration...');
            }
            
            const result = this.expressionUtils.integrateDefinite(expression, variable, lowerBound, upperBound, options);
            console.log('✓ Successfully integrated!');
            console.log(`Original: ${expression.toString()}`);
            console.log(`Definite integral from ${lowerBound} to ${upperBound}: ${result}`);
            
            return result;
        } catch (error) {
            console.log(`✗ Integration error: ${error.message}`);
            return null;
        }
    }

    private async evaluateExpression(expr?: ExpressionNode): Promise<number | null> {
        try {
            let expression = expr;
            if (!expression) {
                const expressionStr = await this.question('Enter a mathematical expression: ');
                console.log(`\nParsing: "${expressionStr}"`);
                expression = parse(expressionStr) as ExpressionNode;
                console.log('✓ Successfully parsed!');
            }

            console.log(`\nExpression to evaluate: ${expression.toString()}`);
            
            // Extract variables from the expression
            const variables = this.extractVariables(expression);
            
            if (variables.length === 0) {
                console.log('No variables found. Evaluating directly...');
                const result = this.expressionUtils.evaluate(expression, {});
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
            
            const result = this.expressionUtils.evaluate(expression, context);
            console.log(`✓ Result: ${result}`);
            console.log(`Evaluation: ${expression.toString()} = ${result}`);
            console.log(`With values: ${Object.entries(context).map(([k, v]) => `${k}=${v}`).join(', ')}`);
            
            return result;
        } catch (error) {
            console.log(`✗ Evaluation error: ${error.message}`);
            return null;
        }
    }

    private extractVariables(expr: ExpressionNode): string[] {
        const variables = new Set<string>();
        
        const traverse = (node: ExpressionNode) => {
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
            } else if (node.type === 'exponential') {
                const exp = node as any;
                traverse(exp.exponent);
            }
        };
        
        traverse(expr);
        return Array.from(variables).filter(v => v !== 'C').sort(); // Filter out integration constant 'C'
    }

    private async fullWorkflow(): Promise<void> {
        console.log('\n=== Full Workflow: Parse → Differentiate → Integrate → Evaluate ===');
        
        // Step 1: Parse
        const expression = await this.parseExpression();
        if (!expression) return;
        
        // Step 2: Differentiate
        console.log('\n--- Differentiation Step ---');
        const derivative = await this.differentiateExpression(expression);
        if (!derivative) return;
        
        // Step 3: Integrate Indefinite
        console.log('\n--- Indefinite Integration Step ---');
        const indefiniteIntegral = await this.integrateIndefinite(expression);
        
        // Step 4: Integrate Definite
        console.log('\n--- Definite Integration Step ---');
        await this.integrateDefinite(expression);
        
        // Step 5: Evaluate original
        console.log('\n--- Evaluating Original Expression ---');
        await this.evaluateExpression(expression);
        
        // Step 6: Evaluate derivative
        console.log('\n--- Evaluating Derivative ---');
        await this.evaluateExpression(derivative);
        
        // Step 7: Evaluate indefinite integral (if available)
        if (indefiniteIntegral) {
            console.log('\n--- Evaluating Indefinite Integral ---');
            await this.evaluateExpression(indefiniteIntegral);
        }
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
        console.log('Integration examples: x^2, sin(x), e^x, 1/x');
        console.log('============================\n');
    }

    async run(): Promise<void> {
        console.log('Welcome to the Interactive Mathematical Expression Calculator!');
        console.log('Now with integration capabilities!');
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
                        await this.integrateIndefinite();
                        break;
                    case '4':
                        await this.integrateDefinite();
                        break;
                    case '5':
                        await this.evaluateExpression();
                        break;
                    case '6':
                        await this.fullWorkflow();
                        break;
                    case '7':
                        console.log('Goodbye! Thanks for using the calculator.');
                        this.rl.close();
                        return;
                    default:
                        console.log('Invalid choice. Please select 1-7.');
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