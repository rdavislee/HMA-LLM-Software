import { expect } from 'chai';
import {
    NumberNode,
    VariableNode,
    BinaryOperationNode,
    UnaryOperationNode,
    FunctionCallNode,
    ConstantNode
} from '../src/expression';

import {
    ExpressionNode,
    BinaryOperatorType,
    UnaryOperatorType,
    FunctionNameType,
    ConstantType // Changed from ConstantNameType
} from '../src/expressionInterface';

import { parse } from '../src/parser';

// Helper functions to create expected AST nodes for clarity.
// These now create actual instances of the ExpressionNode classes.
// Chai's deep.equal will compare these instances with those returned by the parser.
// The 'toString' method should now be present on these objects, aligning with the actual AST nodes.

const numNode = (value: number): ExpressionNode => new NumberNode(value);
const varNode = (name: string): ExpressionNode => new VariableNode(name);
const constNode = (name: ConstantType): ExpressionNode => new ConstantNode(name); // Updated type here
const binOpNode = (operator: BinaryOperatorType, left: ExpressionNode, right: ExpressionNode): ExpressionNode => new BinaryOperationNode(operator, left, right);
const unOpNode = (operator: UnaryOperatorType, operand: ExpressionNode): ExpressionNode => new UnaryOperationNode(operator, operand);
const funcCallNode = (name: FunctionNameType, args: ExpressionNode[]): ExpressionNode => new FunctionCallNode(name, args);

