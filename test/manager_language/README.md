# Manager Language Test Suite

This directory contains a comprehensive test suite for the Manager Language implementation, using partitioning methods to ensure complete coverage of all manager agent capabilities.

## Overview

The Manager Language is designed for autonomous agents that manage folders and coordinate work within a codebase. The test suite validates all seven core directives:

- **CREATE**: Create files and folders
- **DELETE**: Delete files and folders
- **READ**: Read files and list folder contents
- **DELEGATE**: Delegate tasks to other agents
- **FINISH**: Complete the task and report results
- **WAIT**: Wait for other operations to complete
- **RUN**: Execute terminal commands

## Test Files

### test_manager_interpreter.py
Comprehensive tests for the `ManagerLanguageInterpreter` class with 30+ test cases covering:

#### CREATE Directive Tests (Partitions)
- **Success cases**: File creation, folder creation, nested structures
- **Error cases**: Existing files/folders, permission issues, invalid paths
- **Edge cases**: Empty names, special characters, deep nesting
- **Accumulation**: Multiple creations in sequence

#### DELETE Directive Tests (Partitions)
- **Success cases**: File deletion, folder deletion, recursive deletion
- **Error cases**: Non-existent items, permission issues, locked files
- **Safety checks**: Confirmation of deletion, cleanup verification
- **Dependency handling**: Files within folders, nested structures

#### READ Directive Tests (Partitions)
- **File reading**: Existing files, empty files, large files
- **Folder listing**: Empty folders, populated folders, nested structures
- **Error cases**: Non-existent items, permission issues
- **Content handling**: Binary files, text files, special characters

#### DELEGATE Directive Tests (Partitions)
- **File delegation**: Single file tasks, multiple file tasks
- **Folder delegation**: Module creation, structure setup
- **Prompt variations**: Simple prompts, complex prompts, special characters
- **Task tracking**: Delegation logging, completion tracking

#### FINISH Directive Tests (Partitions)
- **Message types**: Simple, complex, empty, special characters
- **Context preservation**: Maintaining state through completion
- **Integration**: Working with other directives

#### WAIT Directive Tests (Partitions)
- **Synchronization**: Waiting for delegations, waiting for operations
- **State management**: Proper waiting state, resumption handling
- **Integration**: Coordination with other agents

#### RUN Directive Tests (Partitions)
- **Simple commands**: Basic command execution with output
- **Complex commands**: Commands with arguments and pipes
- **Failing commands**: Error handling for failed commands
- **Multiple commands**: Sequential command execution

#### Context Management Tests (Partitions)
- **Initialization**: Fresh context state
- **State tracking**: Operations accumulation, delegation tracking
- **Reset functionality**: Context cleanup
- **Persistence**: Export/import capabilities
- **Configuration**: Runtime settings changes

#### Error Handling Tests (Partitions)
- **Parsing errors**: Invalid directives, malformed syntax
- **Execution errors**: Runtime failures, permission issues
- **Recovery**: Graceful degradation, error reporting

#### Integration Tests (Partitions)
- **Realistic workflows**: Multi-step project scenarios
- **Security enforcement**: File system boundaries
- **Cross-directive interactions**: State sharing between operations

### test_manager_parser.py
Tests for the `ManagerLanguageParser` class with 40+ test cases covering:

#### Parsing Success Cases (Partitions)
- **CREATE directives**: File creation, folder creation, path variations
- **DELETE directives**: File deletion, folder deletion, recursive options
- **READ directives**: File reading, folder listing, path handling
- **DELEGATE directives**: File delegation, folder delegation, prompt variations
- **FINISH directives**: Message variations, special characters
- **WAIT directives**: Simple wait, conditional wait
- **RUN directives**: Simple commands, complex commands, escaped characters

#### Multiple Directive Parsing (Partitions)
- **Mixed types**: Different directive combinations
- **Empty lines**: Whitespace handling
- **Comments**: Comment filtering
- **Complex workflows**: Real-world project scenarios

#### Error Handling (Partitions)
- **Invalid directives**: Unknown commands
- **Malformed syntax**: Missing parameters, incorrect format
- **Empty input**: Edge case handling

#### String Processing (Partitions)
- **Escape sequences**: Quotes, newlines, tabs, backslashes
- **Unicode**: International character support
- **Long strings**: Large content handling
- **Path handling**: Windows paths, Unix paths, relative paths

### test_manager_ast.py
Tests for AST classes with 80+ test cases covering:

#### Data Classes (Partitions)
- **Target**: File targets, folder targets, path handling, string representation
- **PromptField**: Message handling, special characters, complex content
- **DelegateItem**: Individual delegation items, task specifications

#### Directive Classes (Partitions)
- **CreateDirective**: File creation, folder creation, context handling
- **DeleteDirective**: File deletion, folder deletion, safety checks
- **ReadDirective**: File reading, folder listing, content processing
- **DelegateDirective**: Task delegation, prompt management, tracking
- **FinishDirective**: Completion handling, message processing
- **WaitDirective**: Synchronization, state management
- **RunDirective**: Command execution, output handling

#### AST Node Classes (Partitions)
- **ActionNode**: Action representation and visitor pattern
- **TargetNode**: Target representation for files and folders
- **PromptFieldNode**: Prompt field representation
- **ParamSetNode**: Parameter set handling and agent selection
- **WaitDirectiveNode**: Wait directive representation
- **DirectiveNode**: Complete directive representation

#### Integration Tests (Partitions)
- **Workflow sequences**: Multi-directive interactions
- **Context preservation**: State management across operations
- **String representations**: Serialization and display
- **Visitor pattern**: AST traversal and processing

## Partitioning Strategy

The test suite uses systematic partitioning methods to ensure complete coverage:

### Input Partitioning
- **Valid inputs**: All supported directive formats and parameters
- **Invalid inputs**: Malformed syntax, missing parameters
- **Edge cases**: Empty strings, very long inputs, special characters
- **Boundary values**: File size limits, path length limits

### State Partitioning
- **Initial state**: Fresh interpreter instances
- **Intermediate states**: Partially completed workflows
- **Final states**: Completed tasks, error states
- **Context variations**: Different file system scenarios

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
- **File system safety**: Controlled file operations
- **Path validation**: Prevention of directory traversal
- **Permission enforcement**: Proper access control
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
# Run all manager language tests
cd test/manager_language
python -m pytest -v

# Run specific test file
python -m pytest test_manager_interpreter.py -v

# Run with coverage reporting
python -m pytest --cov=src.languages.manager_language --cov-report=html
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
- **File system mocking**: Isolated testing environments 