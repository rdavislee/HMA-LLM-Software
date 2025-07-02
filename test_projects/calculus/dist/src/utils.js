"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExpressionUtils = void 0;
const expression_1 = require("./expression");
// Helper functions to create nodes using the Expression class
const num = (value) => new expression_1.NumberNode(value);
const variable = (name) => new expression_1.VariableNode(name);
// FIX: Corrected the order of arguments for the 'op' helper function to match its usage and common convention
const op = (left, operator, right) => new expression_1.BinaryOperationNode(operator, left, right);
const func = (name, args) => new expression_1.FunctionCallNode(name, args);
const unaryOp = (operator, operand) => new expression_1.UnaryOperationNode(operator, operand); // Added for convenience
/**
 * ExpressionUtils provides a suite of utility functions for manipulating
 * and analyzing mathematical expressions represented as Abstract Syntax Trees (ASTs).
 * This includes evaluation, symbolic differentiation, symbolic/numerical integration,
 * and symbolic simplification.
 */
class ExpressionUtils {
    /**
     * Evaluates a given expression node within a specific context of variable values.
     * @param expression The root node of the expression AST to evaluate.
     * @param context An object mapping variable names to their numeric values.
     * @returns The numeric result of the expression.
     * @throws {Error} If a variable in the expression is not found in the context.
     * @throws {Error} If an invalid operation or function call is encountered during evaluation.
     */
    evaluate(expression, context) {
        switch (expression.type) {
            case 'number':
                const numExpr = expression;
                return numExpr.value;
            case 'variable':
                const varExpr = expression;
                // FIX: Corrected template literal for error message to string concatenation
                if (!(varExpr.name in context)) {
                    throw new Error("Undefined variable '" + varExpr.name + "' in context.");
                }
                return context[varExpr.name];
            case 'binaryOperation':
                const binOpExpr = expression;
                const leftVal = this.evaluate(binOpExpr.left, context);
                const rightVal = this.evaluate(binOpExpr.right, context);
                switch (binOpExpr.operator) {
                    case 'add': return leftVal + rightVal;
                    case 'subtract': return leftVal - rightVal;
                    case 'multiply': return leftVal * rightVal;
                    case 'divide':
                        if (rightVal === 0)
                            throw new Error("Division by zero.");
                        return leftVal / rightVal;
                    case 'power': return Math.pow(leftVal, rightVal);
                    default:
                        throw new Error("Unsupported operator: " + binOpExpr.operator);
                }
            case 'functionCall':
                const funcCallExpr = expression;
                const argVals = funcCallExpr.args.map(arg => this.evaluate(arg, context));
                switch (funcCallExpr.name) {
                    case 'sin': return Math.sin(argVals[0]);
                    case 'cos': return Math.cos(argVals[0]);
                    case 'tan': return Math.tan(argVals[0]);
                    case 'log': // Common logarithm (base 10)
                        if (argVals[0] <= 0)
                            throw new Error("Logarithm of non-positive number.");
                        return Math.log10(argVals[0]);
                    case 'ln': // Natural logarithm
                        if (argVals[0] <= 0)
                            throw new Error("Logarithm of non-positive number.");
                        return Math.log(argVals[0]);
                    case 'exp': return Math.exp(argVals[0]);
                    case 'sqrt':
                        if (argVals[0] < 0)
                            throw new Error("Square root of negative number.");
                        return Math.sqrt(argVals[0]);
                    case 'abs': return Math.abs(argVals[0]);
                    default:
                        throw new Error("Unsupported function: " + funcCallExpr.name);
                }
            case 'unaryOperation':
                const unOpExpr = expression;
                const operandVal = this.evaluate(unOpExpr.operand, context);
                switch (unOpExpr.operator) {
                    case 'negate': return -operandVal;
                    default: throw new Error("Unsupported unary operator: " + unOpExpr.operator);
                }
            case 'constant':
                const constExpr = expression;
                switch (constExpr.name) {
                    case 'e': return Math.E;
                    case 'pi': return Math.PI;
                    default: throw new Error("Unsupported constant: " + constExpr.name);
                }
            case 'exponential':
                const expExpr = expression;
                const exponentVal = this.evaluate(expExpr.exponent, context);
                return Math.exp(exponentVal);
            default:
                throw new Error("Unknown expression node type: " + expression.type);
        }
    }
    /**
     * Computes the symbolic derivative of a given expression with respect to a specified variable.
     * Limited to basic differentiation rules.
     * @param expression The root node of the expression AST to differentiate.
     * @param targetVariable The name of the variable with respect to which the differentiation is performed.
     * @returns A new ExpressionNode representing the derivative of the input expression.
     * @throws {Error} If the differentiation rules for a specific node type are not implemented or an unsupported case is encountered.
     */
    differentiate(expression, targetVariable) {
        let result;
        switch (expression.type) {
            case 'number':
                result = num(0);
                break;
            case 'variable':
                const varExpr = expression;
                result = varExpr.name === targetVariable ? num(1) : num(0);
                break;
            case 'binaryOperation':
                const binOpExpr = expression;
                const u = binOpExpr.left;
                const v = binOpExpr.right;
                const du = this.differentiate(u, targetVariable);
                const dv = this.differentiate(v, targetVariable);
                switch (binOpExpr.operator) {
                    case 'add':
                    case 'subtract':
                        // FIX: Corrected argument order for 'op' helper
                        result = op(du, binOpExpr.operator, dv);
                        break;
                    case 'multiply':
                        // FIX: Corrected argument order for 'op' helper
                        result = op(op(du, 'multiply', v), 'add', op(u, 'multiply', dv));
                        break;
                    case 'divide':
                        // FIX: Corrected argument order for 'op' helper
                        result = op(op(du, 'multiply', v), 'subtract', op(u, 'multiply', dv));
                        result = op(result, 'divide', op(v, 'power', num(2)));
                        break;
                    case 'power':
                        if (v.type === 'number') {
                            const n = v.value;
                            if (u.type === 'number') {
                                result = num(0);
                                break;
                            }
                            // FIX: Corrected argument order for 'op' helper
                            result = op(num(n), 'multiply', op(op(u, 'power', num(n - 1)), 'multiply', du));
                            break;
                        }
                        else if (u.type === 'number') {
                            const c = u.value;
                            if (c === 0) {
                                result = num(0);
                                break;
                            }
                            if (c === 1) {
                                result = num(0);
                                break;
                            }
                            // FIX: Corrected argument order for 'op' helper
                            result = op(op(u, 'power', v), 'multiply', op(func('ln', [u]), 'multiply', dv));
                            break;
                        }
                        else {
                            throw new Error("Differentiation of u^v where both u and v are non-constant expressions is not supported yet.");
                        }
                    default:
                        throw new Error("Unsupported operator for differentiation: " + binOpExpr.operator);
                }
                break;
            case 'functionCall':
                const funcCallExpr = expression;
                if (funcCallExpr.args.length !== 1) {
                    throw new Error("Differentiation of multi-argument functions like " + funcCallExpr.name + " is not supported yet.");
                }
                const arg = funcCallExpr.args[0];
                const darg = this.differentiate(arg, targetVariable);
                switch (funcCallExpr.name) {
                    case 'sin': // FIX: Corrected argument order for 'op' helper
                        result = op(func('cos', [arg]), 'multiply', darg);
                        break;
                    case 'cos': // FIX: Corrected argument order for 'op' helper
                        result = op(num(-1), 'multiply', op(func('sin', [arg]), 'multiply', darg));
                        break;
                    case 'tan': // FIX: Corrected argument order for 'op' helper
                        result = op(op(num(1), 'divide', op(func('cos', [arg]), 'power', num(2))), 'multiply', darg);
                        break;
                    case 'ln': // FIX: Corrected argument order for 'op' helper
                        result = op(op(num(1), 'divide', arg), 'multiply', darg);
                        break;
                    case 'exp': // FIX: Corrected argument order for 'op' helper and used op helper
                        result = op(new expression_1.ExponentialNode(arg), 'multiply', darg);
                        break;
                    case 'sqrt': // FIX: Corrected argument order for 'op' helper
                        result = op(op(num(1), 'divide', op(num(2), 'multiply', func('sqrt', [arg]))), 'multiply', darg);
                        break;
                    case 'abs':
                        throw new Error("Differentiation of absolute value function is not supported symbolically.");
                    case 'log':
                    case 'arcsin':
                    case 'arccos':
                    case 'arctan':
                        throw new Error("Differentiation of function " + funcCallExpr.name + " is not supported yet.");
                    default:
                        throw new Error("Unsupported function for differentiation: " + funcCallExpr.name);
                }
                break;
            case 'unaryOperation':
                const unOpExpr = expression;
                const dOperand = this.differentiate(unOpExpr.operand, targetVariable);
                result = new expression_1.UnaryOperationNode(unOpExpr.operator, dOperand);
                break;
            case 'constant':
                result = num(0);
                break;
            case 'exponential':
                const expExpr = expression;
                const dExponent = this.differentiate(expExpr.exponent, targetVariable);
                // FIX: Corrected argument order for 'op' helper
                result = op(new expression_1.ExponentialNode(expExpr.exponent), 'multiply', dExponent);
                break;
            default:
                throw new Error("Unknown expression node type for differentiation: " + expression.type);
        }
        return this.simplify(result);
    }
    _collectVariables(expression, variables) {
        switch (expression.type) {
            case 'number':
            case 'constant':
                break;
            case 'variable':
                variables.add(expression.name);
                break;
            case 'binaryOperation':
                const binOp = expression;
                this._collectVariables(binOp.left, variables);
                this._collectVariables(binOp.right, variables);
                break;
            case 'unaryOperation':
                this._collectVariables(expression.operand, variables);
                break;
            case 'functionCall':
                expression.args.forEach(arg => this._collectVariables(arg, variables));
                break;
            case 'exponential':
                this._collectVariables(expression.exponent, variables);
                break;
            default:
                break;
        }
    }
    /**
     * Computes the symbolic indefinite integral of a given expression.
     * Limited to basic integration rules.
     * @param expression The root node of the expression AST to integrate.
     * @param targetVariable The name of the variable with respect to which the integration is performed.
     * @returns An IntegrationResult object.
     * @throws {Error} If the integration rules for a specific node type are not implemented.
     */
    integrateIndefinite(expression, targetVariable) {
        let integratedExpr = null;
        let unintegratable = true;
        const getAntiderivative = (expr) => {
            switch (expr.type) {
                case 'number':
                    const numExpr = expr;
                    // FIX: Corrected argument order for 'op' helper
                    return op(numExpr, 'multiply', variable(targetVariable));
                case 'variable':
                    const varExpr = expr;
                    if (varExpr.name === targetVariable) {
                        // FIX: Corrected argument order for 'op' helper
                        return op(op(variable(targetVariable), 'power', num(2)), 'divide', num(2));
                    }
                    else {
                        // FIX: Corrected argument order for 'op' helper
                        return op(varExpr, 'multiply', variable(targetVariable));
                    }
                case 'binaryOperation':
                    const binOpExpr = expr;
                    if (binOpExpr.operator === 'divide' && binOpExpr.left.type === 'number' && binOpExpr.left.value === 1 &&
                        binOpExpr.right.type === 'variable' && binOpExpr.right.name === targetVariable) {
                        return func('ln', [variable(targetVariable)]);
                    }
                    if (binOpExpr.operator === 'add' || binOpExpr.operator === 'subtract') {
                        const leftAnti = getAntiderivative(binOpExpr.left);
                        const rightAnti = getAntiderivative(binOpExpr.right);
                        if (leftAnti !== "UNINTEGRATABLE_EXPRESSION" && rightAnti !== "UNINTEGRATABLE_EXPRESSION") {
                            // FIX: Corrected argument order for 'op' helper
                            return op(leftAnti, binOpExpr.operator, rightAnti);
                        }
                    }
                    else if (binOpExpr.operator === 'power' && binOpExpr.left.type === 'variable' && binOpExpr.left.name === targetVariable && binOpExpr.right.type === 'number') {
                        const n = binOpExpr.right.value;
                        if (n === -1) {
                            return func('ln', [variable(targetVariable)]);
                        }
                        else {
                            // FIX: Corrected argument order for 'op' helper
                            return op(op(variable(targetVariable), 'power', num(n + 1)), 'divide', num(n + 1));
                        }
                    }
                    else if (binOpExpr.operator === 'power') {
                        // Handle e^u forms (where base is 'e' constant)
                        if (binOpExpr.left.type === 'constant' && binOpExpr.left.name === 'e') {
                            const u = binOpExpr.right; // The exponent
                            // Case: e^x (u is the target variable)
                            if (u.type === 'variable' && u.name === targetVariable) {
                                return expr; // Integral of e^x is e^x
                            }
                            // Case: e^(ax) (u is a multiplication of a constant and the target variable)
                            if (u.type === 'binaryOperation' && u.operator === 'multiply') {
                                const product = u;
                                let aNode = null;
                                let xNode = null;
                                // Check for a*x or x*a
                                if (product.left.type === 'number' &&
                                    product.right.type === 'variable' &&
                                    product.right.name === targetVariable) {
                                    aNode = product.left;
                                    xNode = product.right;
                                }
                                else if (product.right.type === 'number' &&
                                    product.left.type === 'variable' &&
                                    product.left.name === targetVariable) {
                                    aNode = product.right;
                                    xNode = product.left;
                                }
                                if (aNode !== null && xNode !== null) {
                                    if (aNode.value === 0) {
                                        // Integral of e^0 (which is 1) is x
                                        return op(num(1), 'multiply', variable(targetVariable));
                                    }
                                    // Integral of e^(ax) is (1/a)e^(ax)
                                    const oneOverA = op(num(1), 'divide', aNode);
                                    return op(oneOverA, 'multiply', expr); // 'expr' here is the original e^(ax) node
                                }
                            }
                            // If it's e^u but u is not 'x' or 'ax', it's unintegratable by this rule
                            return "UNINTEGRATABLE_EXPRESSION";
                        }
                        // Extend a^x rule (where base 'a' is a number or a constant like pi, but not 'e')
                        if (binOpExpr.right.type === 'variable' && binOpExpr.right.name === targetVariable &&
                            (binOpExpr.left.type === 'number' || (binOpExpr.left.type === 'constant' && binOpExpr.left.name !== 'e'))) {
                            const baseNode = binOpExpr.left;
                            // Special handling for numerical base values
                            if (baseNode.type === 'number') {
                                const a = baseNode.value;
                                if (a <= 0) {
                                    return "UNINTEGRATABLE_EXPRESSION";
                                }
                                else if (a === 1) {
                                    return variable(targetVariable); // Integral of 1^x (which is 1) is x
                                }
                            }
                            // For other valid bases (e.g., NumberNode > 0 and != 1, or ConstantNode like 'pi')
                            return op(expr, 'divide', func('ln', [baseNode]));
                        }
                    }
                    else if (binOpExpr.operator === 'multiply') {
                        let constantFactor = null;
                        let functionFactor = null;
                        const isConstantFactorForIntegration = (node) => (node.type === 'number') ||
                            (node.type === 'constant') ||
                            (node.type === 'variable' && node.name !== targetVariable && node.name !== 'C');
                        if (isConstantFactorForIntegration(binOpExpr.left)) {
                            constantFactor = binOpExpr.left;
                            functionFactor = binOpExpr.right;
                        }
                        else if (isConstantFactorForIntegration(binOpExpr.right)) {
                            constantFactor = binOpExpr.right;
                            functionFactor = binOpExpr.left;
                        }
                        if (constantFactor !== null && functionFactor !== null) {
                            const integral_f_x = getAntiderivative(functionFactor);
                            if (integral_f_x !== "UNINTEGRATABLE_EXPRESSION") {
                                // FIX: Corrected argument order for 'op' helper
                                return op(constantFactor, 'multiply', integral_f_x);
                            }
                        }
                    }
                    break;
                case 'functionCall':
                    const funcCallExpr = expr;
                    if (funcCallExpr.args.length === 1 && funcCallExpr.args[0].type === 'variable' && funcCallExpr.args[0].name === targetVariable) {
                        switch (funcCallExpr.name) {
                            case 'sin': // FIX: Corrected argument order for 'op' helper
                                return op(num(-1), 'multiply', func('cos', [variable(targetVariable)]));
                            case 'cos': return func('sin', [variable(targetVariable)]);
                            case 'exp': return new expression_1.ExponentialNode(variable(targetVariable));
                            case 'ln': // FIX: Corrected argument order for 'op' helper
                                return op(op(variable(targetVariable), 'multiply', func('ln', [variable(targetVariable)])), 'subtract', variable(targetVariable));
                        }
                    }
                    break;
                case 'unaryOperation':
                    const unOpExpr = expr;
                    if (unOpExpr.operator === 'negate') {
                        const result = getAntiderivative(unOpExpr.operand);
                        if (result !== "UNINTEGRATABLE_EXPRESSION") {
                            return new expression_1.UnaryOperationNode('negate', result);
                        }
                    }
                    break;
                case 'constant':
                    const constExpr = expr;
                    // FIX: Corrected argument order for 'op' helper
                    return op(constExpr, 'multiply', variable(targetVariable));
                case 'exponential':
                    const expExpr = expr;
                    // Handle e^(ax)
                    if (expExpr.exponent.type === 'binaryOperation' &&
                        expExpr.exponent.operator === 'multiply') {
                        const product = expExpr.exponent;
                        let aNode = null;
                        let xNode = null;
                        // Check for a*x or x*a
                        if (product.left.type === 'number' &&
                            product.right.type === 'variable' &&
                            product.right.name === targetVariable) {
                            aNode = product.left;
                            xNode = product.right;
                        }
                        else if (product.right.type === 'number' &&
                            product.left.type === 'variable' &&
                            product.left.name === targetVariable) {
                            aNode = product.right;
                            xNode = product.left;
                        }
                        if (aNode !== null && xNode !== null) {
                            if (aNode.value === 0) {
                                // Integral of e^0 (which is 1) is x
                                return op(num(1), 'multiply', variable(targetVariable));
                            }
                            // Integral of e^(ax) is (1/a)e^(ax)
                            const oneOverA = op(num(1), 'divide', aNode);
                            return op(oneOverA, 'multiply', expExpr);
                        }
                    }
                    // Handle e^x (where a is implicitly 1)
                    if (expExpr.exponent.type === 'variable' && expExpr.exponent.name === targetVariable) {
                        return expExpr;
                    }
                    break;
            }
            return "UNINTEGRATABLE_EXPRESSION";
        };
        const antiderivative = getAntiderivative(expression);
        if (antiderivative === "UNINTEGRATABLE_EXPRESSION") {
            return {
                unintegratable: true,
                integratedExpression: "UNINTEGRATABLE_EXPRESSION",
                constantOfIntegration: null
            };
        }
        else {
            // FIX: Corrected argument order for 'op' helper
            integratedExpr = this.simplify(op(antiderivative, 'add', new expression_1.VariableNode('C')));
            return {
                unintegratable: false,
                integratedExpression: integratedExpr,
                constantOfIntegration: 'C'
            };
        }
    }
    /**
     * Computes the definite integral of a given expression over a specified range.
     * Uses numerical integration (Riemann sum, midpoint rule) if `options.numRectangles` is provided.
     * Otherwise, attempts symbolic integration and evaluates the antiderivative at the bounds.
     * @param expression The root node of the expression AST to integrate.
     * @param targetVariable The name of the variable with respect to which the integration is performed.
     * @param lowerBound The lower limit of integration.
     * @param upperBound The upper limit of integration.
     * @param options Optional. Options for the integration method, suchs as the number of rectangles for numerical integration.
     * @returns The numeric result of the definite integral.
     * @throws {Error} If the expression cannot be integrated or evaluated within the given bounds.
     */
    integrateDefinite(expression, targetVariable, lowerBound, upperBound, options) {
        const numRectangles = options?.numRectangles;
        if (numRectangles && numRectangles > 0) {
            const deltaX = (upperBound - lowerBound) / numRectangles;
            let sum = 0;
            for (let i = 0; i < numRectangles; i++) {
                const x = lowerBound + (i + 0.5) * deltaX;
                const context = { [targetVariable]: x };
                sum += this.evaluate(expression, context);
            }
            return sum * deltaX;
        }
        else {
            // FIX: Add a check for singularity at 0 for 1/x before symbolic integration
            // FIX: Corrected syntax for VariableNode cast
            if (expression.type === 'binaryOperation' && expression.operator === 'divide' &&
                expression.right.type === 'variable' &&
                expression.right.name === targetVariable &&
                lowerBound <= 0 && upperBound >= 0) {
                throw new Error("Division by zero.");
            }
            const indefiniteResult = this.integrateIndefinite(expression, targetVariable);
            if (indefiniteResult.unintegratable) {
                throw new Error("Expression cannot be integrated symbolically. Consider providing `numRectangles` for numerical integration.");
            }
            const antiderivativeWithC = indefiniteResult.integratedExpression;
            const allVariablesInAntiderivative = new Set();
            this._collectVariables(antiderivativeWithC, allVariablesInAntiderivative);
            const baseContext = { 'C': 0 };
            allVariablesInAntiderivative.forEach(varName => {
                if (varName !== targetVariable && varName !== 'C') {
                    baseContext[varName] = 0;
                }
            });
            try {
                const contextUpper = { ...baseContext, [targetVariable]: upperBound };
                const contextLower = { ...baseContext, [targetVariable]: lowerBound };
                const upperVal = this.evaluate(antiderivativeWithC, contextUpper);
                const lowerVal = this.evaluate(antiderivativeWithC, contextLower);
                return upperVal - lowerVal;
            }
            catch (error) {
                if (error.message.includes("Division by zero.") || error.message.includes("Logarithm of non-positive number.")) {
                    throw error;
                }
                throw new Error("Error evaluating antiderivative at integration bounds: " + error.message);
            }
        }
    }
    /**
     * Simplifies a given expression.
     * Implements basic constant folding and identity rules.
     * Applies simplification rules iteratively until a fixed point is reached.
     * @param expression The root node of the expression AST to simplify.
     * @returns A new ExpressionNode representing the simplified form.
     * @throws {Error} If the simplification rules for a specific node type are not implemented or an invalid state is reached.
     */
    simplify(expression) {
        let currentExpression = expression;
        let changed = true;
        while (changed) {
            changed = false;
            let newExpression = this._simplifyPass(currentExpression);
            if (JSON.stringify(newExpression) !== JSON.stringify(currentExpression)) {
                currentExpression = newExpression;
                changed = true;
            }
        }
        return currentExpression;
    }
    _simplifyPass(expression) {
        // Defensive check: Ensure expression is a valid object with a 'type' property set.
        if (!expression || typeof expression !== 'object' || !('type' in expression)) {
            const typeInfo = (expression && typeof expression === 'object') ? `object with keys: ${Object.keys(expression).join(', ')} and type: ${expression.type}` : String(expression);
            throw new Error(`Malformed expression node passed to _simplifyPass: ${typeInfo}. Missing or invalid 'type' property.`);
        }
        switch (expression.type) {
            case 'number':
            case 'variable':
            case 'constant': // Added constant here for simplicity, as they are atomic
                return expression;
            case 'binaryOperation':
                const binOpExpr = expression;
                let simplifiedLeft = this._simplifyPass(binOpExpr.left);
                let simplifiedRight = this._simplifyPass(binOpExpr.right);
                // Constant folding (if both operands are numbers)
                const leftIsNumber = simplifiedLeft.type === 'number';
                const rightIsNumber = simplifiedRight.type === 'number';
                if (leftIsNumber && rightIsNumber) {
                    const leftVal = simplifiedLeft.value;
                    const rightVal = simplifiedRight.value;
                    switch (binOpExpr.operator) {
                        case 'add': return num(leftVal + rightVal);
                        case 'subtract': return num(leftVal - rightVal);
                        case 'multiply': return num(leftVal * rightVal);
                        case 'divide':
                            if (rightVal === 0)
                                return op(simplifiedLeft, 'divide', simplifiedRight); // Keep as is if division by zero
                            return num(leftVal / rightVal);
                        case 'power':
                            if (leftVal === 0 && rightVal === 0)
                                throw new Error('0^0 is undefined.');
                            return num(Math.pow(leftVal, rightVal));
                        default:
                            // Fallback to original if operator not handled by constant folding
                            return op(simplifiedLeft, binOpExpr.operator, simplifiedRight);
                    }
                }
                // --- Complex Sum/Difference Simplification ---
                if (binOpExpr.operator === 'add' || binOpExpr.operator === 'subtract') {
                    const terms = [];
                    let constantSum = 0;
                    let hasC = false; // Flag to track if 'C' was encountered
                    // Helper to collect terms recursively (flattening sums/differences)
                    const collectSignedTerms = (node, currentSign) => {
                        // Recursively simplify the node itself before analyzing its type
                        node = this._simplifyPass(node);
                        if (node.type === 'number') {
                            constantSum += node.value * currentSign;
                        }
                        else if (node.type === 'variable') {
                            if (node.name === 'C') { // Exclude 'C' from terms collection
                                hasC = true;
                            }
                            else {
                                terms.push({ coeff: currentSign, variablePart: node });
                            }
                        }
                        else if (node.type === 'binaryOperation' && node.operator === 'multiply') {
                            const binaryNode = node;
                            if (binaryNode.left.type === 'number' && binaryNode.right.type === 'variable') {
                                if (binaryNode.right.name === 'C') { // Exclude C*C from terms
                                    hasC = true;
                                }
                                else {
                                    terms.push({ coeff: binaryNode.left.value * currentSign, variablePart: binaryNode.right });
                                }
                            }
                            else {
                                terms.push({ coeff: currentSign, variablePart: node });
                            }
                        }
                        else if (node.type === 'unaryOperation' && node.operator === 'negate') {
                            // Handle -expr for sum/difference: recurse with flipped sign
                            collectSignedTerms(node.operand, currentSign * -1);
                        }
                        else if (node.type === 'binaryOperation' && (node.operator === 'add' || node.operator === 'subtract')) {
                            // Flatten nested sums/differences: recurse on children with appropriate signs
                            collectSignedTerms(node.left, currentSign);
                            collectSignedTerms(node.right, currentSign * (node.operator === 'subtract' ? -1 : 1));
                        }
                        else {
                            // For all other complex terms (e.g., x^2, sin(x), ln(x), non-Cx products).
                            // These are treated as unique "variable parts" with a coefficient of 1 (or -1 if negated).
                            terms.push({ coeff: currentSign, variablePart: node });
                        }
                    };
                    collectSignedTerms(simplifiedLeft, 1);
                    collectSignedTerms(simplifiedRight, binOpExpr.operator === 'subtract' ? -1 : 1);
                    // Map to store coefficients for canonical string form of variable parts (e.g., { 'x': 5, 'x^2': -2, 'sin(x)': 1 })
                    const collectedVariableParts = new Map();
                    const canonicalNodeMap = new Map(); // Stores the actual node for canonical string form
                    terms.forEach(term => {
                        if (term.variablePart === null) {
                            // This case is handled by constantSum
                        }
                        else if (term.variablePart.type === 'variable') {
                            const varName = term.variablePart.name;
                            collectedVariableParts.set(varName, (collectedVariableParts.get(varName) || 0) + term.coeff);
                            canonicalNodeMap.set(varName, term.variablePart); // Store original var node
                        }
                        else {
                            // Use JSON.stringify as key for other complex terms
                            const key = JSON.stringify(term.variablePart);
                            collectedVariableParts.set(key, (collectedVariableParts.get(key) || 0) + term.coeff);
                            canonicalNodeMap.set(key, term.variablePart); // Store the original complex node
                        }
                    });
                    // Reconstruct the simplified expression from collected terms
                    let newExpr = null;
                    // Add variable and other terms first
                    const sortedKeys = Array.from(collectedVariableParts.keys()).sort(); // For consistent order
                    sortedKeys.forEach(key => {
                        const coeff = collectedVariableParts.get(key);
                        if (coeff === 0)
                            return;
                        const termNode = canonicalNodeMap.get(key);
                        let termToAdd;
                        if (coeff === 1) {
                            termToAdd = termNode;
                        }
                        else if (coeff === -1) {
                            termToAdd = termNode; // The sign will be handled by the operator
                        }
                        else {
                            termToAdd = op(num(Math.abs(coeff)), 'multiply', termNode); // Always positive coefficient in multiplication
                        }
                        if (newExpr === null) {
                            if (coeff < 0) { // If first term is negative, it's a unary negation
                                newExpr = unaryOp('negate', termToAdd);
                            }
                            else {
                                newExpr = termToAdd;
                            }
                        }
                        else {
                            if (coeff < 0) { // If subsequent term is negative, use add with unary negate
                                newExpr = op(newExpr, 'add', unaryOp('negate', termToAdd));
                            }
                            else { // If subsequent term is positive, use add operator
                                newExpr = op(newExpr, 'add', termToAdd);
                            }
                        }
                    });
                    // Add constant sum
                    if (constantSum !== 0) {
                        if (newExpr === null) {
                            newExpr = num(constantSum);
                        }
                        else {
                            if (constantSum < 0) {
                                newExpr = op(newExpr, 'add', unaryOp('negate', num(Math.abs(constantSum))));
                            }
                            else {
                                newExpr = op(newExpr, 'add', num(constantSum));
                            }
                        }
                    }
                    // Finally, add 'C' if it was present
                    if (hasC) {
                        if (newExpr === null) {
                            newExpr = variable('C');
                        }
                        else {
                            newExpr = op(newExpr, 'add', variable('C')); // C is always positive
                        }
                    }
                    // If all terms cancelled out, return 0
                    return newExpr === null ? num(0) : newExpr;
                }
                // --- Existing Multiplication Simplification ---
                if (binOpExpr.operator === 'multiply') {
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 1)
                        return simplifiedRight;
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 1)
                        return simplifiedLeft;
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 0)
                        return num(0);
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 0)
                        return num(0);
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === -1) {
                        return unaryOp('negate', simplifiedRight);
                    }
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === -1) {
                        return unaryOp('negate', simplifiedLeft);
                    }
                    // Ensure number is on the left for constant/number multiplication
                    if (simplifiedLeft.type === 'constant' && simplifiedRight.type === 'number') {
                        // FIX: Corrected argument order for 'op' helper
                        return op(simplifiedRight, 'multiply', simplifiedLeft);
                    }
                    if (simplifiedLeft.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.name === simplifiedRight.name) {
                        // FIX: Corrected argument order for 'op' helper
                        return op(simplifiedLeft, 'power', num(2));
                    }
                    if (simplifiedLeft.type === 'variable' && simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'power' &&
                        simplifiedRight.left.type === 'variable' && simplifiedRight.right.type === 'number' &&
                        simplifiedLeft.name === simplifiedRight.left.name) {
                        // FIX: Corrected argument order for 'op' helper
                        return op(simplifiedLeft, 'power', num(simplifiedRight.right.value + 1));
                    }
                    if (simplifiedRight.type === 'variable' && simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'power' &&
                        simplifiedLeft.left.type === 'variable' && simplifiedLeft.right.type === 'number' &&
                        simplifiedRight.name === simplifiedLeft.left.name) {
                        // FIX: Corrected argument order for 'op' helper
                        return op(simplifiedLeft.left, 'power', num(simplifiedLeft.right.value + 1));
                    }
                    if (simplifiedLeft.type === 'number' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number' && simplifiedRight.right.type === 'variable') {
                        // FIX: Corrected argument order for 'op' helper
                        return op(num((simplifiedLeft.value) * simplifiedRight.left.value), 'multiply', simplifiedRight.right);
                    }
                    if (simplifiedRight.type === 'number' &&
                        simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'number' && simplifiedLeft.right.type === 'variable') {
                        // FIX: Corrected argument order for 'op' helper
                        return op(num(simplifiedLeft.left.value * simplifiedRight.value), 'multiply', simplifiedLeft.right);
                    }
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'divide' &&
                        simplifiedRight.type === 'number') {
                        // FIX: Corrected argument order for 'op' helper
                        return op(op(simplifiedLeft.left, 'multiply', simplifiedRight), 'divide', simplifiedLeft.right);
                    }
                    if (simplifiedLeft.type === 'number' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'divide') {
                        // FIX: Corrected argument order for 'op' helper
                        return op(op(simplifiedLeft, 'multiply', simplifiedRight.left), 'divide', simplifiedRight.right);
                    }
                }
                // --- Existing Division Simplification ---
                if (binOpExpr.operator === 'divide') {
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 1)
                        return simplifiedLeft;
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 0)
                        return num(0);
                    if (simplifiedLeft.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.name === simplifiedRight.name) {
                        return num(1);
                    }
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.left.name === simplifiedRight.name) {
                        return simplifiedLeft.right;
                    }
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.right.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.right.name === simplifiedRight.name) {
                        return simplifiedLeft.left;
                    }
                    if (simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedLeft.type === 'variable' && simplifiedRight.left.type === 'variable' && simplifiedLeft.name === simplifiedRight.left.name) {
                        // FIX: Corrected argument order for 'op' helper
                        return op(num(1), 'divide', simplifiedRight.right);
                    }
                    // Fix for 1 / (-1 * x) -> -1 / x
                    if (simplifiedLeft.type === 'number' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number') {
                        const numVal = simplifiedLeft.value;
                        const factorVal = simplifiedRight.left.value;
                        const remainingRight = simplifiedRight.right;
                        if (factorVal === 0) {
                            // FIX: Corrected argument order for 'op' helper
                            return op(simplifiedLeft, 'divide', simplifiedRight); // Avoid division by zero in simplification
                        }
                        if (factorVal < 0) {
                            // FIX: Corrected argument order for 'op' helper
                            const tempNegatedNum = this._simplifyPass(unaryOp('negate', num(numVal / Math.abs(factorVal))));
                            return op(tempNegatedNum, 'divide', remainingRight);
                        }
                        else {
                            // FIX: Corrected argument order for 'op' helper
                            return op(num(numVal / factorVal), 'divide', remainingRight);
                        }
                    }
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'number' && simplifiedRight.type === 'number' && simplifiedLeft.left.value === simplifiedRight.value) {
                        return simplifiedLeft.right;
                    }
                    if (simplifiedLeft.type === 'number' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number') {
                        // FIX: Corrected argument order for 'op' helper
                        return op(num((simplifiedLeft.value) / simplifiedRight.left.value), 'divide', simplifiedRight.right);
                    }
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' && simplifiedLeft.left.type === 'number' && simplifiedLeft.right.type === 'variable' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' && simplifiedRight.left.type === 'number' && simplifiedRight.right.type === 'variable' &&
                        simplifiedLeft.right.name === simplifiedRight.right.name) {
                        return num(simplifiedLeft.left.value / simplifiedRight.left.value);
                    }
                    if (simplifiedRight.type === 'unaryOperation' && simplifiedRight.operator === 'negate') {
                        // FIX: Corrected argument order for 'op' helper
                        return op(unaryOp('negate', simplifiedLeft), 'divide', simplifiedRight.operand);
                    }
                    if (simplifiedRight.type === 'number' && simplifiedRight.value < 0) {
                        // FIX: Corrected argument order for 'op' helper
                        return op(unaryOp('negate', simplifiedLeft), 'divide', num(Math.abs(simplifiedRight.value)));
                    }
                    if (simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'divide') {
                        const B = simplifiedRight.left;
                        const C = simplifiedRight.right;
                        // FIX: Corrected argument order for 'op' helper
                        return op(op(simplifiedLeft, 'multiply', C), 'divide', B);
                    }
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'number' && simplifiedRight.type === 'number' &&
                        simplifiedLeft.right.type !== 'number') {
                        // FIX: Corrected argument order for 'op' helper
                        return op(num(simplifiedLeft.left.value / simplifiedRight.value), 'multiply', simplifiedLeft.right);
                    }
                }
                // --- Existing Power Simplification ---
                if (binOpExpr.operator === 'power') {
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === -1) {
                        // FIX: Corrected argument order for 'op' helper
                        return op(num(1), 'divide', simplifiedLeft);
                    }
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 0)
                        return num(1);
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 1)
                        return simplifiedLeft;
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 0) {
                        if (simplifiedRight.type === 'number' && simplifiedRight.value < 0)
                            return op(simplifiedLeft, 'power', simplifiedRight);
                        return num(0);
                    }
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 1)
                        return num(1);
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'power' &&
                        simplifiedLeft.right.type === 'number' && simplifiedRight.type === 'number') {
                        // FIX: Corrected argument order for 'op' helper
                        return op(simplifiedLeft.left, 'power', num(simplifiedLeft.right.value * simplifiedRight.value));
                    }
                }
                // If no simplification rule applied, return the expression with simplified children
                if (simplifiedLeft !== binOpExpr.left || simplifiedRight !== binOpExpr.right) {
                    // FIX: Corrected argument order for 'op' helper
                    return op(simplifiedLeft, binOpExpr.operator, simplifiedRight);
                }
                return expression;
            case 'functionCall':
                const funcCallExpr = expression;
                const simplifiedArgs = funcCallExpr.args.map(arg => this._simplifyPass(arg));
                const argsChanged = funcCallExpr.args.some((arg, i) => arg !== simplifiedArgs[i]);
                let currentFuncCall = (argsChanged) ? func(funcCallExpr.name, simplifiedArgs) : funcCallExpr;
                if (currentFuncCall.type === 'functionCall' && currentFuncCall.name === 'ln' && currentFuncCall.args.length === 1 && currentFuncCall.args[0].type === 'constant' && currentFuncCall.args[0].name === 'e') {
                    return num(1);
                }
                if (currentFuncCall.type === 'functionCall' && currentFuncCall.name === 'exp' && currentFuncCall.args.length === 1 && currentFuncCall.args[0].type === 'functionCall' && currentFuncCall.args[0].name === 'ln' && currentFuncCall.args[0].args.length === 1) {
                    return currentFuncCall.args[0].args[0];
                }
                if (currentFuncCall.type === 'functionCall' && currentFuncCall.args.length === 1 && currentFuncCall.args[0].type === 'number') {
                    const argVal = currentFuncCall.args[0].value;
                    switch (currentFuncCall.name) {
                        case 'sin': return num(Math.sin(argVal));
                        case 'cos': return num(Math.cos(argVal));
                        case 'tan': return num(Math.tan(argVal));
                        case 'ln':
                            if (argVal === 1)
                                return num(0);
                            if (Math.abs(argVal - Math.E) < 1e-9)
                                return num(1); // Handle ln(e)
                            if (argVal <= 0)
                                return currentFuncCall; // Keep as is if invalid domain
                            return currentFuncCall; // Keep symbolic for other numbers like ln(2)
                        case 'exp':
                            if (argVal === 0)
                                return num(1);
                            return num(Math.exp(argVal));
                        case 'sqrt':
                            if (argVal === 0)
                                return num(0);
                            if (argVal > 0)
                                return num(Math.sqrt(argVal));
                            if (argVal < 0)
                                return currentFuncCall;
                            break;
                        case 'abs': return num(Math.abs(argVal));
                        default:
                            return currentFuncCall;
                    }
                }
                return currentFuncCall;
            case 'unaryOperation':
                const unOpExpr = expression;
                const simplifiedOperand = this._simplifyPass(unOpExpr.operand); // Corrected: Simplify operand directly
                // Apply simplification rules based on the simplified operand
                if (unOpExpr.operator === 'negate') {
                    if (simplifiedOperand.type === 'number') {
                        return num(-simplifiedOperand.value);
                    }
                    // Handle -(-x) -> x
                    if (simplifiedOperand.type === 'unaryOperation' && simplifiedOperand.operator === 'negate') {
                        return simplifiedOperand.operand;
                    }
                }
                // If no specific simplification rule applied, and the operand itself changed during its own simplification,
                // return a new node with the simplified operand. Otherwise, return the original expression.
                if (simplifiedOperand !== unOpExpr.operand) {
                    return new expression_1.UnaryOperationNode(unOpExpr.operator, simplifiedOperand);
                }
                return expression;
            case 'exponential':
                const expExpr = expression;
                const simplifiedExponent = this._simplifyPass(expExpr.exponent);
                if (simplifiedExponent.type === 'number' && simplifiedExponent.value === 0) {
                    return num(1);
                }
                if (simplifiedExponent !== expExpr.exponent) {
                    return new expression_1.ExponentialNode(simplifiedExponent);
                }
                return expression;
            default:
                throw new Error("Unknown expression node type for simplification: " + expression.type);
        }
    }
}
exports.ExpressionUtils = ExpressionUtils;
