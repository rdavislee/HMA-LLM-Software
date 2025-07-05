import { AstNode, NodeType, NumberNode, VariableNode, BinaryOpNode, UnaryOpNode, CallNode, ConstantNode } from '../types/ast.js';

function isNumberNode(node: AstNode): node is NumberNode {
    return node.type === NodeType.Number;
}

function isVariableNode(node: AstNode): node is VariableNode {
    return node.type === NodeType.Variable;
}

function isConstantNode(node: AstNode): node is ConstantNode {
    return node.type === NodeType.Constant;
}

function isUnaryOpNode(node: AstNode): node is UnaryOpNode {
    return node.type === NodeType.UnaryOperation;
}

function isBinaryOpNode(node: AstNode): node is BinaryOpNode {
    return node.type === NodeType.BinaryOperation;
}

function isCallNode(node: AstNode): node is CallNode {
    return node.type === NodeType.FunctionCall;
}

/**
 * Simplifies a given Abstract Syntax Tree (AST) node by applying algebraic and trigonometric rules.
 * This function performs various simplifications such as constant folding, combining like terms,
 * applying identity rules, and simplifying trigonometric expressions.
 *
 * @precondition The input `node` must be a valid AstNode representing a mathematical expression.
 * @postcondition The returned AstNode will be a simplified version of the input expression.
 *                The simplification is not guaranteed to be maximal, but common rules will be applied.
 * @throws {Error} If the input node is invalid or an unexpected AST structure is encountered during simplification.
 * @param node The root node of the AST to be simplified.
 * @returns A new AstNode representing the simplified expression.
 */
