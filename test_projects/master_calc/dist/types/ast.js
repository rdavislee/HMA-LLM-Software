export var NodeType;
(function (NodeType) {
    NodeType["Number"] = "Number";
    NodeType["Variable"] = "Variable";
    NodeType["Constant"] = "Constant";
    NodeType["BinaryOperation"] = "BinaryOperation";
    NodeType["UnaryOperation"] = "UnaryOperation";
    NodeType["FunctionCall"] = "FunctionCall";
})(NodeType || (NodeType = {}));
