# Tester Language Test Suite

This directory contains comprehensive tests for the Tester Language implementation, including AST classes, parser functionality, and interpreter behavior.

## Test Coverage

The test suite covers all components of the Tester Language system:

### AST Tests (`test_tester_ast.py`)
- **Directive Classes**: All directive types (ReadDirective, RunDirective, ChangeDirective, FinishDirective)
- **Supporting Classes**: Target, PromptField, AST nodes
- **Visitor Pattern**: ASTVisitor implementation and traversal
- **String Representations**: All `__str__` and `__repr__` methods
- **Data Conversion**: `to_dict()` and `to_string()` methods
- **Validation**: Input validation and error handling

### Parser Tests (`test_tester_parser.py`)
- **Single Directive Parsing**: All directive types with various parameters
- **Multiple Directive Parsing**: Mixed directive sequences
- **String Handling**: Escape sequences, quotes, special characters
- **Error Handling**: Malformed directives, invalid syntax
- **Transformer Testing**: String transformation and AST creation
- **Convenience Functions**: Module-level parsing functions

### Interpreter Tests (`test_tester_interpreter.py`)
- **READ Operations**: File reading, memory management, error handling
- **RUN Operations**: Command execution, output capture, security restrictions
- **CHANGE Operations**: Scratch pad modifications, file creation
- **FINISH Operations**: Task completion, cleanup, parent communication
- **Error Handling**: Exception management, error reporting
- **Agent Integration**: Mock agent interaction, state management

## Test Structure

Each test file follows the partitioning methodology:

1. **Positive Cases**: Testing expected functionality with valid inputs
2. **Negative Cases**: Testing error handling with invalid inputs
3. **Edge Cases**: Testing boundary conditions and special scenarios
4. **Integration**: Testing interaction between components

## Running Tests

### Run All Tester Language Tests
```bash
pytest test/tester_language/ -v
```

### Run Specific Test Files
```bash
pytest test/tester_language/test_tester_ast.py -v
pytest test/tester_language/test_tester_parser.py -v
pytest test/tester_language/test_tester_interpreter.py -v
```

### Run Tests with Coverage
```bash
pytest test/tester_language/ --cov=src.languages.tester_language --cov-report=term-missing
```

## Test Fixtures

The test suite uses several fixtures for consistent test setup:

- **`tmp_workspace`**: Isolated temporary directory for file operations
- **`mock_agent`**: Stub agent implementation for testing interpreter interactions
- **`sample_files`**: Pre-created test files with known content
- **`patch_async`**: Mocking for asynchronous operations

## Test Dependencies

Tests use the following external libraries:
- `pytest`: Main testing framework
- `pytest-asyncio`: For testing async functionality
- `pathlib`: For file system operations
- `unittest.mock`: For mocking dependencies

## Coverage Goals

The test suite aims for 100% code coverage across:
- All AST classes and methods
- Parser functionality and error handling
- Interpreter directive execution
- Agent interaction and state management

## Test Data

Test cases include realistic scenarios:
- **File Reading**: Various file types and paths
- **Command Execution**: Testing commands, linting, analysis tools
- **Scratch Pad Usage**: Debugging code, temporary scripts
- **Error Scenarios**: Missing files, invalid commands, permission errors

## Performance Testing

While not the primary focus, tests include basic performance validations:
- Parser efficiency with large directive sets
- Memory usage during file operations
- Command execution timeouts

## Integration with CI/CD

These tests are designed to run in continuous integration environments:
- No external dependencies required
- Isolated test environments
- Consistent cross-platform behavior
- Clear failure reporting

## Future Test Enhancements

Planned improvements to the test suite:
- Property-based testing with hypothesis
- Load testing for large codebases
- Integration testing with real LLM clients
- Performance benchmarking
- Security testing for command execution 