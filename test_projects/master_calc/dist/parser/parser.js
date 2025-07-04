"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.parse = void 0;
const parserlib = __importStar(require("parserlib"));
const Parser = parserlib.default.css.Parser;
const parser_interface_1 = require("./parser.interface");
// 1. Define Tokens for the Lexer
// Order matters for overlapping patterns (longest match / first defined takes precedence)
const tokens = [
    { type: 'LOG_BASE_KEYWORD', pattern: /\blog_base\b/ },
    { type: 'ARCSIN_KEYWORD', pattern: /\barcsin\b/ },
    { type: 'ARCCOS_KEYWORD', pattern: /\barccos\b/ },
    { type: 'ARCTAN_KEYWORD', pattern: /\barctan\b/ },
    { type: 'ARCCSC_KEYWORD', pattern: /\barccsc\b/ },
    { type: 'ARCSEC_KEYWORD', pattern: /\barcsec\b/ },
    { type: 'ARCCOT_KEYWORD', pattern: /\barccot\b/ },
    { type: 'SIN_KEYWORD', pattern: /\bsin\b/ },
    { type: 'COS_KEYWORD', pattern: /\bcos\b/ },
    { type: 'TAN_KEYWORD', pattern: /\btan\b/ },
    { type: 'CSC_KEYWORD', pattern: /\bcsc\b/ },
    { type: 'SEC_KEYWORD', pattern: /\bsec\b/ },
    { type: 'COT_KEYWORD', pattern: /\bcot\b/ },
    { type: 'LN_KEYWORD', pattern: /\bln\b/ },
    { type: 'LOG_KEYWORD', pattern: /\blog\b/ }, // Must be after LOG_BASE_KEYWORD
    // Constants (must come before VARIABLE if they are single letters)
    { type: 'PI_KEYWORD', pattern: /\bpi\b/ },
    { type: 'E_KEYWORD', pattern: /\be\b/ },
    // Variables (single lowercase letter). This must come AFTER constants like 'e' and 'pi'
    // to ensure 'e' and 'pi' are matched as constants, not variables.
    { type: 'VARIABLE', pattern: /[a-z]/ },
    // Numbers (matches integers, decimals like '3.14', and also '5.', '.5')
    { type: 'NUMBER', pattern: /\d+\.\d+|\d+/ },
    // Operators
    { type: 'PLUS', pattern: /\+/ },
    { type: 'MINUS', pattern: /-/ },
    { type: 'MULTIPLY', pattern: /\*/ },
    { type: 'DIVIDE', pattern: /\// },
    { type: 'POWER', pattern: /\^/ },
    // Punctuation
    { type: 'LPAREN', pattern: /\(/ },
    { type: 'RPAREN', pattern: /\)/ },
    { type: 'COMMA', pattern: /,/ },
    // Whitespace to ignore
    { type: 'WHITESPACE', pattern: /\s+/, group: 'skip' },
];
// 2. Define the Grammar Rules
const grammarRules = {
    // Lowest precedence: Addition and Subtraction (left-associative)
    Expression: [
        ['Expression PLUS Term', (left, _plus, right) => ({
                kind: parser_interface_1.ASTNodeKind.BinaryExpression,
                operator: parser_interface_1.BinaryOperator.Add,
                left,
                right,
            })],
        ['Expression MINUS Term', (left, _minus, right) => ({
                kind: parser_interface_1.ASTNodeKind.BinaryExpression,
                operator: parser_interface_1.BinaryOperator.Subtract,
                left,
                right,
            })],
        ['Term', (term) => term],
    ],
    // Next precedence: Multiplication and Division (left-associative)
    Term: [
        ['Term MULTIPLY Factor', (left, _mul, right) => ({
                kind: parser_interface_1.ASTNodeKind.BinaryExpression,
                operator: parser_interface_1.BinaryOperator.Multiply,
                left,
                right,
            })],
        ['Term DIVIDE Factor', (left, _div, right) => ({
                kind: parser_interface_1.ASTNodeKind.BinaryExpression,
                operator: parser_interface_1.BinaryOperator.Divide,
                left,
                right,
            })],
        ['Factor', (factor) => factor],
    ],
    // Next precedence: Exponentiation (right-associative) and Unary Negation
    Factor: [
        ['Atom POWER Factor', (base, _pow, exponent) => ({
                kind: parser_interface_1.ASTNodeKind.BinaryExpression,
                operator: parser_interface_1.BinaryOperator.Power,
                left: base,
                right: exponent,
            })],
        ['MINUS Atom', (_minus, argument) => ({
                kind: parser_interface_1.ASTNodeKind.UnaryExpression,
                operator: parser_interface_1.UnaryOperator.Negate,
                argument,
            })],
        ['Atom', (atom) => atom],
    ],
    // Highest precedence: Numbers, Variables, Constants, Parenthesized expressions, Function calls
    Atom: [
        ['NUMBER', (tokenText) => ({
                kind: parser_interface_1.ASTNodeKind.NumberLiteral,
                value: parseFloat(tokenText),
            })],
        ['VARIABLE', (tokenText) => ({
                kind: parser_interface_1.ASTNodeKind.Variable,
                name: tokenText,
            })],
        ['PI_KEYWORD', (_tokenText) => ({
                kind: parser_interface_1.ASTNodeKind.Constant,
                name: 'pi',
            })],
        ['E_KEYWORD', (_tokenText) => ({
                kind: parser_interface_1.ASTNodeKind.Constant,
                name: 'e',
            })],
        ['LPAREN Expression RPAREN', (_lp, expr, _rp) => expr],
        ['FunctionCall', (funcCall) => funcCall],
    ],
    FunctionCall: [
        ['LN_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"ln\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Ln, args: args };
            }],
        ['LOG_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"log\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Log, args: args };
            }],
        ['LOG_BASE_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length === 1) {
                    // As per documentation, log_base(value) defaults to base 10, equivalent to log(value)
                    return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Log, args: args };
                }
                else if (args.length === 2) {
                    return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.LogBase, args: args };
                }
                else {
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"log_base\". Expected 1 or 2, got " + args.length + ".");
                }
            }],
        ['SIN_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"sin\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Sin, args: args };
            }],
        ['COS_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"cos\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Cos, args: args };
            }],
        ['TAN_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"tan\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Tan, args: args };
            }],
        ['CSC_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"csc\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Csc, args: args };
            }],
        ['SEC_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"sec\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Sec, args: args };
            }],
        ['COT_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"cot\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Cot, args: args };
            }],
        ['ARCSIN_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"arcsin\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Arcsin, args: args };
            }],
        ['ARCCOS_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"arccos\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Arccos, args: args };
            }],
        ['ARCTAN_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"arctan\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Arctan, args: args };
            }],
        ['ARCCSC_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"arccsc\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Arccsc, args: args };
            }],
        ['ARCSEC_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"arcsec\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Arcsec, args: args };
            }],
        ['ARCCOT_KEYWORD LPAREN Arguments RPAREN', (_nameToken, _lp, args, _rp) => {
                if (args.length !== 1)
                    throw new Error("Invalid expression: Incorrect number of arguments for function \"arccot\". Expected 1, got " + args.length + ".");
                return { kind: parser_interface_1.ASTNodeKind.FunctionCall, name: parser_interface_1.FunctionName.Arccot, args: args };
            }],
    ],
    Arguments: [
        ['Expression COMMA Arguments', (expr, _comma, args) => [expr, ...args]],
        ['Expression', (expr) => [expr]],
        [] // Allow empty arguments, for functions like `log_base()` which might lead here.
    ],
};
// Combine tokens and grammar rules into a single object for the Parser constructor
const combinedGrammar = {
    tokens: tokens,
    start: 'Expression', // The starting rule of the grammar
    ...grammarRules,
};
const parserLibInstance = new Parser(combinedGrammar); // Instantiate the parser globally
// 3. Implement the parse function
const parse = (expression) => {
    if (!expression || expression.trim() === '') {
        throw new Error('Invalid expression: Empty string.');
    }
    const trimmedExpression = expression.trim();
    let openParens = 0;
    let closeParens = 0;
    for (const char of trimmedExpression) {
        if (char === '(')
            openParens++;
        else if (char === ')')
            closeParens++;
    }
    if (openParens !== closeParens) {
        throw new Error('Invalid expression: Unmatched parenthesis.');
    }
    let ast;
    let variables = {};
    try {
        // parserlib's parse method handles lexing internally based on the lexer created with createLexer
        ast = parserLibInstance.parse(trimmedExpression);
        // Traverse AST to collect variables
        const collectVariables = (node) => {
            if (node.kind === parser_interface_1.ASTNodeKind.Variable) {
                variables[node.name] = undefined;
            }
            else if (node.kind === parser_interface_1.ASTNodeKind.BinaryExpression) {
                collectVariables(node.left);
                collectVariables(node.right);
            }
            else if (node.kind === parser_interface_1.ASTNodeKind.UnaryExpression) {
                collectVariables(node.argument);
            }
            else if (node.kind === parser_interface_1.ASTNodeKind.FunctionCall) {
                node.args.forEach(collectVariables);
            }
        };
        collectVariables(ast);
    }
    catch (e) {
        const message = e.message || 'Unknown parsing error.';
        // Lexer errors: No lexing rule matches
        if (message.includes('No lexing rule matches')) {
            const unexpectedCharMatch = message.match(/No lexing rule matches "([^"]+)" at offset (\d+)/);
            if (unexpectedCharMatch) {
                const unexpectedText = unexpectedCharMatch[1];
                // Handle 'pipi', 'PI' as "Unknown constant"
                if (unexpectedText.match(/^[a-zA-Z_][a-zA-Z0-9_]*$/) && !Object.values(parser_interface_1.FunctionName).some(f => f.toLowerCase() === unexpectedText.toLowerCase())) {
                    throw new Error("Invalid expression: Unknown constant \"" + unexpectedText + "\"."); // Added unexpectedText to message
                }
                // Handle numbers with trailing/multiple decimals like '5.' or '1.2.3'
                // The new NUMBER regex should prevent matching '5.' or '.5' as a full number.
                // If it's '5.', then '5' is matched as NUMBER, and '.' is left as unexpected.
                // If it's '.5', then '.' is left as unexpected.
                // If it's '1.2.3', then '1.2' is matched as NUMBER, and '.3' is left as unexpected.
                // So, we need to catch these "unexpected character" cases more generically.
                if (unexpectedText === '.') {
                    throw new Error("Invalid expression: Unexpected character \".\".");
                }
                // Generic unexpected characters like '$'
                throw new Error("Invalid expression: Unexpected character \"" + unexpectedText + "\".");
            }
            throw new Error("Invalid expression: Unexpected character or malformed syntax.");
        }
        // Parser errors: Unexpected end of input
        if (message.includes('Unexpected end of input')) {
            // Check if it's due to a function name without parentheses (e.g., 'sin')
            const potentialFunctionNameMatch = trimmedExpression.match(/([a-zA-Z_][a-zA-Z0-9_]*)\\s*$/);
            if (potentialFunctionNameMatch && Object.values(parser_interface_1.FunctionName).some(f => f.toLowerCase() === potentialFunctionNameMatch[1].toLowerCase())) {
                throw new Error("Invalid expression: Function name \"" + potentialFunctionNameMatch[1] + "\" used without parentheses.");
            }
            throw new Error('Invalid expression: Unexpected end of expression.');
        }
        // Parser errors: Unexpected token
        if (message.includes('Unexpected token')) {
            const unexpectedTokenMatch = message.match(/Unexpected token "([^"]+)" at offset (\\d+)/);
            const offset = unexpectedTokenMatch ? parseInt(unexpectedTokenMatch[2]) : -1;
            const unexpectedTokenText = unexpectedTokenMatch?.[1];
            // Check for starting with a binary operator (e.g., '* 5', '+5')
            if (offset === 0 && (unexpectedTokenText === '*' || unexpectedTokenText === '/' || unexpectedTokenText === '^' || unexpectedTokenText === '+')) {
                throw new Error('Invalid expression: Unexpected token at start of expression.');
            }
            // Check for constant used as a function (e.g., 'pi()')
            if (unexpectedTokenText === '(') {
                const charBeforeParen = trimmedExpression[offset - 1];
                if (charBeforeParen === 'i' && trimmedExpression.substring(offset - 2, offset) === 'pi') {
                    throw new Error("Invalid expression: Unexpected token after constant.");
                }
                if (charBeforeParen === 'e' && trimmedExpression.substring(offset - 1, offset) === 'e') {
                    throw new Error("Invalid expression: Unexpected token after constant.");
                }
            }
            // Generic missing operator logic (e.g. '2(3+4)', 'x(3+4)', '2x', 'pi x', 'pi e', 'xy', ')(')
            const prevTokenChar = offset > 0 ? trimmedExpression[offset - 1] : '';
            const nextTokenChar = unexpectedTokenText ? unexpectedTokenText[0] : '';
            const isOperandStartChar = (c) => /[a-zA-Z0-9(]/.test(c);
            const isOperandEndChar = (c) => /[a-zA-Z0-9)]/.test(c);
            // This rule is for cases like '2x', 'x(', ')('
            if ((isOperandEndChar(prevTokenChar) && nextTokenChar === '(') || // e.g., '2(', 'x(', ')('
                (isOperandEndChar(prevTokenChar) && isOperandStartChar(nextTokenChar) && nextTokenChar !== '(') || // e.g., '2x', 'xy', 'pi x', 'pi e' (excluding cases where next is '(')
                (prevTokenChar === ')' && isOperandStartChar(nextTokenChar)) // e.g., ')x'
            ) {
                throw new Error('Invalid expression: Missing operator between operands.');
            }
            // Specific check for function name without parentheses (e.g., 'sin x', 'sin pi', 'sin')
            // This is primarily for when the unexpected token is an operand *after* a function keyword.
            const potentialFuncKeyword = trimmedExpression.substring(0, offset).match(/([a-zA-Z_][a-zA-Z0-9_]*)\\s*$/)?.[1];
            if (potentialFuncKeyword && Object.values(parser_interface_1.FunctionName).some(f => f.toLowerCase() === potentialFuncKeyword.toLowerCase()) && isOperandStartChar(nextTokenChar)) {
                throw new Error('Invalid expression: Missing operator between function name and operand.');
            }
            // If the unexpected token IS a function name and it's not followed by '(', then it's used without parentheses.
            if (unexpectedTokenText && Object.values(parser_interface_1.FunctionName).some(f => f.toLowerCase() === unexpectedTokenText.toLowerCase())) {
                throw new Error("Invalid expression: Function name \"" + unexpectedTokenText + "\" used without parentheses.");
            }
            throw new Error("Invalid expression: Unexpected token \"" + unexpectedTokenText + "\".");
        }
        // Re-throw custom errors from grammar rules (e.g., incorrect argument count)
        if (message.includes('Incorrect number of arguments for function')) {
            throw e;
        }
        // Fallback for any other unexpected parserlib errors
        throw new Error("Invalid expression: " + message);
    }
    return { ast, variables };
};
exports.parse = parse;
