import { AstNode, NodeType, NumberNode, VariableNode, ConstantNode, BinaryOpNode, UnaryOpNode, CallNode } from '../types/ast.js';

/**
 * Evaluates an Abstract Syntax Tree (AST) node to a numerical value.
 * This function takes an AST node and a map of variable assignments, and computes the numerical result of the expression represented by the AST.
 *
 * @precondition All `VariableNode` instances in the AST must have a corresponding numerical value in the `variables` map.
 * @postcondition Returns a finite numerical value representing the result of the expression.
 * @throws {Error} If:
 *   - A `VariableNode` is encountered that is not defined in the `variables` map.
 *   - An unsupported `NodeType` is encountered.
 *   - A mathematical error occurs during evaluation (e.g., division by zero, invalid function argument).
 * @param node The root `AstNode` of the expression to evaluate.
 * @param variables A `Map` where keys are variable names (strings) and values are their corresponding numerical assignments.
 * @returns The numerical result of the evaluated expression.
 */
export function evaluate(node: AstNode, variables: Map<string, number>): number {
    switch (node.type) {
        case NodeType.Number:
            return (node as NumberNode).value;

        case NodeType.Variable:
            const varNode = node as VariableNode;
            if (!variables.has(varNode.name)) {
                throw new Error(`Variable '${varNode.name}' not defined in the context.`);
            }
            return variables.get(varNode.name)!;

        case NodeType.Constant:
            const constNode = node as ConstantNode;
            if (constNode.name === 'pi') {
                return Math.PI;
            } else if (constNode.name === 'e') {
                return Math.E;
            }
            throw new Error(`Unsupported constant: '${constNode.name}'.`);

        case NodeType.BinaryOperation:
            const binOpNode = node as BinaryOpNode;
            const leftVal = evaluate(binOpNode.left, variables);
            const rightVal = evaluate(binOpNode.right, variables);

            switch (binOpNode.operator) {
                case '+': return leftVal + rightVal;
                case '-': return leftVal - rightVal;
                case '*': return leftVal * rightVal;
                case '/':
                    if (rightVal === 0) {
                        throw new Error('Division by zero.');
                    }
                    return leftVal / rightVal;
                case '^': return Math.pow(leftVal, rightVal);
                default:
                    throw new Error(`Unsupported binary operator: '${binOpNode.operator}'.`);
            }

        case NodeType.UnaryOperation:
            const unOpNode = node as UnaryOpNode;
            const operandVal = evaluate(unOpNode.operand, variables);

            switch (unOpNode.operator) {
                case '-': return -operandVal;
                default:
                    throw new Error(`Unsupported unary operator: '${unOpNode.operator}'.`);
            }

        case NodeType.FunctionCall:
            const callNode = node as CallNode;
            const args = callNode.arguments.map(arg => evaluate(arg, variables));

            switch (callNode.functionName) {
                case 'sin':
                case 'cos':
                case 'tan':
                case 'arcsin':
                case 'arccos':
                case 'arctan':
                case 'abs':
                case 'sqrt':
                    if (args.length !== 1) {
                        throw new Error(`Function '${callNode.functionName}' expects 1 argument(s), but received ${args.length}.`);
                    }
                    break;
                case 'log':
                case 'ln':
                    if (args.length < 1 || args.length > 2) {
                        throw new Error(`Function '${callNode.functionName}' expects 1 or 2 argument(s), but received ${args.length}.`);
                    }
                    break;
                default:
                    throw new Error(`Unsupported function: '${callNode.functionName}'.`);
            }

            switch (callNode.functionName) {
                case 'sin': return Math.sin(args[0]);
                case 'cos': return Math.cos(args[0]);
                case 'tan': return Math.tan(args[0]);
                case 'arcsin': return Math.asin(args[0]);
                case 'arccos': return Math.acos(args[0]);
                case 'arctan': return Math.atan(args[0]);
                case 'ln': return Math.log(args[0]); // Natural logarithm (base e)
                case 'log':
                    if (args.length === 1) {
                        return Math.log10(args[0]); // Base 10 logarithm
                    } else {
                        // log(base, expr)
                        return Math.log(args[1]) / Math.log(args[0]);
                    }
                case 'sqrt':
                    if (args[0] < 0) {
                        throw new Error('Invalid argument for sqrt: must be non-negative.');
                    }
                    return Math.sqrt(args[0]);
                case 'abs': return Math.abs(args[0]);
                default:
                    // This case should ideally not be reached due to the previous switch
                    throw new Error(`Unhandled function case: '${callNode.functionName}'.`);
            }

        default:
            throw new Error(`Unsupported AST node type: ${node.type}`);
    }
}