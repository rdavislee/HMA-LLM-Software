import {
    Expression,
    ExpressionNode,
    NumberNode as INumberNode,
    VariableNode as IVariableNode,
    BinaryOperationNode as IBinaryOperationNode,
    UnaryOperationNode as IUnaryOperationNode,
    FunctionCallNode as IFunctionCallNode,
    ConstantNode as IConstantNode,
    ExponentialNode as IExponentialNode,
    BinaryOperatorType,
    UnaryOperatorType,
    FunctionNameType,
    ConstantType
} from './expressionInterface';

export { ExpressionNode }; // Re-export ExpressionNode for external use

/**
 * Represents a numeric literal in the expression.
 */
export class NumberNode implements INumberNode {
    readonly type = 'number';

    constructor(public value: number) {
        if (!Number.isFinite(value)) {
            throw new Error('NumberNode value must be a finite number.');
        }
    }

    toString(): string {
        return this.value.toString();
    }

    evaluate(variables: Record<string, number> = {}): number {
        return this.value;
    }

    differentiate(variableName: string): ExpressionNode {
        // Derivative of a constant is 0
        return new NumberNode(0);
    }
}

/**
 * Represents a variable in the expression.
 */
export class VariableNode implements IVariableNode {
    readonly type = 'variable';

    constructor(public name: string) {
        // Basic validation for variable name
        if (!name || typeof name !== 'string' || !/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(name)) {
            throw new Error(`Invalid variable name: '${name}'.`);
        }
    }

    toString(): string {
        return this.name;
    }

    evaluate(variables: Record<string, number> = {}): number {
        if (this.name in variables) {
            return variables[this.name];
        }
        throw new Error(`Variable '${this.name}' not defined in evaluation context.`);
    }

    differentiate(variableName: string): ExpressionNode {
        // Derivative of x with respect to x is 1
        // Derivative of x with respect to y (y != x) is 0
        return new NumberNode(this.name === variableName ? 1 : 0);
    }
}

/**
 * Represents a binary operation.
 */
export class BinaryOperationNode implements IBinaryOperationNode {
    readonly type = 'binaryOperation';

    constructor(public operator: BinaryOperatorType, public left: ExpressionNode, public right: ExpressionNode) {
        if (!left || !right) {
            throw new Error('BinaryOperationNode requires both left and right operands.');
        }
    }

    toString(): string {
        const opMap: Record<BinaryOperatorType, string> = {
            'add': '+',
            'subtract': '-',
            'multiply': '*',
            'divide': '/',
            'power': '^'
        };
        const opSymbol = opMap[this.operator];

        // Add parentheses for clarity based on operator precedence (simplified)
        const leftStr = this.left.toString();
        const rightStr = this.right.toString();

        return `(${leftStr} ${opSymbol} ${rightStr})`;
    }

    evaluate(variables: Record<string, number> = {}): number {
        const leftVal = this.left.evaluate(variables);
        const rightVal = this.right.evaluate(variables);

        switch (this.operator) {
            case 'add': return leftVal + rightVal;
            case 'subtract': return leftVal - rightVal;
            case 'multiply': return leftVal * rightVal;
            case 'divide':
                if (rightVal === 0) throw new Error('Division by zero.');
                return leftVal / rightVal;
            case 'power': return Math.pow(leftVal, rightVal);
            default: throw new Error(`Unknown binary operator: ${this.operator}`);
        }
    }

