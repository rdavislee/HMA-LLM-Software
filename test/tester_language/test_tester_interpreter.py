"""
Tests for TesterLanguageInterpreter.
Each test partition matches an interpreter operation and asserts both success and failure behaviours.
"""

from __future__ import annotations

import asyncio
from pathlib import Path as _P
import subprocess
import sys

import pytest

# Ensure the src package is importable
sys.path.insert(0, str(_P(__file__).parent.parent.parent))

from src import set_root_dir  # noqa: E402
from src.languages.tester_language.interpreter import TesterLanguageInterpreter, execute_directive  # noqa: E402
from src.languages.tester_language.ast import (  # noqa: E402
    ReadDirective,
    RunDirective,
    ChangeDirective,
    FinishDirective,
    PromptField,
)


class StubTesterAgent:
    """Minimal tester agent capturing interpreter callbacks."""

    def __init__(self):
        self.read_files: list[str] = []
        self.prompts: list[str] = []
        self.prompt_queue: list[str] = []
        self.personal_file = None
        self.final_result = None
        self.scratch_pad_cleaned = False
        self.parent = None
        self.parent_path = _P("/test/parent")

    # Hooks used by interpreter
    def read_file(self, path: str):
        self.read_files.append(path)

    def cleanup_scratch_pad(self):
        self.scratch_pad_cleaned = True

    async def api_call(self):
        """Process prompt queue for testing."""
        while self.prompt_queue:
            prompt = self.prompt_queue.pop(0)
            self.prompts.append(prompt)


class StubParentAgent:
    """Minimal parent agent for testing."""
    
    def __init__(self):
        self.prompt_queue: list[str] = []
        self.prompts: list[str] = []
        self.stall = False
    
    async def api_call(self):
        """Process prompt queue for testing."""
        while self.prompt_queue:
            prompt = self.prompt_queue.pop(0)
            self.prompts.append(prompt)


# ---------------------- Fixtures ----------------------

@pytest.fixture()
def workspace(tmp_path):
    """Isolated temp directory for file operations."""
    set_root_dir(str(tmp_path))  # Set the root directory for the interpreter
    # Add a project marker so _find_project_root works correctly
    (tmp_path / "requirements.txt").write_text("# test requirements")
    
    # Create scratch_pads directory
    scratch_pads_dir = tmp_path / "scratch_pads"
    scratch_pads_dir.mkdir(exist_ok=True)
    
    return tmp_path


@pytest.fixture()
def tester_agent(workspace):
    """Create a stub tester agent with scratch pad file."""
    agent = StubTesterAgent()
    
    # Create a mock scratch pad file
    scratch_pad_path = workspace / "scratch_pads" / "test_scratch.py"
    scratch_pad_path.write_text("# Test scratch pad\n")
    agent.personal_file = scratch_pad_path
    
    return agent


@pytest.fixture()
def tester_agent_with_parent(workspace):
    """Create a stub tester agent with parent agent."""
    agent = StubTesterAgent()
    parent = StubParentAgent()
    agent.parent = parent
    
    # Create a mock scratch pad file
    scratch_pad_path = workspace / "scratch_pads" / "test_scratch.py"
    scratch_pad_path.write_text("# Test scratch pad\n")
    agent.personal_file = scratch_pad_path
    
    return agent, parent


@pytest.fixture(autouse=True)
def patch_async(monkeypatch):
    """Patch asyncio.create_task to execute synchronously."""
    def sync_create_task(coro):
        try:
            loop = asyncio.get_running_loop()
            # If loop is already running, create a new thread to run the coroutine
            import concurrent.futures
            import threading
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        except RuntimeError:
            # No event loop running, safe to use run_until_complete
            return asyncio.get_event_loop().run_until_complete(coro)
    
    monkeypatch.setattr("asyncio.create_task", sync_create_task)


# ---------------------- READ TESTS ----------------------

def test_read_success(workspace, tester_agent):
    """Test successful READ directive execution."""
    # Create a test file
    test_file = workspace / "test_module.py"
    test_file.write_text("def hello():\n    return 'world'")

    execute_directive('READ "test_module.py"', agent=tester_agent)

    assert tester_agent.read_files == [str(test_file)]
    assert any("READ succeeded" in p for p in tester_agent.prompts)


