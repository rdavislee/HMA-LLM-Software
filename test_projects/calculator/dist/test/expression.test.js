"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const chai_1 = require("chai");
const expression_1 = require("../src/expression"); // Assuming expression.ts exports these directly
describe('Expression Evaluation', () => {
    // Test Partition 1: Basic Numbers
    describe('NumberExpression', () => {
        it('should evaluate a number correctly', () => {
            const expr = new expression_1.NumberExpression(42);
            (0, chai_1.expect)(expr.evaluate({})).to.equal(42);
        });
        it('should evaluate a negative number correctly', () => {
            const expr = new expression_1.NumberExpression(-10);
            (0, chai_1.expect)(expr.evaluate({})).to.equal(-10);
        });
        it('should evaluate a floating point number correctly', () => {
            const expr = new expression_1.NumberExpression(3.14);
            (0, chai_1.expect)(expr.evaluate({})).to.equal(3.14);
        });
    });
    // Test Partition 2: Basic Variables
    describe('VariableExpression', () => {
        it('should evaluate a variable with provided context', () => {
            const expr = new expression_1.VariableExpression('x');
            (0, chai_1.expect)(expr.evaluate({ x: 100 })).to.equal(100);
        });
        it('should throw an error if a variable is undefined', () => {
            const expr = new expression_1.VariableExpression('y');
            (0, chai_1.expect)(() => expr.evaluate({ x: 5 })).to.throw('Undefined variable: y');
        });
        it('should evaluate a variable with zero value', () => {
            const expr = new expression_1.VariableExpression('z');
            (0, chai_1.expect)(expr.evaluate({ z: 0 })).to.equal(0);
        });
    });
    // Test Partition 3: Basic Binary Operations
    describe('BinaryOperationExpression', () => {
        it('should perform addition', () => {
            const expr = new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(5), new expression_1.NumberExpression(3));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(8);
        });
        it('should perform subtraction', () => {
            const expr = new expression_1.BinaryOperationExpression('-', new expression_1.NumberExpression(10), new expression_1.NumberExpression(4));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(6);
        });
        it('should perform multiplication', () => {
            const expr = new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(6), new expression_1.NumberExpression(7));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(42);
        });
        it('should perform division', () => {
            const expr = new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(20), new expression_1.NumberExpression(5));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(4);
        });
        it('should perform exponentiation', () => {
            const expr = new expression_1.BinaryOperationExpression('^', new expression_1.NumberExpression(2), new expression_1.NumberExpression(3));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(8); // 2^3 = 8
        });
        it('should handle division by zero', () => {
            const expr = new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(10), new expression_1.NumberExpression(0));
            (0, chai_1.expect)(() => expr.evaluate({})).to.throw('Division by zero');
        });
        it('should handle operations with negative numbers', () => {
            const expr = new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(-5), new expression_1.NumberExpression(-3));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(-8);
        });
        it('should handle floating point results', () => {
            const expr = new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(10), new expression_1.NumberExpression(3));
            (0, chai_1.expect)(expr.evaluate({})).to.be.closeTo(3.333, 0.001);
        });
    });
    // Test Partition 4: Basic Unary Operations
    describe('UnaryOperationExpression', () => {
        it('should perform negation on a positive number', () => {
            const expr = new expression_1.UnaryOperationExpression('-', new expression_1.NumberExpression(7));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(-7);
        });
        it('should perform negation on a negative number', () => {
            const expr = new expression_1.UnaryOperationExpression('-', new expression_1.NumberExpression(-5));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(5);
        });
        it('should perform negation on zero', () => {
            const expr = new expression_1.UnaryOperationExpression('-', new expression_1.NumberExpression(0));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(0);
        });
    });
    // Test Partition 5: PEMDAS Order of Operations (Parentheses, Exponents, Multiplication/Division, Addition/Subtraction)
    describe('PEMDAS Order of Operations', () => {
        it('should handle multiplication before addition', () => {
            // 2 + 3 * 4 = 2 + 12 = 14
            const expr = new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(2), new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(3), new expression_1.NumberExpression(4)));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(14);
        });
        it('should handle division before subtraction', () => {
            // 10 - 6 / 2 = 10 - 3 = 7
            const expr = new expression_1.BinaryOperationExpression('-', new expression_1.NumberExpression(10), new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(6), new expression_1.NumberExpression(2)));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(7);
        });
        it('should handle exponentiation before multiplication', () => {
            // 2 * 3 ^ 2 = 2 * 9 = 18
            const expr = new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(2), new expression_1.BinaryOperationExpression('^', new expression_1.NumberExpression(3), new expression_1.NumberExpression(2)));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(18);
        });
        it('should handle parentheses overriding order', () => {
            // (2 + 3) * 4 = 5 * 4 = 20
            const expr = new expression_1.BinaryOperationExpression('*', new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(2), new expression_1.NumberExpression(3)), new expression_1.NumberExpression(4));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(20);
        });
        it('should handle multiple nested parentheses', () => {
            // ( (10 - 2) / 4 ) ^ 3 = (8 / 4) ^ 3 = 2 ^ 3 = 8
            const expr = new expression_1.BinaryOperationExpression('^', new expression_1.BinaryOperationExpression('/', new expression_1.BinaryOperationExpression('-', new expression_1.NumberExpression(10), new expression_1.NumberExpression(2)), new expression_1.NumberExpression(4)), new expression_1.NumberExpression(3));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(8);
        });
        it('should handle complex mixed operations', () => {
            // 10 / 2 + 3 * (5 - 1) - 2^3
            // 10 / 2 + 3 * 4 - 8
            // 5 + 12 - 8
            // 17 - 8 = 9
            const expr = new expression_1.BinaryOperationExpression('-', new expression_1.BinaryOperationExpression('+', new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(10), new expression_1.NumberExpression(2)), new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(3), new expression_1.BinaryOperationExpression('-', new expression_1.NumberExpression(5), new expression_1.NumberExpression(1)))), new expression_1.BinaryOperationExpression('^', new expression_1.NumberExpression(2), new expression_1.NumberExpression(3)));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(9);
        });
    });
    // Test Partition 6: Variable Evaluation in Complex Expressions
    describe('Variable Evaluation in Complex Expressions', () => {
        it('should evaluate variables in a simple binary operation', () => {
            // x + y with x=5, y=3 => 8
            const expr = new expression_1.BinaryOperationExpression('+', new expression_1.VariableExpression('x'), new expression_1.VariableExpression('y'));
            (0, chai_1.expect)(expr.evaluate({ x: 5, y: 3 })).to.equal(8);
        });
        it('should evaluate variables in an expression with mixed operations', () => {
            // x + 2 * y - z with x=10, y=3, z=4 => 10 + 2*3 - 4 = 10 + 6 - 4 = 12
            const expr = new expression_1.BinaryOperationExpression('-', new expression_1.BinaryOperationExpression('+', new expression_1.VariableExpression('x'), new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(2), new expression_1.VariableExpression('y'))), new expression_1.VariableExpression('z'));
            (0, chai_1.expect)(expr.evaluate({ x: 10, y: 3, z: 4 })).to.equal(12);
        });
        it('should evaluate variables inside parentheses', () => {
            // (x + y) / z with x=10, y=5, z=3 => (15) / 3 = 5
            const expr = new expression_1.BinaryOperationExpression('/', new expression_1.BinaryOperationExpression('+', new expression_1.VariableExpression('x'), new expression_1.VariableExpression('y')), new expression_1.VariableExpression('z'));
            (0, chai_1.expect)(expr.evaluate({ x: 10, y: 5, z: 3 })).to.equal(5);
        });
        it('should handle unary negation with variables', () => {
            // -x + 5 with x=10 => -10 + 5 = -5
            const expr = new expression_1.BinaryOperationExpression('+', new expression_1.UnaryOperationExpression('-', new expression_1.VariableExpression('x')), new expression_1.NumberExpression(5));
            (0, chai_1.expect)(expr.evaluate({ x: 10 })).to.equal(-5);
        });
        it('should handle complex expression with multiple variables and operations', () => {
            // (a + b) * c / (d - e) ^ 2
            // a=1, b=2, c=4, d=7, e=5
            // (1 + 2) * 4 / (2) ^ 2
            // 3 * 4 / 4
            // 12 / 4 = 3
            const expr = new expression_1.BinaryOperationExpression('/', new expression_1.BinaryOperationExpression('*', new expression_1.BinaryOperationExpression('+', new expression_1.VariableExpression('a'), new expression_1.VariableExpression('b')), new expression_1.VariableExpression('c')), new expression_1.BinaryOperationExpression('^', new expression_1.BinaryOperationExpression('-', new expression_1.VariableExpression('d'), new expression_1.VariableExpression('e')), new expression_1.NumberExpression(2)));
            const variables = { a: 1, b: 2, c: 4, d: 7, e: 5 };
            (0, chai_1.expect)(expr.evaluate(variables)).to.equal(3);
        });
    });
    // Test Partition 7: Edge Cases and Error Handling (beyond basic division by zero)
    describe('Edge Cases and Error Handling', () => {
        it('should handle exponentiation with negative exponent (fractional result)', () => {
            // 2 ^ -1 = 0.5
            const expr = new expression_1.BinaryOperationExpression('^', new expression_1.NumberExpression(2), new expression_1.NumberExpression(-1));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(0.5);
        });
        it('should handle exponentiation with fractional exponent (square root)', () => {
            // 9 ^ 0.5 = 3
            const expr = new expression_1.BinaryOperationExpression('^', new expression_1.NumberExpression(9), new expression_1.NumberExpression(0.5));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(3);
        });
        it('should handle zero exponent', () => {
            // 5 ^ 0 = 1
            const expr = new expression_1.BinaryOperationExpression('^', new expression_1.NumberExpression(5), new expression_1.NumberExpression(0));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(1);
        });
        it('should handle zero multiplied by anything', () => {
            const expr = new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(0), new expression_1.NumberExpression(100));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(0);
        });
        it('should handle zero divided by non-zero', () => {
            const expr = new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(0), new expression_1.NumberExpression(5));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(0);
        });
        it('should handle negative numbers in complex expressions', () => {
            // -5 * (3 - 8) + 10 / -2
            // -5 * (-5) + (-5)
            // 25 - 5 = 20
            const expr = new expression_1.BinaryOperationExpression('+', new expression_1.BinaryOperationExpression('*', new expression_1.UnaryOperationExpression('-', new expression_1.NumberExpression(5)), new expression_1.BinaryOperationExpression('-', new expression_1.NumberExpression(3), new expression_1.NumberExpression(8))), new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(10), new expression_1.NumberExpression(-2)));
            (0, chai_1.expect)(expr.evaluate({})).to.equal(20);
        });
    });
});
