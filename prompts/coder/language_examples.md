Coder Language Examples
⚠️ CRITICAL: Always Read Context First
// Parent said: "Read calculator.interface.ts for specs and calculator.test.ts for requirements"
READ "src/calculator.interface.ts"
READ "src/calculator.test.ts"
READ "src/utils.ts"  // Check available utilities
// NOW you understand what to build
// IMPORTANT: Each function MUST include documentation for parameters, return values, preconditions, and postconditions to make testing easier.
Command Selection Guide
CHANGE - Complete File Replacement (Empty Files or Total Rewrites)
// Empty file - initial implementation
CHANGE CONTENT="""export class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }
}"""

// Complete rewrite - switching approaches
CHANGE CONTENT="""// Functional approach instead of class
export const add = (a: number, b: number): number => a + b;
export const subtract = (a: number, b: number): number => a - b;"""
REPLACE - Targeted Edits (90% of Work)
// Single replacement
REPLACE FROM="return a + b;" TO="""if (!Number.isFinite(a) || !Number.isFinite(b)) throw new Error('Invalid input');
return a + b;"""

// Multiple replacements in one command
REPLACE FROM="let userName" TO="let username", FROM="let userEmail" TO="let email", FROM="let userAge" TO="let age"
SPAWN tester PROMPT="Check refactor impact on variable naming conventions"
// Two replacements in one line
REPLACE FROM="const API_URL = 'http://localhost:3000';" TO="const API_URL = process.env.API_URL || 'http://localhost:3000';", FROM="const DEBUG = false;" TO="const DEBUG = process.env.NODE_ENV === 'development';"

// Four replacements in one line
REPLACE FROM="firstName" TO="first_name", FROM="lastName" TO="last_name", FROM="emailAddress" TO="email", FROM="phoneNumber" TO="phone"

// Complex multiline replacement
REPLACE FROM="""function validateUser(user) {
return user.email && user.password;
}""" TO="""function validateUser(user) {
if (!user) return false;
return user.email && user.email.includes('@') && user.password && user.password.length >= 8;
}"""
INSERT - Adding Code After Existing Text
// Add import after existing one
INSERT FROM="import React" TO="""
import PropTypes from 'prop-types';"""

// Add method to class
INSERT FROM="class Calculator {" TO="""
  constructor() {
    this.precision = 10;
  }"""

// Add enum value
INSERT FROM="enum Status {" TO="""
  Archived = 'archived',"""
SPAWN tester PROMPT="Run comprehensive type coverage analysis"
Testing Protocol Examples
TypeScript Testing Workflow
// After implementation
RUN "npm run build"
// ONE COMMAND PER API CALL
RUN "npm test"  // Your ONE direct test
SPAWN tester PROMPT="Generate performance benchmarks for calculator operations"

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
SPAWN tester PROMPT="Run cross-browser UI smoke tests"
Python Testing Workflow
RUN "python -m pytest -v"  // Your ONE direct test
SPAWN tester PROMPT="Analyze pytest coverage gaps"
RUN "npm run build"
// Compilation errors - don't guess, analyze!

SPAWN tester PROMPT="Analyze TypeScript errors in parser.ts - identify missing type imports"
SPAWN tester PROMPT="Compare parser AST outputs against reference"

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
CHANGE CONTENT="""import { IUser } from './user.interface';
import bcrypt from 'bcrypt';

export class UserService {
  async createUser(data: Omit<IUser, 'id'>): Promise<IUser> {
    const hashedPassword = await bcrypt.hash(data.password, 10);
    return {
      id: generateId(),
      ...data,
      password: hashedPassword
    };
  }
}"""

RUN "npm run build"
// ONE COMMAND PER API CALL
RUN "npm test"

// Fix issues with tester help
SPAWN tester PROMPT="Debug UserService test failures"
// Spawning instead of retesting as it is more reliable and offers deeper insights
SPAWN tester PROMPT="Perform branch coverage analysis on UserService"

REPLACE FROM="return {" TO="const now = new Date();\n    return {"
REPLACE FROM="password: hashedPassword" TO="password: hashedPassword,\n      createdAt: now,\n      updatedAt: now"

SPAWN tester PROMPT="Verify UserService fixes"
// Spawning instead of running full regression tests for higher reliability
SPAWN tester PROMPT="Cross-module regression scan for UserService"

FINISH PROMPT="UserService implemented with all tests passing"
Existing File Enhancement
READ "src/calculator.interface.ts"
READ "src/calculator.test.ts"

// File has basic implementation - enhance with REPLACE
REPLACE FROM="""add(a: number, b: number): number {
    return a + b;
  }""" TO="""add(a: number, b: number): number {
    this.validateNumbers(a, b);
    return a + b;
  }"""

