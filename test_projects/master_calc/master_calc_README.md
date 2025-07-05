# Command-Line Symbolic Calculator

This project implements a command-line tool for symbolic mathematical operations.

## Subdirectories
- src/ - [BEGUN] Core source code for the calculator; module import paths have been refactored.
- src/parser/ - [FINISHED] Tokenizer and Parser modules.
- src/operations/ - [BEGUN] Operations like Simplifier, Evaluator, Differentiator, Integrator.

## Files
- src/types/tokens.ts - [FINISHED] Defines all token types.
- src/types/ast.ts - [FINISHED] Defines Abstract Syntax Tree node classes.
- src/utils/constants.ts - [FINISHED] Mathematical constants (pi, e).
- src/utils/error.ts - [FINISHED] Custom application-specific error handling.
- src/parser/tokenizer.ts - [FINISHED] Converts input string into a stream of tokens.
- src/parser/tokenizer.test.ts - [FINISHED] Comprehensive tests for the tokenizer.
- src/parser/parser.interface.ts - [FINISHED] Defines the parser interface and AST node types.
- src/parser/parser.ts - [FINISHED] Implements the parser to build an AST from tokens.
- src/parser/parser.test.ts - [FINISHED] Comprehensive tests for the parser.
- src/operations/differentiate.ts - [BEGUN] Implementation of the symbolic differentiation function.
- src/operations/differentiate.test.ts - [BEGUN] Tests for the differentiate function.