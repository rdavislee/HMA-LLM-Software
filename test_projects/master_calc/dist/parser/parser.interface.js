"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FunctionName = exports.UnaryOperator = exports.BinaryOperator = exports.ASTNodeKind = void 0;
/**
 * Defines the structure for the Abstract Syntax Tree (AST) nodes
 * used to represent parsed mathematical expressions.
 */
var ASTNodeKind;
(function (ASTNodeKind) {
    ASTNodeKind["NumberLiteral"] = "NumberLiteral";
    ASTNodeKind["Variable"] = "Variable";
    ASTNodeKind["Constant"] = "Constant";
    ASTNodeKind["BinaryExpression"] = "BinaryExpression";
    ASTNodeKind["UnaryExpression"] = "UnaryExpression";
    ASTNodeKind["FunctionCall"] = "FunctionCall";
    ASTNodeKind["Error"] = "Error";
})(ASTNodeKind || (exports.ASTNodeKind = ASTNodeKind = {}));
/**
 * Defines the operators for binary expressions.
 * Follows PEMDAS: Power, Multiply, Divide, Add, Subtract.
 */
var BinaryOperator;
(function (BinaryOperator) {
    BinaryOperator["Add"] = "+";
    BinaryOperator["Subtract"] = "-";
    BinaryOperator["Multiply"] = "*";
    BinaryOperator["Divide"] = "/";
    BinaryOperator["Power"] = "^";
})(BinaryOperator || (exports.BinaryOperator = BinaryOperator = {}));
/**
 * Defines operators for unary expressions.
 * Example: `-x` (negation)
 */
var UnaryOperator;
(function (UnaryOperator) {
    UnaryOperator["Negate"] = "-";
})(UnaryOperator || (exports.UnaryOperator = UnaryOperator = {}));
/**
 * Defines the names of supported mathematical functions.
 */
var FunctionName;
(function (FunctionName) {
    // Logarithms
    FunctionName["LogBase"] = "log_base";
    FunctionName["Ln"] = "ln";
    FunctionName["Log"] = "log";
    // Trigonometry
    FunctionName["Sin"] = "sin";
    FunctionName["Cos"] = "cos";
    FunctionName["Tan"] = "tan";
    FunctionName["Csc"] = "csc";
    FunctionName["Sec"] = "sec";
    FunctionName["Cot"] = "cot";
    // Inverse Trigonometry
    FunctionName["Arcsin"] = "arcsin";
    FunctionName["Arccos"] = "arccos";
    FunctionName["Arctan"] = "arctan";
    FunctionName["Arccsc"] = "arccsc";
    FunctionName["Arcsec"] = "arcsec";
    FunctionName["Arccot"] = "arccot";
})(FunctionName || (exports.FunctionName = FunctionName = {}));
