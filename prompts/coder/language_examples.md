# Coder Language Examples

## ⚠️ CRITICAL: REPLACE vs CHANGE Decision Framework

**Use REPLACE when code already exists in your file (PREFERRED - 90% of cases):**
- File has existing implementation that needs targeted fixes
- Adding new functions to existing code
- Updating imports, variable names, or method signatures
- Fixing bugs in specific functions
- Adding error handling to existing code
- **Rule**: If you can identify specific strings to replace, use REPLACE

**Use CHANGE when (RARE - 10% of cases):**
- File is completely empty and needs initial implementation
- Complete rewrite/restructuring of entire file is needed
- Switching to entirely different implementation approach
- **Rule**: Only when REPLACE cannot accomplish the task

## Reading Files
READ "README.md"
READ "src/api/userController.ts"
READ "components/Button.tsx"
READ "helpers/checks.py"
READ "config/database.json"

## CHANGE Examples (Complete File Replacement - Use Sparingly)

### Initial Implementation (Empty File)
CHANGE CONTENT = "export const API_VERSION = '2.0';\n"

### Complete File Rewrite (When REPLACE Cannot Work)
CHANGE CONTENT = "export function validateEmail(email: string): boolean {\nconst regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\nreturn regex.test(email);\n}"

### Entire File Restructure (Rare Case)
CHANGE CONTENT = "// Complete rewrite from class-based to functional approach\nimport React, { useState } from 'react';\n\nexport const UserManager: React.FC = () => {\n  const [users, setUsers] = useState([]);\n  \n  const addUser = (user: User) => {\n    setUsers(prev => [...prev, user]);\n  };\n  \n  return (\n    <div>\n      {users.map(user => <UserCard key={user.id} user={user} />)}\n    </div>\n  );\n};\n"

## REPLACE Examples (Targeted Fixes When Code Exists - Use These Most Often)

### Version Updates (Existing Configuration)
REPLACE FROM = "API_VERSION = '1.0'" TO = "API_VERSION = '2.0'"

### Function Name Changes (Existing Functions)
REPLACE FROM = "function calculateTotal" TO = "function computeTotal"

### Import Statement Updates (Existing Imports)
REPLACE FROM = "import { oldFunction } from './utils'" TO = "import { newFunction } from './utils'"

### Variable Renaming (Existing Variables)
REPLACE FROM = "let userName" TO = "let username"

### String Literal Updates (Existing Strings)
REPLACE FROM = "error: 'Invalid input'" TO = "error: 'Input validation failed'"

### Type Changes (Existing Type Definitions)
REPLACE FROM = "userId: number" TO = "userId: string"

### Method Signature Updates (Existing Methods)
REPLACE FROM = "authenticate(email: string)" TO = "authenticate(email: string, password: string)"

### Configuration Changes (Existing Config)
REPLACE FROM = "timeout: 5000" TO = "timeout: 10000"

### Multiline Function Replacement (Existing Function Body)
REPLACE FROM = "function validateUser(user) {\nreturn user.email && user.password;\n}" TO = "function validateUser(user) {\nif (!user) return false;\nreturn user.email && user.email.includes('@') && user.password && user.password.length >= 8;\n}"

### Complex Expression Updates (Existing Code Block)
REPLACE FROM = "const result = data.map(item => {\nreturn item.value * 2;\n});" TO = "const result = data.map(item => {\nif (!item || typeof item.value !== 'number') return 0;\nreturn item.value * 2;\n});"

### Interface Definition Updates (Existing Interface)
REPLACE FROM = "interface User {\nid: string;\nname: string;\n}" TO = "interface User {\nid: string;\nname: string;\nemail: string;\ncreatedAt: Date;\n}"

### Error Handling Addition (Existing Try-Catch)
REPLACE FROM="try {\nconst response = await api.call();\nreturn response.data;\n} catch (error) {\nthrow error;\n}" TO="try {\nconst response = await api.call();\nif (!response || !response.data) {\nthrow new Error('Invalid API response');\n}\nreturn response.data;\n} catch (error) {\nconsole.error('API call failed:', error.message);\nthrow new Error(`API Error: ${error.message}`);\n}"

### Class Method Replacement (Existing Method)
REPLACE FROM="public authenticate(credentials: LoginData): boolean {\nreturn this.users.has(credentials.username);\n}" TO="public authenticate(credentials: LoginData): boolean {\nif (!credentials || !credentials.username || !credentials.password) {\nreturn false;\n}\nconst user = this.users.get(credentials.username);\nreturn user && user.password === credentials.password;\n}"

### Import Block Updates (Existing Imports)
REPLACE FROM="import { Component } from 'react';\nimport { Props } from './types';" TO="import React, { Component, useState, useEffect } from 'react';\nimport { Props, State } from './types';\nimport { validateProps } from './utils';"

