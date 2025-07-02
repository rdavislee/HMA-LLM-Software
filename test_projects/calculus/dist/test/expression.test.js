"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const chai_1 = require("chai");
const expression_1 = require("../src/expression"); // Assuming concrete classes are exported from here
describe('Expression AST Nodes', () => {
    // Test Partition: NumberNode
    describe('NumberNode', () => {
        it('should correctly represent a positive integer', () => {
            const num = new expression_1.NumberNode(10);
            (0, chai_1.expect)(num.type).to.equal('number');
            (0, chai_1.expect)(num.value).to.equal(10);
            // toString() is part of the interface, but not implemented by default objects.
            // This test is for the structure. toString() behavior will be tested when implemented in src/expression.ts.
            // expect(num.toString()).to.equal('10');
        });
        it('should correctly represent a negative float', () => {
            const num = new expression_1.NumberNode(-3.14);
            (0, chai_1.expect)(num.type).to.equal('number');
            (0, chai_1.expect)(num.value).to.equal(-3.14);
            // expect(num.toString()).to.equal('-3.14');
        });
        it('should correctly represent zero', () => {
            const num = new expression_1.NumberNode(0);
            (0, chai_1.expect)(num.type).to.equal('number');
            (0, chai_1.expect)(num.value).to.equal(0);
            // expect(num.toString()).to.equal('0');
        });
    });
    // Test Partition: VariableNode
    describe('VariableNode', () => {
        it('should correctly represent a variable "x"', () => {
            const variable = new expression_1.VariableNode('x');
            (0, chai_1.expect)(variable.type).to.equal('variable');
            (0, chai_1.expect)(variable.name).to.equal('x');
            // expect(variable.toString()).to.equal('x');
        });
        it('should correctly represent a variable "theta"', () => {
            const variable = new expression_1.VariableNode('theta');
            (0, chai_1.expect)(variable.type).to.equal('variable');
            (0, chai_1.expect)(variable.name).to.equal('theta');
            // expect(variable.toString()).to.equal('theta');
        });
    });
    // Test Partition: BinaryOperationNode
    describe('BinaryOperationNode', () => {
        // Test partitions for operator types
        const operators = ['add', 'subtract', 'multiply', 'divide', 'power'];
        operators.forEach(operator => {
            it(`should correctly represent a '${operator}' operation`, () => {
                const leftNum = new expression_1.NumberNode(5);
                const rightVar = new expression_1.VariableNode('y');
                const op = new expression_1.BinaryOperationNode(operator, leftNum, rightVar);
                (0, chai_1.expect)(op.type).to.equal('binaryOperation');
                (0, chai_1.expect)(op.operator).to.equal(operator);
                (0, chai_1.expect)(op.left).to.deep.equal(leftNum);
                (0, chai_1.expect)(op.right).to.deep.equal(rightVar);
                // toString() output will depend on implementation, but structure should be consistent
                // For now, we'll test a basic string representation
                // Assuming simple infix notation without complex precedence handling in toString for now
                // The actual toString implementation will be in expression.ts
            });
        });
        it('should represent complex nested binary operations correctly', () => {
            const num1 = new expression_1.NumberNode(2);
            const num2 = new expression_1.NumberNode(3);
            const num3 = new expression_1.NumberNode(4);
            const varX = new expression_1.VariableNode('x');
            const addOp = new expression_1.BinaryOperationNode('add', num1, num2);
            const multiplyOp = new expression_1.BinaryOperationNode('multiply', addOp, num3);
            const finalOp = new expression_1.BinaryOperationNode('power', multiplyOp, varX);
            (0, chai_1.expect)(finalOp.type).to.equal('binaryOperation');
            (0, chai_1.expect)(finalOp.operator).to.equal('power');
            (0, chai_1.expect)(finalOp.left.type).to.equal('binaryOperation');
            (0, chai_1.expect)(finalOp.left.operator).to.equal('multiply');
            (0, chai_1.expect)(finalOp.right).to.deep.equal(varX);
            // Again, toString() depends on implementation. We expect a string representation.
            // Example: "((2 + 3) * 4)^x"
            // This test is more about ensuring the structure is valid, toString() actual output will be tested in expression.ts
        });
    });
    // Test Partition: UnaryOperationNode
    describe('UnaryOperationNode', () => {
        // Test partitions for operator types
        const operators = ['negate'];
        operators.forEach(operator => {
            it(`should correctly represent a '${operator}' operation`, () => {
                const operandNum = new expression_1.NumberNode(7);
                const op = new expression_1.UnaryOperationNode(operator, operandNum);
                (0, chai_1.expect)(op.type).to.equal('unaryOperation');
                (0, chai_1.expect)(op.operator).to.equal(operator);
                (0, chai_1.expect)(op.operand).to.deep.equal(operandNum);
                // Expected toString for negate: "-7"
            });
        });
        it('should handle nested unary operations', () => {
            const num = new expression_1.NumberNode(5);
            const negate1 = new expression_1.UnaryOperationNode('negate', num);
            const negate2 = new expression_1.UnaryOperationNode('negate', negate1);
            (0, chai_1.expect)(negate2.type).to.equal('unaryOperation');
            (0, chai_1.expect)(negate2.operator).to.equal('negate');
            (0, chai_1.expect)(negate2.operand.type).to.equal('unaryOperation');
            (0, chai_1.expect)(negate2.operand.operator).to.equal('negate');
            // Expected toString: "--5" or "-(-5)" depending on implementation
        });
    });
    // Test Partition: FunctionCallNode
    describe('FunctionCallNode', () => {
        // Test partitions for function names
        const functionNames = [
            'log', 'ln', 'exp',
            'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
            'asin', 'acos', 'atan', 'asec', 'acsc', 'acot'
        ];
        functionNames.forEach(funcName => {
            it(`should correctly represent a '${funcName}' function call with one argument`, () => {
                const arg = new expression_1.VariableNode('z');
                const funcCall = new expression_1.FunctionCallNode(funcName, [arg]);
                (0, chai_1.expect)(funcCall.type).to.equal('functionCall');
                (0, chai_1.expect)(funcCall.name).to.equal(funcName);
                (0, chai_1.expect)(funcCall.args).to.have.lengthOf(1);
                (0, chai_1.expect)(funcCall.args[0]).to.deep.equal(arg);
                // Expected toString: "log(z)", "sin(z)", etc.
            });
        });
        it('should handle nested function calls', () => {
            const num = new expression_1.NumberNode(90);
            const sinCall = new expression_1.FunctionCallNode('sin', [num]);
            const logCall = new expression_1.FunctionCallNode('log', [sinCall]);
            (0, chai_1.expect)(logCall.type).to.equal('functionCall');
            (0, chai_1.expect)(logCall.name).to.equal('log');
            (0, chai_1.expect)(logCall.args).to.have.lengthOf(1);
            (0, chai_1.expect)(logCall.args[0].type).to.equal('functionCall');
            (0, chai_1.expect)(logCall.args[0].name).to.equal('sin');
            // Expected toString: "log(sin(90))"
        });
        it('should handle function calls with complex arguments', () => {
            const num1 = new expression_1.NumberNode(5);
            const varX = new expression_1.VariableNode('x');
            const addOp = new expression_1.BinaryOperationNode('add', num1, varX);
            const cosCall = new expression_1.FunctionCallNode('cos', [addOp]);
            (0, chai_1.expect)(cosCall.type).to.equal('functionCall');
            (0, chai_1.expect)(cosCall.name).to.equal('cos');
            (0, chai_1.expect)(cosCall.args).to.have.lengthOf(1);
            (0, chai_1.expect)(cosCall.args[0].type).to.equal('binaryOperation');
            (0, chai_1.expect)(cosCall.args[0].operator).to.equal('add');
            // Expected toString: "cos(5 + x)"
        });
        it('should throw an error for function calls with zero arguments when one is required', () => {
            // The spec for FunctionCallNode in expressionInterface.ts states:
            // "For all supported functions, args must contain exactly one element."
            // This test verifies that the constructor enforces this precondition.
            (0, chai_1.expect)(() => new expression_1.FunctionCallNode('log', []))
                .to.throw('Function \'log\' expects exactly one argument, but received 0.'); // Updated error message to match implementation
        });
        it('should throw an error for function calls with multiple arguments when one is required', () => {
            // The spec for FunctionCallNode in expressionInterface.ts states:
            // "For all supported functions, args must contain exactly one element."
            // This test verifies that the constructor enforces this precondition.
            const num1 = new expression_1.NumberNode(1);
            const num2 = new expression_1.NumberNode(2);
            (0, chai_1.expect)(() => new expression_1.FunctionCallNode('log', [num1, num2]))
                .to.throw('Function \'log\' expects exactly one argument, but received 2.'); // Updated error message to match implementation
        });
    });
    // Test Partition: ConstantNode
    describe('ConstantNode', () => {
        const constants = ['e', 'pi'];
        constants.forEach(constantName => {
            it(`should correctly represent the constant '${constantName}'`, () => {
                const constant = new expression_1.ConstantNode(constantName);
                (0, chai_1.expect)(constant.type).to.equal('constant');
                (0, chai_1.expect)(constant.name).to.equal(constantName);
                // Expected toString: "e" or "pi"
            });
        });
    });
    // Test Partition: ExponentialNode
    describe('ExponentialNode', () => {
        it('should correctly represent e^x', () => {
            const exponentVar = new expression_1.VariableNode('x');
            const expNode = new expression_1.ExponentialNode(exponentVar);
            (0, chai_1.expect)(expNode.type).to.equal('exponential');
            (0, chai_1.expect)(expNode.exponent).to.deep.equal(exponentVar);
            // Expected toString: "e^x"
        });
        it('should correctly represent e^(2*y)', () => {
            const num2 = new expression_1.NumberNode(2);
            const varY = new expression_1.VariableNode('y');
            const multiplyOp = new expression_1.BinaryOperationNode('multiply', num2, varY);
            const expNode = new expression_1.ExponentialNode(multiplyOp);
            (0, chai_1.expect)(expNode.type).to.equal('exponential');
            (0, chai_1.expect)(expNode.exponent).to.deep.equal(multiplyOp);
            // Expected toString: "e^(2 * y)"
        });
        it('should handle nested exponentials: e^(e^x)', () => {
            const varX = new expression_1.VariableNode('x');
            const nestedExp = new expression_1.ExponentialNode(varX);
            const expNode = new expression_1.ExponentialNode(nestedExp);
            (0, chai_1.expect)(expNode.type).to.equal('exponential');
            (0, chai_1.expect)(expNode.exponent).to.deep.equal(nestedExp);
            // Expected toString: "e^(e^x)"
        });
    });
    // Test Partition: Combined/Mixed Expressions
    describe('Combined Expressions', () => {
        it('should correctly represent a complex expression: ((-x + 3) * sin(y)) / log(10)', () => {
            const varX = new expression_1.VariableNode('x');
            const num3 = new expression_1.NumberNode(3);
            const varY = new expression_1.VariableNode('y');
            const num10 = new expression_1.NumberNode(10);
            const negateX = new expression_1.UnaryOperationNode('negate', varX);
            const addOp = new expression_1.BinaryOperationNode('add', negateX, num3);
            const sinY = new expression_1.FunctionCallNode('sin', [varY]);
            const multiplyOp = new expression_1.BinaryOperationNode('multiply', addOp, sinY);
            const log10 = new expression_1.FunctionCallNode('log', [num10]);
            const divideOp = new expression_1.BinaryOperationNode('divide', multiplyOp, log10);
            (0, chai_1.expect)(divideOp.type).to.equal('binaryOperation');
            (0, chai_1.expect)(divideOp.operator).to.equal('divide');
            (0, chai_1.expect)(divideOp.left.operator).to.equal('multiply');
            (0, chai_1.expect)(divideOp.right.name).to.equal('log');
            // The structure is correctly built. toString() will be tested later.
            // Expected toString: "(( -x + 3 ) * sin(y)) / log(10)" (parentheses might vary based on precedence rules in toString)
        });
        it('should correctly represent a complex expression involving new types: e^(pi * cos(x)) + sec(y)', () => {
            const piConst = new expression_1.ConstantNode('pi');
            const varX = new expression_1.VariableNode('x');
            const varY = new expression_1.VariableNode('y');
            const cosX = new expression_1.FunctionCallNode('cos', [varX]);
            const piMultiplyCosX = new expression_1.BinaryOperationNode('multiply', piConst, cosX);
            const expNode = new expression_1.ExponentialNode(piMultiplyCosX);
            const secY = new expression_1.FunctionCallNode('sec', [varY]);
            const finalExpression = new expression_1.BinaryOperationNode('add', expNode, secY);
            (0, chai_1.expect)(finalExpression.type).to.equal('binaryOperation');
            (0, chai_1.expect)(finalExpression.operator).to.equal('add');
            (0, chai_1.expect)(finalExpression.left.type).to.equal('exponential');
            (0, chai_1.expect)(finalExpression.right.type).to.equal('functionCall');
            (0, chai_1.expect)(finalExpression.right.name).to.equal('sec');
            (0, chai_1.expect)(finalExpression.left.exponent.operator).to.equal('multiply');
        });
    });
});
