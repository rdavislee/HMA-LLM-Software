import { IExpression, INumberExpression, IVariableExpression, IBinaryOperationExpression, IUnaryOperationExpression, Expression } from './expressionInterface';

export class NumberExpression implements INumberExpression {
    type: 'number' = 'number';
    constructor(public value: number) {}

    evaluate(variables: { [key: string]: number }): number {
        // NumberExpression simply returns its intrinsic value.
        return this.value;
    }
}

export class VariableExpression implements IVariableExpression {
    type: 'variable' = 'variable';
    constructor(public name: string) {}

    evaluate(variables: { [key: string]: number }): number {
        // VariableExpression looks up its name in the provided variables dictionary.
        // Throws an error if the variable is not found.
        if (!(this.name in variables)) {
            throw new Error(`Undefined variable: ${this.name}`);
        }
        return variables[this.name];
    }
}

export class BinaryOperationExpression implements IBinaryOperationExpression {
    type: 'binaryOperation' = 'binaryOperation';
    constructor(
        public operator: '+' | '-' | '*' | '/' | '^',
        public left: Expression,
        public right: Expression
    ) {}

    evaluate(variables: { [key: string]: number }): number {
        // BinaryOperationExpression evaluates its left and right operands recursively,
        // then performs the specified operation.
        const leftValue = this.left.evaluate(variables);
        const rightValue = this.right.evaluate(variables);

        switch (this.operator) {
            case '+':
                return leftValue + rightValue;
            case '-':
                return leftValue - rightValue;
            case '*':
                return leftValue * rightValue;
            case '/':
                if (rightValue === 0) {
                    throw new Error('Division by zero');
                }
                return leftValue / rightValue;
            case '^':
                return Math.pow(leftValue, rightValue);
            default:
                // This case should ideally not be reached due to TypeScript's type checking
                // but is included for robustness.
                throw new Error(`Unknown binary operator: ${this.operator}`);
        }
    }
}

export class UnaryOperationExpression implements IUnaryOperationExpression {
    type: 'unaryOperation' = 'unaryOperation';
    constructor(
        public operator: '+' | '-',
        public operand: Expression
    ) {}

    evaluate(variables: { [key: string]: number }): number {
        // UnaryOperationExpression evaluates its operand and applies the unary operator.
        const operandValue = this.operand.evaluate(variables);

        switch (this.operator) {
            case '+':
                // Unary plus doesn't change the value
                return +operandValue;
            case '-':
                // Unary minus negates the value
                return -operandValue;
            default:
                // This case should ideally not be reached due to TypeScript's type checking
                // but is included for robustness.
                throw new Error(`Unknown unary operator: ${this.operator}`);
        }
    }
}
