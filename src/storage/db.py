"""
Database connection and session management for HMA-LLM.
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator, Optional, List
from sqlmodel import SQLModel, create_engine, Session, select, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from .models import ChatSession, ChatMessage, ImportedFile, ProjectMeta

logger = logging.getLogger(__name__)

# Database configuration
DATA_DIR = Path("data")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/hma_llm.db")

# Convert SQLite URL to async format for aiosqlite
if DATABASE_URL.startswith("sqlite:"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Create engines
sync_engine = create_engine(DATABASE_URL, echo=False)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# Create session makers
SessionLocal = sessionmaker(bind=sync_engine, class_=Session)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession)

# Background task tracking
_cleanup_task: Optional[asyncio.Task] = None
_cleanup_running = False


async def init_database():
    """Initialize the database by creating all tables."""
    try:
        logger.info("Initializing database...")
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        logger.info(f"Database initialized successfully at {DATABASE_URL}")
        
        # Start background cleanup task
        await start_cleanup_task()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session with proper error handling."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


def get_sync_session() -> Session:
    """Get a synchronous database session."""
    return SessionLocal()


async def health_check() -> bool:
    """Check if the database is accessible."""
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Chat session management with graceful error handling

async def save_chat_session(session_data: dict) -> Optional[str]:
    """Save a chat session to the database with error handling."""
    try:
        async with AsyncSessionLocal() as session:
            # Create or update chat session
            chat_session = ChatSession(**session_data)
            session.add(chat_session)
            await session.commit()
            await session.refresh(chat_session)
            
            logger.debug(f"Saved chat session: {chat_session.id}")
            return chat_session.id
            
    except Exception as e:
        logger.error(f"Failed to save chat session: {e}")
        return None


async def load_chat_sessions(user_id: str = "anonymous", limit: int = 50) -> List[ChatSession]:
    """Load chat sessions for a user with error handling."""
    try:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .where(ChatSession.status == "active")
                .order_by(ChatSession.last_modified.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            sessions = result.scalars().all()
            
            logger.debug(f"Loaded {len(sessions)} chat sessions for user {user_id}")
            return list(sessions)
            
    except Exception as e:
        logger.error(f"Failed to load chat sessions: {e}")
        return []


async def get_chat_session(session_id: str) -> Optional[ChatSession]:
    """Get a specific chat session with all related data."""
    try:
        async with AsyncSessionLocal() as session:
            stmt = select(ChatSession).where(ChatSession.id == session_id)
            result = await session.execute(stmt)
            chat_session = result.scalar_one_or_none()
            
            if chat_session:
                logger.debug(f"Retrieved chat session: {session_id}")
            
            return chat_session
            
    except Exception as e:
        logger.error(f"Failed to get chat session {session_id}: {e}")
        return None


async def delete_chat_session(session_id: str) -> bool:
    """Delete a chat session and all related data."""
    try:
        async with AsyncSessionLocal() as session:
            # Get the session first
            stmt = select(ChatSession).where(ChatSession.id == session_id)
            result = await session.execute(stmt)
            chat_session = result.scalar_one_or_none()
            
            if chat_session:
                # Mark as deleted instead of hard delete for audit
                chat_session.status = "deleted"
                chat_session.last_modified = datetime.utcnow()
                await session.commit()
                
                logger.info(f"Marked chat session {session_id} as deleted")
                return True
            else:
                logger.warning(f"Chat session {session_id} not found for deletion")
                return False
                
    except Exception as e:
        logger.error(f"Failed to delete chat session {session_id}: {e}")
        return False


async def add_chat_message(session_id: str, message_data: dict) -> bool:
    """Add a message to a chat session with size limit validation."""
    try:
        async with AsyncSessionLocal() as session:
            # Check session limits first
            stmt = select(ChatSession).where(ChatSession.id == session_id)
            result = await session.execute(stmt)
            chat_session = result.scalar_one_or_none()
            
            if not chat_session:
                logger.error(f"Chat session {session_id} not found")
                return False
            
            if chat_session.message_count >= 1000:  # MAX_MESSAGES_PER_SESSION
                logger.warning(f"Chat session {session_id} exceeds message limit")
                return False
            
            # Create and add message
            message = ChatMessage(session_id=session_id, **message_data)
            session.add(message)
            
            # Update session message count and timestamp
            chat_session.message_count += 1
            chat_session.last_modified = datetime.utcnow()
            
            await session.commit()
            logger.debug(f"Added message to session {session_id}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to add message to session {session_id}: {e}")
        return False


async def add_imported_file(session_id: str, file_data: dict) -> bool:
    """Add an imported file to a chat session with size validation."""
    try:
        async with AsyncSessionLocal() as session:
            # Check session and file limits
            stmt = select(ChatSession).where(ChatSession.id == session_id)
            result = await session.execute(stmt)
            chat_session = result.scalar_one_or_none()
            
            if not chat_session:
                logger.error(f"Chat session {session_id} not found")
                return False
            
            if chat_session.file_count >= 100:  # MAX_FILES_PER_SESSION
                logger.warning(f"Chat session {session_id} exceeds file limit")
                return False
            
            # Validate file size
            content = file_data.get('content', '')
            if content and len(content.encode('utf-8')) > 10 * 1024 * 1024:  # 10MB
                logger.warning(f"File content too large for session {session_id}")
                return False
            
            # Create and add file
            imported_file = ImportedFile(session_id=session_id, **file_data)
            session.add(imported_file)
            
            # Update session file count
            chat_session.file_count += 1
            chat_session.last_modified = datetime.utcnow()
            
            await session.commit()
            logger.debug(f"Added imported file to session {session_id}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to add imported file to session {session_id}: {e}")
        return False


# Background cleanup task

async def cleanup_old_sessions():
    """Remove chat sessions older than 90 days."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        async with AsyncSessionLocal() as session:
            # Delete old sessions (hard delete after 90 days)
            stmt = delete(ChatSession).where(
                ChatSession.created_at < cutoff_date
            )
            result = await session.execute(stmt)
            deleted_count = result.rowcount
            await session.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old chat sessions")
            
            return deleted_count
            
    except Exception as e:
        logger.error(f"Failed to cleanup old sessions: {e}")
        return 0


