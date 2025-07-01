# Manager Language Examples

## Reading Files & Folders
READ file "README.md"
READ file "calculator.ts", file "types.ts", file "utils.ts"
READ folder "docs"  // Loads docs/docs_README.md
READ folder "api"   // Loads api/api_README.md

## Delegation

### To Files (Task-Type Matching)
DELEGATE file "calculator.interface.ts" PROMPT="SPEC: Define calculator interface with arithmetic operations"
DELEGATE file "test/calculator.test.ts" PROMPT="TEST: Create comprehensive test suite for calculator interface"
DELEGATE file "calculator.ts" PROMPT="IMPLEMENT: Build calculator class to pass all tests"

### To Folders
DELEGATE folder "src" PROMPT="Implement core TypeScript functionality"
DELEGATE folder "test" PROMPT="Create comprehensive test suite"

## Running Commands

### Compilation Only
RUN "node tools/compile-typescript.js"
RUN "node tools/check-typescript.js"

## Testing via Tester Agents

### Broad Testing (Folder-Level)
SPAWN tester PROMPT="Test all files in src/ folder to ensure implementations work"
WAIT

### Specific Testing (Individual Files)
SPAWN tester PROMPT="Test calculator.ts implementation against its test suite"
WAIT

### Module Testing (Related Files)
SPAWN tester PROMPT="Test authentication module - verify userAuth.ts and sessionManager.ts work together"
WAIT

### Post-Implementation Verification
SPAWN tester PROMPT="Verify all tests pass for calculator module after recent implementation"
WAIT

### Child Result Verification (CRITICAL - Prevents hallucination issues)
// Child reports completion or failure
READ file "calculator.ts"  // Always verify actual file state
// Check if implementation exists despite failure claims
SPAWN tester PROMPT="Test calculator.ts implementation to verify current functionality"
WAIT
// Make decisions based on actual file state, not child reports

## README Updates

### Basic Inventory
UPDATE_README CONTENT="# Module Manager\nDirectory Contents\nFiles\n\ncalculator.ts - [IMPLEMENTED] Calculator with arithmetic operations\ncalculator.interface.ts - [COMPLETE] TypeScript interface\ncalculator_README.md - [COMPLETE] This file\n\nSubdirectories\n\ntest/ - [IN PROGRESS] 4/6 test files implemented\ndocs/ - [NOT STARTED] Planned for API docs\n\nStatus\nCore functions complete, 80% test coverage"

**Status Values:** NOT STARTED, SPECCED, TESTS ONLY, IN PROGRESS, IMPLEMENTED, COMPLETE, BLOCKED

## Complete Workflows

### Test-Driven Development (Correct File Order)
CREATE file "calculator.interface.ts"
DELEGATE file "calculator.interface.ts" PROMPT="SPEC: Define calculator interface with arithmetic operations"
WAIT
CREATE file "test/calculator.test.ts"  
DELEGATE file "test/calculator.test.ts" PROMPT="TEST: Create comprehensive tests from interface"
WAIT
CREATE file "calculator.ts"
DELEGATE file "calculator.ts" PROMPT="IMPLEMENT: Build implementation to pass all tests"
WAIT
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Test calculator module - verify implementation passes all test cases"
WAIT
UPDATE_README CONTENT="Calculator implemented with full test coverage"
FINISH PROMPT="Calculator module complete"

### Dependency Resolution Workflow
DELEGATE file "library.ts" PROMPT="IMPLEMENT: Build core library functionality"
WAIT
// Child reports: "Missing moduleA.ts implementation"
// CRITICAL: Verify claim before believing it
READ file "library.ts"  // Check if any work was actually done
// If file has partial implementation despite "missing dependency" claim:
SPAWN tester PROMPT="Test library.ts current state - identify what actually works vs what's missing"
WAIT
// Based on verification, either delegate dependencies or continue with library
DELEGATE file "moduleA.ts" PROMPT="IMPLEMENT: Build specialized processing module"
WAIT  
DELEGATE file "moduleB.ts" PROMPT="IMPLEMENT: Build data type definitions and utilities"
WAIT
// Now retry original task with dependencies resolved
DELEGATE file "library.ts" PROMPT="IMPLEMENT: Build library using moduleA.ts and moduleB.ts"
WAIT
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Test complete library module with all dependencies"
WAIT
UPDATE_README CONTENT="Library implemented with proper separation: moduleB.ts (types), moduleA.ts (processing), library.ts (coordination)"
FINISH PROMPT="Library module complete with proper dependency structure"

