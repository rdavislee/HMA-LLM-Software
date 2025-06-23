"""
Test the agent template functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.messages.protocol import TaskMessage, Task, MessageType


class TestAgentTemplate:
    """Test the agent template functionality for both Manager and Coder agents."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        client = Mock()
        client.generate_response = AsyncMock(return_value="Mock response")
        return client
    
    @pytest.fixture
    def manager_agent(self, temp_dir, mock_llm_client):
        """Create a manager agent for testing."""
        # Create the directory
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create a personal file in the temp directory (where ManagerAgent expects it)
        personal_file = temp_dir / f"{temp_dir.name}_README.md"
        personal_file.write_text("# Test README\nThis is a test README.")
        
        # Create some test files in memory
        test_file = temp_dir / "test.py"
        test_file.write_text("def hello():\n    return 'world'")
        
        agent = ManagerAgent(
            path=str(temp_dir),
            llm_client=mock_llm_client
        )
        
        # Add test file to memory
        agent.read_file(str(test_file))
        
        # Add personal file to memory so it can be accessed by the template
        agent.read_file(str(personal_file))
        
        return agent

    @pytest.fixture
    def coder_agent(self, temp_dir, mock_llm_client):
        """Create a coder agent for testing."""
        # Create a code file
        code_file = temp_dir / "test_code.py"
        code_file.write_text("print('hello world')")

        agent = CoderAgent(
            path=str(code_file),
            llm_client=mock_llm_client
        )
        return agent

    @pytest.mark.asyncio
    async def test_manager_api_call_with_template(self, manager_agent):
        """Test that the manager api_call method uses the template correctly."""
        # Add a task
        task = TaskMessage(
            message_type=MessageType.DELEGATION,
            sender_id="test_sender",
            recipient_id="test_recipient",
            message_id="msg1",
            task=Task(task_id="task1", task_string="Test task")
        )
        manager_agent.activate(task)
        
        # Add a prompt to the queue
        manager_agent.prompt_queue.append("Create a new file")
        
        # Call the api_call method
        await manager_agent.api_call()
        
        # Verify that the LLM client was called
        manager_agent.llm_client.generate_response.assert_called_once()
        
        # Get the call arguments
        call_args = manager_agent.llm_client.generate_response.call_args
        formatted_prompt = call_args[1]['prompt']
        
        # Verify the formatted prompt contains expected sections
        assert "Agent Role" in formatted_prompt
        assert "manager agent" in formatted_prompt
        assert "Current Task" in formatted_prompt
        assert "Test task" in formatted_prompt
        assert "Current Prompt" in formatted_prompt
        assert "Create a new file" in formatted_prompt
        assert "Available Terminal Commands" in formatted_prompt
        assert "python -m pytest" in formatted_prompt # A terminal command
        assert "Instructions" in formatted_prompt
        
        # Verify the prompt queue was cleared
        assert len(manager_agent.prompt_queue) == 0
        
        # Verify the response was added to context
        assert any(entry.prompt == "Create a new file" and entry.response == "Mock response" for entry in manager_agent.context)

    @pytest.mark.asyncio
    async def test_coder_api_call_with_template(self, coder_agent):
        """Test that the coder api_call method uses the template correctly."""
        # Add a task
        task = TaskMessage(
            message_type=MessageType.DELEGATION,
            sender_id="test_sender",
            recipient_id="test_recipient",
            message_id="msg1",
            task=Task(task_id="task1", task_string="Implement feature")
        )
        coder_agent.activate(task)
        
        # Add a prompt to the queue
        coder_agent.prompt_queue.append("Implement the new feature as described.")
        
        # Call the api_call method
        await coder_agent.api_call()
        
        # Verify that the LLM client was called
        coder_agent.llm_client.generate_response.assert_called_once()
        
        # Get the call arguments
        call_args = coder_agent.llm_client.generate_response.call_args
        formatted_prompt = call_args[1]['prompt']
        
        # Verify the formatted prompt contains expected sections
        assert "Agent Role" in formatted_prompt
        assert "Coder agent" in formatted_prompt
        assert "Current Task" in formatted_prompt
        assert "Implement feature" in formatted_prompt
        assert "Current Prompt" in formatted_prompt
        assert "Implement the new feature" in formatted_prompt
        assert "Available Terminal Commands" in formatted_prompt
        assert "python -m pytest" in formatted_prompt # A terminal command
        assert "Instructions" in formatted_prompt
        
        # Verify the prompt queue was cleared
        assert len(coder_agent.prompt_queue) == 0
        
        # Verify the response was added to context
        assert any(entry.prompt == "Implement the new feature as described." and entry.response == "Mock response" for entry in coder_agent.context) 