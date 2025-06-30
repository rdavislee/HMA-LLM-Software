# Tester Language

The Tester Language is a specialized language for tester ephemeral agents in the hierarchical multi-agent software development framework. It provides a simple, structured way for tester agents to communicate their testing actions and findings.

## Overview

Tester agents are ephemeral agents spawned by coder or manager agents to perform context-heavy testing operations. They can read any file in the codebase, run commands (primarily for testing), modify their personal scratch pad for debugging, and report their findings back to the parent agent. Each tester agent gets a personal scratch pad file for writing temporary debugging code.

## Directives

The Tester Language supports four main directives:

### READ
Read any file in the codebase to understand code structure, dependencies, or test implementations.

**Syntax:** `READ "filename"`
**Example:** `READ "src/utils/helpers.py"`

### RUN
Execute terminal commands, typically for running tests, linting, or other analysis tools.

**Syntax:** `RUN "command"`
**Example:** `RUN "python -m pytest tests/test_my_module.py -v"`

### CHANGE
Modify the tester agent's personal scratch pad file with debugging or temporary code.

**Syntax:** `CHANGE CONTENT="file contents"`
**Example:** `CHANGE CONTENT="print('Debug: testing auth module')\nimport pdb; pdb.set_trace()"`

### FINISH
Complete the testing task and report findings back to the parent agent.

**Syntax:** `FINISH PROMPT="completion message"`
**Example:** `FINISH PROMPT="Found 3 failing tests in authentication module - see details in previous output"`

## Key Principles

1. **Scratch Pad for Debugging**: Each tester agent gets a personal scratch pad file for debugging and temporary code.

2. **Read Access**: Tester agents can read any file in the codebase to understand the code being tested.

3. **Command Execution**: Agents can run commands, primarily for testing, linting, and analysis purposes.

4. **Ephemeral Nature**: Tester agents are temporary and report results back to their parent agent. The scratch pad is cleaned up when the agent finishes.

5. **Testing Focus**: These agents are specifically designed for testing tasks, not implementation.

## Scratch Pad Management

Each tester agent automatically gets a personal scratch pad file:

- **Location**: `scratch_pads/` directory in the project root
- **Naming**: Based on the parent agent's path with dots instead of slashes (e.g., `src.auth.user.py_scratch.py`)
- **Cleanup**: Automatically deleted when the tester agent finishes
- **Purpose**: For debugging code, temporary functions, and testing experiments

## Typical Workflow

A typical tester agent workflow follows this pattern:

1. **Receive Testing Task**: Get assigned a testing task from a parent agent
2. **Read Code Files**: Read the source files that need to be tested
3. **Read Test Files**: Read existing test files to understand current test coverage
4. **Run Tests**: Execute test suites to see current status
5. **Debug with Scratch Pad**: Write debugging code in the scratch pad to investigate issues
6. **Run Analysis**: Execute linting, coverage, or other analysis tools
7. **Analyze Results**: Understand what's working and what's failing
8. **Report Findings**: Report detailed findings back to the parent agent

## Example Usage

```python
from src.languages.tester_language import TesterLanguageInterpreter

# Initialize interpreter for a tester agent
interpreter = TesterLanguageInterpreter(agent=tester_agent)

# Read source code to understand implementation
interpreter.execute('READ "src/auth/user.py"')
interpreter.execute('READ "src/auth/session.py"')

# Read existing tests
interpreter.execute('READ "tests/test_auth.py"')

# Run tests to see current status
interpreter.execute('RUN "python -m pytest tests/test_auth.py -v"')

# Write debugging code to scratch pad
debug_code = '''
import sys
sys.path.append("src")
from auth.user import User

# Debug the failing test
def debug_user_creation():
    user = User("test@example.com", "password")
    print(f"User created: {user}")
    print(f"Email: {user.email}")
    return user

if __name__ == "__main__":
    debug_user_creation()
'''
interpreter.execute(f'CHANGE CONTENT="{debug_code}"')

# Run the debug script
interpreter.execute('RUN "python scratch_pads/src.auth.user.py_scratch.py"')

# Run additional analysis
interpreter.execute('RUN "python -m pytest tests/test_auth.py --cov=src.auth --cov-report=term"')

# Check code quality
interpreter.execute('RUN "flake8 src/auth/"')

# Report findings
interpreter.execute('FINISH PROMPT="Authentication tests: 8 passing, 2 failing. Issue found in User.__init__ method - see debug output above. Coverage at 85%."')
```

## Context Management

The interpreter maintains execution context that tracks:

- `reads`: List of files read and their results
- `commands`: List of commands executed and their results
- `changes`: List of scratch pad modifications made
- `finished`: Boolean indicating if the testing task is complete
- `completion_prompt`: The message sent when finishing

## Error Handling

The language includes comprehensive error handling:

- File not found errors for READ operations
- Command execution errors with detailed output
- Scratch pad write errors with helpful messages
- Parsing errors with helpful error messages
- Timeout handling for long-running commands

## Integration with Agent System

The Tester Language is designed to work within the hierarchical agent framework:

- Parent agents (coder or manager) spawn tester agents for testing tasks
- Tester agents use the Tester Language to execute their assigned testing tasks
- The FINISH directive reports results back to the parent agent and cleans up the scratch pad
- Tester agents are ephemeral and don't persist after completing their task

## Differences from Coder Language

The Tester Language is similar to the Coder Language but with key differences:

- **Scratch Pad Only**: Tester agents can only modify their own scratch pad file, not project files
- **Ephemeral Nature**: Tester agents don't persist and their scratch pads are cleaned up
- **Testing Focus**: Commands are typically testing-related
- **Result Reporting**: Results are reported back to parent agents

## Command Restrictions

Tester agents can only run commands from the allowed commands list defined in the system configuration. This typically includes:

- Testing frameworks (pytest, unittest, etc.)
- Code analysis tools (flake8, pylint, mypy, etc.)
- Coverage tools (coverage.py, pytest-cov, etc.)
- Build tools (make, npm, etc.)
- Python interpreter for running debug scripts

## Future Enhancements

Potential future additions to the Tester Language:

- Support for test result parsing and structured reporting
- Integration with continuous integration systems
- Support for performance testing and benchmarking
- Enhanced error analysis and debugging capabilities
- Integration with test management tools
- Support for multiple scratch pad files or temporary file creation 