    differentiate(variableName: string): ExpressionNode {
        const dLeft = this.left.differentiate(variableName);
        const dRight = this.right.differentiate(variableName);

        switch (this.operator) {
            case 'add':
                return new BinaryOperationNode('add', dLeft, dRight);
            case 'subtract':
                return new BinaryOperationNode('subtract', dLeft, dRight);
            case 'multiply':
                // Product rule: (f*g)' = f'*g + f*g'
                const term1 = new BinaryOperationNode('multiply', dLeft, this.right);
                const term2 = new BinaryOperationNode('multiply', this.left, dRight);
                return new BinaryOperationNode('add', term1, term2);
            case 'divide':
                // Quotient rule: (f/g)' = (f'*g - f*g') / g^2
                const numerator = new BinaryOperationNode('subtract',
                    new BinaryOperationNode('multiply', dLeft, this.right),
                    new BinaryOperationNode('multiply', this.left, dRight)
                );
                const denominator = new BinaryOperationNode('power', this.right, new NumberNode(2));
                return new BinaryOperationNode('divide', numerator, denominator);
            case 'power':
                // d/dx(f^g) = f^g * (g'ln(f) + g*f'/f)
                // If g is a constant (NumberNode), then d/dx(f^c) = c * f^(c-1) * f'
                if (this.right instanceof NumberNode) {
                    const c = this.right.value;
                    if (c === 0) return new NumberNode(0); // f^0 = 1, derivative is 0
                    if (c === 1) return dLeft; // f^1 = f, derivative is f'
                    const newExponent = new NumberNode(c - 1);
                    const powerTerm = new BinaryOperationNode('power', this.left, newExponent);
                    const multipliedTerm = new BinaryOperationNode('multiply', new NumberNode(c), powerTerm);
                    return new BinaryOperationNode('multiply', multipliedTerm, dLeft);
                } else if (this.left instanceof ConstantNode && this.left.name === 'e') {
                    // This case should ideally be handled by ExponentialNode for e^g
                    // For now, if it's e^g, delegate to ExponentialNode's differentiation.
                    // This is a bit hacky as it creates a new ExponentialNode just for diff.
                    // A better approach would be to ensure parser creates ExponentialNode for e^x.
                    return new ExponentialNode(this.right).differentiate(variableName);
                }
                throw new Error('Differentiation of power operation (f^g) not fully implemented for non-constant exponent or base not \'e\'.');
            default:
                throw new Error(`Differentiation for operator ${this.operator} not implemented.`);
        }
    }
}

/**
 * Represents a unary operation.
 */
export class UnaryOperationNode implements IUnaryOperationNode {
    readonly type = 'unaryOperation';

    constructor(public operator: UnaryOperatorType, public operand: ExpressionNode) {
        if (!operand) {
            throw new Error('UnaryOperationNode requires an operand.');
        }
    }

    toString(): string {
        const opMap: Record<UnaryOperatorType, string> = {
            'negate': '-'
        };
        const opSymbol = opMap[this.operator];
        return `${opSymbol}${this.operand.toString()}`;
    }

    evaluate(variables: Record<string, number> = {}): number {
        const operandVal = this.operand.evaluate(variables);
        switch (this.operator) {
            case 'negate': return -operandVal;
            default: throw new Error(`Unknown unary operator: ${this.operator}`);
        }
    }

    differentiate(variableName: string): ExpressionNode {
        const dOperand = this.operand.differentiate(variableName);
        switch (this.operator) {
            case 'negate':
                return new UnaryOperationNode('negate', dOperand);
            default:
                throw new Error(`Differentiation for unary operator ${this.operator} not implemented.`);
        }
    }
}

/**
 * Represents a function call.
 */
export class FunctionCallNode implements IFunctionCallNode {
    readonly type = 'functionCall';

    constructor(public name: FunctionNameType, public args: ExpressionNode[]) {
        if (!name || typeof name !== 'string') {
            throw new Error('FunctionCallNode requires a function name.');
        }
        if (!Array.isArray(args)) {
            throw new Error('FunctionCallNode args must be an array.');
        }
        // Basic validation for common functions requiring single argument
        if (['log', 'sin', 'cos', 'tan', 'ln', 'exp', 'sec', 'csc', 'cot', 'asin', 'acos', 'atan', 'asec', 'acsc', 'acot'].includes(name) && args.length !== 1) {
            throw new Error(`Function '${name}' expects exactly one argument, but received ${args.length}.`);
        }
    }

    toString(): string {
        const argsStr = this.args.map(arg => arg.toString()).join(', ');
        return `${this.name}(${argsStr})`;
    }

