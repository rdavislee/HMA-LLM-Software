import { expect } from "chai";
import { differentiate } from "./differentiate.js";
import { AstNode, NodeType, NumberNode, VariableNode, BinaryOpNode, UnaryOpNode, CallNode, ConstantNode } from "../types/ast.js";
import { simplify } from "./simplify.js"; // Added simplify import as differentiate should return simplified AST

// Helper functions for building AST nodes
function num(value: number): NumberNode {
    return { type: NodeType.Number, value };
}

function variable(name: string): VariableNode {
    return { type: NodeType.Variable, name };
}

function constant(name: 'pi' | 'e'): ConstantNode {
    return { type: NodeType.Constant, name };
}

function plus(left: AstNode, right: AstNode): BinaryOpNode {
    return { type: NodeType.BinaryOperation, operator: '+', left, right };
}

function minus(left: AstNode, right: AstNode): BinaryOpNode {
    return { type: NodeType.BinaryOperation, operator: '-', left, right };
}

function multiply(left: AstNode, right: AstNode): BinaryOpNode {
    return { type: NodeType.BinaryOperation, operator: '*', left, right };
}

function divide(left: AstNode, right: AstNode): BinaryOpNode {
    return { type: NodeType.BinaryOperation, operator: '/', left, right };
}

function power(base: AstNode, exponent: AstNode): BinaryOpNode {
    return { type: NodeType.BinaryOperation, operator: '^', left: base, right: exponent };
}

function negate(operand: AstNode): UnaryOpNode {
    return { type: NodeType.UnaryOperation, operator: '-', operand };
}

