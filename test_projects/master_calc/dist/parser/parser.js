import { TokenType } from "../types/tokens.js";
import { NodeType } from "../types/ast.js";
import { CalculatorError } from "../utils/error.js";
export function parse(tokens) {
    let currentTokenIndex = 0;
    const peek = () => {
        return tokens[currentTokenIndex] || { type: TokenType.EOF, position: tokens[tokens.length - 1]?.position || 0 };
    };
    const consume = (expectedType, errorMessage) => {
        const token = peek();
        if (token.type === TokenType.EOF && expectedType !== TokenType.EOF) {
            throw new CalculatorError(errorMessage || `Syntax Error: Expected ${TokenType[expectedType]} but found EOF`);
        }
        if (token.type !== expectedType) {
            throw new CalculatorError(errorMessage || `Syntax Error: Unexpected token type ${TokenType[token.type]} at position ${token.position}`);
        }
        currentTokenIndex++;
        return token;
    };
    const isAtEnd = () => {
        return peek().type === TokenType.EOF;
    };
    // Add function arities map here
    const functionArities = {
        'sin': 1, 'cos': 1, 'tan': 1, 'csc': 1, 'sec': 1, 'cot': 1,
        'arcsin': 1, 'arccos': 1, 'arctan': 1, 'arccsc': 1, 'arcsec': 1, 'arccot': 1,
        'ln': 1,
        'log': 'variadic',
    };
    // Primary: NUMBER | VARIABLE | CONSTANT | LPAREN Expression RPAREN | FunctionCall
    const parsePrimary = () => {
        const token = peek();
        let node;
        switch (token.type) {
            case TokenType.NUMBER:
                consume(TokenType.NUMBER);
                node = { type: NodeType.Number, value: parseFloat(token.value) };
                break;
            case TokenType.VARIABLE:
                consume(TokenType.VARIABLE);
                node = { type: NodeType.Variable, name: token.value };
                break;
            case TokenType.CONSTANT:
                consume(TokenType.CONSTANT);
                node = { type: NodeType.Constant, name: token.value };
                break;
            case TokenType.LPAREN:
                consume(TokenType.LPAREN);
                node = parseExpression(); // Recursive call for sub-expression
                consume(TokenType.RPAREN, `Syntax Error: Expected ) but found ${TokenType[peek().type]} at position ${peek().position}`);
                break;
            case TokenType.LOG:
            case TokenType.LN:
            case TokenType.SIN:
            case TokenType.COS:
            case TokenType.TAN:
            case TokenType.CSC:
            case TokenType.SEC:
            case TokenType.COT:
            case TokenType.ARCSIN:
            case TokenType.ARCCOS:
            case TokenType.ARCTAN:
            case TokenType.ARCCSC:
            case TokenType.ARCSEC:
            case TokenType.ARCCOT:
                const functionName = token.value;
                consume(token.type); // Consume the function name token
                consume(TokenType.LPAREN, `Syntax Error: Expected ( after function name ${functionName} at position ${token.position}`);
                const args = [];
                // Check for empty arguments (e.g., sin())
                if (peek().type === TokenType.RPAREN) {
                    throw new CalculatorError(`Syntax Error: Expected expression but found RPAREN at position ${peek().position}`);
                }
                args.push(parseExpression()); // Parse the first argument
                // Check for additional arguments (only for 'log' function)
                if (functionName === 'log') {
                    if (peek().type === TokenType.COMMA) {
                        consume(TokenType.COMMA);
                        // Check for missing expression after comma (e.g., log(2,))
                        if (peek().type === TokenType.RPAREN || isAtEnd()) {
                            throw new CalculatorError(`Syntax Error: Expected expression but found ${TokenType[peek().type]} at position ${peek().position}`);
                        }
                        args.push(parseExpression()); // Parse the second argument for log
                    }
                    else if (peek().type === TokenType.NUMBER || peek().type === TokenType.VARIABLE || peek().type === TokenType.CONSTANT || peek().type === TokenType.LPAREN) {
                        // If it's not a comma, but another expression token, it's a missing comma error
                        throw new CalculatorError(`Syntax Error: Expected COMMA but found ${TokenType[peek().type]} at position ${peek().position}`);
                    }
                }
                else { // For single-argument functions (sin, cos, etc.)
                    if (peek().type === TokenType.COMMA) {
                        // This means an unexpected comma for a single-arg function, like sin(x,y)
                        throw new CalculatorError(`Syntax Error: Unexpected token type COMMA at position ${peek().position}`);
                    }
                }
                consume(TokenType.RPAREN, `Syntax Error: Expected ) but found ${TokenType[peek().type]} at position ${peek().position}`);
                // Arity checks
                const expectedArity = functionArities[functionName];
                if (expectedArity !== 'variadic' && args.length !== expectedArity) {
                    throw new CalculatorError(`Syntax Error: Function '${functionName}' expects ${expectedArity} argument(s) but received ${args.length} at position ${token.position}`);
                }
                else if (functionName === 'log' && (args.length < 1 || args.length > 2)) {
                    // Specific check for log as it's 'variadic' but with defined limits
                    throw new CalculatorError(`Syntax Error: Function 'log' expects 1 or 2 arguments but received ${args.length} at position ${token.position}`);
                }
                node = { type: NodeType.FunctionCall, functionName, arguments: args };
                break;
            case TokenType.EOF:
                throw new CalculatorError(`Syntax Error: Expected expression but found EOF`);
            default:
                throw new CalculatorError(`Syntax Error: Unexpected token type ${TokenType[token.type]} at position ${token.position}`);
        }
        return node;
    };
    // Unary: MINUS Unary | Primary
    const parseUnary = () => {
        if (peek().type === TokenType.MINUS) {
            const operatorToken = consume(TokenType.MINUS);
            const operand = parsePower(); // Unary minus applies to the result of Power expression
            return { type: NodeType.UnaryOperation, operator: '-', operand };
        }
        return parsePrimary();
    };
    // Power: Unary ( POWER Power )? (Right-associative)
    const parsePower = () => {
        let left = parseUnary();
        if (peek().type === TokenType.POWER) {
            const operatorToken = consume(TokenType.POWER);
            const right = parsePower(); // Recursive call for right operand for right-associativity
            left = {
                type: NodeType.BinaryOperation,
                operator: operatorToken.value,
                left,
                right,
            };
        }
        return left;
    };
    // Multiplicative: Power ( (MULTIPLY | DIVIDE) Power )* (Left-associative)
    const parseMultiplicative = () => {
        let left = parsePower();
        while (peek().type === TokenType.MULTIPLY || peek().type === TokenType.DIVIDE) {
            const operatorToken = consume(peek().type);
            const right = parsePower();
            left = {
                type: NodeType.BinaryOperation,
                operator: operatorToken.value,
                left,
                right,
            };
        }
        return left;
    };
    // Additive: Multiplicative ( (PLUS | MINUS) Multiplicative )* (Left-associative)
    const parseAdditive = () => {
        let left = parseMultiplicative();
        while (peek().type === TokenType.PLUS || peek().type === TokenType.MINUS) {
            const operatorToken = consume(peek().type);
            const right = parseMultiplicative();
            left = {
                type: NodeType.BinaryOperation,
                operator: operatorToken.value,
                left,
                right,
            };
        }
        return left;
    };
    // Main parse function entry point
    const parseExpression = () => {
        if (isAtEnd()) { // Handle empty expression
            throw new CalculatorError("Syntax Error: Unexpected EOF");
        }
        return parseAdditive();
    };
    const ast = parseExpression();
    // Ensure no remaining tokens after parsing the full expression
    if (!isAtEnd()) {
        throw new CalculatorError(`Syntax Error: Unexpected token type ${TokenType[peek().type]} at position ${peek().position}`);
    }
    return ast;
}
