# Complete Frontend-Backend Integration Plan for HMA-LLM

## Overview
This document provides a comprehensive, step-by-step plan to complete the integration between the React frontend and Python Socket.IO backend for the HMA-LLM Software Construction system. The plan is organized into 10 phases with detailed implementation steps, code examples, and testing strategies.

## Current State Assessment
Before starting implementation, verify the following components exist:
- ✅ **Backend**: Socket.IO server in `src/server.py` with basic message routing
- ✅ **Frontend**: React app in `web_app/` with WebSocket service and UI components
- ✅ **Agent System**: Hierarchical agents (Master, Manager, Coder) with DSLs
- ✅ **LLM Integration**: Multi-provider support already connected to frontend
- ❌ **Missing**: Agent response parsing, file operation broadcasting, phase management

## Phase 1: Master Agent Integration (Week 1)

### Alternative: Wrapper Approach (Minimal Backend Changes)

If you want to integrate the Master Agent without modifying the core backend files in `src/`, you can use a wrapper approach that only requires changes to `server.py` and a new wrapper file.

#### Benefits of the Wrapper Approach:
- **No changes to core agent files** - All existing agent implementations remain untouched
- **Backward compatible** - Existing functionality continues to work
- **Easy to remove** - Just delete the wrapper file and remove the import
- **Fallback support** - Works even if Master Agent implementation changes
- **Isolated testing** - Can test the wrapper independently

#### Create Master Agent Wrapper
```python
# src/master_agent_wrapper.py
"""
Wrapper for Master Agent integration without modifying core backend files.
This allows us to use the Master Agent while keeping the existing implementation intact.
"""

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MasterAgentWrapper:
    """
    Wrapper class that interfaces between the server and Master Agent
    without modifying the core agent implementation.
    """
    
    def __init__(self, project_path: Path, llm_client, server_callback):
        self.project_path = project_path
        self.llm_client = llm_client
        self.server_callback = server_callback
        self.phase = "understanding"
        self.understanding_complete = False
        self.conversation_history = []
        self.documentation = ""
        
        # Instead of importing and modifying Master Agent, we'll simulate its behavior
        self.master_agent = None
        self._init_master_agent()
    
    def _init_master_agent(self):
        """Initialize Master Agent without modifying its source."""
        try:
            # Dynamically import to avoid modifying the import structure
            from src.agents.master_agent import MasterAgent
            from src.orchestrator.master_prompter import MasterPrompter
            
            prompter = MasterPrompter()
            self.master_agent = MasterAgent(
                path=str(self.project_path),
                llm_client=self.llm_client,
                prompter=prompter
            )
        except Exception as e:
            logger.warning(f"Could not import Master Agent, using fallback: {e}")
            # Use a fallback implementation if needed
            self.master_agent = None
    
    async def process_understanding_message(self, user_message: str) -> str:
        """Process user message during understanding phase."""
        self.conversation_history.append({"role": "user", "content": user_message})
        
        if self.master_agent:
            # Use the actual Master Agent if available
            try:
                # Call Master Agent's method through reflection to avoid tight coupling
                if hasattr(self.master_agent, 'process_message'):
                    response = await self.master_agent.process_message(user_message)
                else:
                    # Fallback to LLM directly
                    response = await self._direct_llm_call(user_message)
            except Exception as e:
                logger.error(f"Error calling Master Agent: {e}")
                response = await self._direct_llm_call(user_message)
        else:
            # Fallback implementation
            response = await self._direct_llm_call(user_message)
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    async def _direct_llm_call(self, user_message: str) -> str:
        """Direct LLM call as fallback."""
        prompt = f"""You are a Master Agent helping to understand project requirements.
        
Previous conversation:
{self._format_conversation()}

User: {user_message}

Ask clarifying questions to understand:
1. The main functionality needed
2. Technical requirements and constraints
3. User interface requirements
4. Any specific features or integrations

Response:"""
        
        response = await self.llm_client.generate_response(
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7
        )
        return response
    
    def _format_conversation(self) -> str:
        """Format conversation history."""
        return "\n".join([
            f"{msg['role'].title()}: {msg['content']}" 
            for msg in self.conversation_history[-10:]  # Last 10 messages
        ])
    
    async def is_understanding_complete(self) -> bool:
        """Check if we have enough understanding to proceed."""
        # Simple heuristic: after 5+ exchanges, check if we have enough info
        if len(self.conversation_history) < 6:
            return False
        
        # Ask LLM if we have enough information
        check_prompt = f"""Based on this conversation, do we have enough information to start building the project?

{self._format_conversation()}

Answer with YES if we have enough information about:
- Main functionality
- Technical stack
- Basic requirements

Answer with NO if we need more clarification.

Answer (YES/NO):"""
        
        response = await self.llm_client.generate_response(
            messages=[{"role": "system", "content": check_prompt}],
            temperature=0.1
        )
        
        return "YES" in response.upper()
    
    async def generate_documentation(self) -> str:
        """Generate documentation from understanding phase."""
        doc_prompt = f"""Generate a documentation.md file based on this project discussion:

{self._format_conversation()}

Include:
1. Project Overview
2. Key Requirements
3. Technical Specifications
4. Features to Implement

Format as markdown:"""
        
        self.documentation = await self.llm_client.generate_response(
            messages=[{"role": "system", "content": doc_prompt}],
            temperature=0.7
        )
        
        # Save documentation
        doc_path = self.project_path / "documentation.md"
        doc_path.write_text(self.documentation)
        
        return self.documentation
    
    async def create_project_structure(self) -> Dict[str, Any]:
        """Create project structure based on understanding."""
        structure_prompt = f"""Based on this project documentation, create a project structure:

{self.documentation}

List the directories and files needed in this format:
- src/ (directory)
- src/components/ (directory)
- src/App.tsx (file)
- package.json (file)

Project structure:"""
        
        structure_response = await self.llm_client.generate_response(
            messages=[{"role": "system", "content": structure_prompt}],
            temperature=0.7
        )
        
        # Parse and create structure
        created_items = []
        for line in structure_response.strip().split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            # Parse path and type
            parts = line[1:].strip().split(' ')
            if len(parts) >= 2 and '(' in parts[-1]:
                path = ' '.join(parts[:-1])
                item_type = parts[-1].strip('()')
                
                full_path = self.project_path / path
                
                if item_type == 'directory':
                    full_path.mkdir(parents=True, exist_ok=True)
                elif item_type == 'file':
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    if not full_path.exists():
                        full_path.touch()
                
                created_items.append({
                    "path": path,
                    "type": item_type
                })
        
        return {
            "created": created_items,
            "structure": structure_response
        }
```

#### Minimal Changes to server.py
```python
# In server.py - Add import at the top
from .master_agent_wrapper import MasterAgentWrapper

# In run_project_initialization method, replace the direct Master Agent usage:
async def run_project_initialization(self, client_id: str, init_manager: ProjectInitializationManager):
    """Run project initialization with Master Agent wrapper."""
    try:
        # Create wrapper instead of direct Master Agent
        master_wrapper = MasterAgentWrapper(
            project_path=init_manager.project_path,
            llm_client=get_llm_client(init_manager.server.clients[client_id].llm_model),
            server_callback=lambda msg: asyncio.create_task(
                init_manager.send_chat_message(msg)
            )
        )
        
        # Phase 1: Understanding
        await init_manager.send_chat_message(
            "Let me understand your project requirements. What specific features and functionality do you need?"
        )
        
        # Process user messages
        while not await master_wrapper.is_understanding_complete():
            try:
                user_message = await asyncio.wait_for(
                    init_manager.message_queue.get(),
                    timeout=300.0  # 5 minute timeout
                )
                
                response = await master_wrapper.process_understanding_message(user_message)
                await init_manager.send_chat_message(response)
                
            except asyncio.TimeoutError:
                await init_manager.send_chat_message(
                    "Are you still there? Please let me know if you need more time or if you'd like to continue."
                )
        
        # Generate documentation
        await init_manager.send_status_update(
            phase=1,
            phase_title="Product Understanding",
            status="completed",
            message="I've gathered enough information. Let me document the requirements."
        )
        
        documentation = await master_wrapper.generate_documentation()
        
        # Phase 2: Structure
        await init_manager.send_status_update(
            phase=2,
            phase_title="Project Structure",
            status="active",
            message="Creating project structure based on requirements...",
            requires_approval=True
        )
        
        # Wait for approval
        await self.wait_for_approval(client_id)
        
        # Create structure
        structure_result = await master_wrapper.create_project_structure()
        
        # Send file tree updates
        for item in structure_result["created"]:
            await self.send_to_client(client_id, {
                "type": "file_tree_update",
                "payload": {
                    "action": "create",
                    "filePath": item["path"],
                    "fileType": "folder" if item["type"] == "directory" else "file"
                }
            })
        
        # Phase 3: Continue with existing manager/coder flow
        await init_manager.send_status_update(
            phase=3,
            phase_title="Implementation",
            status="active",
            message="Ready to start implementation with the agent hierarchy.",
            requires_approval=True
        )
        
        # After approval, continue with normal flow...
        
    except Exception as e:
        logger.error(f"Error in project initialization: {e}")
        await init_manager.send_chat_message(f"Error: {str(e)}")
```

#### Alternative: Proxy Pattern
For even more isolation, you can create a proxy that intercepts and modifies behavior:

