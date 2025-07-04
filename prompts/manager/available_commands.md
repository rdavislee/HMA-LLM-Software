# Available Terminal Commands for Managers

**IMPORTANT: All terminal commands are executed from the root directory of the project, regardless of which folder the agent is responsible for.**

## Testing Guidelines

**Direct Testing Limit:** Manager agents may run **one** direct test execution per task to get an immediate picture of the current state.

**After this single direct run, all further testing must use tester agents via `SPAWN tester`.**

## Language-Specific Commands

### TypeScript Projects

**Compilation & Diagnostics:**
```
RUN "npx tsc --noEmit"          // Check errors without compiling
RUN "npm run build"             // Full compilation
```

**Single Direct Test (after compilation):**
```
RUN "npm test"                  // Run test suite once
```

**Code Quality:**
```
RUN "npx eslint src/"          // Linting
RUN "npx tsc --noEmit"         // Type checking
```

### Python Projects

**Single Direct Test:**
```
RUN "python -m pytest -v"       // Run test suite once
```

**Code Quality:**
```
RUN "flake8 src/"              // Linting
RUN "mypy src/"                // Type checking
RUN "black src/ --check"       // Format checking
```

### Java Projects

**Compilation:**
```
RUN "mvn compile"              // Maven compilation
RUN "gradle build"             // Gradle build
```

**Single Direct Test:**
```
RUN "mvn test"                 // Maven tests once
RUN "gradle test"              // Gradle tests once
```

## File Inspection (PowerShell)

```
RUN "type src/calculator.ts"                    // View file contents
RUN "dir src"                                   // List directory
RUN "findstr /n \"class\" src/calculator.ts"    // Search with line numbers
```

## Testing Workflow Examples

### TypeScript Testing Workflow
```
// Step 1: Compile
RUN "npm run build"

// Step 2: One direct test for initial assessment
RUN "npm test"

// Step 3: If tests fail or need investigation
SPAWN tester PROMPT="Debug failing tests in calculator module - identify root cause"
WAIT

// Step 4: Based on tester findings, delegate fixes
DELEGATE file "calculator.ts" PROMPT="Fix divide by zero handling based on test failures"

// Step 5: After fix, use tester for verification
SPAWN tester PROMPT="Verify calculator.ts fixes - ensure all tests now pass"
WAIT
```

### Python Testing Workflow
```
// Step 1: One direct test run
RUN "python -m pytest -v"

// Step 2: Tests show failures in auth module
SPAWN tester PROMPT="Investigate auth.py test failures - check token validation logic"
WAIT

// Step 3: Tester identifies issue, delegate fix
DELEGATE file "auth.py" PROMPT="Fix token expiry check - should use UTC time not local"

// Step 4: Verify with tester
SPAWN tester PROMPT="Test auth.py after UTC time fix"
WAIT
```

### Java Testing Workflow
```
// Step 1: Compile
RUN "mvn compile"

// Step 2: One direct test
RUN "mvn test"

// Step 3: Complex integration test failures
SPAWN tester PROMPT="Debug UserService integration test failures"
WAIT

// Step 4: Fix based on analysis
DELEGATE file "UserService.java" PROMPT="Fix transaction rollback in createUser method"

// Step 5: Comprehensive retest
SPAWN tester PROMPT="Run full UserService test suite including integration tests"
WAIT
```

## When to Use Tester Agents

**Use direct test command (once) when:**
- Getting initial test status
- Quick pass/fail check needed
- Simple verification after compilation

**Must use tester agent when:**
- Already ran direct test once
- Need to debug specific failures
- Want detailed error analysis
- Testing integration between modules
- Need to run subset of tests
- Investigating flaky tests
- Need test coverage analysis

## Common Patterns

### Initial Module Check
```
// TypeScript
RUN "npm run build"
RUN "npm test"
// If any failures, switch to tester

// Python  
RUN "python -m pytest -v"
// If any failures, switch to tester

// Java
RUN "mvn compile"
RUN "mvn test"
// If any failures, switch to tester
```

### Deep Test Investigation
```
// Never do this:
RUN "npm test"
RUN "npm test -- --grep calculator"  // ❌ Second test run forbidden

// Do this instead:
RUN "npm test"
SPAWN tester PROMPT="Focus on calculator module test failures"
WAIT
```

### Module Integration Testing
```
// Always use tester for complex scenarios
SPAWN tester PROMPT="Test parser and lexer integration - verify token passing"
WAIT

SPAWN tester PROMPT="Test full authentication flow from login to token refresh"
WAIT
```

## Key Rules

1. **One direct test per task** - After that, use tester agents
2. **Always compile first** for compiled languages
3. **Root directory execution** - All commands run from project root
4. **Tester for debugging** - Any investigation beyond pass/fail needs tester
5. **Tester for retests** - Cannot run same test command twice directly