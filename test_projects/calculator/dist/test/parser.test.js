"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const chai_1 = require("chai");
const parser_1 = require("../src/parser"); // Import the Parser class
const expression_1 = require("../src/expression"); // Using the expression objects for expected ASTs
describe('Parser', () => {
    let parser;
    beforeEach(() => {
        parser = new parser_1.Parser(); // Instantiate the Parser before each test
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
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.NumberExpression(123));
    });
    it('should parse a decimal number', () => {
        const ast = parser.parse('3.14');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.NumberExpression(3.14));
    });
    it('should parse a variable', () => {
        const ast = parser.parse('x');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.VariableExpression('x'));
    });
    it('should parse a multi-character variable', () => {
        const ast = parser.parse('myVar');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.VariableExpression('myVar'));
    });
    it('should parse a simple addition', () => {
        const ast = parser.parse('1 + 2');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(1), new expression_1.NumberExpression(2)));
    });
    it('should parse a simple subtraction', () => {
        const ast = parser.parse('5 - 3');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('-', new expression_1.NumberExpression(5), new expression_1.NumberExpression(3)));
    });
    it('should parse a simple multiplication', () => {
        const ast = parser.parse('4 * 6');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(4), new expression_1.NumberExpression(6)));
    });
    it('should parse a simple division', () => {
        const ast = parser.parse('10 / 2');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(10), new expression_1.NumberExpression(2)));
    });
    it('should parse exponentiation', () => {
        const ast = parser.parse('2 ^ 3');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('^', new expression_1.NumberExpression(2), new expression_1.NumberExpression(3)));
    });
    // PEMDAS order of operations tests
    it('should respect multiplication over addition (PEMDAS)', () => {
        const ast = parser.parse('2 + 3 * 4');
        // Expected: 2 + (3 * 4)
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(2), new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(3), new expression_1.NumberExpression(4))));
    });
    it('should respect division over subtraction (PEMDAS)', () => {
        const ast = parser.parse('10 - 4 / 2');
        // Expected: 10 - (4 / 2)
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('-', new expression_1.NumberExpression(10), new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(4), new expression_1.NumberExpression(2))));
    });
    it('should respect exponentiation over multiplication (PEMDAS)', () => {
        const ast = parser.parse('2 * 3 ^ 2');
        // Expected: 2 * (3 ^ 2)
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(2), new expression_1.BinaryOperationExpression('^', new expression_1.NumberExpression(3), new expression_1.NumberExpression(2))));
    });
    it('should handle left-to-right associativity for same precedence operators (addition/subtraction)', () => {
        const ast = parser.parse('10 - 5 + 2');
        // Expected: (10 - 5) + 2
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('+', new expression_1.BinaryOperationExpression('-', new expression_1.NumberExpression(10), new expression_1.NumberExpression(5)), new expression_1.NumberExpression(2)));
    });
    it('should handle left-to-right associativity for same precedence operators (multiplication/division)', () => {
        const ast = parser.parse('24 / 4 * 2');
        // Expected: (24 / 4) * 2
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('*', new expression_1.BinaryOperationExpression('/', new expression_1.NumberExpression(24), new expression_1.NumberExpression(4)), new expression_1.NumberExpression(2)));
    });
    // Unary operations tests
    it('should parse unary plus with a number', () => {
        const ast = parser.parse('+5');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.UnaryOperationExpression('+', new expression_1.NumberExpression(5)));
    });
    it('should parse unary minus with a number', () => {
        const ast = parser.parse('-10');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.UnaryOperationExpression('-', new expression_1.NumberExpression(10)));
    });
    it('should parse unary minus with a variable', () => {
        const ast = parser.parse('-x');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.UnaryOperationExpression('-', new expression_1.VariableExpression('x')));
    });
    it('should parse multiple unary operators', () => {
        const ast = parser.parse('--5');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.UnaryOperationExpression('-', new expression_1.UnaryOperationExpression('-', new expression_1.NumberExpression(5))));
    });
    // Parentheses tests
    it('should parse an expression with parentheses to override PEMDAS', () => {
        const ast = parser.parse('(2 + 3) * 4');
        // Expected: (2 + 3) * 4
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('*', new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(2), new expression_1.NumberExpression(3)), new expression_1.NumberExpression(4)));
    });
    it('should parse an expression with nested parentheses', () => {
        const ast = parser.parse('((1 + 2) * 3) - 4');
        // Expected: ((1 + 2) * 3) - 4
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('-', new expression_1.BinaryOperationExpression('*', new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(1), new expression_1.NumberExpression(2)), new expression_1.NumberExpression(3)), new expression_1.NumberExpression(4)));
    });
    it('should parse a unary operation inside parentheses', () => {
        const ast = parser.parse('-(5 + x)');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.UnaryOperationExpression('-', new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(5), new expression_1.VariableExpression('x'))));
    });
    // Combined complex expressions
    it('should parse a complex expression with mixed operations and parentheses', () => {
        const ast = parser.parse('x + 5 * (y - 2) / 3 ^ z');
        // Expected: x + (5 * ((y - 2) / (3 ^ z)))
        // Note: Division and multiplication have same precedence, processed left-to-right
        // Exponentiation has higher precedence than multiplication/division
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.BinaryOperationExpression('+', new expression_1.VariableExpression('x'), new expression_1.BinaryOperationExpression('/', new expression_1.BinaryOperationExpression('*', new expression_1.NumberExpression(5), new expression_1.BinaryOperationExpression('-', new expression_1.VariableExpression('y'), new expression_1.NumberExpression(2))), new expression_1.BinaryOperationExpression('^', new expression_1.NumberExpression(3), new expression_1.VariableExpression('z')))));
    });
    it('should parse an expression with leading unary operators and parentheses', () => {
        const ast = parser.parse('-(-(2 + 3) * 4)');
        (0, chai_1.expect)(ast).to.deep.equal(new expression_1.UnaryOperationExpression('-', new expression_1.UnaryOperationExpression('-', new expression_1.BinaryOperationExpression('*', new expression_1.BinaryOperationExpression('+', new expression_1.NumberExpression(2), new expression_1.NumberExpression(3)), new expression_1.NumberExpression(4)))));
    });
    // Error handling tests (assuming the parser throws an error for invalid syntax)
    // These tests depend on the parser's error mechanism.
    // If the parser returns a specific error object or null, adjust expectations.
    it('should throw an error for an empty string', () => {
        (0, chai_1.expect)(() => parser.parse('')).to.throw('Syntax Error: Empty expression');
    });
    it('should throw an error for an incomplete expression', () => {
        (0, chai_1.expect)(() => parser.parse('1 +')).to.throw('Syntax Error: Incomplete expression');
    });
    it('should throw an error for mismatched parentheses', () => {
        (0, chai_1.expect)(() => parser.parse('(1 + 2')).to.throw('Syntax Error: Mismatched parentheses');
        (0, chai_1.expect)(() => parser.parse('1 + 2)')).to.throw('Syntax Error: Mismatched parentheses');
    });
    it('should throw an error for invalid characters', () => {
        (0, chai_1.expect)(() => parser.parse('1 $ 2')).to.throw('Syntax Error: Invalid character');
    });
    it('should throw an error for an invalid sequence of operators', () => {
        (0, chai_1.expect)(() => parser.parse('1 * / 2')).to.throw('Syntax Error: Unexpected operator');
    });
    it('should throw an error for a number followed by a variable without an operator', () => {
        (0, chai_1.expect)(() => parser.parse('2x')).to.throw('Syntax Error: Unexpected token');
    });
    it('should throw an error for a variable followed by a number without an operator', () => {
        (0, chai_1.expect)(() => parser.parse('x2')).to.throw('Syntax Error: Unexpected token'); // Assuming 'x2' is not a valid variable name, or it's 'x' followed by '2'
    });
    it('should throw an error for a variable followed by an opening parenthesis without an operator', () => {
        (0, chai_1.expect)(() => parser.parse('x(2+3)')).to.throw('Syntax Error: Unexpected token');
    });
    it('should throw an error for an empty set of parentheses', () => {
        (0, chai_1.expect)(() => parser.parse('()')).to.throw('Syntax Error: Empty parentheses');
    });
});