```python
# src/master_agent_proxy.py
class MasterAgentProxy:
    """Proxy that adds Master Agent behavior to existing agents."""
    
    def __init__(self, manager_agent, llm_client):
        self.manager_agent = manager_agent
        self.llm_client = llm_client
        self.phase = "understanding"
    
    def __getattr__(self, name):
        """Proxy all other calls to the underlying manager agent."""
        return getattr(self.manager_agent, name)
    
    async def process_with_phases(self, task_message):
        """Add phase-based processing on top of normal manager behavior."""
        # Phase 1: Understanding (handled before this)
        # Phase 2: Structure (handled before this)
        # Phase 3: Delegation - use normal manager behavior
        return await self.manager_agent.process_task(task_message)
```

### Step 1: Update Server Message Routing

#### 1.1 Import Required Modules
```python
# In src/server.py, add to imports
from src.agents.master_agent import MasterAgent
from src.orchestrator.master_prompter import MasterPrompter
from typing import Literal

# Phase type definition
PhaseType = Literal['understanding', 'structure', 'delegation', 'completed']
```

#### 1.2 Enhance ClientSession Dataclass
```python
@dataclass
class ClientSession:
    """Represents a connected client session."""
    sid: str
    client_id: str
    project_path: Optional[Path] = None
    llm_model: str = "gpt-4o"
    llm_config: Dict[str, Any] = field(default_factory=dict)
    # New Master Agent fields
    master_agent: Optional[MasterAgent] = None
    current_phase: Optional[PhaseType] = None
    phase_data: Dict[str, Any] = field(default_factory=dict)
    phase_approved: bool = False
    understanding_context: List[Dict[str, str]] = field(default_factory=list)
```

#### 1.3 Modify handle_start_project_init Method
```python
async def handle_start_project_init(self, client_id: str, payload: Dict[str, Any]):
    """Initialize a new project with Master Agent workflow."""
    try:
        session = self.clients.get(client_id)
        if not session:
            return
        
        # Create project directory
        project_name = payload.get("projectName", f"project_{int(time.time())}")
        project_path = Path("generated_projects") / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Update session
        session.project_path = project_path
        session.current_phase = "understanding"
        session.phase_approved = False
        
        # Create Master Agent
        llm_client = get_llm_client(session.llm_model)
        master_prompter = MasterPrompter()
        
        session.master_agent = MasterAgent(
            project_path=str(project_path),
            llm_client=llm_client,
            prompter=master_prompter
        )
        
        # Store in agents dict
        master_agent_id = f"{client_id}_master"
        self.agents[master_agent_id] = session.master_agent
        
        # Send phase update to frontend
        await self.send_phase_update(client_id, "understanding", {
            "message": "Let's understand your project requirements. I'll ask you some questions to ensure I fully understand what you want to build.",
            "requiresApproval": False
        })
        
        # Send initial message
        await self.send_to_client(client_id, {
            "type": "message",
            "payload": {
                "id": str(uuid.uuid4()),
                "content": "Hello! I'm ready to help you build your project. Let me start by understanding what you'd like to create. What kind of application or system are you looking to build?",
                "sender": "ai",
                "timestamp": datetime.now().isoformat(),
                "agentId": master_agent_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error initializing project for {client_id}: {e}")
        await self.send_error(client_id, str(e))
```

#### 1.4 Update handle_prompt Method
```python
async def handle_prompt(self, client_id: str, payload: Dict[str, Any]):
    """Handle prompts with Master Agent phase awareness."""
    try:
        session = self.clients.get(client_id)
        if not session:
            return
        
        prompt = payload.get("prompt", "")
        agent_id = payload.get("agentId", "root")
        
        # Phase 1: Understanding - Route to Master Agent
        if session.master_agent and session.current_phase == "understanding":
            # Store conversation history
            session.understanding_context.append({
                "role": "user",
                "content": prompt
            })
            
            # Get response from Master Agent
            master_agent_id = f"{client_id}_master"
            response = await session.master_agent.process_understanding_message(prompt)
            
            # Store AI response
            session.understanding_context.append({
                "role": "assistant", 
                "content": response
            })
            
            # Check if understanding is complete
            if await session.master_agent.is_understanding_complete():
                # Generate documentation
                await session.master_agent.generate_documentation()
                
                # Transition to structure phase
                session.current_phase = "structure"
                await self.send_phase_update(client_id, "structure", {
                    "message": "I've understood your requirements. Now I'll create the project structure.",
                    "requiresApproval": True,
                    "documentation": await session.master_agent.get_documentation_summary()
                })
            else:
                # Send response
                await self.send_to_client(client_id, {
                    "type": "message",
                    "payload": {
                        "id": str(uuid.uuid4()),
                        "content": response,
                        "sender": "ai",
                        "timestamp": datetime.now().isoformat(),
                        "agentId": master_agent_id
                    }
                })
        
        # Phase 2: Structure - Master Agent creates structure
        elif session.master_agent and session.current_phase == "structure":
            if session.phase_approved:
                await session.master_agent.create_project_structure()
                
                # Transition to delegation
                session.current_phase = "delegation"
                session.phase_approved = False
                
                await self.send_phase_update(client_id, "delegation", {
                    "message": "Project structure created. Ready to start implementation.",
                    "requiresApproval": True
                })
        
        # Phase 3: Delegation - Master Agent delegates to managers
        elif session.master_agent and session.current_phase == "delegation":
            if session.phase_approved:
                # Create root manager and start delegation
                await session.master_agent.start_delegation(prompt)
                
                # Continue with normal agent flow
                # ... existing prompt handling code ...
        
        # Normal operation (post-phase workflow) or direct agent communication
        else:
            # Handle direct agent responses and parse for file operations
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                
                # Send prompt to agent and get response
                response = await agent.process_message(prompt)
                
                # CRITICAL: Parse response for file operations and broadcast
                await self.parse_agent_responses_and_broadcast(client_id, agent_id, response)
                
                # Send chat response to frontend
                await self.send_to_client(client_id, {
                    "type": "message",
                    "payload": {
                        "id": str(uuid.uuid4()),
                        "content": response,
                        "sender": "ai",
                        "timestamp": datetime.now().isoformat(),
                        "agentId": agent_id
                    }
                })
            else:
                # Handle case where agent doesn't exist
                await self.send_error(client_id, f"Agent {agent_id} not found")
            
    except Exception as e:
        logger.error(f"Error handling prompt from {client_id}: {e}")
        await self.send_error(client_id, str(e))
```

### Step 2: Implement Phase Management

#### 2.1 Create Phase Update Method
```python
async def send_phase_update(self, client_id: str, phase: PhaseType, data: Dict[str, Any]):
    """Send phase update to frontend."""
    await self.send_to_client(client_id, {
        "type": "phase_update",
        "payload": {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            **data
        }
    })
```

#### 2.2 Update Phase Approval Handlers
```python
async def handle_approve_phase(self, client_id: str, payload: Dict[str, Any]):
    """Handle phase approval from frontend."""
    try:
        session = self.clients.get(client_id)
        if not session:
            return
        
        phase = payload.get("phase")
        if phase != session.current_phase:
            await self.send_error(client_id, "Phase mismatch")
            return
        
        session.phase_approved = True
        
        # Trigger next phase action
        if phase == "structure":
            # Create structure
            await self.handle_prompt(client_id, {"prompt": "", "agentId": "master"})
        elif phase == "delegation":
            # Start implementation
            initial_prompt = payload.get("prompt", "Start building the project")
            await self.handle_prompt(client_id, {"prompt": initial_prompt, "agentId": "master"})
        
    except Exception as e:
        logger.error(f"Error approving phase for {client_id}: {e}")
        await self.send_error(client_id, str(e))

async def handle_reject_phase(self, client_id: str, payload: Dict[str, Any]):
    """Handle phase rejection from frontend."""
    try:
        session = self.clients.get(client_id)
        if not session:
            return
        
        phase = payload.get("phase")
        reason = payload.get("reason", "")
        
        if phase == "structure":
            # Go back to understanding
            session.current_phase = "understanding"
            await self.send_phase_update(client_id, "understanding", {
                "message": f"Let me revise my understanding. You mentioned: {reason}",
                "requiresApproval": False
            })
        elif phase == "delegation":
            # Revise structure
            session.current_phase = "structure"
            await self.send_phase_update(client_id, "structure", {
                "message": f"Let me revise the project structure based on your feedback: {reason}",
                "requiresApproval": True
            })
        
    except Exception as e:
        logger.error(f"Error rejecting phase for {client_id}: {e}")
        await self.send_error(client_id, str(e))
```

### Step 3: Frontend Phase Display Components

