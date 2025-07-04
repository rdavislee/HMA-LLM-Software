Available Terminal Commands for Tester Agents
IMPORTANT: All terminal commands are executed from the root directory of the project, regardless of which agent spawned the tester.
Testing Commands by Language
TypeScript Projects
Standard Testing Workflow:
RUN "npm run build"              // Compile first
RUN "npm test"                   // Run all tests
Targeted Testing:
RUN "npm test -- --grep 'specific test'"
RUN "npx mocha dist/test/specific.test.js"
Diagnostics:
RUN "npx tsc --noEmit"          // Check TypeScript errors
RUN "npx eslint src/"           // Linting
Run Scratch Pad:
RUN "npx tsx scratch_pads/debug_script.ts"
Python Projects
Testing:
RUN "python -m pytest -v"                           // All tests
RUN "python -m pytest test/test_auth.py -v"        // Specific file
RUN "python -m pytest test/test_auth.py::test_login -v"  // Specific test
RUN "python -m pytest -k 'keyword'"                 // Tests matching keyword
RUN "python -m pytest --tb=short"                   // Shorter traceback
Code Quality:
RUN "flake8 src/"               // Style checking
RUN "mypy src/"                 // Type checking
RUN "black src/ --check"        // Format checking
Coverage:
RUN "python -m pytest --cov=src --cov-report=term"
Run Scratch Pad:
RUN "python scratch_pads/debug_script.py"
Java Projects
Testing:
RUN "mvn test"                                      // All tests
RUN "mvn test -Dtest=CalculatorTest"              // Specific test class
RUN "mvn test -Dtest=CalculatorTest#testAdd"      // Specific method
RUN "gradle test"                                   // Gradle alternative
Run Scratch Pad:
RUN "javac scratch_pads/DebugScript.java && java -cp scratch_pads:. DebugScript"
File Inspection (PowerShell)
RUN "type src/calculator.ts"                    // View file contents
RUN "findstr /n \"function\" src/calculator.ts" // Search with line numbers
RUN "dir src"                                   // List directory
RUN "Get-Content src/calculator.ts | Select-String 'pattern'"  // PowerShell search
Scratch Pad Execution
TypeScript:
RUN "npx tsx scratch_pads/debug_script.ts"     // Fast execution with tsx
RUN "npx ts-node scratch_pads/debug_script.ts" // Alternative
Python:
RUN "python scratch_pads/debug_script.py"
Java:
RUN "cd scratch_pads && javac DebugScript.java && java DebugScript"
Common Investigation Patterns
Quick Test Status Check
// TypeScript
RUN "npm run build && npm test"

// Python
RUN "python -m pytest -v"

// Java  
RUN "mvn test"
Specific Test Investigation
// TypeScript - single test
RUN "npm test -- --grep 'should handle division by zero'"

// Python - single test
RUN "python -m pytest test/test_calc.py::test_division_by_zero -v"

// Java - single test
RUN "mvn test -Dtest=CalculatorTest#testDivisionByZero"
Error Diagnostics
// TypeScript compilation errors
RUN "npx tsc --noEmit"

// Python import errors
RUN "python -c \"import src.calculator; print('Import successful')\""

// Java compilation
RUN "mvn compile"
Coverage Analysis
// TypeScript
RUN "npm test -- --coverage"

// Python
RUN "python -m pytest --cov=src --cov-report=term --cov-report=html"

// Java
RUN "mvn test jacoco:report"
Quick Diagnostic Commands
// Check if file exists
RUN "if exist src\calculator.ts (echo File exists) else (echo File not found)"

// Count test files
RUN "dir /s /b test\*.test.ts | find /c \".test.ts\""

// Find TODO comments
RUN "findstr /n \"TODO\" src\*.ts"
Environment Verification
// Node/TypeScript
RUN "node --version"
RUN "npm --version"
RUN "npx tsc --version"

// Python
RUN "python --version"
RUN "pip list | findstr pytest"

// Java
RUN "java --version"
RUN "mvn --version"
Common Workflows
Standard Investigation
RUN "npm test"                  // See current state
READ "test/failing.test.ts"    // Understand test
READ "src/module.ts"           // Check implementation
// Report findings directly
Deep Debug (When Requested)
RUN "npm test -- --grep 'specific failure'"
READ "src/complex.ts"
CHANGE CONTENT="import { complexFunction } from '../src/complex';\n\n// Debug code here"
RUN "npx tsx scratch_pads/debug_script.ts"
// Report detailed findings
Multiple Test Failures
RUN "python -m pytest -v"       // See all failures
RUN "python -m pytest --tb=line"  // Get concise failure list
// Categorize failures and recommend parallel investigation
Remember: Most investigations need only RUN and READ commands. Use scratch pad only when parent explicitly requests deep debugging of specific issues.