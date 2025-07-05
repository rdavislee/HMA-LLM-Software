Coder Language Examples
⚠️ CRITICAL: Always Read Context First
// Parent said: "Read calculator.interface.ts for specs and calculator.test.ts for requirements"
READ "src/calculator.interface.ts"
READ "src/calculator.test.ts"
READ "src/utils.ts"  // Check available utilities
// NOW you understand what to build
Command Selection Guide
CHANGE - Complete File Replacement (Empty Files or Total Rewrites)
// Empty file - initial implementation
CHANGE CONTENT="export class Calculator {\n  add(a: number, b: number): number {\n    return a + b;\n  }\n}"

// Complete rewrite - switching approaches
CHANGE CONTENT="// Functional approach instead of class\nexport const add = (a: number, b: number): number => a + b;\nexport const subtract = (a: number, b: number): number => a - b;"
REPLACE - Targeted Edits (90% of Work)
// Single replacement
REPLACE FROM="return a + b;" TO="if (!Number.isFinite(a) || !Number.isFinite(b)) throw new Error('Invalid input');\nreturn a + b;"

// Multiple replacements in one command
REPLACE FROM="let userName" TO="let username", FROM="let userEmail" TO="let email", FROM="let userAge" TO="let age"

// Two replacements in one line
REPLACE FROM="const API_URL = 'http://localhost:3000';" TO="const API_URL = process.env.API_URL || 'http://localhost:3000';", FROM="const DEBUG = false;" TO="const DEBUG = process.env.NODE_ENV === 'development';"

// Four replacements in one line
REPLACE FROM="firstName" TO="first_name", FROM="lastName" TO="last_name", FROM="emailAddress" TO="email", FROM="phoneNumber" TO="phone"

// Complex multiline replacement
REPLACE FROM="function validateUser(user) {\nreturn user.email && user.password;\n}" TO="function validateUser(user) {\nif (!user) return false;\nreturn user.email && user.email.includes('@') && user.password && user.password.length >= 8;\n}"
INSERT - Adding Code After Existing Text
// Add import after existing one
INSERT FROM="import React" TO="\nimport PropTypes from 'prop-types';"

// Add method to class
INSERT FROM="class Calculator {" TO="\n  constructor() {\n    this.precision = 10;\n  }"

// Add enum value
INSERT FROM="enum Status {" TO="\n  Archived = 'archived',"
Testing Protocol Examples
TypeScript Testing Workflow
// After implementation
RUN "npm run build"
// ONE COMMAND PER API CALL
RUN "npm test"  // Your ONE direct test

Persistent Compilation Failure and Escalation Example
// Agent attempts to build after implementation
RUN "npm run build"
// Compilation errors - agent tries targeted fixes
REPLACE FROM="let result = calculate(a, b);" TO="let result = add(a, b);"
// ONE COMMAND PER API CALL
RUN "npm run build"
// More errors - agent tries another fix
REPLACE FROM="import { add } from './math';" TO="import { add } from './utils';"
// ONE COMMAND PER API CALL
RUN "npm run build"
// Still failing - agent tries a few more REPLACE attempts
REPLACE FROM="export function add" TO="export const add"
// ONE COMMAND PER API CALL
RUN "npm run build"
// After several cycles, errors persist and are not localizable to a single line
// Agent spawns a tester to analyze persistent compilation errors
SPAWN tester PROMPT="Analyze persistent TypeScript compilation errors in calculator.ts and suggest root causes or missing dependencies."
// If tester feedback does not resolve the issue, agent decides to try a complete rewrite
CHANGE CONTENT="// New approach: rewrite as a class\nexport class Calculator {\n  add(a: number, b: number): number {\n    return a + b;\n  }\n}"
// ONLY ONE COMMAND PER API CALL
RUN "npm run build"
// If errors still persist after rewrite
FINISH PROMPT="Tried multiple targeted fixes, tester analysis, and a complete rewrite, but compilation errors remain. Unable to resolve with current context. Requesting parent agent to diagnose and provide guidance on persistent errors."

// Tests fail - need analysis
SPAWN tester PROMPT="Analyze test failures in calculator.ts - focus on division operations"

// Fix based on tester findings
REPLACE FROM="return a / b;" TO="if (b === 0) throw new Error('Division by zero');\nreturn a / b;"

// Need to retest? Use tester
SPAWN tester PROMPT="Verify calculator.ts division fix"
Python Testing Workflow
RUN "python -m pytest -v"  // Your ONE direct test