#### 3.1 Create PhaseIndicator Component
```typescript
// web_app/components/PhaseIndicator.tsx
import { useState, useEffect } from 'react';
import { CheckCircle, Circle, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { useSocketEvent } from '../hooks/useSocketEvent';

interface Phase {
  id: 'understanding' | 'structure' | 'delegation' | 'completed';
  name: string;
  description: string;
}

const phases: Phase[] = [
  { id: 'understanding', name: 'Understanding', description: 'Gathering project requirements' },
  { id: 'structure', name: 'Structure', description: 'Creating project architecture' },
  { id: 'delegation', name: 'Implementation', description: 'Building your project' },
  { id: 'completed', name: 'Completed', description: 'Project ready' }
];

export function PhaseIndicator() {
  const [currentPhase, setCurrentPhase] = useState<Phase['id']>('understanding');
  const [phaseData, setPhaseData] = useState<any>({});
  const [requiresApproval, setRequiresApproval] = useState(false);

  useSocketEvent('phase_update', (update) => {
    setCurrentPhase(update.phase);
    setPhaseData(update);
    setRequiresApproval(update.requiresApproval || false);
  });

  const handleApprove = () => {
    websocketService.send({
      type: 'approve_phase',
      payload: { phase: currentPhase }
    });
  };

  const handleReject = () => {
    const reason = prompt('Please provide feedback for revision:');
    if (reason) {
      websocketService.send({
        type: 'reject_phase',
        payload: { phase: currentPhase, reason }
      });
    }
  };

  return (
    <div className="p-4 border-b">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium">Project Phases</h3>
        {requiresApproval && (
          <div className="flex gap-2">
            <Button size="sm" onClick={handleApprove}>Approve</Button>
            <Button size="sm" variant="outline" onClick={handleReject}>Revise</Button>
          </div>
        )}
      </div>
      
      <div className="flex items-center space-x-2">
        {phases.map((phase, index) => {
          const isActive = phase.id === currentPhase;
          const isCompleted = phases.findIndex(p => p.id === currentPhase) > index;
          
          return (
            <div key={phase.id} className="flex items-center">
              <div className={`flex flex-col items-center ${isActive ? 'text-primary' : ''}`}>
                {isCompleted ? (
                  <CheckCircle className="h-6 w-6 text-green-500" />
                ) : isActive ? (
                  <Loader2 className="h-6 w-6 animate-spin" />
                ) : (
                  <Circle className="h-6 w-6 text-muted-foreground" />
                )}
                <span className="text-xs mt-1">{phase.name}</span>
              </div>
              {index < phases.length - 1 && (
                <div className={`h-0.5 w-12 mx-2 ${isCompleted ? 'bg-green-500' : 'bg-muted'}`} />
              )}
            </div>
          );
        })}
      </div>
      
      {phaseData.message && (
        <div className="mt-4 p-3 bg-muted rounded-md">
          <p className="text-sm">{phaseData.message}</p>
        </div>
      )}
    </div>
  );
}
```

## Phase 2: Terminal Integration (Week 1-2)

### Step 1: Wire ContainerManager to Agents

#### 1.1 Create TerminalManager Class
```python
# src/terminal/terminal_manager.py
from typing import Dict, Optional
import asyncio
from .container_manager import ContainerManager
from .terminal_session import TerminalSession

class TerminalManager:
    """Manages terminal sessions for agents."""
    
    def __init__(self, container_manager: ContainerManager):
        self.container_manager = container_manager
        self.sessions: Dict[str, TerminalSession] = {}
        self.agent_sessions: Dict[str, str] = {}  # agent_id -> session_id
    
    async def get_or_create_session(self, agent_id: str, project_path: str) -> TerminalSession:
        """Get existing or create new terminal session for agent."""
        if agent_id in self.agent_sessions:
            session_id = self.agent_sessions[agent_id]
            if session_id in self.sessions:
                return self.sessions[session_id]
        
        # Create new session
        session = await self.container_manager.create_workspace_container(
            project_id=agent_id,
            workspace_path=project_path
        )
        
        self.sessions[session.session_id] = session
        self.agent_sessions[agent_id] = session.session_id
        
        return session
    
    async def execute_command(self, agent_id: str, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute command for agent and return output."""
        if agent_id not in self.agent_sessions:
            raise ValueError(f"No terminal session for agent {agent_id}")
        
        session_id = self.agent_sessions[agent_id]
        session = self.sessions.get(session_id)
        
        if not session:
            raise ValueError(f"Terminal session {session_id} not found")
        
        # Execute command
        result = await self.container_manager.exec_command(
            session_id=session_id,
            command=command,
            timeout=timeout
        )
        
        return {
            "success": result.get("exit_code", 1) == 0,
            "output": result.get("output", ""),
            "error": result.get("error", ""),
            "exit_code": result.get("exit_code", 1)
        }
    
    async def cleanup_agent_sessions(self, agent_id: str):
        """Clean up terminal sessions for an agent."""
        if agent_id in self.agent_sessions:
            session_id = self.agent_sessions[agent_id]
            await self.container_manager.stop_container(session_id)
            del self.sessions[session_id]
            del self.agent_sessions[agent_id]
```

#### 1.2 Update HMAServer to Include TerminalManager
```python
# In src/server.py __init__ method
from src.terminal.terminal_manager import TerminalManager

class HMAServer:
    def __init__(self):
        # ... existing initialization ...
        self.container_manager = ContainerManager()
        self.terminal_manager = TerminalManager(self.container_manager)
```

### Step 2: Update Agent DSL for Terminal Support

#### 2.1 Update Coder Language Grammar
```lark
// src/languages/coder_language/grammar.lark
// Add to existing grammar
command: run_command | run_tests | install_dependencies

run_command: "run_command(" STRING ")"
run_tests: "run_tests(" STRING? ")"
install_dependencies: "install_dependencies(" STRING ")"

// Example usage:
// run_command("npm install")
// run_tests("src/components")
// install_dependencies("package.json")
```

#### 2.2 Add Terminal AST Nodes
```python
# src/languages/coder_language/ast.py
# Add new node classes

@dataclass
class RunCommandNode(ASTNode):
    """Run a shell command."""
    command: str

@dataclass
class RunTestsNode(ASTNode):
    """Run tests for a specific path or entire project."""
    path: Optional[str] = None

@dataclass
class InstallDependenciesNode(ASTNode):
    """Install project dependencies."""
    file_path: str  # package.json, requirements.txt, etc.
```

#### 2.3 Update Interpreter
```python
# src/languages/coder_language/interpreter.py
# Add to CoderInterpreter class

async def visit_RunCommandNode(self, node: RunCommandNode) -> CommandResult:
    """Execute a shell command."""
    try:
        # Get terminal manager from context
        terminal_manager = self.context.get("terminal_manager")
        if not terminal_manager:
            return CommandResult(
                success=False,
                message="Terminal not available",
                data={}
            )
        
        # Execute command
        agent_id = self.context.get("agent_id")
        result = await terminal_manager.execute_command(
            agent_id=agent_id,
            command=node.command
        )
        
        return CommandResult(
            success=result["success"],
            message=result["output"],
            data={
                "exit_code": result["exit_code"],
                "error": result["error"]
            }
        )
        
    except Exception as e:
        return CommandResult(
            success=False,
            message=f"Command execution failed: {str(e)}",
            data={}
        )

async def visit_RunTestsNode(self, node: RunTestsNode) -> CommandResult:
    """Run project tests."""
    # Detect test framework and run appropriate command
    project_path = self.context.get("project_path")
    
    # Check for test configuration files
    if (Path(project_path) / "package.json").exists():
        command = "npm test"
        if node.path:
            command += f" -- {node.path}"
    elif (Path(project_path) / "pytest.ini").exists():
        command = f"pytest {node.path or '.'}"
    elif (Path(project_path) / "Cargo.toml").exists():
        command = "cargo test"
    else:
        command = "echo 'No test framework detected'"
    
    return await self.visit_RunCommandNode(RunCommandNode(command=command))
```

### Step 3: Frontend Terminal Integration

#### 3.1 Update Terminal Component for Multi-Session
```typescript
// web_app/components/Terminal.tsx
import { useState, useEffect, useRef } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import { useSocketEvent } from '../hooks/useSocketEvent';
import websocketService from '../services/websocket';

interface TerminalSession {
  sessionId: string;
  projectId: string;
  status: 'starting' | 'running' | 'stopped' | 'error';
}

export function Terminal({ projectId }: { projectId: string }) {
  const [sessions, setSessions] = useState<Map<string, TerminalSession>>(new Map());
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  
  // Handle terminal session updates
  useSocketEvent('terminal_session', (session: TerminalSession) => {
    setSessions(prev => {
      const updated = new Map(prev);
      updated.set(session.sessionId, session);
      return updated;
    });
    
    // Auto-activate first session
    if (!activeSessionId && session.status === 'running') {
      setActiveSessionId(session.sessionId);
    }
  });
  
  // Handle terminal data
  useSocketEvent('terminal_data', (data: { sessionId: string; data: string }) => {
    if (data.sessionId === activeSessionId && xtermRef.current) {
      xtermRef.current.write(data.data);
    }
  });
  
  // Create terminal on mount
  useEffect(() => {
    if (!projectId) return;
    
    websocketService.createTerminalSession(projectId);
  }, [projectId]);
  
  // Initialize xterm when session is active
  useEffect(() => {
    if (!activeSessionId || !terminalRef.current) return;
    
    const term = new XTerm({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Consolas, "Courier New", monospace',
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
      }
    });
    
    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();
    
    term.loadAddon(fitAddon);
    term.loadAddon(webLinksAddon);
    term.open(terminalRef.current);
    fitAddon.fit();
    
    // Handle input
    term.onData((data) => {
      websocketService.sendTerminalData(activeSessionId, data);
    });
    
    // Handle resize
    const handleResize = () => {
      fitAddon.fit();
      const { cols, rows } = term;
      websocketService.resizeTerminal(activeSessionId, cols, rows);
    };
    
    window.addEventListener('resize', handleResize);
    xtermRef.current = term;
    
    return () => {
      window.removeEventListener('resize', handleResize);
      term.dispose();
      xtermRef.current = null;
    };
  }, [activeSessionId]);
  
  return (
    <div className="h-full flex flex-col bg-background">
      {/* Terminal tabs for multiple sessions */}
      <div className="flex border-b">
        {Array.from(sessions.values()).map(session => (
          <button
            key={session.sessionId}
            onClick={() => setActiveSessionId(session.sessionId)}
            className={`px-4 py-2 text-sm ${
              activeSessionId === session.sessionId 
                ? 'bg-primary text-primary-foreground' 
                : 'hover:bg-muted'
            }`}
          >
            Terminal {session.sessionId.slice(0, 8)}
          </button>
        ))}
      </div>
      
      {/* Terminal content */}
      <div ref={terminalRef} className="flex-1" />
    </div>
  );
}
```

