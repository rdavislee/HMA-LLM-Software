# Manager Language Examples

## Reading Files & Folders
READ file "README.md"
READ file "calculator.ts", file "types.ts", file "utils.ts"
READ folder "docs"  // Loads docs/docs_README.md
READ folder "api"   // Loads api/api_README.md

## Delegation

### To Files
DELEGATE file "calculator.ts" PROMPT="Implement calculator class with basic arithmetic"
DELEGATE file "calculator.interface.ts" PROMPT="Define TypeScript interface"
DELEGATE file "test/calculator.test.ts" PROMPT="Create comprehensive test suite"

### To Folders
DELEGATE folder "src" PROMPT="Implement core TypeScript functionality"
DELEGATE folder "test" PROMPT="Create comprehensive test suite"

## Running Commands

### TypeScript Testing (Required Sequence)
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"

### With Options
RUN "node tools/run-mocha.js --grep 'specific test'"
RUN "node tools/run-mocha.js dist/test/calculator.test.js"

## README Updates

### Basic Inventory
UPDATE_README CONTENT_STRING="# Module Manager
Directory Contents
Files

calculator.ts - [IMPLEMENTED] Calculator with arithmetic operations
calculator.interface.ts - [COMPLETE] TypeScript interface
calculator_README.md - [COMPLETE] This file

Subdirectories

test/ - [IN PROGRESS] 4/6 test files implemented
docs/ - [NOT STARTED] Planned for API docs

Status
Core functions complete, 80% test coverage"

**Status Values:** NOT STARTED, SPECCED, TESTS ONLY, IN PROGRESS, IMPLEMENTED, COMPLETE, BLOCKED

## Complete Workflows

### Test-Driven Development
DELEGATE file "calculator.ts" PROMPT="SPEC: Define calculator interface"
WAIT
DELEGATE file "test/calculator.test.ts" PROMPT="TEST: Create tests from spec"
WAIT
DELEGATE file "calculator.ts" PROMPT="IMPLEMENT: Build to pass all tests"
WAIT
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
UPDATE_README CONTENT_STRING="Calculator implemented with full test coverage"
FINISH PROMPT="Calculator module complete"

### Quick Implementation Check
READ file "calculator.ts"
RUN "node tools/check-typescript.js"
DELEGATE file "calculator.ts" PROMPT="Fix TypeScript errors"
WAIT
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
FINISH PROMPT="TypeScript errors fixed"

## Key Rules
- One command per line
- WAIT after delegations
- Paths relative to root
- Update README before FINISH
- Always compile before testing TypeScript