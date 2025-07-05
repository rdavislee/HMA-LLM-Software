import { expect } from "chai";
import { evaluate } from "../operations/evaluate.js";
import { NodeType } from "../types/ast.js";
// Helper functions to create AST nodes for cleaner test cases
const num = (value) => ({ type: NodeType.Number, value });
const variable = (name) => ({ type: NodeType.Variable, name });
const constant = (name) => ({ type: NodeType.Constant, name });
const binary = (operator, left, right) => ({
    type: NodeType.BinaryOperation,
    operator,
    left,
    right,
});
const unary = (operator, operand) => ({
    type: NodeType.UnaryOperation,
    operator,
    operand,
});
const call = (functionName, args) => ({
    type: NodeType.FunctionCall,
    functionName,
    arguments: args,
});
describe("evaluate", () => {
    let variables;
    beforeEach(() => {
        variables = new Map();
    });
    // Test NumberNode
    it("should evaluate a NumberNode correctly", () => {
        const node = num(42);
        expect(evaluate(node, variables)).to.equal(42);
    });
    // Test VariableNode
    it("should evaluate a VariableNode with substitution", () => {
        variables.set("x", 10);
        const node = variable("x");
        expect(evaluate(node, variables)).to.equal(10);
    });
    it("should throw an error for an undefined VariableNode", () => {
        const node = variable("y");
        expect(() => evaluate(node, variables)).to.throw("Variable 'y' not defined in the context.");
    });
    // Test ConstantNode
    it("should evaluate 'pi' constant correctly", () => {
        const node = constant("pi");
        expect(evaluate(node, variables)).to.be.closeTo(Math.PI, 0.0001);
    });
    it("should evaluate 'e' constant correctly", () => {
        const node = constant("e");
        expect(evaluate(node, variables)).to.be.closeTo(Math.E, 0.0001);
    });
    // Test BinaryOpNode
    describe("Binary Operations", () => {
        it("should perform addition correctly", () => {
            const node = binary("+", num(5), num(3));
            expect(evaluate(node, variables)).to.equal(8);
        });
        it("should perform subtraction correctly", () => {
            const node = binary("-", num(10), num(4));
            expect(evaluate(node, variables)).to.equal(6);
        });
        it("should perform multiplication correctly", () => {
            const node = binary("*", num(6), num(7));
            expect(evaluate(node, variables)).to.equal(42);
        });
        it("should perform division correctly", () => {
            const node = binary("/", num(10), num(2));
            expect(evaluate(node, variables)).to.equal(5);
        });
        it("should throw an error for division by zero", () => {
            const node = binary("/", num(10), num(0));
            expect(() => evaluate(node, variables)).to.throw("Division by zero.");
        });
        it("should perform exponentiation correctly", () => {
            const node = binary("^", num(2), num(3));
            expect(evaluate(node, variables)).to.equal(8);
        });
        it("should handle nested binary operations", () => {
            // (5 + 3) * 2
            const node = binary("*", binary("+", num(5), num(3)), num(2));
            expect(evaluate(node, variables)).to.equal(16);
        });
        it("should handle variables in binary operations", () => {
            variables.set("a", 10);
            variables.set("b", 2);
            // a / b + 5
            const node = binary("+", binary("/", variable("a"), variable("b")), num(5));
            expect(evaluate(node, variables)).to.equal(10);
        });
    });
    // Test UnaryOpNode
    describe("Unary Operations", () => {
        it("should perform negation correctly", () => {
            const node = unary("-", num(5));
            expect(evaluate(node, variables)).to.equal(-5);
        });
        it("should perform nested negation correctly", () => {
            // -(-5)
            const node = unary("-", unary("-", num(5)));
            expect(evaluate(node, variables)).to.equal(5);
        });
        it("should negate a variable", () => {
            variables.set("x", 10);
            const node = unary("-", variable("x"));
            expect(evaluate(node, variables)).to.equal(-10);
        });
    });
    // Test FunctionCall
    describe("Function Calls", () => {
        it("should evaluate sin(0) correctly", () => {
            const node = call("sin", [num(0)]);
            expect(evaluate(node, variables)).to.be.closeTo(0, 0.0001);
        });
        it("should evaluate cos(pi) correctly", () => {
            const node = call("cos", [constant("pi")]);
            expect(evaluate(node, variables)).to.be.closeTo(-1, 0.0001);
        });
        it("should evaluate tan(pi/4) correctly", () => {
            const node = call("tan", [binary("/", constant("pi"), num(4))]);
            expect(evaluate(node, variables)).to.be.closeTo(1, 0.0001);
        });
        it("should evaluate ln(e) correctly", () => {
            const node = call("ln", [constant("e")]);
            expect(evaluate(node, variables)).to.be.closeTo(1, 0.0001);
        });
        it("should evaluate log(100) correctly (base 10)", () => {
            const node = call("log", [num(100)]);
            expect(evaluate(node, variables)).to.be.closeTo(2, 0.0001);
        });
        it("should evaluate log(base, expr) correctly", () => {
            // log(2, 8) = 3
            const node = call("log", [num(2), num(8)]);
            expect(evaluate(node, variables)).to.be.closeTo(3, 0.0001);
        });
        it("should evaluate sqrt(9) correctly", () => {
            const node = call("sqrt", [num(9)]);
            expect(evaluate(node, variables)).to.equal(3);
        });
        it("should throw an error for sqrt of negative number", () => {
            const node = call("sqrt", [num(-1)]);
            expect(() => evaluate(node, variables)).to.throw("Invalid argument for sqrt: must be non-negative.");
        });
        it("should evaluate abs(-5) correctly", () => {
            const node = call("abs", [num(-5)]);
            expect(evaluate(node, variables)).to.equal(5);
        });
        it("should throw an error for unsupported function", () => {
            const node = call("unknownFunc", [num(5)]);
            expect(() => evaluate(node, variables)).to.throw("Unsupported function: 'unknownFunc'.");
        });
        it("should throw an error for incorrect number of arguments (e.g., sin with 2 args)", () => {
            const node = call("sin", [num(1), num(2)]);
            expect(() => evaluate(node, variables)).to.throw("Function 'sin' expects 1 argument(s), but received 2.");
        });
        it("should throw an error for log with too many arguments", () => {
            const node = call("log", [num(10), num(2), num(3)]);
            expect(() => evaluate(node, variables)).to.throw("Function 'log' expects 1 or 2 argument(s), but received 3.");
        });
        it("should throw an error for log with too few arguments (0 args)", () => {
            const node = call("log", []);
            expect(() => evaluate(node, variables)).to.throw("Function 'log' expects 1 or 2 argument(s), but received 0.");
        });
        it("should handle nested function calls", () => {
            // sin(pi / 2)
            const node = call("sin", [binary("/", constant("pi"), num(2))]);
            expect(evaluate(node, variables)).to.be.closeTo(1, 0.0001);
        });
        it("should handle function calls with variables", () => {
            variables.set("angle", Math.PI / 6); // 30 degrees
            const node = call("sin", [variable("angle")]);
            expect(evaluate(node, variables)).to.be.closeTo(0.5, 0.0001);
        });
    });
    // Complex expressions
    it("should evaluate a complex expression with variables and functions", () => {
        variables.set("x", 2);
        variables.set("y", 3);
        // (x + y) * sin(pi / 2) + log(100)
        const expression = binary("+", binary("*", binary("+", variable("x"), variable("y")), call("sin", [binary("/", constant("pi"), num(2))])), call("log", [num(100)]));
        // (2 + 3) * sin(pi/2) + log(100) = 5 * 1 + 2 = 7
        expect(evaluate(expression, variables)).to.be.closeTo(7, 0.0001);
    });
    // Edge case: empty variables map when not needed
    it("should evaluate an expression without variables if no variables are present", () => {
        const node = binary("+", num(10), num(5));
        expect(evaluate(node, new Map())).to.equal(15);
    });
    // Test unsupported node type (should throw)
    it("should throw an error for an unsupported AST node type", () => {
        const unknownNode = { type: 'UnknownType' }; // Cast to simulate unknown type
        expect(() => evaluate(unknownNode, variables)).to.throw("Unsupported AST node type: UnknownType");
    });
});
