import { expect } from 'chai';
import { Parser } from '../src/parser'; // Import the Parser class
import {
    NumberExpression,
    VariableExpression,
    BinaryOperationExpression,
    UnaryOperationExpression
} from '../src/expression'; // Using the expression objects for expected ASTs

describe('Parser', () => {
    let parser: Parser;

    beforeEach(() => {
        parser = new Parser(); // Instantiate the Parser before each test
    });

    // Test partitions:
    // 1. Numbers (integers, decimals)
    // 2. Variables
    // 3. Binary Operations (+, -, *, /, ^)
    //    - Basic operations
    //    - PEMDAS order of operations (multiplication/division before addition/subtraction, exponentiation highest)
    //    - Left-to-right associativity for same precedence operators
    // 4. Unary Operations (+, -)
    //    - Applied to numbers
    //    - Applied to variables
    //    - Applied to parenthesized expressions
    // 5. Parentheses
    //    - Simple grouping
    //    - Nested parentheses
    // 6. Combined complex expressions
    // 7. Error handling for invalid syntax (e.g., incomplete expressions, malformed expressions)

    it('should parse a simple number', () => {
        const ast = parser.parse('123');
        expect(ast).to.deep.equal(new NumberExpression(123));
    });

    it('should parse a decimal number', () => {
        const ast = parser.parse('3.14');
        expect(ast).to.deep.equal(new NumberExpression(3.14));
    });

    it('should parse a variable', () => {
        const ast = parser.parse('x');
        expect(ast).to.deep.equal(new VariableExpression('x'));
    });

    it('should parse a multi-character variable', () => {
        const ast = parser.parse('myVar');
        expect(ast).to.deep.equal(new VariableExpression('myVar'));
    });

    it('should parse a simple addition', () => {
        const ast = parser.parse('1 + 2');
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '+',
                new NumberExpression(1),
                new NumberExpression(2)
            )
        );
    });

    it('should parse a simple subtraction', () => {
        const ast = parser.parse('5 - 3');
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '-',
                new NumberExpression(5),
                new NumberExpression(3)
            )
        );
    });

    it('should parse a simple multiplication', () => {
        const ast = parser.parse('4 * 6');
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '*',
                new NumberExpression(4),
                new NumberExpression(6)
            )
        );
    });

    it('should parse a simple division', () => {
        const ast = parser.parse('10 / 2');
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '/',
                new NumberExpression(10),
                new NumberExpression(2)
            )
        );
    });

    it('should parse exponentiation', () => {
        const ast = parser.parse('2 ^ 3');
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '^',
                new NumberExpression(2),
                new NumberExpression(3)
            )
        );
    });

    // PEMDAS order of operations tests
    it('should respect multiplication over addition (PEMDAS)', () => {
        const ast = parser.parse('2 + 3 * 4');
        // Expected: 2 + (3 * 4)
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '+',
                new NumberExpression(2),
                new BinaryOperationExpression(
                    '*',
                    new NumberExpression(3),
                    new NumberExpression(4)
                )
            )
        );
    });

    it('should respect division over subtraction (PEMDAS)', () => {
        const ast = parser.parse('10 - 4 / 2');
        // Expected: 10 - (4 / 2)
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '-',
                new NumberExpression(10),
                new BinaryOperationExpression(
                    '/',
                    new NumberExpression(4),
                    new NumberExpression(2)
                )
            )
        );
    });

    it('should respect exponentiation over multiplication (PEMDAS)', () => {
        const ast = parser.parse('2 * 3 ^ 2');
        // Expected: 2 * (3 ^ 2)
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '*',
                new NumberExpression(2),
                new BinaryOperationExpression(
                    '^',
                    new NumberExpression(3),
                    new NumberExpression(2)
                )
            )
        );
    });

    it('should handle left-to-right associativity for same precedence operators (addition/subtraction)', () => {
        const ast = parser.parse('10 - 5 + 2');
        // Expected: (10 - 5) + 2
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '+',
                new BinaryOperationExpression(
                    '-',
                    new NumberExpression(10),
                    new NumberExpression(5)
                ),
                new NumberExpression(2)
            )
        );
    });

    it('should handle left-to-right associativity for same precedence operators (multiplication/division)', () => {
        const ast = parser.parse('24 / 4 * 2');
        // Expected: (24 / 4) * 2
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '*',
                new BinaryOperationExpression(
                    '/',
                    new NumberExpression(24),
                    new NumberExpression(4)
                ),
                new NumberExpression(2)
            )
        );
    });

    // Unary operations tests
    it('should parse unary plus with a number', () => {
        const ast = parser.parse('+5');
        expect(ast).to.deep.equal(
            new UnaryOperationExpression(
                '+',
                new NumberExpression(5)
            )
        );
    });

    it('should parse unary minus with a number', () => {
        const ast = parser.parse('-10');
        expect(ast).to.deep.equal(
            new UnaryOperationExpression(
                '-',
                new NumberExpression(10)
            )
        );
    });

    it('should parse unary minus with a variable', () => {
        const ast = parser.parse('-x');
        expect(ast).to.deep.equal(
            new UnaryOperationExpression(
                '-',
                new VariableExpression('x')
            )
        );
    });

    it('should parse multiple unary operators', () => {
        const ast = parser.parse('--5');
        expect(ast).to.deep.equal(
            new UnaryOperationExpression(
                '-',
                new UnaryOperationExpression(
                    '-',
                    new NumberExpression(5)
                )
            )
        );
    });

    // Parentheses tests
    it('should parse an expression with parentheses to override PEMDAS', () => {
        const ast = parser.parse('(2 + 3) * 4');
        // Expected: (2 + 3) * 4
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '*',
                new BinaryOperationExpression(
                    '+',
                    new NumberExpression(2),
                    new NumberExpression(3)
                ),
                new NumberExpression(4)
            )
        );
    });

    it('should parse an expression with nested parentheses', () => {
        const ast = parser.parse('((1 + 2) * 3) - 4');
        // Expected: ((1 + 2) * 3) - 4
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '-',
                new BinaryOperationExpression(
                    '*',
                    new BinaryOperationExpression(
                        '+',
                        new NumberExpression(1),
                        new NumberExpression(2)
                    ),
                    new NumberExpression(3)
                ),
                new NumberExpression(4)
            )
        );
    });

    it('should parse a unary operation inside parentheses', () => {
        const ast = parser.parse('-(5 + x)');
        expect(ast).to.deep.equal(
            new UnaryOperationExpression(
                '-',
                new BinaryOperationExpression(
                    '+',
                    new NumberExpression(5),
                    new VariableExpression('x')
                )
            )
        );
    });

    // Combined complex expressions
    it('should parse a complex expression with mixed operations and parentheses', () => {
        const ast = parser.parse('x + 5 * (y - 2) / 3 ^ z');
        // Expected: x + (5 * ((y - 2) / (3 ^ z)))
        // Note: Division and multiplication have same precedence, processed left-to-right
        // Exponentiation has higher precedence than multiplication/division
        expect(ast).to.deep.equal(
            new BinaryOperationExpression(
                '+',
                new VariableExpression('x'),
                new BinaryOperationExpression(
                    '/',
                    new BinaryOperationExpression(
                        '*',
                        new NumberExpression(5),
                        new BinaryOperationExpression(
                            '-',
                            new VariableExpression('y'),
                            new NumberExpression(2)
                        )
                    ),
                    new BinaryOperationExpression(
                        '^',
                        new NumberExpression(3),
                        new VariableExpression('z')
                    )
                )
            )
        );
    });

    it('should parse an expression with leading unary operators and parentheses', () => {
        const ast = parser.parse('-(-(2 + 3) * 4)');
        expect(ast).to.deep.equal(
            new UnaryOperationExpression(
                '-',
                new UnaryOperationExpression(
                    '-',
                    new BinaryOperationExpression(
                        '*',
                        new BinaryOperationExpression(
                            '+',
                            new NumberExpression(2),
                            new NumberExpression(3)
                        ),
                        new NumberExpression(4)
                    )
                )
            )
        );
    });

    // Error handling tests (assuming the parser throws an error for invalid syntax)
    // These tests depend on the parser's error mechanism.
    // If the parser returns a specific error object or null, adjust expectations.
    it('should throw an error for an empty string', () => {
        expect(() => parser.parse('')).to.throw('Syntax Error: Empty expression');
    });

    it('should throw an error for an incomplete expression', () => {
        expect(() => parser.parse('1 +')).to.throw('Syntax Error: Incomplete expression');
    });

    it('should throw an error for mismatched parentheses', () => {
        expect(() => parser.parse('(1 + 2')).to.throw('Syntax Error: Mismatched parentheses');
        expect(() => parser.parse('1 + 2)')).to.throw('Syntax Error: Mismatched parentheses');
    });

    it('should throw an error for invalid characters', () => {
        expect(() => parser.parse('1 $ 2')).to.throw('Syntax Error: Invalid character');
    });

    it('should throw an error for an invalid sequence of operators', () => {
        expect(() => parser.parse('1 * / 2')).to.throw('Syntax Error: Unexpected operator');
    });

    it('should throw an error for a number followed by a variable without an operator', () => {
        expect(() => parser.parse('2x')).to.throw('Syntax Error: Unexpected token');
    });

    it('should throw an error for a variable followed by a number without an operator', () => {
        expect(() => parser.parse('x2')).to.throw('Syntax Error: Unexpected token'); // Assuming 'x2' is not a valid variable name, or it's 'x' followed by '2'
    });

    it('should throw an error for a variable followed by an opening parenthesis without an operator', () => {
        expect(() => parser.parse('x(2+3)')).to.throw('Syntax Error: Unexpected token');
    });

    it('should throw an error for an empty set of parentheses', () => {
        expect(() => parser.parse('()')).to.throw('Syntax Error: Empty parentheses');
    });
});
