import { expect } from "chai";
import { differentiate } from "./differentiate.js";
import { NodeType } from "../types/ast.js";
// Helper functions for building AST nodes
function num(value) {
    return { type: NodeType.Number, value };
}
function variable(name) {
    return { type: NodeType.Variable, name };
}
function constant(name) {
    return { type: NodeType.Constant, name };
}
function plus(left, right) {
    return { type: NodeType.BinaryOperation, operator: '+', left, right };
}
function minus(left, right) {
    return { type: NodeType.BinaryOperation, operator: '-', left, right };
}
function multiply(left, right) {
    return { type: NodeType.BinaryOperation, operator: '*', left, right };
}
function divide(left, right) {
    return { type: NodeType.BinaryOperation, operator: '/', left, right };
}
function power(base, exponent) {
    return { type: NodeType.BinaryOperation, operator: '^', left: base, right: exponent };
}
function negate(operand) {
    return { type: NodeType.UnaryOperation, operator: '-', operand };
}
function call(functionName, args) {
    return { type: NodeType.FunctionCall, functionName, arguments: args };
}
describe("differentiate", () => {
    // Test cases for basic differentiation rules
    it("should differentiate a constant to 0", () => {
        const expr = num(5);
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(num(0));
    });
    it("should differentiate a variable with respect to itself to 1", () => {
        const expr = variable("x");
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(num(1));
    });
    it("should differentiate a variable with respect to another variable to 0", () => {
        const expr = variable("y");
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(num(0));
    });
    it("should differentiate a constant 'pi' to 0", () => {
        const expr = constant("pi");
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(num(0));
    });
    it("should differentiate a constant 'e' to 0", () => {
        const expr = constant("e");
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(num(0));
    });
    // Power Rule: d/dx (x^n) = n*x^(n-1)
    it("should apply the power rule for x^n", () => {
        const expr = power(variable("x"), num(3)); // x^3
        const expected = multiply(num(3), power(variable("x"), num(2))); // 3*x^2
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should apply the power rule for x^1 (variable only)", () => {
        const expr = variable("x"); // x^1
        const expected = num(1); // 1
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should handle power rule where base is not the differentiation variable", () => {
        const expr = power(variable("y"), num(2)); // y^2
        const expected = num(0); // 0 (y treated as constant wrt x)
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    // Sum Rule: d/dx (u + v) = u' + v'
    it("should apply the sum rule for addition", () => {
        const expr = plus(variable("x"), num(5)); // x + 5
        const expected = plus(num(1), num(0)); // 1 + 0
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should apply the sum rule for subtraction", () => {
        const expr = minus(power(variable("x"), num(2)), variable("x")); // x^2 - x
        const expected = minus(multiply(num(2), power(variable("x"), num(1))), num(1)); // 2*x^1 - 1
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    // Product Rule: d/dx (u * v) = u'v + uv'
    it("should apply the product rule", () => {
        const expr = multiply(variable("x"), power(variable("x"), num(2))); // x * x^2
        // u = x, v = x^2
        // u' = 1, v' = 2*x
        // Expected: (1 * x^2) + (x * 2*x) => x^2 + 2*x^2
        const expected = plus(multiply(num(1), power(variable("x"), num(2))), multiply(variable("x"), multiply(num(2), power(variable("x"), num(1)))));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should apply the product rule with constant multiple", () => {
        const expr = multiply(num(3), variable("x")); // 3*x
        // u = 3, v = x
        // u' = 0, v' = 1
        // Expected: (0 * x) + (3 * 1) => 0 + 3 => 3
        const expected = plus(multiply(num(0), variable("x")), multiply(num(3), num(1)));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    // Quotient Rule: d/dx (u / v) = (u'v - uv') / v^2 (derived from product and chain for v^-1)
    // Note: The differentiate function may produce a more complex AST before simplification.
    it("should apply the quotient rule for u/v", () => {
        const expr = divide(variable("x"), power(variable("x"), num(2))); // x / x^2
        // u = x, v = x^2
        // u' = 1, v' = 2*x
        // Expected: ((1 * x^2) - (x * 2*x)) / (x^2)^2 => (x^2 - 2*x^2) / x^4
        const expected = divide(minus(multiply(num(1), power(variable("x"), num(2))), multiply(variable("x"), multiply(num(2), power(variable("x"), num(1))))), power(power(variable("x"), num(2)), num(2)));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    // Chain Rule: d/dx (f(g(x))) = f'(g(x)) * g'(x)
    it("should apply the chain rule for sin(x^2)", () => {
        const inner = power(variable("x"), num(2)); // x^2
        const expr = call("sin", [inner]); // sin(x^2)
        // d/dx(sin(u)) = cos(u) * du/dx
        // u = x^2, du/dx = 2*x
        // Expected: cos(x^2) * 2*x
        const expected = multiply(call("cos", [power(variable("x"), num(2))]), multiply(num(2), power(variable("x"), num(1))));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should apply the chain rule for ln(2*x)", () => {
        const inner = multiply(num(2), variable("x")); // 2*x
        const expr = call("ln", [inner]); // ln(2*x)
        // d/dx(ln(u)) = (1/u) * du/dx
        // u = 2*x, du/dx = 2
        // Expected: (1/(2*x)) * 2
        const expected = multiply(divide(num(1), multiply(num(2), variable("x"))), num(2));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    // Unary Negation: d/dx (-u) = -u'
    it("should differentiate a negated expression", () => {
        const expr = negate(power(variable("x"), num(2))); // -(x^2)
        // Expected: -(2*x)
        const expected = negate(multiply(num(2), power(variable("x"), num(1))));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    // Trigonometric functions
    it("should differentiate sin(x) to cos(x)", () => {
        const expr = call("sin", [variable("x")]);
        const expected = call("cos", [variable("x")]);
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should differentiate cos(x) to -sin(x)", () => {
        const expr = call("cos", [variable("x")]);
        const expected = negate(call("sin", [variable("x")]));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should differentiate tan(x) to sec(x)^2", () => {
        const expr = call("tan", [variable("x")]);
        const expected = power(call("sec", [variable("x")]), num(2));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    // Logarithmic functions
    it("should differentiate ln(x) to 1/x", () => {
        const expr = call("ln", [variable("x")]);
        const expected = divide(num(1), variable("x"));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should differentiate log(x) to 1/(x * ln(10))", () => {
        const expr = call("log", [variable("x")]);
        const expected = divide(num(1), multiply(variable("x"), call("ln", [num(10)])));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    // Nested expressions and combinations
    it("should differentiate a complex expression (sum, product, power)", () => {
        // d/dx (x^2 + 3*x + 5)
        const expr = plus(plus(power(variable("x"), num(2)), multiply(num(3), variable("x"))), num(5));
        // Expected: d/dx(x^2) + d/dx(3*x) + d/dx(5)
        //           (2*x) + (3*1) + 0
        //           (2*x) + 3
        const dx_x2 = multiply(num(2), power(variable("x"), num(1)));
        const dx_3x = plus(multiply(num(0), variable("x")), multiply(num(3), num(1)));
        const dx_5 = num(0);
        const expected = plus(plus(dx_x2, dx_3x), dx_5);
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should differentiate (x+1)^2 using chain and power rule", () => {
        // d/dx ((x+1)^2)
        const inner = plus(variable("x"), num(1));
        const expr = power(inner, num(2));
        // u = x+1, du/dx = 1
        // Expected: 2 * (x+1)^1 * 1
        const expected = multiply(num(2), power(plus(variable("x"), num(1)), num(1)));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
    it("should throw an error for unimplemented node types or functions", () => {
        // This test verifies the initial state or missing implementations
        const expr = variable("x"); // This will pass the initial error
        expect(() => differentiate(expr, "x")).to.throw("Differentiation not yet implemented.");
        // Example for future unimplemented functions (if any)
        // const unknownFunction = call("unknownFunc", [variable("x")]);
        // expect(() => differentiate(unknownFunction, "x")).to.throw("Unknown function for differentiation: unknownFunc");
    });
    it("should throw an error if differentiation variable is empty", () => {
        const expr = variable("x");
        expect(() => differentiate(expr, "")).to.throw("Differentiation variable cannot be empty.");
    });
});