## Critical Implementation Gap: File Operation Integration

**Current Status**: The architecture for LLM agents to edit files exists but has a key integration gap in `server.py`.

### The Missing Link

While the system has:
- ✅ **Agent DSLs** - Languages for file operations (CHANGE, CREATE, DELETE)
- ✅ **File Operation Interpreters** - Execute file changes on disk
- ✅ **Frontend Components** - FileTree and CodeEditor display
- ✅ **WebSocket Infrastructure** - Real-time communication

**The gap is**: Agent responses containing file operations are not being parsed and converted to WebSocket events for the frontend.

### What Needs Implementation

The server needs to:

1. **Parse Agent Responses** - Extract file operations from agent language commands
2. **Execute File Operations** - Use the existing interpreters to perform changes
3. **Broadcast Updates** - Send `file_tree_update` events to frontend

```python
# In server.py - Missing integration
async def parse_agent_response(self, agent_response: str, agent_id: str, client_id: str):
    """Parse agent response and extract file operations."""
    
    # Example: Agent responds with "CHANGE CONTENT=new_code"
    if "CHANGE CONTENT=" in agent_response:
        # Extract content and file path
        content = extract_content(agent_response)
        file_path = agent.get_file_path()
        
        # Execute file change
        with open(file_path, 'w') as f:
            f.write(content)
        
        # Broadcast to frontend
        await self.send_to_client(client_id, {
            "type": "file_tree_update",
            "payload": {
                "action": "update",
                "filePath": str(file_path),
                "fileType": "file",
                "content": content
            }
        })
```

### Implementation Priority

This gap should be addressed **immediately after Master Agent integration** as it's essential for users to see agent file modifications in real-time.

### Required Server.py Changes

The following methods need to be added to `HMAServer` class:

```python
async def parse_agent_responses_and_broadcast(self, client_id: str, agent_id: str, response: str):
    """Parse agent responses for file operations and broadcast to frontend."""
    try:
        # Import language parsers
        from src.languages.coder_language.parser import CoderParser
        from src.languages.manager_language.parser import ManagerParser
        
        # Determine agent type and use appropriate parser
        if "coder" in agent_id.lower():
            parser = CoderParser()
            ast = parser.parse(response)
            
            # Execute and broadcast file operations
            for node in ast.directives:
                if node.type == "CHANGE":
                    await self.handle_coder_file_change(client_id, agent_id, node)
                elif node.type == "CREATE":
                    await self.handle_file_creation(client_id, agent_id, node)
        
        elif "manager" in agent_id.lower():
            parser = ManagerParser()
            ast = parser.parse(response)
            
            # Execute and broadcast directory operations
            for action in ast.actions:
                if action.type == "CREATE":
                    await self.handle_manager_create(client_id, agent_id, action)
                elif action.type == "DELETE":
                    await self.handle_manager_delete(client_id, agent_id, action)
    
    except Exception as e:
        logger.error(f"Error parsing agent response: {e}")

async def handle_coder_file_change(self, client_id: str, agent_id: str, change_node):
    """Handle coder agent file changes."""
    agent = self.agents.get(agent_id)
    if not agent:
        return
    
    # Get file path from agent
    file_path = Path(agent.path) / agent.own_file
    
    # Write content to disk
    file_path.write_text(change_node.content)
    
    # Broadcast to frontend
    await self.send_to_client(client_id, {
        "type": "file_tree_update",
        "payload": {
            "action": "update",
            "filePath": str(file_path.relative_to(self.clients[client_id].project_path)),
            "fileType": "file",
            "content": change_node.content,
            "agentId": agent_id
        }
    })
```

## Phase 3: Real-time Code Streaming (Week 2)

### Step 1: Implement StreamManager

#### 1.1 Create StreamManager Class
```python
# src/streaming/stream_manager.py
import asyncio
from typing import Optional, Callable, Awaitable
from datetime import datetime

class StreamManager:
    """Manages code streaming from agents to frontend."""
    
    def __init__(self, send_callback: Callable[[str, dict], Awaitable[None]]):
        self.send_callback = send_callback
        self.active_streams: Dict[str, asyncio.Task] = {}
    
    async def stream_code(
        self, 
        client_id: str,
        agent_id: str, 
        file_path: str, 
        content: str, 
        syntax: str = "plaintext",
        chunk_size: int = 100,
        delay: float = 0.05
    ):
        """Stream code content to frontend in chunks."""
        stream_id = f"{agent_id}:{file_path}"
        
        # Cancel existing stream for this file
        if stream_id in self.active_streams:
            self.active_streams[stream_id].cancel()
        
        # Create streaming task
        task = asyncio.create_task(
            self._stream_content(
                client_id, agent_id, file_path, 
                content, syntax, chunk_size, delay
            )
        )
        self.active_streams[stream_id] = task
        
        try:
            await task
        finally:
            self.active_streams.pop(stream_id, None)
    
    async def _stream_content(
        self,
        client_id: str,
        agent_id: str,
        file_path: str,
        content: str,
        syntax: str,
        chunk_size: int,
        delay: float
    ):
        """Internal method to stream content."""
        # Send stream start
        await self.send_callback(client_id, {
            "type": "code_stream",
            "payload": {
                "agentId": agent_id,
                "filePath": file_path,
                "content": "",
                "isComplete": False,
                "syntax": syntax,
                "action": "start"
            }
        })
        
        # Stream chunks
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            
            await self.send_callback(client_id, {
                "type": "code_stream",
                "payload": {
                    "agentId": agent_id,
                    "filePath": file_path,
                    "content": chunk,
                    "isComplete": False,
                    "syntax": syntax,
                    "action": "append"
                }
            })
            
            await asyncio.sleep(delay)
        
        # Send completion
        await self.send_callback(client_id, {
            "type": "code_stream",
            "payload": {
                "agentId": agent_id,
                "filePath": file_path,
                "content": "",
                "isComplete": True,
                "syntax": syntax,
                "action": "complete"
            }
        })
```

#### 1.2 Integrate StreamManager with Agents
```python
# Update src/agents/coder_agent.py
class CoderAgent(BaseAgent):
    def __init__(self, path: str, parent: Optional[BaseAgent], llm_client, stream_manager: Optional[StreamManager] = None):
        super().__init__(path, parent, llm_client)
        self.stream_manager = stream_manager
    
    async def write_code(self, file_path: str, content: str, syntax: str = "typescript"):
        """Write code with streaming support."""
        # Write to file system
        full_path = Path(self.path) / file_path
        full_path.write_text(content)
        
        # Stream to frontend if available
        if self.stream_manager and hasattr(self, 'client_id'):
            await self.stream_manager.stream_code(
                client_id=self.client_id,
                agent_id=self.agent_id,
                file_path=str(full_path),
                content=content,
                syntax=syntax
            )
```

### Step 2: Frontend Streaming Display

