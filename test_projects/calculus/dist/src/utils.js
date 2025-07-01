"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExpressionUtils = void 0;
const expression_1 = require("./expression");
// Helper functions to create nodes using the Expression class
const num = (value) => new expression_1.NumberNode(value);
const variable = (name) => new expression_1.VariableNode(name);
const op = (operator, left, right) => new expression_1.BinaryOperationNode(operator, left, right);
const func = (name, args) => new expression_1.FunctionCallNode(name, args);
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
                if (!(varExpr.name in context)) {
                    throw new Error(`Variable '${varExpr.name}' not found in evaluation context.`);
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
                        throw new Error(`Unsupported operator: ${binOpExpr.operator}`);
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
                        throw new Error(`Unsupported function: ${funcCallExpr.name}`);
                }
            case 'unaryOperation': // NEW
                const unOpExpr = expression;
                const operandVal = this.evaluate(unOpExpr.operand, context);
                switch (unOpExpr.operator) {
                    case 'negate': return -operandVal;
                    default: throw new Error(`Unsupported unary operator: ${unOpExpr.operator}`);
                }
            case 'constant': // NEW
                const constExpr = expression;
                switch (constExpr.name) {
                    case 'e': return Math.E;
                    case 'pi': return Math.PI;
                    default: throw new Error(`Unsupported constant: ${constExpr.name}`);
                }
            case 'exponential': // NEW
                const expExpr = expression;
                const exponentVal = this.evaluate(expExpr.exponent, context);
                return Math.exp(exponentVal);
            default:
                throw new Error(`Unknown expression node type: ${expression.type}`);
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
                result = num(0); // d(c)/dx = 0
                break;
            case 'variable':
                const varExpr = expression;
                result = varExpr.name === targetVariable ? num(1) : num(0); // d(x)/dx = 1, d(y)/dx = 0
                break;
            case 'binaryOperation':
                const binOpExpr = expression;
                const u = binOpExpr.left;
                const v = binOpExpr.right;
                const du = this.differentiate(u, targetVariable);
                const dv = this.differentiate(v, targetVariable);
                switch (binOpExpr.operator) {
                    case 'add': // d(u+v)/dx = du/dx + dv/dx
                    case 'subtract': // d(u-v)/dx = du/dx - dv/dx
                        result = op(binOpExpr.operator, du, dv);
                        break;
                    case 'multiply': // d(uv)/dx = u'v + uv'
                        result = op('add', op('multiply', du, v), op('multiply', u, dv));
                        break;
                    case 'divide': // d(u/v)/dx = (u'v - uv')/v^2
                        result = op('divide', op('subtract', op('multiply', du, v), op('multiply', u, dv)), op('power', v, num(2)));
                        break;
                    case 'power': // d(u^n)/dx = n*u^(n-1)*u' (if v is a number)
                        if (v.type === 'number') {
                            const n = v.value;
                            // Handle d(c^n)/dx = 0 if u is a constant
                            if (u.type === 'number') {
                                result = num(0);
                                break;
                            }
                            result = op('multiply', num(n), op('multiply', op('power', u, num(n - 1)), du));
                            break;
                        }
                        else if (u.type === 'number') { // d(c^v)/dx = c^v * ln(c) * v'
                            const c = u.value;
                            if (c === 0) {
                                result = num(0); // 0^v is 0, derivative is 0
                                break;
                            }
                            if (c === 1) {
                                result = num(0); // 1^v is 1, derivative is 0
                                break;
                            }
                            result = op('multiply', op('power', u, v), op('multiply', num(Math.log(c)), dv));
                            break;
                        }
                        else {
                            // d(u^v)/dx = u^v * (v*u'/u + v'*ln(u))
                            // This is complex and might lead to non-simplified expressions.
                            // For now, throw error for u^v where both are non-constants/non-simple variables.
                            throw new Error(`Differentiation of u^v where both u and v are non-constant expressions is not supported yet.`);
                        }
                    default:
                        throw new Error(`Unsupported operator for differentiation: ${binOpExpr.operator}`);
                }
                break;
            case 'functionCall':
                const funcCallExpr = expression;
                if (funcCallExpr.args.length !== 1) {
                    throw new Error(`Differentiation of multi-argument functions like ${funcCallExpr.name} is not supported yet.`);
                }
                const arg = funcCallExpr.args[0];
                const darg = this.differentiate(arg, targetVariable);
                switch (funcCallExpr.name) {
                    case 'sin':
                        result = op('multiply', func('cos', [arg]), darg);
                        break;
                    case 'cos':
                        result = op('multiply', num(-1), op('multiply', func('sin', [arg]), darg));
                        break;
                    case 'tan': // d(tan(u))/dx = sec^2(u) * u' = (1/cos^2(u)) * u'
                        result = op('multiply', op('divide', num(1), op('power', func('cos', [arg]), num(2))), darg);
                        break;
                    case 'ln': // d(ln(u))/dx = u'/u
                        result = op('multiply', op('divide', num(1), arg), darg);
                        break;
                    case 'exp':
                        result = op('multiply', new expression_1.ExponentialNode(arg), darg);
                        break; // Changed func('exp', [arg]) to new ExponentialNode(arg)
                    case 'sqrt': // d(sqrt(u))/dx = u' / (2*sqrt(u))
                        result = op('multiply', op('divide', num(1), op('multiply', num(2), func('sqrt', [arg]))), darg);
                        break;
                    case 'abs':
                        // d(|u|)/dx = u/|u| * u' (for u != 0) - this is tricky for symbolic differentiation.
                        throw new Error(`Differentiation of absolute value function is not supported symbolically.`);
                    case 'log':
                    case 'arcsin':
                    case 'arccos':
                    case 'arctan':
                        throw new Error(`Differentiation of function ${funcCallExpr.name} is not supported yet.`);
                    default:
                        throw new Error(`Unsupported function for differentiation: ${funcCallExpr.name}`);
                }
                break;
            case 'unaryOperation': // NEW
                const unOpExpr = expression;
                const dOperand = this.differentiate(unOpExpr.operand, targetVariable);
                result = new expression_1.UnaryOperationNode(unOpExpr.operator, dOperand); // d(-u)/dx = -du/dx
                break;
            case 'constant': // NEW
                result = num(0); // d(constant)/dx = 0
                break;
            case 'exponential': // NEW
                const expExpr = expression;
                // d(e^u)/dx = e^u * du/dx
                const dExponent = this.differentiate(expExpr.exponent, targetVariable);
                result = op('multiply', new expression_1.ExponentialNode(expExpr.exponent), dExponent);
                break;
            default:
                throw new Error(`Unknown expression node type for differentiation: ${expression.type}`);
        }
        return this.simplify(result); // Apply simplification before returning
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
        // Implement basic symbolic integration rules
        // For now, only handle simple cases.
        // If it cannot integrate, return unintegratable: true
        let integratedExpr = "UNINTEGRATABLE_EXPRESSION";
        let unintegratable = true;
        let constantOfIntegration = null;
        switch (expression.type) {
            case 'number':
                const numExpr = expression;
                // ∫c dx = cx + C
                integratedExpr = op('add', op('multiply', numExpr, variable(targetVariable)), new expression_1.VariableNode('C'));
                unintegratable = false;
                constantOfIntegration = 'C';
                break;
            case 'variable':
                const varExpr = expression;
                if (varExpr.name === targetVariable) {
                    // ∫x dx = x^2 / 2 + C (Power Rule for n=1)
                    integratedExpr = op('add', op('divide', op('power', variable(targetVariable), num(2)), num(2)), new expression_1.VariableNode('C'));
                    unintegratable = false;
                    constantOfIntegration = 'C';
                }
                else {
                    // ∫y dx = yx + C (if y is treated as a constant wrt x)
                    integratedExpr = op('add', op('multiply', varExpr, variable(targetVariable)), new expression_1.VariableNode('C'));
                    unintegratable = false;
                    constantOfIntegration = 'C';
                }
                break;
            case 'binaryOperation':
                const binOpExpr = expression;
                if (binOpExpr.operator === 'add' || binOpExpr.operator === 'subtract') {
                    const leftResult = this.integrateIndefinite(binOpExpr.left, targetVariable);
                    const rightResult = this.integrateIndefinite(binOpExpr.right, targetVariable);
                    if (!leftResult.unintegratable && !rightResult.unintegratable) {
                        integratedExpr = op('add', op(binOpExpr.operator, leftResult.integratedExpression, rightResult.integratedExpression), new expression_1.VariableNode('C'));
                        unintegratable = false;
                        constantOfIntegration = 'C';
                    }
                }
                else if (binOpExpr.operator === 'power' && binOpExpr.left.type === 'variable' && binOpExpr.left.name === targetVariable && binOpExpr.right.type === 'number') {
                    // Power Rule: ∫x^n dx = x^(n+1)/(n+1) (for n != -1)
                    const n = binOpExpr.right.value;
                    if (n === -1) { // ∫1/x dx = ln(|x|) + C
                        integratedExpr = op('add', func('ln', [func('abs', [variable(targetVariable)])]), new expression_1.VariableNode('C'));
                        unintegratable = false;
                        constantOfIntegration = 'C';
                    }
                    else {
                        integratedExpr = op('add', op('divide', op('power', variable(targetVariable), num(n + 1)), num(n + 1)), new expression_1.VariableNode('C'));
                        unintegratable = false;
                        constantOfIntegration = 'C';
                    }
                }
                else if (binOpExpr.operator === 'power' && binOpExpr.right.type === 'variable' && binOpExpr.right.name === targetVariable && binOpExpr.left.type === 'number') {
                    // ∫a^x dx = a^x / ln(a) + C
                    const a = binOpExpr.left.value;
                    if (a <= 0) { // log(a) undefined or complex for a<=0
                        integratedExpr = "UNINTEGRATABLE_EXPRESSION";
                        unintegratable = true;
                        constantOfIntegration = null;
                    }
                    else if (a === 1) { // ∫1^x dx = ∫1 dx = x + C
                        integratedExpr = op('add', variable(targetVariable), new expression_1.VariableNode('C'));
                        unintegratable = false;
                        constantOfIntegration = 'C';
                    }
                    else {
                        integratedExpr = op('add', op('divide', expression, func('ln', [num(a)])), new expression_1.VariableNode('C'));
                        unintegratable = false;
                        constantOfIntegration = 'C';
                    }
                }
                break;
            case 'functionCall':
                const funcCallExpr = expression;
                if (funcCallExpr.args.length === 1 && funcCallExpr.args[0].type === 'variable' && funcCallExpr.args[0].name === targetVariable) {
                    switch (funcCallExpr.name) {
                        case 'sin':
                            integratedExpr = op('add', op('multiply', num(-1), func('cos', [variable(targetVariable)])), new expression_1.VariableNode('C'));
                            unintegratable = false;
                            constantOfIntegration = 'C';
                            break;
                        case 'cos':
                            integratedExpr = op('add', func('sin', [variable(targetVariable)]), new expression_1.VariableNode('C'));
                            unintegratable = false;
                            constantOfIntegration = 'C';
                            break;
                        case 'exp':
                            integratedExpr = op('add', new expression_1.ExponentialNode(variable(targetVariable)), new expression_1.VariableNode('C'));
                            unintegratable = false;
                            constantOfIntegration = 'C';
                            break;
                        case 'ln': // ∫ln(x)dx = xln(x) - x + C
                            integratedExpr = op('add', op('subtract', op('multiply', variable(targetVariable), func('ln', [variable(targetVariable)])), variable(targetVariable)), new expression_1.VariableNode('C'));
                            unintegratable = false;
                            constantOfIntegration = 'C';
                            break;
                    }
                }
                break;
            case 'unaryOperation': // NEW
                const unOpExpr = expression;
                if (unOpExpr.operator === 'negate') {
                    const result = this.integrateIndefinite(unOpExpr.operand, targetVariable);
                    if (!result.unintegratable) {
                        integratedExpr = op('add', new expression_1.UnaryOperationNode('negate', result.integratedExpression), new expression_1.VariableNode('C'));
                        unintegratable = false;
                        constantOfIntegration = 'C';
                    }
                }
                break;
            case 'constant': // NEW
                const constExpr = expression;
                // ∫c dx = cx + C
                integratedExpr = op('add', op('multiply', constExpr, variable(targetVariable)), new expression_1.VariableNode('C'));
                unintegratable = false;
                constantOfIntegration = 'C';
                break;
            case 'exponential': // NEW
                const expExpr = expression;
                // ∫e^u du where u = x (i.e., ∫e^x dx) = e^x + C
                if (expExpr.exponent.type === 'variable' && expExpr.exponent.name === targetVariable) {
                    integratedExpr = op('add', expExpr, new expression_1.VariableNode('C'));
                    unintegratable = false;
                    constantOfIntegration = 'C';
                }
                break;
            default:
                break;
        }
        return {
            unintegratable: unintegratable,
            integratedExpression: integratedExpr,
            constantOfIntegration: constantOfIntegration
        };
    }
    /**
     * Computes the definite integral of a given expression over a specified range.
     * Uses numerical integration (Riemann sum, midpoint rule) if `options.numRectangles` is provided.
     * Otherwise, attempts symbolic integration and evaluates the antiderivative at the bounds.
     * @param expression The root node of the expression AST to integrate.
     * @param targetVariable The name of the variable with respect to which the integration is performed.
     * @param lowerBound The lower limit of integration.
     * @param upperBound The upper limit of integration.
     * @param options Optional. Options for the integration method, such as the number of rectangles for numerical integration.
     * @returns The numeric result of the definite integral.
     * @throws {Error} If the expression cannot be integrated or evaluated within the given bounds.
     */
    integrateDefinite(expression, targetVariable, lowerBound, upperBound, options) {
        const numRectangles = options?.numRectangles;
        if (numRectangles && numRectangles > 0) {
            // Numerical integration using Riemann sum (midpoint rule for better accuracy)
            const deltaX = (upperBound - lowerBound) / numRectangles;
            let sum = 0;
            for (let i = 0; i < numRectangles; i++) {
                const x = lowerBound + (i + 0.5) * deltaX; // Midpoint
                const context = { [targetVariable]: x };
                sum += this.evaluate(expression, context);
            }
            return sum * deltaX;
        }
        else {
            // Attempt symbolic integration first, then evaluate the antiderivative
            const indefiniteResult = this.integrateIndefinite(expression, targetVariable);
            if (indefiniteResult.unintegratable) {
                // If symbolic fails and no numerical options specified, throw.
                throw new Error("Expression cannot be integrated symbolically. Consider providing `numRectangles` for numerical integration.");
            }
            const antiderivative = indefiniteResult.integratedExpression;
            try {
                // Evaluate F(upperBound) - F(lowerBound). The constant of integration cancels out.
                // So, we need to evaluate the antiderivative without the explicit '+ C' term.
                // A simplified approach: evaluate the antiderivative directly, and the '+C' from indefiniteResult
                // should not affect the definite integral value if it's a simple variable node.
                // However, the current indefiniteResult.integratedExpression *includes* 'C'.
                // The evaluate method handles 'C' as an undefined variable unless explicitly passed in context.
                // For definite integrals, 'C' is assumed to cancel out. We can simply provide an empty context for 'C'.
                // To properly handle this, we need to remove the '+C' node from the antiderivative if it exists.
                // Or, ensure 'C' is treated as 0 in the evaluation context for definite integration.
                // For now, if 'C' is a variable, evaluating it in an empty context will throw. So, let's pass C:0.
                const contextUpper = { [targetVariable]: upperBound, 'C': 0 };
                const contextLower = { [targetVariable]: lowerBound, 'C': 0 };
                const upperVal = this.evaluate(antiderivative, contextUpper);
                const lowerVal = this.evaluate(antiderivative, contextLower);
                return upperVal - lowerVal;
            }
            catch (error) {
                throw new Error(`Error evaluating antiderivative at integration bounds: ${error.message}`);
            }
        }
    }
    /**
     * Simplifies a given expression.
     * Implements basic constant folding and identity rules.
     * @param expression The root node of the expression AST to simplify.
     * @returns A new ExpressionNode representing the simplified form.
     * @throws {Error} If the simplification rules for a specific node type are not implemented or an invalid state is reached.
     */
    simplify(expression) {
        switch (expression.type) {
            case 'number':
            case 'variable':
                return expression;
            case 'binaryOperation':
                const binOpExpr = expression;
                const simplifiedLeft = this.simplify(binOpExpr.left);
                const simplifiedRight = this.simplify(binOpExpr.right);
                // Constant folding
                if (simplifiedLeft.type === 'number' && simplifiedRight.type === 'number') {
                    const leftVal = simplifiedLeft.value;
                    const rightVal = simplifiedRight.value;
                    switch (binOpExpr.operator) {
                        case 'add': return num(leftVal + rightVal);
                        case 'subtract': return num(leftVal - rightVal);
                        case 'multiply': return num(leftVal * rightVal);
                        case 'divide':
                            if (rightVal === 0)
                                throw new Error("Division by zero during simplification.");
                            return num(leftVal / rightVal);
                        case 'power':
                            if (leftVal === 0 && rightVal === 0)
                                throw new Error("0^0 is undefined."); // Added 0^0 check
                            return num(Math.pow(leftVal, rightVal));
                    }
                }
                // Identity rules
                if (binOpExpr.operator === 'add') {
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 0)
                        return simplifiedRight;
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 0)
                        return simplifiedLeft;
                    // Combine like terms: Cx + Dx = (C+D)x
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'number' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number' &&
                        simplifiedLeft.right.type === 'variable' && simplifiedRight.right.type === 'variable' &&
                        simplifiedLeft.right.name === simplifiedRight.right.name) {
                        return op('multiply', num(simplifiedLeft.left.value + simplifiedRight.left.value), variable(simplifiedLeft.right.name));
                    }
                    // Combine like terms: x + x = 2x
                    if (simplifiedLeft.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.name === simplifiedRight.name) {
                        return op('multiply', num(2), variable(simplifiedLeft.name));
                    }
                    // Combine like terms: x + Cx = (1+C)x
                    if (simplifiedLeft.type === 'variable' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number' && simplifiedRight.right.type === 'variable' &&
                        simplifiedLeft.name === simplifiedRight.right.name) {
                        return op('multiply', num(1 + simplifiedRight.left.value), variable(simplifiedLeft.name));
                    }
                    // Combine like terms: Cx + x = (C+1)x
                    if (simplifiedRight.type === 'variable' &&
                        simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'number' && simplifiedLeft.right.type === 'variable' &&
                        simplifiedRight.name === simplifiedLeft.right.name) {
                        return op('multiply', num(simplifiedLeft.left.value + 1), variable(simplifiedRight.name));
                    }
                }
                if (binOpExpr.operator === 'subtract') {
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 0)
                        return simplifiedLeft;
                    // Simplify x - x = 0
                    if (simplifiedLeft.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.name === simplifiedRight.name) {
                        return num(0);
                    }
                    // Simplify Cx - Dx = (C-D)x
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'number' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number' &&
                        simplifiedLeft.right.type === 'variable' && simplifiedRight.right.type === 'variable' &&
                        simplifiedLeft.right.name === simplifiedRight.right.name) {
                        return op('multiply', num(simplifiedLeft.left.value - simplifiedRight.left.value), variable(simplifiedLeft.right.name));
                    }
                    // Simplify x - Cx = (1-C)x
                    if (simplifiedLeft.type === 'variable' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number' && simplifiedRight.right.type === 'variable' &&
                        simplifiedLeft.name === simplifiedRight.right.name) {
                        return op('multiply', num(1 - simplifiedRight.left.value), variable(simplifiedLeft.name));
                    }
                    // Simplify Cx - x = (C-1)x
                    if (simplifiedRight.type === 'variable' &&
                        simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'number' && simplifiedLeft.right.type === 'variable' &&
                        simplifiedRight.name === simplifiedLeft.right.name) {
                        return op('multiply', num(simplifiedLeft.left.value - 1), variable(simplifiedRight.name));
                    }
                    // Simplify 0 - x = -x
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 0) {
                        return new expression_1.UnaryOperationNode('negate', simplifiedRight);
                    }
                }
                if (binOpExpr.operator === 'multiply') {
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 1)
                        return simplifiedRight;
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 1)
                        return simplifiedLeft;
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 0)
                        return num(0);
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 0)
                        return num(0);
                    // Simplify -1 * x to -x
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === -1) {
                        return new expression_1.UnaryOperationNode('negate', simplifiedRight);
                    }
                    // Simplify x * -1 to -x
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === -1) {
                        return new expression_1.UnaryOperationNode('negate', simplifiedLeft);
                    }
                    // Simplify x * x = x^2
                    if (simplifiedLeft.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.name === simplifiedRight.name) {
                        return op('power', simplifiedLeft, num(2));
                    }
                    // Simplify x * x^n = x^(n+1)
                    if (simplifiedLeft.type === 'variable' && simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'power' &&
                        simplifiedRight.left.type === 'variable' && simplifiedRight.right.type === 'number' &&
                        simplifiedLeft.name === simplifiedRight.left.name) {
                        return op('power', simplifiedLeft, num(simplifiedRight.right.value + 1));
                    }
                    // Simplify x^n * x = x^(n+1)
                    if (simplifiedRight.type === 'variable' && simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'power' &&
                        simplifiedLeft.left.type === 'variable' && simplifiedLeft.right.type === 'number' &&
                        simplifiedRight.name === simplifiedLeft.left.name) {
                        return op('power', simplifiedLeft.left, num(simplifiedLeft.right.value + 1));
                    }
                    // Simplify C * (D*x) = (C*D)*x
                    if (simplifiedLeft.type === 'number' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number' && simplifiedRight.right.type === 'variable') {
                        return op('multiply', num((simplifiedLeft.value) * simplifiedRight.left.value), simplifiedRight.right);
                    }
                    // Simplify (C*x) * D = (C*D)*x
                    if (simplifiedRight.type === 'number' &&
                        simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'number' && simplifiedLeft.right.type === 'variable') {
                        return op('multiply', num(simplifiedLeft.left.value * simplifiedRight.value), simplifiedLeft.right);
                    }
                }
                if (binOpExpr.operator === 'divide') {
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 1)
                        return simplifiedLeft;
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 0)
                        return num(0); // 0/x = 0
                    // Simplify x / x = 1
                    if (simplifiedLeft.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.name === simplifiedRight.name) {
                        return num(1);
                    }
                    // Simplify (A*B)/A = B
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.left.name === simplifiedRight.name) {
                        return simplifiedLeft.right;
                    }
                    // Simplify (A*B)/B = A
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.right.type === 'variable' && simplifiedRight.type === 'variable' && simplifiedLeft.right.name === simplifiedRight.name) {
                        return simplifiedLeft.left;
                    }
                    // Simplify A/(A*B) = 1/B
                    if (simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedLeft.type === 'variable' && simplifiedRight.left.type === 'variable' && simplifiedLeft.name === simplifiedRight.left.name) {
                        return op('divide', num(1), simplifiedRight.right);
                    }
                    // Simplify C / (C*X) = 1/X
                    if (simplifiedLeft.type === 'number' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number' && simplifiedLeft.value === simplifiedRight.left.value) {
                        return op('divide', num(1), simplifiedRight.right);
                    }
                    // Simplify (C*X) / C = X
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' &&
                        simplifiedLeft.left.type === 'number' && simplifiedRight.type === 'number' && simplifiedLeft.left.value === simplifiedRight.value) {
                        return simplifiedLeft.right;
                    }
                    // Simplify C / (D*X) = (C/D) / X
                    if (simplifiedLeft.type === 'number' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' &&
                        simplifiedRight.left.type === 'number') {
                        return op('divide', num((simplifiedLeft.value) / simplifiedRight.left.value), simplifiedRight.right);
                    }
                    // Simplify (C*X) / (D*X) = C/D
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'multiply' && simplifiedLeft.left.type === 'number' && simplifiedLeft.right.type === 'variable' &&
                        simplifiedRight.type === 'binaryOperation' && simplifiedRight.operator === 'multiply' && simplifiedRight.left.type === 'number' && simplifiedRight.right.type === 'variable' &&
                        simplifiedLeft.right.name === simplifiedRight.right.name) {
                        return num(simplifiedLeft.left.value / simplifiedRight.left.value);
                    }
                }
                if (binOpExpr.operator === 'power') {
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 0)
                        return num(1); // x^0 = 1
                    if (simplifiedRight.type === 'number' && simplifiedRight.value === 1)
                        return simplifiedLeft; // x^1 = x
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 0) { // 0^x = 0 (for x > 0)
                        if (simplifiedRight.type === 'number' && simplifiedRight.value <= 0)
                            throw new Error("0^0 is undefined or 0^negative is infinity."); // 0^0 handled above
                        return num(0);
                    }
                    if (simplifiedLeft.type === 'number' && simplifiedLeft.value === 1)
                        return num(1); // 1^x = 1
                    // Simplify (x^a)^b to x^(a*b)
                    if (simplifiedLeft.type === 'binaryOperation' && simplifiedLeft.operator === 'power' &&
                        simplifiedLeft.right.type === 'number' && simplifiedRight.type === 'number') {
                        return op('power', simplifiedLeft.left, num(simplifiedLeft.right.value * simplifiedRight.value));
                    }
                }
                // If children were simplified, but parent cannot be, return new node with simplified children
                // This ensures tree traversal and re-creation even if no direct simplification occurs at current node.
                if (simplifiedLeft !== binOpExpr.left || simplifiedRight !== binOpExpr.right) {
                    return op(binOpExpr.operator, simplifiedLeft, simplifiedRight);
                }
                return expression; // No change, return original reference for efficiency
            case 'functionCall':
                const funcCallExpr = expression;
                const simplifiedArgs = funcCallExpr.args.map(arg => this.simplify(arg));
                // Check if any argument was simplified
                const argsChanged = funcCallExpr.args.some((arg, i) => arg !== simplifiedArgs[i]);
                // Basic function simplification (e.g., sin(0) = 0, cos(0) = 1, exp(0) = 1, ln(1) = 0)
                if (simplifiedArgs.length === 1 && simplifiedArgs[0].type === 'number') {
                    const argVal = simplifiedArgs[0].value;
                    switch (funcCallExpr.name) {
                        case 'sin': return num(Math.sin(argVal)); // Evaluate if argument is a number
                        case 'cos': return num(Math.cos(argVal));
                        case 'tan': return num(Math.tan(argVal));
                        case 'ln':
                            if (argVal === 1)
                                return num(0); // ln(1) = 0
                            if (argVal > 0)
                                return num(Math.log(argVal));
                            break; // Cannot simplify ln(0) or ln(negative)
                        case 'exp':
                            if (argVal === 0)
                                return num(1); // exp(0) = 1
                            return num(Math.exp(argVal));
                        case 'sqrt':
                            if (argVal === 0)
                                return num(0); // sqrt(0) = 0
                            if (argVal > 0)
                                return num(Math.sqrt(argVal));
                            break; // Cannot simplify sqrt(negative)
                        case 'abs': return num(Math.abs(argVal));
                    }
                }
                // Simplify ln(e) = 1
                if (funcCallExpr.name === 'ln' && simplifiedArgs.length === 1 && simplifiedArgs[0].type === 'constant' && simplifiedArgs[0].name === 'e') {
                    return num(1);
                }
                // Simplify exp(ln(x)) = x
                if (funcCallExpr.name === 'exp' && simplifiedArgs.length === 1 && simplifiedArgs[0].type === 'functionCall' && simplifiedArgs[0].name === 'ln' && simplifiedArgs[0].args.length === 1) {
                    return simplifiedArgs[0].args[0];
                }
                // If arguments were simplified or no direct simplification at this node, return new node
                if (argsChanged) {
                    return func(funcCallExpr.name, simplifiedArgs);
                }
                return expression; // No change, return original reference
            case 'unaryOperation': // NEW
                const unOpExpr = expression;
                const simplifiedOperand = this.simplify(unOpExpr.operand);
                if (simplifiedOperand.type === 'number') {
                    switch (unOpExpr.operator) {
                        case 'negate': return num(-(simplifiedOperand.value));
                    }
                }
                // Simplify -(-x) = x
                if (unOpExpr.operator === 'negate' && simplifiedOperand.type === 'unaryOperation' && simplifiedOperand.operator === 'negate') {
                    return simplifiedOperand.operand;
                }
                if (simplifiedOperand !== unOpExpr.operand) {
                    return new expression_1.UnaryOperationNode(unOpExpr.operator, simplifiedOperand);
                }
                return expression;
            case 'constant': // NEW
                return expression; // Constants are already simplified
            case 'exponential': // NEW
                const expExpr = expression;
                const simplifiedExponent = this.simplify(expExpr.exponent);
                if (simplifiedExponent.type === 'number' && simplifiedExponent.value === 0) {
                    return num(1); // e^0 = 1
                }
                if (simplifiedExponent !== expExpr.exponent) {
                    return new expression_1.ExponentialNode(simplifiedExponent);
                }
                return expression;
            default:
                throw new Error(`Unknown expression node type for simplification: ${expression.type}`);
        }
    }
}
exports.ExpressionUtils = ExpressionUtils;
