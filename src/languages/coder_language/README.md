# Coder Language

The Coder Language is a specialized language for coder agents in the hierarchical multi-agent software development framework. It provides a simple, structured way for coder agents to communicate their actions and intentions.

## Overview

Coder agents are responsible for implementing specific files in the codebase. They can read any file in the codebase, run commands (primarily for testing), change their own file, and finish their tasks.

## Directives

The Coder Language supports four main directives:

### READ
Read any file in the codebase to understand dependencies, imports, or other context.

**Syntax:** `READ "filename"`
**Example:** `READ "src/utils/helpers.py"`

### RUN
Execute terminal commands, typically for running tests or other development tasks.

**Syntax:** `RUN "command"`
**Example:** `RUN "python -m pytest tests/test_my_file.py"`

### CHANGE
Replace the entire contents of the agent's own file. This is the only file the agent can modify.

**Syntax:** `CHANGE CONTENT="new file contents"`
**Example:** `CHANGE CONTENT="def new_function(): return True"`

### FINISH
Complete the current task and report back to the parent agent.

**Syntax:** `FINISH PROMPT="completion message"`
**Example:** `FINISH PROMPT="Successfully implemented the user authentication feature"`

## Key Principles

1. **File Ownership**: Each coder agent is responsible for one specific file and can only modify that file.

2. **Read Access**: Coder agents can read any file in the codebase to understand dependencies and context.

3. **Command Execution**: Agents can run commands, primarily for testing purposes.

4. **Complete File Replacement**: When changing their file, agents must provide the entire file contents, not just partial changes.

## Typical Workflow

A typical coder agent workflow follows this pattern:

1. **Receive Task**: Get assigned a task and identify the file to work on
2. **Read Dependencies**: Read files that the agent's file depends on or imports from
3. **Run Tests**: Execute tests to see the current state and failures
4. **Implement Changes**: Modify the file to address the requirements
5. **Test Again**: Run tests to verify the implementation
6. **Iterate**: Repeat steps 4-5 until tests pass
7. **Finish**: Report completion back to the parent agent

## Example Usage

```python
from src.languages.coder_language import CoderLanguageInterpreter

# Initialize interpreter for a specific file
interpreter = CoderLanguageInterpreter(own_file="src/auth/user.py")

# Read dependencies
context = interpreter.execute('READ "src/models/user.py"')
context = interpreter.execute('READ "src/utils/validation.py"')

# Run tests to see current state
context = interpreter.execute('RUN "python -m pytest tests/test_user.py"')

# Implement changes
new_content = '''
from src.models.user import User
from src.utils.validation import validate_email

def create_user(email: str, password: str) -> User:
    if not validate_email(email):
        raise ValueError("Invalid email")
    return User(email=email, password=password)
'''

context = interpreter.execute(f'CHANGE CONTENT="{new_content}"')

# Run tests again
context = interpreter.execute('RUN "python -m pytest tests/test_user.py"')

# Finish task
context = interpreter.execute('FINISH PROMPT="User creation functionality implemented successfully"')
```

## Context Management

The interpreter maintains a context that tracks all executed actions:

- `reads`: List of files read and their results
- `commands`: List of commands executed and their results
- `changes`: List of file changes made
- `finished`: Boolean indicating if the task is complete
- `completion_prompt`: The message sent when finishing
- `own_file`: The file this agent is responsible for

## Error Handling

The language includes comprehensive error handling:

- File not found errors for READ operations
- Permission errors for CHANGE operations on non-owned files
- Command execution errors with detailed output
- Parsing errors with helpful error messages

## Integration with Manager Language

The Coder Language is designed to work alongside the Manager Language in the hierarchical agent framework:

- Manager agents use the Manager Language to delegate tasks to coder agents
- Coder agents use the Coder Language to execute their assigned tasks
- Both languages share similar syntax and structure for consistency
- The FINISH directive in Coder Language corresponds to the DELEGATE directive in Manager Language

## Future Enhancements

Potential future additions to the Coder Language:

- Support for partial file modifications
- Integration with version control systems
- Support for code formatting and linting commands
- Enhanced error reporting and debugging capabilities
- Integration with IDE and development tools 