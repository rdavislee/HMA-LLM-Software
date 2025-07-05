import { expect } from "chai";
import { simplify } from "./simplify.js";
import { NodeType } from "../types/ast.js";
// Helper functions to create AST nodes for tests
function num(value) {
    return { type: NodeType.Number, value };
}
function variable(name) {
    return { type: NodeType.Variable, name };
}
function binaryOp(operator, left, right) {
    return { type: NodeType.BinaryOperation, operator, left, right };
}
function unaryOp(operator, operand) {
    return { type: NodeType.UnaryOperation, operator, operand };
}
function call(functionName, args) {
    return { type: NodeType.FunctionCall, functionName, arguments: args };
}
describe("simplify", () => {
    describe("Constant Folding", () => {
        it("should fold addition of numbers", () => {
            const input = binaryOp('+', num(2), num(3));
            const expected = num(5);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should fold subtraction of numbers", () => {
            const input = binaryOp('-', num(5), num(2));
            const expected = num(3);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should fold multiplication of numbers", () => {
            const input = binaryOp('*', num(4), num(2));
            const expected = num(8);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should fold division of numbers", () => {
            const input = binaryOp('/', num(10), num(2));
            const expected = num(5);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should fold exponentiation of numbers", () => {
            const input = binaryOp('^', num(2), num(3));
            const expected = num(8);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should fold multiplication by zero (left)", () => {
            const input = binaryOp('*', num(0), variable('x'));
            const expected = num(0);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should fold multiplication by zero (right)", () => {
            const input = binaryOp('*', variable('x'), num(0));
            const expected = num(0);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should fold division of zero by non-zero", () => {
            const input = binaryOp('/', num(0), variable('x'));
            const expected = num(0);
            expect(simplify(input)).to.deep.equal(expected);
        });
    });
    describe("Identity Rules", () => {
        it("should simplify x + 0 to x", () => {
            const input = binaryOp('+', variable('x'), num(0));
            const expected = variable('x');
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify 0 + x to x", () => {
            const input = binaryOp('+', num(0), variable('x'));
            const expected = variable('x');
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify x - 0 to x", () => {
            const input = binaryOp('-', variable('x'), num(0));
            const expected = variable('x');
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify x * 1 to x", () => {
            const input = binaryOp('*', variable('x'), num(1));
            const expected = variable('x');
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify 1 * x to x", () => {
            const input = binaryOp('*', num(1), variable('x'));
            const expected = variable('x');
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify x / 1 to x", () => {
            const input = binaryOp('/', variable('x'), num(1));
            const expected = variable('x');
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify x ^ 1 to x", () => {
            const input = binaryOp('^', variable('x'), num(1));
            const expected = variable('x');
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify 1 ^ x to 1", () => {
            const input = binaryOp('^', num(1), variable('x'));
            const expected = num(1);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify x ^ 0 to 1 (for non-zero x)", () => {
            const input = binaryOp('^', variable('x'), num(0));
            const expected = num(1);
            expect(simplify(input)).to.deep.equal(expected);
        });
    });
    describe("Combining Like Terms", () => {
        it("should combine x + x to 2*x", () => {
            const input = binaryOp('+', variable('x'), variable('x'));
            const expected = binaryOp('*', num(2), variable('x'));
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should combine x + 2*x to 3*x", () => {
            const input = binaryOp('+', variable('x'), binaryOp('*', num(2), variable('x')));
            const expected = binaryOp('*', num(3), variable('x'));
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should combine 2*x + 3*x to 5*x", () => {
            const input = binaryOp('+', binaryOp('*', num(2), variable('x')), binaryOp('*', num(3), variable('x')));
            const expected = binaryOp('*', num(5), variable('x'));
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify x - x to 0", () => {
            const input = binaryOp('-', variable('x'), variable('x'));
            const expected = num(0);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify 2*x - x to x", () => {
            const input = binaryOp('-', binaryOp('*', num(2), variable('x')), variable('x'));
            const expected = variable('x');
            expect(simplify(input)).to.deep.equal(expected);
        });
    });
    describe("Exponent Rules", () => {
        it("should simplify x^a * x^b to x^(a+b)", () => {
            const input = binaryOp('*', binaryOp('^', variable('x'), num(2)), binaryOp('^', variable('x'), num(3)));
            const expected = binaryOp('^', variable('x'), num(5));
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify (x^a)^b to x^(a*b)", () => {
            const input = binaryOp('^', binaryOp('^', variable('x'), num(2)), num(3));
            const expected = binaryOp('^', variable('x'), num(6));
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify x^a / x^b to x^(a-b)", () => {
            const input = binaryOp('/', binaryOp('^', variable('x'), num(5)), binaryOp('^', variable('x'), num(2)));
            const expected = binaryOp('^', variable('x'), num(3));
            expect(simplify(input)).to.deep.equal(expected);
        });
    });
    describe("Trigonometric Identities", () => {
        it("should simplify sin(x)^2 + cos(x)^2 to 1", () => {
            const sinSq = binaryOp('^', call('sin', [variable('x')]), num(2));
            const cosSq = binaryOp('^', call('cos', [variable('x')]), num(2));
            const input = binaryOp('+', sinSq, cosSq);
            const expected = num(1);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify cos(x)^2 + sin(x)^2 to 1", () => {
            const sinSq = binaryOp('^', call('sin', [variable('x')]), num(2));
            const cosSq = binaryOp('^', call('cos', [variable('x')]), num(2));
            const input = binaryOp('+', cosSq, sinSq);
            const expected = num(1);
            expect(simplify(input)).to.deep.equal(expected);
        });
    });
    describe("Other Simplifications", () => {
        it("should simplify -(-x) to x", () => {
            const input = unaryOp('-', unaryOp('-', variable('x')));
            const expected = variable('x');
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify x / x to 1 (for non-zero x)", () => {
            const input = binaryOp('/', variable('x'), variable('x'));
            const expected = num(1);
            expect(simplify(input)).to.deep.equal(expected);
        });
    });
    describe("Nested Simplifications (assuming recursive simplification)", () => {
        it("should simplify nested constant folding", () => {
            const input = binaryOp('+', num(1), binaryOp('*', num(2), num(3))); // 1 + (2 * 3) -> 1 + 6 -> 7
            const expected = num(7);
            expect(simplify(input)).to.deep.equal(expected);
        });
        it("should simplify expressions with multiple rules applied", () => {
            // (x + 0) * 1 + sin(y)^2 + cos(y)^2
            const sinYSq = binaryOp('^', call('sin', [variable('y')]), num(2));
            const cosYSq = binaryOp('^', call('cos', [variable('y')]), num(2));
            const input = binaryOp('+', binaryOp('*', binaryOp('+', variable('x'), num(0)), num(1)), binaryOp('+', sinYSq, cosYSq));
            // Expected: x + 1
            const expected = binaryOp('+', variable('x'), num(1));
            expect(simplify(input)).to.deep.equal(expected);
        });
    });
});
