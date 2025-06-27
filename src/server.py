"""
WebSocket server for real-time communication with the HMA-LLM frontend.
Handles agent updates, code streaming, and project management.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Set, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

import websockets
from websockets.server import WebSocketServerProtocol

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
    websocket: WebSocketServerProtocol
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
    """Main server class handling WebSocket connections and agent orchestration."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.clients: Dict[str, ClientSession] = {}
        self.agents: Dict[str, BaseAgent] = {}
        self.projects: Dict[str, Path] = {}
        
    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting HMA-LLM WebSocket server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a new client connection."""
        client_id = str(uuid.uuid4())
        session = ClientSession(websocket=websocket, client_id=client_id)
        self.clients[client_id] = session
        
        logger.info(f"Client {client_id} connected")
        
        try:
            # Send welcome message
            await self.send_to_client(client_id, {
                "type": "message",
                "payload": {
                    "id": str(uuid.uuid4()),
                    "content": "Welcome to HMA-LLM Software Construction! Describe what you want to build.",
                    "sender": "ai",
                    "timestamp": datetime.now().isoformat(),
                    "agentId": "system"
                }
            })
            
            async for message in websocket:
                await self.handle_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            await self.cleanup_client(client_id)
    
    async def handle_message(self, client_id: str, message: str):
        """Handle incoming message from client."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "prompt":
                await self.handle_prompt(client_id, data["payload"])
            elif message_type == "import_project":
                await self.handle_import_project(client_id, data["payload"])
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}")
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
        
        # Create root manager agent if it doesn't exist
        root_agent_id = f"{client_id}_root"
        if root_agent_id not in self.agents:
            llm_client = get_llm_client()
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
        
        # Create task and activate agent
        task = Task(
            task_id=str(uuid.uuid4()),
            task_string=prompt
        )
        
        task_message = TaskMessage(
            message_type=MessageType.DELEGATION,
            sender_id="user",
            recipient_id=root_agent_id,
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
        asyncio.create_task(self.process_agent_task(client_id, root_agent_id, task_message))
    
    async def process_agent_task(self, client_id: str, agent_id: str, task_message: TaskMessage):
        """Process a task for an agent asynchronously."""
        try:
            agent = self.agents[agent_id]
            
            # Send initial processing message
            await self.send_to_client(client_id, {
                "type": "message",
                "payload": {
                    "id": str(uuid.uuid4()),
                    "content": f"Processing: {task_message.task.task_string}",
                    "sender": "ai",
                    "timestamp": datetime.now().isoformat(),
                    "agentId": agent_id
                }
            })
            
            # Process the task with streaming support
            async for update in self.stream_agent_work(agent, task_message):
                if update['type'] == 'code':
                    # Stream code updates
                    await self.send_to_client(client_id, {
                        "type": "code_stream",
                        "payload": {
                            "agentId": update['file_id'],
                            "content": update['content'],
                            "isComplete": update.get('isComplete', False)
                        }
                    })
                elif update['type'] == 'delegation':
                    # Handle child agent creation
                    child_agent_id = update['child_id']
                    if child_agent_id not in self.agents:
                        # Create child agent based on type
                        child_path = Path(agent.path) / update['child_name']
                        if update['agent_type'] == 'manager':
                            child_agent = ManagerAgent(str(child_path), agent.llm_client)
                        else:
                            child_agent = CoderAgent(str(child_path), agent.llm_client)
                        self.agents[child_agent_id] = child_agent
                    
                    # Send delegation update
                    await self.send_to_client(client_id, {
                        "type": "delegation",
                        "payload": {
                            "parentId": agent_id,
                            "childId": child_agent_id,
                            "task": update['task'],
                            "taskMessage": asdict(update['task_message'])
                        }
                    })
            
            # Send completion notification
            await self.send_agent_update(client_id, {
                "agentId": agent_id,
                "status": "inactive",
                "task": None
            })
            
            # Send completion message
            await self.send_to_client(client_id, {
                "type": "message",
                "payload": {
                    "id": str(uuid.uuid4()),
                    "content": f"✅ Task completed successfully!",
                    "sender": "ai",
                    "timestamp": datetime.now().isoformat(),
                    "agentId": agent_id
                }
            })
            
        except Exception as e:
            logger.error(f"Error processing task for agent {agent_id}: {e}")
            
            # Send error notification
            await self.send_agent_update(client_id, {
                "agentId": agent_id,
                "status": "error",
                "task": str(e)
            })
    
    async def handle_import_project(self, client_id: str, payload: Dict[str, Any]):
        """Handle project import request."""
        # For now, just acknowledge the import
        await self.send_to_client(client_id, {
            "type": "message",
            "payload": {
                "id": str(uuid.uuid4()),
                "content": "Project import functionality coming soon!",
                "sender": "ai",
                "timestamp": datetime.now().isoformat(),
                "agentId": "system"
            }
        })
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send a message to a specific client."""
        session = self.clients.get(client_id)
        if session and session.websocket.open:
            try:
                await session.websocket.send(json.dumps(message))
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
        """Stream agent work updates - implement based on your agent logic"""
        # This is a placeholder - implement based on how your agents work
        yield {
            'type': 'code',
            'file_id': 'app-py',
            'content': '# Starting implementation...\n',
            'isComplete': False
        }

async def main():
    """Main entry point for the server."""
    server = HMAServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main()) 