def test_read_source_file(workspace, tester_agent):
    """Test READ directive with source file."""
    # Create source file
    src_dir = workspace / "src"
    src_dir.mkdir()
    src_file = src_dir / "auth" / "user.py"
    src_file.parent.mkdir(parents=True)
    src_file.write_text("class User:\n    pass")

    execute_directive('READ "src/auth/user.py"', agent=tester_agent)

    assert tester_agent.read_files == [str(src_file)]
    assert any("READ succeeded" in p for p in tester_agent.prompts)


def test_read_test_file(workspace, tester_agent):
    """Test READ directive with test file."""
    # Create test file
    tests_dir = workspace / "tests"
    tests_dir.mkdir()
    test_file = tests_dir / "test_auth.py"
    test_file.write_text("def test_user_creation():\n    assert True")

    execute_directive('READ "tests/test_auth.py"', agent=tester_agent)

    assert tester_agent.read_files == [str(test_file)]
    assert any("READ succeeded" in p for p in tester_agent.prompts)


def test_read_missing_file(workspace, tester_agent):
    """Test READ directive with missing file."""
    execute_directive('READ "missing_file.py"', agent=tester_agent)

    assert tester_agent.read_files == []
    assert any("READ failed" in p and "File not found" in p for p in tester_agent.prompts)


def test_read_no_agent(workspace):
    """Test READ directive with no agent."""
    execute_directive('READ "test.py"', agent=None)
    # Should not crash, but also should not do anything


def test_read_agent_without_read_file_method(workspace):
    """Test READ directive with agent that doesn't have read_file method."""
    class MinimalAgent:
        def __init__(self):
            self.prompt_queue = []
            self.prompts = []
        
        async def api_call(self):
            while self.prompt_queue:
                prompt = self.prompt_queue.pop(0)
                self.prompts.append(prompt)

    agent = MinimalAgent()
    test_file = workspace / "test.py"
    test_file.write_text("print('test')")

    execute_directive('READ "test.py"', agent=agent)

    assert any("READ failed" in p and "read_file method available" in p for p in agent.prompts)


# ---------------------- RUN TESTS ----------------------

def test_run_success(monkeypatch, workspace, tester_agent):
    """Test successful RUN directive execution."""
    class MockCompletedProcess:
        def __init__(self):
            self.returncode = 0
            self.stdout = "All tests passed\n"
            self.stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockCompletedProcess())

    execute_directive('RUN "python -m pytest"', agent=tester_agent)
    assert any("RUN succeeded" in p and "All tests passed" in p for p in tester_agent.prompts)


def test_run_pytest_command(monkeypatch, workspace, tester_agent):
    """Test RUN directive with pytest command."""
    class MockCompletedProcess:
        def __init__(self):
            self.returncode = 0
            self.stdout = "5 passed, 0 failed\n"
            self.stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockCompletedProcess())

    execute_directive('RUN "python -m pytest tests/ -v"', agent=tester_agent)
    assert any("RUN succeeded" in p and "5 passed" in p for p in tester_agent.prompts)


def test_run_coverage_command(monkeypatch, workspace, tester_agent):
    """Test RUN directive with coverage command."""
    class MockCompletedProcess:
        def __init__(self):
            self.returncode = 0
            self.stdout = "Coverage: 85%\n"
            self.stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockCompletedProcess())

    execute_directive('RUN "python -m pytest --cov=src"', agent=tester_agent)
    assert any("RUN succeeded" in p and "Coverage: 85%" in p for p in tester_agent.prompts)


def test_run_linting_command(monkeypatch, workspace, tester_agent):
    """Test RUN directive with linting command."""
    class MockCompletedProcess:
        def __init__(self):
            self.returncode = 0
            self.stdout = "No style violations found\n"
            self.stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockCompletedProcess())

    execute_directive('RUN "flake8 src/"', agent=tester_agent)
    assert any("RUN succeeded" in p and "No style violations" in p for p in tester_agent.prompts)


