"""
Comprehensive test suite for BaseAgent class.

This test suite covers:
- Agent initialization and configuration
- Activation and deactivation workflows
- Task processing and API calls
- File reading and memory management
- Context management
- Error handling and edge cases
- Manager vs Coder agent behavior
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

# Import the classes we're testing
from src.agents.base_agent import BaseAgent
from src.messages.protocol import TaskMessage, Task, MessageType
from src.llm.base import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing."""
    
    def __init__(self, responses: Dict[str, str] = None):
        self.responses = responses or {}
        self.call_count = 0
        self.last_prompt = None
        self.last_context = None
    
    async def generate_response(
        self, 
        prompt: str, 
        context: str = None,
        temperature: float = 0.7, 
        max_tokens: int = 1000
    ) -> str:
        """Mock response generation."""
        self.call_count += 1
        self.last_prompt = prompt
        self.last_context = context
        
        # Return predefined response or default
        return self.responses.get(prompt, f"Mock response {self.call_count}")
    
    async def generate_structured_response(
        self, 
        prompt: str, 
        schema: Dict[str, Any],
        context: str = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Mock structured response generation."""
        self.call_count += 1
        self.last_prompt = prompt
        self.last_context = context
        
        # Return a mock structured response
        return {"status": "success", "data": "mock_data"}


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing abstract methods."""
    
    async def get_context_string(self) -> str:
        """Get context string for LLM."""
        memory_contents = await self._get_memory_contents()
        structure = await self._get_codebase_structure_string()
        
        context_parts = [
            f"Codebase Structure:\n{structure}",
            f"Memory Files ({len(memory_contents)}):"
        ]
        
        for filename, content in memory_contents.items():
            context_parts.append(f"\n--- {filename} ---\n{content}")
        
        return "\n".join(context_parts)
    
    async def _process_response(self, response: str) -> None:
        """Process LLM response."""
        # Simple implementation for testing
        pass


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    task = Task(
        task_id="test_task_001",
        task_string="Create a simple calculator function"
    )
    return TaskMessage(
        message_type=MessageType.DELEGATION,
        sender_id="parent_agent",
        recipient_id="test_agent",
        timestamp=1234567890.0,
        message_id="msg_001",
        task=task
    )


@pytest.fixture
def coder_agent(temp_dir, mock_llm_client):
    """Create a coder agent for testing."""
    code_file = temp_dir / "calculator.py"
    code_file.write_text("# Calculator implementation")
    
    return ConcreteAgent(
        path=str(code_file),
        parent_path=str(temp_dir),
        llm_client=mock_llm_client
    )


@pytest.fixture
def manager_agent(temp_dir, mock_llm_client):
    """Create a manager agent for testing."""
    manager_dir = temp_dir / "src"
    manager_dir.mkdir()
    
    return ConcreteAgent(
        path=str(manager_dir),
        parent_path=str(temp_dir),
        children_paths=[str(manager_dir / "file1.py"), str(manager_dir / "file2.py")],
        llm_client=mock_llm_client
    )


class TestAgentInitialization:
    """Test agent initialization and configuration."""
    
    def test_coder_agent_initialization(self, coder_agent):
        """Test coder agent initialization."""
        assert coder_agent.is_coder
        assert not coder_agent.is_manager
        assert coder_agent.personal_file == coder_agent.path
        assert coder_agent.parent_path is not None
        assert len(coder_agent.children_paths) == 0
        assert not coder_agent.is_active
        assert coder_agent.active_task is None
        assert len(coder_agent.memory) == 0
        assert len(coder_agent.context) == 0
        assert len(coder_agent.prompt_queue) == 0
        assert not coder_agent.stall
    
    def test_manager_agent_initialization(self, manager_agent):
        """Test manager agent initialization."""
        assert manager_agent.is_manager
        assert not manager_agent.is_coder
        assert manager_agent.personal_file.name.endswith("_README.md")
        assert manager_agent.parent_path is not None
        assert len(manager_agent.children_paths) == 2
        assert not manager_agent.is_active
        assert manager_agent.active_task is None
        assert len(manager_agent.memory) == 0
        assert len(manager_agent.context) == 0
        assert len(manager_agent.prompt_queue) == 0
        assert not manager_agent.stall
    
    def test_agent_without_llm_client(self, temp_dir):
        """Test agent initialization without LLM client."""
        agent = ConcreteAgent(path=str(temp_dir / "test.py"))
        assert agent.llm_client is None
    
    def test_agent_with_custom_context_size(self, temp_dir, mock_llm_client):
        """Test agent with custom context size."""
        custom_size = 12000
        agent = ConcreteAgent(
            path=str(temp_dir / "test.py"),
            llm_client=mock_llm_client,
            max_context_size=custom_size
        )
        assert agent.max_context_size == custom_size
    
    def test_agent_path_resolution(self, temp_dir):
        """Test that agent paths are properly resolved."""
        relative_path = "test.py"
        agent = ConcreteAgent(path=relative_path)
        assert agent.path.is_absolute()
        assert agent.path.name == "test.py"


class TestAgentActivation:
    """Test agent activation and deactivation."""
    
    @pytest.mark.asyncio
    async def test_activate_agent(self, coder_agent, sample_task):
        """Test successful agent activation."""
        await coder_agent.activate(sample_task)
        
        assert coder_agent.is_active
        assert coder_agent.active_task == sample_task
    
    @pytest.mark.asyncio
    async def test_activate_already_active_agent(self, coder_agent, sample_task):
        """Test activation of already active agent."""
        await coder_agent.activate(sample_task)
        
        with pytest.raises(RuntimeError, match="already active"):
            await coder_agent.activate(sample_task)
    
    @pytest.mark.asyncio
    async def test_deactivate_agent(self, coder_agent, sample_task):
        """Test successful agent deactivation."""
        await coder_agent.activate(sample_task)
        await coder_agent.deactivate()
        
        assert not coder_agent.is_active
        assert coder_agent.active_task is None
        assert len(coder_agent.memory) == 0
        assert len(coder_agent.context) == 0
        assert len(coder_agent.prompt_queue) == 0
        assert not coder_agent.stall
    
    @pytest.mark.asyncio
    async def test_deactivate_with_active_children(self, manager_agent, sample_task):
        """Test deactivation with active children."""
        await manager_agent.activate(sample_task)
        manager_agent.active_children = ["child1", "child2"]
        
        with pytest.raises(RuntimeError, match="active children"):
            await manager_agent.deactivate()


class TestFileReading:
    """Test file reading and memory management."""
    
    @pytest.mark.asyncio
    async def test_read_file(self, coder_agent, temp_dir):
        """Test adding file to memory."""
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("Hello, World!")
        
        await coder_agent.read_file(str(test_file))
        
        assert "test_file.txt" in coder_agent.memory
        assert coder_agent.memory["test_file.txt"] == test_file.resolve()
    
    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, coder_agent):
        """Test reading non-existent file."""
        await coder_agent.read_file("nonexistent_file.txt")
        
        assert "nonexistent_file.txt" in coder_agent.memory
    
    @pytest.mark.asyncio
    async def test_get_memory_contents(self, coder_agent, temp_dir):
        """Test reading memory file contents."""
        test_file = temp_dir / "test_file.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)
        
        await coder_agent.read_file(str(test_file))
        contents = await coder_agent._get_memory_contents()
        
        assert "test_file.txt" in contents
        assert contents["test_file.txt"] == test_content
    
    @pytest.mark.asyncio
    async def test_get_memory_contents_nonexistent(self, coder_agent):
        """Test reading contents of non-existent file in memory."""
        await coder_agent.read_file("nonexistent_file.txt")
        contents = await coder_agent._get_memory_contents()
        
        assert "nonexistent_file.txt" in contents
        assert "[File does not exist:" in contents["nonexistent_file.txt"]