    evaluate(variables: Record<string, number> = {}): number {
        if (this.args.length !== 1) {
            throw new Error(`Evaluation not supported for function '${this.name}' with ${this.args.length} arguments.`);
        }
        const argVal = this.args[0].evaluate(variables);

        switch (this.name) {
            case 'sin': return Math.sin(argVal);
            case 'cos': return Math.cos(argVal);
            case 'tan': return Math.tan(argVal);
            case 'log': return Math.log10(argVal); // Common log (base 10)
            case 'ln': return Math.log(argVal); // Natural log (base e)
            case 'exp': return Math.exp(argVal); // e^x, for general exp() function
            case 'sec': return 1 / Math.cos(argVal);
            case 'csc': return 1 / Math.sin(argVal);
            case 'cot': return 1 / Math.tan(argVal);
            case 'asin': return Math.asin(argVal);
            case 'acos': return Math.acos(argVal);
            case 'atan': return Math.atan(argVal);
            // Inverse sec/csc/cot are more complex, might need library or approximation
            case 'asec': throw new Error('asec evaluation not implemented.');
            case 'acsc': throw new Error('acsc evaluation not implemented.');
            case 'acot': throw new Error('acot evaluation not implemented.');
            default: throw new Error(`Unknown function: ${this.name}`);
        }
    }

    differentiate(variableName: string): ExpressionNode {
        if (this.args.length !== 1) {
            throw new Error(`Differentiation not supported for function '${this.name}' with ${this.args.length} arguments.`);
        }
        const operand = this.args[0];
        const dOperand = operand.differentiate(variableName);

        // Chain rule: d/dx(f(u)) = f'(u) * du/dx
        let fPrimeOfU: ExpressionNode; // Derivative of the outer function with respect to its argument

        switch (this.name) {
            case 'sin':
                fPrimeOfU = new FunctionCallNode('cos', [operand]);
                break;
            case 'cos':
                fPrimeOfU = new UnaryOperationNode('negate', new FunctionCallNode('sin', [operand]));
                break;
            case 'tan':
                // d/du(tan(u)) = sec^2(u) = (sec(u))^2
                fPrimeOfU = new BinaryOperationNode('power', new FunctionCallNode('sec', [operand]), new NumberNode(2));
                break;
            case 'ln':
                // d/du(ln(u)) = 1/u
                fPrimeOfU = new BinaryOperationNode('divide', new NumberNode(1), operand);
                break;
            case 'log':
                // d/du(log_b(u)) = 1/(u * ln(b))
                // Assuming log is base 10: 1/(u * ln(10))
                fPrimeOfU = new BinaryOperationNode('divide', new NumberNode(1),
                    new BinaryOperationNode('multiply', operand, new FunctionCallNode('ln', [new NumberNode(10)]))
                );
                break;
            case 'exp':
                // d/du(exp(u)) = exp(u)
                fPrimeOfU = new FunctionCallNode('exp', [operand]); // For general exp() function
                break;
            case 'sec':
                // d/du(sec(u)) = sec(u)tan(u)
                fPrimeOfU = new BinaryOperationNode('multiply', new FunctionCallNode('sec', [operand]), new FunctionCallNode('tan', [operand]));
                break;
            case 'csc':
                // d/du(csc(u)) = -csc(u)cot(u)
                fPrimeOfU = new UnaryOperationNode('negate', new BinaryOperationNode('multiply', new FunctionCallNode('csc', [operand]), new FunctionCallNode('cot', [operand])));
                break;
            case 'cot':
                // d/du(cot(u)) = -csc^2(u) = -(csc(u))^2
                fPrimeOfU = new UnaryOperationNode('negate', new BinaryOperationNode('power', new FunctionCallNode('csc', [operand]), new NumberNode(2)));
                break;
            case 'asin':
                // d/du(asin(u)) = 1 / sqrt(1 - u^2)
                fPrimeOfU = new BinaryOperationNode('divide', new NumberNode(1),
                    new BinaryOperationNode('power',
                        new BinaryOperationNode('subtract', new NumberNode(1), new BinaryOperationNode('power', operand, new NumberNode(2))),
                        new NumberNode(0.5) // sqrt
                    )
                );
                break;
            case 'acos':
                // d/du(acos(u)) = -1 / sqrt(1 - u^2)
                fPrimeOfU = new UnaryOperationNode('negate', new BinaryOperationNode('divide', new NumberNode(1),
                    new BinaryOperationNode('power',
                        new BinaryOperationNode('subtract', new NumberNode(1), new BinaryOperationNode('power', operand, new NumberNode(2))),
                        new NumberNode(0.5) // sqrt
                    )
                ));
                break;
            case 'atan':
                // d/du(atan(u)) = 1 / (1 + u^2)
                fPrimeOfU = new BinaryOperationNode('divide', new NumberNode(1),
                    new BinaryOperationNode('add', new NumberNode(1), new BinaryOperationNode('power', operand, new NumberNode(2)))
                );
                break;
            // Inverse sec/csc/cot differentiation are more complex, for now throw error
            case 'asec':
            case 'acsc':
            case 'acot':
                throw new Error(`Differentiation for function '${this.name}' not fully implemented.`);
            default:
                throw new Error(`Differentiation for function '${this.name}' not implemented.`);
        }

        // Apply chain rule: f'(u) * du/dx
        return new BinaryOperationNode('multiply', fPrimeOfU, dOperand);
    }
}

