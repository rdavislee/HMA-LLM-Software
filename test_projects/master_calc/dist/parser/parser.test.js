import { expect } from 'chai';
import { parse } from './parser.js';
import { tokenize } from './tokenizer.js';
import { NodeType } from '../types/ast.js';
describe('Parser', () => {
    // Helper to parse and return the AST root
    const parseExpression = (expression) => {
        const tokens = tokenize(expression);
        return parse(tokens);
    };
    describe('Basic Arithmetic Operations', () => {
        it('should parse a single number', () => {
            const ast = parseExpression('123');
            expect(ast.type).to.equal(NodeType.Number);
            expect(ast.value).to.equal(123);
        });
        it('should parse a single variable', () => {
            const ast = parseExpression('x');
            expect(ast.type).to.equal(NodeType.Variable);
            expect(ast.name).to.equal('x');
        });
        it('should parse addition', () => {
            const ast = parseExpression('2+3');
            expect(ast.type).to.equal(NodeType.BinaryOperation);
            expect(ast.operator).to.equal('+');
            expect(ast.left.value).to.equal(2);
            expect(ast.right.value).to.equal(3);
        });
        it('should parse subtraction', () => {
            const ast = parseExpression('5-2');
            expect(ast.type).to.equal(NodeType.BinaryOperation);
            expect(ast.operator).to.equal('-');
        });
        it('should parse multiplication', () => {
            const ast = parseExpression('4*6');
            expect(ast.type).to.equal(NodeType.BinaryOperation);
            expect(ast.operator).to.equal('*');
        });
        it('should parse division', () => {
            const ast = parseExpression('8/2');
            expect(ast.type).to.equal(NodeType.BinaryOperation);
            expect(ast.operator).to.equal('/');
        });
        it('should parse power', () => {
            const ast = parseExpression('2^3');
            expect(ast.type).to.equal(NodeType.BinaryOperation);
            expect(ast.operator).to.equal('^');
        });
    });
    describe('Operator Precedence (PEMDAS)', () => {
        it('should handle multiplication before addition', () => {
            const ast = parseExpression('2+3*4');
            expect(ast.operator).to.equal('+');
            expect(ast.left.value).to.equal(2);
            expect(ast.right.operator).to.equal('*');
            expect(ast.right.left.value).to.equal(3);
            expect(ast.right.right.value).to.equal(4);
        });
        it('should handle parentheses correctly', () => {
            const ast = parseExpression('(2+3)*4');
            expect(ast.operator).to.equal('*');
            expect(ast.right.value).to.equal(4);
            expect(ast.left.operator).to.equal('+');
            expect(ast.left.left.value).to.equal(2);
            expect(ast.left.right.value).to.equal(3);
        });
        it('should handle power before multiplication', () => {
            const ast = parseExpression('2^3*4');
            expect(ast.operator).to.equal('*');
            expect(ast.right.value).to.equal(4);
            expect(ast.left.operator).to.equal('^');
            expect(ast.left.left.value).to.equal(2);
            expect(ast.left.right.value).to.equal(3);
        });
        it('should handle left-to-right for same precedence (multiplication/division)', () => {
            const ast = parseExpression('10/2*5');
            expect(ast.operator).to.equal('*');
            expect(ast.right.value).to.equal(5);
            expect(ast.left.operator).to.equal('/');
            expect(ast.left.left.value).to.equal(10);
            expect(ast.left.right.value).to.equal(2);
        });
        it('should handle left-to-right for same precedence (addition/subtraction)', () => {
            const ast = parseExpression('10-2+5');
            expect(ast.operator).to.equal('+');
            expect(ast.right.value).to.equal(5);
            expect(ast.left.operator).to.equal('-');
            expect(ast.left.left.value).to.equal(10);
            expect(ast.left.right.value).to.equal(2);
        });
    });
    describe('Unary Minus', () => {
        it('should parse a negative number', () => {
            const ast = parseExpression('-5');
            expect(ast.type).to.equal(NodeType.UnaryOperation);
            expect(ast.operator).to.equal('-');
            expect(ast.operand.value).to.equal(5);
        });
        it('should parse a negative variable', () => {
            const ast = parseExpression('-x');
            expect(ast.type).to.equal(NodeType.UnaryOperation);
            expect(ast.operator).to.equal('-');
            expect(ast.operand.name).to.equal('x');
        });
        it('should parse a negative expression in parentheses', () => {
            const ast = parseExpression('-(2+3)');
            expect(ast.type).to.equal(NodeType.UnaryOperation);
            expect(ast.operator).to.equal('-');
            expect(ast.operand.operator).to.equal('+');
        });
        it('should handle unary minus with power', () => {
            // -2^2 should be -(2^2) = -4, not (-2)^2 = 4
            const ast = parseExpression('-2^2');
            expect(ast.type).to.equal(NodeType.UnaryOperation);
            expect(ast.operator).to.equal('-');
            const operand = ast.operand;
            expect(operand.type).to.equal(NodeType.BinaryOperation);
            expect(operand.operator).to.equal('^');
            expect(operand.left.value).to.equal(2);
            expect(operand.right.value).to.equal(2);
        });
    });
    describe('Function Calls', () => {
        it('should parse sin(x)', () => {
            const ast = parseExpression('sin(x)');
            expect(ast.type).to.equal(NodeType.FunctionCall);
            expect(ast.functionName).to.equal('sin');
            expect(ast.arguments).to.have.lengthOf(1);
            expect(ast.arguments[0].type).to.equal(NodeType.Variable);
            expect(ast.arguments[0].name).to.equal('x');
        });
        it('should parse log(10)', () => {
            const ast = parseExpression('log(10)');
            expect(ast.type).to.equal(NodeType.FunctionCall);
            expect(ast.functionName).to.equal('log');
            expect(ast.arguments).to.have.lengthOf(1);
            expect(ast.arguments[0].type).to.equal(NodeType.Number);
            expect(ast.arguments[0].value).to.equal(10);
        });
        it('should parse ln(e)', () => {
            const ast = parseExpression('ln(e)');
            expect(ast.type).to.equal(NodeType.FunctionCall);
            expect(ast.functionName).to.equal('ln');
            expect(ast.arguments).to.have.lengthOf(1);
            expect(ast.arguments[0].type).to.equal(NodeType.Constant);
            expect(ast.arguments[0].name).to.equal('e');
        });
        it('should parse log(base, expr)', () => {
            const ast = parseExpression('log(2,8)');
            expect(ast.type).to.equal(NodeType.FunctionCall);
            expect(ast.functionName).to.equal('log');
            expect(ast.arguments).to.have.lengthOf(2);
            expect(ast.arguments[0].type).to.equal(NodeType.Number);
            expect(ast.arguments[0].value).to.equal(2);
            expect(ast.arguments[1].type).to.equal(NodeType.Number);
            expect(ast.arguments[1].value).to.equal(8);
        });
        it('should parse nested functions', () => {
            const ast = parseExpression('sin(cos(x))');
            expect(ast.functionName).to.equal('sin');
            const innerCall = ast.arguments[0];
            expect(innerCall.functionName).to.equal('cos');
            expect(innerCall.arguments[0].type).to.equal(NodeType.Variable);
        });
        it('should parse functions with expressions as arguments', () => {
            const ast = parseExpression('sin(2*x+3)');
            expect(ast.functionName).to.equal('sin');
            const arg = ast.arguments[0];
            expect(arg.operator).to.equal('+');
            expect(arg.left.operator).to.equal('*');
        });
    });
    describe('Constants', () => {
        it('should parse pi', () => {
            const ast = parseExpression('pi');
            expect(ast.type).to.equal(NodeType.Constant);
            expect(ast.name).to.equal('pi');
        });
        it('should parse e', () => {
            const ast = parseExpression('e');
            expect(ast.type).to.equal(NodeType.Constant);
            expect(ast.name).to.equal('e');
        });
    });
    describe('Complex Expressions', () => {
        it('should parse a complex expression with precedence and functions', () => {
            const ast = parseExpression('2*sin(x+pi)^3 - log(e, 5)');
            expect(ast.operator).to.equal('-');
            const left = ast.left;
            expect(left.operator).to.equal('*');
            expect(left.left.value).to.equal(2);
            const sinCall = left.right;
            expect(sinCall.operator).to.equal('^');
            expect(sinCall.right.value).to.equal(3);
            expect(sinCall.left.functionName).to.equal('sin');
            const right = ast.right;
            expect(right.functionName).to.equal('log');
            expect(right.arguments[0].name).to.equal('e');
            expect(right.arguments[1].value).to.equal(5);
        });
        it('should parse expression with multiple variable and constants', () => {
            const ast = parseExpression('alpha + beta * pi / e');
            expect(ast.operator).to.equal('+');
            expect(ast.left.name).to.equal('alpha');
            const right = ast.right;
            expect(right.operator).to.equal('/');
            expect(right.right.name).to.equal('e');
            const innerLeft = right.left;
            expect(innerLeft.operator).to.equal('*');
            expect(innerLeft.left.name).to.equal('beta');
            expect(innerLeft.right.name).to.equal('pi');
        });
    });
    describe('Error Handling', () => {
        it('should throw an error for mismatched parentheses (missing R)', () => {
            expect(() => parseExpression('(2+3')).to.throw('Syntax Error: Expected ) but found EOF');
        });
        it('should throw an error for mismatched parentheses (missing L)', () => {
            expect(() => parseExpression('2+3)')).to.throw('Syntax Error: Unexpected token type RPAREN at position 3');
        });
        it('should throw an error for empty expression', () => {
            expect(() => parseExpression('')).to.throw('Syntax Error: Unexpected EOF');
        });
        it('should throw an error for missing operand after operator', () => {
            expect(() => parseExpression('2+')).to.throw('Syntax Error: Expected expression but found EOF');
        });
        it('should throw an error for missing operator between numbers', () => {
            expect(() => parseExpression('2 3')).to.throw('Syntax Error: Unexpected token type NUMBER at position 2');
        });
        it('should throw an error for missing operator between number and variable', () => {
            expect(() => parseExpression('2x')).to.throw('Syntax Error: Unexpected token type VARIABLE at position 1');
        });
        it('should throw an error for invalid function call (empty arguments)', () => {
            expect(() => parseExpression('sin()')).to.throw('Syntax Error: Expected expression but found RPAREN');
        });
        it('should throw an error for invalid function call (too many arguments for single-arg func)', () => {
            expect(() => parseExpression('sin(x,y)')).to.throw('Syntax Error: Unexpected token type COMMA at position 5');
        });
        it('should throw an error for invalid function call (missing comma for multi-arg func)', () => {
            expect(() => parseExpression('log(2 8)')).to.throw('Syntax Error: Expected COMMA but found NUMBER');
        });
        it('should throw an error for invalid function call (missing second arg for multi-arg func)', () => {
            expect(() => parseExpression('log(2,)')).to.throw('Syntax Error: Expected expression but found RPAREN');
        });
        it('should throw an error for trailing operator', () => {
            expect(() => parseExpression('2+3*')).to.throw('Syntax Error: Expected expression but found EOF');
        });
        it('should throw an error for unexpected token at end', () => {
            expect(() => parseExpression('2+3x')).to.throw('Syntax Error: Unexpected token type VARIABLE at position 3');
        });
    });
});