function call(functionName: string, args: AstNode[]): CallNode {
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

    // Power Rule: d/dx (a^x) = a^x * ln(a)
    it("should apply the power rule for a^x (constant base, variable exponent)", () => {
        const expr = power(num(2), variable("x")); // 2^x
        const expected = multiply(power(num(2), variable("x")), call("ln", [num(2)])); // 2^x * ln(2)
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should apply the power rule for e^x", () => {
        const expr = power(constant("e"), variable("x")); // e^x
        const expected = power(constant("e"), variable("x")); // e^x (since ln(e) = 1)
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    // Sum Rule: d/dx (u + v) = u' + v'
    it("should apply the sum rule for addition and simplify", () => {
        const expr = plus(variable("x"), num(5)); // x + 5
        const expected = num(1); // 1 + 0 simplifies to 1
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should apply the sum rule for subtraction and simplify", () => {
        const expr = minus(power(variable("x"), num(2)), variable("x")); // x^2 - x
        const expected = minus(multiply(num(2), variable("x")), num(1)); // 2*x - 1
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    // Product Rule: d/dx (u * v) = u'v + uv'
    it("should apply the product rule and simplify", () => {
        const expr = multiply(variable("x"), power(variable("x"), num(2))); // x * x^2
        // u = x, v = x^2
        // u' = 1, v' = 2*x
        // Derivative: (1 * x^2) + (x * 2*x) => x^2 + 2*x^2 => 3*x^2
        const expected = multiply(num(3), power(variable("x"), num(2)));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should apply the product rule with constant multiple and simplify", () => {
        const expr = multiply(num(3), variable("x")); // 3*x
        // u = 3, v = x
        // u' = 0, v' = 1
        // Derivative: (0 * x) + (3 * 1) => 0 + 3 => 3
        const expected = num(3);
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should apply the product rule with a function term (x*sin(x))", () => {
        const expr = multiply(variable("x"), call("sin", [variable("x")])); // x*sin(x)
        // u = x, v = sin(x)
        // u' = 1, v' = cos(x)
        // Derivative: (1 * sin(x)) + (x * cos(x)) => sin(x) + x*cos(x)
        const expected = plus(call("sin", [variable("x")]), multiply(variable("x"), call("cos", [variable("x")])));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    // Quotient Rule: d/dx (u / v) = (u'v - uv') / v^2
    it("should apply the quotient rule for u/v and simplify", () => {
        const expr = divide(variable("x"), power(variable("x"), num(2))); // x / x^2
        // u = x, v = x^2
        // u' = 1, v' = 2*x
        // Derivative: ((1 * x^2) - (x * 2*x)) / (x^2)^2 => (x^2 - 2*x^2) / x^4 => -x^2 / x^4 => -1/x^2
        const expected = divide(negate(num(1)), power(variable("x"), num(2)));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    // Chain Rule: d/dx (f(g(x))) = f'(g(x)) * g'(x)
    it("should apply the chain rule for sin(x^2) and simplify", () => {
        const inner = power(variable("x"), num(2)); // x^2
        const expr = call("sin", [inner]); // sin(x^2)
        // d/dx(sin(u)) = cos(u) * du/dx
        // u = x^2, du/dx = 2*x
        // Derivative: cos(x^2) * 2*x
        const expected = multiply(
            call("cos", [power(variable("x"), num(2))]),
            multiply(num(2), variable("x"))
        );
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should apply the chain rule for ln(2*x) and simplify", () => {
        const inner = multiply(num(2), variable("x")); // 2*x
        const expr = call("ln", [inner]); // ln(2*x)
        // d/dx(ln(u)) = (1/u) * du/dx
        // u = 2*x, du/dx = 2
        // Derivative: (1/(2*x)) * 2 => 1/x
        const expected = divide(num(1), variable("x"));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should apply the chain rule for nested functions (sin(cos(x)))", () => {
        const inner = call("cos", [variable("x")]); // cos(x)
        const expr = call("sin", [inner]); // sin(cos(x))
        // d/dx(sin(u)) = cos(u) * du/dx
        // u = cos(x), du/dx = -sin(x)
        // Derivative: cos(cos(x)) * (-sin(x))
        const expected = multiply(call("cos", [call("cos", [variable("x")])]), negate(call("sin", [variable("x")])));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should apply the chain rule for ln(x^2) and simplify", () => {
        const inner = power(variable("x"), num(2)); // x^2
        const expr = call("ln", [inner]); // ln(x^2)
        // d/dx(ln(u)) = (1/u) * du/dx
        // u = x^2, du/dx = 2*x
        // Derivative: (1/x^2) * 2*x => 2*x / x^2 => 2/x
        const expected = divide(num(2), variable("x"));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });


    // Unary Negation: d/dx (-u) = -u'
    it("should differentiate a negated expression and simplify", () => {
        const expr = negate(power(variable("x"), num(2))); // -(x^2)
        // Expected: -(2*x)
        const expected = negate(multiply(num(2), variable("x")));
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
    it("should differentiate a complex expression (sum, product, power) and simplify", () => {
        // d/dx (x^2 + 3*x + 5)
        const expr = plus(
            plus(power(variable("x"), num(2)), multiply(num(3), variable("x"))),
            num(5)
        );
        // Expected: d/dx(x^2) + d/dx(3*x) + d/dx(5)
        //           (2*x) + (3*1) + 0
        //           (2*x) + 3
        const expected = plus(multiply(num(2), variable("x")), num(3));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should differentiate (x+1)^2 using chain and power rule and simplify", () => {
        // d/dx ((x+1)^2)
        const inner = plus(variable("x"), num(1));
        const expr = power(inner, num(2));
        // u = x+1, du/dx = 1
        // Derivative: 2 * (x+1)^1 * 1 => 2 * (x+1)
        const expected = multiply(num(2), plus(variable("x"), num(1)));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should throw an error if differentiation variable is empty", () => {
        const expr = variable("x");
        expect(() => differentiate(expr, "")).to.throw("Differentiation variable cannot be empty.");
    });

    it("should throw an error for unimplemented function arcsin(x)", () => {
        const expr = call("arcsin", [variable("x")]);
        expect(() => differentiate(expr, "x")).to.throw("Differentiation for function 'arcsin' not implemented.");
    });

    // Test for expressions not involving the differentiation variable
    it("should differentiate an expression with a variable not being differentiated to 0", () => {
        const expr = plus(variable("y"), power(variable("y"), num(2))); // y + y^2
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(num(0));
    });

    it("should differentiate a mixed expression where only some parts contain the variable", () => {
        // d/dx (x^2 + y + 5)
        const expr = plus(plus(power(variable("x"), num(2)), variable("y")), num(5));
        // Expected: d/dx(x^2) + d/dx(y) + d/dx(5) => 2*x + 0 + 0 => 2*x
        const expected = multiply(num(2), variable("x"));
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should handle division by a constant and simplify", () => {
        // d/dx (x / 2) = d/dx (0.5 * x) = 0.5
        const expr = divide(variable("x"), num(2));
        const expected = num(0.5);
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });

    it("should handle multiplication by a variable not being differentiated", () => {
        // d/dx (y * x) = y * 1 = y
        const expr = multiply(variable("y"), variable("x"));
        const expected = variable("y");
        const result = differentiate(expr, "x");
        expect(result).to.deep.equal(expected);
    });
});