async def cleanup_task():
    """Background task that runs cleanup periodically."""
    global _cleanup_running
    _cleanup_running = True
    
    logger.info("Started database cleanup background task")
    
    try:
        while _cleanup_running:
            # Run cleanup every 24 hours
            await asyncio.sleep(24 * 60 * 60)
            
            if _cleanup_running:  # Check again in case we're shutting down
                await cleanup_old_sessions()
                
    except asyncio.CancelledError:
        logger.info("Database cleanup task cancelled")
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
    finally:
        _cleanup_running = False


async def start_cleanup_task():
    """Start the background cleanup task."""
    global _cleanup_task
    
    if _cleanup_task is None or _cleanup_task.done():
        _cleanup_task = asyncio.create_task(cleanup_task())
        logger.info("Started database cleanup background task")


async def stop_cleanup_task():
    """Stop the background cleanup task."""
    global _cleanup_task, _cleanup_running
    
    _cleanup_running = False
    
    if _cleanup_task and not _cleanup_task.done():
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
        
        logger.info("Stopped database cleanup background task")


# Graceful database operations with fallbacks

async def safe_db_operation(operation, *args, **kwargs):
    """Execute a database operation with graceful error handling."""
    try:
        return await operation(*args, **kwargs)
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        # Return appropriate fallback values based on operation type
        if hasattr(operation, '__name__'):
            op_name = operation.__name__
            if 'load' in op_name or 'get' in op_name:
                return [] if 'sessions' in op_name else None
            elif 'save' in op_name or 'add' in op_name or 'delete' in op_name:
                return False
        return None 