### Regular Expression with Escaping (Existing Regex)
REPLACE FROM="const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;" TO="const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$/;"

### Template String Updates (Existing Template)
REPLACE FROM="const message = `Hello ${name}, welcome!`;" TO="const message = `Hello ${name || 'Guest'}, welcome to our application!`;"

### Template String with Literal Newline Characters (Existing Template)
// Note: \\n creates actual newline character in string output  
REPLACE FROM = "const message = `Welcome ${name}`;" TO = "const message = `Welcome ${name}\\nPlease check your email.`;"

### Escaping Clarification Examples
// \n = line break in code (structural)
REPLACE FROM = "if (user) {\nreturn user.name;\n}" TO = "if (user && user.active) {\nreturn user.name;\n}"

// \\n = literal newline character in string (rare)
REPLACE FROM = "console.log('Hello');" TO = "console.log('Hello\\nWorld');"

### Code Deletion Examples (Replace with Empty String - Existing Code)
REPLACE FROM="console.log('Debug: user data', userData);\n" TO=""
REPLACE FROM="import { unusedFunction } from './helpers';\n" TO=""
REPLACE FROM="function deprecatedHelper(input: string): string {\nreturn input.toUpperCase();\n}\n\n" TO=""
REPLACE FROM="// TODO: Remove this old implementation\n// function oldCalculate(a, b) {\n//   return a + b;\n// }\n" TO=""

## Multiple Replace Operations (Batch Updates)

### Multiple Related Variables
REPLACE FROM="let userName" TO="let username", FROM="let userEmail" TO="let email", FROM="let userAge" TO="let age"

### Multiple Configuration Values
REPLACE FROM="timeout: 5000" TO="timeout: 10000", FROM="retries: 3" TO="retries: 5", FROM="debug: false" TO="debug: true"

### Multiple Import Updates
REPLACE FROM="import { oldFunction }" TO="import { newFunction }", FROM="'./old-path'" TO="'./new-path'"

### Multiple API Endpoints
REPLACE FROM="'/api/v1/users'" TO="'/api/v2/users'", FROM="'/api/v1/posts'" TO="'/api/v2/posts'"

### Multiple Error Messages
REPLACE FROM="'Invalid input'" TO="'Input validation failed'", FROM="'User not found'" TO="'User does not exist'"

## Running Commands

### Compilation Only
RUN "node tools/compile-typescript.js"
RUN "node tools/check-typescript.js"

### Direct Test (Allowed ONCE per task)
RUN "node tools/run-mocha.js"
RUN "python -m pytest"

## Testing via Tester Agents (After First Direct Test)

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

### API Endpoint Implementation (Starting with Existing Code)
// FIRST: Read context files as instructed by parent
READ "test/userController.test.ts"
READ "src/user.interface.ts"
// File already has basic structure - use REPLACE for targeted improvements
REPLACE FROM="export async function getUser(id: string): Promise<User> {\nreturn db.users.findById(id);\n}" TO="export async function getUser(id: string): Promise<User> {\nif (!id || !id.match(/^[a-f0-9]{24}$/)) {\nthrow new Error('Invalid user ID format');\n}\nconst user = await db.users.findById(id);\nif (!user) throw new Error('User not found');\nreturn user;\n}"
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Test getUser endpoint implementation"
WAIT
FINISH PROMPT = "User endpoint enhanced with validation"

### React Component Development (Empty File - Use CHANGE)
// FIRST: Read all context files specified by parent
READ "test/Button.test.tsx"
READ "components/ButtonInterface.ts"
// File is empty - use CHANGE for initial implementation
CHANGE CONTENT = "import React from 'react';\nimport { ButtonProps } from './ButtonInterface';\nexport const Button: React.FC<ButtonProps> = ({\nlabel,\nonClick,\ndisabled = false,\nvariant = 'primary'\n}) => {\nconst className = \`btn btn-\\${variant} \\${disabled ? 'disabled' : ''}\`;\nreturn (\n<button \nclassName={className}\nonClick={onClick}\ndisabled={disabled}\n>\n{label}\n</button>\n);\n};"
SPAWN tester PROMPT="Test Button component against all test cases"
WAIT
FINISH PROMPT = "Button component implemented with all props"

### Iterative Bug Fixes with REPLACE (Existing Implementation)
// FIRST: Read context files as instructed by parent  
READ "test/calculator.test.ts"
READ "src/calculator.interface.ts"
// File already has implementation - use REPLACE for specific fixes
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
// Make targeted fixes based on each tester's recommendations using REPLACE
FINISH PROMPT = "User system issues resolved using parallel tester analysis: auth, validation, and database problems fixed independently"