def test_run_invalid_command(workspace, tester_agent):
    """Test RUN directive with invalid command."""
    execute_directive('RUN "sudo rm -rf /"', agent=tester_agent)
    assert any("Invalid command" in p for p in tester_agent.prompts)


def test_run_command_failure(monkeypatch, workspace, tester_agent):
    """Test RUN directive with command that fails."""
    class MockCompletedProcess:
        def __init__(self):
            self.returncode = 1
            self.stdout = ""
            self.stderr = "Test failed: assertion error\n"

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockCompletedProcess())

    execute_directive('RUN "python -m pytest"', agent=tester_agent)
    assert any("RUN failed" in p and "assertion error" in p for p in tester_agent.prompts)


def test_run_command_failure_with_stdout_and_stderr(monkeypatch, workspace, tester_agent):
    """Test RUN directive with command that fails with both stdout and stderr."""
    class MockCompletedProcess:
        def __init__(self):
            self.returncode = 1
            self.stdout = "Test output\n"
            self.stderr = "Error message\n"

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockCompletedProcess())

    execute_directive('RUN "python -m pytest"', agent=tester_agent)
    assert any("RUN failed" in p and "Test output" in p and "Error message" in p for p in tester_agent.prompts)


def test_run_command_failure_stdout_only(monkeypatch, workspace, tester_agent):
    """Test RUN directive with command that fails with stdout only."""
    class MockCompletedProcess:
        def __init__(self):
            self.returncode = 1
            self.stdout = "Failed with output\n"
            self.stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockCompletedProcess())

    execute_directive('RUN "python -m pytest"', agent=tester_agent)
    assert any("RUN failed" in p and "Failed with output" in p for p in tester_agent.prompts)


def test_run_command_timeout(monkeypatch, workspace, tester_agent):
    """Test RUN directive with command that times out."""
    def mock_run(*args, **kwargs):
        raise subprocess.TimeoutExpired("pytest", timeout=300)

    monkeypatch.setattr("subprocess.run", mock_run)

    execute_directive('RUN "python -m pytest"', agent=tester_agent)
    assert any("RUN failed" in p and "timed out" in p for p in tester_agent.prompts)


# ---------------------- CHANGE TESTS ----------------------

def test_change_success(workspace, tester_agent):
    """Test successful CHANGE directive execution."""
    content = "import sys\nprint('Debug info')\nsys.exit(0)"
    
    execute_directive(f'CHANGE CONTENT="{content}"', agent=tester_agent)
    
    # Check that scratch pad was updated
    assert tester_agent.personal_file.read_text() == content
    assert any("CHANGE succeeded" in p for p in tester_agent.prompts)


def test_change_debug_code(workspace, tester_agent):
    """Test CHANGE directive with debug code."""
    debug_code = """
import pdb
def debug_function():
    pdb.set_trace()
    print('Debugging point reached')
    return True
"""
    
    execute_directive(f'CHANGE CONTENT="{debug_code}"', agent=tester_agent)
    
    written_content = tester_agent.personal_file.read_text()
    assert "import pdb" in written_content
    assert "debug_function" in written_content
    assert any("CHANGE succeeded" in p for p in tester_agent.prompts)


def test_change_test_helper(workspace, tester_agent):
    """Test CHANGE directive with test helper functions."""
    helper_code = """
def create_test_user():
    return {'id': 1, 'name': 'Test User', 'email': 'test@example.com'}

def assert_user_valid(user):
    assert 'id' in user
    assert 'name' in user
    assert 'email' in user
"""
    
    execute_directive(f'CHANGE CONTENT="{helper_code}"', agent=tester_agent)
    
    written_content = tester_agent.personal_file.read_text()
    assert "create_test_user" in written_content
    assert "assert_user_valid" in written_content


def test_change_empty_content(workspace, tester_agent):
    """Test CHANGE directive with empty content."""
    execute_directive('CHANGE CONTENT=""', agent=tester_agent)
    
    assert tester_agent.personal_file.read_text() == ""
    assert any("CHANGE succeeded" in p for p in tester_agent.prompts)


def test_change_no_personal_file(workspace):
    """Test CHANGE directive with agent that has no personal file."""
    agent = StubTesterAgent()
    agent.personal_file = None
    
    execute_directive('CHANGE CONTENT="test"', agent=agent)
    
    assert any("CHANGE failed" in p and "no scratch pad file" in p for p in agent.prompts)


