export enum NodeType {
    Number = 'Number',
    Variable = 'Variable',
    Constant = 'Constant',
    BinaryOperation = 'BinaryOperation',
    UnaryOperation = 'UnaryOperation',
    FunctionCall = 'FunctionCall',
}

export interface AstNode {
    type: NodeType;
}

export interface NumberNode extends AstNode {
    type: NodeType.Number;
    value: number;
}

export interface VariableNode extends AstNode {
    type: NodeType.Variable;
    name: string;
}

export interface ConstantNode extends AstNode {
    type: NodeType.Constant;
    name: 'pi' | 'e';
}

export interface BinaryOpNode extends AstNode {
    type: NodeType.BinaryOperation;
    operator: '+' | '-' | '*' | '/' | '^';
    left: AstNode;
    right: AstNode;
}

export interface UnaryOpNode extends AstNode {
    type: NodeType.UnaryOperation;
    operator: '-'; // Currently only negation
    operand: AstNode;
}

export interface CallNode extends AstNode {
    type: NodeType.FunctionCall;
    functionName: string;
    arguments: AstNode[];
}

// Union type for convenience when working with AST nodes
export type ExpressionNode =
    | NumberNode
    | VariableNode
    | ConstantNode
    | BinaryOpNode
    | UnaryOpNode
    | CallNode;
