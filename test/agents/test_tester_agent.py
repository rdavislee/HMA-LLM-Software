"""
Tests for TesterAgent.
Tests cover initialization, scratch pad management, API calls, and integration with parent agents.
"""

import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import pytest
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src import set_root_dir
from src.agents.tester_agent import TesterAgent
from src.agents.base_agent import BaseAgent
from src.llm.base import BaseLLMClient


class DummyLLMClient(BaseLLMClient):
    """A no-op stub for BaseLLMClient that simply echoes prompts."""
    
    def __init__(self):
        super().__init__()
    
    @property
    def supports_system_role(self) -> bool:
        return True
    
    async def generate_response(self, messages, system_prompt=None):
        return "FINISH PROMPT=\"Test completed\""
    
    async def generate_structured_response(self, messages, schema, system_prompt=None, temperature=0.7):
        return {"result": "test"}


class DummyParentAgent(BaseAgent):
    """Dummy parent agent for testing."""
    
    def __init__(self, path: str):
        super().__init__(path)
        self.prompt_queue = []
        self.prompts = []
    
    async def api_call(self):
        # Process prompts
        while self.prompt_queue:
            prompt = self.prompt_queue.pop(0)
            self.prompts.append(prompt)


# ---------------------- Fixtures ----------------------

@pytest.fixture()
def workspace(tmp_path):
    """Isolated temp directory for testing."""
    set_root_dir(str(tmp_path))
    (tmp_path / "requirements.txt").write_text("# test requirements")
    return tmp_path


@pytest.fixture()
def parent_agent(workspace):
    """Create a dummy parent agent."""
    return DummyParentAgent(str(workspace / "src" / "module.py"))


@pytest.fixture()
def llm_client():
    """Create a dummy LLM client."""
    return DummyLLMClient()


# ---------------------- Initialization Tests ----------------------

def test_tester_agent_creation(workspace, parent_agent, llm_client):
    """Test basic TesterAgent creation."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path),
        llm_client=llm_client
    )
    
    assert agent.parent == parent_agent
    assert agent.parent_path == parent_agent.path
    assert agent.llm_client == llm_client
    assert agent.personal_file is not None
    assert agent.personal_file.exists()


def test_tester_agent_creation_without_llm(workspace, parent_agent):
    """Test TesterAgent creation without LLM client."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    assert agent.parent == parent_agent
    assert agent.llm_client is None
    assert agent.personal_file is not None


def test_tester_agent_inherits_ephemeral_agent(workspace, parent_agent):
    """Test that TesterAgent properly inherits from EphemeralAgent."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    # Check ephemeral agent attributes
    assert hasattr(agent, 'parent')
    assert hasattr(agent, 'parent_path')
    assert hasattr(agent, 'stall')
    assert hasattr(agent, 'prompt_queue')
    assert hasattr(agent, 'memory')
    assert hasattr(agent, 'context')
    assert hasattr(agent, 'active_task')
    
    # Check methods
    assert hasattr(agent, 'process_task')
    assert hasattr(agent, 'read_file')
    assert hasattr(agent, '_get_memory_contents')
    assert hasattr(agent, '_get_codebase_structure_string')


# ---------------------- Scratch Pad Tests ----------------------

def test_scratch_pad_creation(workspace, parent_agent):
    """Test scratch pad file creation."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    scratch_pad = agent.personal_file
    assert scratch_pad is not None
    assert scratch_pad.exists()
    assert scratch_pad.parent.name == "scratch_pads"
    assert "_scratch_" in scratch_pad.name and scratch_pad.name.endswith(".py")
    
    # Check initial content
    content = scratch_pad.read_text()
    assert "# Tester Agent Scratch Pad" in content
    assert str(parent_agent.path) in content
    assert "def debug_helper():" in content