export function simplify(node: AstNode): AstNode {
    let simplifiedNode: AstNode = node; // Start with the original node

    // Recursively simplify children first
    switch (node.type) {
        case NodeType.Number:
        case NodeType.Variable:
        case NodeType.Constant:
            return node;

        case NodeType.UnaryOperation:
            if (!isUnaryOpNode(node)) throw new Error("Expected UnaryOpNode");
            const unaryNode = node;
            const simplifiedOperand = simplify(unaryNode.operand);

            let currentUnaryNode: UnaryOpNode = { ...unaryNode, operand: simplifiedOperand };

            if (currentUnaryNode.operator === '-') {
                if (isUnaryOpNode(currentUnaryNode.operand) && currentUnaryNode.operand.operator === '-') {
                    return simplify(currentUnaryNode.operand.operand);
                }
                if (isNumberNode(currentUnaryNode.operand)) {
                    return { type: NodeType.Number, value: -currentUnaryNode.operand.value } as NumberNode;
                }
            }
            simplifiedNode = currentUnaryNode;
            break;

        case NodeType.BinaryOperation:
            if (!isBinaryOpNode(node)) throw new Error("Expected BinaryOpNode");
            const binaryNode = node;
            const simplifiedLeft = simplify(binaryNode.left);
            const simplifiedRight = simplify(binaryNode.right);

            let currentBinaryNode: BinaryOpNode = { ...binaryNode, left: simplifiedLeft, right: simplifiedRight };

            if (isNumberNode(currentBinaryNode.left) && isNumberNode(currentBinaryNode.right)) {
                const leftVal = currentBinaryNode.left.value;
                const rightVal = currentBinaryNode.right.value;
                switch (currentBinaryNode.operator) {
                    case '+': return { type: NodeType.Number, value: leftVal + rightVal } as NumberNode;
                    case '-': return { type: NodeType.Number, value: leftVal - rightVal } as NumberNode;
                    case '*': return { type: NodeType.Number, value: leftVal * rightVal } as NumberNode;
                    case '/':
                        if (rightVal === 0) {
                            return currentBinaryNode;
                        }
                        return { type: NodeType.Number, value: leftVal / rightVal } as NumberNode;
                    case '^': return { type: NodeType.Number, value: Math.pow(leftVal, rightVal) } as NumberNode;
                }
            }

            const left = currentBinaryNode.left;
            const right = currentBinaryNode.right;

            if (currentBinaryNode.operator === '+') {
                if (isNumberNode(left) && left.value === 0) return right;
                if (isNumberNode(right) && right.value === 0) return left;
            }

            if (currentBinaryNode.operator === '-' && isNumberNode(right) && right.value === 0) {
                return left;
            }

            if (currentBinaryNode.operator === '*') {
                if ((isNumberNode(left) && left.value === 0) || (isNumberNode(right) && right.value === 0)) {
                    return { type: NodeType.Number, value: 0 } as NumberNode;
                }
            }

            if (currentBinaryNode.operator === '*') {
                if (isNumberNode(left) && left.value === 1) return right;
                if (isNumberNode(right) && right.value === 1) return left;
            }

            if (currentBinaryNode.operator === '/' && isNumberNode(right) && right.value === 1) {
                return left;
            }

            if (currentBinaryNode.operator === '/' && isNumberNode(left) && left.value === 0) {
                if (!isNumberNode(right) || right.value !== 0) {
                     return { type: NodeType.Number, value: 0 } as NumberNode;
                }
            }

            if (currentBinaryNode.operator === '^' && isNumberNode(right) && right.value === 1) {
                return left;
            }

            if (currentBinaryNode.operator === '^' && isNumberNode(left) && left.value === 1) {
                return { type: NodeType.Number, value: 1 } as NumberNode;
            }

            if (currentBinaryNode.operator === '^' && isNumberNode(right) && right.value === 0) {
                if (isNumberNode(left) && left.value === 0) {
                    return currentBinaryNode;
                }
                return { type: NodeType.Number, value: 1 } as NumberNode;
            }

            if (currentBinaryNode.operator === '/' && nodesAreEqual(left, right)) {
                if (isNumberNode(left) && left.value === 0) {
                    return currentBinaryNode;
                }
                return { type: NodeType.Number, value: 1 } as NumberNode;
            }

            if (currentBinaryNode.operator === '+') {
                const leftCoeffTerm = getCoefficientAndTerm(left);
                const rightCoeffTerm = getCoefficientAndTerm(right);

                if (leftCoeffTerm && rightCoeffTerm && nodesAreEqual(leftCoeffTerm.term, rightCoeffTerm.term)) {
                    const newCoeff = leftCoeffTerm.coefficient + rightCoeffTerm.coefficient;
                    if (newCoeff === 0) return { type: NodeType.Number, value: 0 } as NumberNode;
                    if (newCoeff === 1) return leftCoeffTerm.term;
                    return { type: NodeType.BinaryOperation, operator: '*', left: { type: NodeType.Number, value: newCoeff } as NumberNode, right: leftCoeffTerm.term } as BinaryOpNode;
                }
            }

            if (currentBinaryNode.operator === '-') {
                const leftCoeffTerm = getCoefficientAndTerm(left);
                const rightCoeffTerm = getCoefficientAndTerm(right);

                if (leftCoeffTerm && rightCoeffTerm && nodesAreEqual(leftCoeffTerm.term, rightCoeffTerm.term)) {
                    const newCoeff = leftCoeffTerm.coefficient - rightCoeffTerm.coefficient;
                    if (newCoeff === 0) return { type: NodeType.Number, value: 0 } as NumberNode;
                    if (newCoeff === 1) return leftCoeffTerm.term;
                    if (newCoeff === -1) return { type: NodeType.UnaryOperation, operator: '-', operand: leftCoeffTerm.term } as UnaryOpNode;
                    return { type: NodeType.BinaryOperation, operator: '*', left: { type: NodeType.Number, value: newCoeff } as NumberNode, right: leftCoeffTerm.term } as BinaryOpNode;
                }
            }

            if (currentBinaryNode.operator === '*') {
                const baseLeft = getBaseIfPower(left);
                const expLeft = getExponentIfPower(left);
                const baseRight = getBaseIfPower(right);
                const expRight = getExponentIfPower(right);

                if (baseLeft && expLeft && baseRight && expRight &&
                    nodesAreEqual(baseLeft, baseRight) &&
                    isNumberNode(expLeft) && isNumberNode(expRight)) {
                    return {
                        type: NodeType.BinaryOperation,
                        operator: '^',
                        left: baseLeft,
                        right: { type: NodeType.Number, value: expLeft.value + expRight.value } as NumberNode
                    } as BinaryOpNode;
                }
            }

            if (currentBinaryNode.operator === '^' && isBinaryOpNode(simplifiedLeft) && simplifiedLeft.operator === '^' &&
                isNumberNode(simplifiedLeft.right) && isNumberNode(simplifiedRight)) {
                return {
                    type: NodeType.BinaryOperation,
                    operator: '^',
                    left: simplifiedLeft.left,
                    right: { type: NodeType.Number, value: simplifiedLeft.right.value * simplifiedRight.value } as NumberNode
                } as BinaryOpNode;
            }

            if (currentBinaryNode.operator === '/') {
                const baseLeft = getBaseIfPower(left);
                const expLeft = getExponentIfPower(left);
                const baseRight = getBaseIfPower(right);
                const expRight = getExponentIfPower(right);

                if (baseLeft && expLeft && baseRight && expRight &&
                    nodesAreEqual(baseLeft, baseRight) &&
                    isNumberNode(expLeft) && isNumberNode(expRight)) {
                    return {
                        type: NodeType.BinaryOperation,
                        operator: '^',
                        left: baseLeft,
                        right: { type: NodeType.Number, value: expLeft.value - expRight.value } as NumberNode
                    } as BinaryOpNode;
                }
            }

            if (currentBinaryNode.operator === '+') {
                const isSquaredTrig = (node: AstNode, funcName: string): AstNode | null => {
                    if (isBinaryOpNode(node) && node.operator === '^' &&
                        isNumberNode(node.right) && node.right.value === 2 &&
                        isCallNode(node.left) && node.left.functionName === funcName &&
                        node.left.arguments.length === 1) {
                        return node.left.arguments[0];
                    }
                    return null;
                };

                const leftArgSin = isSquaredTrig(left, 'sin');
                const rightArgCos = isSquaredTrig(right, 'cos');

                if (leftArgSin && rightArgCos && nodesAreEqual(leftArgSin, rightArgCos)) {
                    return { type: NodeType.Number, value: 1 } as NumberNode;
                }

                const leftArgCos = isSquaredTrig(left, 'cos');
                const rightArgSin = isSquaredTrig(right, 'sin');

                if (leftArgCos && rightArgSin && nodesAreEqual(leftArgCos, rightArgSin)) {
                    return { type: NodeType.Number, value: 1 } as NumberNode;
                }
            }
            simplifiedNode = currentBinaryNode;
            break;

        case NodeType.FunctionCall:
            if (!isCallNode(node)) throw new Error("Expected CallNode");
            const callNode = node;
            const simplifiedArgs = callNode.arguments.map(simplify);
            let currentCallNode: CallNode = { ...callNode, arguments: simplifiedArgs };
            simplifiedNode = currentCallNode;
            break;

        default:
            throw new Error(`Unknown AST node type: ${(node as any).type}`);
    }

    // If the node was simplified, recursively simplify the new node again.
    // This is important for nested simplifications (e.g., (2+3)+x -> 5+x).
    if (!nodesAreEqual(node, simplifiedNode)) {
        return simplify(simplifiedNode);
    }

    return simplifiedNode;
}

