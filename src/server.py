"""
Socket.IO server for real-time communication with the HMA-LLM frontend.
Handles agent updates, code streaming, and project management.
"""

import asyncio
import json
import logging
import uuid
import sys
from typing import Dict, Set, Optional, Any, List, Callable, Awaitable
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

# Add the project root to Python path to enable src imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import socketio
from aiohttp import web

from src.agents.base_agent import BaseAgent
from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.llm.providers import get_llm_client
from src.messages.protocol import TaskMessage, Task, MessageType
from src import ROOT_DIR
from src.config import Language, set_global_language
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
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.sio = socketio.AsyncServer(
            cors_allowed_origins='*',
            async_mode='aiohttp'
        )
        self.app = web.Application()
        self.sio.attach(self.app, socketio_path='/ws')
        
        self.clients: Dict[str, ClientSession] = {}
        self.agents: Dict[str, BaseAgent] = {}
        self.projects: Dict[str, Path] = {}
        
        # Task management - NEW
        self.active_tasks: Dict[str, asyncio.Task] = {}  # Maps client_id to active task
        
        # Project initialization management - NEW
        self.project_initializations: Dict[str, ProjectInitializationManager] = {}  # Maps client_id to initialization manager
        self.pending_approvals: Dict[str, asyncio.Event] = {}  # Maps client_id to approval events
        self.approval_responses: Dict[str, str] = {}  # Maps client_id to approval responses
        
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

async def main():
    """Main entry point for the server."""
    server = HMAServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main()) 