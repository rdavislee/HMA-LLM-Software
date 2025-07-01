"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.parse = void 0;
const expression_1 = require("./expression"); // Import concrete classes
// Simple token stream manager
class TokenStream {
    constructor(input) {
        this.currentIndex = 0;
        this.tokens = this.tokenize(input);
    }
    // Basic tokenizer:
    // - Recognizes numbers (integers and floats)
    // - Recognizes variables/function names (alphabetic sequences)
    // - Recognizes operators and parentheses
    tokenize(expression) {
        // Regex for tokens:
        // 1. Numbers: \d+(\.\d*)?|\.\d+ (handles numbers like 123, 3.14, or .5)
        // 2. Variable/Function names: [a-zA-Z_]+
        // 3. Operators: \+|\-|\*|\/|\^|\(|\)|, (single character operators)
        const regex = /(\d+(\.\d*)?|\.\d+|[a-zA-Z_]+|\+|\-|\*|\/|\^|\(|\)|,)/g;
        let match;
        const result = [];
        while ((match = regex.exec(expression)) !== null) {
            if (match[0].trim() !== '') { // Ensure no empty matches from weird regex behavior
                result.push(match[0]);
            }
        }
        return result;
    }
    peek() {
        return this.tokens[this.currentIndex];
    }
    consume() {
        if (this.currentIndex >= this.tokens.length) {
            throw new Error('Unexpected end of input');
        }
        return this.tokens[this.currentIndex++];
    }
    // Consume a token only if it matches the expected type
    expect(expected) {
        const token = this.consume();
        if (token !== expected) {
            throw new Error(`Expected '${expected}' but got '${token}'`);
        }
        return token;
    }
    // Check if current token matches and consume it
    match(expected) {
        if (this.peek() === expected) {
            this.consume();
            return true;
        }
        return false;
    }
    isAtEnd() {
        return this.currentIndex >= this.tokens.length;
    }
}
function parse(input) {
    const stream = new TokenStream(input.trim());
    // parseFactor: Handles numbers, variables, function calls, and parenthesized expressions.
    function parseFactor() {
        const token = stream.peek();
        if (!token) {
            throw new Error('Unexpected end of input during factor parsing');
        }
        // Number (check for both integer and float formats, including leading dot for floats like .5)
        if (!isNaN(Number(token))) {
            // Ensure the token represents a valid number string (e.g., not just '.')
            if (token === '.' || (token.startsWith('.') && isNaN(Number('0' + token)))) {
                throw new Error(`Invalid number format: ${token}`);
            }
            return new expression_1.NumberNode(Number(stream.consume()));
        }
        // Parenthesized expression
        if (stream.match('(')) {
            const expr = parseExpression();
            stream.expect(')');
            return expr;
        }
        // Variable or Function Call
        if (token.match(/^[a-zA-Z_]+$/)) {
            const name = stream.consume();
            // Check for constants like 'e' or 'pi' BEFORE checking for general variables
            const constants = ['e', 'pi'];
            if (constants.includes(name)) {
                return new expression_1.ConstantNode(name);
            }
            if (stream.match('(')) { // It's a function call
                const args = []; // Changed type here to ExpressionNode[]
                if (stream.peek() === ')') { // If ')' immediately follows '(', it's an empty argument list
                    throw new Error(`Missing argument`);
                }
                // Parse the first argument
                args.push(parseExpression());
                // As per current spec and tests, only single argument functions are expected.
                // If multiple arguments are encountered, it's an error for now.
                if (stream.peek() === ',') {
                    throw new Error('Functions with multiple arguments are not supported by this parser yet.');
                }
                stream.expect(')'); // Expect closing parenthesis
                // Validate function name against allowed types
                const functionNames = [
                    'log', 'ln', 'exp',
                    'sin', 'cos', 'tan',
                    'sec', 'csc', 'cot',
                    'asin', 'acos', 'atan',
                    'asec', 'acsc', 'acot',
                    'sinh', 'cosh', 'tanh',
                    'asinh', 'acosh', 'atanh'
                ];
                if (!functionNames.includes(name)) {
                    throw new Error(`Unknown function: ${name}`);
                }
                return new expression_1.FunctionCallNode(name, args); // Explicit cast for args
            }
            else { // It's a variable
                return new expression_1.VariableNode(name);
            }
        }
        throw new Error(`Unexpected token at factor: ${token}`);
    }
    // parseUnary: Handles unary negation.
    function parseUnary() {
        if (stream.match('-')) {
            const operand = parseUnary(); // Allow nested unary operations (--x)
            return new expression_1.UnaryOperationNode('negate', operand); // Explicit cast for operand
        }
        return parseFactor();
    }
    // parsePower: Handles exponentiation (right-associative).
    function parsePower() {
        let left = parseUnary();
        while (stream.match('^')) {
            const right = parsePower(); // Right-associative
            left = new expression_1.BinaryOperationNode('power', left, right); // Explicit casts for left and right
        }
        return left;
    }
    // parseTerm: Handles multiplication and division (left-associative).
    function parseTerm() {
        let left = parsePower();
        while (stream.peek() === '*' || stream.peek() === '/') {
            const operatorToken = stream.consume();
            const right = parsePower();
            left = new expression_1.BinaryOperationNode(operatorToken === '*' ? 'multiply' : 'divide', left, // Explicit cast for left
            right);
        }
        return left;
    }
    // parseExpression: Handles addition and subtraction (left-associative).
    function parseExpression() {
        let left = parseTerm();
        while (stream.peek() === '+' || stream.peek() === '-') {
            const operatorToken = stream.consume();
            const right = parseTerm();
            left = new expression_1.BinaryOperationNode(operatorToken === '+' ? 'add' : 'subtract', left, // Explicit cast for left
            right);
        }
        return left;
    }
    const result = parseExpression();
    if (!stream.isAtEnd()) {
        throw new Error(`Unexpected tokens at end of input: ${stream.peek()}`);
    }
    return result;
}
exports.parse = parse;
