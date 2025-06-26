# Coder Language Examples

This file contains comprehensive examples of how to use the Coder Language for various scenarios. The Coder Language is designed for file-level agents that can read files, run commands, change their assigned file, and signal task completion.

## Basic File Operations

### Reading Files
```
READ "README.md"
READ "main.py"
READ "calculator.ts"
```

### Reading Nested or Special Files
```
READ "src/utils.py"
READ "src/calculator.ts"
READ "config/settings.json"
READ "docs/usage.md"
```

## File Modification

### Changing Python File Content
```
CHANGE CONTENT = "print(\"Hello, world!\")\n"
```

### Changing TypeScript File Content
```
CHANGE CONTENT = "console.log('Hello, world!');\n"
```

### Overwriting with Multiline Content (Python)
```
CHANGE CONTENT = """def add(a, b):\n    return a + b\n\nprint(add(2, 3))\n"""
```

### Overwriting with Multiline Content (TypeScript)
```
CHANGE CONTENT = """function add(a: number, b: number): number {\n    return a + b;\n}\n\nconsole.log(add(2, 3));\n"""
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

## Complete Workflow Examples

### TypeScript Test-Driven Development
```
READ "test/calculator.test.ts"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
CHANGE CONTENT = """// Updated implementation based on test failures
export class Calculator {
    add(a: number, b: number): number {
        return a + b;
    }
    
    divide(a: number, b: number): number {
        if (b === 0) {
            return a > 0 ? Infinity : a < 0 ? -Infinity : NaN;
        }
        return a / b;
    }
}"""
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
FINISH PROMPT = "Implementation updated and all tests now pass."
```

### Python Module Development (Future Support)
```
READ "test_module.py"
CHANGE CONTENT = """def process_data(data):
    if not data:
        return []
    
    result = []
    for item in data:
        if isinstance(item, (int, float)) and item > 0:
            result.append(item * 2)
    
    return result

if __name__ == "__main__":
    test_data = [1, 2, -1, 3.5, "invalid"]
    print(process_data(test_data))
"""
RUN "python -m pytest test_module.py"
FINISH PROMPT = "Python module implemented and tested successfully."
```

### Simple TypeScript Development
```
READ "test/calculator.test.ts"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
CHANGE CONTENT = """export class Calculator {
    add(a: number, b: number): number {
        return a + b;
    }
    
    divide(a: number, b: number): number {
        if (b === 0) {
            return a > 0 ? Infinity : a < 0 ? -Infinity : NaN;
        }
        return a / b;
    }
}"""
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
FINISH PROMPT = "Implementation complete and all tests pass."
```

### Debugging Failed Tests (TypeScript) - MANDATORY Context Gathering
```
// STEP 1: Gather ALL context before making changes
READ "test/calculator.test.ts"
READ "src/calculator.ts" 
READ "src/calculatorInterface.ts"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js --grep 'should handle division by zero'"

// STEP 2: Now analyze and make informed changes
CHANGE CONTENT = """// Fixed division by zero handling based on test expectations
export class Calculator {
    divide(a: number, b: number): number {
        if (b === 0) {
            return a > 0 ? Infinity : a < 0 ? -Infinity : NaN;
        }
        return a / b;
    }
}"""
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js --grep 'divide'"
FINISH PROMPT = "Division method fixed and all division tests pass."
```

### Test Issue Assessment (TypeScript) - With Required Reading
```
// MANDATORY: Read all relevant files first
READ "test/calculator.test.ts"
READ "src/calculator.ts"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
// Now with full context, can properly assess the issue
FINISH PROMPT = "Test failure due to floating point precision issue. Test expects exact equality (3e+100) but gets (3.0000000000000002e+100). Implementation is mathematically correct - test should use .closeTo() instead of .equal() for large number arithmetic."
```

### Fixing Floating Point Test Tolerance (TypeScript)
```
READ "test/calculator.test.ts"
CHANGE CONTENT = """// ... existing test code ...
it('should handle large numbers', () => {
    expect(calculator.add(1e100, 2e100)).to.be.closeTo(3e100, 1e90); // Tolerance appropriate for 1e+100 scale
});
// ... existing test code ..."""
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js --grep 'large numbers'"
FINISH PROMPT = "Fixed floating point tolerance in large number test - changed from .equal() to .closeTo() with appropriate scale tolerance."
```

## Error Handling Patterns

### Handling Nonexistent Files
```
READ "nonexistent.py" // Will error if file does not exist
FINISH PROMPT = "File not found, cannot proceed."
```

### Handling Failing Commands
```
RUN "exit 1" // Will error due to nonzero exit code
FINISH PROMPT = "Command failed, aborting."
```

## Best Practices

1. **Always FINISH with a descriptive message** to clearly indicate task completion.
2. **Read files before making changes** to ensure up-to-date context.
3. **Run tests after making changes** to validate correctness.
4. **Use quoted strings for all filenames, commands, and content.**
5. **Handle errors gracefully** by finishing with a clear prompt message.
6. **Follow language-specific testing workflows** (TypeScript: compile then test; Python: direct testing) 