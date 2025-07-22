"""
Socket.IO server for real-time communication with the HMA-LLM frontend.
Handles agent updates, code streaming, and project management.
"""

import asyncio
import json
import logging
import uuid
import sys
import os
import hashlib
import zipfile
import tempfile
import shutil
import base64
from typing import Dict, Set, Optional, Any, List, Callable, Awaitable
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

# Add the project root to Python path to enable src imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import socketio
from aiohttp import web

# Git operations
try:
    import git
    from git import Repo, InvalidGitRepositoryError, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    # Create dummy classes for type hints when git is not available
    class Repo:
        pass
    class InvalidGitRepositoryError(Exception):
        pass
    class GitCommandError(Exception):
        pass
    
    logger = logging.getLogger(__name__)
    logger.warning("GitPython not available - git operations will be disabled")

from src.storage import init_database
from src.agents.base_agent import BaseAgent
from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.llm.providers import get_llm_client
from src.messages.protocol import TaskMessage, Task, MessageType
from src.terminal.container_manager import ContainerManager
from src.terminal.terminal_session import TerminalManager
from src import ROOT_DIR
from src.config import Language
from src.initializer import initialize_new_project

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ClientSession:
    """Represents a connected client session."""
    sid: str
    client_id: str
    project_path: Optional[Path] = None

@dataclass
class AgentStatus:
    """Status information for an agent."""
    agent_id: str
    status: str
    task: Optional[str] = None
    file_path: Optional[str] = None

@dataclass
class ProjectInitializationManager:
    """Manages project initialization state and communication."""
    client_id: str
    server: 'HMAServer'
    project_path: Path
    language: Language
    initial_prompt: str
    project_name: Optional[str]
    current_phase: int = 1
    is_active: bool = True
    master_agent: Optional[Any] = None
    root_manager: Optional[Any] = None
    agent_lookup: Optional[Dict[Path, Any]] = None
    message_queue: asyncio.Queue = None  # Queue for user messages during Phase 1
    
    def __post_init__(self):
        """Initialize the message queue after dataclass initialization."""
        if self.message_queue is None:
            self.message_queue = asyncio.Queue()
    
    async def send_status_update(self, phase: int, phase_title: str, status: str, message: str = None, requires_approval: bool = False):
        """Send a project initialization status update to the client."""
        await self.server.send_to_client(self.client_id, {
            "type": "project_init_status",
            "payload": {
                "phase": phase,
                "phaseTitle": phase_title,
                "status": status,
                "projectId": self.project_path.name,
                "projectPath": str(self.project_path),
                "message": message,
                "requiresApproval": requires_approval
            }
        })
    
    async def send_chat_message(self, content: str, sender: str = "ai"):
        """Send a chat message during project initialization."""
        await self.server.send_to_client(self.client_id, {
            "type": "message",
            "payload": {
                "id": str(uuid.uuid4()),
                "content": content,
                "sender": sender,
                "timestamp": datetime.now().isoformat(),
                "agentId": "hive_initializer"
            }
        })

def map_frontend_language_to_backend(language_code: str) -> Language:
    """Map frontend language codes to backend Language enum values."""
    # For now, we only support TypeScript in the backend
    # In the future, this can be expanded when more languages are added
    language_mapping = {
        'typescript': Language.TYPESCRIPT,
        'javascript': Language.TYPESCRIPT,  # Map JS to TS for now
        'react': Language.TYPESCRIPT,
        'vue': Language.TYPESCRIPT,
        # All other languages default to TypeScript for now
        # TODO: Add more languages when backend supports them
    }
    
    return language_mapping.get(language_code.lower(), Language.TYPESCRIPT)

