import { Expression } from './expressionInterface';
import { NumberExpression, VariableExpression, BinaryOperationExpression, UnaryOperationExpression } from './expression';

// Token types
enum TokenType {
    NUMBER,
    VARIABLE,
    PLUS,
    MINUS,
    MULTIPLY,
    DIVIDE,
    POWER,
    LPAREN,
    RPAREN,
    EOF, // End Of File
}

// Token structure
interface Token {
    type: TokenType;
    value?: string | number;
}

/**
 * @class Parser
 * @description
 * Defines a parser for mathematical expressions. It takes a string expression
 * and converts it into an Abstract Syntax Tree (AST) represented by Expression objects.
 * The parser supports numbers, variables, basic arithmetic operations (+, -, *, /, ^),
 * and parentheses for grouping, respecting PEMDAS order of operations.
 */
export class Parser {
    private tokens: Token[] = []; // Initialize tokens array
    private currentIndex: number = 0; // Initialize currentIndex

    /**
     * @method parse
     * @description
     * Parses a string mathematical expression into an Expression object (AST).
     * This method is responsible for tokenizing the input string and building
     * the expression tree according to standard mathematical operator precedence (PEMDAS).
     *
     * @param expressionString The input mathematical expression as a string.
     * @returns An Expression object representing the parsed AST.
     * @throws {Error} If the expression string is invalid, contains unsupported characters,
     *                 has mismatched parentheses, or results in an ambiguous parse.
     *
     * @precondition
     * - `expressionString` must be a non-empty string.
     * - `expressionString` may contain:
     *     - Numbers (integers or decimals, e.g., '123', '3.14').
     *     - Variables (single letters, e.g., 'x', 'y', 'z', case-sensitive).
     *     - Operators: '+', '-', '*', '/', '^'.
     *     - Parentheses: '(', ')'.
     *     - Whitespace (which will be ignored).
     * - The expression must be syntactically valid (e.g., no '1++2', '()', 'x+').
     *
     * @postcondition
     * - Returns a valid `Expression` object representing the parsed expression tree.
     * - The returned `Expression` object adheres to the `Expression` interface defined
     *   in `src/expressionInterface.ts`. Concrete classes from `src/expression.ts`
     *   will be used internally to construct this object.
     * - Operator precedence (PEMDAS: Parentheses, Exponents, Multiplication/Division, Addition/Subtraction)
     *   is correctly applied in the construction of the AST.
     * - For example:
     *     - "2 + 3 * x" should parse to an AdditionExpression with 2 and a MultiplicationExpression (3, x).
     *     - "(2 + 3) * x" should parse to a MultiplicationExpression with an AdditionExpression (2, 3) and x.
     *     - "2 ^ 3 ^ 4" should parse as right-associative for exponentiation (2 ^ (3 ^ 4)).
     *
     * @constraints
     * - Only supported characters are allowed.
     * - No implicit multiplication (e.g., '2x' or '(2)x' is not supported; must be '2*x').
     * - Unary minus/plus at the beginning or after an operator/parenthesis is supported (e.g., '-5', '2 * -3', '(-x)').
     * - Floating-point numbers are supported.
     *
     * @errors
     * - `Error("Invalid expression: ...")`: For general parsing errors, syntax errors, or unsupported tokens.
     * - `Error("Mismatched parentheses")`: If parentheses are not balanced.
     * - `Error("Unexpected end of expression")`: If an operator is at the end of the string, or an opening parenthesis is not closed.
     * - `Error("Invalid token: ...")`: If an unrecognized character or sequence is encountered.
     *
     * @assumptions
     * - The input string is a single mathematical expression.
     * - Variable names are single characters (e.g., 'x', 'y', 'A', 'B').
     * - Operators are single characters.
     * - Whitespace should be ignored during parsing.
     * - Standard left-to-right associativity for +, -, *, /
     * - Right-to-left associativity for ^ (exponentiation).
     */
    public parse(expressionString: string): Expression {
        if (!expressionString || expressionString.trim() === '') {
            throw new Error("Syntax Error: Empty expression");
        }

        this.tokenize(expressionString);
        this.currentIndex = 0;

        const expression = this.parseExpression();

        if (this.peek().type !== TokenType.EOF) {
            // This covers cases like "1 + 2 a" or "1 + 2)"
            const unexpectedTokenValue = this.peek().value !== undefined ? `'${this.peek().value}'` : `'${TokenType[this.peek().type]}'`;
            if (this.peek().type === TokenType.RPAREN) {
                 throw new Error("Syntax Error: Mismatched parentheses"); // For trailing ')'
            }
            throw new Error(`Syntax Error: Unexpected token ${unexpectedTokenValue} after expression`);
        }

        return expression;
    }

