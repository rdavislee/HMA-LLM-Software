import { expect } from 'chai';
import {
    NumberNode,
    VariableNode,
    BinaryOperationNode,
    UnaryOperationNode,
    FunctionCallNode,
    ConstantNode,
    ExponentialNode
} from '../src/expression'; // Assuming concrete classes are exported from here

import {
    Expression,
    BinaryOperatorType,
    UnaryOperatorType,
    FunctionNameType,
    ConstantType,
    ExpressionNode
} from '../src/expressionInterface'; // Types and interfaces are exported from here

describe('Expression AST Nodes', () => {

    // Test Partition: NumberNode
    describe('NumberNode', () => {
        it('should correctly represent a positive integer', () => {
            const num = new NumberNode(10);
            expect(num.type).to.equal('number');
            expect(num.value).to.equal(10);
            // toString() is part of the interface, but not implemented by default objects.
            // This test is for the structure. toString() behavior will be tested when implemented in src/expression.ts.
            // expect(num.toString()).to.equal('10');
        });

        it('should correctly represent a negative float', () => {
            const num = new NumberNode(-3.14);
            expect(num.type).to.equal('number');
            expect(num.value).to.equal(-3.14);
            // expect(num.toString()).to.equal('-3.14');
        });

        it('should correctly represent zero', () => {
            const num = new NumberNode(0);
            expect(num.type).to.equal('number');
            expect(num.value).to.equal(0);
            // expect(num.toString()).to.equal('0');
        });
    });

    // Test Partition: VariableNode
    describe('VariableNode', () => {
        it('should correctly represent a variable "x"', () => {
            const variable = new VariableNode('x');
            expect(variable.type).to.equal('variable');
            expect(variable.name).to.equal('x');
            // expect(variable.toString()).to.equal('x');
        });

        it('should correctly represent a variable "theta"', () => {
            const variable = new VariableNode('theta');
            expect(variable.type).to.equal('variable');
            expect(variable.name).to.equal('theta');
            // expect(variable.toString()).to.equal('theta');
        });
    });

    // Test Partition: BinaryOperationNode
    describe('BinaryOperationNode', () => {
        // Test partitions for operator types
        const operators: BinaryOperatorType[] = ['add', 'subtract', 'multiply', 'divide', 'power'];

        operators.forEach(operator => {
            it(`should correctly represent a '${operator}' operation`, () => {
                const leftNum = new NumberNode(5);
                const rightVar = new VariableNode('y');
                const op = new BinaryOperationNode(operator, leftNum, rightVar);
                expect(op.type).to.equal('binaryOperation');
                expect(op.operator).to.equal(operator);
                expect(op.left).to.deep.equal(leftNum);
                expect(op.right).to.deep.equal(rightVar);
                // toString() output will depend on implementation, but structure should be consistent
                // For now, we'll test a basic string representation
                // Assuming simple infix notation without complex precedence handling in toString for now
                // The actual toString implementation will be in expression.ts
            });
        });

        it('should represent complex nested binary operations correctly', () => {
            const num1 = new NumberNode(2);
            const num2 = new NumberNode(3);
            const num3 = new NumberNode(4);
            const varX = new VariableNode('x');

            const addOp = new BinaryOperationNode('add', num1, num2);

            const multiplyOp = new BinaryOperationNode('multiply', addOp, num3);

            const finalOp = new BinaryOperationNode('power', multiplyOp, varX);
            expect(finalOp.type).to.equal('binaryOperation');
            expect(finalOp.operator).to.equal('power');
            expect(finalOp.left.type).to.equal('binaryOperation');
            expect((finalOp.left as BinaryOperationNode).operator).to.equal('multiply');
            expect(finalOp.right).to.deep.equal(varX);
            // Again, toString() depends on implementation. We expect a string representation.
            // Example: "((2 + 3) * 4)^x"
            // This test is more about ensuring the structure is valid, toString() actual output will be tested in expression.ts
        });
    });

    // Test Partition: UnaryOperationNode
    describe('UnaryOperationNode', () => {
        // Test partitions for operator types
        const operators: UnaryOperatorType[] = ['negate'];

        operators.forEach(operator => {
            it(`should correctly represent a '${operator}' operation`, () => {
                const operandNum = new NumberNode(7);
                const op = new UnaryOperationNode(operator, operandNum);
                expect(op.type).to.equal('unaryOperation');
                expect(op.operator).to.equal(operator);
                expect(op.operand).to.deep.equal(operandNum);
                // Expected toString for negate: "-7"
            });
        });

        it('should handle nested unary operations', () => {
            const num = new NumberNode(5);
            const negate1 = new UnaryOperationNode('negate', num);
            const negate2 = new UnaryOperationNode('negate', negate1);
            expect(negate2.type).to.equal('unaryOperation');
            expect(negate2.operator).to.equal('negate');
            expect(negate2.operand.type).to.equal('unaryOperation');
            expect((negate2.operand as UnaryOperationNode).operator).to.equal('negate');
            // Expected toString: "--5" or "-(-5)" depending on implementation
        });
    });

    // Test Partition: FunctionCallNode
    describe('FunctionCallNode', () => {
        // Test partitions for function names
        const functionNames: FunctionNameType[] = [
            'log', 'ln', 'exp',
            'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
            'asin', 'acos', 'atan', 'asec', 'acsc', 'acot'
        ];

        functionNames.forEach(funcName => {
            it(`should correctly represent a '${funcName}' function call with one argument`, () => {
                const arg = new VariableNode('z');
                const funcCall = new FunctionCallNode(funcName, [arg]);
                expect(funcCall.type).to.equal('functionCall');
                expect(funcCall.name).to.equal(funcName);
                expect(funcCall.args).to.have.lengthOf(1);
                expect(funcCall.args[0]).to.deep.equal(arg);
                // Expected toString: "log(z)", "sin(z)", etc.
            });
        });

        it('should handle nested function calls', () => {
            const num = new NumberNode(90);
            const sinCall = new FunctionCallNode('sin', [num]);
            const logCall = new FunctionCallNode('log', [sinCall]);
            expect(logCall.type).to.equal('functionCall');
            expect(logCall.name).to.equal('log');
            expect(logCall.args).to.have.lengthOf(1);
            expect(logCall.args[0].type).to.equal('functionCall');
            expect((logCall.args[0] as FunctionCallNode).name).to.equal('sin');
            // Expected toString: "log(sin(90))"
        });

        it('should handle function calls with complex arguments', () => {
            const num1 = new NumberNode(5);
            const varX = new VariableNode('x');
            const addOp = new BinaryOperationNode('add', num1, varX);
            const cosCall = new FunctionCallNode('cos', [addOp]);
            expect(cosCall.type).to.equal('functionCall');
            expect(cosCall.name).to.equal('cos');
            expect(cosCall.args).to.have.lengthOf(1);
            expect(cosCall.args[0].type).to.equal('binaryOperation');
            expect((cosCall.args[0] as BinaryOperationNode).operator).to.equal('add');
            // Expected toString: "cos(5 + x)"
        });

        it('should throw an error for function calls with zero arguments when one is required', () => {
            // The spec for FunctionCallNode in expressionInterface.ts states:
            // "For all supported functions, args must contain exactly one element."
            // This test verifies that the constructor enforces this precondition.
            expect(() => new FunctionCallNode('log', []))
                .to.throw('Function \'log\' expects exactly one argument, but received 0.'); // Updated error message to match implementation
        });

        it('should throw an error for function calls with multiple arguments when one is required', () => {
            // The spec for FunctionCallNode in expressionInterface.ts states:
            // "For all supported functions, args must contain exactly one element."
            // This test verifies that the constructor enforces this precondition.
            const num1 = new NumberNode(1);
            const num2 = new NumberNode(2);
            expect(() => new FunctionCallNode('log', [num1, num2]))
                .to.throw('Function \'log\' expects exactly one argument, but received 2.'); // Updated error message to match implementation
        });
    });

    // Test Partition: ConstantNode
    describe('ConstantNode', () => {
        const constants: ConstantType[] = ['e', 'pi'];

        constants.forEach(constantName => {
            it(`should correctly represent the constant '${constantName}'`, () => {
                const constant = new ConstantNode(constantName);
                expect(constant.type).to.equal('constant');
                expect(constant.name).to.equal(constantName);
                // Expected toString: "e" or "pi"
            });
        });
    });

    // Test Partition: ExponentialNode
    describe('ExponentialNode', () => {
        it('should correctly represent e^x', () => {
            const exponentVar = new VariableNode('x');
            const expNode = new ExponentialNode(exponentVar);
            expect(expNode.type).to.equal('exponential');
            expect(expNode.exponent).to.deep.equal(exponentVar);
            // Expected toString: "e^x"
        });

        it('should correctly represent e^(2*y)', () => {
            const num2 = new NumberNode(2);
            const varY = new VariableNode('y');
            const multiplyOp = new BinaryOperationNode('multiply', num2, varY);
            const expNode = new ExponentialNode(multiplyOp);
            expect(expNode.type).to.equal('exponential');
            expect(expNode.exponent).to.deep.equal(multiplyOp);
            // Expected toString: "e^(2 * y)"
        });

        it('should handle nested exponentials: e^(e^x)', () => {
            const varX = new VariableNode('x');
            const nestedExp = new ExponentialNode(varX);
            const expNode = new ExponentialNode(nestedExp);
            expect(expNode.type).to.equal('exponential');
            expect(expNode.exponent).to.deep.equal(nestedExp);
            // Expected toString: "e^(e^x)"
        });
    });

    // Test Partition: Combined/Mixed Expressions
    describe('Combined Expressions', () => {
        it('should correctly represent a complex expression: ((-x + 3) * sin(y)) / log(10)', () => {
            const varX = new VariableNode('x');
            const num3 = new NumberNode(3);
            const varY = new VariableNode('y');
            const num10 = new NumberNode(10);

            const negateX = new UnaryOperationNode('negate', varX);
            const addOp = new BinaryOperationNode('add', negateX, num3);
            const sinY = new FunctionCallNode('sin', [varY]);
            const multiplyOp = new BinaryOperationNode('multiply', addOp, sinY);
            const log10 = new FunctionCallNode('log', [num10]);
            const divideOp = new BinaryOperationNode('divide', multiplyOp, log10);

            expect(divideOp.type).to.equal('binaryOperation');
            expect(divideOp.operator).to.equal('divide');
            expect((divideOp.left as BinaryOperationNode).operator).to.equal('multiply');
            expect((divideOp.right as FunctionCallNode).name).to.equal('log');
            // The structure is correctly built. toString() will be tested later.
            // Expected toString: "(( -x + 3 ) * sin(y)) / log(10)" (parentheses might vary based on precedence rules in toString)
        });

        it('should correctly represent a complex expression involving new types: e^(pi * cos(x)) + sec(y)', () => {
            const piConst = new ConstantNode('pi');
            const varX = new VariableNode('x');
            const varY = new VariableNode('y');

            const cosX = new FunctionCallNode('cos', [varX]);
            const piMultiplyCosX = new BinaryOperationNode('multiply', piConst, cosX);
            const expNode = new ExponentialNode(piMultiplyCosX);
            const secY = new FunctionCallNode('sec', [varY]);
            const finalExpression = new BinaryOperationNode('add', expNode, secY);

            expect(finalExpression.type).to.equal('binaryOperation');
            expect(finalExpression.operator).to.equal('add');
            expect(finalExpression.left.type).to.equal('exponential');
            expect(finalExpression.right.type).to.equal('functionCall');
            expect((finalExpression.right as FunctionCallNode).name).to.equal('sec');
            expect(((finalExpression.left as ExponentialNode).exponent as BinaryOperationNode).operator).to.equal('multiply');
        });
    });
});