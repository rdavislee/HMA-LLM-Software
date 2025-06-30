# Coder Language Test Suite

This directory contains a comprehensive test suite for the Coder Language implementation, mirroring the manager language test structure and using partitioning methods to ensure complete coverage.

## Overview

The Coder Language is designed for autonomous agents that manage individual files in a codebase. The test suite validates all four core directives:

- **READ**: Read any file in the codebase for context
- **RUN**: Execute terminal commands (primarily for testing)
- **CHANGE**: Modify the agent's assigned file
- **FINISH**: Complete the task and report results

## Test Files

### test_interpreter.py
Comprehensive tests for the `CoderLanguageInterpreter` class with 40 test cases covering:

#### READ Directive Tests (Partitions)
- **Success cases**: Existing files, nested files, empty files
- **Error cases**: Non-existent files, permission issues
- **Edge cases**: Large files, binary files, special characters
- **Accumulation**: Multiple reads in sequence

#### RUN Directive Tests (Partitions)
- **Success cases**: Simple commands, complex commands with output
- **Error cases**: Invalid commands, failing commands
- **Output handling**: stdout, stderr, exit codes
- **Command types**: Test commands, build commands, validation commands

#### CHANGE Directive Tests (Partitions)
- **Success cases**: Own file modifications, content variations
- **Security boundaries**: Unauthorized file access prevention
- **Content types**: Empty content, large content, special characters
- **File paths**: Nested paths, complex filenames

#### FINISH Directive Tests (Partitions)
- **Message types**: Simple, complex, empty, special characters
- **Context preservation**: Maintaining state through completion
- **Integration**: Working with other directives

#### Context Management Tests (Partitions)
- **Initialization**: Fresh context state
- **State tracking**: Operations accumulation
- **Reset functionality**: Context cleanup
- **Persistence**: Export/import capabilities
- **Configuration**: Runtime settings changes

#### Error Handling Tests (Partitions)
- **Parsing errors**: Invalid directives, malformed syntax
- **Execution errors**: Runtime failures, permission issues
- **Recovery**: Graceful degradation

#### Integration Tests (Partitions)
- **Realistic workflows**: Multi-step development scenarios
- **Security enforcement**: File ownership boundaries
- **Cross-directive interactions**: State sharing between operations

### test_parser.py
Tests for the `CoderLanguageParser` class with 30+ test cases covering:

#### Parsing Success Cases (Partitions)
- **READ directives**: Simple files, paths, special characters
- **RUN directives**: Simple commands, complex commands, pipes
- **CHANGE directives**: Various content types, multiline content
- **FINISH directives**: Message variations, special characters

#### Multiple Directive Parsing (Partitions)
- **Mixed types**: Different directive combinations
- **Empty lines**: Whitespace handling
- **Comments**: Comment filtering
- **Complex workflows**: Real-world scenarios

#### Error Handling (Partitions)
- **Invalid directives**: Unknown commands
- **Malformed syntax**: Missing parameters, incorrect format
- **Empty input**: Edge case handling

#### String Processing (Partitions)
- **Escape sequences**: Quotes, newlines, tabs, backslashes
- **Unicode**: International character support
- **Long strings**: Large content handling

### test_ast.py
Tests for AST classes with 25+ test cases covering:

#### Data Classes (Partitions)
- **Target**: File targets, path handling, string representation
- **PromptField**: Message handling, special characters, complex content

#### Directive Classes (Partitions)
- **ReadDirective**: Creation, execution, context handling
- **RunDirective**: Command handling, context preservation
- **ChangeDirective**: Content management, file operations
- **FinishDirective**: Completion handling, message processing

#### Integration Tests (Partitions)
- **Workflow sequences**: Multi-directive interactions
- **Context preservation**: State management across operations
- **String representations**: Serialization and display

## Partitioning Strategy

The test suite uses systematic partitioning methods to ensure complete coverage:

### Input Partitioning
- **Valid inputs**: All supported directive formats and parameters
- **Invalid inputs**: Malformed syntax, missing parameters
- **Edge cases**: Empty strings, very long inputs, special characters
- **Boundary values**: File size limits, command length limits

### State Partitioning
- **Initial state**: Fresh interpreter instances
- **Intermediate states**: Partially completed workflows
- **Final states**: Completed tasks, error states
- **Context variations**: Different file ownership scenarios

### Output Partitioning
- **Success outputs**: Completed operations, valid results
- **Error outputs**: Parsing failures, execution failures
- **Partial outputs**: Interrupted operations, incomplete workflows

### Functional Partitioning
- **Core functionality**: Primary directive execution
- **Supporting functionality**: Context management, error handling
- **Integration functionality**: Multi-directive workflows

## Security Testing

Special focus on security boundaries:
- **File ownership enforcement**: Agents can only modify assigned files
- **Command execution safety**: Controlled terminal access
- **Context isolation**: Proper state management

## Performance Considerations

Tests validate:
- **Large file handling**: Reading substantial files
- **Multiple operations**: Sequence performance
- **Memory management**: Context cleanup
- **Error recovery**: Graceful failure handling

## Coverage Metrics

The test suite achieves comprehensive coverage through:
- **Line coverage**: All code paths executed
- **Branch coverage**: All conditional branches tested
- **Function coverage**: All public methods validated
- **Integration coverage**: Real-world usage scenarios

## Running the Tests

```bash
# Run all coder language tests
cd test/coder_language
python -m pytest -v

# Run specific test file
python -m pytest test_interpreter.py -v

# Run with coverage reporting
python -m pytest --cov=src.languages.coder_language --cov-report=html
```

## Test Maintenance

The test suite is designed for:
- **Easy extension**: Adding new test cases for new features
- **Clear organization**: Logical grouping of related tests
- **Maintainable structure**: Clear naming and documentation
- **CI/CD integration**: Automated testing on code changes

## Future Enhancements

Potential test suite improvements:
- **Property-based testing**: Automated input generation
- **Performance benchmarks**: Execution time monitoring
- **Integration testing**: Multi-agent scenarios
- **Stress testing**: High-load scenarios 