### API Endpoint Refinement (Existing Code)
READ "test/userAPI.test.ts"
READ "src/userAPI.ts"
SPAWN tester PROMPT="Test user API endpoints"
WAIT
// Fix validation based on test feedback - file already exists, use REPLACE
REPLACE FROM="if (!email)" TO="if (!email || !email.includes('@'))"
REPLACE FROM="status: 'success'" TO="status: 'created'"
REPLACE FROM="res.status(400)" TO="res.status(422)"
SPAWN tester PROMPT="Retest user API after validation fixes"
WAIT
FINISH PROMPT = "User API endpoints updated with proper validation and status codes"

### Multiline Error Handling Refinement (Existing Function)
READ "test/database.test.ts"
READ "src/database.ts"
SPAWN tester PROMPT="Test database connection handling"
WAIT
// Tester reports: need better error handling for connection failures
// File has existing function - use REPLACE for enhancement
REPLACE FROM="async connect() {\nthis.connection = await createConnection();\nreturn this.connection;\n}" TO="async connect() {\ntry {\nthis.connection = await createConnection();\nif (!this.connection) {\nthrow new Error('Connection failed to establish');\n}\nreturn this.connection;\n} catch (error) {\nconsole.error('Database connection error:', error.message);\nthrow new Error(`Failed to connect to database: ${error.message}`);\n}\n}"
SPAWN tester PROMPT="Retest database connection with improved error handling"
WAIT
FINISH PROMPT = "Database connection updated with comprehensive error handling and logging"

### Implementation with Test-Driven Iteration (Mixed Approach)
READ "test/auth.test.ts"
READ "src/middleware/auth.ts"
// If file is empty - use CHANGE for initial implementation
CHANGE CONTENT = "// Initial auth middleware implementation\nimport jwt from 'jsonwebtoken';\n\nexport function authMiddleware(req, res, next) {\n  const token = req.headers.authorization;\n  if (!token) {\n    return res.status(401).json({ error: 'No token provided' });\n  }\n  // Basic structure - needs enhancement\n  next();\n}\n"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"  // Direct test (allowed ONCE)
// If tests fail, try ONE fix using REPLACE (code now exists), then:
SPAWN tester PROMPT="Test auth middleware implementation"
WAIT
// Based on tester feedback, make fixes using REPLACE (targeted improvements)
REPLACE FROM="const token = req.headers.authorization;" TO="const token = req.headers.authorization?.split(' ')[1];"
REPLACE FROM="// Basic structure - needs enhancement\n  next();" TO="try {\n    const decoded = jwt.verify(token, process.env.JWT_SECRET);\n    req.user = decoded;\n    next();\n  } catch (error) {\n    return res.status(401).json({ error: 'Invalid token' });\n  }"
SPAWN tester PROMPT="Retest auth middleware after fixes"
WAIT
FINISH PROMPT = "Auth middleware implemented and all tests passing"

## Task Types

### SPEC Task (Interface File Agent - Usually Empty File)
READ "existing-api.md"
// Interface files are often empty initially - use CHANGE
CHANGE CONTENT = "/**\n * User authentication interface\n * @precondition: email must be unique and valid format\n * @postcondition: password is hashed before storage\n * @invariant: createdAt <= updatedAt\n */\nexport interface IUser {\nid: string;\nemail: string;\npassword: string;  // bcrypt hashed\nrole: 'user' | 'admin';\ncreatedAt: Date;\nupdatedAt: Date;\n}\n\nexport interface IUserService {\nauthenticate(email: string, password: string): Promise<IUser | null>;\ncreateUser(userData: Omit<IUser, 'id' | 'createdAt' | 'updatedAt'>): Promise<IUser>;\n}"
FINISH PROMPT = "User interface specification complete with authentication contracts"

### TEST Task (Test File Agent - Usually Empty File)
READ "user.interface.ts"
// Test files are often empty initially - use CHANGE
CHANGE CONTENT = "import { IUser, IUserService } from '../src/user.interface';\nimport { expect } from 'chai';\n\n// Test partitions:\n// - Valid emails: standard, with dots, with plus\n// - Invalid emails: no @, no domain, spaces\n// - Edge cases: empty string, null, very long\ndescribe('User Authentication', () => {\ndescribe('authenticate()', () => {\nit('should return user for valid credentials', async () => {\n// Test implementation here\n});\nit('should return null for invalid password', async () => {\n// Test implementation here\n});\n// More partition tests...\n});\n});"
FINISH PROMPT = "User authentication tests covering all interface contracts"

