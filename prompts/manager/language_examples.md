# Manager Language Examples

This file contains comprehensive examples of how to use the Manager Language for various scenarios.

## Basic File Operations

### Reading Files
```
READ file "README.md"
READ file "main.py"
READ file "calculator.ts"
```

# Reading many files at once
```
READ file "README.md", file "main.py", file "utils.py", file "config.json"
READ file "calculator.ts", file "types.ts", file "utils.ts"
```

# Reading a set of related files
```
READ file "models.py", file "controllers.py", file "views.py"
READ file "calculator.ts", file "calculator.interface.ts", file "types.ts"
```

### Reading Folders (fetch README)
When you want to load the documentation of an entire sub-module into memory, use `READ folder` with the folder name. The interpreter will search for `<folder_name>_README.md` inside the folder and add it to the agent's memory.

```
READ folder "docs"
READ folder "api"
```

For example, if the project has a directory structure like:

```
project/
  ├── docs/
  │   └── docs_README.md
  └── api/
      └── api_README.md
```

`READ folder "docs"` will load `docs/docs_README.md`, and `READ folder "api"` will load `api/api_README.md` into memory.

## Delegation Examples

### Delegate to File Agents (Mixed Languages)
```
DELEGATE file "main.py" PROMPT="Create a Python main function that initializes the application"
DELEGATE file "calculator.ts" PROMPT="Create a TypeScript calculator class with basic arithmetic operations"
DELEGATE file "calculator.interface.ts" PROMPT="Define the TypeScript interface for the calculator"
DELEGATE file "requirements.txt" PROMPT="Create a requirements.txt with necessary Python packages"
DELEGATE file "package.json" PROMPT="Create package.json with TypeScript dependencies"
DELEGATE file "README.md" PROMPT="Create a comprehensive README for this project"
```

### Delegate to Folder Agents (Mixed Environments)
```
DELEGATE folder "src" PROMPT="Create TypeScript source files with interfaces and core functionality"
DELEGATE folder "python_backend" PROMPT="Create Python backend with API endpoints and data processing"
DELEGATE folder "test" PROMPT="Create comprehensive test suite for both TypeScript and Python modules"
```


## Agent Maintenance

### Updating Personal README with Directory Inventory
```
UPDATE_README CONTENT_STRING="# Calculator Module Manager

This manager coordinates development of a TypeScript calculator module with comprehensive testing.

## Directory Contents

### Files
- `calculator.ts` - [IMPLEMENTED] Main calculator class with basic arithmetic operations
- `calculator.interface.ts` - [COMPLETE] TypeScript interface defining calculator contract
- `calculator_README.md` - [COMPLETE] This documentation file

### Subdirectories
- `test/` - [IN PROGRESS] Test suite directory, 4/6 test files implemented
- `docs/` - [NOT STARTED] Documentation folder planned for API docs

## Current Status
- Core arithmetic functions (add, subtract, multiply, divide) are complete
- Advanced functions (power, logarithm) need implementation  
- Test coverage at 80%, missing edge case tests
- All implemented functionality passes current tests

## Next Steps
- Complete advanced mathematical functions
- Expand test coverage for edge cases
- Generate API documentation"
```

### Directory Inventory After File Creation
```
UPDATE_README CONTENT_STRING="# Source Module Manager

## Directory Contents

### Files  
- `main.ts` - [SPECCED] Main application entry point, interface defined
- `utils.ts` - [TESTS ONLY] Utility functions, comprehensive test suite exists
- `config.ts` - [NOT STARTED] Configuration management, planned but not begun
- `src_README.md` - [COMPLETE] This documentation file

### Subdirectories
- `components/` - [IN PROGRESS] UI components, 3/5 files implemented
- `services/` - [BLOCKED] Service layer, waiting for API specification
- `types/` - [COMPLETE] TypeScript type definitions, all defined and tested

## Development Progress
Total files: 3 created, 2 pending
Test coverage: 60% (utils fully tested, main/config pending)
Blocking issues: API spec needed for services implementation"
```

### Status Updates After Child Completion
```
UPDATE_README CONTENT_STRING="# TypeScript Application Manager

## Directory Contents

### Files
- `app.ts` - [COMPLETE] Main application with all modules implemented and tested
- `types.ts` - [COMPLETE] Type definitions with full interface coverage
- `package.json` - [COMPLETE] All dependencies specified and tested

### Subdirectories  
- `components/` - [COMPLETE] TypeScript components for all features
- `utils/` - [IN PROGRESS] Utility functions, 2/3 modules complete
- `test/` - [COMPLETE] Comprehensive test suite with 95% coverage

## Project Status
- Core functionality fully implemented and tested
- Utility modules nearly complete (missing validation utils)
- All tests passing
- Ready for deployment after utility completion"
```

## System Commands

### TypeScript Testing Workflow (REQUIRED SEQUENCE)
```
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
```

### TypeScript Testing with Specific Tests
```
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js --grep 'specific test name'"
```

### TypeScript Testing for Specific Files
```
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js dist/test/calculator.test.js"
```

### Python Testing (Future Support)
```
RUN "python -m pytest tests/"
RUN "python -m pytest tests/test_file.py::test_function"
```



## Complete Workflow Example (Prototype)

### Coordinating TypeScript Development
```
READ file "calculator.ts"
RUN "node tools/check-typescript.js"
DELEGATE file "calculator.ts" PROMPT="Fix the TypeScript errors shown in diagnostics and refactor with better structure"
DELEGATE file "test/calculator.test.ts" PROMPT="Create comprehensive tests for the refactored calculator"
RUN "node tools/check-typescript.js"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
UPDATE_README CONTENT_STRING="Successfully refactored calculator.ts with improved structure and comprehensive tests."
FINISH PROMPT="Refactoring complete"
```

## Error Handling Patterns

### Checking Before Operations
```
READ file "config.ts"
DELEGATE file "config.ts" PROMPT="Add error handling to configuration loading"
DELEGATE file "test/config.test.ts" PROMPT="Add tests for error handling in config"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js --grep 'config'"
```

## Best Practices

1. **Always use WAIT after delegating tasks** to ensure completion before proceeding
2. **Update README regularly** to maintain context for future agent instances
3. **Use FINISH with descriptive messages** to clearly indicate task completion
4. **Run tests after major changes** to ensure code quality
5. **Delegate to appropriate agent types** - files for file agents, folders for manager agents
6. **Maintain directory inventory** with current status of all files and folders
7. **Use standardized status labels** (NOT STARTED, SPECCED, TESTS ONLY, IN PROGRESS, IMPLEMENTED, COMPLETE, BLOCKED)
8. **Update inventory after every delegation** to reflect current development state
9. **Follow language-specific workflows** when running tests or building projects
10. **Plan for multi-language coordination** when projects span multiple programming environments