class TestContextManagement:
    """Test context and memory management."""
    
    @pytest.mark.asyncio
    async def test_load_context_includes_personal_file(self, coder_agent):
        """Test that personal file is always included in context."""
        await coder_agent._load_context()
        
        assert "personal_file" in coder_agent.memory
        assert coder_agent.memory["personal_file"] == coder_agent.personal_file
    
    @pytest.mark.asyncio
    async def test_get_codebase_structure_string(self, coder_agent, temp_dir):
        """Test codebase structure generation."""
        # Create a simple project structure
        (temp_dir / "src").mkdir()
        (temp_dir / "tests").mkdir()
        (temp_dir / "requirements.txt").write_text("pytest")
        (temp_dir / "src" / "main.py").write_text("# Main file")
        (temp_dir / "tests" / "test_main.py").write_text("# Test file")
        
        structure = await coder_agent._get_codebase_structure_string()
        
        assert "Project Structure" in structure
        assert "requirements.txt" in structure
        assert "src/" in structure
        assert "tests/" in structure
        assert "Current agent location" in structure
    
    @pytest.mark.asyncio
    async def test_get_context_string(self, coder_agent, temp_dir):
        """Test full context string generation."""
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("Test content")
        
        await coder_agent.read_file(str(test_file))
        context_string = await coder_agent.get_context_string()
        
        assert "Codebase Structure" in context_string
        assert "Memory Files" in context_string
        assert "test_file.txt" in context_string
        assert "Test content" in context_string