def test_scratch_pad_naming_file_parent(workspace, parent_agent):
    """Test scratch pad naming for file-based parent."""
    # Parent is a file
    file_parent = workspace / "src" / "auth" / "user.py"
    file_parent.parent.mkdir(parents=True)
    file_parent.write_text("# user module")
    
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(file_parent)
    )
    
    scratch_pad = agent.personal_file
    expected_name = "src.auth.user.py_scratch_0.py"
    assert scratch_pad.name == expected_name


def test_scratch_pad_naming_directory_parent(workspace, parent_agent):
    """Test scratch pad naming for directory-based parent."""
    # Parent is a directory
    dir_parent = workspace / "src" / "auth"
    dir_parent.mkdir(parents=True)
    
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(dir_parent)
    )
    
    scratch_pad = agent.personal_file
    expected_name = "src.auth_manager_scratch_0.py"
    assert scratch_pad.name == expected_name


def test_scratch_pad_fallback_naming(workspace, parent_agent):
    """Test scratch pad naming fallback when path is not relative to ROOT_DIR."""
    # Use absolute path outside ROOT_DIR
    external_path = Path("/tmp/external/file.py")
    
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(external_path)
    )
    
    scratch_pad = agent.personal_file
    assert scratch_pad.name == "tester_scratch_0.py"


def test_multiple_testers_unique_naming(workspace, parent_agent):
    """Test that multiple tester agents from the same parent get unique numbered names."""
    # Parent is a file
    file_parent = workspace / "src" / "auth" / "user.py"
    file_parent.parent.mkdir(parents=True)
    file_parent.write_text("# user module")
    
    # Create first tester agent
    agent1 = TesterAgent(
        parent=parent_agent,
        parent_path=str(file_parent)
    )
    
    # Create second tester agent from same parent
    agent2 = TesterAgent(
        parent=parent_agent,
        parent_path=str(file_parent)
    )
    
    # Create third tester agent from same parent
    agent3 = TesterAgent(
        parent=parent_agent,
        parent_path=str(file_parent)
    )
    
    # Check that they have different numbered names
    assert agent1.personal_file.name == "src.auth.user.py_scratch_0.py"
    assert agent2.personal_file.name == "src.auth.user.py_scratch_1.py"
    assert agent3.personal_file.name == "src.auth.user.py_scratch_2.py"
    
    # Verify all files exist
    assert agent1.personal_file.exists()
    assert agent2.personal_file.exists()
    assert agent3.personal_file.exists()
    
    # Cleanup one and create another to test number reuse
    agent2.cleanup_scratch_pad()
    
    agent4 = TesterAgent(
        parent=parent_agent,
        parent_path=str(file_parent)
    )
    
    # Should reuse the lowest available number (1)
    assert agent4.personal_file.name == "src.auth.user.py_scratch_1.py"


def test_scratch_pad_memory_addition(workspace, parent_agent):
    """Test that scratch pad is added to agent memory."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    scratch_pad_name = agent.personal_file.name
    assert scratch_pad_name in agent.memory
    assert agent.memory[scratch_pad_name] == agent.personal_file


def test_scratch_pad_creation_failure(workspace, parent_agent, monkeypatch):
    """Test scratch pad creation failure handling."""
    # Mock ROOT_DIR to None to simulate failure
    monkeypatch.setattr("src.ROOT_DIR", None)
    
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    assert agent.personal_file is None


# ---------------------- Cleanup Tests ----------------------

def test_cleanup_scratch_pad_success(workspace, parent_agent):
    """Test successful scratch pad cleanup."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    scratch_pad = agent.personal_file
    assert scratch_pad.exists()
    
    agent.cleanup_scratch_pad()
    
    assert not scratch_pad.exists()


def test_cleanup_scratch_pad_no_file(workspace, parent_agent):
    """Test cleanup when no scratch pad file exists."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    # Remove the scratch pad file
    agent.personal_file.unlink()
    
    # Should not raise exception
    agent.cleanup_scratch_pad()


def test_cleanup_scratch_pad_none(workspace, parent_agent):
    """Test cleanup when personal_file is None."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    agent.personal_file = None
    
    # Should not raise exception
    agent.cleanup_scratch_pad()


