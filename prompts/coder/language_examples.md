markdown# Coder Language Examples

## Reading Files
READ "README.md"
READ "src/api/userController.ts"
READ "components/Button.tsx"
READ "helpers/checks.py"
READ "config/database.json"

## Changing File Content

### Simple Changes
CHANGE CONTENT = "export const API_VERSION = '2.0';\n"

### Multiline Changes
CHANGE CONTENT = "export function validateEmail(email: string): boolean {\nconst regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\nreturn regex.test(email);\n}"

## Replacing Specific Content

### Version Updates
REPLACE FROM="API_VERSION = '1.0'" TO="API_VERSION = '2.0'"

### Function Name Changes
REPLACE FROM="function calculateTotal" TO="function computeTotal"

### Import Statement Updates
REPLACE FROM="import { oldFunction } from './utils'" TO="import { newFunction } from './utils'"

### Variable Renaming
REPLACE FROM="let userName" TO="let username"

### String Literal Updates
REPLACE FROM="error: 'Invalid input'" TO="error: 'Input validation failed'"

### Type Changes
REPLACE FROM="userId: number" TO="userId: string"

### Method Signature Updates
REPLACE FROM="authenticate(email: string)" TO="authenticate(email: string, password: string)"

### Configuration Changes
REPLACE FROM="timeout: 5000" TO="timeout: 10000"

### Multiline Function Replacement
REPLACE FROM="function validateUser(user) {\nreturn user.email && user.password;\n}" TO="function validateUser(user) {\nif (!user) return false;\nreturn user.email && user.email.includes('@') && user.password && user.password.length >= 8;\n}"

### Complex Expression Updates
REPLACE FROM="const result = data.map(item => {\nreturn item.value * 2;\n});" TO="const result = data.map(item => {\nif (!item || typeof item.value !== 'number') return 0;\nreturn item.value * 2;\n});"

### Interface Definition Updates
REPLACE FROM="interface User {\nid: string;\nname: string;\n}" TO="interface User {\nid: string;\nname: string;\nemail: string;\ncreatedAt: Date;\n}"

### Error Handling Addition
REPLACE FROM="try {\nconst response = await api.call();\nreturn response.data;\n} catch (error) {\nthrow error;\n}" TO="try {\nconst response = await api.call();\nif (!response || !response.data) {\nthrow new Error('Invalid API response');\n}\nreturn response.data;\n} catch (error) {\nconsole.error('API call failed:', error.message);\nthrow new Error(`API Error: ${error.message}`);\n}"

### Class Method Replacement
REPLACE FROM="public authenticate(credentials: LoginData): boolean {\nreturn this.users.has(credentials.username);\n}" TO="public authenticate(credentials: LoginData): boolean {\nif (!credentials || !credentials.username || !credentials.password) {\nreturn false;\n}\nconst user = this.users.get(credentials.username);\nreturn user && user.password === credentials.password;\n}"

### Import Block Updates
REPLACE FROM="import { Component } from 'react';\nimport { Props } from './types';" TO="import React, { Component, useState, useEffect } from 'react';\nimport { Props, State } from './types';\nimport { validateProps } from './utils';"

### Regular Expression with Escaping
REPLACE FROM="const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;" TO="const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$/;"

### Template String Updates (Simple)
REPLACE FROM="const message = `Hello ${name}, welcome!`;" TO="const message = `Hello ${name || 'Guest'}, welcome to our application!`;"

### Template String with Literal Newline Characters
// Note: \\n creates actual newline character in string output  
REPLACE FROM="const message = `Welcome ${name}`;" TO="const message = `Welcome ${name}\\nPlease check your email.`;"

### Escaping Clarification Examples
// \n = line break in code (structural)
REPLACE FROM="if (user) {\nreturn user.name;\n}" TO="if (user && user.active) {\nreturn user.name;\n}"

// \\n = literal newline character in string (rare)
REPLACE FROM="console.log('Hello');" TO="console.log('Hello\\nWorld');"

## Running Commands

### Compilation Only
RUN "node tools/compile-typescript.js"
RUN "node tools/check-typescript.js"

## Testing via Tester Agents

