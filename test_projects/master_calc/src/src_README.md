# Source Code

This directory contains all the main source code for the command-line symbolic calculator, organized into logical modules. This refactoring task involves updating all relative import paths to include the '.js' extension.

## Files
- src_README.md - [FINISHED] This README file.
- src/types/tokens.ts - [FINISHED] Defines all token types for the lexer and parser.
- src/types/ast.ts - [FINISHED] Defines Abstract Syntax Tree (AST) node classes.
- src/utils/constants.ts - [FINISHED] Provides mathematical constants like PI and E.
- src/utils/error.ts - [FINISHED] Implements a custom application-specific error class.
- src/parser/parser.interface.ts - [FINISHED] Parser interface definitions.
- src/parser/parser.test.ts - [FINISHED] Test suite for the parser.
- src/parser/parser.ts - [FINISHED] Parser implementation.
- src/parser/tokenizer.ts - [FINISHED] Tokenizer implementation.
- src/parser/tokenizer.test.ts - [FINISHED] Test suite for the tokenizer.
- src/operations/integrate.ts - [FINISHED] Integration function.
- src/operations/differentiate.test.ts - [FINISHED] Test suite for differentiation.
- src/cli/index.ts - [FINISHED] CLI main entry point.
- src/cli/index.test.ts - [FINISHED] Test suite for CLI.
- src/operations/differentiate.ts - [FINISHED] Differentiate function.
- src/operations/evaluate.ts - [FINISHED] Evaluate function.
- src/operations/evaluate.test.ts - [FINISHED] Test suite for evaluation.
- src/operations/integrate.ts - [FINISHED] Integration function.
- src/operations/integrate.test.ts - [FINISHED] Test suite for integration.
- src/operations/simplify.ts - [FINISHED] Simplify function.
- src/operations/simplify.test.ts - [FINISHED] Test suite for simplification.

## Subdirectories
- cli/ - [FINISHED] Manages user interaction and the main application loop.
- operations/ - [FINISHED] Contains modules for evaluating, differentiating, integrating, and simplifying ASTs.
- parser/ - [FINISHED] Handles tokenization and parsing to build the AST.
- types/ - [FINISHED] Defines core data structures like tokens and AST nodes.
- utils/ - [FINISHED] Provides general utility functions, constants, and error handling.