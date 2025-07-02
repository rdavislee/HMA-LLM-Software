/**
 * @file src/expressionInterface.ts
 * Defines TypeScript interfaces for the recursive expression object.
 */

/**
 * Represents the base interface for any expression in the abstract syntax tree.
 * All specific expression types (number, variable, operation) will implement this.
 * @method evaluate - Evaluates the expression given a dictionary of variable values.
 * @param variables - An object mapping variable names (strings) to their numeric values.
 * @returns The numeric result of the expression evaluation.
 */
export interface IExpression {
    evaluate(variables: { [key: string]: number }): number;
}

/**
 * Represents a numeric literal expression (e.g., 5, 3.14).
 */
export interface INumberExpression extends IExpression {
    type: 'number';
    value: number;
}

/**
 * Represents a variable expression (e.g., x, y, pi).
 */
export interface IVariableExpression extends IExpression {
    type: 'variable';
    name: string;
}

/**
 * Represents a binary operation expression (e.g., a + b, x * y).
 */
export interface IBinaryOperationExpression extends IExpression {
    type: 'binaryOperation';
    operator: '+' | '-' | '*' | '/' | '^';
    left: Expression; // Use the union type for recursive definition
    right: Expression; // Use the union type for recursive definition
}

/**
 * Represents a unary operation expression (e.g., -x, +y).
 */
export interface IUnaryOperationExpression extends IExpression {
    type: 'unaryOperation';
    operator: '+' | '-'; // Unary plus or minus (negation)
    operand: Expression; // Use the union type for recursive definition
}

/**
 * Represents an expression explicitly wrapped in parentheses.
 * While parentheses primarily affect parsing precedence, including this
 * type allows for explicit representation in the AST if desired by the parser.
 */
export interface IParenthesizedExpression extends IExpression {
    type: 'parenthesized';
    expression: Expression; // The expression contained within the parentheses
}

/**
 * A union type representing any valid expression node in the AST.
 * This allows for recursive definition of expression trees.
 */
export type Expression =
    | INumberExpression
    | IVariableExpression
    | IBinaryOperationExpression
    | IUnaryOperationExpression
    | IParenthesizedExpression;