describe('Parser', () => {
    // Test partitions:
    // 1. Number literals: integers, decimals, zero.
    // 2. Variable literals: single letter, common variable names.
    // 3. Constants: 'e', 'pi'.
    // 4. Binary operations:
    //    - Basic operations: add, subtract, multiply, divide, power.
    //    - Chained operations (left-associativity for +, -, *, /; right-associativity for ^).
    // 5. Unary operations: negation.
    // 6. Function calls: log, sin, cos, tan, ln, asin, acos, atan with various argument types.
    // 7. Operator Precedence (PEMDAS/BODMAS): Correct order of operations.
    // 8. Parentheses for Grouping: Overriding default precedence.
    // 9. Combined Complex Expressions: Mix of all node types.
    // 10. Whitespace Handling: Robustness to varying whitespace.
    // 11. Error Handling: Invalid syntax (e.g., unmatched parentheses, missing operands, invalid tokens).

    describe('Number Parsing', () => {
        it('should parse a single integer', () => {
            expect(parse('123')).to.deep.equal(numNode(123));
        });

        it('should parse a decimal number', () => {
            expect(parse('3.14')).to.deep.equal(numNode(3.14));
        });

        it('should parse zero', () => {
            expect(parse('0')).to.deep.equal(numNode(0));
        });
    });

    describe('Variable Parsing', () => {
        it('should parse a single variable', () => {
            expect(parse('x')).to.deep.equal(varNode('x'));
        });

        it('should parse a variable with multiple characters', () => {
            expect(parse('theta')).to.deep.equal(varNode('theta'));
        });
    });

    describe('Constant Parsing', () => {
        it('should parse constant "e"', () => {
            expect(parse('e')).to.deep.equal(constNode('e'));
        });

        it('should parse constant "pi"', () => {
            expect(parse('pi')).to.deep.equal(constNode('pi'));
        });

        it('should parse expression with constant e (2*e)', () => {
            expect(parse('2 * e')).to.deep.equal(binOpNode('multiply', numNode(2), constNode('e')));
        });

        it('should parse expression with constant pi (pi/2)', () => {
            expect(parse('pi / 2')).to.deep.equal(binOpNode('divide', constNode('pi'), numNode(2)));
        });
    });

    describe('Binary Operation Parsing', () => {
        it('should parse addition (1 + 2)', () => {
            expect(parse('1 + 2')).to.deep.equal(binOpNode('add', numNode(1), numNode(2)));
        });

        it('should parse subtraction (5 - 3)', () => {
            expect(parse('5 - 3')).to.deep.equal(binOpNode('subtract', numNode(5), numNode(3)));
        });

        it('should parse multiplication (4 * 6)', () => {
            expect(parse('4 * 6')).to.deep.equal(binOpNode('multiply', numNode(4), numNode(6)));
        });

        it('should parse division (10 / 2)', () => {
            expect(parse('10 / 2')).to.deep.equal(binOpNode('divide', numNode(10), numNode(2)));
        });

        it('should parse power (2 ^ 3)', () => {
            expect(parse('2 ^ 3')).to.deep.equal(binOpNode('power', numNode(2), numNode(3)));
        });

        it('should parse chained addition (left-associative: 1 + 2 + 3)', () => {
            expect(parse('1 + 2 + 3')).to.deep.equal(binOpNode('add', binOpNode('add', numNode(1), numNode(2)), numNode(3)));
        });

        it('should parse chained multiplication (left-associative: 2 * 3 * 4)', () => {
            expect(parse('2 * 3 * 4')).to.deep.equal(binOpNode('multiply', binOpNode('multiply', numNode(2), numNode(3)), numNode(4)));
        });

        it('should parse chained power (right-associative: 2 ^ 3 ^ 2)', () => {
            expect(parse('2 ^ 3 ^ 2')).to.deep.equal(binOpNode('power', numNode(2), binOpNode('power', numNode(3), numNode(2))));
        });
    });

    describe('Unary Operation Parsing', () => {
        it('should parse negation of a number (-5)', () => {
            expect(parse('-5')).to.deep.equal(unOpNode('negate', numNode(5)));
        });

        it('should parse negation of a variable (-x)', () => {
            expect(parse('-x')).to.deep.equal(unOpNode('negate', varNode('x')));
        });

        it('should parse negation of a constant (-e)', () => {
            expect(parse('-e')).to.deep.equal(unOpNode('negate', constNode('e')));
        });

        it('should parse negation of an expression (-(1 + 2))', () => {
            expect(parse('-(1 + 2)')).to.deep.equal(unOpNode('negate', binOpNode('add', numNode(1), numNode(2))));
        });

        it('should parse double negation (--5)', () => {
            expect(parse('--5')).to.deep.equal(unOpNode('negate', unOpNode('negate', numNode(5))));
        });
    });

    describe('Function Call Parsing', () => {
        it('should parse log(x)', () => {
            expect(parse('log(x)')).to.deep.equal(funcCallNode('log', [varNode('x')]));
        });

        it('should parse sin(3.14)', () => {
            expect(parse('sin(3.14)')).to.deep.equal(funcCallNode('sin', [numNode(3.14)]));
        });

        it('should parse cos(y + 1)', () => {
            expect(parse('cos(y + 1)')).to.deep.equal(funcCallNode('cos', [binOpNode('add', varNode('y'), numNode(1))]));
        });

        it('should parse tan(2 * pi)', () => {
            expect(parse('tan(2 * pi)')).to.deep.equal(funcCallNode('tan', [binOpNode('multiply', numNode(2), constNode('pi'))]));
        });

        it('should parse ln(x^2)', () => {
            expect(parse('ln(x^2)')).to.deep.equal(funcCallNode('ln', [binOpNode('power', varNode('x'), numNode(2))]));
        });

        it('should parse asin(0.5)', () => {
            expect(parse('asin(0.5)')).to.deep.equal(funcCallNode('asin', [numNode(0.5)]));
        });

        it('should parse acos(z)', () => {
            expect(parse('acos(z)')).to.deep.equal(funcCallNode('acos', [varNode('z')]));
        });

        it('should parse atan(e * x)', () => {
            expect(parse('atan(e * x)')).to.deep.equal(funcCallNode('atan', [binOpNode('multiply', constNode('e'), varNode('x'))]));
        });
    });

    describe('Operator Precedence (PEMDAS/BODMAS)', () => {
        it('should respect multiplication over addition (2 + 3 * 4)', () => {
            expect(parse('2 + 3 * 4')).to.deep.equal(binOpNode('add', numNode(2), binOpNode('multiply', numNode(3), numNode(4))));
        });

        it('should respect division over subtraction (10 - 6 / 2)', () => {
            expect(parse('10 - 6 / 2')).to.deep.equal(binOpNode('subtract', numNode(10), binOpNode('divide', numNode(6), numNode(2))));
        });

        it('should respect power over multiplication (2 * 3 ^ 2)', () => {
            expect(parse('2 * 3 ^ 2')).to.deep.equal(binOpNode('multiply', numNode(2), binOpNode('power', numNode(3), numNode(2))));
        });

        it('should handle multiple levels of precedence (1 + 2 * 3 ^ 2 - 4 / 2)', () => {
            expect(parse('1 + 2 * 3 ^ 2 - 4 / 2')).to.deep.equal(
                binOpNode('subtract',
                    binOpNode('add',
                        numNode(1),
                        binOpNode('multiply',
                            numNode(2),
                            binOpNode('power', numNode(3), numNode(2))
                        )
                    ),
                    binOpNode('divide', numNode(4), numNode(2))
                )
            );
        });
    });

    describe('Parentheses for Grouping', () => {
        it('should enforce order with parentheses (addition before multiplication: (2 + 3) * 4)', () => {
            expect(parse('(2 + 3) * 4')).to.deep.equal(binOpNode('multiply', binOpNode('add', numNode(2), numNode(3)), numNode(4)));
        });

        it('should handle nested parentheses ( ((1 + 2) * 3) - 4 )', () => {
            expect(parse('((1 + 2) * 3) - 4')).to.deep.equal(
                binOpNode('subtract',
                    binOpNode('multiply',
                        binOpNode('add', numNode(1), numNode(2)),
                        numNode(3)
                    ),
                    numNode(4)
                )
            );
        });
    });

    describe('Combined Complex Expressions', () => {
        it('should parse sin(x) + cos(y) * (z - 1) ^ 2', () => {
            expect(parse('sin(x) + cos(y) * (z - 1) ^ 2')).to.deep.equal(
                binOpNode('add',
                    funcCallNode('sin', [varNode('x')]),
                    binOpNode('multiply',
                        funcCallNode('cos', [varNode('y')]),
                        binOpNode('power',
                            binOpNode('subtract', varNode('z'), numNode(1)),
                            numNode(2)
                        )
                    )
                )
            );
        });

        it('should parse -x + -(y * z)', () => {
            expect(parse('-x + -(y * z)')).to.deep.equal(
                binOpNode('add',
                    unOpNode('negate', varNode('x')),
                    unOpNode('negate', binOpNode('multiply', varNode('y'), varNode('z')))
                )
            );
        });

        it('should parse log(a + b) / (c - d) ^ -e', () => {
            expect(parse('log(a + b) / (c - d) ^ -e')).to.deep.equal(
                binOpNode('divide',
                    funcCallNode('log', [binOpNode('add', varNode('a'), varNode('b'))]),
                    binOpNode('power',
                        binOpNode('subtract', varNode('c'), varNode('d')),
                        unOpNode('negate', constNode('e'))
                    )
                )
            );
        });

        it('should parse asin(pi/2) + acos(0) - atan(e)', () => {
            expect(parse('asin(pi/2) + acos(0) - atan(e)')).to.deep.equal(
                binOpNode('subtract',
                    binOpNode('add',
                        funcCallNode('asin', [binOpNode('divide', constNode('pi'), numNode(2))]),
                        funcCallNode('acos', [numNode(0)])
                    ),
                    funcCallNode('atan', [constNode('e')])
                )
            );
        });
    });

    describe('Whitespace Handling', () => {
        it('should ignore leading/trailing whitespace', () => {
            expect(parse('  1 + 2  ')).to.deep.equal(binOpNode('add', numNode(1), numNode(2)));
        });

        it('should ignore irregular whitespace between tokens', () => {
            expect(parse('1   +  2*  x')).to.deep.equal(binOpNode('add', numNode(1), binOpNode('multiply', numNode(2), varNode('x'))));
        });
    });

    describe('Error Handling for Invalid Syntax', () => {
        it('should throw an error for unmatched opening parenthesis', () => {
            expect(() => parse('(1 + 2')).to.throw();
        });

        it('should throw an error for unmatched closing parenthesis', () => {
            expect(() => parse('1 + 2)')).to.throw();
        });

        it('should throw an error for empty input', () => {
            expect(() => parse('')).to.throw();
        });

        it('should throw an error for invalid characters', () => {
            expect(() => parse('1 $ 2')).to.throw();
        });

        it('should throw an error for missing operand (binary)', () => {
            expect(() => parse('1 +')).to.throw();
        });

        it('should throw an error for missing operand (unary)', () => {
            expect(() => parse('-')).to.throw();
        });

        it('should throw an error for missing argument in function call', () => {
            expect(() => parse('sin()')).to.throw();
        });

        it('should throw an error for too many arguments in function call (assuming single argument functions)', () => {
            expect(() => parse('sin(x, y)')).to.throw();
        });

        it('should throw an error for unexpected token', () => {
            expect(() => parse('1 2')).to.throw();
        });

        it('should throw an error for function call without parentheses', () => {
            expect(() => parse('sin x')).to.throw();
        });
    });
});
