Available Terminal Commands for Coder Agents
IMPORTANT: All terminal commands are executed from the root directory of the project, regardless of which file the agent is responsible for.
Testing Restrictions
⚠️ CODER AGENTS GET ONE DIRECT TEST PER TASK ⚠️

ONE test execution allowed - Run tests directly ONCE, then use tester agents
Compilation unlimited - Compile as needed, but analyze errors with testers
No test-fix loops - After first test failure, must use tester agents

Language-Specific Commands
TypeScript Projects
Compilation & Diagnostics:
RUN "npx tsc --noEmit"          // Check errors without output
RUN "npm run build"             // Full compilation
One Direct Test:
RUN "npm test"                  // Allowed ONCE per task
After First Test - Use Testers:
SPAWN tester PROMPT="Analyze test failures in calculator.ts"
WAIT
Python Projects
One Direct Test:
RUN "python -m pytest -v"       // Allowed ONCE per task
Code Quality:
RUN "flake8 src/calculator.py"  // Lint specific file
RUN "mypy src/calculator.py"    // Type check specific file
Java Projects
Compilation:
RUN "mvn compile"              // Maven compilation
RUN "gradle build"             // Gradle build
One Direct Test:
RUN "mvn test"                 // Allowed ONCE per task
RUN "gradle test"              // Allowed ONCE per task
File Inspection (PowerShell)
RUN "type src/calculator.ts"                    // View file contents
RUN "findstr /n \"function\" src/calculator.ts" // Search with line numbers
Testing Workflow Examples
TypeScript Workflow
// Step 1: Initial implementation done
RUN "npm run build"

// Step 2: Your ONE direct test
RUN "npm test"

// Step 3: Tests fail - MUST use tester now
SPAWN tester PROMPT="Debug failing divide tests in calculator.ts"
WAIT

// Step 4: Fix based on tester analysis
REPLACE FROM="return a / b;" TO="if (b === 0) throw new Error('Division by zero');\nreturn a / b;"

// Step 5: Need to test again? Use tester
SPAWN tester PROMPT="Verify calculator.ts division fix"
WAIT
Python Workflow
// Step 1: Implementation complete
RUN "python -m pytest -v"  // Your ONE direct test

// Step 2: Multiple failures - spawn multiple testers
SPAWN tester PROMPT="Debug auth failures", tester PROMPT="Debug validation errors"
WAIT

// Step 3: Fix based on analysis
REPLACE FROM="if not email:" TO="if not email or '@' not in email:"

// Step 4: Retest with tester
SPAWN tester PROMPT="Verify auth.py email validation fix"
WAIT
Compilation Error Workflow
// Step 1: Try to compile
RUN "npm run build"

// Step 2: Compilation errors - don't guess!
SPAWN tester PROMPT="Analyze TypeScript errors - identify missing imports"
WAIT

// Step 3: If missing dependency
FINISH PROMPT="Missing dependency: need parseExpression from parser module"

// Step 4: If fixable
REPLACE FROM="import { Token }" TO="import { Token, TokenType }"
Loop Prevention Patterns
❌ FORBIDDEN Pattern
RUN "npm test"
// Tests fail
RUN "npm test"  // ❌ FORBIDDEN - already used direct test
// More failures
RUN "npm test"  // ❌ FORBIDDEN - causing loop
✅ CORRECT Pattern
RUN "npm test"  // Your ONE test
// Tests fail
SPAWN tester PROMPT="Analyze all test failures"
WAIT
// Fix based on analysis
SPAWN tester PROMPT="Verify fixes"
WAIT
Compilation Loop Prevention
RUN "npm run build"
// Errors
// Fix attempt
RUN "npm run build"
// Still errors - STOP!
SPAWN tester PROMPT="Debug persistent compilation errors"
WAIT
Multiple Tester Strategy
// When many tests fail, divide the work
RUN "npm test"  // Shows 15 failures

// Don't do this:
SPAWN tester PROMPT="Fix all 15 test failures"  // Too broad

// Do this instead:
SPAWN tester PROMPT="Debug arithmetic operation failures", tester PROMPT="Debug input validation failures", tester PROMPT="Debug edge case handling failures"
WAIT
Common Anti-Patterns to Avoid
❌ Test-Fix-Test Loop
RUN "npm test"
REPLACE FROM="..." TO="..."
RUN "npm test"  // ❌ FORBIDDEN
REPLACE FROM="..." TO="..."
RUN "npm test"  // ❌ FORBIDDEN
❌ Blind Compilation Fixes
RUN "npm run build"
// Error: Cannot find name 'validateInput'
REPLACE FROM="validateInput(" TO="this.validateInput("
RUN "npm run build"
// Error: Property 'validateInput' does not exist
REPLACE FROM="this.validateInput(" TO="// validateInput("
// ❌ Just commenting out instead of understanding
✅ Correct Approach
RUN "npm run build"
// Error: Cannot find name 'validateInput'
SPAWN tester PROMPT="Analyze missing validateInput - should it be imported or implemented?"
WAIT
// Tester says: "Should be imported from utils"
REPLACE FROM="import { calculate }" TO="import { calculate, validateInput }"
Key Rules

ONE test per task - Direct test execution limited to once
Unlimited compilation - But analyze errors with testers
Root directory execution - All commands run from project root
Testers for debugging - Any analysis beyond first attempt
Multiple testers for complex issues - Divide and conquer
No loops - Recognize when you're repeating actions