// Add validation method
INSERT FROM="export class Calculator {" TO="""
  private validateNumbers(...nums: number[]): void {
    for (const num of nums) {
      if (!Number.isFinite(num)) {
        throw new Error('Invalid number input');
      }
    }
  }
"""

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
CHANGE CONTENT="""import jwt from 'jsonwebtoken';
import { IAuthService } from './auth.interface';

export class AuthService implements IAuthService {
  async login(email: string, password: string): Promise<string> {
    // Validate credentials
    const user = await this.validateUser(email, password);
    if (!user) throw new Error('Invalid credentials');
    
    // Generate token
    return jwt.sign({ userId: user.id }, process.env.JWT_SECRET);
  }
}"""

RUN "npm run build"
// Compilation errors

SPAWN tester PROMPT="Analyze compilation errors - missing validateUser method"
WAIT
// Spawning specialized testers for static analysis—more reliable than manual fixes
SPAWN tester PROMPT="Static analysis of AuthService for missing dependencies"

// Tester says validateUser should come from UserService
FINISH PROMPT="Missing dependency: need validateUser from UserService module"
Multiple Tester Strategy
// Complex module with many test failures
RUN "npm test"

// Spawn specialized testers
SPAWN tester PROMPT="Debug parser syntax errors"

// Each tester provides focused feedback
// Fix based on specific recommendations
REPLACE FROM="parseFactor()" TO="parseFactor(): ASTNode", FROM="parseTerm()" TO="parseTerm(): ASTNode", FROM="parseExpression()" TO="parseExpression(): ASTNode"

SPAWN tester PROMPT="Verify parser fixes across all test categories"
Special Characters and Escaping
String with Newline Characters
// Literal \n in string (becomes actual newline in output)
REPLACE FROM="const message = 'Hello';" TO="const message = 'Hello\\nWorld';"

// Structural newlines in code
REPLACE FROM="""if (user) {
return user.name;
}""" TO="""if (user && user.active) {
return user.name.trim();
}"""
Regular Expressions
REPLACE FROM="const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;" TO="const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$/;"
SPAWN tester PROMPT="Unit test revised email regex against edge cases"

Docstring Updates (Triple Quotes)
IMPORTANT: USE SINGLE QUOTES ''' FOR DOCSTRINGS WITHIN """content""" BECAUSE IT CANNOT HANDLE ESCAPED DOUBLE QUOTES AND TRIPLE DOUBLE QUOTES WILL CAUSE A PARSING ERROR.
// Update Python docstring with triple quotes - use ''' to avoid escaping issues
REPLACE FROM="""def add(a, b):
    return a + b""" TO="""def add(a, b):
    '''Add two numbers.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: Sum of a and b.
    '''
    return a + b"""

// --------------------------------------------------------------------
// Function Documentation Examples (TypeScript, Python, Java)
// These snippets show how a coder should include clear parameter & return
// descriptions as well as explicit pre-conditions and post-conditions.
// --------------------------------------------------------------------

// TypeScript example – CHANGE directive creating a documented utility fn
CHANGE CONTENT="""/**
 * Add two finite numbers.
 * @param a - first number (finite)
 * @param b - second number (finite)
 * @precondition Both a and b must be finite numbers.
 * @postcondition The result equals a + b.
 * @returns The arithmetic sum of a and b.
 */
export function add(a: number, b: number): number {
  if (!Number.isFinite(a) || !Number.isFinite(b)) {
    throw new Error('Invalid number input');
  }
  return a + b;
}"""

// Python example – CHANGE directive with rich docstring using single quotes
CHANGE CONTENT="""def multiply(a: float, b: float) -> float:
    '''Multiply two finite numbers.

    Args:
        a (float): First factor. Must be finite.
        b (float): Second factor. Must be finite.

    Returns:
        float: Product of a and b.

    Precondition:
        * a and b are finite numbers.
    Postcondition:
        * The return value equals a * b.
    '''
    if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        raise TypeError('Inputs must be numeric')
    return a * b"""