### Specific File Testing
SPAWN tester PROMPT="Test calculator.ts implementation against test suite"
WAIT

### Broad Testing (for understanding overall status)
SPAWN tester PROMPT="Test all authentication module files"
WAIT

### Debug Specific Failing Tests
SPAWN tester PROMPT="Debug why login tests are failing - investigate auth.ts and login.test.ts"
WAIT

## Complete Workflows

### API Endpoint Implementation
// FIRST: Read context files as instructed by parent
READ "test/userController.test.ts"
READ "src/user.interface.ts"
// THEN: Implement based on context
CHANGE CONTENT = "export async function getUser(id: string): Promise<User> {\nif (!id || !id.match(/^[a-f0-9]{24}$/)) {\nthrow new Error('Invalid user ID format');\n}\nconst user = await db.users.findById(id);\nif (!user) throw new Error('User not found');\nreturn user;\n}"
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Test getUser endpoint implementation"
WAIT
FINISH PROMPT = "User endpoint implemented with validation"

### React Component Development  
// FIRST: Read all context files specified by parent
READ "test/Button.test.tsx"
READ "components/ButtonInterface.ts"
// THEN: Implement based on learned requirements
CHANGE CONTENT = "import React from 'react';\nimport { ButtonProps } from './ButtonInterface';\nexport const Button: React.FC<ButtonProps> = ({\nlabel,\nonClick,\ndisabled = false,\nvariant = 'primary'\n}) => {\nconst className = \`btn btn-\\${variant} \\${disabled ? 'disabled' : ''}\`;\nreturn (\n<button \nclassName={className}\nonClick={onClick}\ndisabled={disabled}\n>\n{label}\n</button>\n);\n};"
SPAWN tester PROMPT="Test Button component against all test cases"
WAIT
FINISH PROMPT = "Button component implemented with all props"

### Iterative Bug Fixes with REPLACE
// FIRST: Read context files as instructed by parent  
READ "test/calculator.test.ts"
READ "src/calculator.interface.ts"
// THEN: Begin implementation and testing cycle
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Test calculator implementation"
WAIT
// Tester reports: division by zero not handled
REPLACE FROM="return a / b;" TO="if (b === 0) throw new Error('Division by zero'); return a / b;"
SPAWN tester PROMPT="Retest calculator after division fix"
WAIT
// Tester reports: negative number handling needed
REPLACE FROM="Math.sqrt(value)" TO="if (value < 0) throw new Error('Cannot compute square root of negative number'); return Math.sqrt(value)"
SPAWN tester PROMPT="Final calculator test"
WAIT
FINISH PROMPT = "Calculator implementation completed with error handling"

### Multiple Parallel Investigations
READ "test/userSystem.test.ts"
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Debug authentication failures in user system"
SPAWN tester PROMPT="Debug validation errors in user input processing"
SPAWN tester PROMPT="Debug database connection issues in user persistence"
WAIT
// Each tester reports findings for their specific domain
// Make targeted fixes based on each tester's recommendations
FINISH PROMPT = "User system issues resolved using parallel tester analysis: auth, validation, and database problems fixed independently"

### API Endpoint Refinement
READ "test/userAPI.test.ts"
READ "src/userAPI.ts"
SPAWN tester PROMPT="Test user API endpoints"
WAIT
// Fix validation based on test feedback
REPLACE FROM="if (!email)" TO="if (!email || !email.includes('@'))"
REPLACE FROM="status: 'success'" TO="status: 'created'"
REPLACE FROM="res.status(400)" TO="res.status(422)"
SPAWN tester PROMPT="Retest user API after validation fixes"
WAIT
FINISH PROMPT = "User API endpoints updated with proper validation and status codes"

### Multiline Error Handling Refinement
READ "test/database.test.ts"
READ "src/database.ts"
SPAWN tester PROMPT="Test database connection handling"
WAIT
// Tester reports: need better error handling for connection failures
REPLACE FROM="async connect() {\nthis.connection = await createConnection();\nreturn this.connection;\n}" TO="async connect() {\ntry {\nthis.connection = await createConnection();\nif (!this.connection) {\nthrow new Error('Connection failed to establish');\n}\nreturn this.connection;\n} catch (error) {\nconsole.error('Database connection error:', error.message);\nthrow new Error(`Failed to connect to database: ${error.message}`);\n}\n}"
SPAWN tester PROMPT="Retest database connection with improved error handling"
WAIT
FINISH PROMPT = "Database connection updated with comprehensive error handling and logging"