class TestTaskProcessing:
    """Test task processing and API calls."""
    
    @pytest.mark.asyncio
    async def test_process_task_adds_to_queue(self, coder_agent):
        """Test that process_task adds prompt to queue."""
        prompt = "Create a function"
        await coder_agent.process_task(prompt)
        
        assert len(coder_agent.prompt_queue) == 1
        assert coder_agent.prompt_queue[0] == prompt
    
    @pytest.mark.asyncio
    async def test_process_task_without_stall_calls_api(self, coder_agent, mock_llm_client):
        """Test that process_task calls API when not stalled."""
        prompt = "Create a function"
        
        with patch.object(coder_agent, 'api_call', new_callable=AsyncMock) as mock_api_call:
            await coder_agent.process_task(prompt)
            mock_api_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_task_with_stall_does_not_call_api(self, coder_agent):
        """Test that process_task doesn't call API when stalled."""
        coder_agent.stall = True
        prompt = "Create a function"
        
        with patch.object(coder_agent, 'api_call', new_callable=AsyncMock) as mock_api_call:
            await coder_agent.process_task(prompt)
            mock_api_call.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_api_call_with_llm_client(self, coder_agent, mock_llm_client):
        """Test API call with LLM client."""
        coder_agent.prompt_queue = ["Task 1", "Task 2"]
        
        await coder_agent.api_call()
        
        assert mock_llm_client.call_count == 1
        assert "1. Task 1" in mock_llm_client.last_prompt
        assert "2. Task 2" in mock_llm_client.last_prompt
        assert len(coder_agent.prompt_queue) == 0
        assert coder_agent.stall
    
    @pytest.mark.asyncio
    async def test_api_call_without_llm_client(self, coder_agent):
        """Test API call without LLM client."""
        coder_agent.llm_client = None
        coder_agent.prompt_queue = ["Task 1"]
        
        # Should not raise an exception
        await coder_agent.api_call()
        
        assert len(coder_agent.prompt_queue) == 0
        assert coder_agent.stall
    
    @pytest.mark.asyncio
    async def test_api_call_adds_to_context(self, coder_agent, mock_llm_client):
        """Test that API call adds response to context."""
        coder_agent.prompt_queue = ["Test prompt"]
        
        await coder_agent.api_call()
        
        assert len(coder_agent.context) == 1
        assert "Test prompt" in coder_agent.context
        assert coder_agent.context["Test prompt"] == "Mock response 1"


class TestAgentStatus:
    """Test agent status reporting."""
    
    def test_get_status_coder_agent(self, coder_agent):
        """Test status for coder agent."""
        status = coder_agent.get_status()
        
        assert status['agent_type'] == 'coder'
        assert status['path'] == str(coder_agent.path)
        assert status['personal_file'] == str(coder_agent.personal_file)
        assert status['is_active'] == False
        assert status['active_task'] == None
        assert status['memory_files'] == 0
        assert status['context_entries'] == 0
        assert status['prompt_queue_size'] == 0
        assert status['stall'] == False
        assert status['active_children'] == 0
    
    def test_get_status_manager_agent(self, manager_agent):
        """Test status for manager agent."""
        status = manager_agent.get_status()
        
        assert status['agent_type'] == 'manager'
        assert status['path'] == str(manager_agent.path)
        assert status['personal_file'] == str(manager_agent.personal_file)
        assert status['is_active'] == False
        assert status['active_task'] == None
        assert status['memory_files'] == 0
        assert status['context_entries'] == 0
        assert status['prompt_queue_size'] == 0
        assert status['stall'] == False
        assert status['active_children'] == 0
    
    def test_get_status_with_active_task(self, coder_agent, sample_task):
        """Test status with active task."""
        coder_agent.is_active = True
        coder_agent.active_task = sample_task
        coder_agent.memory['test.txt'] = Path('test.txt')
        coder_agent.context['prompt'] = 'response'
        coder_agent.prompt_queue = ['task1', 'task2']
        coder_agent.stall = True
        
        status = coder_agent.get_status()
        
        assert status['is_active'] == True
        assert status['active_task'] == str(sample_task)
        assert status['memory_files'] == 1
        assert status['context_entries'] == 1
        assert status['prompt_queue_size'] == 2
        assert status['stall'] == True