def test_cleanup_scratch_pad_permission_error(workspace, parent_agent, monkeypatch):
    """Test cleanup with permission error."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    # Mock the pathlib.Path.unlink method to raise permission error
    import pathlib
    original_unlink = pathlib.Path.unlink
    
    def mock_unlink(self):
        if str(self) == str(agent.personal_file):
            raise PermissionError("Cannot delete file")
        return original_unlink(self)
    
    monkeypatch.setattr(pathlib.Path, "unlink", mock_unlink)
    
    # Should not raise exception but should handle error
    agent.cleanup_scratch_pad()


# ---------------------- API Call Tests ----------------------

@pytest.mark.asyncio
async def test_api_call_with_system_role_support(workspace, parent_agent, llm_client):
    """Test API call with LLM client that supports system role."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path),
        llm_client=llm_client
    )
    
    agent.prompt_queue.append("Test the authentication module")
    
    await agent.api_call()
    
    assert agent.stall is False  # Should be unstalled after api_call
    assert len(agent.context) == 1
    assert agent.context[0].prompt == "Test the authentication module"
    assert agent.context[0].response == 'FINISH PROMPT="Test completed"'


@pytest.mark.asyncio
async def test_api_call_without_system_role_support(workspace, parent_agent):
    """Test API call with LLM client that doesn't support system role."""
    class NoSystemRoleLLMClient(DummyLLMClient):
        def __init__(self):
            super().__init__()
        
        @property
        def supports_system_role(self) -> bool:
            return False
        
        async def generate_response(self, prompt):
            return "FINISH PROMPT=\"Test completed without system role\""
        
        async def generate_structured_response(self, messages, schema, system_prompt=None, temperature=0.7):
            return {"result": "test_no_system"}
    
    llm_client = NoSystemRoleLLMClient()
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path),
        llm_client=llm_client
    )
    
    agent.prompt_queue.append("Test the module")
    
    await agent.api_call()
    
    assert len(agent.context) == 1
    assert "Test completed without system role" in agent.context[0].response


@pytest.mark.asyncio
async def test_api_call_without_llm_client(workspace, parent_agent):
    """Test API call without LLM client."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    agent.prompt_queue.append("Test prompt")
    
    await agent.api_call()
    
    # Should handle gracefully when no LLM client
    assert agent.stall is True  # Remains stalled when no LLM
    assert len(agent.context) == 0


def test_api_call_template_loading(workspace, parent_agent, llm_client):
    """Test that API call properly loads templates and configurations."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path),
        llm_client=llm_client
    )
    
    # Check that Jinja environment is set up
    assert agent.jinja_env is not None
    
    # Check template loading (these should not raise exceptions)
    try:
        system_template = agent.jinja_env.get_template('system_template.j2')
        tester_template = agent.jinja_env.get_template('tester_template.j2')
        assert system_template is not None
        assert tester_template is not None
    except Exception as e:
        pytest.fail(f"Template loading failed: {e}")


# ---------------------- Memory and Context Tests ----------------------

def test_memory_contents_includes_scratch_pad(workspace, parent_agent):
    """Test that memory contents include the scratch pad."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    memory_contents = agent._get_memory_contents()
    
    scratch_pad_name = agent.personal_file.name
    assert scratch_pad_name in memory_contents
    assert "# Tester Agent Scratch Pad" in memory_contents[scratch_pad_name]


def test_read_file_adds_to_memory(workspace, parent_agent):
    """Test that read_file method adds files to memory."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    # Create a test file
    test_file = workspace / "test_module.py"
    test_file.write_text("def test_function():\n    pass")
    
    agent.read_file(str(test_file))
    
    assert test_file.name in agent.memory
    assert agent.memory[test_file.name] == test_file
    
    memory_contents = agent._get_memory_contents()
    assert test_file.name in memory_contents
    assert "def test_function():" in memory_contents[test_file.name]


