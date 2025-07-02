"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UnaryOperationExpression = exports.BinaryOperationExpression = exports.VariableExpression = exports.NumberExpression = void 0;
class NumberExpression {
    constructor(value) {
        this.value = value;
        this.type = 'number';
    }
    evaluate(variables) {
        // NumberExpression simply returns its intrinsic value.
        return this.value;
    }
}
exports.NumberExpression = NumberExpression;
class VariableExpression {
    constructor(name) {
        this.name = name;
        this.type = 'variable';
    }
    evaluate(variables) {
        // VariableExpression looks up its name in the provided variables dictionary.
        // Throws an error if the variable is not found.
        if (!(this.name in variables)) {
            throw new Error(`Undefined variable: ${this.name}`);
        }
        return variables[this.name];
    }
}
exports.VariableExpression = VariableExpression;
class BinaryOperationExpression {
    constructor(operator, left, right) {
        this.operator = operator;
        this.left = left;
        this.right = right;
        this.type = 'binaryOperation';
    }
    evaluate(variables) {
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
exports.BinaryOperationExpression = BinaryOperationExpression;
class UnaryOperationExpression {
    constructor(operator, operand) {
        this.operator = operator;
        this.operand = operand;
        this.type = 'unaryOperation';
    }
    evaluate(variables) {
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
exports.UnaryOperationExpression = UnaryOperationExpression;