class TestAgentRepresentation:
    """Test agent string representation."""
    
    def test_repr_coder_agent(self, coder_agent):
        """Test string representation of coder agent."""
        repr_str = repr(coder_agent)
        
        assert "CoderAgent" in repr_str
        assert str(coder_agent.path) in repr_str
        assert "active=False" in repr_str
    
    def test_repr_manager_agent(self, manager_agent):
        """Test string representation of manager agent."""
        repr_str = repr(manager_agent)
        
        assert "ManagerAgent" in repr_str
        assert str(manager_agent.path) in repr_str
        assert "active=False" in repr_str
    
    def test_repr_active_agent(self, coder_agent):
        """Test string representation of active agent."""
        coder_agent.is_active = True
        repr_str = repr(coder_agent)
        
        assert "active=True" in repr_str


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_api_call_with_file_read_error(self, coder_agent, temp_dir):
        """Test API call when file reading fails."""
        # Create a file that will cause a permission error
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("Test content")
        
        await coder_agent.read_file(str(test_file))
        
        # Mock file reading to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            await coder_agent.api_call()
        
        # Should not raise an exception, should handle error gracefully
    
    @pytest.mark.asyncio
    async def test_get_codebase_structure_with_permission_error(self, coder_agent, temp_dir):
        """Test codebase structure generation with permission errors."""
        # Create a directory that will cause permission errors
        restricted_dir = temp_dir / "restricted"
        restricted_dir.mkdir()
        
        # Mock iterdir to raise PermissionError
        with patch.object(Path, 'iterdir', side_effect=PermissionError("Access denied")):
            structure = await coder_agent._get_codebase_structure_string()
            
            assert "Permission Denied" in structure
    
    def test_agent_with_nonexistent_path(self, mock_llm_client):
        """Test agent with non-existent path."""
        agent = ConcreteAgent(
            path="nonexistent_file.py",
            llm_client=mock_llm_client
        )
        
        assert agent.is_coder
        assert agent.personal_file.name == "nonexistent_file.py"
    
    @pytest.mark.asyncio
    async def test_multiple_prompt_processing(self, coder_agent, mock_llm_client):
        """Test processing multiple prompts in sequence."""
        prompts = ["Task 1", "Task 2", "Task 3"]
        
        for prompt in prompts:
            await coder_agent.process_task(prompt)
        
        # Should have made one API call with all prompts
        assert mock_llm_client.call_count == 1
        assert "1. Task 1" in mock_llm_client.last_prompt
        assert "2. Task 2" in mock_llm_client.last_prompt
        assert "3. Task 3" in mock_llm_client.last_prompt


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_task_workflow(self, coder_agent, sample_task, temp_dir):
        """Test complete task workflow from activation to completion."""
        # Create some test files
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("Test content")
        
        # Activate agent
        await coder_agent.activate(sample_task)
        assert coder_agent.is_active
        
        # Read files
        await coder_agent.read_file(str(test_file))
        assert "test_file.txt" in coder_agent.memory
        
        # Process task
        await coder_agent.process_task("Create a function")
        assert len(coder_agent.prompt_queue) == 0
        
        # Deactivate agent
        await coder_agent.deactivate()
        assert not coder_agent.is_active
        assert len(coder_agent.memory) == 0
    
    @pytest.mark.asyncio
    async def test_manager_with_children_workflow(self, manager_agent, sample_task):
        """Test manager agent workflow with children."""
        await manager_agent.activate(sample_task)
        
        # Simulate having active children
        manager_agent.active_children = ["child1"]
        
        # Should not be able to deactivate with active children
        with pytest.raises(RuntimeError):
            await manager_agent.deactivate()
        
        # Clear children and deactivate
        manager_agent.active_children = []
        await manager_agent.deactivate()
        assert not manager_agent.is_active


if __name__ == "__main__":
    pytest.main([__file__])