def test_codebase_structure_string(workspace, parent_agent):
    """Test codebase structure string generation."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    # Create some test structure
    (workspace / "src" / "module.py").parent.mkdir(parents=True)
    (workspace / "src" / "module.py").write_text("# module")
    (workspace / "tests" / "test_module.py").parent.mkdir(parents=True)
    (workspace / "tests" / "test_module.py").write_text("# test")
    
    structure = agent._get_codebase_structure_string()
    
    assert workspace.name in structure
    assert "src/" in structure
    assert "tests/" in structure
    assert "module.py" in structure
    assert "test_module.py" in structure


# ---------------------- Integration Tests ----------------------

@pytest.mark.asyncio
async def test_process_task_integration(workspace, parent_agent, llm_client):
    """Test complete process_task integration."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path),
        llm_client=llm_client
    )
    
    await agent.process_task("Analyze the authentication system")
    
    assert len(agent.prompt_queue) == 0  # Should be processed
    assert len(agent.context) == 1
    assert "Analyze the authentication system" in agent.context[0].prompt


def test_status_reporting(workspace, parent_agent):
    """Test agent status reporting."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    status = agent.get_status()
    
    assert status['agent_type'] == 'ephemeral'
    assert status['parent_path'] == str(parent_agent.path)
    assert status['parent_type'] in ['manager', 'coder']
    assert 'memory_files' in status
    assert 'context_entries' in status
    assert 'prompt_queue_size' in status
    assert 'stall' in status


def test_string_representation(workspace, parent_agent):
    """Test agent string representation."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    repr_str = repr(agent)
    assert "EphemeralAgent" in repr_str
    assert str(parent_agent.path) in repr_str


# ---------------------- Error Handling Tests ----------------------

@pytest.mark.asyncio
async def test_api_call_exception_handling(workspace, parent_agent):
    """Test API call exception handling through process_task."""
    class FailingLLMClient(DummyLLMClient):
        async def generate_response(self, messages, system_prompt=None):
            raise Exception("LLM failure")
        
        async def generate_structured_response(self, messages, schema, system_prompt=None, temperature=0.7):
            raise Exception("Structured LLM failure")
    
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path),
        llm_client=FailingLLMClient()
    )
    
    # Should not raise exception when using process_task (has exception handling)
    await agent.process_task("Test prompt")
    
    # Should handle error gracefully - prompt queue should contain error message
    assert "Exception during api_call" in "\n".join(agent.prompt_queue)


def test_scratch_pad_creation_io_error(workspace, parent_agent, monkeypatch):
    """Test scratch pad creation with I/O error."""
    import builtins
    original_open = builtins.open
    
    def mock_open(*args, **kwargs):
        if len(args) > 0 and 'scratch_pads' in str(args[0]) and len(args) > 1 and 'w' in str(args[1]):
            raise IOError("Cannot write file")
        return original_open(*args, **kwargs)
    
    monkeypatch.setattr(builtins, 'open', mock_open)
    
    # Should handle the error gracefully
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path)
    )
    
    # Agent should still be created even if scratch pad creation fails
    assert agent is not None


# ---------------------- Edge Cases ----------------------

def test_empty_prompt_queue_api_call(workspace, parent_agent, llm_client):
    """Test API call with empty prompt queue."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path),
        llm_client=llm_client
    )
    
    # Don't add any prompts
    assert len(agent.prompt_queue) == 0
    
    # Should handle empty queue gracefully
    asyncio.run(agent.api_call())


def test_multiple_prompts_in_queue(workspace, parent_agent, llm_client):
    """Test API call with multiple prompts in queue."""
    agent = TesterAgent(
        parent=parent_agent,
        parent_path=str(parent_agent.path),
        llm_client=llm_client
    )
    
    agent.prompt_queue.extend([
        "First prompt",
        "Second prompt",
        "Third prompt"
    ])
    
    asyncio.run(agent.api_call())
    
    # All prompts should be joined and processed
    assert len(agent.context) == 1
    combined_prompt = agent.context[0].prompt
    assert "First prompt" in combined_prompt
    assert "Second prompt" in combined_prompt
    assert "Third prompt" in combined_prompt 