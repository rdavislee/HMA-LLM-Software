"""
Defines the agent-to-agent communication protocol.
Will define:
- Message types (task, query, result, error)
- Task types (create_file, modify_file, etc.)
- Message format and structure
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum

'''
Defines the different types of messages that can be exchanged between agents.
'''
class MessageType(Enum):
    TASK = "task"
    QUERY = "query"
    RESULT = "result"
    ERROR = "error"
    STATUS = "status"

'''
Defines the specific types of tasks that agents can perform.
'''
class TaskType(Enum):
    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    READ_FILE = "read_file"
    RUN_COMMAND = "run_command"
    DELEGATE = "delegate"
    WAIT = "wait"
    UPDATE_README = "update_readme"

@dataclass
class Message:
    '''
    Base message structure for agent communcation.
    '''
    message_type: MessageType
    sender_id: str
    recipient_id: str
    content: Dict[str, Any]
    timestamp: float
    message_id: str

@dataclass
class TaskMessage(Message):
    '''
    Message for task delegation.
    '''
    task_type: TaskType
    task_id: str
    priority: int = 1
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ResultMessage(Message):
    '''
    Message for returning task results.
    '''
    task_id: str
    success: bool
    result_data: Any = None
    error_message: Optional[str] = None

@dataclass
class QueryMessage(Message):
    '''
    Message for requesting information.
    '''
    query_type: str
    query_data: Dict[str, Any]


@dataclass
class StatusMessage(Message):
    '''
    Message for status updates.
    '''
    status: str
    details: Optional[Dict[str, Any]] = None