### Implementation with Test-Driven Iteration
READ "test/auth.test.ts"
READ "src/middleware/auth.ts"
CHANGE CONTENT = "// Initial implementation attempt..."
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Test auth middleware implementation"
WAIT
// Based on tester feedback, make fixes
CHANGE CONTENT = "// Fixed implementation based on test results..."
SPAWN tester PROMPT="Retest auth middleware after fixes"
WAIT
FINISH PROMPT = "Auth middleware implemented and all tests passing"

## Task Types

### SPEC Task (Interface File Agent)
READ "existing-api.md"
CHANGE CONTENT = "/**\n * User authentication interface\n * @precondition: email must be unique and valid format\n * @postcondition: password is hashed before storage\n * @invariant: createdAt <= updatedAt\n */\nexport interface IUser {\nid: string;\nemail: string;\npassword: string;  // bcrypt hashed\nrole: 'user' | 'admin';\ncreatedAt: Date;\nupdatedAt: Date;\n}\n\nexport interface IUserService {\nauthenticate(email: string, password: string): Promise<IUser | null>;\ncreateUser(userData: Omit<IUser, 'id' | 'createdAt' | 'updatedAt'>): Promise<IUser>;\n}"
FINISH PROMPT = "User interface specification complete with authentication contracts"

### TEST Task (Test File Agent)
READ "user.interface.ts"
CHANGE CONTENT = "import { IUser, IUserService } from '../src/user.interface';\nimport { expect } from 'chai';\n\n// Test partitions:\n// - Valid emails: standard, with dots, with plus\n// - Invalid emails: no @, no domain, spaces\n// - Edge cases: empty string, null, very long\ndescribe('User Authentication', () => {\ndescribe('authenticate()', () => {\nit('should return user for valid credentials', async () => {\n// Test implementation here\n});\nit('should return null for invalid password', async () => {\n// Test implementation here\n});\n// More partition tests...\n});\n});"
FINISH PROMPT = "User authentication tests covering all interface contracts"

### IMPLEMENT Task (Implementation File Agent)
READ "test/user.test.ts"
READ "user.interface.ts"
CHANGE CONTENT = "import { IUser, IUserService } from './user.interface';\nimport bcrypt from 'bcrypt';\n\nexport class UserService implements IUserService {\nasync authenticate(email: string, password: string): Promise<IUser | null> {\nif (!email || !password) return null;\nconst user = await this.findUserByEmail(email);\nif (!user) return null;\nconst isValid = await bcrypt.compare(password, user.password);\nreturn isValid ? user : null;\n}\n\nasync createUser(userData: Omit<IUser, 'id' | 'createdAt' | 'updatedAt'>): Promise<IUser> {\nconst hashedPassword = await bcrypt.hash(userData.password, 10);\nreturn {\nid: generateId(),\n...userData,\npassword: hashedPassword,\ncreatedAt: new Date(),\nupdatedAt: new Date()\n};\n}\n}"
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Test UserService implementation against test suite"
WAIT
FINISH PROMPT = "UserService implemented with all interface contracts and tests passing"

### Error Handling & Loop Prevention Examples

#### Compilation Error Analysis (CRITICAL - prevents loops)
READ "test/calculator.test.ts"
CHANGE CONTENT = "// Initial implementation attempt using validateInput function..."
RUN "node tools/compile-typescript.js"
// Compilation fails: 'validateInput' is not defined
SPAWN tester PROMPT="Analyze compilation errors in calculator.ts - identify missing validateInput function source"
WAIT
// Tester reports: validateInput should come from helpers.ts module
FINISH PROMPT = "Missing dependency: need `validateInput` function from helpers.ts module. Cannot proceed without this utility function."