/**
 * Represents a mathematical constant (e.g., 'e', 'pi').
 */
export class ConstantNode implements IConstantNode {
    readonly type = 'constant';

    constructor(public name: ConstantType) {
        if (!['e', 'pi'].includes(name)) {
            throw new Error(`Invalid constant name: '${name}'. Must be 'e' or 'pi'.`);
        }
    }

    toString(): string {
        return this.name;
    }

    evaluate(variables: Record<string, number> = {}): number {
        switch (this.name) {
            case 'e': return Math.E;
            case 'pi': return Math.PI;
            default: throw new Error(`Unknown constant: ${this.name}`);
        }
    }

    differentiate(variableName: string): ExpressionNode {
        // Derivative of a constant is 0
        return new NumberNode(0);
    }
}

/**
 * Represents the exponential function e^x.
 * This is distinct from a general power operation to allow specific handling for differentiation/integration.
 */
export class ExponentialNode implements IExponentialNode {
    readonly type = 'exponential';

    constructor(public exponent: ExpressionNode) {
        if (!exponent) {
            throw new Error('ExponentialNode requires an exponent expression.');
        }
    }

    toString(): string {
        // Parenthesize the exponent if it's not a simple number or variable
        const exponentStr = this.exponent.toString();
        // A simple heuristic for when to parenthesize:
        // if it contains operations or is a complex function call, add parens.
        // This is a simplification; a proper parser/printer would handle precedence.
        if (this.exponent.type === 'binaryOperation' || this.exponent.type === 'unaryOperation' || this.exponent.type === 'functionCall') {
            return `e^(${exponentStr})`;
        }
        return `e^${exponentStr}`;
    }

    evaluate(variables: Record<string, number> = {}): number {
        const exponentVal = this.exponent.evaluate(variables);
        return Math.exp(exponentVal);
    }

    differentiate(variableName: string): ExpressionNode {
        // d/dx(e^u) = e^u * du/dx
        const dExponent = this.exponent.differentiate(variableName);
        // We should avoid creating a multiplication node if du/dx is 1 or 0
        if (dExponent instanceof NumberNode && dExponent.value === 0) {
            return new NumberNode(0);
        }
        if (dExponent instanceof NumberNode && dExponent.value === 1) {
            return this; // Return e^u
        }
        // Otherwise, return e^u * du/dx
        return new BinaryOperationNode('multiply', this, dExponent);
    }
}

/**
 * Factory function for NumberNode.
 */
export const num = (value: number): NumberNode => new NumberNode(value);

/**
 * Factory function for VariableNode.
 */
export const variable = (name: string): VariableNode => new VariableNode(name);

/**
 * Factory function for BinaryOperationNode.
 */
export const op = (operator: BinaryOperatorType, left: ExpressionNode, right: ExpressionNode): BinaryOperationNode => new BinaryOperationNode(operator, left, right);

/**
 * Factory function for UnaryOperationNode.
 */
export const unaryOp = (operator: UnaryOperatorType, operand: ExpressionNode): UnaryOperationNode => new UnaryOperationNode(operator, operand);

/**
 * Factory function for FunctionCallNode.
 */
export const func = (name: FunctionNameType, args: ExpressionNode[]): FunctionCallNode => new FunctionCallNode(name, args);

/**
 * Factory function for ConstantNode.
 */
export const constant = (name: ConstantType): ConstantNode => new ConstantNode(name);

/**
 * Factory function for ExponentialNode.
 */
export const exponential = (exponent: ExpressionNode): ExponentialNode => new ExponentialNode(exponent);
