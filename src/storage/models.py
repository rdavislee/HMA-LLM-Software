"""
Database models for HMA-LLM using SQLModel.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, Text
from sqlalchemy import DateTime

# Constants for limits
MAX_MESSAGES_PER_SESSION = 1000
MAX_FILES_PER_SESSION = 100
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB per file
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB total content per file

class ChatSession(SQLModel, table=True):
    """Chat session model."""
    __tablename__ = "chat_sessions"
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(default="anonymous", index=True)  # Default user until auth
    title: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    last_modified: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    project_id: Optional[str] = Field(default=None, index=True)
    project_path: Optional[str] = Field(default=None, max_length=512)
    
    # Size tracking for limits
    message_count: int = Field(default=0)
    file_count: int = Field(default=0)
    
    # Status and metadata
    status: str = Field(default="active")  # active, archived, deleted
    session_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Relationships
    messages: List["ChatMessage"] = Relationship(back_populates="session", cascade_delete=True)
    imported_files: List["ImportedFile"] = Relationship(back_populates="session", cascade_delete=True)
    project_meta: Optional["ProjectMeta"] = Relationship(back_populates="session")


class ChatMessage(SQLModel, table=True):
    """Individual chat message model."""
    __tablename__ = "chat_messages"
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="chat_sessions.id", index=True)
    type: str = Field(max_length=20)  # user, assistant, system
    content: str = Field(sa_column=Column(Text))  # Use Text for large content
    timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    agent_id: Optional[str] = Field(default=None, max_length=100)
    message_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Relationship
    session: ChatSession = Relationship(back_populates="messages")


class ImportedFile(SQLModel, table=True):
    """Imported project file metadata and content."""
    __tablename__ = "imported_files"
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="chat_sessions.id", index=True)
    name: str = Field(max_length=255)
    path: str = Field(max_length=1024)  # Relative path within project
    file_type: str = Field(default="file", max_length=20)  # file, directory
    size: Optional[int] = Field(default=None)  # Size in bytes
    content: Optional[str] = Field(default=None, sa_column=Column(Text))  # File content stored directly
    content_hash: Optional[str] = Field(default=None, max_length=64)  # SHA256 hash for deduplication
    mime_type: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    
    # Relationship
    session: ChatSession = Relationship(back_populates="imported_files")


class ProjectMeta(SQLModel, table=True):
    """Project metadata and status."""
    __tablename__ = "project_meta"
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="chat_sessions.id", index=True, unique=True)
    project_path: str = Field(max_length=512)
    language: str = Field(max_length=50)
    status: str = Field(default="active")  # active, completed, archived, error
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    last_modified: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    
    # Project initialization state
    init_phase: Optional[int] = Field(default=None)  # 1, 2, 3
    init_status: Optional[str] = Field(default=None, max_length=50)  # active, waiting_approval, completed, error
    
    # Additional metadata
    project_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Relationship
    session: ChatSession = Relationship(back_populates="project_meta")


# Validation functions for size limits
def validate_session_limits(session: ChatSession) -> List[str]:
    """Validate session size limits and return list of errors."""
    errors = []
    
    if session.message_count > MAX_MESSAGES_PER_SESSION:
        errors.append(f"Session exceeds maximum message count ({MAX_MESSAGES_PER_SESSION})")
    
    if session.file_count > MAX_FILES_PER_SESSION:
        errors.append(f"Session exceeds maximum file count ({MAX_FILES_PER_SESSION})")
    
    return errors


def validate_file_size(content: str, file_size: Optional[int] = None) -> List[str]:
    """Validate file size limits and return list of errors."""
    errors = []
    
    if file_size and file_size > MAX_FILE_SIZE_BYTES:
        errors.append(f"File exceeds maximum size ({MAX_FILE_SIZE_BYTES / (1024*1024):.1f}MB)")
    
    if content and len(content.encode('utf-8')) > MAX_CONTENT_LENGTH:
        errors.append(f"File content exceeds maximum length ({MAX_CONTENT_LENGTH / (1024*1024):.1f}MB)")
    
    return errors 