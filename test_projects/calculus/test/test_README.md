# Test Module
Directory Contents
Files

expression.test.ts - [BLOCKED] Tests for the mathematical expression ADT are blocked by missing 'evaluate' and 'differentiate' methods on Expression ADT nodes in src/expression.ts and src/expressionInterface.ts.
parser.test.ts - [BLOCKED] Tests for the parser module are blocked due to missing exports (e.g., 'ConstantNode' from src/expression.ts) and missing 'evaluate'/'differentiate' methods on ADT nodes from src/expression.ts/Interface. Requires changes in src/ directory.
utils.test.ts - [BLOCKED] Compilation error fixed, but ExpressionSimplifier test 'should simplify x / 1 to x' is failing. This is due to a missing simplification rule for division by 1 in src/utils.ts, which is outside this manager's scope. Requires changes in src/utils.ts.

Subdirectories

(No subdirectories)