    private tokenize(expressionString: string): void {
        this.tokens = [];
        let i = 0;
        const s = expressionString.replace(/\s+/g, ''); // Remove all whitespace

        while (i < s.length) {
            let char = s[i];

            if (/[0-9]/.test(char)) {
                let numStr = '';
                while (i < s.length && (/[0-9]/.test(s[i]) || s[i] === '.')) {
                    if (s[i] === '.' && numStr.includes('.')) {
                        throw new Error(`Syntax Error: Invalid number format '${numStr + s[i]}'`);
                    }
                    numStr += s[i];
                    i++;
                }
                this.tokens.push({ type: TokenType.NUMBER, value: parseFloat(numStr) });
                continue;
            }

            if (/[a-zA-Z]/.test(char)) {
                let varName = '';
                while (i < s.length && /[a-zA-Z]/.test(s[i])) { // Variables are only letters based on 'myVar' and 'x2' tests
                    varName += s[i];
                    i++;
                }
                this.tokens.push({ type: TokenType.VARIABLE, value: varName });
                continue;
            }

            switch (char) {
                case '+': this.tokens.push({ type: TokenType.PLUS }); break;
                case '-': this.tokens.push({ type: TokenType.MINUS }); break;
                case '*': this.tokens.push({ type: TokenType.MULTIPLY }); break;
                case '/': this.tokens.push({ type: TokenType.DIVIDE }); break;
                case '^': this.tokens.push({ type: TokenType.POWER }); break;
                case '(': this.tokens.push({ type: TokenType.LPAREN }); break;
                case ')': this.tokens.push({ type: TokenType.RPAREN }); break;
                default:
                    throw new Error(`Syntax Error: Invalid character '${char}'`);
            }
            i++;
        }
        this.tokens.push({ type: TokenType.EOF });
    }

    private advance(): Token {
        if (this.currentIndex >= this.tokens.length) {
            throw new Error("Syntax Error: Unexpected end of expression");
        }
        return this.tokens[this.currentIndex++];
    }

    private peek(): Token {
        if (this.currentIndex >= this.tokens.length) {
            return { type: TokenType.EOF };
        }
        return this.tokens[this.currentIndex];
    }

    private match(type: TokenType): Token {
        const token = this.peek();
        if (token.type === type) {
            return this.advance();
        }
        if (type === TokenType.RPAREN) {
             throw new Error("Syntax Error: Mismatched parentheses");
        }
        if (token.type === TokenType.EOF) {
            throw new Error("Syntax Error: Incomplete expression");
        }
        if ([TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.POWER].includes(token.type)) {
            throw new Error("Syntax Error: Unexpected operator");
        }
        throw new Error(`Syntax Error: Unexpected token '${token.value || TokenType[token.type]}'`);
    }

    // Expression -> Term ( ( '+' | '-' ) Term )*
    private parseExpression(): Expression {
        let expr = this.parseTerm();

        while (this.peek().type === TokenType.PLUS || this.peek().type === TokenType.MINUS) {
            const operatorToken = this.advance();
            const right = this.parseTerm();
            expr = new BinaryOperationExpression(operatorToken.type === TokenType.PLUS ? '+' : '-', expr, right);
        }
        return expr;
    }

    // Term -> Factor ( ( '*' | '/' ) Factor )*
    private parseTerm(): Expression {
        let expr = this.parseFactor();

        while (this.peek().type === TokenType.MULTIPLY || this.peek().type === TokenType.DIVIDE) {
            const operatorToken = this.advance();
            const right = this.parseFactor();
            expr = new BinaryOperationExpression(operatorToken.type === TokenType.MULTIPLY ? '*' : '/' , expr, right);
        }
        return expr;
    }

