# Manager Language Examples

## Core Commands

### Reading Files & Folders
```
READ file "src/README.md"

READ file "src/calculator.ts", file "src/types.ts"

READ folder "src"  // Loads src/src_README.md
```

### Creating/Deleting
```
CREATE file "src/parser.interface.ts"

CREATE folder "src/utils"

DELETE file "src/old-config.json"

DELETE folder "src/deprecated"
```

### Delegation to Direct Children
```
DELEGATE file "src/calculator.interface.ts" PROMPT="SPEC: Define Calculator interface with add, subtract, multiply, divide methods"

DELEGATE file "src/calculator.test.ts" PROMPT="TEST: Read calculator.interface.ts first. Write comprehensive test suite"

DELEGATE file "src/calculator.ts" PROMPT="IMPLEMENT: Read calculator.interface.ts and calculator.test.ts. Build Calculator class to pass all tests"

DELEGATE folder "src/services" PROMPT="Implement all service layer components with full test coverage"
```

### Running Commands
```
RUN "npm test"

RUN "python -m pytest"

RUN "mvn test"
```

### Spawning Tester Agents
```
SPAWN tester PROMPT="Test calculator.ts implementation"

SPAWN tester PROMPT="Debug failing tests in auth module"

SPAWN tester PROMPT="Verify all files in src/ folder compile and pass tests"
```

### README Updates (3-Status System)
```
UPDATE_README CONTENT="# Parser Module\n\nThis folder contains the recursive descent parser for our language including tokenization and AST generation.\n\n## Files\n- parser.interface.ts - [FINISHED] Parser contract with parse methods\n- parser.test.ts - [FINISHED] 25 test cases covering all grammar rules\n- parser.ts - [BEGUN] Recursive descent parser implementation\n- ast.ts - [NOT STARTED] AST node definitions\n- errors.ts - [FINISHED] Custom parsing error types\n\n## Subdirectories\n- utils/ - [FINISHED] Helper functions for parsing\n- visitors/ - [NOT STARTED] AST visitor pattern implementations"
```

### Finishing
```
FINISH PROMPT="Parser module complete with 100% test coverage"

FINISH PROMPT="Authentication blocked: needs TokenService from ../shared/ outside my scope"
```

### Using WAIT
```
// ONLY needed when multiple children active via comma-separated delegation
DELEGATE file "src/parser.ts" PROMPT="IMPLEMENT: Build parser", file "src/lexer.ts" PROMPT="IMPLEMENT: Build lexer"
// Both are now active
// Later, parser.ts finishes but lexer.ts still active
WAIT  // Cannot FINISH while lexer.ts still working
```

## Common Workflows

### Test-First Development
```
// 1. Spec phase
CREATE file "src/auth.interface.ts"

DELEGATE file "src/auth.interface.ts" PROMPT="SPEC: Define authentication interface with login, logout, refresh methods"

// 2. Test phase  
CREATE file "src/auth.test.ts"

DELEGATE file "src/auth.test.ts" PROMPT="TEST: Read auth.interface.ts. Write tests for all methods including edge cases"

// 3. Implementation phase
CREATE file "src/auth.ts"

DELEGATE file "src/auth.ts" PROMPT="IMPLEMENT: Read auth.interface.ts and auth.test.ts. Build AuthService to pass all tests"

// 4. Verification
SPAWN tester PROMPT="Test auth.ts implementation"

UPDATE_README CONTENT="# Authentication Service\n\nHandles user authentication, session management, and token operations.\n\n## Files\n- auth.interface.ts - [FINISHED] Auth service interface\n- auth.test.ts - [FINISHED] Full test coverage\n- auth.ts - [FINISHED] Auth service implementation"
FINISH PROMPT="Authentication implemented with full coverage"
```

