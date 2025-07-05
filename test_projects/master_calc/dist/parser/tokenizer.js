import { TokenType } from '../types/tokens.js';
import { CalculatorError } from '../utils/error.js';
export function tokenize(expression) {
    const tokens = [];
    let position = 0;
    const operators = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULTIPLY,
        '/': TokenType.DIVIDE,
        '^': TokenType.POWER,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        ',': TokenType.COMMA,
    };
    // Ordered by length descending to prioritize longer matches (e.g., 'arcsin' before 'sin')
    // and then alphabetically for consistency among same-length keywords.
    // This order is critical for correct tokenization of functions and constants.
    const keywords = [
        'arcsin', 'arccos', 'arctan', 'arccsc', 'arcsec', 'arccot',
        'sin', 'cos', 'tan', 'csc', 'sec', 'cot', 'log', 'ln',
        'pi', 'e'
    ];
    // Map keywords to their TokenType
    const keywordTokenMap = {
        'arcsin': TokenType.ARCSIN, 'arccos': TokenType.ARCCOS, 'arctan': TokenType.ARCTAN,
        'arccsc': TokenType.ARCCSC, 'arcsec': TokenType.ARCSEC, 'arccot': TokenType.ARCCOT,
        'sin': TokenType.SIN, 'cos': TokenType.COS,
        'tan': TokenType.TAN, 'csc': TokenType.CSC, 'sec': TokenType.SEC,
        'cot': TokenType.COT, 'log': TokenType.LOG, 'ln': TokenType.LN,
        'pi': TokenType.CONSTANT, 'e': TokenType.CONSTANT,
    };
    while (position < expression.length) {
        let char = expression[position];
        // 1. Whitespace
        if (/\s/.test(char)) {
            position++;
            continue;
        }
        // 2. Numbers
        // Matches integers, decimals (e.g., 123, 123.45, .45)
        if (/\d/.test(char) || (char === '.' && position + 1 < expression.length && /\d/.test(expression[position + 1]))) {
            let start = position;
            while (position < expression.length && (/\d|\./.test(expression[position]))) {
                position++;
            }
            const value = expression.substring(start, position);
            // Basic validation for multiple decimal points
            if ((value.match(/\./g) || []).length > 1) {
                throw new CalculatorError(`Syntax Error: Invalid number format "${value}" at position ${start}`);
            }
            // Ensure it's not just a standalone dot (e.g., "3 + .")
            tokens.push({ type: TokenType.NUMBER, value, position: start });
            continue;
        }
        // 3. Operators and Parentheses
        if (operators[char]) {
            tokens.push({ type: operators[char], value: char, position });
            position++;
            continue;
        }
        // 4. Functions, Constants (multi-character first, then single)
        let matchedKeyword = false;
        for (const keyword of keywords) { // Iterate through pre-sorted keywords
            if (expression.substring(position, position + keyword.length) === keyword) {
                // Ensure it's a full word match (e.g., 'sin' not part of 'sins', 'e' not part of 'exp')
                // A keyword must be followed by a non-alphanumeric character or end of string
                const nextChar = expression[position + keyword.length];
                if (nextChar === undefined || !/[a-zA-Z0-9]/.test(nextChar)) {
                    const type = keywordTokenMap[keyword];
                    tokens.push({ type, value: keyword, position });
                    position += keyword.length;
                    matchedKeyword = true;
                    break;
                }
            }
        }
        if (matchedKeyword) {
            continue;
        }
        // 5. Variables (single or multi-character, if not a keyword)
        // A variable starts with a letter and can contain letters or numbers.
        if (/[a-zA-Z]/.test(char)) {
            let start = position;
            while (position < expression.length && /[a-zA-Z0-9]/.test(expression[position])) {
                position++;
            }
            const value = expression.substring(start, position);
            // After checking against keywords, if it's still a letter sequence, it's a variable.
            tokens.push({ type: TokenType.VARIABLE, value, position: start });
            continue;
        }
        // If none of the above, it's an unrecognized character
        throw new CalculatorError(`Unknown character '${char}' at position ${position}`);
    }
    return tokens;
}