def test_change_creates_parent_directories(workspace, tester_agent):
    """Test CHANGE directive creates parent directories if needed."""
    # Set personal file to a path with non-existent parent directories
    nested_path = workspace / "deep" / "nested" / "scratch.py"
    tester_agent.personal_file = nested_path
    
    content = "print('nested scratch pad')"
    execute_directive(f'CHANGE CONTENT="{content}"', agent=tester_agent)
    
    assert nested_path.exists()
    assert nested_path.read_text() == content
    assert any("CHANGE succeeded" in p for p in tester_agent.prompts)


# ---------------------- FINISH TESTS ----------------------

def test_finish_success(workspace, tester_agent):
    """Test successful FINISH directive execution."""
    execute_directive('FINISH PROMPT="Testing completed successfully"', agent=tester_agent)
    
    assert tester_agent.scratch_pad_cleaned is True
    assert tester_agent.final_result == "Testing completed successfully"


def test_finish_with_parent(workspace, tester_agent_with_parent):
    """Test FINISH directive with parent agent."""
    tester_agent, parent_agent = tester_agent_with_parent
    
    execute_directive('FINISH PROMPT="Analysis complete"', agent=tester_agent)
    
    assert tester_agent.scratch_pad_cleaned is True
    assert any("Tester agent completed" in p and "Analysis complete" in p for p in parent_agent.prompts)


def test_finish_cleanup_without_cleanup_method(workspace):
    """Test FINISH directive with agent that doesn't have cleanup method."""
    class MinimalTesterAgent:
        def __init__(self):
            self.prompt_queue = []
            self.prompts = []
            self.personal_file = None
            self.parent = None
        
        async def api_call(self):
            while self.prompt_queue:
                prompt = self.prompt_queue.pop(0)
                self.prompts.append(prompt)

    agent = MinimalTesterAgent()
    
    execute_directive('FINISH PROMPT="Done"', agent=agent)
    
    # Should not crash and should set final_result
    assert hasattr(agent, 'final_result')
    assert agent.final_result == "Done"


def test_finish_test_results_summary(workspace, tester_agent):
    """Test FINISH directive with comprehensive test results."""
    results = "Testing complete: 15 tests passed, 2 failed, 1 skipped. Coverage: 85%"
    
    execute_directive(f'FINISH PROMPT="{results}"', agent=tester_agent)
    
    assert tester_agent.scratch_pad_cleaned is True
    assert tester_agent.final_result == results


def test_finish_performance_analysis(workspace, tester_agent):
    """Test FINISH directive with performance analysis results."""
    analysis = "Performance analysis: avg response 45ms, max 120ms, 99th percentile 98ms"
    
    execute_directive(f'FINISH PROMPT="{analysis}"', agent=tester_agent)
    
    assert tester_agent.scratch_pad_cleaned is True
    assert tester_agent.final_result == analysis


# ---------------------- ERROR HANDLING TESTS ----------------------

def test_execute_directive_parsing_error(workspace, tester_agent):
    """Test execute_directive with parsing error."""
    execute_directive('INVALID "directive"', agent=tester_agent)
    
    assert any("PARSING FAILED" in p for p in tester_agent.prompts)


def test_execute_directive_no_agent(workspace):
    """Test execute_directive with no agent."""
    # Should not crash
    execute_directive('READ "test.py"', agent=None)


def test_interpreter_exception_handling(workspace, tester_agent):
    """Test interpreter exception handling during directive execution."""
    # Mock a method to raise an exception
    original_read_file = tester_agent.read_file
    
    def failing_read_file(path):
        raise Exception("Simulated read failure")
    
    tester_agent.read_file = failing_read_file
    
    # Create test file so it exists
    test_file = workspace / "test.py"
    test_file.write_text("print('test')")
    
    execute_directive('READ "test.py"', agent=tester_agent)
    
    assert any("Exception during execution" in p for p in tester_agent.prompts)
    
    # Restore original method
    tester_agent.read_file = original_read_file


