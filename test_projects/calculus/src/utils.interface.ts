import { Expression, ExpressionNode } from './expressionInterface';

/**
 * @file Defines TypeScript interfaces for utility functions related to expression manipulation.
 */

/**
 * Represents a context for evaluating expressions, mapping variable names to their numeric values.
 * @example
 * { x: 5, y: 10 }
 */
export interface EvaluationContext {
    [variableName: string]: number;
}

/**
 * Evaluates a given expression node within a specific context of variable values.
 * @precondition `expression` is a valid Expression.
 * @precondition All variables in `expression` must have corresponding numeric values in `context`.
 * @postcondition Returns the numeric result of the expression evaluation.
 * @param expression The root node of the expression AST to evaluate.
 * @param context An object mapping variable names to their numeric values.
 * @returns The numeric result of the expression.
 * @throws {Error} If a variable in the expression is not found in the context.
 * @throws {Error} If an invalid operation or function call is encountered during evaluation.
 */
export interface ExpressionEvaluator {
    evaluate(expression: ExpressionNode, context: EvaluationContext): number;
}

/**
 * Computes the symbolic derivative of a given expression with respect to a specified variable.
 * @precondition `expression` is a valid Expression.
 * @precondition `variable` is a string representing the variable to differentiate with respect to (e.g., 'x').
 * @postcondition Returns a new ExpressionNode representing the derivative.
 * @param expression The root node of the expression AST to differentiate.
 * @param variable The name of the variable with respect to which the differentiation is performed.
 * @returns A new ExpressionNode representing the derivative of the input expression.
 * @throws {Error} If the differentiation rules for a specific node type are not implemented.
 */
export interface ExpressionDifferentiator {
    differentiate(expression: ExpressionNode, variable: string): ExpressionNode;
}

/**
 * Represents the result of an indefinite symbolic integration.
 * @property unintegratable Indicates if the expression could not be integrated symbolically.
 * @property integratedExpression The expression representing the antiderivative, or a special string if unintegratable.
 * @property constantOfIntegration A string representing the constant of integration (e.g., 'C'), or null if unintegratable.
 */
export interface IntegrationResult {
    unintegratable: boolean;
    integratedExpression: ExpressionNode | "UNINTEGRATABLE_EXPRESSION";
    constantOfIntegration: string | null; // Typically 'C' or similar, or null if unintegratable
}

/**
 * Defines options for numerical integration methods.
 * @property numRectangles Optional. The number of rectangles to use for numerical integration (e.g., Riemann sum).
 *                         If not provided, a default or adaptive method should be used by the implementation.
 */
export interface IntegrationOptions {
    numRectangles?: number;
}

/**
 * Computes the symbolic indefinite or definite integral of a given expression with respect to a specified variable.
 * @precondition `expression` is a valid Expression.
 * @precondition `variable` is a string representing the variable to integrate with respect to (e.g., 'x').
 */
export interface ExpressionIntegrator {
    /**
     * Computes the symbolic indefinite integral of a given expression.
     * @param expression The root node of the expression AST to integrate.
     * @param variable The name of the variable with respect to which the integration is performed.
     * @returns An IntegrationResult object.
     * @throws {Error} If the integration rules for a specific node type are not implemented.
     */
    integrateIndefinite(expression: ExpressionNode, variable: string): IntegrationResult;

    /**
     * Computes the definite integral of a given expression over a specified range.
     * @precondition `expression` is a valid Expression.
     * @precondition `variable` is a string representing the variable of integration.
     * @precondition `lowerBound` and `upperBound` are numbers representing the limits of integration.
     * @postcondition Returns the numeric result of the definite integral.
     * @param expression The root node of the expression AST to integrate.
     * @param variable The name of the variable with respect to which the integration is performed.
     * @param lowerBound The lower limit of integration.
     * @param upperBound The upper limit of integration.
     * @param options Optional. Options for the integration method, such as the number of rectangles for numerical integration.
     * @returns The numeric result of the definite integral.
     * @throws {Error} If the expression cannot be integrated or evaluated within the given bounds.
     */
    integrateDefinite(expression: ExpressionNode, variable: string, lowerBound: number, upperBound: number, options?: IntegrationOptions): number;
}

/**
 * Simplifies a given expression.
 * @precondition `expression` is a valid Expression.
 * @postcondition Returns a new ExpressionNode representing the simplified form.
 * @param expression The root node of the expression AST to simplify.
 * @returns A new ExpressionNode representing the simplified form of the input expression.
 * @throws {Error} If the simplification rules for a specific node type are not implemented or an invalid state is reached.
 */
export interface ExpressionSimplifier {
    simplify(expression: ExpressionNode): ExpressionNode;
}