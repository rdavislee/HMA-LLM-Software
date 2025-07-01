"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const chai_1 = require("chai");
const expression_1 = require("../src/expression"); // Import concrete classes
const utils_1 = require("../src/utils");
// Assign the actual evaluators from expressionUtils
const utilsInstance = new utils_1.ExpressionUtils();
const evaluator = utilsInstance;
const differentiator = utilsInstance;
const integrator = utilsInstance;
const simplifier = utilsInstance; // Add simplifier
// Helper function to create literal nodes using concrete classes
const num = (value) => new expression_1.NumberNode(value);
const variable = (name) => new expression_1.VariableNode(name);
// Helper for binary operations using concrete classes
const op = (left, operator, right) => new expression_1.BinaryOperationNode(operator, left, right);
// Helper for unary operations (e.g., negation) using concrete classes
const unaryOp = (operator, operand) => new expression_1.UnaryOperationNode(operator, operand);
// Helper for function calls using concrete classes
const func = (name, args) => new expression_1.FunctionCallNode(name, args);
// Add a helper for deep comparison of expression nodes after simplification
const expectSimplified = (input, expected) => {
    const simplified = simplifier.simplify(input);
    (0, chai_1.expect)(simplified).to.deep.equal(expected);
};
describe('ExpressionEvaluator', () => {
    // Test partitions:
    // - Basic arithmetic operations (addition, subtraction, multiplication, division, exponentiation)
    // - Order of operations (PEMDAS)
    // - Variables with different contexts
    // - Built-in functions (log, sin, cos, tan, etc.)
    // - Nested expressions
    // - Edge cases: division by zero, undefined variables
    describe('evaluate()', () => {
        it('should correctly evaluate basic addition', () => {
            const expr = op(num(5), 'add', num(3));
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(8);
        });
        it('should correctly evaluate basic subtraction', () => {
            const expr = op(num(10), 'subtract', num(4));
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(6);
        });
        it('should correctly evaluate basic multiplication', () => {
            const expr = op(num(6), 'multiply', num(7));
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(42);
        });
        it('should correctly evaluate basic division', () => {
            const expr = op(num(20), 'divide', num(5));
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(4);
        });
        it('should correctly evaluate basic exponentiation', () => {
            const expr = op(num(2), 'power', num(3));
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(8);
        });
        it('should handle negative numbers', () => {
            const expr = op(num(-5), 'add', num(3));
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(-2);
        });
        it('should respect PEMDAS order of operations (multiplication before addition)', () => {
            // 2 + 3 * 4 = 14
            const expr = op(num(2), 'add', op(num(3), 'multiply', num(4)));
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(14);
        });
        it('should respect PEMDAS order of operations (parentheses first)', () => {
            // (2 + 3) * 4 = 20
            const expr = op(op(num(2), 'add', num(3)), 'multiply', num(4));
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(20);
        });
        it('should evaluate expression with single variable', () => {
            const expr = op(variable('x'), 'add', num(5));
            (0, chai_1.expect)(evaluator.evaluate(expr, { x: 10 })).to.equal(15);
        });
        it('should evaluate expression with multiple variables', () => {
            // x * y + z
            const expr = op(op(variable('x'), 'multiply', variable('y')), 'add', variable('z'));
            (0, chai_1.expect)(evaluator.evaluate(expr, { x: 2, y: 3, z: 4 })).to.equal(10);
        });
        it('should throw error for undefined variable', () => {
            const expr = op(variable('x'), 'add', num(5));
            (0, chai_1.expect)(() => evaluator.evaluate(expr, { y: 10 })).to.throw('Undefined variable \'x\' in context.');
        });
        it('should correctly evaluate sin function', () => {
            const expr = func('sin', [num(Math.PI / 2)]);
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.be.closeTo(1, 1e-9);
        });
        it('should correctly evaluate cos function', () => {
            const expr = func('cos', [num(Math.PI)]);
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.be.closeTo(-1, 1e-9);
        });
        it('should correctly evaluate tan function', () => {
            const expr = func('tan', [num(Math.PI / 4)]);
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.be.closeTo(1, 1e-9);
        });
        it('should correctly evaluate natural logarithm (ln) function', () => {
            const expr = func('ln', [num(Math.E)]);
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.be.closeTo(1, 1e-9);
        });
        it('should correctly evaluate nested functions', () => {
            // sin(cos(0)) = sin(1)
            const expr = func('sin', [func('cos', [num(0)])]);
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.be.closeTo(Math.sin(1), 1e-9);
        });
        it('should handle unary negation', () => {
            const expr = unaryOp('negate', num(5)); // Represents -5
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(-5);
        });
        it('should handle unary negation within a binary expression', () => {
            // 10 + (-5)
            const expr = op(num(10), 'add', unaryOp('negate', num(5)));
            (0, chai_1.expect)(evaluator.evaluate(expr, {})).to.equal(5);
        });
        it('should throw error for division by zero', () => {
            const expr = op(num(10), 'divide', num(0));
            (0, chai_1.expect)(() => evaluator.evaluate(expr, {})).to.throw('Division by zero.');
        });
        it('should throw error for log of non-positive number', () => {
            const expr = func('ln', [num(0)]);
            (0, chai_1.expect)(() => evaluator.evaluate(expr, {})).to.throw('Logarithm of non-positive number.');
        });
        it('should handle complex nested expressions', () => {
            // 2 * sin(PI/6) + ln(e^2) - (4 - x)^2 where x = 1
            // 2 * 0.5 + 2 - (4 - 1)^2 = 1 + 2 - 3^2 = 3 - 9 = -6
            const expr = op(op(op(num(2), 'multiply', func('sin', [op(num(Math.PI), 'divide', num(6))])), 'add', func('ln', [op(num(Math.E), 'power', num(2))])), 'subtract', op(op(num(4), 'subtract', variable('x')), 'power', num(2)));
            (0, chai_1.expect)(evaluator.evaluate(expr, { x: 1 })).to.be.closeTo(-6, 1e-9);
        });
    });
});
describe('ExpressionDifferentiator', () => {
    // Test partitions:
    // - Constant rule: d/dx(C) = 0
    // - Power rule: d/dx(x^n) = nx^(n-1)
    // - Sum/Difference rule: d/dx(f(x) +/- g(x)) = f'(x) +/- g'(x)
    // - Product rule: d/dx(f(x)g(x)) = f'(x)g(x) + f(x)g'(x)
    // - Quotient rule: d/dx(f(x)/g(x)) = (f'(x)g(x) - f(x)g'(x)) / g(x)^2
    // - Chain rule: d/dx(f(g(x))) = f'(g(x)) * g'(x)
    // - Trigonometric functions: sin(x), cos(x), tan(x)
    // - Logarithmic functions: ln(x)
    // - Exponential functions: e^x, a^x
    // - Mixed expressions with multiple rules
    // - Differentiation with respect to a different variable (should treat as constant)
    // - Simplification of results (e.g., 1*x = x, 0*x = 0, x^0 = 1, x^1 = x, 0+x = x, x-0 = x, x-x=0, x*x=x^2, (A/B)*C, A/(A*B), (A*B)/A, (x^a)^b, -(-x)=x, x+x=2x, nX+mX=(n+m)X, etc.)
    describe('differentiate()', () => {
        it('should differentiate a constant to 0', () => {
            const expr = num(5);
            const expected = num(0);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should differentiate a variable to 1 with respect to itself', () => {
            const expr = variable('x');
            const expected = num(1);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should differentiate a variable to 0 with respect to a different variable', () => {
            const expr = variable('y');
            const expected = num(0);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply the power rule for x^n (d/dx(x^2) = 2x)', () => {
            const expr = op(variable('x'), 'power', num(2));
            const expected = op(num(2), 'multiply', variable('x')); // 2*x
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply the power rule for x^1 (d/dx(x) = 1)', () => {
            const expr = op(variable('x'), 'power', num(1));
            const expected = num(1);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply the power rule for x^0 (d/dx(1) = 0)', () => {
            const expr = op(variable('x'), 'power', num(0));
            const expected = num(0);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply sum rule: d/dx(x + 5) = 1 + 0 = 1', () => {
            const expr = op(variable('x'), 'add', num(5));
            const expected = num(1);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply difference rule: d/dx(x - 5) = 1 - 0 = 1', () => {
            const expr = op(variable('x'), 'subtract', num(5));
            const expected = num(1);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply product rule: d/dx(x * x) = 1*x + x*1 = 2x', () => {
            const expr = op(variable('x'), 'multiply', variable('x'));
            const expected = op(num(2), 'multiply', variable('x')); // 2x
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply product rule: d/dx(x * sin(x)) = sin(x) + x*cos(x)', () => {
            const expr = op(variable('x'), 'multiply', func('sin', [variable('x')]));
            const expected = op(func('sin', [variable('x')]), 'add', op(variable('x'), 'multiply', func('cos', [variable('x')])));
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply quotient rule: d/dx(x / x) = (1*x - x*1) / x^2 = 0', () => {
            const expr = op(variable('x'), 'divide', variable('x'));
            const expected = num(0);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should differentiate sin(x) to cos(x)', () => {
            const expr = func('sin', [variable('x')]);
            const expected = func('cos', [variable('x')]);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should differentiate cos(x) to -sin(x)', () => {
            const expr = func('cos', [variable('x')]);
            const expected = unaryOp('negate', func('sin', [variable('x')])); // -sin(x)
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should differentiate tan(x) to sec^2(x) (or 1/cos^2(x))', () => {
            const expr = func('tan', [variable('x')]);
            const expected = op(num(1), 'divide', op(func('cos', [variable('x')]), 'power', num(2)));
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should differentiate ln(x) to 1/x', () => {
            const expr = func('ln', [variable('x')]);
            const expected = op(num(1), 'divide', variable('x'));
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply chain rule: d/dx(sin(x^2)) = cos(x^2) * 2x', () => {
            const innerExpr = op(variable('x'), 'power', num(2));
            const expr = func('sin', [innerExpr]);
            const expected = op(func('cos', [innerExpr]), 'multiply', op(num(2), 'multiply', variable('x')) // 2x
            );
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply chain rule with log: d/dx(ln(2x)) = (1/(2x)) * 2 = 1/x', () => {
            const innerExpr = op(num(2), 'multiply', variable('x'));
            const expr = func('ln', [innerExpr]);
            const expected = op(num(1), 'divide', variable('x'));
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should handle complex expression: d/dx(x^2 + 3x - 5) = 2x + 3', () => {
            const expr = op(op(op(variable('x'), 'power', num(2)), 'add', op(num(3), 'multiply', variable('x'))), 'subtract', num(5));
            const expected = op(op(num(2), 'multiply', variable('x')), 'add', num(3));
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should handle differentiation of an expression with respect to a different variable', () => {
            // d/dy(x^2 + 3x - 5) = 0
            const expr = op(op(op(variable('x'), 'power', num(2)), 'add', op(num(3), 'multiply', variable('x'))), 'subtract', num(5));
            const expected = num(0);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'y')).to.deep.equal(expected);
        });
        // New tests to align with simplify function's behavior
        it('should differentiate Cx to C (d/dx(5x) = 5)', () => {
            const expr = op(num(5), 'multiply', variable('x'));
            const expected = num(5);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should differentiate x/C to 1/C (d/dx(x/5) = 1/5)', () => {
            const expr = op(variable('x'), 'divide', num(5));
            const expected = num(0.2);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should differentiate e^x to e^x', () => {
            const expr = new expression_1.ExponentialNode(variable('x'));
            const expected = new expression_1.ExponentialNode(variable('x'));
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should apply chain rule for exp(f(x)): d/dx(exp(x^2)) = exp(x^2) * 2x', () => {
            const innerExpr = op(variable('x'), 'power', num(2));
            const expr = new expression_1.ExponentialNode(innerExpr);
            const expected = op(new expression_1.ExponentialNode(innerExpr), 'multiply', op(num(2), 'multiply', variable('x')));
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should simplify -(-x) to x before differentiation: d/dx(-(-x)) = 1', () => {
            const expr = unaryOp('negate', unaryOp('negate', variable('x')));
            const expected = num(1);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
        it('should simplify x+x to 2x before differentiation: d/dx(x+x) = 2', () => {
            const expr = op(variable('x'), 'add', variable('x'));
            const expected = num(2);
            (0, chai_1.expect)(differentiator.differentiate(expr, 'x')).to.deep.equal(expected);
        });
    });
});
describe('ExpressionSimplifier', () => {
    // Test partitions:
    // - Constant folding (e.g., 2+3=5)
    // - Identity elements (x+0=x, x*1=x, x/1=x)
    // - Zero elements (x*0=0, 0/x=0)
    // - Power simplifications (x^0=1, x^1=x, (x^a)^b = x^(a*b))
    // - Negation simplifications (-(-x)=x, -1*x=-x)
    // - Combining like terms (x+x=2x, Cx+Dx=(C+D)x)
    // - Division simplifications (x/x=1, C*x/C=x, 1/(-1*x)=-1/x, (A*B)/A=B, A/(A*B)=1/B, C/(C*X)=1/X)
    // - Function argument simplifications (sin(x+0)=sin(x), ln(1)=0, exp(0)=1, ln(e)=1, exp(ln(x))=x)
    // - Nested expression simplification (combining multiple rules)
    describe('simplify()', () => {
        // --- Constant Folding ---
        it('should perform constant folding for addition', () => {
            const expr = op(num(2), 'add', num(3));
            const expected = num(5);
            expectSimplified(expr, expected);
        });
        it('should perform constant folding for subtraction', () => {
            const expr = op(num(10), 'subtract', num(4));
            const expected = num(6);
            expectSimplified(expr, expected);
        });
        it('should perform constant folding for multiplication', () => {
            const expr = op(num(6), 'multiply', num(7));
            const expected = num(42);
            expectSimplified(expr, expected);
        });
        it('should perform constant folding for division', () => {
            const expr = op(num(20), 'divide', num(5));
            const expected = num(4);
            expectSimplified(expr, expected);
        });
        it('should perform constant folding for exponentiation', () => {
            const expr = op(num(2), 'power', num(3));
            const expected = num(8);
            expectSimplified(expr, expected);
        });
        it('should handle division by zero during constant folding', () => {
            const expr = op(num(10), 'divide', num(0));
            const simplified = simplifier.simplify(expr);
            (0, chai_1.expect)(simplified).to.deep.equal(expr); // Simplifier returns original node for division by zero
            (0, chai_1.expect)(() => evaluator.evaluate(simplified, {})).to.throw('Division by zero.');
        });
        // --- Identity Elements ---
        it('should simplify x + 0 to x', () => {
            const expr = op(variable('x'), 'add', num(0));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        it('should simplify 0 + x to x', () => {
            const expr = op(num(0), 'add', variable('x'));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        it('should simplify x - 0 to x', () => {
            const expr = op(variable('x'), 'subtract', num(0));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        it('should simplify x * 1 to x', () => {
            const expr = op(variable('x'), 'multiply', num(1));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        it('should simplify 1 * x to x', () => {
            const expr = op(num(1), 'multiply', variable('x'));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        it('should simplify x / 1 to x', () => {
            const expr = op(variable('x'), 'divide', num(1));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        // --- Zero Elements ---
        it('should simplify x * 0 to 0', () => {
            const expr = op(variable('x'), 'multiply', num(0));
            const expected = num(0);
            expectSimplified(expr, expected);
        });
        it('should simplify 0 * x to 0', () => {
            const expr = op(num(0), 'multiply', variable('x'));
            const expected = num(0);
            expectSimplified(expr, expected);
        });
        it('should simplify 0 / x to 0 (for x != 0)', () => {
            const expr = op(num(0), 'divide', variable('x'));
            const expected = num(0);
            expectSimplified(expr, expected);
        });
        it('should simplify 0 - x to -x', () => {
            const expr = op(num(0), 'subtract', variable('x'));
            const expected = unaryOp('negate', variable('x'));
            expectSimplified(expr, expected);
        });
        // --- Power Simplifications ---
        it('should simplify x^0 to 1 (for x != 0)', () => {
            const expr = op(variable('x'), 'power', num(0));
            const expected = num(1);
            expectSimplified(expr, expected);
        });
        it('should simplify x^1 to x', () => {
            const expr = op(variable('x'), 'power', num(1));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        it('should simplify 0^x to 0 (for x > 0)', () => {
            const expr = op(num(0), 'power', variable('x'));
            const expected = num(0);
            expectSimplified(expr, expected);
        });
        it('should simplify 1^x to 1', () => {
            const expr = op(num(1), 'power', variable('x'));
            const expected = num(1);
            expectSimplified(expr, expected);
        });
        it('should simplify (x^a)^b to x^(a*b)', () => {
            const expr = op(op(variable('x'), 'power', num(2)), 'power', num(3)); // (x^2)^3
            const expected = op(variable('x'), 'power', num(6)); // x^6
            expectSimplified(expr, expected);
        });
        // --- Negation Simplifications ---
        it('should simplify -(-x) to x', () => {
            const expr = unaryOp('negate', unaryOp('negate', variable('x')));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        it('should simplify -1 * x to -x', () => {
            const expr = op(num(-1), 'multiply', variable('x'));
            const expected = unaryOp('negate', variable('x'));
            expectSimplified(expr, expected);
        });
        it('should simplify x * -1 to -x', () => {
            const expr = op(variable('x'), 'multiply', num(-1));
            const expected = unaryOp('negate', variable('x'));
            expectSimplified(expr, expected);
        });
        // --- Combining Like Terms (Addition/Subtraction) ---
        it('should simplify x + x to 2x', () => {
            const expr = op(variable('x'), 'add', variable('x'));
            const expected = op(num(2), 'multiply', variable('x'));
            expectSimplified(expr, expected);
        });
        it('should simplify 2x + 3x to 5x', () => {
            const expr = op(op(num(2), 'multiply', variable('x')), 'add', op(num(3), 'multiply', variable('x')));
            const expected = op(num(5), 'multiply', variable('x'));
            expectSimplified(expr, expected);
        });
        it('should simplify x - x to 0', () => {
            const expr = op(variable('x'), 'subtract', variable('x'));
            const expected = num(0);
            expectSimplified(expr, expected);
        });
        it('should simplify 5x - 2x to 3x', () => {
            const expr = op(op(num(5), 'multiply', variable('x')), 'subtract', op(num(2), 'multiply', variable('x')));
            const expected = op(num(3), 'multiply', variable('x'));
            expectSimplified(expr, expected);
        });
        // --- Combining Like Terms (Multiplication/Division) ---
        it('should simplify x * x to x^2', () => {
            const expr = op(variable('x'), 'multiply', variable('x'));
            const expected = op(variable('x'), 'power', num(2));
            expectSimplified(expr, expected);
        });
        it('should simplify x * x^2 to x^3', () => {
            const expr = op(variable('x'), 'multiply', op(variable('x'), 'power', num(2)));
            const expected = op(variable('x'), 'power', num(3));
            expectSimplified(expr, expected);
        });
        it('should simplify C*x / C to x', () => {
            const expr = op(op(num(5), 'multiply', variable('x')), 'divide', num(5));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        it('should simplify x / x to 1', () => {
            const expr = op(variable('x'), 'divide', variable('x'));
            const expected = num(1);
            expectSimplified(expr, expected);
        });
        // --- Fraction Simplification ---
        it('should simplify 1 / (-1 * x) to -1 / x', () => {
            const expr = op(num(1), 'divide', op(num(-1), 'multiply', variable('x')));
            const expected = op(unaryOp('negate', num(1)), 'divide', variable('x')); // -1/x
            expectSimplified(expr, expected);
        });
        it('should simplify (A*B)/A to B', () => {
            const expr = op(op(variable('a'), 'multiply', variable('b')), 'divide', variable('a'));
            const expected = variable('b');
            expectSimplified(expr, expected);
        });
        it('should simplify A/(A*B) to 1/B', () => {
            const expr = op(variable('a'), 'divide', op(variable('a'), 'multiply', variable('b')));
            const expected = op(num(1), 'divide', variable('b'));
            expectSimplified(expr, expected);
        });
        it('should simplify C / (C*X) to 1/X', () => {
            const expr = op(num(5), 'divide', op(num(5), 'multiply', variable('x')));
            const expected = op(num(1), 'divide', variable('x'));
            expectSimplified(expr, expected);
        });
        // --- Function Argument Simplifications ---
        it('should simplify sin(x+0) to sin(x)', () => {
            const expr = func('sin', [op(variable('x'), 'add', num(0))]);
            const expected = func('sin', [variable('x')]);
            expectSimplified(expr, expected);
        });
        it('should simplify ln(1) to 0', () => {
            const expr = func('ln', [num(1)]);
            const expected = num(0);
            expectSimplified(expr, expected);
        });
        it('should simplify exp(0) to 1', () => {
            const expr = func('exp', [num(0)]);
            const expected = num(1);
            expectSimplified(expr, expected);
        });
        it('should simplify ln(e) to 1', () => {
            const expr = func('ln', [new expression_1.ConstantNode('e')]);
            const expected = num(1);
            expectSimplified(expr, expected);
        });
        it('should simplify exp(ln(x)) to x', () => {
            const expr = func('exp', [func('ln', [variable('x')])]);
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        // --- Nested and Complex Simplifications ---
        it('should apply multiple simplifications in a nested expression: (x+0)*1^1 - (y-y)', () => {
            // (x+0) -> x
            // 1^1 -> 1
            // x*1 -> x
            // y-y -> 0
            // x - 0 -> x
            const expr = op(op(op(variable('x'), 'add', num(0)), 'multiply', op(num(1), 'power', num(1))), 'subtract', op(variable('y'), 'subtract', variable('y')));
            const expected = variable('x');
            expectSimplified(expr, expected);
        });
        it('should simplify a constant multiplied by a simplified expression', () => {
            // 2 * (x + 0) -> 2 * x
            const expr = op(num(2), 'multiply', op(variable('x'), 'add', num(0)));
            const expected = op(num(2), 'multiply', variable('x'));
            expectSimplified(expr, expected);
        });
        it('should simplify a complex sum with like terms and constants', () => {
            // 2x + 3 + 5x - 1 + x = 8x + 2
            const term_2x_plus_3 = op(op(num(2), 'multiply', variable('x')), 'add', num(3));
            const term_5x_minus_1 = op(op(num(5), 'multiply', variable('x')), 'subtract', num(1));
            const sum_of_first_two_terms = op(term_2x_plus_3, 'add', term_5x_minus_1);
            const expr = op(sum_of_first_two_terms, 'add', variable('x'));
            const expected = op(op(num(8), 'multiply', variable('x')), 'add', num(2));
            expectSimplified(expr, expected);
        });
        it('should simplify nested multiplications with constants: 2 * (3 * x) to 6x', () => {
            const expr = op(num(2), 'multiply', op(num(3), 'multiply', variable('x')));
            const expected = op(num(6), 'multiply', variable('x'));
            expectSimplified(expr, expected);
        });
        it('should simplify nested divisions with constants: 10 / (2 / x) to 5x', () => {
            // 10 / (2/x) = 10 * x / 2 = 5x
            const expr = op(num(10), 'divide', op(num(2), 'divide', variable('x')));
            const expected = op(num(5), 'multiply', variable('x'));
            expectSimplified(expr, expected);
        });
        it('should simplify nested divisions with constants: (10 / 2) / x to 5/x', () => {
            // (10 / 2) / x = 5 / x
            const expr = op(op(num(10), 'divide', num(2)), 'divide', variable('x'));
            const expected = op(num(5), 'divide', variable('x'));
            expectSimplified(expr, expected);
        });
        it('should simplify expressions involving PI and E constants', () => {
            // PI * 2 * E + 0 = 2*PI*E
            const expr = op(op(op(new expression_1.ConstantNode('pi'), 'multiply', num(2)), 'multiply', new expression_1.ConstantNode('e')), 'add', num(0));
            const expected = op(op(num(2), 'multiply', new expression_1.ConstantNode('pi')), 'multiply', new expression_1.ConstantNode('e'));
            expectSimplified(expr, expected);
        });
        it('should simplify 0^0 if it throws (or is handled as NaN/undefined)', () => {
            const expr = op(num(0), 'power', num(0));
            // Depending on implementation, this might throw or result in a specific NaN/undefined behavior.
            // If the simplify function relies on evaluate for constant folding, evaluate should throw.
            (0, chai_1.expect)(() => simplifier.simplify(expr)).to.throw('0^0 is undefined.');
        });
        it('should simplify complex expression (x + 2*x + 3) * (y - y + 1) / 1^z', () => {
            // (x + 2*x + 3) = 3x + 3
            // (y - y + 1) = 1
            // (3x + 3) * 1 = 3x + 3
            // 1^z = 1
            // (3x + 3) / 1 = 3x + 3
            const innerTerm1 = op(variable('x'), 'add', op(num(2), 'multiply', variable('x')));
            const term_3x_plus_3 = op(innerTerm1, 'add', num(3));
            const innerTerm2 = op(variable('y'), 'subtract', variable('y'));
            const term_y_minus_y_plus_1 = op(innerTerm2, 'add', num(1));
            const product_expr = op(term_3x_plus_3, 'multiply', term_y_minus_y_plus_1);
            const power_1_z = op(num(1), 'power', variable('z'));
            const expr = op(product_expr, 'divide', power_1_z);
            const expected = op(op(num(3), 'multiply', variable('x')), 'add', num(3));
            expectSimplified(expr, expected);
        });
    });
});
describe('ExpressionIntegrator', () => {
    // Helper to check indefinite integration results
    const checkIndefiniteResult = (expr, variable, expectedIntegratedExpr, expectedUnintegratable, expectedConstant) => {
        const result = integrator.integrateIndefinite(expr, variable);
        (0, chai_1.expect)(result.unintegratable).to.equal(expectedUnintegratable);
        (0, chai_1.expect)(result.constantOfIntegration).to.equal(expectedConstant);
        if (expectedUnintegratable) {
            (0, chai_1.expect)(result.integratedExpression).to.equal("UNINTEGRATABLE_EXPRESSION");
        }
        else {
            // Need to compare ASTs for integrated expression
            (0, chai_1.expect)(result.integratedExpression).to.deep.equal(expectedIntegratedExpr);
        }
    };
    describe('integrateIndefinite()', () => {
        // Test partitions:
        // - Constant rule: C -> Cx
        // - Power rule: x^n -> x^(n+1)/(n+1) (including x^-1 -> ln(x))
        // - Sum/Difference rule: (f +/- g) -> integral(f) +/- integral(g)
        // - Constant multiple rule: C*f(x) -> C*integral(f(x))
        // - Trigonometric functions: sin(x), cos(x)
        // - Exponential functions: e^x, a^x
        // - Logarithmic functions: ln(x)
        // - Unary negation: -f(x) -> -integral(f(x))
        // - Unintegratable by simple rules: tan(x), arcsin(x), products, quotients, chain rule (u-sub) cases
        it('should integrate a constant to constant*variable + C', () => {
            // ∫ 5 dx = 5x + C
            const expr = num(5);
            const expected = op(op(num(5), 'multiply', variable('x')), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should integrate a constant with respect to a different variable', () => {
            // ∫ 5 dy = 5y + C
            const expr = num(5);
            const expected = op(op(num(5), 'multiply', variable('y')), 'add', variable('C'));
            checkIndefiniteResult(expr, 'y', expected, false, 'C');
        });
        it('should integrate variable x to x^2/2 + C', () => {
            // ∫ x dx = x^2/2 + C
            const expr = variable('x');
            const expected = op(op(variable('x'), 'power', num(2)), 'divide', num(2));
            const expectedWithC = op(expected, 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expectedWithC, false, 'C');
        });
        it('should integrate variable y to y^2/2 + C', () => {
            // ∫ y dy = y^2/2 + C
            const expr = variable('y');
            const expected = op(op(variable('y'), 'power', num(2)), 'divide', num(2));
            const expectedWithC = op(expected, 'add', variable('C'));
            checkIndefiniteResult(expr, 'y', expectedWithC, false, 'C');
        });
        it('should treat other variables as constants: ∫ y dx = yx + C', () => {
            const expr = variable('y');
            const expected = op(op(variable('y'), 'multiply', variable('x')), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should apply power rule: ∫ x^2 dx = x^3/3 + C', () => {
            const expr = op(variable('x'), 'power', num(2));
            const expected = op(op(variable('x'), 'power', num(3)), 'divide', num(3));
            const expectedWithC = op(expected, 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expectedWithC, false, 'C');
        });
        it('should apply power rule for negative exponent: ∫ x^-2 dx = x^-1/-1 + C = -1/x + C', () => {
            const expr = op(variable('x'), 'power', num(-2));
            const expected = op(unaryOp('negate', op(num(1), 'divide', variable('x'))), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should handle integral of 1/x (x^-1) as ln(x) + C', () => {
            const expr = op(variable('x'), 'power', num(-1));
            const expected = op(func('ln', [variable('x')]), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should apply sum rule: ∫ (x + 5) dx = x^2/2 + 5x + C', () => {
            const expr = op(variable('x'), 'add', num(5));
            const expectedTerm1 = op(op(variable('x'), 'power', num(2)), 'divide', num(2));
            const expectedTerm2 = op(num(5), 'multiply', variable('x'));
            const expected = op(op(expectedTerm1, 'add', expectedTerm2), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should apply difference rule: ∫ (x^2 - x) dx = x^3/3 - x^2/2 + C', () => {
            const expr = op(op(variable('x'), 'power', num(2)), 'subtract', variable('x'));
            const expectedTerm1 = op(op(variable('x'), 'power', num(3)), 'divide', num(3));
            const expectedTerm2 = op(op(variable('x'), 'power', num(2)), 'divide', num(2));
            const expected = op(op(expectedTerm1, 'subtract', expectedTerm2), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should apply constant multiple rule: ∫ 2x dx = x^2 + C', () => {
            const expr = op(num(2), 'multiply', variable('x'));
            const expected = op(op(variable('x'), 'power', num(2)), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should integrate sin(x) to -cos(x) + C', () => {
            const expr = func('sin', [variable('x')]);
            const expected = op(unaryOp('negate', func('cos', [variable('x')])), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should integrate cos(x) to sin(x) + C', () => {
            const expr = func('cos', [variable('x')]);
            const expected = op(func('sin', [variable('x')]), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should integrate exp(x) to exp(x) + C', () => {
            const expr = new expression_1.ExponentialNode(variable('x'));
            const expected = op(new expression_1.ExponentialNode(variable('x')), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should integrate ln(x) to xln(x) - x + C', () => {
            const expr = func('ln', [variable('x')]);
            const expected = op(op(op(variable('x'), 'multiply', func('ln', [variable('x')])), 'subtract', variable('x')), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should integrate a^x (e.g. 2^x) to a^x/ln(a) + C', () => {
            const expr = op(num(2), 'power', variable('x'));
            const expected = op(op(num(2), 'power', variable('x')), 'divide', func('ln', [num(2)]));
            const expectedWithC = op(expected, 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expectedWithC, false, 'C');
        });
        it('should apply unary negation: ∫ -x dx = -x^2/2 + C', () => {
            const expr = unaryOp('negate', variable('x'));
            const expected = op(unaryOp('negate', op(op(variable('x'), 'power', num(2)), 'divide', num(2))), 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expected, false, 'C');
        });
        it('should handle complex integrable expression: ∫ (3x^2 + sin(x) - 4e^x) dx = x^3 - cos(x) - 4e^x + C', () => {
            // (3x^2 + sin(x) - 4e^x)
            const expr = op(op(op(num(3), 'multiply', op(variable('x'), 'power', num(2))), 'add', func('sin', [variable('x')])), 'subtract', op(num(4), 'multiply', new expression_1.ExponentialNode(variable('x'))));
            // x^3 - cos(x) - 4e^x
            const expectedIntegrated = op(op(op(variable('x'), 'power', num(3)), 'subtract', func('cos', [variable('x')])), 'subtract', op(num(4), 'multiply', new expression_1.ExponentialNode(variable('x'))));
            const expectedWithC = op(expectedIntegrated, 'add', variable('C'));
            checkIndefiniteResult(expr, 'x', expectedWithC, false, 'C');
        });
        // Unintegratable cases
        it('should mark tan(x) as unintegratable', () => {
            const expr = func('tan', [variable('x')]);
            checkIndefiniteResult(expr, 'x', "UNINTEGRATABLE_EXPRESSION", true, null);
        });
        it('should mark arcsin(x) as unintegratable', () => {
            const expr = func('arcsin', [variable('x')]);
            checkIndefiniteResult(expr, 'x', "UNINTEGRATABLE_EXPRESSION", true, null);
        });
        it('should mark product x*sin(x) as unintegratable (requires integration by parts)', () => {
            const expr = op(variable('x'), 'multiply', func('sin', [variable('x')]));
            checkIndefiniteResult(expr, 'x', "UNINTEGRATABLE_EXPRESSION", true, null);
        });
        it('should mark complex quotient x/(x+1) as unintegratable', () => {
            const expr = op(variable('x'), 'divide', op(variable('x'), 'add', num(1)));
            checkIndefiniteResult(expr, 'x', "UNINTEGRATABLE_EXPRESSION", true, null);
        });
        it('should mark function with complex argument (e.g., sin(2x)) as unintegratable (requires u-sub)', () => {
            const expr = func('sin', [op(num(2), 'multiply', variable('x'))]);
            checkIndefiniteResult(expr, 'x', "UNINTEGRATABLE_EXPRESSION", true, null);
        });
        it('should mark complex power rule like x^y as unintegratable', () => {
            const expr = op(variable('x'), 'power', variable('y'));
            checkIndefiniteResult(expr, 'x', "UNINTEGRATABLE_EXPRESSION", true, null);
        });
    });
    describe('integrateDefinite()', () => {
        // Test partitions:
        // - Various functions (polynomials, trig, exp, log)
        // - Different bounds (positive, negative, zero, inverted)
        // - Accuracy checks (using closeTo)
        // - numRectangles scaling (indirectly via accuracy for different interval sizes)
        // - Error cases (singularities, domain errors)
        // - Handling of other variables (treated as 0 by current implementation)
        const tolerance = 1e-7; // Use a reasonable tolerance for numerical integration
        it('should integrate constant function from 0 to 5: ∫ 5 dx = 25', () => {
            const expr = num(5);
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, 5, {})).to.be.closeTo(25, tolerance);
        });
        it('should integrate x from 0 to 1: ∫ x dx = 0.5', () => {
            const expr = variable('x');
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, 1, {})).to.be.closeTo(0.5, tolerance);
        });
        it('should integrate x^2 from 0 to 1: ∫ x^2 dx = 1/3', () => {
            const expr = op(variable('x'), 'power', num(2));
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, 1, {})).to.be.closeTo(1 / 3, tolerance);
        });
        it('should integrate 2x + 3 from 0 to 2: ∫ (2x + 3) dx = 10', () => {
            const expr = op(op(num(2), 'multiply', variable('x')), 'add', num(3));
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, 2, {})).to.be.closeTo(10, tolerance);
        });
        it('should integrate x^3 - 4x + 1 from -1 to 2: ∫ (x^3 - 4x + 1) dx = 0.75', () => {
            const expr = op(op(op(variable('x'), 'power', num(3)), 'subtract', op(num(4), 'multiply', variable('x'))), 'add', num(1));
            // Definite integral: [x^4/4 - 2x^2 + x] from -1 to 2
            // F(2) = 16/4 - 2*4 + 2 = 4 - 8 + 2 = -2
            // F(-1) = 1/4 - 2*1 - 1 = 1/4 - 3 = -11/4 = -2.75
            // F(2) - F(-1) = -2 - (-2.75) = 0.75
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', -1, 2, {})).to.be.closeTo(0.75, tolerance);
        });
        it('should integrate sin(x) from 0 to PI: ∫ sin(x) dx = 2', () => {
            const expr = func('sin', [variable('x')]);
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, Math.PI, {})).to.be.closeTo(2, tolerance);
        });
        it('should integrate cos(x) from 0 to PI/2: ∫ cos(x) dx = 1', () => {
            const expr = func('cos', [variable('x')]);
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, Math.PI / 2, {})).to.be.closeTo(1, tolerance);
        });
        it('should integrate exp(x) from 0 to 1: ∫ e^x dx = e - 1', () => {
            const expr = new expression_1.ExponentialNode(variable('x'));
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, 1, {})).to.be.closeTo(Math.E - 1, tolerance);
        });
        it('should integrate 1/x from 1 to e: ∫ 1/x dx = 1', () => {
            const expr = op(num(1), 'divide', variable('x'));
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 1, Math.E, {})).to.be.closeTo(1, tolerance);
        });
        it('should return 0 when lower and upper bounds are the same', () => {
            const expr = variable('x');
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 5, 5, {})).to.equal(0);
        });
        it('should handle inverted bounds: ∫ x dx from 5 to 1 = -∫ x dx from 1 to 5 = -12', () => {
            const expr = variable('x');
            // ∫ x dx from 1 to 5 = [x^2/2] from 1 to 5 = 25/2 - 1/2 = 24/2 = 12
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 5, 1, {})).to.be.closeTo(-12, tolerance);
        });
        it('should integrate x^2 from -1 to 1: ∫ x^2 dx = 2/3', () => {
            const expr = op(variable('x'), 'power', num(2));
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', -1, 1, {})).to.be.closeTo(2 / 3, tolerance);
        });
        // Test for numRectangles scaling indirectly by checking accuracy.
        // For a larger interval, the number of rectangles increases, leading to potentially better accuracy
        // or at least consistent accuracy for a given tolerance.
        it('should maintain accuracy for larger intervals (implicit numRectangles scaling)', () => {
            // ∫ x dx from 0 to 10 = [x^2/2] from 0 to 10 = 100/2 = 50
            const expr = variable('x');
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, 10, {})).to.be.closeTo(50, tolerance);
        });
        it('should throw error for singularity within bounds (1/x from -1 to 1)', () => {
            const expr = op(num(1), 'divide', variable('x'));
            (0, chai_1.expect)(() => integrator.integrateDefinite(expr, 'x', -1, 1, {})).to.throw('Division by zero.');
        });
        it('should throw error for domain violation within bounds (ln(x) from -1 to 1)', () => {
            const expr = func('ln', [variable('x')]);
            (0, chai_1.expect)(() => integrator.integrateDefinite(expr, 'x', -1, 1, {})).to.throw('Logarithm of non-positive number.');
        });
        it('should handle pi and e as constants in definite integral', () => {
            // ∫ (pi * x + e) dx from 0 to 1 = [pi*x^2/2 + e*x] from 0 to 1 = pi/2 + e
            const expr = op(op(new expression_1.ConstantNode('pi'), 'multiply', variable('x')), 'add', new expression_1.ConstantNode('e'));
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, 1, {})).to.be.closeTo(Math.PI / 2 + Math.E, tolerance);
        });
        it('should handle expressions with variables other than integration variable (treated as 0 by current implementation)', () => {
            // ∫ (ax + b) dx from 0 to 1 with respect to x.
            // Current integrateDefinite implementation treats 'a' and 'b' as 0 if not the integration variable.
            // So, ∫ (0*x + 0) dx = 0.
            const expr = op(op(variable('a'), 'multiply', variable('x')), 'add', variable('b'));
            (0, chai_1.expect)(integrator.integrateDefinite(expr, 'x', 0, 1, {})).to.be.closeTo(0, tolerance);
        });
    });
});
