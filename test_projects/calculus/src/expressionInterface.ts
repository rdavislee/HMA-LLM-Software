/**
 * @file Defines TypeScript interfaces for Abstract Syntax Tree (AST) nodes
 *       representing mathematical expressions.
 */

/**
 * Base interface for all AST expression nodes.
 * All specific expression nodes must extend this interface.
 * Includes a method for string representation of the expression.
 */
export interface Expression {
    /** A string literal discriminating the type of the expression node. */
    type: string;
    /**
     * Returns a string representation of the expression.
     * @returns The string representation.
     */
    toString(): string;
    /**
     * Evaluates the expression with given variable values.
     * @param variables A map of variable names to their numerical values.
     * @returns The numerical result of the expression.
     */
    evaluate(variables: Record<string, number>): number;
    /**
     * Computes the derivative of the expression with respect to a specified variable.
     * @param variableName The name of the variable to differentiate with respect to.
     * @returns A new ExpressionNode representing the derivative.
     */
    differentiate(variableName: string): ExpressionNode;
}

/**
 * Represents a numeric literal in the expression.
 * @precondition value is a finite number.
 */
export interface NumberNode extends Expression {
    type: 'number';
    value: number;
}

/**
 * Represents a variable in the expression.
 * @precondition name is a valid identifier (e.g., 'x', 'y', 'theta').
 */
export interface VariableNode extends Expression {
    type: 'variable';
    name: string;
}

/**
 * Defines the set of supported binary operators.
 */
export type BinaryOperatorType = 'add' | 'subtract' | 'multiply' | 'divide' | 'power';

/**
 * Represents a binary operation (e.g., Addition, Subtraction, Multiplication, Division, Power).
 * @precondition left and right are valid Expression nodes.
 */
export interface BinaryOperationNode extends Expression {
    type: 'binaryOperation';
    operator: BinaryOperatorType;
    left: ExpressionNode;
    right: ExpressionNode;
}

/**
 * Defines the set of supported unary operators.
 */
export type UnaryOperatorType = 'negate';

/**
 * Represents a unary operation (e.g., Negation).
 * @precondition operand is a valid Expression node.
 */
export interface UnaryOperationNode extends Expression {
    type: 'unaryOperation';
    operator: UnaryOperatorType;
    operand: ExpressionNode;
}

/**
 * Defines the set of supported function names.
 */
export type FunctionNameType =
    'log' | 'ln' | 'exp' | // Existing
    'sin' | 'cos' | 'tan' | // Existing trigonometric
    'sec' | 'csc' | 'cot' | // New trigonometric
    'asin' | 'acos' | 'atan' | // New inverse trigonometric (abbreviated)
    'arcsin' | 'arccos' | 'arctan' | // New inverse trigonometric (full names)
    'asec' | 'acsc' | 'acot' | // New inverse trigonometric
    'sinh' | 'cosh' | 'tanh' | // New hyperbolic trigonometric
    'asinh' | 'acosh' | 'atanh' | // New inverse hyperbolic trigonometric
    'sqrt' | 'abs' | 'ceil' | 'floor' | 'round'; // New mathematical functions

/**
 * Represents a function call (e.g., Log, Sin, Cos, Tan).
 * @precondition name is a valid FunctionNameType.
 * @precondition args is an array of valid Expression nodes.
 * @precondition For all supported functions, args must contain exactly one element.
 */
export interface FunctionCallNode extends Expression {
    type: 'functionCall';
    name: FunctionNameType;
    args: ExpressionNode[];
}

/**
 * Defines the set of supported mathematical constants.
 */
export type ConstantType = 'e' | 'pi';

/**
 * Represents a mathematical constant (e.g., 'e', 'pi').
 */
export interface ConstantNode extends Expression {
    type: 'constant';
    name: ConstantType;
}

/**
 * Represents the exponential function e^x.
 * This is distinct from a general power operation to allow specific handling for differentiation/integration.
 * @precondition exponent is a valid Expression node.
 */
export interface ExponentialNode extends Expression {
    type: 'exponential';
    exponent: ExpressionNode;
}

/**
 * A union type representing any possible AST expression node.
 */
export type ExpressionNode =
    NumberNode |
    VariableNode |
    BinaryOperationNode |
    UnaryOperationNode |
    FunctionCallNode |
    ConstantNode |
    ExponentialNode;
