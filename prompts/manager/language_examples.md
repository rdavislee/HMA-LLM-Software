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

## File Operations (Use Sparingly)

### Creating Files/Folders 
CREATE file "src/config.json"  // Only when delegation isn't appropriate
CREATE folder "src/utils"       // Only for empty structure setup

### Deleting Files/Folders
DELETE file "old-config.json"   // Only when truly obsolete
DELETE folder "deprecated"      // Be very careful with deletions

## Spawning Tester Agents

### Test Verification for Specific Files
SPAWN tester PROMPT="Verify tests pass for calculator.ts and parser.ts files"
WAIT
SPAWN tester PROMPT="Check test coverage for all files in src/auth/ folder"
WAIT

### After Delegating Implementation
DELEGATE file "calculator.ts" PROMPT="Fix implementation"
WAIT
SPAWN tester PROMPT="Verify calculator.ts tests are now passing"
WAIT

### Multiple File Testing
DELEGATE file "userAuth.ts", file "sessionManager.ts" PROMPT="Implement authentication"
WAIT
SPAWN tester PROMPT="Test userAuth.ts and sessionManager.ts implementations"
WAIT

## Key Rules
- One command per line
- WAIT after delegations and spawns
- Paths relative to root
- Update README before FINISH
- Always compile before testing TypeScript
- Use CREATE/DELETE sparingly - prefer delegation
- Spawn testers only for complex debugging needs