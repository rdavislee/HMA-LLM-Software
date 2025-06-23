# Manager Language Examples

This file contains comprehensive examples of how to use the Manager Language for various scenarios.

## Basic File Operations

### Reading Files
```
READ file "README.md"
READ file "main.py"
```

# Reading many files at once
```
READ file "README.md", file "main.py", file "utils.py", file "config.py"
```

# Reading a set of related files
```
READ file "models.py", file "controllers.py", file "views.py"
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

### Delegate to File Agents
```
DELEGATE file "main.py" PROMPT="Create a Python main function that prints hello world"
DELEGATE file "requirements.txt" PROMPT="Create a requirements.txt with basic Python packages"
DELEGATE file "README.md" PROMPT="Create a comprehensive README for this project"
```

### Delegate to Folder Agents
```
DELEGATE folder "src" PROMPT="Create a module structure with __init__.py and core functionality"
DELEGATE folder "tests" PROMPT="Create test files for the src module"
```

## Concurrent Task Management

### Delegating Multiple Independent Tasks
```
DELEGATE file "utils.py" PROMPT="Create utility functions for file operations"
DELEGATE file "config.py" PROMPT="Create configuration management"
DELEGATE file "database.py" PROMPT="Create database connection utilities"
```

### Sequential Task Management
```
DELEGATE file "models.py" PROMPT="Create data models"
DELEGATE file "controllers.py" PROMPT="Create controllers that use the models"
DELEGATE file "views.py" PROMPT="Create views that use the controllers"
```

## Agent Maintenance

### Updating Personal README
```
UPDATE_README CONTENT_STRING="This manager agent is responsible for the current directory. It coordinates development of a Python web application with models, controllers, and views. The agent follows a test-first development approach and maintains separation of concerns."
```

## System Commands

### Running Tests
```
RUN "python -m pytest tests/"
RUN "python -m unittest discover tests"
```

### Building and Installing
```
RUN "pip install -r requirements.txt"
RUN "python setup.py build"
```

## Complete Workflow Example (Prototype)

### Coordinating Without File Creation/Deletion
```
READ file "old_module.py"
DELEGATE file "new_module.py" PROMPT="Refactor the old module with better structure and documentation"
DELEGATE file "test_new_module.py" PROMPT="Create tests for the refactored module"
RUN "python -m pytest test_new_module.py"
UPDATE_README CONTENT_STRING="Successfully refactored old_module.py to new_module.py with improved structure and comprehensive tests."
FINISH PROMPT="Refactoring complete"
```

## Error Handling Patterns

### Checking Before Operations
```
READ file "config.py"
DELEGATE file "config.py" PROMPT="Add error handling to configuration loading"
DELEGATE file "test_config.py" PROMPT="Add tests for error handling in config"
RUN "python -m pytest test_config.py"
```

## Best Practices

1. **Always use WAIT after delegating tasks** to ensure completion before proceeding
2. **Update README regularly** to maintain context for future agent instances
3. **Use FINISH with descriptive messages** to clearly indicate task completion
4. **Run tests after major changes** to ensure code quality
5. **Delegate to appropriate agent types** - files for file agents, folders for manager agents 