// Multiple test failures - divide and conquer
SPAWN tester PROMPT="Debug authentication failures in auth.py", tester PROMPT="Debug validation errors in auth.py", tester PROMPT="Investigate token expiry issues in auth.py"
Compilation Error Handling
RUN "npm run build"
// Compilation errors - don't guess, analyze!

SPAWN tester PROMPT="Analyze TypeScript errors in parser.ts - identify missing type imports"

// If missing dependency
FINISH PROMPT="Missing dependency: need TokenType from lexer module"

// If fixable locally
REPLACE FROM="import { Parser }" TO="import { Parser, ParserOptions }"
Complete Workflow Examples
Empty File Implementation
// Read context as instructed
READ "src/user.interface.ts"
// ONE COMMAND PER API CALL
READ "src/user.test.ts"

// Empty file - use CHANGE
CHANGE CONTENT="import { IUser } from './user.interface';\nimport bcrypt from 'bcrypt';\n\nexport class UserService {\n  async createUser(data: Omit<IUser, 'id'>): Promise<IUser> {\n    const hashedPassword = await bcrypt.hash(data.password, 10);\n    return {\n      id: generateId(),\n      ...data,\n      password: hashedPassword\n    };\n  }\n}"

RUN "npm run build"
// ONE COMMAND PER API CALL
RUN "npm test"

// Fix issues with tester help
SPAWN tester PROMPT="Debug UserService test failures"
WAIT

REPLACE FROM="return {" TO="const now = new Date();\n    return {"
REPLACE FROM="password: hashedPassword" TO="password: hashedPassword,\n      createdAt: now,\n      updatedAt: now"

SPAWN tester PROMPT="Verify UserService fixes"
WAIT

FINISH PROMPT="UserService implemented with all tests passing"
Existing File Enhancement
READ "src/calculator.interface.ts"
READ "src/calculator.test.ts"

// File has basic implementation - enhance with REPLACE
REPLACE FROM="add(a: number, b: number): number {\n    return a + b;\n  }" TO="add(a: number, b: number): number {\n    this.validateNumbers(a, b);\n    return a + b;\n  }"

// Add validation method
INSERT FROM="export class Calculator {" TO="\n  private validateNumbers(...nums: number[]): void {\n    for (const num of nums) {\n      if (!Number.isFinite(num)) {\n        throw new Error('Invalid number input');\n      }\n    }\n  }\n"

// Multiple fixes at once
REPLACE FROM="subtract(a: number, b: number)" TO="subtract(a: number, b: number): number", FROM="multiply(a: number, b: number)" TO="multiply(a: number, b: number): number", FROM="divide(a: number, b: number)" TO="divide(a: number, b: number): number"
//ONE COMMAND PER API CALL
RUN "npm test"

SPAWN tester PROMPT="Test calculator after validation additions"


FINISH PROMPT="Calculator enhanced with input validation"
Complex Debugging Scenario
READ "src/auth.interface.ts"
READ "src/auth.test.ts"
READ "src/utils/jwt.ts"

// Initial implementation attempt
CHANGE CONTENT="import jwt from 'jsonwebtoken';\nimport { IAuthService } from './auth.interface';\n\nexport class AuthService implements IAuthService {\n  async login(email: string, password: string): Promise<string> {\n    // Validate credentials\n    const user = await this.validateUser(email, password);\n    if (!user) throw new Error('Invalid credentials');\n    \n    // Generate token\n    return jwt.sign({ userId: user.id }, process.env.JWT_SECRET);\n  }\n}"

RUN "npm run build"
// Compilation errors

SPAWN tester PROMPT="Analyze compilation errors - missing validateUser method"
WAIT

// Tester says validateUser should come from UserService
FINISH PROMPT="Missing dependency: need validateUser from UserService module"
Multiple Tester Strategy
// Complex module with many test failures
RUN "npm test"

// Spawn specialized testers
SPAWN tester PROMPT="Debug parser syntax errors", tester PROMPT="Debug parser precedence issues", tester PROMPT="Debug parser error recovery"

// Each tester provides focused feedback
// Fix based on specific recommendations
REPLACE FROM="parseFactor()" TO="parseFactor(): ASTNode", FROM="parseTerm()" TO="parseTerm(): ASTNode", FROM="parseExpression()" TO="parseExpression(): ASTNode"

SPAWN tester PROMPT="Verify parser fixes across all test categories"
Special Characters and Escaping
String with Newline Characters
// Literal \n in string (becomes actual newline in output)
REPLACE FROM="const message = 'Hello';" TO="const message = 'Hello\\nWorld';"

