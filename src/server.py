"""
Socket.IO server for real-time communication with the HMA-LLM frontend.
Handles agent updates, code streaming, and project management.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Set, Optional, Any, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

import socketio
from aiohttp import web

from src.agents.base_agent import BaseAgent
from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.llm.providers import get_llm_client
from src.messages.protocol import TaskMessage, Task, MessageType
from src import ROOT_DIR

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

async def main():
    """Main entry point for the server."""
    server = HMAServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main()) 