#### 2.1 Update CodeEditor for Streaming
```typescript
// web_app/components/CodeEditor.tsx
import { useState, useEffect, useRef } from 'react';
import { Editor } from '@monaco-editor/react';
import { useSocketEvent } from '../hooks/useSocketEvent';

interface StreamingFile {
  path: string;
  content: string;
  isStreaming: boolean;
  syntax: string;
}

export function CodeEditor({ filePath, onSave }: { filePath: string; onSave?: (content: string) => void }) {
  const [streamingFiles, setStreamingFiles] = useState<Map<string, StreamingFile>>(new Map());
  const [content, setContent] = useState('');
  const editorRef = useRef<any>(null);
  
  // Handle code streaming
  useSocketEvent('code_stream', (stream) => {
    const { filePath, content: chunk, isComplete, syntax, action } = stream;
    
    setStreamingFiles(prev => {
      const updated = new Map(prev);
      const existing = updated.get(filePath) || { path: filePath, content: '', isStreaming: true, syntax };
      
      switch (action) {
        case 'start':
          updated.set(filePath, { ...existing, content: '', isStreaming: true });
          break;
        case 'append':
          updated.set(filePath, { ...existing, content: existing.content + chunk });
          break;
        case 'complete':
          updated.set(filePath, { ...existing, isStreaming: false });
          break;
      }
      
      return updated;
    });
  });
  
  // Update editor content when streaming
  useEffect(() => {
    const streamingFile = streamingFiles.get(filePath);
    if (streamingFile) {
      setContent(streamingFile.content);
      
      // Scroll to bottom during streaming
      if (streamingFile.isStreaming && editorRef.current) {
        const editor = editorRef.current;
        const model = editor.getModel();
        const lastLine = model.getLineCount();
        editor.revealLine(lastLine);
      }
    }
  }, [streamingFiles, filePath]);
  
  return (
    <div className="h-full relative">
      {streamingFiles.get(filePath)?.isStreaming && (
        <div className="absolute top-2 right-2 z-10">
          <div className="flex items-center gap-2 bg-primary/10 px-3 py-1 rounded-full">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <span className="text-xs">AI is writing...</span>
          </div>
        </div>
      )}
      
      <Editor
        path={filePath}
        value={content}
        language={detectLanguage(filePath)}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          wordWrap: 'on',
          automaticLayout: true,
          scrollBeyondLastLine: false,
        }}
        onMount={(editor) => {
          editorRef.current = editor;
        }}
        onChange={(value) => {
          setContent(value || '');
        }}
      />
    </div>
  );
}

function detectLanguage(filePath: string): string {
  const ext = filePath.split('.').pop()?.toLowerCase();
  const languageMap: Record<string, string> = {
    ts: 'typescript',
    tsx: 'typescript',
    js: 'javascript',
    jsx: 'javascript',
    py: 'python',
    java: 'java',
    cpp: 'cpp',
    c: 'c',
    h: 'c',
    cs: 'csharp',
    go: 'go',
    rs: 'rust',
    php: 'php',
    rb: 'ruby',
    swift: 'swift',
    kt: 'kotlin',
    scala: 'scala',
    r: 'r',
    sql: 'sql',
    html: 'html',
    css: 'css',
    scss: 'scss',
    sass: 'sass',
    less: 'less',
    xml: 'xml',
    yaml: 'yaml',
    yml: 'yaml',
    json: 'json',
    md: 'markdown',
    sh: 'shell',
    bash: 'shell',
    ps1: 'powershell',
    dockerfile: 'dockerfile',
  };
  
  return languageMap[ext || ''] || 'plaintext';
}
```

## Phase 4: Complete File Synchronization (Week 2-3)

### Step 1: File State Management

#### 1.1 Create FileStateManager
```python
# src/file_sync/file_state_manager.py
import asyncio
from pathlib import Path
from typing import Dict, Set, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

@dataclass
class FileState:
    """Represents the state of a file."""
    path: Path
    content: str
    checksum: str
    last_modified: datetime
    locked_by: Optional[str] = None  # agent_id or 'user'
    dirty: bool = False

class FileStateManager:
    """Manages file state and synchronization."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.file_states: Dict[str, FileState] = {}
        self.file_locks: Dict[str, str] = {}  # file_path -> locker_id
        self.watchers: Set[Callable[[str, str], Awaitable[None]]] = set()
    
    def compute_checksum(self, content: str) -> str:
        """Compute SHA256 checksum of content."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def load_file(self, file_path: str) -> FileState:
        """Load file state from disk."""
        full_path = self.project_path / file_path
        
        if full_path.exists():
            content = full_path.read_text()
            checksum = self.compute_checksum(content)
            
            state = FileState(
                path=full_path,
                content=content,
                checksum=checksum,
                last_modified=datetime.fromtimestamp(full_path.stat().st_mtime)
            )
            
            self.file_states[file_path] = state
            return state
        else:
            raise FileNotFoundError(f"File not found: {file_path}")
    
    async def update_file(self, file_path: str, content: str, updater_id: str) -> bool:
        """Update file content with conflict detection."""
        state = self.file_states.get(file_path)
        
        if not state:
            # New file
            full_path = self.project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            
            self.file_states[file_path] = FileState(
                path=full_path,
                content=content,
                checksum=self.compute_checksum(content),
                last_modified=datetime.now()
            )
            
            await self.notify_watchers(file_path, 'created')
            return True
        
        # Check for conflicts
        if state.locked_by and state.locked_by != updater_id:
            return False  # File is locked by another entity
        
        # Update file
        state.content = content
        state.checksum = self.compute_checksum(content)
        state.last_modified = datetime.now()
        state.dirty = True
        
        # Write to disk
        state.path.write_text(content)
        
        await self.notify_watchers(file_path, 'updated')
        return True
    
    async def lock_file(self, file_path: str, locker_id: str) -> bool:
        """Lock a file for exclusive access."""
        if file_path in self.file_locks:
            return self.file_locks[file_path] == locker_id
        
        self.file_locks[file_path] = locker_id
        
        if file_path in self.file_states:
            self.file_states[file_path].locked_by = locker_id
        
        return True
    
    async def unlock_file(self, file_path: str, locker_id: str) -> bool:
        """Unlock a file."""
        if self.file_locks.get(file_path) == locker_id:
            del self.file_locks[file_path]
            
            if file_path in self.file_states:
                self.file_states[file_path].locked_by = None
            
            return True
        return False
    
    def add_watcher(self, callback: Callable[[str, str], Awaitable[None]]):
        """Add a file change watcher."""
        self.watchers.add(callback)
    
    async def notify_watchers(self, file_path: str, action: str):
        """Notify all watchers of file changes."""
        tasks = [watcher(file_path, action) for watcher in self.watchers]
        await asyncio.gather(*tasks, return_exceptions=True)
```

#### 1.2 Integrate FileStateManager with Server
```python
# In src/server.py
class HMAServer:
    def __init__(self):
        # ... existing initialization ...
        self.file_managers: Dict[str, FileStateManager] = {}  # client_id -> manager
    
    async def get_file_manager(self, client_id: str) -> Optional[FileStateManager]:
        """Get or create file manager for client."""
        session = self.clients.get(client_id)
        if not session or not session.project_path:
            return None
        
        if client_id not in self.file_managers:
            manager = FileStateManager(session.project_path)
            
            # Add watcher for frontend updates
            async def notify_frontend(file_path: str, action: str):
                await self.send_to_client(client_id, {
                    "type": "file_sync_update",
                    "payload": {
                        "filePath": file_path,
                        "action": action,
                        "timestamp": datetime.now().isoformat()
                    }
                })
            
            manager.add_watcher(notify_frontend)
            self.file_managers[client_id] = manager
        
        return self.file_managers[client_id]
```

### Step 2: Two-way Synchronization

#### 2.1 Handle Frontend File Edits
```python
async def handle_file_edit(self, client_id: str, payload: Dict[str, Any]):
    """Handle file edit from frontend."""
    try:
        file_path = payload.get("filePath")
        content = payload.get("content")
        
        if not file_path or content is None:
            await self.send_error(client_id, "Missing file path or content")
            return
        
        manager = await self.get_file_manager(client_id)
        if not manager:
            await self.send_error(client_id, "No project open")
            return
        
        # Update file
        success = await manager.update_file(file_path, content, f"user_{client_id}")
        
        if success:
            await self.send_to_client(client_id, {
                "type": "file_edit_result",
                "payload": {
                    "success": True,
                    "filePath": file_path
                }
            })
            
            # Notify agents of change
            await self.notify_agents_of_file_change(client_id, file_path)
        else:
            await self.send_to_client(client_id, {
                "type": "file_edit_result",
                "payload": {
                    "success": False,
                    "filePath": file_path,
                    "error": "File is locked by an agent"
                }
            })
    
    except Exception as e:
        logger.error(f"Error handling file edit: {e}")
        await self.send_error(client_id, str(e))

async def notify_agents_of_file_change(self, client_id: str, file_path: str):
    """Notify relevant agents about file changes."""
    # Find agents working on or near this file
    for agent_id, agent in self.agents.items():
        if agent_id.startswith(client_id):
            # Check if agent is interested in this file
            agent_path = Path(agent.path)
            file_full_path = Path(file_path)
            
            if file_full_path.is_relative_to(agent_path) or agent_path.is_relative_to(file_full_path.parent):
                # Agent might be interested
                await agent.notify_file_change(file_path)
```

#### 2.2 Frontend File Sync Hook
```typescript
// web_app/hooks/useFileSync.ts
import { useState, useEffect, useCallback } from 'react';
import { useSocketEvent } from './useSocketEvent';
import websocketService from '../services/websocket';

interface FileSyncState {
  lockedFiles: Set<string>;
  dirtyFiles: Set<string>;
  lastSync: Record<string, Date>;
}

export function useFileSync() {
  const [syncState, setSyncState] = useState<FileSyncState>({
    lockedFiles: new Set(),
    dirtyFiles: new Set(),
    lastSync: {}
  });
  
  // Handle file sync updates
  useSocketEvent('file_sync_update', (update) => {
    const { filePath, action } = update;
    
    setSyncState(prev => {
      const newState = { ...prev };
      
      if (action === 'locked') {
        newState.lockedFiles.add(filePath);
      } else if (action === 'unlocked') {
        newState.lockedFiles.delete(filePath);
      }
      
      newState.lastSync[filePath] = new Date();
      
      return newState;
    });
  });
  
  // Save file to backend
  const saveFile = useCallback(async (filePath: string, content: string) => {
    websocketService.send({
      type: 'file_edit',
      payload: { filePath, content }
    });
    
    setSyncState(prev => ({
      ...prev,
      dirtyFiles: new Set(prev.dirtyFiles).add(filePath)
    }));
  }, []);
  
  // Handle save confirmation
  useSocketEvent('file_edit_result', (result) => {
    if (result.success) {
      setSyncState(prev => {
        const newDirty = new Set(prev.dirtyFiles);
        newDirty.delete(result.filePath);
        return { ...prev, dirtyFiles: newDirty };
      });
    }
  });
  
  return {
    syncState,
    saveFile,
    isLocked: (filePath: string) => syncState.lockedFiles.has(filePath),
    isDirty: (filePath: string) => syncState.dirtyFiles.has(filePath)
  };
}
```