// Structural newlines in code
REPLACE FROM="if (user) {\nreturn user.name;\n}" TO="if (user && user.active) {\nreturn user.name.trim();\n}"
Regular Expressions
REPLACE FROM="const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;" TO="const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$/;"
Complex Error Handling
REPLACE FROM="try {\nconst response = await api.call();\nreturn response.data;\n} catch (error) {\nthrow error;\n}" TO="try {\nconst response = await api.call();\nif (!response || !response.data) {\nthrow new Error('Invalid API response');\n}\nreturn response.data;\n} catch (error) {\nconsole.error('API call failed:', error.message);\nthrow new Error(`API Error: ${error.message}`);\n}"
Loop Prevention Examples
REPLACE Failure → CHANGE Pattern
// Try targeted fix
REPLACE FROM="if (/ (sin|cos|tan|log|sqrt|exp|abs) /i.test(trimmedExpression)) {" TO="if (/\\b(sin|cos|tan|log|sqrt|exp|abs)\\b/i.test(trimmedExpression)) {"
// Failed: String not found

REPLACE FROM="if (/(sin|cos|tan|log|sqrt|exp|abs /i.test(trimmedExpression)) {" TO="if (/\\b(sin|cos|tan|log|sqrt|exp|abs)\\b/i.test(trimmedExpression)) {"
// Failed: String not found

// After 2-3 failures, switch to CHANGE
READ "src/mathEngine.ts"

CHANGE CONTENT="// Complete implementation with fixed regex\nimport { create, MathJsInstance } from 'mathjs';\n\nconst math: MathJsInstance = create({});\n\nexport class MathJSEngine {\n  evaluate(expression: string): number {\n    if (/\\b(sin|cos|tan|log|sqrt|exp|abs)\\b/i.test(expression)) {\n      throw new Error('Invalid expression');\n    }\n    return math.evaluate(expression);\n  }\n}"
Extended Attempts Without Progress
// After 5 cycles of test-fix-test with no improvement
FINISH PROMPT="After 5 attempts, still failing 8 tests. Issue appears to be architectural - async handling in tests doesn't match sync implementation. Need parent guidance on async requirements."
Task Type Examples
SPEC Task (Empty Interface File)
READ "requirements.md"

CHANGE CONTENT="/**\n * Calculator service interface\n * @precondition: All numeric inputs must be finite numbers\n * @postcondition: Results are accurate to 10 decimal places\n * @throws {Error} On invalid input or division by zero\n */\nexport interface ICalculator {\n  add(a: number, b: number): number;\n  subtract(a: number, b: number): number;\n  multiply(a: number, b: number): number;\n  divide(a: number, b: number): number;\n}\n\nexport interface IScientificCalculator extends ICalculator {\n  sqrt(value: number): number;\n  pow(base: number, exponent: number): number;\n}"

FINISH PROMPT="Calculator interfaces specified with contracts"
TEST Task (Empty Test File)
READ "src/calculator.interface.ts"

CHANGE CONTENT="import { expect } from 'chai';\nimport { Calculator } from '../src/calculator';\n\n// Test partitions:\n// - Normal values: positive, negative, zero\n// - Edge cases: MAX_VALUE, MIN_VALUE, Infinity\n// - Errors: NaN inputs, null, undefined\n\ndescribe('Calculator', () => {\n  let calc: Calculator;\n  \n  beforeEach(() => {\n    calc = new Calculator();\n  });\n  \n  describe('add()', () => {\n    it('should add two positive numbers', () => {\n      expect(calc.add(2, 3)).to.equal(5);\n    });\n    \n    it('should handle negative numbers', () => {\n      expect(calc.add(-5, 3)).to.equal(-2);\n    });\n    \n    it('should throw on NaN input', () => {\n      expect(() => calc.add(NaN, 5)).to.throw('Invalid number input');\n    });\n  });\n});"

FINISH PROMPT="Calculator tests written covering all partitions"
IMPLEMENT Task (Mixed Approach)
READ "src/calculator.interface.ts"

READ "src/calculator.test.ts"

READ "src/utils/validators.ts"

// Check if we have dependencies
READ "src/utils/math-helpers.ts"  // Empty

// Can't proceed without helpers
FINISH PROMPT="Missing dependency: need math helper functions from math-helpers.ts for precision handling"
Key Patterns

Always read context first - Never start without understanding requirements
One test only - After that, use tester agents
Spawn multiple testers - Divide complex problems
REPLACE for existing code - CHANGE only for empty/rewrite
Switch to CHANGE - After REPLACE failures
Check dependencies - Don't implement what belongs elsewhere
Finish when stuck - After ~5 attempts with no progress