### Implementation Verification Workflow (With Hallucination Protection)
READ file "calculator.ts"
RUN "node tools/check-typescript.js"
DELEGATE file "calculator.ts" PROMPT="Fix TypeScript errors"
WAIT
// Child reports: "Failed to fix errors due to parsing issues"
// CRITICAL: Don't trust the report - verify actual state
READ file "calculator.ts"  // Check if fixes were actually applied
RUN "node tools/compile-typescript.js"  // Test actual compilation status
// If compilation succeeds despite child's "failure" claim:
SPAWN tester PROMPT="Test calculator.ts after TypeScript error fixes"
WAIT
FINISH PROMPT="TypeScript errors fixed and tests passing - child was hallucinating failure"

### Multi-File Implementation with Testing
DELEGATE file "userAuth.ts", file "sessionManager.ts" PROMPT="Implement authentication components"
WAIT
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Test authentication system - verify userAuth.ts and sessionManager.ts integration"
WAIT
UPDATE_README CONTENT="Authentication system implemented and tested"
FINISH PROMPT="Authentication module complete with integration testing"

## File Operations (Use Sparingly)

### Creating Files/Folders 
CREATE file "src/config.json"
CREATE folder "src/utils"

### Deleting Files/Folders
DELETE file "old-config.json"
DELETE folder "deprecated"

## Spawning Tester Agents

### Broad Testing Examples
SPAWN tester PROMPT="Test all files in src/ directory for compilation and runtime errors"
WAIT

SPAWN tester PROMPT="Run complete test suite for authentication module"
WAIT

SPAWN tester PROMPT="Verify test coverage across all implemented files in this folder"
WAIT

### Specific Testing Examples
SPAWN tester PROMPT="Test calculator.ts implementation against test/calculator.test.ts"
WAIT

SPAWN tester PROMPT="Debug failing tests in userController.ts - identify root cause"
WAIT

SPAWN tester PROMPT="Test integration between parser.ts and lexer.ts modules"
WAIT

### Post-Delegation Testing
DELEGATE file "calculator.ts" PROMPT="Fix implementation based on test failures"
WAIT
SPAWN tester PROMPT="Retest calculator.ts to confirm fixes resolved issues"
WAIT

## Child Verification Workflows (CRITICAL)

### When Child Reports Failure
```
// Child says: "Cannot implement due to parsing errors"
READ file "problematic-file.ts"  // Check actual file state
// If file contains new implementation:
SPAWN tester PROMPT="Test problematic-file.ts to verify if implementation actually works"
WAIT
// If tester confirms it works:
UPDATE_README CONTENT="Implementation complete despite child's incorrect failure report"
FINISH PROMPT="Task complete - child was hallucinating parsing errors"
```

### When Child Reports Success  
```
// Child says: "Implementation complete" or "Tests are implemented"
READ file "completed-file.ts"  // Verify work was actually done
// If file is empty or only contains boilerplate despite "complete" claim:
DELEGATE file "completed-file.ts" PROMPT="Actually implement the required functionality"
WAIT
// If file has substantial content:
SPAWN tester PROMPT="Test completed-file.ts to confirm functionality"
WAIT
// Proceed based on actual verification, not child's claim
```

### When Child Reports Missing Dependencies
```
// Child says: "Cannot proceed - missing functions from other files"
READ file "child-file.ts"  // Check if any work was actually done
// If file has substantial implementation:
SPAWN tester PROMPT="Test child-file.ts current state - identify what actually works"
WAIT
// Often child has working code but thinks it failed
```

## Key Rules
- One command per line
- WAIT after delegations and spawns  
- Paths relative to root
- Update README before FINISH
- Always compile before spawning testers for TypeScript
- Use CREATE/DELETE sparingly - prefer delegation
- Use tester agents for ALL testing verification
- **ALWAYS verify child work with READ before trusting reports**