#### Recognizing Missing Dependencies Early
READ "test/calculator.test.ts"
READ "moduleA.ts"  // File exists but is empty
READ "moduleB.ts"  // File exists but is empty  
FINISH PROMPT = "Cannot implement calculator without dependencies. Need separate modules for core functionality before proceeding."

#### TypeScript Error Investigation
CHANGE CONTENT = "// Implementation with imports..."
RUN "node tools/check-typescript.js"
// Multiple import errors
SPAWN tester PROMPT="Debug TypeScript errors - determine if missing functions should be implemented here or elsewhere"
WAIT
// Tester identifies dependency pattern
FINISH PROMPT = "Missing dependencies identified: parser functions belong in separate parser.ts module, not in this utility file."

#### Avoiding the Compile-Fix Loop
CHANGE CONTENT = "// First attempt at implementation..."
RUN "node tools/compile-typescript.js" 
// Compilation fails
CHANGE CONTENT = "// Second attempt with fixes..."
RUN "node tools/compile-typescript.js"
// Still failing - missing complex functions
SPAWN tester PROMPT="Analyze compilation errors - check if large missing functions belong in other modules"
WAIT
FINISH PROMPT = "Dependency analysis shows AST traversal functions should be in separate ast.ts module. Need 200+ lines of parser logic that doesn't belong in this file."

#### Using Tester Agent for Complex Debugging
// After initial implementation
CHANGE CONTENT = "// Fixed auth implementation..."
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Debug authentication failures - investigate token validation logic"
WAIT
// Use tester's findings for next attempt
CHANGE CONTENT = "// Revised implementation based on tester analysis..."
SPAWN tester PROMPT="Retest authentication after token validation fix"
WAIT

#### REPLACE vs CHANGE Decision Making
// For small targeted fixes, use REPLACE
READ "src/utils.ts"
SPAWN tester PROMPT="Test utility functions"
WAIT
// Tester reports specific function issue
REPLACE FROM="return value.toString()" TO="return value?.toString() ?? ''"
SPAWN tester PROMPT="Retest utilities after null safety fix"
WAIT

// For major restructuring, use CHANGE
READ "src/legacy-component.ts"
SPAWN tester PROMPT="Test legacy component"
WAIT
// Tester reports: entire approach needs rewriting
CHANGE CONTENT = "// Complete new implementation..."
SPAWN tester PROMPT="Test rewritten component"
WAIT

#### REPLACE Error Handling
READ "src/config.ts"
REPLACE FROM="DATABASE_URL = 'localhost'" TO="DATABASE_URL = process.env.DB_URL || 'localhost'"
// If string not found, agent will be reprompted with error
// Use READ to verify current content before attempting REPLACE again

### Reporting Test Issues Based on Tester Feedback
READ "test/formatter.test.ts"
READ "src/formatter.ts"
SPAWN tester PROMPT="Test formatter implementation and identify any issues"
WAIT
FINISH PROMPT = "Test issue identified by tester: expects trimmed output but implementation preserves whitespace. Spec unclear - need clarification on whitespace handling"

## Key Rules
- One command per line
- Always compile before spawning testers for TypeScript
- READ context before CHANGE or REPLACE
- **REPLACE vs CHANGE**: Use REPLACE for small targeted fixes (single line changes, variable renames, imports). Use CHANGE for major restructuring or new implementations
- **REPLACE safety**: If REPLACE fails with "string not found", READ the file first to verify current content
- **Multiline REPLACE**: Use `\n` for code line breaks, `\"` for quotes, `\\` for literal backslashes. Ensure exact whitespace matching
- **REPLACE precision**: For multiline REPLACE, include exact indentation and spacing from the original code to ensure successful matching
- **Escaping rules**: 
  - `\n` = line break in code structure (most common)
  - `\\n` = literal newline character within string values (rare)
  - `\\` = literal backslash character (for regex, paths, etc.)
- Use SPAWN tester for ALL testing needs AND compilation error analysis
- WAIT after spawning testers
- FINISH with clear explanation based on tester findings
- **NEVER get stuck in compile-fix loops** - use tester agents and dependency requests instead
- **Maximum 3 compilation attempts** - after that, spawn tester or FINISH with dependency request
- **Ask "Should I implement this function or request it?"** before writing complex logic