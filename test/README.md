# Testing Documentation

This directory contains comprehensive tests for the HMA-LLM-Software project.

## Test Structure

```
test/
├── agents/                    # Agent-related tests
│   ├── base_agent_test.py    # BaseAgent class tests
│   └── README.md             # Agent testing documentation
├── coder_language/           # Coder language tests
├── manager_language/         # Manager language tests
└── README.md                 # This file
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test/agents/base_agent_test.py

# Run with verbose output
python -m pytest -v

# Run specific test class
python -m pytest test/agents/base_agent_test.py::TestAgentInitialization

# Run specific test method
python -m pytest test/agents/base_agent_test.py::TestAgentInitialization::test_coder_agent_initialization
```

### Using the Test Runner Script

```bash
# Run default test suite
python scripts/run_tests.py

# Run with verbose output
python scripts/run_tests.py --verbose

# Run with coverage
python scripts/run_tests.py --coverage

# Run with HTML coverage report
python scripts/run_tests.py --coverage --html

# Run only integration tests
python scripts/run_tests.py --markers integration

# Exclude slow tests
python scripts/run_tests.py --exclude slow
```

### Coverage Reporting

```bash
# Generate coverage report
python -m pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html

# Generate XML coverage report (for CI/CD)
python -m pytest --cov=src --cov-report=xml
```

## Test Categories

### Unit Tests
- **Agent Initialization**: Tests for proper agent setup and configuration
- **File Operations**: Tests for file reading, memory management
- **Context Management**: Tests for context building and management
- **Task Processing**: Tests for task queue and API call handling

### Integration Tests
- **Complete Workflows**: End-to-end agent workflows
- **Manager-Child Interactions**: Hierarchical agent communication
- **File System Operations**: Real file system interactions

### Edge Cases
- **Error Handling**: Permission errors, missing files, etc.
- **Concurrent Operations**: Multiple prompts, stalled states
- **Boundary Conditions**: Empty states, maximum limits

## Test Fixtures

The test suite uses several fixtures to provide common test data:

- `temp_dir`: Temporary directory for file operations
- `mock_llm_client`: Mock LLM client for testing
- `sample_task`: Sample task message for testing
- `coder_agent`: Pre-configured coder agent
- `manager_agent`: Pre-configured manager agent

## Mock Objects

### MockLLMClient
A mock implementation of `BaseLLMClient` that:
- Tracks API call counts
- Records last prompt and context
- Returns configurable responses
- Supports both regular and structured responses

### ConcreteAgent
A concrete implementation of `BaseAgent` that:
- Implements abstract methods for testing
- Provides simple context string generation
- Allows testing of base functionality

## Test Patterns

### Async Testing
All async methods are tested using `pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_method():
    result = await some_async_method()
    assert result == expected_value
```

### Fixture Usage
Tests use fixtures for setup and teardown:

```python
def test_with_fixture(coder_agent, temp_dir):
    # Test implementation using fixtures
    pass
```

### Mocking
External dependencies are mocked:

```python
with patch.object(agent, 'api_call', new_callable=AsyncMock) as mock_api:
    await agent.process_task("test")
    mock_api.assert_called_once()
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Use fixtures to ensure proper cleanup of test resources
3. **Descriptive Names**: Test names should clearly describe what is being tested
4. **Assertions**: Use specific assertions that test one thing at a time
5. **Documentation**: Document complex test scenarios and edge cases

## Continuous Integration

The test suite is designed to run in CI/CD environments:

- All tests should pass without external dependencies
- Coverage reports are generated for quality metrics
- Tests are organized to run efficiently in parallel
- Mock objects eliminate external API dependencies

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in Python path
2. **Async Test Failures**: Check that `pytest-asyncio` is installed
3. **File Permission Errors**: Tests use temporary directories to avoid permission issues
4. **Mock Issues**: Ensure mocks are properly configured for async methods

### Debug Mode

Run tests with debug output:

```bash
python -m pytest -s --tb=long
```

This will show print statements and full tracebacks for debugging. 