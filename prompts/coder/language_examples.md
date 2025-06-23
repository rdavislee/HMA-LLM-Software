# Coder Language Examples

This file contains comprehensive examples of how to use the Coder Language for various scenarios. The Coder Language is designed for file-level agents that can read files, run commands, change their assigned file, and signal task completion.

## Basic File Operations

### Reading Files
```
READ "README.md"
READ "main.py"
```

### Reading Nested or Special Files
```
READ "src/utils.py"
READ "config/settings.json"
READ "docs/usage.md"
```

## File Modification

### Changing File Content
```
CHANGE CONTENT = "print(\"Hello, world!\")\n"
```

### Overwriting with Multiline Content
```
CHANGE CONTENT = """def add(a, b):\n    return a + b\n\nprint(add(2, 3))\n"""
```

## System Commands

### Running Tests
```
RUN "python -m pytest test_main.py"
RUN "python -m unittest discover tests"
```

### Installing Dependencies
```
RUN "pip install -r requirements.txt"
```

## Complete Workflow Example

### Refactor and Test a File
```
READ "old_module.py"
CHANGE CONTENT = """# Refactored module\ndef foo():\n    pass\n"""
RUN "python -m pytest test_old_module.py"
FINISH PROMPT = "Refactoring and testing complete."
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