# ---------------------- INTEGRATION TESTS ----------------------

def test_complete_testing_workflow(monkeypatch, workspace, tester_agent):
    """Test complete testing workflow with multiple directives."""
    # Create test files
    src_file = workspace / "src" / "calculator.py"
    src_file.parent.mkdir(parents=True)
    src_file.write_text("def add(a, b):\n    return a + b")
    
    test_file = workspace / "tests" / "test_calculator.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_add():\n    assert add(2, 3) == 5")
    
    # Mock subprocess for RUN commands
    class MockCompletedProcess:
        def __init__(self, stdout="Tests passed", stderr="", returncode=0):
            self.stdout = stdout
            self.stderr = stderr
            self.returncode = returncode
    
    run_results = [
        MockCompletedProcess("5 passed, 0 failed"),  # First pytest run
        MockCompletedProcess("Debug output"),        # Debug script run
        MockCompletedProcess("Coverage: 90%")        # Coverage run
    ]
    
    def mock_run(*args, **kwargs):
        if run_results:
            return run_results.pop(0)
        else:
            return MockCompletedProcess("Default output")
    
    monkeypatch.setattr("subprocess.run", mock_run)
    
    # Execute workflow
    execute_directive('READ "src/calculator.py"', agent=tester_agent)
    execute_directive('READ "tests/test_calculator.py"', agent=tester_agent)
    execute_directive('RUN "python -m pytest tests/"', agent=tester_agent)
    execute_directive('CHANGE CONTENT="print(\'Debug: testing calculator\')"', agent=tester_agent)
    execute_directive('RUN "python -c \\"exec(open(\'test_scratch.py\').read())\\"', agent=tester_agent)
    execute_directive('RUN "python -m pytest --cov=src"', agent=tester_agent)
    execute_directive('FINISH PROMPT="Calculator testing complete - all tests pass"', agent=tester_agent)
    
    # Verify results
    assert len(tester_agent.read_files) == 2
    assert str(src_file) in tester_agent.read_files
    assert str(test_file) in tester_agent.read_files
    
    assert any("5 passed" in p for p in tester_agent.prompts)
    assert any("Debug output" in p for p in tester_agent.prompts)
    assert any("Coverage: 90%" in p for p in tester_agent.prompts)
    
    assert "Debug: testing calculator" in tester_agent.personal_file.read_text()
    assert tester_agent.scratch_pad_cleaned is True
    assert tester_agent.final_result == "Calculator testing complete - all tests pass"


def test_error_recovery_workflow(workspace, tester_agent):
    """Test workflow with errors and recovery."""
    # Try to read non-existent file
    execute_directive('READ "missing.py"', agent=tester_agent)
    assert any("READ failed" in p for p in tester_agent.prompts)
    
    # Try invalid command
    execute_directive('RUN "invalid_command"', agent=tester_agent)
    assert any("Invalid command" in p for p in tester_agent.prompts)
    
    # Successful operations should still work
    execute_directive('CHANGE CONTENT="# Recovery test"', agent=tester_agent)
    assert any("CHANGE succeeded" in p for p in tester_agent.prompts)
    assert "# Recovery test" in tester_agent.personal_file.read_text()
    
    # Finish should work normally
    execute_directive('FINISH PROMPT="Completed despite errors"', agent=tester_agent)
    assert tester_agent.scratch_pad_cleaned is True
    assert tester_agent.final_result == "Completed despite errors"


# ---------------------- ASYNC BEHAVIOR TESTS ----------------------

@pytest.mark.asyncio
async def test_async_prompt_handling(workspace, tester_agent):
    """Test async prompt handling behavior."""
    # Create an agent that tracks async calls
    class AsyncTrackingAgent(StubTesterAgent):
        def __init__(self):
            super().__init__()
            self.api_call_count = 0
        
        async def api_call(self):
            self.api_call_count += 1
            await super().api_call()
    
    agent = AsyncTrackingAgent()
    agent.personal_file = tester_agent.personal_file
    
    # Execute directive that should trigger async call
    execute_directive('READ "nonexistent.py"', agent=agent)
    
    # Verify async call was made
    assert agent.api_call_count == 1
    assert len(agent.prompts) > 0 