class HMAServer:
    """Main server class handling Socket.IO connections and agent orchestration."""
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        # Read from environment variables with fallbacks
        self.host = host or os.getenv("HMA_HOST", "localhost")
        self.port = port or int(os.getenv("HMA_PORT", "8080"))
        
        # WebSocket configuration from environment
        ws_path = os.getenv("WS_PATH", "/ws")
        cors_origins = os.getenv("WS_CORS_ORIGINS", "*")
        
        self.sio = socketio.AsyncServer(
            cors_allowed_origins=cors_origins,
            async_mode='aiohttp'
        )
        self.app = web.Application()
        self.sio.attach(self.app, socketio_path=ws_path)
        
        self.clients: Dict[str, ClientSession] = {}
        self.agents: Dict[str, BaseAgent] = {}
        self.projects: Dict[str, Path] = {}
        
        # Task management - NEW
        self.active_tasks: Dict[str, asyncio.Task] = {}  # Maps client_id to active task
        
        # Project initialization management - NEW
        self.project_initializations: Dict[str, ProjectInitializationManager] = {}  # Maps client_id to initialization manager
        self.pending_approvals: Dict[str, asyncio.Event] = {}  # Maps client_id to approval events
        self.approval_responses: Dict[str, str] = {}  # Maps client_id to approval responses
        
        # Container and terminal management
        self.container_manager = ContainerManager()
        self.terminal_manager = TerminalManager()
        
        # Set up Socket.IO event handlers
        self.setup_handlers()
        
    def setup_handlers(self):
        """Set up Socket.IO event handlers."""
        
        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection."""
            client_id = str(uuid.uuid4())
            session = ClientSession(sid=sid, client_id=client_id)
            self.clients[client_id] = session
            
            logger.info(f"Client {client_id} connected (sid: {sid})")
            
            # Send welcome message
            await self.sio.emit('message', {
                "type": "message",
                "payload": {
                    "id": str(uuid.uuid4()),
                    "content": "Welcome to HMA-LLM Software Construction! I'm here to help you build amazing applications. What would you like to create today?",
                    "sender": "ai",
                    "timestamp": datetime.now().isoformat(),
                    "agentId": "system"
                }
            }, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection."""
            # Find client by sid
            client_id = None
            for cid, session in self.clients.items():
                if session.sid == sid:
                    client_id = cid
                    break
            
            if client_id:
                logger.info(f"Client {client_id} disconnected")
                await self.cleanup_client(client_id)
        
        @self.sio.event
        async def message(sid, data):
            """Handle incoming message from client."""
            # Find client by sid
            client_id = None
            for cid, session in self.clients.items():
                if session.sid == sid:
                    client_id = cid
                    break
            
            if client_id:
                await self.handle_message(client_id, data)
        
    async def start(self):
        """Start the Socket.IO server."""
        logger.info(f"Starting HMA-LLM Socket.IO server on {self.host}:{self.port}")
        
        # Initialize database
        try:
            await init_database()
            logger.info("Database initialization completed")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            logger.warning("Continuing without database - chat persistence disabled")
            # Don't raise - allow server to continue without database
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"Server started on http://{self.host}:{self.port}")
        
        # Keep the server running
        await asyncio.Future()
    
    async def handle_message(self, client_id: str, data: str):
        """Handle incoming messages from clients."""
        try:
            message = json.loads(data)
            message_type = message.get("type")
            payload = message.get("payload", {})
            
            logger.info(f"Received message from {client_id}: {message_type}")
            
            if message_type == "prompt":
                await self.handle_prompt(client_id, payload)
            elif message_type == "import_project":
                await self.handle_import_project(client_id, payload)
            elif message_type == "file_select":
                await self.handle_file_select(client_id, payload)
            elif message_type == "code_edit":
                await self.handle_code_edit(client_id, payload)
            elif message_type == "stop":  # NEW: Handle stop command
                await self.handle_stop(client_id, payload)
            elif message_type == "start_project_init":  # NEW: Handle project initialization
                await self.handle_start_project_init(client_id, payload)
            elif message_type == "approve_phase":  # NEW: Handle phase approval
                await self.handle_approve_phase(client_id, payload)
            elif message_type == "reject_phase":  # NEW: Handle phase rejection
                await self.handle_reject_phase(client_id, payload)
            elif message_type == "new_chat":  # Handle new chat
                await self.handle_new_chat(client_id, payload)
            elif message_type == "clear_project":  # Handle clear project
                await self.handle_clear_project(client_id, payload)
            elif message_type == "terminal_create":  # Handle terminal creation
                await self.handle_terminal_create(client_id, payload)
            elif message_type == "terminal_data":  # Handle terminal data
                await self.handle_terminal_data(client_id, payload)
            elif message_type == "terminal_resize":  # Handle terminal resize
                await self.handle_terminal_resize(client_id, payload)
            elif message_type == "terminal_close":  # Handle terminal close
                await self.handle_terminal_close(client_id, payload)
            # Add git and file operation handlers to the handle_message method
            elif message_type == "save_chat_session":  # Handle chat session save
                await self.handle_save_chat_session(client_id, payload)
            elif message_type == "load_chat_history":  # Handle chat history load
                await self.handle_load_chat_history(client_id, payload)
            elif message_type == "delete_chat_session":  # Handle chat session delete
                await self.handle_delete_chat_session(client_id, payload)
            # Git operation handlers
            elif message_type == "git_status":
                await self.handle_git_status(client_id, payload)
            elif message_type == "git_diff":
                await self.handle_git_diff(client_id, payload)
            elif message_type == "git_stage":
                await self.handle_git_stage(client_id, payload)
            elif message_type == "git_unstage":
                await self.handle_git_unstage(client_id, payload)
            elif message_type == "git_commit":
                await self.handle_git_commit(client_id, payload)
            elif message_type == "git_branches":
                await self.handle_git_branches(client_id, payload)
            elif message_type == "git_checkout":
                await self.handle_git_checkout(client_id, payload)
            elif message_type == "git_push":
                await self.handle_git_push(client_id, payload)
            elif message_type == "git_pull":
                await self.handle_git_pull(client_id, payload)
            elif message_type == "git_commits":
                await self.handle_git_commits(client_id, payload)
            elif message_type == "git_init":
                await self.handle_git_init(client_id, payload)
            # File system operation handlers
            elif message_type == "file_create":
                await self.handle_file_create(client_id, payload)
            elif message_type == "file_read":
                await self.handle_file_read(client_id, payload)
            elif message_type == "file_update":
                await self.handle_file_update(client_id, payload)
            elif message_type == "file_delete":
                await self.handle_file_delete(client_id, payload)
            elif message_type == "dir_create":
                await self.handle_dir_create(client_id, payload)
            elif message_type == "dir_list":
                await self.handle_dir_list(client_id, payload)
            elif message_type == "dir_delete":
                await self.handle_dir_delete(client_id, payload)
            # Project download handler
            elif message_type == "download_project":
                await self.handle_download_project(client_id, payload)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error processing message from client {client_id}: {e}")
    
    async def handle_prompt(self, client_id: str, payload: Dict[str, Any]):
        """Handle a prompt from the client."""
        agent_id = payload.get("agentId", "root")
        prompt = payload.get("prompt", "")
        
        session = self.clients.get(client_id)
        if not session:
            return
        
        # Check if we're in project initialization mode
        if client_id in self.project_initializations:
            init_manager = self.project_initializations[client_id]
            
            # During Phase 1, route user messages to the Master Agent
            if init_manager.is_active and init_manager.current_phase == 1:
                # Send user message to the Master Agent via the human interface
                # This allows the Master Agent to process user responses during Phase 1
                logger.info(f"Routing user message to Master Agent during Phase 1: {prompt}")
                
                # First, send the user message as a chat message
                await self.send_to_client(client_id, {
                    "type": "message",
                    "payload": {
                        "id": str(uuid.uuid4()),
                        "content": prompt,
                        "sender": "user",
                        "timestamp": datetime.now().isoformat(),
                        "agentId": "user"
                    }
                })
                
                # Then, if we have a pending response event, trigger it with the user's message
                if client_id in self.pending_approvals:
                    # This is an approval response
                    if prompt.strip().lower() == "approved":
                        self.approval_responses[client_id] = "approved"
                    else:
                        self.approval_responses[client_id] = f"rejected: {prompt}"
                    self.pending_approvals[client_id].set()
                else:
                    # This is a regular conversation during Phase 1
                    # Add the message to the queue for the Master Agent to process
                    await init_manager.message_queue.put(prompt)
                    logger.info(f"Added user message to queue for Master Agent: {prompt}")
                
                return
        
        # Normal prompt handling (existing code)
        # Create project directory if it doesn't exist
        if not session.project_path:
            project_name = f"project_{uuid.uuid4().hex[:8]}"
            session.project_path = ROOT_DIR / "generated_projects" / project_name
            session.project_path.mkdir(parents=True, exist_ok=True)
            self.projects[client_id] = session.project_path
            
            # Send project status update
            await self.send_to_client(client_id, {
                "type": "project_status",
                "payload": {
                    "projectId": project_name,
                    "projectPath": str(session.project_path),
                    "status": "initializing"
                }
            })
        
        # Create root manager agent if it doesn't exist
        root_agent_id = f"{client_id}_root"
        if root_agent_id not in self.agents:
            llm_client = get_llm_client('gpt-4o')  # or your preferred model
            root_agent = ManagerAgent(
                path=str(session.project_path),
                llm_client=llm_client
            )
            self.agents[root_agent_id] = root_agent
            
            # Send agent creation notification
            await self.send_agent_update(client_id, {
                "agentId": root_agent_id,
                "status": "inactive",
                "task": None
            })
        
        # Send initial AI response
        await self.send_to_client(client_id, {
            "type": "message",
            "payload": {
                "id": str(uuid.uuid4()),
                "content": f"I'll help you {prompt.lower()}. Let me start by analyzing the requirements and setting up the project structure.",
                "sender": "ai",
                "timestamp": datetime.now().isoformat(),
                "agentId": root_agent_id
            }
        })
        
        # Create task and activate agent
        task = Task(
            task_id=str(uuid.uuid4()),
            task_string=prompt
        )
        
        task_message = TaskMessage(
            message_type=MessageType.DELEGATION,
            sender="user",  # String for user, not agent object
            recipient=root_agent,
            message_id=str(uuid.uuid4()),
            task=task
        )
        
        # Activate the root agent
        root_agent = self.agents[root_agent_id]
        root_agent.activate(task_message)
        
        # Send agent activation notification
        await self.send_agent_update(client_id, {
            "agentId": root_agent_id,
            "status": "active",
            "task": prompt
        })
        
        # Process the task asynchronously
        task = asyncio.create_task(self.process_agent_task(client_id, root_agent_id, task_message))
        self.active_tasks[client_id] = task  # Store the task for potential cancellation
    
    async def handle_stop(self, client_id: str, payload: Dict[str, Any]):
        """Handle stop/cancel request from client."""
        logger.info(f"Received stop request from client {client_id}")
        
        # Cancel active task if it exists
        if client_id in self.active_tasks:
            task = self.active_tasks[client_id]
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled active task for client {client_id}")
                
                # Send cancellation notification
                await self.send_to_client(client_id, {
                    "type": "message",
                    "payload": {
                        "id": str(uuid.uuid4()),
                        "content": "Task cancelled by user.",
                        "sender": "system",
                        "timestamp": datetime.now().isoformat(),
                        "agentId": "system"
                    }
                })
                
                # Update all active agents to inactive
                agents_to_deactivate = [aid for aid in self.agents.keys() if aid.startswith(f"{client_id}_")]
                for agent_id in agents_to_deactivate:
                    await self.send_agent_update(client_id, {
                        "agentId": agent_id,
                        "status": "inactive",
                        "task": None
                    })
            
            # Remove from active tasks
            del self.active_tasks[client_id]
        else:
            logger.info(f"No active task found for client {client_id}")
    
    async def handle_start_project_init(self, client_id: str, payload: Dict[str, Any]):
        """Handle project initialization request from client."""
        language_code = payload.get("language", "typescript")
        initial_prompt = payload.get("initialPrompt", "")
        project_name = payload.get("projectName")
        
        logger.info(f"Starting project initialization for client {client_id}: {language_code}, {initial_prompt}")
        
        session = self.clients.get(client_id)
        if not session:
            logger.error(f"No session found for client {client_id}")
            await self.send_to_client(client_id, {
                "type": "message",
                "payload": {
                    "id": str(uuid.uuid4()),
                    "content": "❌ Error: No active session found. Please refresh the page and try again.",
                    "sender": "system",
                    "timestamp": datetime.now().isoformat(),
                    "agentId": "system"
                }
            })
            return
        
        try:
            # Map frontend language to backend language
            language = map_frontend_language_to_backend(language_code)
            
            # Create project directory
            if not project_name:
                project_name = f"project_{uuid.uuid4().hex[:8]}"
            
            project_path = ROOT_DIR / "generated_projects" / project_name
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Update session
            session.project_path = project_path
            self.projects[client_id] = project_path
            
            # Send project status update
            await self.send_to_client(client_id, {
                "type": "project_status",
                "payload": {
                    "projectId": project_name,
                    "projectPath": str(project_path),
                    "status": "initializing"
                }
            })
            
            # Create initial project structure (empty project folder)
            await self.send_to_client(client_id, {
                "type": "file_tree_update",
                "payload": {
                    "action": "create",
                    "filePath": ".",
                    "fileType": "folder"
                }
            })
            
            # Send initial documentation.md file
            doc_content = f"# {project_name}\n\nInitial Request: {initial_prompt}\n\n"
            doc_path = project_path / "documentation.md"
            doc_path.write_text(doc_content, encoding='utf-8')
            
            await self.send_to_client(client_id, {
                "type": "file_tree_update",
                "payload": {
                    "action": "create",
                    "filePath": "documentation.md",
                    "fileType": "file",
                    "content": doc_content
                }
            })
            
            # Create project initialization manager
            init_manager = ProjectInitializationManager(
                client_id=client_id,
                server=self,
                project_path=project_path,
                language=language,
                initial_prompt=initial_prompt,
                project_name=project_name
            )
            self.project_initializations[client_id] = init_manager
            
            # Send initial status update
            await init_manager.send_status_update(
                phase=1,
                phase_title="Product Understanding",
                status="active",
                message="Hive is starting to understand your project requirements..."
            )
            
            # Send initial chat message
            await init_manager.send_chat_message(
                f"🚀 Starting new {language_code.title()} project: **{project_name}**\n\n"
                f"I'll help you build: *{initial_prompt}*\n\n"
                f"Let me begin with Phase 1 - Product Understanding. I'll ask you some questions to better understand your requirements.",
                sender="ai"
            )
            
            # Start the project initialization process asynchronously
            task = asyncio.create_task(self.run_project_initialization(client_id, init_manager))
            self.active_tasks[client_id] = task
            
        except Exception as e:
            logger.error(f"Error starting project initialization for client {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "message",
                "payload": {
                    "id": str(uuid.uuid4()),
                    "content": f"❌ Error starting project initialization: {str(e)}",
                    "sender": "system",
                    "timestamp": datetime.now().isoformat(),
                    "agentId": "system"
                }
            })
            
            # Clean up on error
            if client_id in self.project_initializations:
                del self.project_initializations[client_id]
            if client_id in self.projects:
                del self.projects[client_id]
            if session:
                session.project_path = None
    
    async def handle_approve_phase(self, client_id: str, payload: Dict[str, Any]):
        """Handle phase approval from client."""
        phase = payload.get("phase")
        logger.info(f"Client {client_id} approved phase {phase}")
        
        # Set approval response and trigger event
        self.approval_responses[client_id] = "approved"
        if client_id in self.pending_approvals:
            self.pending_approvals[client_id].set()
    
    async def handle_reject_phase(self, client_id: str, payload: Dict[str, Any]):
        """Handle phase rejection from client."""
        phase = payload.get("phase")
        feedback = payload.get("feedback", "")
        logger.info(f"Client {client_id} rejected phase {phase} with feedback: {feedback}")
        
        # Set rejection response and trigger event
        self.approval_responses[client_id] = f"rejected: {feedback}" if feedback else "rejected"
        if client_id in self.pending_approvals:
            self.pending_approvals[client_id].set()
    
    async def handle_new_chat(self, client_id: str, payload: Dict[str, Any]):
        """Handle new chat from client."""
        logger.info(f"Received new chat request from client {client_id}")
        
        # Clean up project initialization state
        await self.cleanup_project_initialization(client_id)
        
        # Send welcome message
        await self.send_to_client(client_id, {
            "type": "message",
            "payload": {
                "id": str(uuid.uuid4()),
                "content": "Welcome to Hive! I'm here to help you build amazing applications. What would you like to create today?",
                "sender": "ai",
                "timestamp": datetime.now().isoformat(),
                "agentId": "system"
            }
        })
    
    async def handle_clear_project(self, client_id: str, payload: Dict[str, Any]):
        """Handle clear project from client."""
        logger.info(f"Received clear project request from client {client_id}")
        
        # Clean up project initialization state
        await self.cleanup_project_initialization(client_id)
        
        # Send confirmation message
        await self.send_to_client(client_id, {
            "type": "message",
            "payload": {
                "id": str(uuid.uuid4()),
                "content": "Project cleared successfully.",
                "sender": "system",
                "timestamp": datetime.now().isoformat(),
                "agentId": "system"
            }
        })
    
    async def cleanup_project_initialization(self, client_id: str):
        """Clean up project initialization resources for a client."""
        # Cancel active project initialization task
        if client_id in self.active_tasks:
            task = self.active_tasks[client_id]
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled project initialization task for client {client_id}")
            del self.active_tasks[client_id]
        
        # Clean up project initialization state
        if client_id in self.project_initializations:
            del self.project_initializations[client_id]
        if client_id in self.pending_approvals:
            del self.pending_approvals[client_id]
        if client_id in self.approval_responses:
            del self.approval_responses[client_id]
        
        # Clear project path
        session = self.clients.get(client_id)
        if session:
            session.project_path = None
        if client_id in self.projects:
            del self.projects[client_id]
    
    async def process_agent_task(self, client_id: str, agent_id: str, task_message: TaskMessage):
        """Process a task for an agent asynchronously."""
        try:
            agent = self.agents[agent_id]
            
            # Process the task with streaming support
            async for update in self.stream_agent_work(agent, task_message):
                if update['type'] == 'message':
                    # Send agent message
                    await self.send_to_client(client_id, {
                        "type": "message",
                        "payload": {
                            "id": str(uuid.uuid4()),
                            "content": update['content'],
                            "sender": "ai",
                            "timestamp": datetime.now().isoformat(),
                            "agentId": agent_id,
                            "metadata": update.get('metadata')
                        }
                    })
                elif update['type'] == 'code':
                    # Stream code updates
                    await self.send_to_client(client_id, {
                        "type": "code_stream",
                        "payload": {
                            "agentId": update['file_id'],
                            "filePath": update['file_path'],
                            "content": update['content'],
                            "isComplete": update.get('isComplete', False),
                            "syntax": update.get('syntax', 'text')
                        }
                    })
                elif update['type'] == 'file_created':
                    # Send file tree update
                    await self.send_to_client(client_id, {
                        "type": "file_tree_update",
                        "payload": {
                            "action": "create",
                            "filePath": update['file_path'],
                            "fileType": update['file_type'],
                            "content": update.get('content', '')
                        }
                    })
                elif update['type'] == 'delegation':
                    # Handle child agent creation
                    child_agent_id = update['child_id']
                    if child_agent_id not in self.agents:
                        # Create child agent based on type
                        child_path = Path(agent.path) / update['child_name']
                        if update['agent_type'] == 'manager':
                            child_agent = ManagerAgent(
                                path=str(child_path), 
                                parent=agent,
                                llm_client=agent.llm_client
                            )
                        else:
                            child_agent = CoderAgent(
                                path=str(child_path),
                                parent=agent,
                                llm_client=agent.llm_client
                            )
                        self.agents[child_agent_id] = child_agent
                        agent.children.append(child_agent)
                    
                    # Send delegation message
                    await self.send_to_client(client_id, {
                        "type": "message",
                        "payload": {
                            "id": str(uuid.uuid4()),
                            "content": f"📁 Delegating to {update['child_name']}: {update['task']}",
                            "sender": "system",
                            "timestamp": datetime.now().isoformat(),
                            "agentId": agent_id
                        }
                    })
                    
                    # Send child agent activation
                    await self.send_agent_update(client_id, {
                        "agentId": child_agent_id,
                        "status": "active",
                        "task": update['task'],
                        "parentId": agent_id
                    })
                elif update['type'] == 'agent_update':
                    # Forward agent status update
                    await self.send_agent_update(client_id, update['data'])
            
            # Send completion notification
            await self.send_agent_update(client_id, {
                "agentId": agent_id,
                "status": "completed",
                "task": None
            })
            
            # Send completion message
            await self.send_to_client(client_id, {
                "type": "message",
                "payload": {
                    "id": str(uuid.uuid4()),
                    "content": f"✅ Task completed successfully! Your project is ready.",
                    "sender": "ai",
                    "timestamp": datetime.now().isoformat(),
                    "agentId": agent_id
                }
            })
            
            # Update project status
            await self.send_to_client(client_id, {
                "type": "project_status",
                "payload": {
                    "projectId": self.projects.get(client_id, "unknown"),
                    "projectPath": str(self.clients[client_id].project_path),
                    "status": "completed"
                }
            })
            
        except asyncio.CancelledError:
            # Task was cancelled
            logger.info(f"Task cancelled for agent {agent_id}")
            raise  # Re-raise to properly handle cancellation
            
        except Exception as e:
            logger.error(f"Error processing task for agent {agent_id}: {e}")
            
            # Send error notification
            await self.send_agent_update(client_id, {
                "agentId": agent_id,
                "status": "error",
                "task": str(e)
            })
            
            await self.send_to_client(client_id, {
                "type": "message",
                "payload": {
                    "id": str(uuid.uuid4()),
                    "content": f"❌ An error occurred: {str(e)}",
                    "sender": "system",
                    "timestamp": datetime.now().isoformat(),
                    "agentId": agent_id
                }
            })
        finally:
            # Clean up task from active tasks
            if client_id in self.active_tasks and self.active_tasks[client_id].done():
                del self.active_tasks[client_id]
    
    async def handle_import_project(self, client_id: str, payload: Dict[str, Any]):
        """Handle project import request."""
        files = payload.get("files", [])
        session = self.clients.get(client_id)
        
        if not session:
            return
            
        # Create project directory if it doesn't exist
        if not session.project_path:
            project_name = f"project_{uuid.uuid4().hex[:8]}"
            session.project_path = ROOT_DIR / "generated_projects" / project_name
            session.project_path.mkdir(parents=True, exist_ok=True)
            self.projects[client_id] = session.project_path
            
            # Send project status update
            await self.send_to_client(client_id, {
                "type": "project_status",
                "payload": {
                    "projectId": project_name,
                    "projectPath": str(session.project_path),
                    "status": "initializing"
                }
            })
        
        await self.send_to_client(client_id, {
            "type": "message",
            "payload": {
                "id": str(uuid.uuid4()),
                "content": f"Importing project with {len(files)} files...",
                "sender": "system",
                "timestamp": datetime.now().isoformat(),
                "agentId": "system"
            }
        })
        
        # Process each imported file
        created_dirs = set()
        
        for file_data in files:
            try:
                file_path = file_data.get("path", file_data.get("name", ""))
                file_type = file_data.get("type", "file")
                content = file_data.get("content", "")
                
                if not file_path:
                    continue
                
                # Normalize path separators
                file_path = file_path.replace("\\", "/")
                
                # Create directory structure
                if "/" in file_path:
                    dir_parts = file_path.split("/")[:-1]
                    for i in range(len(dir_parts)):
                        dir_path = "/".join(dir_parts[:i+1])
                        if dir_path not in created_dirs:
                            created_dirs.add(dir_path)
                            full_dir_path = session.project_path / dir_path
                            full_dir_path.mkdir(parents=True, exist_ok=True)
                            
                            # Send directory creation update
                            await self.send_to_client(client_id, {
                                "type": "file_tree_update",
                                "payload": {
                                    "action": "create",
                                    "filePath": dir_path,
                                    "fileType": "folder"
                                }
                            })
                
                # Create the file
                if file_type == "file":
                    full_file_path = session.project_path / file_path
                    full_file_path.parent.mkdir(parents=True, exist_ok=True)
                    full_file_path.write_text(content, encoding='utf-8')
                    
                    # Send file creation update
                    await self.send_to_client(client_id, {
                        "type": "file_tree_update",
                        "payload": {
                            "action": "create",
                            "filePath": file_path,
                            "fileType": "file",
                            "content": content
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Error importing file {file_path}: {e}")
                await self.send_to_client(client_id, {
                    "type": "message",
                    "payload": {
                        "id": str(uuid.uuid4()),
                        "content": f"Error importing {file_path}: {str(e)}",
                        "sender": "system",
                        "timestamp": datetime.now().isoformat(),
                        "agentId": "system"
                    }
                })
        
        # Send completion message
        await self.send_to_client(client_id, {
            "type": "message",
            "payload": {
                "id": str(uuid.uuid4()),
                "content": f"✅ Successfully imported {len(files)} files!",
                "sender": "system",
                "timestamp": datetime.now().isoformat(),
                "agentId": "system"
            }
        })
        
        # Update project status
        await self.send_to_client(client_id, {
            "type": "project_status",
            "payload": {
                "projectId": self.projects.get(client_id, "unknown"),
                "projectPath": str(session.project_path),
                "status": "active"
            }
        })
    
    async def handle_file_select(self, client_id: str, payload: Dict[str, Any]):
        """Handle file selection from frontend."""
        file_path = payload.get("filePath")
        session = self.clients.get(client_id)
        
        if session and session.project_path and file_path:
            full_path = session.project_path / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    content = full_path.read_text()
                    # File content is already displayed in frontend, no need to send again
                    logger.info(f"File selected: {file_path}")
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
    
    async def handle_code_edit(self, client_id: str, payload: Dict[str, Any]):
        """Handle code edits from frontend."""
        file_path = payload.get("filePath")
        content = payload.get("content", "")
        session = self.clients.get(client_id)
        
        if session and session.project_path and file_path:
            full_path = session.project_path / file_path
            try:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                logger.info(f"File updated: {file_path}")
            except Exception as e:
                logger.error(f"Error writing file {file_path}: {e}")
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send a message to a specific client."""
        session = self.clients.get(client_id)
        if session:
            try:
                await self.sio.emit('message', message, room=session.sid)
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {e}")
    
    async def send_agent_update(self, client_id: str, update: Dict[str, Any]):
        """Send an agent status update to a client."""
        await self.send_to_client(client_id, {
            "type": "agent_update",
            "payload": update
        })
    
    async def cleanup_client(self, client_id: str):
        """Clean up resources when a client disconnects."""
        if client_id in self.clients:
            del self.clients[client_id]
        
        # Clean up project resources
        if client_id in self.projects:
            del self.projects[client_id]
        
        # Clean up agents for this client
        agents_to_remove = [aid for aid in self.agents.keys() if aid.startswith(client_id)]
        for agent_id in agents_to_remove:
            del self.agents[agent_id]
        
        # Clean up project initialization resources
        await self.cleanup_project_initialization(client_id)

    # Terminal management methods
    async def handle_terminal_create(self, client_id: str, payload: Dict[str, Any]):
        """Handle terminal creation request with enhanced session management."""
        project_id = payload.get("projectId", "default")
        
        try:
            session = self.clients.get(client_id)
            if not session:
                logger.error(f"No session found for client {client_id}")
                return
            
            # Get or create workspace path
            workspace_path = session.project_path or (Path("generated_projects") / project_id)
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Check existing sessions for this project (allow up to 5 concurrent sessions)
            existing_sessions = [s for s in self.terminal_manager.sessions.keys() 
                               if s.startswith(f"terminal_{project_id}_")]
            
            if len(existing_sessions) >= 5:
                await self.send_to_client(client_id, {
                    "type": "terminal_session",
                    "payload": {
                        "sessionId": None,
                        "projectId": project_id,
                        "status": "error",
                        "error": "Maximum number of terminal sessions (5) reached for this project"
                    }
                })
                return
            
            # Create container if it doesn't exist
            if project_id not in self.container_manager.containers:
                container_id = self.container_manager.create_workspace_container(project_id, workspace_path)
                container = self.container_manager.containers.get(project_id)
                
                if not container:
                    await self.send_to_client(client_id, {
                        "type": "terminal_session",
                        "payload": {
                            "sessionId": None,
                            "projectId": project_id,
                            "status": "error",
                            "error": "Failed to create container"
                        }
                    })
                    return
                
                # Start container
                success = self.container_manager.start_container(project_id)
                if not success:
                    await self.send_to_client(client_id, {
                        "type": "terminal_session",
                        "payload": {
                            "sessionId": None,
                            "projectId": project_id,
                            "status": "error",
                            "error": "Failed to start container"
                        }
                    })
                    return
            else:
                container = self.container_manager.containers[project_id]
                container_id = container.id
            
            # Create unique terminal session
            session_id = f"terminal_{project_id}_{uuid.uuid4().hex[:8]}"
            
            def on_data(sess_id: str, data: str):
                # Send terminal data to client
                asyncio.create_task(self.send_to_client(client_id, {
                    "type": "terminal_data",
                    "payload": {"sessionId": sess_id, "data": data}
                }))
            
            def on_exit(sess_id: str):
                # Send terminal session update
                asyncio.create_task(self.send_to_client(client_id, {
                    "type": "terminal_session",
                    "payload": {
                        "sessionId": sess_id,
                        "projectId": project_id,
                        "status": "stopped"
                    }
                }))
                # Clean up session
                if sess_id in self.terminal_manager.sessions:
                    del self.terminal_manager.sessions[sess_id]
            
            # Create session
            terminal_success = await self.terminal_manager.create_session(
                session_id, project_id, container, on_data, on_exit
            )
            
            if terminal_success:
                # Send session info to client
                await self.send_to_client(client_id, {
                    "type": "terminal_session",
                    "payload": {
                        "sessionId": session_id,
                        "projectId": project_id,
                        "containerId": container_id,
                        "status": "running"
                    }
                })
                
                logger.info(f"Created terminal session {session_id} for project {project_id}")
            else:
                await self.send_to_client(client_id, {
                    "type": "terminal_session",
                    "payload": {
                        "sessionId": None,
                        "projectId": project_id,
                        "status": "error",
                        "error": "Failed to create terminal session"
                    }
                })
                
        except Exception as e:
            logger.error(f"Error creating terminal for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "terminal_session",
                "payload": {
                    "sessionId": None,
                    "projectId": project_id,
                    "status": "error",
                    "error": str(e)
                }
            })
    
    async def handle_terminal_data(self, client_id: str, payload: Dict[str, Any]):
        """Handle terminal data input."""
        session_id = payload.get("sessionId")
        data = payload.get("data", "")
        
        if not session_id:
            return
            
        try:
            session = self.terminal_manager.sessions.get(session_id)
            if session:
                await session.send_data(data)
            else:
                logger.warning(f"Terminal session {session_id} not found")
        except Exception as e:
            logger.error(f"Error sending data to terminal {session_id}: {e}")
    
    async def handle_terminal_resize(self, client_id: str, payload: Dict[str, Any]):
        """Handle terminal resize."""
        session_id = payload.get("sessionId")
        cols = payload.get("cols", 80)
        rows = payload.get("rows", 24)
        
        if not session_id:
            return
            
        try:
            session = self.terminal_manager.sessions.get(session_id)
            if session:
                await session.resize(cols, rows)
            else:
                logger.warning(f"Terminal session {session_id} not found for resize")
        except Exception as e:
            logger.error(f"Error resizing terminal {session_id}: {e}")
    
    async def handle_terminal_close(self, client_id: str, payload: Dict[str, Any]):
        """Handle terminal close."""
        session_id = payload.get("sessionId")
        
        if not session_id:
            return
            
        try:
            session = self.terminal_manager.sessions.get(session_id)
            if session:
                await session.close()
                if session_id in self.terminal_manager.sessions:
                    del self.terminal_manager.sessions[session_id]
                logger.info(f"Closed terminal session {session_id}")
            else:
                logger.warning(f"Terminal session {session_id} not found for close")
        except Exception as e:
            logger.error(f"Error closing terminal {session_id}: {e}")

    # Git operation handlers
    def get_project_repo(self, client_id: str) -> Optional[Repo]:
        """Get the Git repository for a client's project."""
        session = self.clients.get(client_id)
        if not session or not session.project_path:
            return None
        
        try:
            return Repo(session.project_path)
        except InvalidGitRepositoryError:
            return None
    
    async def handle_git_status(self, client_id: str, payload: Dict[str, Any]):
        """Handle git status request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_status",
                    "payload": {"status": None, "error": "Git not available"}
                })
                return
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_status", 
                    "payload": {"status": None, "error": "No git repository found"}
                })
                return
            
            # Get status
            staged_files = []
            unstaged_files = []
            untracked_files = []
            
            # Get staged files
            for item in repo.index.diff("HEAD"):
                change_type = 'M' if item.change_type == 'M' else 'A' if item.change_type == 'A' else 'D'
                staged_files.append({
                    "file_path": item.a_path or item.b_path,
                    "status": change_type,
                    "staged": True
                })
            
            # Get unstaged files
            for item in repo.index.diff(None):
                change_type = 'M' if item.change_type == 'M' else 'A' if item.change_type == 'A' else 'D'
                unstaged_files.append({
                    "file_path": item.a_path or item.b_path,
                    "status": change_type,
                    "staged": False
                })
            
            # Get untracked files
            for file_path in repo.untracked_files:
                untracked_files.append({
                    "file_path": file_path,
                    "status": "??",
                    "staged": False
                })
            
            # Get branch info
            try:
                current_branch = repo.active_branch.name
                is_detached = False
            except:
                current_branch = str(repo.head.commit)[:8]
                is_detached = True
            
            # Get ahead/behind counts
            ahead = 0
            behind = 0
            try:
                if repo.active_branch.tracking_branch():
                    ahead = len(list(repo.iter_commits(f'{repo.active_branch.tracking_branch()}..HEAD')))
                    behind = len(list(repo.iter_commits(f'HEAD..{repo.active_branch.tracking_branch()}')))
            except:
                pass
            
            status_data = {
                "staged_files": staged_files,
                "unstaged_files": unstaged_files,
                "untracked_files": untracked_files,
                "current_branch": current_branch,
                "ahead": ahead,
                "behind": behind,
                "is_dirty": repo.is_dirty(),
                "is_detached": is_detached
            }
            
            await self.send_to_client(client_id, {
                "type": "git_status",
                "payload": {"status": status_data}
            })
            
        except Exception as e:
            logger.error(f"Git status error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_status",
                "payload": {"status": None, "error": str(e)}
            })
    
    async def handle_git_diff(self, client_id: str, payload: Dict[str, Any]):
        """Handle git diff request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_diff",
                    "payload": {"diff": None, "error": "Git not available"}
                })
                return
            
            file_path = payload.get("filePath")
            staged = payload.get("staged", False)
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_diff",
                    "payload": {"diff": None, "error": "No git repository found"}
                })
                return
            
            # Generate diff
            if staged:
                # Diff of staged changes
                diff_text = repo.git.diff("--cached", file_path)
            else:
                # Diff of unstaged changes
                diff_text = repo.git.diff(file_path)
            
            # Count added/removed lines
            added_lines = len([line for line in diff_text.split('\n') if line.startswith('+')])
            removed_lines = len([line for line in diff_text.split('\n') if line.startswith('-')])
            
            # Check if binary file
            is_binary = "Binary files" in diff_text
            
            diff_data = {
                "file_path": file_path,
                "diff_content": diff_text,
                "added_lines": added_lines,
                "removed_lines": removed_lines,
                "is_binary": is_binary
            }
            
            await self.send_to_client(client_id, {
                "type": "git_diff",
                "payload": {"diff": diff_data}
            })
            
        except Exception as e:
            logger.error(f"Git diff error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_diff",
                "payload": {"diff": None, "error": str(e)}
            })
    
    async def handle_git_stage(self, client_id: str, payload: Dict[str, Any]):
        """Handle git stage file request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_stage_result",
                    "payload": {"filePath": payload.get("filePath", ""), "success": False, "error": "Git not available"}
                })
                return
            
            file_path = payload.get("filePath")
            if not file_path:
                await self.send_to_client(client_id, {
                    "type": "git_stage_result",
                    "payload": {"filePath": "", "success": False, "error": "File path required"}
                })
                return
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_stage_result",
                    "payload": {"filePath": file_path, "success": False, "error": "No git repository found"}
                })
                return
            
            # Stage the file
            repo.index.add([file_path])
            
            await self.send_to_client(client_id, {
                "type": "git_stage_result",
                "payload": {"filePath": file_path, "success": True}
            })
            
        except Exception as e:
            logger.error(f"Git stage error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_stage_result",
                "payload": {"filePath": payload.get("filePath", ""), "success": False, "error": str(e)}
            })
    
    async def handle_git_unstage(self, client_id: str, payload: Dict[str, Any]):
        """Handle git unstage file request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_unstage_result",
                    "payload": {"filePath": payload.get("filePath", ""), "success": False, "error": "Git not available"}
                })
                return
            
            file_path = payload.get("filePath")
            if not file_path:
                await self.send_to_client(client_id, {
                    "type": "git_unstage_result", 
                    "payload": {"filePath": "", "success": False, "error": "File path required"}
                })
                return
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_unstage_result",
                    "payload": {"filePath": file_path, "success": False, "error": "No git repository found"}
                })
                return
            
            # Unstage the file
            repo.index.reset([file_path])
            
            await self.send_to_client(client_id, {
                "type": "git_unstage_result",
                "payload": {"filePath": file_path, "success": True}
            })
            
        except Exception as e:
            logger.error(f"Git unstage error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_unstage_result",
                "payload": {"filePath": payload.get("filePath", ""), "success": False, "error": str(e)}
            })
    
    async def handle_git_commit(self, client_id: str, payload: Dict[str, Any]):
        """Handle git commit request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_commit_result",
                    "payload": {"success": False, "error": "Git not available"}
                })
                return
            
            message = payload.get("message")
            author_name = payload.get("authorName")
            author_email = payload.get("authorEmail")
            
            if not message:
                await self.send_to_client(client_id, {
                    "type": "git_commit_result",
                    "payload": {"success": False, "error": "Commit message required"}
                })
                return
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_commit_result",
                    "payload": {"success": False, "error": "No git repository found"}
                })
                return
            
            # Set author if provided
            if author_name and author_email:
                actor = git.Actor(author_name, author_email)
                commit = repo.index.commit(message, author=actor, committer=actor)
            else:
                commit = repo.index.commit(message)
            
            await self.send_to_client(client_id, {
                "type": "git_commit_result",
                "payload": {"success": True, "commitHash": str(commit)}
            })
            
        except Exception as e:
            logger.error(f"Git commit error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_commit_result",
                "payload": {"success": False, "error": str(e)}
            })
    
    async def handle_git_branches(self, client_id: str, payload: Dict[str, Any]):
        """Handle git branches request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_branches",
                    "payload": {"branches": [], "error": "Git not available"}
                })
                return
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_branches",
                    "payload": {"branches": [], "error": "No git repository found"}
                })
                return
            
            branches = []
            
            # Local branches
            for branch in repo.branches:
                branches.append({
                    "name": branch.name,
                    "is_current": branch == repo.active_branch,
                    "is_remote": False,
                    "tracking_branch": str(branch.tracking_branch()) if branch.tracking_branch() else None,
                    "last_commit_hash": str(branch.commit)[:8],
                    "last_commit_message": branch.commit.message.strip().split('\n')[0][:50],
                    "last_commit_time": branch.commit.committed_datetime.isoformat()
                })
            
            # Remote branches
            for remote in repo.remotes:
                for ref in remote.refs:
                    if not ref.name.endswith('/HEAD'):
                        branches.append({
                            "name": ref.name,
                            "is_current": False,
                            "is_remote": True,
                            "tracking_branch": None,
                            "last_commit_hash": str(ref.commit)[:8],
                            "last_commit_message": ref.commit.message.strip().split('\n')[0][:50],
                            "last_commit_time": ref.commit.committed_datetime.isoformat()
                        })
            
            await self.send_to_client(client_id, {
                "type": "git_branches",
                "payload": {"branches": branches}
            })
            
        except Exception as e:
            logger.error(f"Git branches error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_branches",
                "payload": {"branches": [], "error": str(e)}
            })
    
    async def handle_git_checkout(self, client_id: str, payload: Dict[str, Any]):
        """Handle git checkout branch request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_checkout_result",
                    "payload": {"branchName": payload.get("branchName", ""), "success": False, "error": "Git not available"}
                })
                return
            
            branch_name = payload.get("branchName")
            if not branch_name:
                await self.send_to_client(client_id, {
                    "type": "git_checkout_result",
                    "payload": {"branchName": "", "success": False, "error": "Branch name required"}
                })
                return
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_checkout_result", 
                    "payload": {"branchName": branch_name, "success": False, "error": "No git repository found"}
                })
                return
            
            # Checkout the branch
            repo.git.checkout(branch_name)
            
            await self.send_to_client(client_id, {
                "type": "git_checkout_result",
                "payload": {"branchName": branch_name, "success": True}
            })
            
        except Exception as e:
            logger.error(f"Git checkout error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_checkout_result",
                "payload": {"branchName": payload.get("branchName", ""), "success": False, "error": str(e)}
            })
    
    async def handle_git_push(self, client_id: str, payload: Dict[str, Any]):
        """Handle git push request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_push_result",
                    "payload": {"success": False, "remoteName": payload.get("remoteName", "origin"), "error": "Git not available"}
                })
                return
            
            remote_name = payload.get("remoteName", "origin")
            branch_name = payload.get("branchName")
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_push_result",
                    "payload": {"success": False, "remoteName": remote_name, "error": "No git repository found"}
                })
                return
            
            # Get remote
            try:
                remote = repo.remote(remote_name)
            except:
                await self.send_to_client(client_id, {
                    "type": "git_push_result",
                    "payload": {"success": False, "remoteName": remote_name, "error": f"Remote '{remote_name}' not found"}
                })
                return
            
            # Push
            if branch_name:
                remote.push(branch_name)
            else:
                remote.push()
            
            await self.send_to_client(client_id, {
                "type": "git_push_result",
                "payload": {"success": True, "remoteName": remote_name, "branchName": branch_name}
            })
            
        except Exception as e:
            logger.error(f"Git push error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_push_result",
                "payload": {"success": False, "remoteName": payload.get("remoteName", "origin"), "error": str(e)}
            })
    
    async def handle_git_pull(self, client_id: str, payload: Dict[str, Any]):
        """Handle git pull request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_pull_result",
                    "payload": {"success": False, "remoteName": payload.get("remoteName", "origin"), "error": "Git not available"}
                })
                return
            
            remote_name = payload.get("remoteName", "origin")
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_pull_result",
                    "payload": {"success": False, "remoteName": remote_name, "error": "No git repository found"}
                })
                return
            
            # Get remote
            try:
                remote = repo.remote(remote_name)
            except:
                await self.send_to_client(client_id, {
                    "type": "git_pull_result",
                    "payload": {"success": False, "remoteName": remote_name, "error": f"Remote '{remote_name}' not found"}
                })
                return
            
            # Pull
            remote.pull()
            
            await self.send_to_client(client_id, {
                "type": "git_pull_result",
                "payload": {"success": True, "remoteName": remote_name}
            })
            
        except Exception as e:
            logger.error(f"Git pull error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_pull_result",
                "payload": {"success": False, "remoteName": payload.get("remoteName", "origin"), "error": str(e)}
            })
    
    async def handle_git_commits(self, client_id: str, payload: Dict[str, Any]):
        """Handle git commits request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_commits",
                    "payload": {"commits": [], "error": "Git not available"}
                })
                return
            
            max_count = payload.get("maxCount", 50)
            
            repo = self.get_project_repo(client_id)
            if not repo:
                await self.send_to_client(client_id, {
                    "type": "git_commits",
                    "payload": {"commits": [], "error": "No git repository found"}
                })
                return
            
            commits = []
            for commit in repo.iter_commits(max_count=max_count):
                commits.append({
                    "hash": str(commit),
                    "short_hash": str(commit)[:8],
                    "author_name": commit.author.name,
                    "author_email": commit.author.email,
                    "committer_name": commit.committer.name,
                    "committer_email": commit.committer.email,
                    "message": commit.message.strip(),
                    "timestamp": commit.committed_datetime.isoformat(),
                    "parents": [str(p) for p in commit.parents],
                    "files_changed": list(commit.stats.files.keys())[:10]  # Limit to 10 files
                })
            
            await self.send_to_client(client_id, {
                "type": "git_commits",
                "payload": {"commits": commits}
            })
            
        except Exception as e:
            logger.error(f"Git commits error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_commits",
                "payload": {"commits": [], "error": str(e)}
            })
    
    async def handle_git_init(self, client_id: str, payload: Dict[str, Any]):
        """Handle git repository initialization request."""
        try:
            if not GIT_AVAILABLE:
                await self.send_to_client(client_id, {
                    "type": "git_init_result",
                    "payload": {"success": False, "error": "Git not available"}
                })
                return
            
            session = self.clients.get(client_id)
            if not session or not session.project_path:
                await self.send_to_client(client_id, {
                    "type": "git_init_result",
                    "payload": {"success": False, "error": "No project path found"}
                })
                return
            
            # Check if repo already exists
            try:
                existing_repo = Repo(session.project_path)
                await self.send_to_client(client_id, {
                    "type": "git_init_result",
                    "payload": {"success": False, "error": "Git repository already exists"}
                })
                return
            except InvalidGitRepositoryError:
                pass  # No repo exists, we can proceed
            
            # Initialize repository
            repo = Repo.init(session.project_path)
            
            # Create .gitignore with sensible defaults
            gitignore_content = payload.get("gitignore", self.get_default_gitignore())
            gitignore_path = session.project_path / ".gitignore"
            gitignore_path.write_text(gitignore_content, encoding='utf-8')
            
            # Add .gitignore to repo
            repo.index.add([".gitignore"])
            
            # Initial commit
            repo.index.commit("Initial commit")
            
            await self.send_to_client(client_id, {
                "type": "git_init_result",
                "payload": {"success": True, "message": "Git repository initialized successfully"}
            })
            
            # Send file tree update for .gitignore
            await self.send_to_client(client_id, {
                "type": "file_tree_update",
                "payload": {
                    "action": "create",
                    "filePath": ".gitignore",
                    "fileType": "file",
                    "content": gitignore_content
                }
            })
            
        except Exception as e:
            logger.error(f"Git init error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "git_init_result",
                "payload": {"success": False, "error": str(e)}
            })
    
    def get_default_gitignore(self) -> str:
        """Get default .gitignore content."""
        return """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production
/build
/dist

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
tmp/
temp/
"""

    async def stream_agent_work(self, agent: BaseAgent, task_message: TaskMessage):
        """Stream agent work updates in real-time."""
        try:
            # Process the task
            await agent.process_task(task_message.task.task_string)
            
            # Get agent response from context
            if agent.context:
                last_response = agent.context[-1].response
                
                # Parse agent language and generate updates
                if agent.is_manager:
                    # Manager agent - parse manager language
                    async for update in self.parse_manager_response(agent, last_response):
                        yield update
                else:
                    # Coder agent - parse coder language
                    async for update in self.parse_coder_response(agent, last_response):
                        yield update
                        
        except Exception as e:
            logger.error(f"Error in agent streaming: {e}")
            yield {
                'type': 'message',
                'content': f"Error: {str(e)}"
            }

    async def parse_manager_response(self, agent: ManagerAgent, response: str):
        """Parse manager agent response and generate updates."""
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse manager language commands
            if line.startswith('CREATE'):
                parts = line.split('"')
                if len(parts) >= 2:
                    file_type = 'folder' if 'folder' in line else 'file'
                    file_path = parts[1]
                    
                    yield {
                        'type': 'message',
                        'content': f"Creating {file_type}: {file_path}"
                    }
                    
                    # Create actual file/folder
                    full_path = Path(agent.path) / file_path
                    if file_type == 'folder':
                        full_path.mkdir(parents=True, exist_ok=True)
                    else:
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.touch()
                    
                    yield {
                        'type': 'file_created',
                        'file_path': file_path,
                        'file_type': file_type
                    }
                    
            elif line.startswith('DELEGATE'):
                parts = line.split('"')
                if len(parts) >= 4:
                    target_type = 'folder' if 'folder' in line else 'file'
                    target_path = parts[1]
                    task_desc = parts[3]
                    
                    child_id = f"{agent.path}_{target_path}".replace('/', '_')
                    
                    yield {
                        'type': 'delegation',
                        'child_id': child_id,
                        'child_name': target_path,
                        'agent_type': 'manager' if target_type == 'folder' else 'coder',
                        'task': task_desc
                    }
                    
            elif line.startswith('UPDATE_README'):
                # Extract content
                content_start = line.find('CONTENT="') + len('CONTENT="')
                content_end = line.rfind('"')
                if content_start < content_end:
                    content = line[content_start:content_end]
                    
                    # Write README
                    readme_path = Path(agent.path) / f"{Path(agent.path).name}_README.md"
                    readme_path.write_text(content)
                    
                    yield {
                        'type': 'message',
                        'content': "Updated README documentation"
                    }

    async def parse_coder_response(self, agent: CoderAgent, response: str):
        """Parse coder agent response and generate updates."""
        lines = response.strip().split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Parse coder language commands
            if line.startswith('READ'):
                parts = line.split('"')
                if len(parts) >= 2:
                    file_path = parts[1]
                    yield {
                        'type': 'message',
                        'content': f"Reading {file_path} for context..."
                    }
                    
            elif line.startswith('CHANGE'):
                # Extract content
                content_start = line.find('CONTENT="') + len('CONTENT="')
                
                # Find the end of content (could be multi-line)
                content_lines = [line[content_start:]]
                j = i + 1
                while j < len(lines) and not content_lines[-1].endswith('"'):
                    content_lines.append(lines[j])
                    j += 1
                
                content = '\n'.join(content_lines)
                if content.endswith('"'):
                    content = content[:-1]
                
                # Replace escape sequences
                content = content.replace('\\n', '\n').replace('\\"', '"')
                
                # Determine file syntax
                file_ext = Path(agent.path).suffix.lower()
                syntax_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'typescript',
                    '.tsx': 'typescript',
                    '.jsx': 'javascript',
                    '.html': 'html',
                    '.css': 'css',
                    '.json': 'json',
                    '.md': 'markdown'
                }
                syntax = syntax_map.get(file_ext, 'text')
                
                # Stream code in chunks
                chunk_size = 100
                for k in range(0, len(content), chunk_size):
                    chunk = content[k:k + chunk_size]
                    is_complete = k + chunk_size >= len(content)
                    
                    yield {
                        'type': 'code',
                        'file_id': str(agent.path),
                        'file_path': str(Path(agent.path).relative_to(Path(agent.path).parent.parent)),
                        'content': chunk,
                        'isComplete': is_complete,
                        'syntax': syntax
                    }
                    
                    # Small delay for streaming effect
                    await asyncio.sleep(0.05)
                
                # Write actual file
                Path(agent.path).write_text(content)
                
            elif line.startswith('RUN'):
                parts = line.split('"')
                if len(parts) >= 2:
                    command = parts[1]
                    yield {
                        'type': 'message',
                        'content': f"Running: {command}"
                    }

    async def run_project_initialization(self, client_id: str, init_manager: ProjectInitializationManager):
        """Run the three-phase project initialization process."""
        try:
            logger.info(f"Starting project initialization for client {client_id}")
            
            # Create human interface function that communicates via WebSocket
            async def websocket_human_interface(prompt: str) -> str:
                """Human interface function that uses WebSocket for communication."""
                logger.info(f"Master agent message for client {client_id}: {prompt}")
                
                # Extract phase information from the prompt
                current_phase = init_manager.current_phase
                if "Phase 1:" in prompt:
                    current_phase = 1
                elif "Phase 2:" in prompt:
                    current_phase = 2
                elif "Phase 3:" in prompt:
                    current_phase = 3
                
                # Update phase if it changed
                if current_phase != init_manager.current_phase:
                    init_manager.current_phase = current_phase
                
                # Check if this is a phase completion message requiring approval
                is_phase_completion = any(phrase in prompt for phrase in [
                    "Type 'Approved' to move to Phase",
                    "Type 'Approved' to approve",
                    "Phase Complete",
                    "Complete**"
                ])
                
                # Check if this is the FINISH directive message
                is_finish_message = "use FINISH" in prompt
                
                if is_phase_completion:
                    # This is a phase completion requiring approval
                    # Send as a chat message first
                    await init_manager.send_chat_message(prompt, sender="ai")
                    
                    # Then update status to show waiting for approval
                    phase_titles = {1: "Product Understanding", 2: "Structure Stage", 3: "Implementation"}
                    await init_manager.send_status_update(
                        phase=init_manager.current_phase,
                        phase_title=phase_titles.get(init_manager.current_phase, "Unknown"),
                        status="waiting_approval",
                        message=f"Phase {init_manager.current_phase} complete. Waiting for your approval to continue.",
                        requires_approval=True
                    )
                    
                    # Wait for approval/rejection
                    approval_event = asyncio.Event()
                    self.pending_approvals[client_id] = approval_event
                    
                    await approval_event.wait()
                    
                    # Get the response
                    response = self.approval_responses.get(client_id, "approved")
                    
                    # Clean up
                    if client_id in self.pending_approvals:
                        del self.pending_approvals[client_id]
                    if client_id in self.approval_responses:
                        del self.approval_responses[client_id]
                    
                    logger.info(f"Client {client_id} responded: {response}")
                    
                    # Handle rejection with feedback
                    if response.startswith("rejected"):
                        if ":" in response:
                            feedback = response.split(":", 1)[1].strip()
                            return feedback
                        else:
                            return "Please make improvements and use FINISH when ready."
                    
                    return "approved"
                elif is_finish_message:
                    # This is a FINISH directive message from the Master Agent
                    # Don't send it as a chat message, just return empty string
                    logger.info(f"Master agent FINISH directive for phase {init_manager.current_phase}")
                    return ""
                else:
                    # This is a regular message from the Master Agent (questions, updates, etc.)
                    # Send it as a normal chat message
                    await init_manager.send_chat_message(prompt, sender="ai")
                    
                    # For non-approval messages during Phase 1, we need to wait for user input
                    if init_manager.current_phase == 1 and not is_phase_completion:
                        # During Phase 1, the Master Agent is having a conversation
                        # Wait for user response from the message queue
                        try:
                            # Wait for up to 300 seconds (5 minutes) for user response
                            user_response = await asyncio.wait_for(
                                init_manager.message_queue.get(), 
                                timeout=300.0
                            )
                            logger.info(f"Got user response for Master Agent: {user_response}")
                            return user_response
                        except asyncio.TimeoutError:
                            logger.warning(f"Timeout waiting for user response during Phase 1")
                            return "No response received. Please continue with your questions."
                    
                    # For other phases or situations, return empty string
                    return ""
            
            # Get LLM clients
            master_llm_client = get_llm_client('gpt-4o')
            base_llm_client = get_llm_client('gpt-4o')
            
            # Run the project initialization
            logger.info(f"Calling initialize_new_project for {init_manager.project_path}")
            
            master_agent, root_manager, agent_lookup = await initialize_new_project(
                root_directory=init_manager.project_path,
                initial_prompt=init_manager.initial_prompt,
                human_interface_fn=websocket_human_interface,
                language=init_manager.language,
                master_llm_client=master_llm_client,
                base_llm_client=base_llm_client,
                max_context_size=80000
            )
            
            # Store the agents in the initialization manager
            init_manager.master_agent = master_agent
            init_manager.root_manager = root_manager
            init_manager.agent_lookup = agent_lookup
            
            # Send completion status
            await init_manager.send_status_update(
                phase=3,
                phase_title="Implementation",
                status="completed",
                message="🎉 Project initialization completed successfully! Your project is ready."
            )
            
            # Send final completion message
            await init_manager.send_chat_message(
                "✅ **Project Initialization Complete!**\n\n"
                f"Your {init_manager.language.value} project has been successfully created at `{init_manager.project_path.name}`.\n\n"
                "The project structure has been set up and initial implementation is complete. "
                "You can now explore the files in the Project Files panel and continue development."
            )
            
            # Send project status update
            await self.send_to_client(client_id, {
                "type": "project_status",
                "payload": {
                    "projectId": init_manager.project_path.name,
                    "projectPath": str(init_manager.project_path),
                    "status": "completed"
                }
            })
            
            # Send file tree updates for created files
            await self.scan_and_send_file_tree(client_id, init_manager.project_path)
            
            logger.info(f"Project initialization completed for client {client_id}")
            
        except asyncio.CancelledError:
            logger.info(f"Project initialization cancelled for client {client_id}")
            await init_manager.send_chat_message("❌ Project initialization was cancelled.", sender="system")
            raise
            
        except Exception as e:
            logger.error(f"Error during project initialization for client {client_id}: {e}")
            await init_manager.send_status_update(
                phase=init_manager.current_phase,
                phase_title="Error",
                status="error",
                message=f"An error occurred during project initialization: {str(e)}"
            )
            await init_manager.send_chat_message(
                f"❌ **Project Initialization Failed**\n\nError: {str(e)}\n\n"
                "Please try starting a new project again.",
                sender="system"
            )
            
        finally:
            # Clean up
            if client_id in self.project_initializations:
                del self.project_initializations[client_id]
            if client_id in self.pending_approvals:
                del self.pending_approvals[client_id]
            if client_id in self.approval_responses:
                del self.approval_responses[client_id]
            if client_id in self.active_tasks:
                del self.active_tasks[client_id]
    
    # Database and chat persistence methods
    async def handle_save_chat_session(self, client_id: str, payload: Dict[str, Any]):
        """Handle chat session save request."""
        try:
            from src.storage.db import save_chat_session, add_chat_message, add_imported_file
            
            session_data = payload.get("session", {})
            
            # Extract basic session info
            session_info = {
                "id": session_data.get("id"),
                "title": session_data.get("title", "Untitled Session"),
                "user_id": "anonymous",  # Default until auth is implemented
                "project_id": session_data.get("projectId"),
                "project_path": session_data.get("projectPath"),
                "status": "active"
            }
            
            # Save the session first
            session_id = await save_chat_session(session_info)
            
            if session_id:
                # Save messages
                messages = session_data.get("messages", [])
                for message in messages:
                    message_data = {
                        "type": message.get("type", "user"),
                        "content": message.get("content", ""),
                        "agent_id": message.get("agentId"),
                        "metadata": message.get("metadata")
                    }
                    await add_chat_message(session_id, message_data)
                
                # Save imported files
                files = session_data.get("projectFiles", [])
                for file_info in files:
                    file_data = {
                        "name": file_info.get("name", ""),
                        "path": file_info.get("path", ""),
                        "file_type": file_info.get("type", "file"),
                        "size": file_info.get("size"),
                        "content": file_info.get("content"),
                        "mime_type": file_info.get("mimeType")
                    }
                    await add_imported_file(session_id, file_data)
                
                # Send success response
                await self.send_to_client(client_id, {
                    "type": "chat_save_result",
                    "payload": {"success": True, "sessionId": session_id}
                })
                
                logger.info(f"Saved chat session {session_id} for client {client_id}")
            else:
                # Send failure response
                await self.send_to_client(client_id, {
                    "type": "chat_save_result", 
                    "payload": {"success": False, "error": "Failed to save session"}
                })
                
        except Exception as e:
            logger.error(f"Save chat session error for client {client_id}: {e}")
            await self.send_to_client(client_id, {
                "type": "chat_save_result",
                "payload": {"success": False, "error": str(e)}
            })

    async def handle_load_chat_history(self, client_id: str, payload: Dict[str, Any]):
        """Handle chat history load request."""
        try:
            from src.storage.db import load_chat_sessions
            
            user_id = payload.get("userId", "anonymous")
            limit = payload.get("limit", 50)
            
            # Load sessions from database
            sessions = await load_chat_sessions(user_id, limit)
            
            # Convert to response format
            session_list = []
            for session in sessions:
                session_data = {
                    "id": session.id,
                    "title": session.title,
                    "createdAt": session.created_at.isoformat(),
                    "lastModified": session.last_modified.isoformat(),
                    "messageCount": session.message_count,
                    "fileCount": session.file_count,
                    "projectId": session.project_id,
                    "status": session.status
                }
                session_list.append(session_data)
            
            # Send response
            await self.send_to_client(client_id, {
                "type": "chat_history_response",
                "payload": {"sessions": session_list}
            })
            
            logger.debug(f"Loaded {len(sessions)} chat sessions for client {client_id}")
            
        except Exception as e:
            logger.error(f"Load chat history error for client {client_id}: {e}")
            await self.send_to_client(client_id, {
                "type": "chat_history_response",
                "payload": {"sessions": [], "error": str(e)}
            })

    async def handle_delete_chat_session(self, client_id: str, payload: Dict[str, Any]):
        """Handle chat session delete request."""
        try:
            from src.storage.db import delete_chat_session
            
            session_id = payload.get("sessionId")
            if not session_id:
                raise ValueError("Session ID is required")
            
            # Delete the session
            success = await delete_chat_session(session_id)
            
            # Send response
            await self.send_to_client(client_id, {
                "type": "chat_delete_result",
                "payload": {"success": success, "sessionId": session_id}
            })
            
            if success:
                logger.info(f"Deleted chat session {session_id} for client {client_id}")
            else:
                logger.warning(f"Failed to delete chat session {session_id} for client {client_id}")
                
        except Exception as e:
            logger.error(f"Delete chat session error for client {client_id}: {e}")
            await self.send_to_client(client_id, {
                "type": "chat_delete_result",
                "payload": {"success": False, "sessionId": payload.get("sessionId"), "error": str(e)}
            })

    async def scan_and_send_file_tree(self, client_id: str, project_path: Path):
        """Scan the project directory and send file tree updates to the client."""
        try:
            for item in project_path.rglob("*"):
                # Skip hidden files and directories
                if any(part.startswith('.') for part in item.parts):
                    continue
                
                relative_path = item.relative_to(project_path)
                
                if item.is_file():
                    try:
                        content = item.read_text(encoding='utf-8')
                        await self.send_to_client(client_id, {
                            "type": "file_tree_update",
                            "payload": {
                                "action": "create",
                                "filePath": str(relative_path).replace("\\", "/"),
                                "fileType": "file",
                                "content": content
                            }
                        })
                    except (UnicodeDecodeError, PermissionError):
                        # Skip binary files or files we can't read
                        continue
                elif item.is_dir():
                    # Send directory creation update
                    await self.send_to_client(client_id, {
                        "type": "file_tree_update",
                        "payload": {
                            "action": "create",
                            "filePath": str(relative_path).replace("\\", "/"),
                            "fileType": "folder"
                        }
                    })
                        
        except Exception as e:
            logger.error(f"Error scanning file tree for client {client_id}: {e}")

    # File system operation handlers for container operations
    async def get_container_for_client(self, client_id: str):
        """Get the active container for a client's project."""
        session = self.clients.get(client_id)
        if not session or not session.project_path:
            return None, "No project path found"
        
        project_id = session.project_path.name
        container = self.container_manager.containers.get(project_id)
        
        if not container:
            return None, "No container found for project"
        
        return container, None
    
    async def handle_file_create(self, client_id: str, payload: Dict[str, Any]):
        """Handle file creation in container."""
        try:
            file_path = payload.get("filePath")
            content = payload.get("content", "")
            
            if not file_path:
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": False, "operation": "create", "path": "", "error": "File path required"}
                })
                return
            
            container, error = await self.get_container_for_client(client_id)
            if error:
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": False, "operation": "create", "path": file_path, "error": error}
                })
                return
            
            # Create file in container
            # First, create parent directories if needed
            dir_path = str(Path(file_path).parent)
            if dir_path != ".":
                mkdir_command = f"mkdir -p {dir_path}"
                exec_result = container.exec_run(mkdir_command, workdir="/workspace")
                if exec_result.exit_code != 0:
                    await self.send_to_client(client_id, {
                        "type": "file_operation_result",
                        "payload": {"success": False, "operation": "create", "path": file_path, "error": f"Failed to create directory: {exec_result.output.decode()}"}
                    })
                    return
            
            # Write file content
            escaped_content = content.replace("'", "'\"'\"'")
            touch_command = f"echo '{escaped_content}' > {file_path}"
            exec_result = container.exec_run(touch_command, workdir="/workspace")
            
            if exec_result.exit_code == 0:
                # Also create in local filesystem for backup
                session = self.clients.get(client_id)
                if session and session.project_path:
                    local_file_path = session.project_path / file_path
                    local_file_path.parent.mkdir(parents=True, exist_ok=True)
                    local_file_path.write_text(content, encoding='utf-8')
                
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": True, "operation": "create", "path": file_path}
                })
                
                # Send file tree update
                await self.send_to_client(client_id, {
                    "type": "file_tree_update",
                    "payload": {
                        "action": "create",
                        "filePath": file_path,
                        "fileType": "file",
                        "content": content
                    }
                })
            else:
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": False, "operation": "create", "path": file_path, "error": exec_result.output.decode()}
                })
                
        except Exception as e:
            logger.error(f"File create error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "file_operation_result",
                "payload": {"success": False, "operation": "create", "path": payload.get("filePath", ""), "error": str(e)}
            })
    
    async def handle_file_read(self, client_id: str, payload: Dict[str, Any]):
        """Handle file read from container."""
        try:
            file_path = payload.get("filePath")
            
            if not file_path:
                await self.send_to_client(client_id, {
                    "type": "file_read_result",
                    "payload": {"success": False, "path": "", "content": None, "error": "File path required"}
                })
                return
            
            container, error = await self.get_container_for_client(client_id)
            if error:
                await self.send_to_client(client_id, {
                    "type": "file_read_result",
                    "payload": {"success": False, "path": file_path, "content": None, "error": error}
                })
                return
            
            # Read file from container
            cat_command = f"cat {file_path}"
            exec_result = container.exec_run(cat_command, workdir="/workspace")
            
            if exec_result.exit_code == 0:
                content = exec_result.output.decode('utf-8')
                await self.send_to_client(client_id, {
                    "type": "file_read_result",
                    "payload": {"success": True, "path": file_path, "content": content}
                })
            else:
                await self.send_to_client(client_id, {
                    "type": "file_read_result",
                    "payload": {"success": False, "path": file_path, "content": None, "error": exec_result.output.decode()}
                })
                
        except Exception as e:
            logger.error(f"File read error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "file_read_result",
                "payload": {"success": False, "path": payload.get("filePath", ""), "content": None, "error": str(e)}
            })
    
    async def handle_file_update(self, client_id: str, payload: Dict[str, Any]):
        """Handle file update in container."""
        try:
            file_path = payload.get("filePath")
            content = payload.get("content", "")
            
            if not file_path:
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": False, "operation": "update", "path": "", "error": "File path required"}
                })
                return
            
            container, error = await self.get_container_for_client(client_id)
            if error:
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": False, "operation": "update", "path": file_path, "error": error}
                })
                return
            
            # Update file in container
            escaped_content = content.replace("'", "'\"'\"'")
            echo_command = f"echo '{escaped_content}' > {file_path}"
            exec_result = container.exec_run(echo_command, workdir="/workspace")
            
            if exec_result.exit_code == 0:
                # Also update local filesystem
                session = self.clients.get(client_id)
                if session and session.project_path:
                    local_file_path = session.project_path / file_path
                    if local_file_path.exists():
                        local_file_path.write_text(content, encoding='utf-8')
                
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": True, "operation": "update", "path": file_path}
                })
                
                # Send file tree update
                await self.send_to_client(client_id, {
                    "type": "file_tree_update",
                    "payload": {
                        "action": "update",
                        "filePath": file_path,
                        "fileType": "file",
                        "content": content
                    }
                })
            else:
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": False, "operation": "update", "path": file_path, "error": exec_result.output.decode()}
                })
                
        except Exception as e:
            logger.error(f"File update error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "file_operation_result",
                "payload": {"success": False, "operation": "update", "path": payload.get("filePath", ""), "error": str(e)}
            })
    
    async def handle_file_delete(self, client_id: str, payload: Dict[str, Any]):
        """Handle file deletion in container."""
        try:
            file_path = payload.get("filePath")
            
            if not file_path:
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": False, "operation": "delete", "path": "", "error": "File path required"}
                })
                return
            
            container, error = await self.get_container_for_client(client_id)
            if error:
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": False, "operation": "delete", "path": file_path, "error": error}
                })
                return
            
            # Delete file from container
            rm_command = f"rm -f {file_path}"
            exec_result = container.exec_run(rm_command, workdir="/workspace")
            
            if exec_result.exit_code == 0:
                # Also delete from local filesystem
                session = self.clients.get(client_id)
                if session and session.project_path:
                    local_file_path = session.project_path / file_path
                    if local_file_path.exists():
                        local_file_path.unlink()
                
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": True, "operation": "delete", "path": file_path}
                })
                
                # Send file tree update
                await self.send_to_client(client_id, {
                    "type": "file_tree_update",
                    "payload": {
                        "action": "delete",
                        "filePath": file_path,
                        "fileType": "file"
                    }
                })
            else:
                await self.send_to_client(client_id, {
                    "type": "file_operation_result",
                    "payload": {"success": False, "operation": "delete", "path": file_path, "error": exec_result.output.decode()}
                })
                
        except Exception as e:
            logger.error(f"File delete error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "file_operation_result",
                "payload": {"success": False, "operation": "delete", "path": payload.get("filePath", ""), "error": str(e)}
            })
    
    async def handle_dir_create(self, client_id: str, payload: Dict[str, Any]):
        """Handle directory creation in container."""
        try:
            dir_path = payload.get("dirPath")
            
            if not dir_path:
                await self.send_to_client(client_id, {
                    "type": "dir_operation_result",
                    "payload": {"success": False, "operation": "create", "path": "", "error": "Directory path required"}
                })
                return
            
            container, error = await self.get_container_for_client(client_id)
            if error:
                await self.send_to_client(client_id, {
                    "type": "dir_operation_result",
                    "payload": {"success": False, "operation": "create", "path": dir_path, "error": error}
                })
                return
            
            # Create directory in container
            mkdir_command = f"mkdir -p {dir_path}"
            exec_result = container.exec_run(mkdir_command, workdir="/workspace")
            
            if exec_result.exit_code == 0:
                # Also create local directory
                session = self.clients.get(client_id)
                if session and session.project_path:
                    local_dir_path = session.project_path / dir_path
                    local_dir_path.mkdir(parents=True, exist_ok=True)
                
                await self.send_to_client(client_id, {
                    "type": "dir_operation_result",
                    "payload": {"success": True, "operation": "create", "path": dir_path}
                })
                
                # Send file tree update
                await self.send_to_client(client_id, {
                    "type": "file_tree_update",
                    "payload": {
                        "action": "create",
                        "filePath": dir_path,
                        "fileType": "folder"
                    }
                })
            else:
                await self.send_to_client(client_id, {
                    "type": "dir_operation_result",
                    "payload": {"success": False, "operation": "create", "path": dir_path, "error": exec_result.output.decode()}
                })
                
        except Exception as e:
            logger.error(f"Directory create error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "dir_operation_result",
                "payload": {"success": False, "operation": "create", "path": payload.get("dirPath", ""), "error": str(e)}
            })
    
    async def handle_dir_list(self, client_id: str, payload: Dict[str, Any]):
        """Handle directory listing in container."""
        try:
            dir_path = payload.get("dirPath", ".")
            
            container, error = await self.get_container_for_client(client_id)
            if error:
                await self.send_to_client(client_id, {
                    "type": "dir_list_result",
                    "payload": {"success": False, "path": dir_path, "items": [], "error": error}
                })
                return
            
            # List directory in container
            ls_command = f"ls -la {dir_path}"
            exec_result = container.exec_run(ls_command, workdir="/workspace")
            
            if exec_result.exit_code == 0:
                output_lines = exec_result.output.decode('utf-8').strip().split('\n')
                items = []
                
                for line in output_lines[1:]:  # Skip total line
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 9:
                            permissions = parts[0]
                            name = ' '.join(parts[8:])
                            if name not in ['.', '..']:
                                items.append({
                                    "name": name,
                                    "type": "directory" if permissions.startswith('d') else "file",
                                    "permissions": permissions,
                                    "size": parts[4] if not permissions.startswith('d') else 0
                                })
                
                await self.send_to_client(client_id, {
                    "type": "dir_list_result",
                    "payload": {"success": True, "path": dir_path, "items": items}
                })
            else:
                await self.send_to_client(client_id, {
                    "type": "dir_list_result",
                    "payload": {"success": False, "path": dir_path, "items": [], "error": exec_result.output.decode()}
                })
                
        except Exception as e:
            logger.error(f"Directory list error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "dir_list_result",
                "payload": {"success": False, "path": payload.get("dirPath", "."), "items": [], "error": str(e)}
            })
    
    async def handle_dir_delete(self, client_id: str, payload: Dict[str, Any]):
        """Handle directory deletion in container."""
        try:
            dir_path = payload.get("dirPath")
            
            if not dir_path:
                await self.send_to_client(client_id, {
                    "type": "dir_operation_result",
                    "payload": {"success": False, "operation": "delete", "path": "", "error": "Directory path required"}
                })
                return
            
            container, error = await self.get_container_for_client(client_id)
            if error:
                await self.send_to_client(client_id, {
                    "type": "dir_operation_result",
                    "payload": {"success": False, "operation": "delete", "path": dir_path, "error": error}
                })
                return
            
            # Delete directory from container
            rm_command = f"rm -rf {dir_path}"
            exec_result = container.exec_run(rm_command, workdir="/workspace")
            
            if exec_result.exit_code == 0:
                # Also delete from local filesystem
                session = self.clients.get(client_id)
                if session and session.project_path:
                    local_dir_path = session.project_path / dir_path
                    if local_dir_path.exists():
                        shutil.rmtree(local_dir_path)
                
                await self.send_to_client(client_id, {
                    "type": "dir_operation_result",
                    "payload": {"success": True, "operation": "delete", "path": dir_path}
                })
                
                # Send file tree update
                await self.send_to_client(client_id, {
                    "type": "file_tree_update",
                    "payload": {
                        "action": "delete",
                        "filePath": dir_path,
                        "fileType": "folder"
                    }
                })
            else:
                await self.send_to_client(client_id, {
                    "type": "dir_operation_result",
                    "payload": {"success": False, "operation": "delete", "path": dir_path, "error": exec_result.output.decode()}
                })
                
        except Exception as e:
            logger.error(f"Directory delete error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "dir_operation_result",
                "payload": {"success": False, "operation": "delete", "path": payload.get("dirPath", ""), "error": str(e)}
            })

    # Project download handler with Socket.IO streaming
    async def handle_download_project(self, client_id: str, payload: Dict[str, Any]):
        """Handle project download request with chunked zip streaming."""
        try:
            session = self.clients.get(client_id)
            if not session or not session.project_path:
                await self.send_to_client(client_id, {
                    "type": "download_error",
                    "payload": {"error": "No project found to download"}
                })
                return
            
            project_path = session.project_path
            project_name = project_path.name
            
            # Create temporary zip file
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
                temp_zip_path = temp_file.name
            
            try:
                # Create zip file
                with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    file_count = 0
                    for file_path in project_path.rglob('*'):
                        if file_path.is_file():
                            # Skip hidden files, temporary files, and common build artifacts
                            if self.should_include_in_zip(file_path, project_path):
                                arcname = file_path.relative_to(project_path)
                                zipf.write(file_path, arcname)
                                file_count += 1
                
                # Get zip file stats
                zip_size = Path(temp_zip_path).stat().st_size
                
                # Calculate checksum
                with open(temp_zip_path, 'rb') as f:
                    zip_content = f.read()
                    checksum = hashlib.sha256(zip_content).hexdigest()
                
                # Send header first
                header = {
                    "name": f"{project_name}.zip",
                    "totalBytes": zip_size,
                    "fileCount": file_count,
                    "createdAt": datetime.now().isoformat(),
                    "checksum": checksum,
                    "chunkSize": 64 * 1024,  # 64KB chunks
                    "version": "1.0"
                }
                
                await self.send_to_client(client_id, {
                    "type": "download_header",
                    "payload": header
                })
                
                # Stream zip file in chunks
                chunk_size = header["chunkSize"]
                chunk_index = 0
                total_chunks = (zip_size + chunk_size - 1) // chunk_size
                
                with open(temp_zip_path, 'rb') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        
                        # Encode chunk as base64 for JSON transport
                        chunk_b64 = base64.b64encode(chunk).decode('utf-8')
                        
                        await self.send_to_client(client_id, {
                            "type": "download_chunk",
                            "payload": {
                                "chunkIndex": chunk_index,
                                "totalChunks": total_chunks,
                                "data": chunk_b64,
                                "size": len(chunk)
                            }
                        })
                        
                        chunk_index += 1
                        
                        # Small delay to prevent overwhelming the client
                        await asyncio.sleep(0.01)
                
                # Send completion message
                await self.send_to_client(client_id, {
                    "type": "download_complete",
                    "payload": {
                        "totalChunks": total_chunks,
                        "totalBytes": zip_size,
                        "checksum": checksum
                    }
                })
                
                logger.info(f"Successfully streamed project download for {client_id}: {project_name} ({zip_size} bytes, {file_count} files)")
                
            finally:
                # Clean up temporary file
                try:
                    Path(temp_zip_path).unlink()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Project download error for {client_id}: {e}", exc_info=True)
            await self.send_to_client(client_id, {
                "type": "download_error",
                "payload": {"error": str(e)}
            })
    
    def should_include_in_zip(self, file_path: Path, project_root: Path) -> bool:
        """Determine if a file should be included in the project zip."""
        relative_path = file_path.relative_to(project_root)
        path_parts = relative_path.parts
        
        # Skip hidden files and directories
        if any(part.startswith('.') for part in path_parts):
            # But include .gitignore and .env.example
            if file_path.name in ['.gitignore', '.env.example']:
                return True
            return False
        
        # Skip common build/dependency directories
        skip_dirs = {
            'node_modules', '__pycache__', '.pytest_cache', 'dist', 'build', 
            'target', '.next', '.nuxt', 'coverage', '.nyc_output', 'venv', 
            'env', '.venv', '.env', 'site-packages'
        }
        
        if any(part in skip_dirs for part in path_parts):
            return False
        
        # Skip common temporary and log files
        skip_patterns = [
            '*.log', '*.tmp', '*.temp', '*.cache', '*.pid', '*.lock',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dylib', '*.dll',
            'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*',
            '.DS_Store', 'Thumbs.db', 'desktop.ini'
        ]
        
        import fnmatch
        for pattern in skip_patterns:
            if fnmatch.fnmatch(file_path.name, pattern):
                return False
        
        # Skip very large files (> 10MB)
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except:
            return False
        
        return True

async def main():
    """Main entry point for the server."""
    server = HMAServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        # Cleanup database background tasks
        try:
            from src.storage.db import stop_cleanup_task
            await stop_cleanup_task()
        except Exception as e:
            logger.error(f"Error stopping cleanup task: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 