    // Factor -> Unary ( '^' Factor )?  // Right-associative for ^
    private parseFactor(): Expression {
        let expr = this.parseUnary();

        if (this.peek().type === TokenType.POWER) {
            this.advance(); // Consume '^'
            const right = this.parseFactor(); // Right-associativity: parseFactor() again
            expr = new BinaryOperationExpression('^', expr, right);
        }
        return expr;
    }

    // Unary -> ('+' | '-') Term | Primary
    // This rule ensures that unary operators apply to the entire 'Term' that follows them,
    // which correctly handles expressions like '- (2 * 3)' where the unary operator applies
    // to the result of the multiplication. This provides the correct precedence for unary
    // operators relative to multiplication/division (higher or equal) and addition/subtraction (higher).
    private parseUnary(): Expression {
        if (this.peek().type === TokenType.PLUS || this.peek().type === TokenType.MINUS) {
            const operatorToken = this.advance();
            // The operand for a unary operator is now a Term.
            // This aligns with standard operator precedence where unary operations
            // have higher precedence than multiplication/division/addition/subtraction,
            // but the operand itself can be a complex expression that might involve these.
            // For example, in -(2 * 3), the '-' applies to the result of (2 * 3).
            // parseTerm will correctly handle the multiplication within its scope.
            let operand = this.parseTerm(); 
            return new UnaryOperationExpression(operatorToken.type === TokenType.PLUS ? '+' : '-', operand);
        }
        return this.parsePrimary();
    }

    // Primary -> Number | Variable | '(' Expression ')'
    private parsePrimary(): Expression {
        const token = this.peek();

        switch (token.type) {
            case TokenType.NUMBER:
                this.advance();
                // After a number, if the next token is a variable or LPAREN, it's an error (implicit multiplication)
                if (this.peek().type === TokenType.VARIABLE || this.peek().type === TokenType.LPAREN) {
                    throw new Error("Syntax Error: Unexpected token"); // For "2x" or "2(3)"
                }
                return new NumberExpression(token.value as number);
            case TokenType.VARIABLE:
                this.advance();
                // After a variable, if the next token is a number or LPAREN, it's an error (implicit multiplication)
                if (this.peek().type === TokenType.NUMBER || this.peek().type === TokenType.LPAREN) {
                    throw new Error("Syntax Error: Unexpected token"); // For "x2" or "x(3)"
                }
                return new VariableExpression(token.value as string);
            case TokenType.LPAREN:
                this.advance(); // Consume '('
                // Check for empty parentheses "()"
                if (this.peek().type === TokenType.RPAREN) {
                    throw new Error("Syntax Error: Empty parentheses");
                }
                // Parse the content of parentheses as a full expression. The parseExpression method
                // is designed to correctly handle all operator precedences, including unary operators,
                // through its delegation to lower-precedence parsing functions.
                let expr: Expression = this.parseExpression();
                
                this.match(TokenType.RPAREN); // Consume ')'
                // After a parenthesized expression, if the next token is a number, variable or LPAREN, it's an error
                if (this.peek().type === TokenType.NUMBER || this.peek().type === TokenType.VARIABLE || this.peek().type === TokenType.LPAREN) {
                    throw new Error("Syntax Error: Unexpected token"); // For "(2)x" or "(2)(3)"
                }
                return expr;
            case TokenType.EOF:
                throw new Error("Syntax Error: Incomplete expression");
            default:
                // This covers cases where an operator or RPAREN appears where a primary is expected
                if ([TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.POWER].includes(token.type)) {
                    throw new Error("Syntax Error: Unexpected operator"); // E.g., "1 + * 2"
                }
                if (token.type === TokenType.RPAREN) {
                    throw new Error("Syntax Error: Mismatched parentheses"); // E.g., "1 + ) 2" (unexpected ')' in middle)
                }
                throw new Error(`Syntax Error: Unexpected token '${token.value || TokenType[token.type]}'`);
        }
    }
}