# Project: Command-Line Symbolic Calculator

## Product Vision
A command-line tool, built from scratch in TypeScript, that can parse, evaluate, differentiate, and integrate mathematical expressions symbolically. The tool will handle standard algebraic and trigonometric functions, constants, and variables, providing an interactive loop for continuous calculations.

## Architecture Overview
The application will be built around an Abstract Syntax Tree (AST). The process flow is:
**Input String -> Tokenizer -> Parser -> AST -> Operation Engine -> Simplifier -> Renderer -> Output String**

### Core Components
- **Tokenizer (Lexer):** Scans the input string and converts it into a sequence of tokens (e.g., `NUMBER`, `VARIABLE`, `PLUS`, `ARCSIN`).
- **Parser:** Takes the token stream and builds an AST, respecting the order of operations (PEMDAS).
- **Operation Engine:** A collection of modules that operate on the AST. Each operation will be in its own file.
    - **Evaluator:** Substitutes variable nodes with values and computes a numerical result.
    - **Differentiator:** Applies differentiation rules to the AST to produce a new AST for the derivative.
    - **Integrator:** Applies basic integration rules (indefinite and definite) to produce a new AST.
- **Simplifier:** A dedicated module that traverses the AST to apply a wide range of algebraic and trigonometric simplification rules.
- **CLI:** Manages user interaction, including prompting for operations, variables, and bounds, and handling the main application loop.

## Modules

### Module 1: Tokenizer (`src/parser/tokenizer.ts`)
- **Purpose**: To convert a raw mathematical expression string into a list of tokens.
- **Key Interfaces**: `tokenize(expression: string): Token[]`
- **Dependencies**: None.

### Module 2: Parser (`src/parser/parser.ts`)
- **Purpose**: To build an Abstract Syntax Tree (AST) from a list of tokens.
- **Key Interfaces**: `parse(tokens: Token[]): AstNode`
- **Dependencies**: Tokenizer.

### Module 3: Evaluator (`src/operations/evaluate.ts`)
- **Purpose**: To compute the numerical value of an AST, given variable values.
- **Key Interfaces**: `evaluate(node: AstNode, variables: Map<string, number>): number`
- **Dependencies**: Parser.

### Module 4: Differentiator (`src/operations/differentiate.ts`)
- **Purpose**: To compute the symbolic derivative of an AST with respect to a variable.
- **Key Interfaces**: `differentiate(node: AstNode, variable: string): AstNode`
- **Dependencies**: Parser, Simplifier.

### Module 5: Integrator (`src/operations/integrate.ts`)
- **Purpose**: To compute the symbolic integral (definite and indefinite) of an AST.
- **Key Interfaces**: `integrate(node: AstNode, variable: string): AstNode`
- **Dependencies**: Parser, Simplifier.

### Module 6: Simplifier (`src/operations/simplifier.ts`)
- **Purpose**: To simplify an AST using algebraic and trigonometric rules.
- **Key Interfaces**: `simplify(node: AstNode): AstNode`
- **Dependencies**: Parser.

### Module 7: CLI (`src/cli/index.ts`)
- **Purpose**: To handle all user I/O and orchestrate the calls to other modules.
- **Key Interfaces**: `run()`
- **Dependencies**: All other modules.

## Feature Specifications
- **Operators:** `+`, `-`, `*`, `/`, `^` (PEMDAS respected). Multiplication must be explicit (no `2x`).
- **Functions:**
    - `log(expr)` (base 10), `ln(expr)` (base e), `log(base, expr)`.
    - Trig: `sin`, `cos`, `tan`, `csc`, `sec`, `cot`.
    - Inverse Trig: `arcsin`, `arccos`, `arctan`, `arccsc`, `arcsec`, `arccot`.
- **Constants:** `pi`, `e`.
- **Variables:** Can be single-character (`x`) or multi-character (`alpha`).
- **Simplification:** Must be comprehensive.
    - Combine like terms: `x + x` -> `2*x`.
    - Constant folding: `2 + 3` -> `5`.
    - Identity rules: `x * 1` -> `x`, `x + 0` -> `x`.
    - Exponent rules: `x^a * x^b` -> `x^(a+b)`, `(x^a)^b` -> `x^(a*b)`, `x^a / x^b` -> `x^(a-b)`.
    - Trigonometric identities: `sin(x)^2 + cos(x)^2` -> `1`.
- **Operations:**
    - **Evaluate:** Prompts for variable values. Leaves unbound variables in the expression.
    - **Differentiate:** Prompts for the variable of differentiation.
    - **Integrate (Indefinite):** Prompts for the variable of integration. Appends `+ C` (or another unused variable).
    - **Integrate (Definite):** Prompts for variable and bounds. Bounds can be expressions.
- **Error Handling:** Clear error messages for invalid expressions or operations.
- **Interaction:** A main loop that allows reusing the previous result.

## Development Plan
1.  **Phase 1: Core Types**: Implement the foundational type definitions for tokens (`TokenType`, `Token`) and the Abstract Syntax Tree (`NodeType`, `AstNode` variants) in `src/types/`.
2.  **Phase 2: Tokenizer**: Implement the `tokenize` function in `src/parser/tokenizer.ts` with comprehensive unit tests.
3.  **Phase 3: Parser**: Implement the `parse` function in `src/parser/parser.ts` to construct an AST. Include extensive tests for operator precedence, function calls, and error handling.
4.  **Phase 4: Simplifier**: Implement the `simplify` function in `src/operations/simplify.ts`. Test various algebraic and trigonometric identities.
5.  **Phase 5: Operations**: Implement `evaluate`, `differentiate`, and `integrate` in `src/operations/` with thorough tests for each.
6.  **Phase 6: CLI**: Build the interactive command-line interface in `src/cli/index.ts` to tie all modules together.

## Environment Guide
- **Language**: TypeScript
- **Build**: `npm run build`
- **Test**: `npm test`
- **Run**: `npm start`
- **Key Libraries**:
    - `typescript`: Core language compiler.
    - `ts-node`: Execute TypeScript files directly.
    - `tsx`: High-performance TypeScript executor for development.
    - `mocha`, `chai`, `@types/mocha`, `@types/chai`: Testing framework and assertion library.