// Helper to check if two nodes are structurally equal for comparison purposes
function nodesAreEqual(node1: AstNode, node2: AstNode): boolean {
    if (node1.type !== node2.type) return false;

    switch (node1.type) {
        case NodeType.Number:
            return (node1 as NumberNode).value === (node2 as NumberNode).value;
        case NodeType.Variable:
            return (node1 as VariableNode).name === (node2 as VariableNode).name;
        case NodeType.Constant:
            return (node1 as ConstantNode).name === (node2 as ConstantNode).name;
        case NodeType.UnaryOperation:
            return (node1 as UnaryOpNode).operator === (node2 as UnaryOpNode).operator &&
                   nodesAreEqual((node1 as UnaryOpNode).operand, (node2 as UnaryOpNode).operand);
        case NodeType.BinaryOperation:
            // For commutative operations (+, *), order doesn't matter for equality in some contexts,
            // but for deep.equal, it does. For simplification, we want to match exact structure.
            return (node1 as BinaryOpNode).operator === (node2 as BinaryOpNode).operator &&
                   nodesAreEqual((node1 as BinaryOpNode).left, (node2 as BinaryOpNode).left) &&
                   nodesAreEqual((node1 as BinaryOpNode).right, (node2 as BinaryOpNode).right);
        case NodeType.FunctionCall:
            const call1 = node1 as CallNode;
            const call2 = node2 as CallNode;
            if (call1.functionName !== call2.functionName || call1.arguments.length !== call2.arguments.length) return false;
            for (let i = 0; i < call1.arguments.length; i++) {
                if (!nodesAreEqual(call1.arguments[i], call2.arguments[i])) return false;
            }
            return true;
        default:
            return false;
    }
}

// Helper function to extract coefficient and term for like term combination
// Returns { coefficient: number; term: AstNode } or null if not a simple term
// Handles 'x' as 1*x and '2*x' as 2*x
function getCoefficientAndTerm(node: AstNode): { coefficient: number; term: AstNode } | null {
    if (isVariableNode(node)) {
        return { coefficient: 1, term: node };
    }
    if (isBinaryOpNode(node) && node.operator === '*') {
        const left = node.left;
        const right = node.right;

        // Try to find a coefficient on either side
        if (isNumberNode(left)) {
            const termResult = getCoefficientAndTerm(right);
            if (termResult) {
                return { coefficient: left.value * termResult.coefficient, term: termResult.term };
            }
        }
        if (isNumberNode(right)) {
            const termResult = getCoefficientAndTerm(left);
            if (termResult) {
                return { coefficient: right.value * termResult.coefficient, term: termResult.term };
            }
        }
    }
    // If it's a unary negation of a term, e.g., -x or -(2*x)
    if (isUnaryOpNode(node) && node.operator === '-') {
        const termResult = getCoefficientAndTerm(node.operand);
        if (termResult) {
            return { coefficient: -termResult.coefficient, term: termResult.term };
        }
    }
    return null;
}

// Helper to get the base of a power expression (e.g., in x^a, returns x)
function getBaseIfPower(node: AstNode): AstNode | null {
    if (isBinaryOpNode(node) && node.operator === '^') {
        return node.left;
    }
    // If it's not a power, but a variable, treat it as x^1
    if (isVariableNode(node)) {
        return node;
    }
    return null;
}

// Helper to get the exponent of a power expression (e.g., in x^a, returns a)
function getExponentIfPower(node: AstNode): AstNode | null {
    if (isBinaryOpNode(node) && node.operator === '^') {
        return node.right;
    }
    // If it's not a power, but a variable, treat it as x^1
    if (isVariableNode(node)) {
        return { type: NodeType.Number, value: 1 } as NumberNode;
    }
    return null;
}