### IMPLEMENT Task (Implementation File Agent - Mixed Approach)
READ "test/user.test.ts"
READ "user.interface.ts"
// Check if file has existing implementation
READ "src/user.ts"
// If file is empty - use CHANGE for initial implementation
CHANGE CONTENT = "import { IUser, IUserService } from './user.interface';\nimport bcrypt from 'bcrypt';\n\nexport class UserService implements IUserService {\nasync authenticate(email: string, password: string): Promise<IUser | null> {\nif (!email || !password) return null;\nconst user = await this.findUserByEmail(email);\nif (!user) return null;\nconst isValid = await bcrypt.compare(password, user.password);\nreturn isValid ? user : null;\n}\n\nasync createUser(userData: Omit<IUser, 'id' | 'createdAt' | 'updatedAt'>): Promise<IUser> {\nconst hashedPassword = await bcrypt.hash(userData.password, 10);\nreturn {\nid: generateId(),\n...userData,\npassword: hashedPassword,\ncreatedAt: new Date(),\nupdatedAt: new Date()\n};\n}\n}"
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Test UserService implementation against test suite"
WAIT
// If tests fail, use REPLACE for targeted fixes (code now exists)
REPLACE FROM="if (!email || !password) return null;" TO="if (!email || !password || !email.includes('@')) return null;"
SPAWN tester PROMPT="Retest UserService after validation enhancement"
WAIT
FINISH PROMPT = "UserService implemented with all interface contracts and tests passing"

### Error Handling & Loop Prevention Examples

#### Compilation Error Analysis (CRITICAL - prevents loops)
READ "test/calculator.test.ts"
// Try initial implementation - file is empty, use CHANGE
CHANGE CONTENT = "// Initial implementation using validateInput function\nimport { validateInput } from './helpers';\n\nexport class Calculator {\n  add(a: number, b: number): number {\n    validateInput(a, b);\n    return a + b;\n  }\n}"
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

#### TypeScript Error Investigation (Existing Code)
// File already has some implementation - use REPLACE for fixes
REPLACE FROM="import { parseData } from './parser';" TO="import { parseData, validateData } from './parser';"
RUN "node tools/check-typescript.js"
// Multiple import errors
SPAWN tester PROMPT="Debug TypeScript errors - determine if missing functions should be implemented here or elsewhere"
WAIT
// Tester identifies dependency pattern
FINISH PROMPT = "Missing dependencies identified: parser functions belong in separate parser.ts module, not in this utility file."

#### Avoiding the Compile-Fix Loop (Mixed Approach)
// First attempt - file is empty, use CHANGE
CHANGE CONTENT = "// First attempt at implementation\nimport { complexFunction } from './utils';\n\nexport function mainLogic() {\n  return complexFunction();\n}"
RUN "node tools/compile-typescript.js" 
// Compilation fails
// Second attempt - code exists now, use REPLACE for fixes
REPLACE FROM="import { complexFunction } from './utils';" TO="import { complexFunction, helperFunction } from './utils';"
RUN "node tools/compile-typescript.js"
// Still failing - missing complex functions
SPAWN tester PROMPT="Analyze compilation errors - check if large missing functions belong in other modules"
WAIT
FINISH PROMPT = "Dependency analysis shows AST traversal functions should be in separate ast.ts module. Need 200+ lines of parser logic that doesn't belong in this file."

#### Using Tester Agent for Complex Debugging (Existing Code)
// After initial implementation - code exists, use REPLACE for fixes
REPLACE FROM="// Fixed auth implementation..." TO="// Revised auth with better token handling..."
RUN "node tools/compile-typescript.js"
SPAWN tester PROMPT="Debug authentication failures - investigate token validation logic"
WAIT
// Use tester's findings for next attempt - code exists, use REPLACE
REPLACE FROM="const token = req.headers.authorization;" TO="const token = req.headers.authorization?.replace('Bearer ', '');"
SPAWN tester PROMPT="Retest authentication after token validation fix"
WAIT

#### REPLACE vs CHANGE Decision Making Examples
// For small targeted fixes, use REPLACE (existing code)
READ "src/utils.ts"
SPAWN tester PROMPT="Test utility functions"
WAIT
// Tester reports specific function issue - code exists, use REPLACE
REPLACE FROM="return value.toString()" TO="return value?.toString() ?? ''"
SPAWN tester PROMPT="Retest utilities after null safety fix"
WAIT

// For major restructuring, use CHANGE (complete rewrite needed)
READ "src/legacy-component.ts"
SPAWN tester PROMPT="Test legacy component"
WAIT
// Tester reports: entire approach needs rewriting - use CHANGE for complete rewrite
CHANGE CONTENT = "// Complete new functional approach\nimport React, { useState, useEffect } from 'react';\n\nexport const ModernComponent: React.FC = () => {\n  const [state, setState] = useState(initialState);\n  \n  useEffect(() => {\n    // Modern lifecycle logic\n  }, []);\n  \n  return <div>Modern implementation</div>;\n};"
SPAWN tester PROMPT="Test rewritten component"
WAIT

#### REPLACE Error Handling (Existing Code)
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
- **REPLACE vs CHANGE**: Use REPLACE for targeted fixes when code already exists (90%). Use CHANGE only for empty files or complete rewrites (10%)
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