## Phase 5: Storage & Persistence (Week 3)

### Step 1: Complete Database Implementation

#### 1.1 Enhance Database Models
```python
# src/storage/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class ChatSession(SQLModel, table=True):
    """Chat session model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    project_id: Optional[str] = None
    status: str = Field(default="active")  # active, archived, deleted
    
    # Relationships
    messages: List["ChatMessage"] = Relationship(back_populates="session")
    imported_files: List["ImportedFile"] = Relationship(back_populates="session")

class ChatMessage(SQLModel, table=True):
    """Individual chat message."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="chatsession.id", index=True)
    type: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: Optional[str] = None
    metadata: Optional[str] = None  # JSON string
    
    # Relationships
    session: ChatSession = Relationship(back_populates="messages")

class ImportedFile(SQLModel, table=True):
    """Imported file metadata."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="chatsession.id", index=True)
    name: str
    path: str
    size: int
    content_hash: str
    imported_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    session: ChatSession = Relationship(back_populates="imported_files")

class ProjectMeta(SQLModel, table=True):
    """Project metadata."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="chatsession.id", index=True)
    project_path: str
    language: str
    framework: Optional[str] = None
    status: str = Field(default="active")  # active, completed, archived
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Statistics
    total_files: int = 0
    total_lines: int = 0
    total_tokens_used: int = 0
    
    # Agent hierarchy snapshot (JSON)
    agent_hierarchy: Optional[str] = None
```

#### 1.2 Implement Database Operations
```python
# src/storage/db.py
from sqlmodel import Session, create_engine, SQLModel, select
from typing import List, Optional
import os
from datetime import datetime, timedelta
import asyncio
import json

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hma_llm.db")
engine = create_engine(DATABASE_URL, echo=False)

# Initialize database
def init_database():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)

# Session management
def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session

# Chat session operations
async def save_chat_session(session_data: dict) -> bool:
    """Save or update chat session."""
    try:
        with Session(engine) as db:
            # Check if session exists
            existing = db.get(ChatSession, session_data["id"])
            
            if existing:
                # Update existing session
                for key, value in session_data.items():
                    if key != "id" and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.last_modified = datetime.utcnow()
            else:
                # Create new session
                chat_session = ChatSession(**session_data)
                db.add(chat_session)
            
            db.commit()
            return True
    except Exception as e:
        print(f"Error saving chat session: {e}")
        return False

async def save_chat_message(message_data: dict) -> bool:
    """Save chat message."""
    try:
        with Session(engine) as db:
            message = ChatMessage(**message_data)
            db.add(message)
            db.commit()
            return True
    except Exception as e:
        print(f"Error saving chat message: {e}")
        return False

async def load_chat_sessions(user_id: str, limit: int = 50) -> List[dict]:
    """Load chat sessions for user."""
    try:
        with Session(engine) as db:
            statement = (
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .where(ChatSession.status != "deleted")
                .order_by(ChatSession.last_modified.desc())
                .limit(limit)
            )
            
            sessions = db.exec(statement).all()
            
            result = []
            for session in sessions:
                # Count messages
                message_count = len(session.messages)
                file_count = len(session.imported_files)
                
                result.append({
                    "id": session.id,
                    "title": session.title,
                    "created_at": session.created_at,
                    "last_modified": session.last_modified,
                    "project_id": session.project_id,
                    "status": session.status,
                    "message_count": message_count,
                    "file_count": file_count
                })
            
            return result
    except Exception as e:
        print(f"Error loading chat sessions: {e}")
        return []

async def load_chat_messages(session_id: str) -> List[dict]:
    """Load messages for a chat session."""
    try:
        with Session(engine) as db:
            statement = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.timestamp.asc())
            )
            
            messages = db.exec(statement).all()
            
            return [
                {
                    "id": msg.id,
                    "type": msg.type,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "agent_id": msg.agent_id,
                    "metadata": json.loads(msg.metadata) if msg.metadata else None
                }
                for msg in messages
            ]
    except Exception as e:
        print(f"Error loading chat messages: {e}")
        return []

# Cleanup operations
async def cleanup_old_sessions(days: int = 180):
    """Delete sessions older than specified days."""
    try:
        with Session(engine) as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            statement = (
                select(ChatSession)
                .where(ChatSession.last_modified < cutoff_date)
                .where(ChatSession.status != "archived")
            )
            
            old_sessions = db.exec(statement).all()
            
            for session in old_sessions:
                session.status = "deleted"
            
            db.commit()
            
            return len(old_sessions)
    except Exception as e:
        print(f"Error cleaning up old sessions: {e}")
        return 0

# Background cleanup task
cleanup_task = None

async def start_cleanup_task(interval_hours: int = 24):
    """Start background cleanup task."""
    global cleanup_task
    
    async def cleanup_loop():
        while True:
            try:
                deleted_count = await cleanup_old_sessions()
                print(f"Cleaned up {deleted_count} old sessions")
            except Exception as e:
                print(f"Cleanup task error: {e}")
            
            await asyncio.sleep(interval_hours * 3600)
    
    cleanup_task = asyncio.create_task(cleanup_loop())

async def stop_cleanup_task():
    """Stop background cleanup task."""
    global cleanup_task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
```

### Step 2: Session Persistence Integration

#### 2.1 Update Server Handlers
```python
# In src/server.py
async def handle_save_chat_session(self, client_id: str, payload: Dict[str, Any]):
    """Save chat session to database."""
    try:
        from src.storage.db import save_chat_session, save_chat_message
        
        session_data = payload.get("session", {})
        messages = session_data.pop("messages", [])
        
        # Save session
        success = await save_chat_session(session_data)
        
        if success:
            # Save messages
            for msg in messages:
                msg["session_id"] = session_data["id"]
                await save_chat_message(msg)
            
            await self.send_to_client(client_id, {
                "type": "chat_save_result",
                "payload": {"success": True, "sessionId": session_data["id"]}
            })
        else:
            await self.send_to_client(client_id, {
                "type": "chat_save_result",
                "payload": {"success": False, "error": "Failed to save session"}
            })
    
    except Exception as e:
        logger.error(f"Error saving chat session: {e}")
        await self.send_error(client_id, str(e))

async def handle_load_chat_history(self, client_id: str, payload: Dict[str, Any]):
    """Load chat history from database."""
    try:
        from src.storage.db import load_chat_sessions
        
        user_id = payload.get("userId", f"user_{client_id}")
        limit = payload.get("limit", 50)
        
        sessions = await load_chat_sessions(user_id, limit)
        
        await self.send_to_client(client_id, {
            "type": "chat_history_response",
            "payload": {"sessions": sessions}
        })
    
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        await self.send_error(client_id, str(e))
```

## Phase 6: Git Integration (Week 3-4)

### Step 1: Complete Git Operations

#### 1.1 Implement Git Handlers
```python
# In src/server.py
async def handle_git_status(self, client_id: str, payload: Dict[str, Any]):
    """Get git status for project."""
    try:
        session = self.clients.get(client_id)
        if not session or not session.project_path:
            await self.send_error(client_id, "No project open")
            return
        
        from src.git.git_manager import GitManager
        
        git_manager = GitManager(str(session.project_path))
        status = await git_manager.get_status()
        
        await self.send_to_client(client_id, {
            "type": "git_status_response",
            "payload": status
        })
    
    except Exception as e:
        logger.error(f"Error getting git status: {e}")
        await self.send_error(client_id, str(e))

async def handle_git_commit(self, client_id: str, payload: Dict[str, Any]):
    """Create git commit."""
    try:
        session = self.clients.get(client_id)
        if not session or not session.project_path:
            await self.send_error(client_id, "No project open")
            return
        
        message = payload.get("message", "")
        files = payload.get("files", [])
        author = payload.get("author", {"name": "HMA-LLM User", "email": "user@hma-llm.ai"})
        
        from src.git.git_manager import GitManager
        
        git_manager = GitManager(str(session.project_path))
        
        # Stage files
        for file_path in files:
            await git_manager.stage_file(file_path)
        
        # Create commit
        commit_hash = await git_manager.commit(
            message=message,
            author_name=author["name"],
            author_email=author["email"]
        )
        
        await self.send_to_client(client_id, {
            "type": "git_operation_result",
            "payload": {
                "operation": "commit",
                "success": True,
                "commitHash": commit_hash
            }
        })
    
    except Exception as e:
        logger.error(f"Error creating git commit: {e}")
        await self.send_error(client_id, str(e))
```

#### 1.2 Add Git Support to Agent DSL
```lark
// In manager_language/grammar.lark
git_init: "git_init()"
git_commit: "git_commit(" STRING ")"
git_branch: "git_branch(" STRING ")"
git_merge: "git_merge(" STRING ")"
```