### Concurrent Delegation (Single Command)
```
// Delegate multiple independent tasks in one command
DELEGATE file "src/user.ts" PROMPT="IMPLEMENT: Read user.interface.ts and user.test.ts. Build User class", file "src/role.ts" PROMPT="IMPLEMENT: Read role.interface.ts and role.test.ts. Build Role class", file "src/permission.ts" PROMPT="IMPLEMENT: Read permission.interface.ts and permission.test.ts. Build Permission class"

// If user.ts finishes first but others still active
WAIT  // Must wait for all to complete

// Once all finish
UPDATE_README CONTENT="# Access Control Module\n\nImplements user roles and permissions for the application.\n\n## Files\n- user.ts - [FINISHED] User model with authentication\n- role.ts - [FINISHED] Role definitions and hierarchy\n- permission.ts - [FINISHED] Permission checking logic"
FINISH PROMPT="All access control components complete"
```

### Multiple Tester Spawns
```
// Spawn multiple testers for different aspects
SPAWN tester PROMPT="Test parser.ts functionality", tester PROMPT="Test lexer.ts functionality", tester PROMPT="Verify parser-lexer integration"
WAIT  // Wait for all tester results
```

### Child Verification Pattern
```
// Child reports: "Cannot implement due to missing dependencies"
READ file "src/module.ts"  // Always verify actual state

// If file has implementation despite "failure"
SPAWN tester PROMPT="Test module.ts - verify what actually works"

// If file truly empty
DELEGATE file "src/dependency.ts" PROMPT="IMPLEMENT: Build required dependency first"
```

### Handling Child Hallucinations
```
// Child claims: "Tests implemented successfully"
READ file "src/module.test.ts"  

// If file empty or just boilerplate
DELEGATE file "src/module.test.ts" PROMPT="TEST: Actually implement comprehensive test suite"

// Child claims: "Cannot proceed, human intervention required"
READ file "src/problem.ts"

SPAWN tester PROMPT="Debug problem.ts - find workaround for claimed blocker"
```

### Multiple File Operations
```
// Create multiple files at once
CREATE file "src/auth.interface.ts", file "src/auth.test.ts", file "src/auth.ts"

// Read multiple files
READ file "src/user.ts", file "src/role.ts", file "src/permission.ts"

// Delete multiple items
DELETE file "src/old-auth.ts", folder "src/deprecated-auth"
```

### Progressive README Updates
```
// Initial state
UPDATE_README CONTENT="# Calculator Module\n\nImplements arithmetic operations for the application.\n\n## Files\n- calculator.interface.ts - [NOT STARTED] Interface definitions\n- calculator.test.ts - [NOT STARTED] Test suite\n- calculator.ts - [NOT STARTED] Implementation"

// After spec completion
UPDATE_README CONTENT="# Calculator Module\n\nImplements arithmetic operations for the application.\n\n## Files\n- calculator.interface.ts - [FINISHED] Interface with add, subtract, multiply, divide\n- calculator.test.ts - [NOT STARTED] Test suite\n- calculator.ts - [NOT STARTED] Implementation"

// After test writing
UPDATE_README CONTENT="# Calculator Module\n\nImplements arithmetic operations for the application.\n\n## Files\n- calculator.interface.ts - [FINISHED] Interface with add, subtract, multiply, divide\n- calculator.test.ts - [FINISHED] 20 tests covering all operations and edge cases\n- calculator.ts - [BEGUN] Implementation in progress"

// Final state
UPDATE_README CONTENT="# Calculator Module\n\nImplements arithmetic operations for the application.\n\n## Files\n- calculator.interface.ts - [FINISHED] Interface with add, subtract, multiply, divide\n- calculator.test.ts - [FINISHED] 20 tests covering all operations and edge cases\n- calculator.ts - [FINISHED] Full implementation passing all tests"
```

## Quick Reference

**Status Values**: NOT STARTED, BEGUN, FINISHED (only these 3!)

**Development Order**: Interface → Tests → Implementation

**Context Instructions**: Always tell children what files to READ

**Verification**: Always READ files and SPAWN testers to verify child claims

**WAIT Usage**: Only when children active from comma-separated delegation/spawn

**Cannot FINISH**: While any child is still active

**Multiple Operations**: Use commas to delegate/spawn multiple in one command

**README Format**: Purpose summary + file/folder list with status and description