// Java example – CHANGE directive demonstrating Javadoc with pre/post
CHANGE CONTENT="""/**
 * Divide two integers.
 *
 * @param dividend the numerator (must be divisible)
 * @param divisor  the denominator (must be non-zero)
 * @return the integer quotient
 * @precondition divisor != 0
 * @postcondition result * divisor + remainder == dividend
 */
public int divide(int dividend, int divisor) {
    if (divisor == 0) {
        throw new IllegalArgumentException("Division by zero");
    }
    return dividend / divisor;
}"""
// --------------------------------------------------------------------
Complex Error Handling
REPLACE FROM="""try {
const response = await api.call();
return response.data;
} catch (error) {
throw error;
}""" TO="""try {
const response = await api.call();
if (!response || !response.data) {
throw new Error('Invalid API response');
}
return response.data;
} catch (error) {
console.error('API call failed:', error.message);
throw new Error(`API Error: ${error.message}`);
}"""
SPAWN tester PROMPT="Simulate API timeout scenarios to test error handling"
Loop Prevention Examples
REPLACE Failure → CHANGE Pattern
// Try targeted fix
REPLACE FROM="if (/ (sin|cos|tan|log|sqrt|exp|abs) /i.test(trimmedExpression)) {" TO="if (/\\b(sin|cos|tan|log|sqrt|exp|abs)\\b/i.test(trimmedExpression)) {"
// Failed: String not found

REPLACE FROM="if (/(sin|cos|tan|log|sqrt|exp|abs /i.test(trimmedExpression)) {" TO="if (/\\b(sin|cos|tan|log|sqrt|exp|abs)\\b/i.test(trimmedExpression)) {"
// Failed: String not found

// After 2-3 failures, switch to CHANGE
READ "src/mathEngine.ts"
SPAWN tester PROMPT="Investigate regex edge case failures"

CHANGE CONTENT="""// Complete implementation with fixed regex
import { create, MathJsInstance } from 'mathjs';

const math: MathJsInstance = create({});

export class MathJSEngine {
  evaluate(expression: string): number {
    if (/\\b(sin|cos|tan|log|sqrt|exp|abs)\\b/i.test(expression)) {
      throw new Error('Invalid expression');
    }
    return math.evaluate(expression);
  }
}"""
Extended Attempts Without Progress
// After 5 cycles of test-fix-test with no improvement
FINISH PROMPT="After 5 attempts, still failing 8 tests. Issue appears to be architectural - async handling in tests doesn't match sync implementation. Need parent guidance on async requirements."
Task Type Examples
SPEC Task (Empty Interface File)
READ "requirements.md"

CHANGE CONTENT="""/**
 * Calculator service interface
 * @precondition: All numeric inputs must be finite numbers
 * @postcondition: Results are accurate to 10 decimal places
 * @throws {Error} On invalid input or division by zero
 */
export interface ICalculator {
  add(a: number, b: number): number;
  subtract(a: number, b: number): number;
  multiply(a: number, b: number): number;
  divide(a: number, b: number): number;
}

export interface IScientificCalculator extends ICalculator {
  sqrt(value: number): number;
  pow(base: number, exponent: number): number;
}"""

FINISH PROMPT="Calculator interfaces specified with contracts"
SPAWN tester PROMPT="Review interface contracts for completeness"
TEST Task (Empty Test File)
READ "src/calculator.interface.ts"

CHANGE CONTENT="""import { expect } from 'chai';
import { Calculator } from '../src/calculator';

// Test partitions:
// - Normal values: positive, negative, zero
// - Edge cases: MAX_VALUE, MIN_VALUE, Infinity
// - Errors: NaN inputs, null, undefined

describe('Calculator', () => {
  let calc: Calculator;
  
  beforeEach(() => {
    calc = new Calculator();
  });
  
  describe('add()', () => {
    it('should add two positive numbers', () => {
      expect(calc.add(2, 3)).to.equal(5);
    });
    
    it('should handle negative numbers', () => {
      expect(calc.add(-5, 3)).to.equal(-2);
    });
    
    it('should throw on NaN input', () => {
      expect(() => calc.add(NaN, 5)).to.throw('Invalid number input');
    });
  });
});"""

FINISH PROMPT="Calculator tests written covering all partitions"
IMPLEMENT Task (Mixed Approach)
READ "src/calculator.interface.ts"

READ "src/calculator.test.ts"

READ "src/utils/validators.ts"

// Check if we have dependencies
READ "src/utils/math-helpers.ts"  // Empty
SPAWN tester PROMPT="Prototype math helper functions for precision handling"

// Can't proceed without helpers
FINISH PROMPT="Missing dependency: need math helper functions from math-helpers.ts for precision handling"
Key Patterns

Always read context first - Never start without understanding requirements
One test only - After that, use tester agents
REPLACE for existing code - CHANGE only for empty/rewrite
Switch to CHANGE - After REPLACE failures
Check dependencies - Don't implement what belongs elsewhere
Finish when stuck - After ~5 attempts with no progress

YOU CANNOT CHANGE OTHER FILES. NEVER TRY TO CHANGE A FILE BESIDES YOUR OWN. FINISH AND RECOMMEND THIS ACTION.