```python
# In manager_language/interpreter.py
async def visit_GitCommitNode(self, node: GitCommitNode) -> CommandResult:
    """Create a git commit."""
    try:
        git_manager = self.context.get("git_manager")
        if not git_manager:
            # Initialize git manager
            project_path = self.context.get("project_path")
            git_manager = GitManager(project_path)
            self.context["git_manager"] = git_manager
        
        # Stage all changes
        await git_manager.stage_all()
        
        # Commit
        commit_hash = await git_manager.commit(
            message=node.message,
            author_name="HMA-LLM Agent",
            author_email="agent@hma-llm.ai"
        )
        
        return CommandResult(
            success=True,
            message=f"Created commit: {commit_hash}",
            data={"commit_hash": commit_hash}
        )
    except Exception as e:
        return CommandResult(
            success=False,
            message=f"Git commit failed: {str(e)}",
            data={}
        )
```

### Step 2: Frontend Git UI Integration

#### 2.1 Complete GitPanel Component
```typescript
// web_app/components/GitPanel.tsx
import { useState, useEffect } from 'react';
import { GitBranch, GitCommit, GitPullRequest, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { useSocketEvent } from '../hooks/useSocketEvent';
import websocketService from '../services/websocket';

interface GitStatus {
  branch: string;
  ahead: number;
  behind: number;
  staged: string[];
  unstaged: string[];
  untracked: string[];
}

export function GitPanel() {
  const [gitStatus, setGitStatus] = useState<GitStatus | null>(null);
  const [commitMessage, setCommitMessage] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);
  
  // Fetch git status on mount
  useEffect(() => {
    refreshStatus();
  }, []);
  
  // Handle git status response
  useSocketEvent('git_status_response', (status: GitStatus) => {
    setGitStatus(status);
    setIsLoading(false);
  });
  
  // Handle git operation results
  useSocketEvent('git_operation_result', (result) => {
    if (result.success) {
      if (result.operation === 'commit') {
        setCommitMessage('');
        setSelectedFiles(new Set());
        refreshStatus();
      }
    }
    setIsLoading(false);
  });
  
  const refreshStatus = () => {
    setIsLoading(true);
    websocketService.send({
      type: 'git_status',
      payload: {}
    });
  };
  
  const handleCommit = () => {
    if (!commitMessage.trim() || selectedFiles.size === 0) return;
    
    setIsLoading(true);
    websocketService.send({
      type: 'git_commit',
      payload: {
        message: commitMessage,
        files: Array.from(selectedFiles)
      }
    });
  };
  
  const toggleFileSelection = (file: string) => {
    const newSelection = new Set(selectedFiles);
    if (newSelection.has(file)) {
      newSelection.delete(file);
    } else {
      newSelection.add(file);
    }
    setSelectedFiles(newSelection);
  };
  
  if (!gitStatus) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="h-full flex flex-col p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <GitBranch className="h-4 w-4" />
          <span className="font-medium">{gitStatus.branch}</span>
          {gitStatus.ahead > 0 && (
            <span className="text-xs text-green-500">↑{gitStatus.ahead}</span>
          )}
          {gitStatus.behind > 0 && (
            <span className="text-xs text-red-500">↓{gitStatus.behind}</span>
          )}
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={refreshStatus}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div>
      
      {/* File changes */}
      <div className="flex-1 overflow-y-auto space-y-4">
        {/* Unstaged changes */}
        {gitStatus.unstaged.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">Unstaged Changes</h4>
            <div className="space-y-1">
              {gitStatus.unstaged.map(file => (
                <label
                  key={file}
                  className="flex items-center gap-2 p-2 hover:bg-muted rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedFiles.has(file)}
                    onChange={() => toggleFileSelection(file)}
                  />
                  <span className="text-sm">{file}</span>
                </label>
              ))}
            </div>
          </div>
        )}
        
        {/* Untracked files */}
        {gitStatus.untracked.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">Untracked Files</h4>
            <div className="space-y-1">
              {gitStatus.untracked.map(file => (
                <label
                  key={file}
                  className="flex items-center gap-2 p-2 hover:bg-muted rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedFiles.has(file)}
                    onChange={() => toggleFileSelection(file)}
                  />
                  <span className="text-sm text-muted-foreground">{file}</span>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Commit section */}
      <div className="border-t pt-4 mt-4">
        <Textarea
          placeholder="Commit message..."
          value={commitMessage}
          onChange={(e) => setCommitMessage(e.target.value)}
          className="mb-2"
          rows={3}
        />
        <Button
          onClick={handleCommit}
          disabled={!commitMessage.trim() || selectedFiles.size === 0 || isLoading}
          className="w-full"
        >
          <GitCommit className="h-4 w-4 mr-2" />
          Commit {selectedFiles.size > 0 && `(${selectedFiles.size} files)`}
        </Button>
      </div>
    </div>
  );
}
```

## Phase 7: Project Export/Import (Week 4)

### Step 1: Export Functionality

#### 1.1 Enhance Download Handler
```python
# Already implemented in server.py - enhance with progress tracking
async def handle_download_project(self, client_id: str, payload: Dict[str, Any]):
    """Enhanced project download with metadata."""
    try:
        session = self.clients.get(client_id)
        if not session or not session.project_path:
            await self.send_error(client_id, "No project open")
            return
        
        # Create project metadata
        metadata = {
            "project_name": session.project_path.name,
            "export_date": datetime.now().isoformat(),
            "llm_model": session.llm_model,
            "total_agents": len([a for a in self.agents.keys() if a.startswith(client_id)]),
            "session_id": session.client_id
        }
        
        # Save metadata to project
        metadata_path = session.project_path / ".hma-llm-meta.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))
        
        # Continue with existing download logic...
        # ... (existing implementation)
        
    except Exception as e:
        logger.error(f"Error downloading project: {e}")
        await self.send_error(client_id, str(e))
```

### Step 2: Import Enhancement

#### 2.1 Improve Import Handler
```python
async def handle_import_project(self, client_id: str, payload: Dict[str, Any]):
    """Enhanced project import with validation."""
    try:
        files = payload.get("files", [])
        project_name = payload.get("projectName", f"imported_{int(time.time())}")
        
        # Validate import
        if not files:
            await self.send_error(client_id, "No files to import")
            return
        
        # Check for malicious patterns
        suspicious_patterns = [
            "eval(", "exec(", "__import__", "subprocess",
            "os.system", "open(", "file("
        ]
        
        for file_data in files:
            content = file_data.get("content", "")
            if any(pattern in content for pattern in suspicious_patterns):
                await self.send_to_client(client_id, {
                    "type": "import_warning",
                    "payload": {
                        "file": file_data["path"],
                        "warning": "File contains potentially dangerous code patterns"
                    }
                })
        
        # Create project structure
        project_path = Path("generated_projects") / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Import files
        imported_count = 0
        for file_data in files:
            file_path = project_path / file_data["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_data["content"])
            imported_count += 1
            
            # Send progress
            await self.send_to_client(client_id, {
                "type": "import_progress",
                "payload": {
                    "current": imported_count,
                    "total": len(files),
                    "file": file_data["path"]
                }
            })
        
        # Check for .hma-llm-meta.json
        meta_path = project_path / ".hma-llm-meta.json"
        if meta_path.exists():
            metadata = json.loads(meta_path.read_text())
            await self.send_to_client(client_id, {
                "type": "import_metadata",
                "payload": metadata
            })
        
        # Initialize git if needed
        if not (project_path / ".git").exists():
            git_manager = GitManager(str(project_path))
            await git_manager.init()
            await git_manager.stage_all()
            await git_manager.commit("Initial import", "HMA-LLM", "import@hma-llm.ai")
        
        # Update session
        session = self.clients.get(client_id)
        if session:
            session.project_path = project_path
        
        await self.send_to_client(client_id, {
            "type": "import_complete",
            "payload": {
                "projectPath": str(project_path),
                "fileCount": imported_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error importing project: {e}")
        await self.send_error(client_id, str(e))
```

## Phase 8: Testing & Polish (Week 4)

### Step 1: Integration Tests

#### 1.1 End-to-End Test Suite
```python
# test/test_full_integration.py
import pytest
import asyncio
from src.server import HMAServer
from src.storage.db import init_database

@pytest.mark.asyncio
async def test_full_project_flow():
    """Test complete project creation flow."""
    # Initialize
    init_database()
    server = HMAServer()
    
    # Simulate client connection
    client_id = "test_client_123"
    server.clients[client_id] = ClientSession(
        sid="test_sid",
        client_id=client_id
    )
    
    # Start project
    await server.handle_start_project_init(client_id, {
        "projectName": "test_project"
    })
    
    # Verify master agent created
    assert f"{client_id}_master" in server.agents
    
    # Simulate understanding phase
    await server.handle_prompt(client_id, {
        "prompt": "I want to build a todo app with React and TypeScript"
    })
    
    # Approve structure phase
    await server.handle_approve_phase(client_id, {
        "phase": "structure"
    })
    
    # Verify project structure created
    session = server.clients[client_id]
    assert session.project_path.exists()
    
    # Test file operations
    await server.handle_file_edit(client_id, {
        "filePath": "src/App.tsx",
        "content": "export default function App() { return <div>Hello</div>; }"
    })
    
    # Test git operations
    await server.handle_git_status(client_id, {})
    await server.handle_git_commit(client_id, {
        "message": "Initial commit",
        "files": ["src/App.tsx"]
    })
    
    # Cleanup
    await server.cleanup()
```

