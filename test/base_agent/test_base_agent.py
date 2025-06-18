"""
Test suite for the base agent system.
"""

import asyncio
import tempfile
import shutil
import uuid
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import pytest
import subprocess

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent, ALLOWED_COMMANDS, MAX_CONTEXT_DEPTH, DEFAULT_MAX_CONTEXT_SIZE
from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.messages.protocol import TaskMessage, MessageType, TaskType, ResultMessage, Message
from src.llm.base import BaseLLMClient

# Create a concrete implementation of BaseAgent for testing
class TestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing purposes."""

    async def process_task(self, task: TaskMessage):
        """Simple implementation that returns task content."""
        return f"Processed: {task.content}"
    

class TestBaseAgent:
    """Test suite for BaseAgent functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        client = MagicMock(spec=BaseLLMClient)
        client.generate_response = AsyncMock(return_value="Mock LLM response")
        return client
    
    @pytest.fixture
    def test_file(self, temp_dir):
        """Create a test file."""
        file_path = temp_dir / "test_file.py"
        file_path.write_text("# Test file content\nprint('Hello')")
        return file_path
    
    @pytest.fixture
    def test_task(self):
        """Create a test task message."""
        return TaskMessage(
            message_type=MessageType.TASK,
            sender_id="parent_123",
            recipient_id="agent_456",
            content={"instruction": "Test task"},
            timestamp=time.time(),
            message_id=str(uuid.uuid4()),
            task_type=TaskType.IMPLEMENT,
            task_id=str(uuid.uuid4()),
            task_data={"test": "data"}
        )
    
    # Test initialization and basic properties

    def test_init_coder_agent(self, test_file, mock_llm_client):
        """Test initialization of a coder agent (file-based)."""
        agent = TestAgent(
            agent_id="test_agent_1",
            path=str(test_file),
            parent_id="parent_123",
            llm_client=mock_llm_client,
            max_content_size=5000
        )

        assert agent.agent_id == "test_agent_1"
        assert agent.path == test_file
        assert agent.parent_id == "parent_123"
        assert agent.llm_client == mock_llm_client
        assert agent.max_context_size == 5000
        assert not agent.is_active
        assert agent.current_task_id is None
        assert agent.personal_file == test_file
        assert agent.is_coder
        assert not agent.is_manager

    def test_init_manager_agent(self, temp_dir, mock_llm_client):
        """Test initialization of a manager agent (directory-based)."""
        agent = TestAgent(
            agent_id="test_manager_1",
            path=str(temp_dir),
            parent_id=None,
            llm_client=mock_llm_client
        )

        assert agent.agent_id == "test_manager_1"
        assert agent.path == temp_dir
        assert agent.parent_id is None
        assert agent.max_content_size == DEFAULT_MAX_CONTEXT_SIZE
        assert agent.personal_file == temp_dir.parent / f"{temp_dir.name}_README.md"
        assert agent.is_manager
        assert not agent.is_coder

    def test_init_nonexistent_file(self, temp_dir, mock_llm_client):
        """Test initialization with a non-existent file path."""
        nonexistent_path = temp_dir / "nonexistent.py"
        agent = TestAgent(
            agent_id="test_agent_2",
            path=str(nonexistent_path)
        )

        # Should be treated as a coder agent
        assert agent.is_coder
        assert not agent.is_manager
        assert agent.personal_file == nonexistent_path

    # Test activation & deactivation

    @pytest.mark.asyncio
    async def test_activate_success(self, test_file, mock_llm_client, test_task):
        """Test successful agent activation."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file),
            parent_id="parent_123",
            llm_client=mock_llm_client
        )

        # Mock the interval methods
        agent._load_context = AsyncMock()
        agent._send_result = AsyncMock()

        await agent.activate(test_task)

        # Verify activation state
        assert agent._load_context.called
        assert agent._send_result.called
        assert agent._send_result.call_args[0][2] == True

    @pytest.mark.asyncio
    async def test_activate_already_active(self, test_file, test_task);
        """Test activation when agent is already active"""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file)
        )

        agent.is_active = True
        agent.current_task_id = "existing_task"

        with pytest.raises(RuntimeError, match="already active"):
            await agent.activate(test_task)
        
    @pytest.mark.asyncio
    async def test_activate_with_error(self, test_file, test_task):
        """Test activation when task processing fails."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file),
            parent_id="parent_123"
        )

        # Make process_task raise an error
        agent.process_task = AsyncMock(side_effect=Exception("Processing failed"))
        agent._load_context = AsyncMock()
        agent._send_result = AsyncMock()

        await agent.activate(test_task)

        # Verify error handling
        assert agent._send_result.called
        assert agent._send_result.call_args[0][2] == False
        assert agent.error_count == 1

    @pytest.mark.asyncio
    async def test_deactivate(self, test_file):
        """Test agent deactivation."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file)
        )

        # Set up active state
        agent.is_active = True
        agent.current_task_id = "task_123"
        agent.active_tasks["task_123"] = {
            'task': MagicMock(),
            'start_time': time.time(),
            'status': 'active'
        }
        agent.memory = {"key": "value"}
        agent.context_cache = {"file": "content"}

        await agent.deactive()

        # Verify deactivation
        assert not agent.is_active
        assert agent.current_task_id is None
        assert len(agent.memory) == 0
        assert len(agent.contex_cache) == 0
        assert "task_123" in agent.completed_tasks
        assert "task_123" not in agent.active_tasks

    # Test file operations

    @pytest.mark.asyncio
    async def test_read_file_success(self, test_file):
        """Test successful file reading."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file)
        )

        content = await agent._read_file(str(test_file))
        assert content == "# Test file content\nprint('Hello')"

        # Test caching
        assert str(test_file) in agent.context_cache

        # Read again - should use cache
        with patch("builtins.open", mock_open()) as mock_file:
            content2 = await agent.read_file(str(test_file))
            assert content2 == content
            mock_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_read_file_not_found(self, temp_dir):
        """Test reading non-existent file."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(temp_dir)
        )

        with pytest.raises(FileNotFoundError):
            await agent.read_file(str(temp_dir / "nonexistent.txt"))
    
    @pytest.mark.asyncio
    async def test_read_file_permission_error(self, test_file):
        """Test reading file with permission error."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file)
        )

        with patch("builtins.open", side_effect=PermissionError()):
            with pytest.raises(PermissionError):
                await agent.read_file(str(test_file))

    @pytest.mark.asyncio
    async def test_update_personal_file_success(self, test_file):
        """Test updating personal file."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file)
        )

        new_content = "# Updated content\nprint('Updated')"
        await agent.update_personal_file(new_content)

        # Verify file was updated
        assert test_file.read_text() == new_content

        # Test cache update
        agent.context_cache[str(test_file)] = "old content"
        await agent.update_personal_file("newer content")
        assert agent.context_cache[str(test_file)] == "newer content"

    @pytest.mark.asyncio
    async def test_update_personal_file_no_personal_file(self, temp_dir):
        """Test updating when agent has no personal file."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(temp_dir)
        )
        agent.personal_file = None

        with pytest.raises(RuntimeError, match="no personal file"):
            await agent.update_personal_file("content")

    @pytest.mark.asyncio
    async def test_update_personal_file_create_parent_dirs(self, temp_dir):
        """Test creating parent directories when updating personal files."""
        nested_path = temp_dir / "sub1" / "sub2" / "file.py"
        agent = TestAgent(
            agent_id="test_agent",
            path=str(nested_path)
        )

        await agent.update_personal_file("content")
        assert nested_path.exists()
        assert nested_path.read_text() == "content"

    # Test command execution

    @pytest.mark.asyncio
    async def test_run_command_allowed(self, temp_dir):
        """Test running allowed commands."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(temp_dir)
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="file1.txt\nfile2.txt",
                stderr="",
                returncode=0
            )

            result = await agent.run_command("ls")

            assert result['stdout'] == "file1.txt\nfile2.txt"
            assert result['stderr'] == ""
            assert result['returncode'] == 0
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_command_not_allowed(self, temp_dir):
        """Test running disallowed commands."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(temp_dir)
        )

        with pytest.raises(PermissionError, match="Command not allowed"):
            await agent.run_command("rm -rf /")
    
    @pytest.mark.asyncio
    async def test_run_command_with_cwd(self, temp_dir):
        """Test running command with custom working directory."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(temp_dir)
        )

        custom_cwd = str(temp_dir / "subdir")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

            await agent.run_command("ls", cwd=custom_cwd)

            # Verify cwd was passed correctly
            assert mock_run.call_args[1]['cwd'] == custom_cwd

    @pytest.mark.asyncio
    async def test_run_command_timeout(self, temp_dir):
        """Test command timeout."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(temp_dir)
        )

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ls", 30)):
            with pytest.raises(subprocess.TimeoutExpired):
                await agent.run_command("ls")
    
    # Test message handling

    @pytest.mark.asyncio
    async def test_send_message(self, test_file):
        """Test sending messages."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file)
        )

        message = Message(
            message_type=MessageType.TASK,
            sender_id="test_agent",
            recipient_id="parent_123",
            content={"test": "data"},
            timestamp=time.time(),
            message_id=str(uuid.uuid4())
        )

        await agent.send_message("parent_123", message)

        assert len(agent.message_queue) == 1
        assert agent.message_queue[0] == message

    @pytest.mark.asyncio
    async def test_receive_messages(self, test_file):
        """Test receiving messages."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file)
        )

        # Add multiple messages
        messages = []
        for i in range(3):
            msg = Message(
                message_type=MessageType.TASK,
                sender_id=f"sender_{i}",
                recipient_id="test_agent",
                content={"index": i},
                timestamp=time.time(),
                message_id=str(uuid.uuid4())
            )
            messages.append(msg)
            agent.message_queue.append(msg)

        # Receive messages
        received = await agent.receive_messages()

        assert len(received) == 3
        assert received == messages
        assert len(agent.message_queue) == 0
    
    # Test context loading

    @pytest.mark.asyncio
    async def test_load_context(self, test_file):
        """Test loading context."""
        agent = TestAgent(
            agent_id="test_agent",
            path=str(test_file)
        )

        agent._get_codebase_structure_string = AsyncMock(
            return_value="Mock codebase structure"
        )

        await agent._load_context()

        assert 'personal_file_content' in agent.memory
        assert agent.memory['personal_file_content'] == "# Test file content\nprint('Hello')"
        assert agent.memory['codebase_structure'] == "Mock codebase structure"
        assert agent.memory['allowed_commands'] == list(ALLOWED_COMMANDS)

    