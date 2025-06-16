"""
Test suite for the base agent system.
"""

import asyncio
import tempfile
import shutil
import uuid
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagickMock
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.base_agent import BaseAgent
from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.messages.protocol import TaskMessage, MessageType, TaskType
from src.llm.base import BaseLLMClient