#### 1.2 WebSocket Communication Test
```python
# test/test_websocket_flow.py
import socketio
import asyncio
import json

async def test_websocket_communication():
    """Test WebSocket message flow."""
    sio = socketio.AsyncClient()
    messages_received = []
    
    @sio.event
    async def message(data):
        messages_received.append(data)
    
    # Connect
    await sio.connect('http://localhost:8080', socketio_path='/ws')
    
    # Test LLM configuration
    await sio.send(json.dumps({
        "type": "llm_config",
        "payload": {
            "model": "gpt-4.1-turbo",
            "temperature": 0.8
        }
    }))
    
    await asyncio.sleep(1)
    
    # Verify response
    config_responses = [
        msg for msg in messages_received 
        if msg.get("type") == "llm_config_update"
    ]
    assert len(config_responses) > 0
    
    await sio.disconnect()
```

### Step 2: Performance Optimization

#### 2.1 Connection Pooling
```python
# src/server.py
class ConnectionPool:
    """Manage WebSocket connections efficiently."""
    
    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self.active_connections = 0
        self.waiting_queue = asyncio.Queue()
    
    async def acquire(self):
        """Acquire a connection slot."""
        if self.active_connections >= self.max_connections:
            await self.waiting_queue.get()
        self.active_connections += 1
    
    def release(self):
        """Release a connection slot."""
        self.active_connections -= 1
        if not self.waiting_queue.empty():
            self.waiting_queue.put_nowait(None)
```

#### 2.2 Frontend Optimization
```typescript
// web_app/src/App.tsx
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const CodeEditor = lazy(() => import('./components/CodeEditor'));
const Terminal = lazy(() => import('./components/Terminal'));
const GitPanel = lazy(() => import('./components/GitPanel'));

// Use React.memo for expensive components
const FileTree = React.memo(FileTreeComponent);
const ChatPanel = React.memo(ChatPanelComponent);
```

## Phase 9: Error Handling & Recovery

### Step 1: Comprehensive Error Handling

#### 1.1 Global Error Handler
```python
# src/server.py
async def global_error_handler(self, client_id: str, error: Exception):
    """Handle all unhandled errors gracefully."""
    error_type = type(error).__name__
    error_message = str(error)
    
    # Log error with context
    logger.error(f"Unhandled error for client {client_id}: {error_type} - {error_message}", 
                 exc_info=True)
    
    # Determine error severity
    if isinstance(error, (FileNotFoundError, ValueError)):
        severity = "warning"
    elif isinstance(error, (ConnectionError, TimeoutError)):
        severity = "error"
        # Attempt recovery
        await self.attempt_recovery(client_id)
    else:
        severity = "critical"
    
    # Notify client
    await self.send_to_client(client_id, {
        "type": "error",
        "payload": {
            "severity": severity,
            "message": error_message,
            "recovery_available": severity != "critical"
        }
    })
```

#### 1.2 Frontend Error Boundary
```typescript
// web_app/components/ErrorBoundary.tsx
import { Component, ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';
import { Button } from './ui/button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    
    // Send error to backend for logging
    websocketService.send({
      type: 'client_error',
      payload: {
        error: error.toString(),
        stack: error.stack,
        componentStack: errorInfo.componentStack
      }
    });
  }
  
  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex flex-col items-center justify-center h-full p-8">
          <AlertCircle className="h-12 w-12 text-destructive mb-4" />
          <h2 className="text-lg font-semibold mb-2">Something went wrong</h2>
          <p className="text-muted-foreground mb-4">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <Button onClick={() => window.location.reload()}>
            Reload Application
          </Button>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

## Phase 10: Deployment & Documentation

### Step 1: Docker Configuration

#### 1.1 Multi-stage Dockerfile
```dockerfile
# Dockerfile
# Frontend build stage
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY web_app/package*.json ./
RUN npm ci
COPY web_app/ ./
RUN npm run build

# Backend stage
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY prompts/ ./prompts/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./static

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./data/hma_llm.db

# Create data directory
RUN mkdir -p data generated_projects

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Start server
CMD ["python", "-m", "src.server"]
```

#### 1.2 Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=sqlite:///./data/hma_llm.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_GEMINI_API_KEY=${GOOGLE_GEMINI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - XAI_API_KEY=${XAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./generated_projects:/app/generated_projects
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
    
  # Optional: Redis for session management
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Optional: PostgreSQL for production
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=hma_llm
      - POSTGRES_USER=hma_llm
      - POSTGRES_PASSWORD=${DB_PASSWORD:-secure_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### Step 2: Production Deployment Guide

#### 2.1 Deployment Documentation
```markdown
# HMA-LLM Production Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Domain name with SSL certificate
- At least one LLM API key

## Deployment Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-org/hma-llm.git
   cd hma-llm
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Build and Start Services**
   ```bash
   docker-compose up -d --build
   ```

4. **Initialize Database**
   ```bash
   docker-compose exec app python -c "from src.storage.db import init_database; init_database()"
   ```

5. **Configure Reverse Proxy (nginx)**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /ws {
           proxy_pass http://localhost:8080/ws;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_read_timeout 86400;
       }
   }
   ```

## Monitoring

1. **Health Check Endpoint**
   ```bash
   curl https://your-domain.com/health
   ```

2. **Logs**
   ```bash
   docker-compose logs -f app
   ```

3. **Metrics** (if configured)
   - Prometheus endpoint: `/metrics`
   - Grafana dashboards available

## Backup & Recovery

1. **Database Backup**
   ```bash
   docker-compose exec postgres pg_dump -U hma_llm hma_llm > backup.sql
   ```

2. **Project Files Backup**
   ```bash
   tar -czf projects_backup.tar.gz generated_projects/
   ```

## Scaling Considerations

- Use Redis for session management in multi-instance deployments
- Configure load balancer with sticky sessions for WebSocket
- Use shared storage (NFS/S3) for generated_projects directory
- Consider Kubernetes deployment for auto-scaling
```

## Integration Checklist

Use this checklist to verify implementation completeness:

### Phase 1: Master Agent Integration
- [ ] Wrapper approach implemented in `src/master_agent_wrapper.py`
- [ ] Server.py updated with Master Agent message routing
- [ ] Phase management methods added (`send_phase_update`, `handle_approve_phase`)
- [ ] PhaseIndicator component created and integrated
- [ ] Three-phase workflow (Understanding → Structure → Delegation) functional

### Critical Gap: File Operation Integration
- [ ] `parse_agent_responses_and_broadcast` method implemented
- [ ] Agent response parsing for CHANGE/CREATE operations
- [ ] `file_tree_update` events broadcasting to frontend
- [ ] FileTree component receiving and displaying real-time updates

### Phase 2: Terminal Integration
- [ ] TerminalManager class created
- [ ] Agent DSL updated with terminal commands
- [ ] Container management integrated
- [ ] Frontend Terminal component supports multiple sessions

### Phase 3: Real-time Code Streaming
- [ ] StreamManager implemented
- [ ] Code streaming events (`code_stream`) working
- [ ] CodeEditor shows streaming indicator
- [ ] Progressive content display functional

### Phase 4: File Synchronization
- [ ] FileStateManager for conflict detection
- [ ] Two-way sync (frontend edits → backend)
- [ ] File locking mechanism
- [ ] `useFileSync` hook implemented

### Phase 5: Storage & Persistence
- [ ] Database models defined and created
- [ ] Chat session persistence working
- [ ] Background cleanup tasks running
- [ ] Load/save chat history functional

### Phase 6: Git Integration
- [ ] Git handlers in server.py
- [ ] Agent DSL git commands
- [ ] GitPanel component functional
- [ ] Status, commit, branch operations working

### Phase 7: Project Export/Import
- [ ] Enhanced download with metadata
- [ ] Security validation on import
- [ ] Progress tracking for large imports
- [ ] Git initialization on import

### Phase 8-10: Testing, Error Handling, Deployment
- [ ] End-to-end test suite
- [ ] Error boundaries and recovery
- [ ] Docker configuration
- [ ] Production deployment guide

## Verification Commands

After each phase, run these commands to verify functionality:

```bash
# Backend tests
python -m pytest test/ -v

# Frontend tests  
cd web_app && npm test

# Integration test
python test_llm_integration.py

# Build verification
cd web_app && npm run build
```

## Troubleshooting Common Issues

### WebSocket Connection Issues
- Verify CORS settings in server.py
- Check firewall/proxy configuration
- Ensure Socket.IO paths match frontend/backend

### Agent Communication Problems
- Check agent creation in server.py logs
- Verify DSL parser imports
- Confirm agent hierarchy structure

### File Operation Failures
- Check file permissions on generated_projects/
- Verify Path handling (absolute vs relative)
- Confirm frontend FileTree update handling

### LLM Integration Issues
- Verify API keys are set correctly
- Check model name mapping between frontend/backend
- Confirm WebSocket event names match

## Conclusion

This comprehensive plan provides a detailed roadmap for completing the HMA-LLM frontend-backend integration. The phased approach ensures systematic implementation while maintaining system stability. 

**Critical Success Factors:**
1. **File Operation Integration** - Must be implemented first for visible progress
2. **Master Agent Integration** - Enables the core AI workflow
3. **Real-time Updates** - Essential for user experience
4. **Error Handling** - Prevents system failures

The plan includes code examples, testing strategies, and deployment configurations to ensure a production-ready system. Use the checklist and verification commands to track progress and identify issues early.