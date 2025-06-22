# Manager Language Examples

This file contains comprehensive examples of how to use the Manager Language for various scenarios.

## Basic File Operations

### Creating a Project Structure
```
CREATE folder "my_project"
CREATE folder "my_project/src"
CREATE folder "my_project/tests"
CREATE folder "my_project/docs"
CREATE file "my_project/README.md"
CREATE file "my_project/requirements.txt"
```

### Reading Files and Folders
```
READ file "my_project/README.md"
READ folder "my_project/src"
```

### Deleting Files and Folders
```
DELETE file "my_project/temp.txt"
DELETE folder "my_project/old_code"
```

## Delegation Examples

### Delegate to File Agents
```
DELEGATE file "my_project/src/main.py" PROMPT="Create a Python main function that prints hello world"
DELEGATE file "my_project/requirements.txt" PROMPT="Create a requirements.txt with basic Python packages"
DELEGATE file "my_project/README.md" PROMPT="Create a comprehensive README for this project"
```

### Delegate to Folder Agents
```
DELEGATE folder "my_project/src" PROMPT="Create a module structure with __init__.py and core functionality"
DELEGATE folder "my_project/tests" PROMPT="Create test files for the src module"
```

## Concurrent Task Management

### Delegating Multiple Independent Tasks
```
DELEGATE file "src/utils.py" PROMPT="Create utility functions for file operations"
DELEGATE file "src/config.py" PROMPT="Create configuration management"
DELEGATE file "src/database.py" PROMPT="Create database connection utilities"
WAIT
```

### Sequential Task Management
```
DELEGATE file "src/models.py" PROMPT="Create data models"
WAIT
DELEGATE file "src/controllers.py" PROMPT="Create controllers that use the models"
WAIT
DELEGATE file "src/views.py" PROMPT="Create views that use the controllers"
```

## Agent Maintenance

### Updating Personal README
```
UPDATE_README CONTENT_STRING="This manager agent is responsible for the my_project directory. It coordinates development of a Python web application with models, controllers, and views. The agent follows a test-first development approach and maintains separation of concerns."
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

## Complete Workflow Examples

### Setting Up a New Module
```
CREATE folder "src/auth"
CREATE file "src/auth/__init__.py"
DELEGATE file "src/auth/models.py" PROMPT="Create user authentication models"
DELEGATE file "src/auth/controllers.py" PROMPT="Create authentication controllers"
DELEGATE file "src/auth/views.py" PROMPT="Create authentication views"
WAIT
DELEGATE folder "tests/auth" PROMPT="Create comprehensive tests for auth module"
WAIT
RUN "python -m pytest tests/auth/"
UPDATE_README CONTENT_STRING="Auth module created with models, controllers, views, and tests. All tests passing."
FINISH PROMPT="Auth module setup complete"
```

### Refactoring Existing Code
```
READ file "src/old_module.py"
DELEGATE file "src/new_module.py" PROMPT="Refactor the old module with better structure and documentation"
WAIT
DELEGATE file "tests/test_new_module.py" PROMPT="Create tests for the refactored module"
WAIT
RUN "python -m pytest tests/test_new_module.py"
DELETE file "src/old_module.py"
UPDATE_README CONTENT_STRING="Successfully refactored old_module.py to new_module.py with improved structure and comprehensive tests."
FINISH PROMPT="Refactoring complete"
```

## Error Handling Patterns

### Checking Before Operations
```
READ file "src/config.py"
DELEGATE file "src/config.py" PROMPT="Add error handling to configuration loading"
WAIT
DELEGATE file "tests/test_config.py" PROMPT="Add tests for error handling in config"
WAIT
RUN "python -m pytest tests/test_config.py"
```

### Cleanup After Errors
```
DELEGATE file "src/experimental.py" PROMPT="Try implementing experimental feature"
WAIT
RUN "python -m pytest tests/test_experimental.py"
DELETE file "src/experimental.py"
UPDATE_README CONTENT_STRING="Experimental feature failed tests and was removed."
```

## Best Practices

1. **Always use WAIT after delegating tasks** to ensure completion before proceeding
2. **Update README regularly** to maintain context for future agent instances
3. **Use FINISH with descriptive messages** to clearly indicate task completion
4. **Run tests after major changes** to ensure code quality
5. **Delete temporary or failed files** to keep the codebase clean
6. **Delegate to appropriate agent types** - files for file agents, folders for manager agents 