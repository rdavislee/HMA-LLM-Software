# Manager Language

A complete implementation of the Manager Language for autonomous agent coordination, built with Lark for robust parsing and execution.

## Overview

The Manager Language is a domain-specific language designed for autonomous agents to communicate directives for file operations, delegation, and coordination. This implementation uses Lark for parsing and provides a clean API for executing manager directives.

## Features

- **Lark-based Parser**: Robust parsing using the Lark library with automatic tokenization
- **AST Representation**: Clean abstract syntax tree for parsed directives
- **File System Operations**: Create, delete, and read files and folders
- **Delegation Support**: Delegate tasks to other agents with prompts
- **Error Handling**: Comprehensive error handling and reporting
- **Context Management**: Maintain execution context across multiple directives
- **Readme Update Support**: Agents can update and maintain a personal README for future instances of themselves using the `UPDATE_README` directive

## Installation

Add the required dependency to your `requirements.txt`:

```
lark>=1.1.0
```

## Quick Start

```python
from src.languages.manager_language import parse_directive, execute_directive

# Parse and execute a single directive
directive = 'CREATE file "example.txt"'
result = execute_directive(directive)
print(result)
```

## Grammar

The Manager Language supports the following directives:

### CREATE Directive
Create files or folders:
```
CREATE file "filename.txt"
CREATE folder "foldername"
```

### DELETE Directive
Delete files or folders:
```
DELETE file "filename.txt"
DELETE folder "foldername"
```

### READ Directive
Read files or list folder contents:
```
READ file "filename.txt"
READ folder "foldername"
```

### DELEGATE Directive
Delegate tasks to other agents:
```
DELEGATE file "filename.txt" PROMPT="Write content for this file"
DELEGATE folder "foldername" PROMPT="Create a module in this folder"
```

### FINISH Directive
Mark completion with a message:
```
FINISH PROMPT="Task completed successfully"
```

### WAIT Directive
Wait for other operations to complete:
```
WAIT
```

### UPDATE_README Directive
Update or maintain a personal README for the agent:
```
UPDATE_README CONTENT="This is the new README content for the agent."
```
- The `CONTENT` field completely replaces the current README content for the agent.
- This directive allows agents to persist important information for future instances of themselves.

## API Reference

### Parser

#### `parse_directive(text: str) -> DirectiveType`
Parse a single directive string into an AST object.

#### `parse_directives(text: str) -> List[DirectiveType]`
Parse multiple directives from a text block (one per line).

#### `ManagerLanguageParser`
Main parser class for advanced usage.

### Interpreter

#### `execute_directive(directive_text: str, base_path: str = ".") -> Dict[str, Any]`
Parse and execute a single directive.

#### `execute_directives(directives_text: str, base_path: str = ".") -> Dict[str, Any]`
Parse and execute multiple directives.

#### `ManagerLanguageInterpreter`
Main interpreter class for advanced usage.

### AST Classes

- `Directive`: Base class for all directives
- `DelegateDirective`: Represents DELEGATE directives
- `FinishDirective`: Represents FINISH directives
- `ActionDirective`: Represents CREATE, DELETE, READ directives
- `WaitDirective`: Represents WAIT directives
- `RunDirective`: Represents RUN directives
- `UpdateReadmeDirective`: Represents UPDATE_README directives
- `Target`: Represents file or folder targets
- `PromptField`: Represents prompt values
- `DelegateItem`: Represents individual delegation items

## Usage Examples

### Basic File Operations

```python
from src.languages.manager_language import execute_directives

# Create a project structure
directives = """
CREATE folder "my_project"
CREATE folder "my_project/src"
CREATE folder "my_project/tests"
CREATE file "my_project/README.md"
"""

result = execute_directives(directives)
print(result)
```

### Delegation

```python
from manager_language import execute_directive

# Delegate file creation to another agent
directive = 'DELEGATE file "src/main.py" PROMPT="Create a Python main function"'
result = execute_directive(directive)
print(result)
```

### Update Agent README

```python
from manager_language import execute_directive

# Update the agent's personal README
directive = 'UPDATE_README CONTENT="Document the agent\'s new capabilities and usage."'
result = execute_directive(directive)
print(result)
# The result context will include a 'readme_updates' key with the new content
```

### Using the Interpreter Class

```python
from src.languages.manager_language import ManagerLanguageInterpreter

# Create interpreter with custom base path
interpreter = ManagerLanguageInterpreter(base_path="./workspace")

# Execute multiple directives
directives = [
    'CREATE folder "project"',
    'CREATE file "project/config.json"',
    'DELEGATE file "project/config.json" PROMPT="Create a JSON configuration"',
    'UPDATE_README CONTENT="Project initialized with config."',
    'FINISH PROMPT="Project setup complete"'
]

for directive in directives:
    result = interpreter.execute(directive)
    print(f"Executed: {directive}")
    print(f"Result: {result}")

# Get final context
context = interpreter.get_context()
print(f"Final context: {context}")
```

### Error Handling

```python
from manager_language import execute_directive

try:
    result = execute_directive('INVALID file "test.txt"')
except Exception as e:
    print(f"Error: {e}")
```

## String Escaping

The language supports standard escape sequences in strings:

- `\"` - Double quote
- `\\` - Backslash
- `\/` - Forward slash
- `\b` - Backspace
- `\f` - Form feed
- `\n` - Newline
- `\r` - Carriage return
- `\t` - Tab
- `\v` - Vertical tab

Example:
```
DELEGATE file "config.json" PROMPT="Create JSON with \"quotes\" and \n newlines"
```

## Context Management

The interpreter maintains an execution context that includes:

- `actions`: List of performed file operations
- `delegations`: List of delegation tasks
- `commands`: List of executed commands
- `readme_updates`: List of README update operations (from UPDATE_README directives)
- `finished`: Whether the agent has finished
- `waiting`: Whether the agent is waiting
- `completion_prompt`: Final completion message

## File Paths

All file operations are relative to the interpreter's base path. You can set a custom base path when creating an interpreter:

```python
interpreter = ManagerLanguageInterpreter(base_path="/path/to/workspace")
```

## Integration with Agent Systems

The Manager Language is designed to integrate with autonomous agent systems:

1. **Parsing**: Parse agent output into structured directives
2. **Execution**: Execute directives to perform file operations
3. **Delegation**: Track delegation tasks for agent coordination
4. **Context**: Maintain execution context for agent state

## Error Handling

The parser and interpreter provide comprehensive error handling:

- **Parse Errors**: Invalid syntax is caught and reported
- **File System Errors**: File operation failures are handled gracefully
- **Context Errors**: Invalid operations are logged in the context

## Testing

Run the demo script to see the language in action:

```bash
python examples/manager_language_demo.py
```

## Contributing

When contributing to the Manager Language:

1. Follow the existing code style
2. Add tests for new features
3. Update the grammar documentation
4. Ensure backward compatibility

## License

This implementation is part of the Autonomous Agent Framework project. 