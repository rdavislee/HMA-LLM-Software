import {
  ExpressionNode, // Import base class ExpressionNode
  NumberNode,
  VariableNode,
  BinaryOperationNode,
  UnaryOperationNode,
  FunctionCallNode,
  ConstantNode, // ADDED: ConstantNode
} from './expression'; // Import concrete classes
import {
  Expression, // Import interface
  BinaryOperatorType,
  UnaryOperatorType,
  FunctionNameType,
  ConstantType // ADDED: ConstantType
} from './expressionInterface'; // Import types and enums

// Simple token stream manager
class TokenStream {
  private tokens: string[];
  private currentIndex: number = 0;

  constructor(input: string) {
    this.tokens = this.tokenize(input);
  }

  // Basic tokenizer:
  // - Recognizes numbers (integers and floats)
  // - Recognizes variables/function names (alphabetic sequences)
  // - Recognizes operators and parentheses
  private tokenize(expression: string): string[] {
    // Regex for tokens:
    // 1. Numbers: \d+(\.\d*)?|\.\d+ (handles numbers like 123, 3.14, or .5)
    // 2. Variable/Function names: [a-zA-Z_]+
    // 3. Operators: \+|\-|\*|\/|\^|\(|\)|, (single character operators)
    const regex = /(\d+(\.\d*)?|\.\d+|[a-zA-Z_]+|\+|\-|\*|\/|\^|\(|\)|,)/g;
    let match;
    const result: string[] = [];
    while ((match = regex.exec(expression)) !== null) {
      if (match[0].trim() !== '') { // Ensure no empty matches from weird regex behavior
        result.push(match[0]);
      }
    }
    return result;
  }

  peek(): string | undefined {
    return this.tokens[this.currentIndex];
  }

  consume(): string {
    if (this.currentIndex >= this.tokens.length) {
      throw new Error('Unexpected end of input');
    }
    return this.tokens[this.currentIndex++];
  }

  // Consume a token only if it matches the expected type
  expect(expected: string): string {
    const token = this.consume();
    if (token !== expected) {
      throw new Error(`Expected '${expected}' but got '${token}'`);
    }
    return token;
  }

  // Check if current token matches and consume it
  match(expected: string): boolean {
    if (this.peek() === expected) {
      this.consume();
      return true;
    }
    return false;
  }

  isAtEnd(): boolean {
    return this.currentIndex >= this.tokens.length;
  }
}

export function parse(input: string): Expression {
  const stream = new TokenStream(input.trim());

  // parseFactor: Handles numbers, variables, function calls, and parenthesized expressions.
  function parseFactor(): ExpressionNode { // Changed return type to ExpressionNode
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
      return new NumberNode(Number(stream.consume()));
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
      const constants: ConstantType[] = ['e', 'pi'];
      if (constants.includes(name as ConstantType)) {
        return new ConstantNode(name as ConstantType);
      }

      if (stream.match('(')) { // It's a function call
        const args: ExpressionNode[] = []; // Changed type here to ExpressionNode[]
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
        const functionNames: FunctionNameType[] = [
          'log', 'ln', 'exp',
          'sin', 'cos', 'tan',
          'sec', 'csc', 'cot',
          'asin', 'acos', 'atan',
          'asec', 'acsc', 'acot',
          'sinh', 'cosh', 'tanh',
          'asinh', 'acosh', 'atanh'
        ];
        if (!functionNames.includes(name as FunctionNameType)) {
          throw new Error(`Unknown function: ${name}`);
        }
        return new FunctionCallNode(name as FunctionNameType, args as ExpressionNode[]); // Explicit cast for args
      } else { // It's a variable
        return new VariableNode(name);
      }
    }

    throw new Error(`Unexpected token at factor: ${token}`);
  }

  // parseUnary: Handles unary negation.
  function parseUnary(): ExpressionNode { // Changed return type to ExpressionNode
    if (stream.match('-')) {
      const operand = parseUnary(); // Allow nested unary operations (--x)
      return new UnaryOperationNode('negate', operand as ExpressionNode); // Explicit cast for operand
    }
    return parseFactor();
  }

  // parsePower: Handles exponentiation (right-associative).
  function parsePower(): ExpressionNode { // Changed return type to ExpressionNode
    let left = parseUnary();
    while (stream.match('^')) {
      const right = parsePower(); // Right-associative
      left = new BinaryOperationNode('power', left as ExpressionNode, right as ExpressionNode); // Explicit casts for left and right
    }
    return left;
  }

  // parseTerm: Handles multiplication and division (left-associative).
  function parseTerm(): ExpressionNode { // Changed return type to ExpressionNode
    let left = parsePower();
    while (stream.peek() === '*' || stream.peek() === '/') {
      const operatorToken = stream.consume();
      const right = parsePower();
      left = new BinaryOperationNode(
        operatorToken === '*' ? 'multiply' : 'divide',
        left as ExpressionNode, // Explicit cast for left
        right as ExpressionNode, // Explicit cast for right
      );
    }
    return left;
  }

  // parseExpression: Handles addition and subtraction (left-associative).
  function parseExpression(): ExpressionNode { // Changed return type to ExpressionNode
    let left = parseTerm();
    while (stream.peek() === '+' || stream.peek() === '-') {
      const operatorToken = stream.consume();
      const right = parseTerm();
      left = new BinaryOperationNode(
        operatorToken === '+' ? 'add' : 'subtract',
        left as ExpressionNode, // Explicit cast for left
        right as ExpressionNode, // Explicit cast for right
      );
    }
    return left;
  }

  const result = parseExpression();
  if (!stream.isAtEnd()) {
    throw new Error(`Unexpected tokens at end of input: ${stream.peek()}`);
  }
  return result;
}