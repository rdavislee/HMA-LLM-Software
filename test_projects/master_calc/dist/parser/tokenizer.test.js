import { expect } from "chai";
import { tokenize } from "./tokenizer.js";
import { TokenType } from "../types/tokens.js";
describe("Tokenizer", () => {
    // Helper function to create expected tokens easily
    const createToken = (type, value, position) => ({
        type,
        value,
        position,
    });
    it("should tokenize an empty string", () => {
        expect(tokenize("")).to.deep.equal([]);
    });
    it("should tokenize a string with only whitespace", () => {
        expect(tokenize("   \t\n")).to.deep.equal([]);
    });
    describe("Numbers", () => {
        it("should tokenize integer numbers", () => {
            expect(tokenize("123")).to.deep.equal([createToken(TokenType.NUMBER, "123", 0)]);
        });
        it("should tokenize decimal numbers", () => {
            expect(tokenize("1.23")).to.deep.equal([createToken(TokenType.NUMBER, "1.23", 0)]);
        });
        it("should tokenize numbers starting with a decimal point (e.g., 0.5)", () => {
            expect(tokenize("0.5")).to.deep.equal([createToken(TokenType.NUMBER, "0.5", 0)]);
        });
        it("should tokenize numbers starting with a decimal point (e.g., .5)", () => {
            expect(tokenize(".5")).to.deep.equal([createToken(TokenType.NUMBER, ".5", 0)]);
        });
        it("should tokenize numbers ending with a decimal point (e.g., 5.)", () => {
            expect(tokenize("5.")).to.deep.equal([createToken(TokenType.NUMBER, "5.", 0)]);
        });
        it("should tokenize multiple numbers separated by spaces", () => {
            expect(tokenize("1 2.3 4")).to.deep.equal([
                createToken(TokenType.NUMBER, "1", 0),
                createToken(TokenType.NUMBER, "2.3", 2),
                createToken(TokenType.NUMBER, "4", 6),
            ]);
        });
        it("should tokenize negative integer numbers (as MINUS then NUMBER)", () => {
            expect(tokenize("-123")).to.deep.equal([
                createToken(TokenType.MINUS, "-", 0),
                createToken(TokenType.NUMBER, "123", 1),
            ]);
        });
        it("should tokenize negative decimal numbers (as MINUS then NUMBER)", () => {
            expect(tokenize("-1.23")).to.deep.equal([
                createToken(TokenType.MINUS, "-", 0),
                createToken(TokenType.NUMBER, "1.23", 1),
            ]);
        });
        it("should tokenize numbers with leading zeros", () => {
            expect(tokenize("007")).to.deep.equal([createToken(TokenType.NUMBER, "007", 0)]);
        });
    });
    describe("Variables", () => {
        it("should tokenize single-character variables", () => {
            expect(tokenize("x")).to.deep.equal([createToken(TokenType.VARIABLE, "x", 0)]);
        });
        it("should tokenize multi-character variables", () => {
            expect(tokenize("alpha")).to.deep.equal([createToken(TokenType.VARIABLE, "alpha", 0)]);
        });
        it("should tokenize variables that contain numbers (e.g., x1, var2)", () => {
            expect(tokenize("x1")).to.deep.equal([createToken(TokenType.VARIABLE, "x1", 0)]);
            expect(tokenize("var2")).to.deep.equal([createToken(TokenType.VARIABLE, "var2", 0)]);
        });
        it("should tokenize multiple variables", () => {
            expect(tokenize("x y z")).to.deep.equal([
                createToken(TokenType.VARIABLE, "x", 0),
                createToken(TokenType.VARIABLE, "y", 2),
                createToken(TokenType.VARIABLE, "z", 4),
            ]);
        });
        it("should tokenize unary minus with a variable", () => {
            expect(tokenize("-x")).to.deep.equal([
                createToken(TokenType.MINUS, "-", 0),
                createToken(TokenType.VARIABLE, "x", 1),
            ]);
        });
        it("should tokenize unary minus with a constant", () => {
            expect(tokenize("-pi")).to.deep.equal([
                createToken(TokenType.MINUS, "-", 0),
                createToken(TokenType.CONSTANT, "pi", 1),
            ]);
        });
    });
    describe("Operators", () => {
        it("should tokenize PLUS operator", () => {
            expect(tokenize("+")).to.deep.equal([createToken(TokenType.PLUS, "+", 0)]);
        });
        it("should tokenize MINUS operator", () => {
            expect(tokenize("-")).to.deep.equal([createToken(TokenType.MINUS, "-", 0)]);
        });
        it("should tokenize MULTIPLY operator", () => {
            expect(tokenize("*")).to.deep.equal([createToken(TokenType.MULTIPLY, "*", 0)]);
        });
        it("should tokenize DIVIDE operator", () => {
            expect(tokenize("/")).to.deep.equal([createToken(TokenType.DIVIDE, "/", 0)]);
        });
        it("should tokenize POWER operator", () => {
            expect(tokenize("^")).to.deep.equal([createToken(TokenType.POWER, "^", 0)]);
        });
        it("should tokenize all operators consecutively", () => {
            expect(tokenize("+-*/^")).to.deep.equal([
                createToken(TokenType.PLUS, "+", 0),
                createToken(TokenType.MINUS, "-", 1),
                createToken(TokenType.MULTIPLY, "*", 2),
                createToken(TokenType.DIVIDE, "/", 3),
                createToken(TokenType.POWER, "^", 4),
            ]);
        });
    });
    describe("Parentheses and Comma", () => {
        it("should tokenize LPAREN", () => {
            expect(tokenize("(")).to.deep.equal([createToken(TokenType.LPAREN, "(", 0)]);
        });
        it("should tokenize RPAREN", () => {
            expect(tokenize(")")).to.deep.equal([createToken(TokenType.RPAREN, ")", 0)]);
        });
        it("should tokenize COMMA", () => {
            expect(tokenize(",")).to.deep.equal([createToken(TokenType.COMMA, ",", 0)]);
        });
        it("should tokenize mixed parentheses and comma", () => {
            expect(tokenize("(),(,)")).to.deep.equal([
                createToken(TokenType.LPAREN, "(", 0),
                createToken(TokenType.RPAREN, ")", 1),
                createToken(TokenType.COMMA, ",", 2),
                createToken(TokenType.LPAREN, "(", 3),
                createToken(TokenType.COMMA, ",", 4),
                createToken(TokenType.RPAREN, ")", 5),
            ]);
        });
    });
    describe("Constants", () => {
        it("should tokenize 'pi'", () => {
            expect(tokenize("pi")).to.deep.equal([createToken(TokenType.CONSTANT, "pi", 0)]);
        });
        it("should tokenize 'e'", () => {
            expect(tokenize("e")).to.deep.equal([createToken(TokenType.CONSTANT, "e", 0)]);
        });
        it("should tokenize multiple constants", () => {
            expect(tokenize("pi e")).to.deep.equal([
                createToken(TokenType.CONSTANT, "pi", 0),
                createToken(TokenType.CONSTANT, "e", 3),
            ]);
        });
    });
    describe("Functions", () => {
        it("should tokenize log functions (log, ln)", () => {
            expect(tokenize("log")).to.deep.equal([createToken(TokenType.LOG, "log", 0)]);
            expect(tokenize("ln")).to.deep.equal([createToken(TokenType.LN, "ln", 0)]);
        });
        it("should tokenize trigonometric functions (sin, cos, tan, csc, sec, cot)", () => {
            expect(tokenize("sin")).to.deep.equal([createToken(TokenType.SIN, "sin", 0)]);
            expect(tokenize("cos")).to.deep.equal([createToken(TokenType.COS, "cos", 0)]);
            expect(tokenize("tan")).to.deep.equal([createToken(TokenType.TAN, "tan", 0)]);
            expect(tokenize("csc")).to.deep.equal([createToken(TokenType.CSC, "csc", 0)]);
            expect(tokenize("sec")).to.deep.equal([createToken(TokenType.SEC, "sec", 0)]);
            expect(tokenize("cot")).to.deep.equal([createToken(TokenType.COT, "cot", 0)]);
        });
        it("should tokenize inverse trigonometric functions (arcsin to arccot)", () => {
            expect(tokenize("arcsin")).to.deep.equal([createToken(TokenType.ARCSIN, "arcsin", 0)]);
            expect(tokenize("arccos")).to.deep.equal([createToken(TokenType.ARCCOS, "arccos", 0)]);
            expect(tokenize("arctan")).to.deep.equal([createToken(TokenType.ARCTAN, "arctan", 0)]);
            expect(tokenize("arccsc")).to.deep.equal([createToken(TokenType.ARCCSC, "arccsc", 0)]);
            expect(tokenize("arcsec")).to.deep.equal([createToken(TokenType.ARCSEC, "arcsec", 0)]);
            expect(tokenize("arccot")).to.deep.equal([createToken(TokenType.ARCCOT, "arccot", 0)]);
        });
        it("should tokenize a full function call with arguments and whitespace", () => {
            const expression = "sin(x) + log(10, y)";
            const expectedTokens = [
                createToken(TokenType.SIN, "sin", 0),
                createToken(TokenType.LPAREN, "(", 3),
                createToken(TokenType.VARIABLE, "x", 4),
                createToken(TokenType.RPAREN, ")", 5),
                createToken(TokenType.PLUS, "+", 7),
                createToken(TokenType.LOG, "log", 9),
                createToken(TokenType.LPAREN, "(", 12),
                createToken(TokenType.NUMBER, "10", 13),
                createToken(TokenType.COMMA, ",", 15),
                createToken(TokenType.VARIABLE, "y", 17),
                createToken(TokenType.RPAREN, ")", 18),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should tokenize a function call without arguments", () => {
            const expression = "sin()";
            const expectedTokens = [
                createToken(TokenType.SIN, "sin", 0),
                createToken(TokenType.LPAREN, "(", 3),
                createToken(TokenType.RPAREN, ")", 4),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should tokenize nested function calls", () => {
            const expression = "sin(cos(x))";
            const expectedTokens = [
                createToken(TokenType.SIN, "sin", 0),
                createToken(TokenType.LPAREN, "(", 3),
                createToken(TokenType.COS, "cos", 4),
                createToken(TokenType.LPAREN, "(", 7),
                createToken(TokenType.VARIABLE, "x", 8),
                createToken(TokenType.RPAREN, ")", 9),
                createToken(TokenType.RPAREN, ")", 10),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should prioritize longer matches for keywords/functions", () => {
            expect(tokenize("arcsin")).to.deep.equal([createToken(TokenType.ARCSIN, "arcsin", 0)]);
            expect(tokenize("sin")).to.deep.equal([createToken(TokenType.SIN, "sin", 0)]);
            expect(tokenize("log")).to.deep.equal([createToken(TokenType.LOG, "log", 0)]);
            expect(tokenize("ln")).to.deep.equal([createToken(TokenType.LN, "ln", 0)]);
        });
    });
    describe("Combined Expressions", () => {
        it("should tokenize a simple arithmetic expression", () => {
            const expression = "1 + 2 * x";
            const expectedTokens = [
                createToken(TokenType.NUMBER, "1", 0),
                createToken(TokenType.PLUS, "+", 2),
                createToken(TokenType.NUMBER, "2", 4),
                createToken(TokenType.MULTIPLY, "*", 6),
                createToken(TokenType.VARIABLE, "x", 8),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should tokenize an expression with functions, constants, and variables", () => {
            const expression = "pi * sin(x) - e^y";
            const expectedTokens = [
                createToken(TokenType.CONSTANT, "pi", 0),
                createToken(TokenType.MULTIPLY, "*", 3),
                createToken(TokenType.SIN, "sin", 5),
                createToken(TokenType.LPAREN, "(", 8),
                createToken(TokenType.VARIABLE, "x", 9),
                createToken(TokenType.RPAREN, ")", 10),
                createToken(TokenType.MINUS, "-", 12),
                createToken(TokenType.CONSTANT, "e", 14),
                createToken(TokenType.POWER, "^", 15),
                createToken(TokenType.VARIABLE, "y", 16),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should handle expressions with various whitespace combinations", () => {
            const expression = " 2 * ( x + y ) /  pi ";
            const expectedTokens = [
                createToken(TokenType.NUMBER, "2", 1),
                createToken(TokenType.MULTIPLY, "*", 3),
                createToken(TokenType.LPAREN, "(", 5),
                createToken(TokenType.VARIABLE, "x", 7),
                createToken(TokenType.PLUS, "+", 9),
                createToken(TokenType.VARIABLE, "y", 11),
                createToken(TokenType.RPAREN, ")", 13),
                createToken(TokenType.DIVIDE, "/", 15),
                createToken(TokenType.CONSTANT, "pi", 18),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should handle implicit multiplication (2x) by tokenizing as separate number and variable", () => {
            // As per documentation: "Multiplication must be explicit (no `2x`)"
            // This is a parser rule, not a tokenizer rule. The tokenizer should produce separate tokens.
            const expression = "2x";
            const expectedTokens = [
                createToken(TokenType.NUMBER, "2", 0),
                createToken(TokenType.VARIABLE, "x", 1),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should handle implicit multiplication (alpha x) by tokenizing as separate variables", () => {
            const expression = "alpha x";
            const expectedTokens = [
                createToken(TokenType.VARIABLE, "alpha", 0),
                createToken(TokenType.VARIABLE, "x", 6),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should tokenize constants concatenated with operators", () => {
            const expression = "pi+e";
            const expectedTokens = [
                createToken(TokenType.CONSTANT, "pi", 0),
                createToken(TokenType.PLUS, "+", 2),
                createToken(TokenType.CONSTANT, "e", 3),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should tokenize numbers concatenated with constants (implicit multiplication)", () => {
            const expression = "2pi";
            const expectedTokens = [
                createToken(TokenType.NUMBER, "2", 0),
                createToken(TokenType.CONSTANT, "pi", 1),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
        it("should tokenize numbers concatenated with functions (implicit multiplication)", () => {
            const expression = "2sin(x)";
            const expectedTokens = [
                createToken(TokenType.NUMBER, "2", 0),
                createToken(TokenType.SIN, "sin", 1),
                createToken(TokenType.LPAREN, "(", 4),
                createToken(TokenType.VARIABLE, "x", 5),
                createToken(TokenType.RPAREN, ")", 6),
            ];
            expect(tokenize(expression)).to.deep.equal(expectedTokens);
        });
    });
    describe("Case Sensitivity and Unrecognized Keywords", () => {
        it("should treat 'Pi' as a variable, not a constant", () => {
            expect(tokenize("Pi")).to.deep.equal([createToken(TokenType.VARIABLE, "Pi", 0)]);
        });
        it("should treat 'E' as a variable, not a constant", () => {
            expect(tokenize("E")).to.deep.equal([createToken(TokenType.VARIABLE, "E", 0)]);
        });
        it("should treat 'SIN' as a variable, not a function", () => {
            expect(tokenize("SIN(x)")).to.deep.equal([
                createToken(TokenType.VARIABLE, "SIN", 0),
                createToken(TokenType.LPAREN, "(", 3),
                createToken(TokenType.VARIABLE, "x", 4),
                createToken(TokenType.RPAREN, ")", 5),
            ]);
        });
        it("should treat 'LOG' as a variable, not a function", () => {
            expect(tokenize("LOG(10)")).to.deep.equal([
                createToken(TokenType.VARIABLE, "LOG", 0),
                createToken(TokenType.LPAREN, "(", 3),
                createToken(TokenType.NUMBER, "10", 4),
                createToken(TokenType.RPAREN, ")", 6),
            ]);
        });
    });
    describe("Error Handling", () => {
        it("should throw an error for an unknown character", () => {
            expect(() => tokenize("1 + @")).to.throw("Unknown character '@' at position 4");
        });
        it("should throw an error for multiple unknown characters", () => {
            expect(() => tokenize("a $ b")).to.throw("Unknown character '$' at position 2");
        });
        it("should treat function-like names that are not actual functions as variables", () => {
            expect(tokenize("sine")).to.deep.equal([createToken(TokenType.VARIABLE, "sine", 0)]);
            expect(tokenize("logarithm")).to.deep.equal([createToken(TokenType.VARIABLE, "logarithm", 0)]);
        });
    });
});
