# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HMA-LLM is a hierarchical multi-agent system for automated software construction. It uses a Master Agent → Manager Agents → Coder Agents architecture where agents communicate via Socket.IO to generate complete software projects from natural language descriptions.

## Development Commands

### Backend (Python)
```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
python scripts/start_dev.py

# Run all tests
python -m pytest test/

# Run tests excluding slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration
```

### Frontend (React/TypeScript)
```bash
cd web_app

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Preview production build
npm run preview

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## Architecture & Key Patterns

### Agent Hierarchy
- **Master Agent**: Root coordinator that plans project structure and delegates to managers
- **Manager Agents**: Control directories, coordinate multiple coders, use manager_language DSL
- **Coder Agents**: Write individual files, use coder_language DSL for operations
- **Tester Agents**: Ephemeral agents for testing operations, spawned by coders/managers, use tester_language DSL

### Socket.IO Communication Flow
1. Frontend sends `prompt` event to backend
2. Master agent receives task and creates plan
3. Agents communicate through `message`, `code_stream`, `agent_update` events
4. Real-time updates flow back to frontend UI

### Key Design Decisions
- **Context Window Optimization**: Agents maintain minimal context (max 8000 tokens)
- **Domain-Specific Languages**: Custom DSLs in `src/languages/` for agent operations
- **Test-First Development**: Wave-based approach (specification → tests → implementation)
- **File-Based Storage**: Projects stored in `generated_projects/` directory

### Backend Structure
```
src/
├── server.py              # Socket.IO server entry point
├── agents/               # Agent implementations
│   ├── master_agent.py   # Root coordinator
│   ├── manager_agent.py  # Directory managers
│   ├── coder_agent.py    # File writers
│   ├── tester_agent.py   # Testing operations
│   └── ephemeral_agent.py # Base for temporary agents
├── llm/                  # Multi-provider LLM integrations
├── languages/            # Agent DSLs
│   ├── master_language/  # Master agent commands
│   ├── manager_language/ # Manager agent commands
│   ├── coder_language/   # Coder agent commands
│   └── tester_language/  # Tester agent commands
├── git/                  # Git operations
├── terminal/             # Docker container management
├── orchestrator/         # Agent prompting system
└── storage/              # Database models (SQLModel)
```

### Frontend Structure
```
web_app/
├── main.tsx              # Application entry point
├── App.tsx               # Main application component
├── components/
│   ├── ResizableLayout.tsx      # Main layout with panels
│   ├── TabbedChatPanel.tsx      # Multi-threaded chat
│   ├── WaveProgress.tsx         # Visual progress indicator
│   ├── ModelSelector.tsx        # LLM model selection
│   ├── Terminal.tsx             # Integrated xterm.js terminal
│   ├── AgentBar.tsx             # Real-time agent status
│   ├── FileTree.tsx             # Project file explorer
│   ├── CodeEditor.tsx           # Monaco editor integration
│   ├── ImportDialog.tsx         # File/project import
│   ├── ChatHistorySidebar.tsx   # Chat session management
│   └── ui/                      # shadcn/ui component library
├── contexts/
│   └── LLMContext.tsx           # LLM state management
├── services/
│   ├── websocket.ts             # Socket.IO client with queuing
│   ├── llm.ts                   # LLM provider types
│   ├── chatStorage.ts           # Local storage persistence
│   └── fileImport.ts            # File import handling
├── hooks/
│   └── useSocketEvent.ts        # WebSocket event hooks
└── styles/
    └── globals.css              # Tailwind CSS with custom styles
```

## Testing Strategy

### Backend Testing
- Unit tests for individual components
- Integration tests for agent communication (`test/test_server_integration.py`)
- Full system tests (`test/test_full_integration.py`)
- Language DSL tests for all agent types (`test/coder_language/`, `test/manager_language/`, etc.)
- Use pytest markers: `slow`, `integration`, `asyncio`

### Frontend Testing
- **Framework**: Jest with React Testing Library
- **Location**: `test_web_app/` directory
- **Coverage**: 70% threshold requirement
- **Components**: Comprehensive mocks for WebSocket, xterm, Monaco editor
- **Commands**:
  ```bash
  cd web_app
  npm test              # Run tests
  npm run test:watch    # Watch mode
  npm run test:coverage # Generate coverage report
  ```

### Manual Testing
```bash
# Test Socket.IO connection
python test_socketio_connection.py

# Run demo script
python scripts/demo.py
```

## Environment Configuration

### Backend (.env)
```env
# LLM API Keys (need at least one)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_GEMINI_API_KEY=
DEEPSEEK_API_KEY=
XAI_API_KEY=

# Server Config
HOST=localhost
PORT=8080

# Docker Configuration
DOCKER_ENABLED=true
CONTAINER_TIMEOUT=300
MAX_CONTAINERS=5

# Database Config
DB_CLEANUP_INTERVAL=3600
MAX_SESSION_AGE=86400

# WebSocket CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (optional .env.development)
```env
VITE_SOCKET_URL=ws://localhost:8080
# Uses default WebSocket URL if not specified
```

## Common Development Tasks

### Adding a New Agent Type
1. Create agent class in `src/agents/` (inherit from `base_agent.py`)
2. Define DSL grammar in `src/languages/[agent_name]_language/grammar.lark`
3. Implement AST nodes in `src/languages/[agent_name]_language/ast.py`
4. Create parser in `src/languages/[agent_name]_language/parser.py`
5. Implement interpreter in `src/languages/[agent_name]_language/interpreter.py`
6. Update prompt templates in `prompts/[agent_name]/`
7. Add orchestrator prompter in `src/orchestrator/[agent_name]_prompter.py`
8. Add Socket.IO event handlers in `src/server.py`
9. Create tests in `test/[agent_name]_language/`

### Modifying Frontend-Backend Communication
1. Add new event type in backend `src/server.py`
2. Update frontend WebSocket service `web_app/src/services/websocket.ts`
3. Define TypeScript types for new messages
4. Handle event in React components using `useSocketEvent` hook
5. Update LLMContext if needed for state management
6. Test with `python test_socketio_connection.py`
7. Add frontend tests in `test_web_app/__tests__/services/`

### Database Schema Changes
1. Modify SQLModel models in `src/storage/`
2. Database uses SQLite (file-based, zero-config)
3. Models auto-create tables on first run

## Key Features

### Implemented Features
- **Multi-LLM Support**: Runtime switching between OpenAI, Anthropic, Google, DeepSeek, and XAI
- **Real-time Agent Hierarchy**: Live visualization of agent parent/child relationships
- **Token Usage Tracking**: Per-agent token consumption monitoring with cost estimates
- **Wave Progress System**: Visual phase progression (specification → testing → implementation)
- **Terminal Integration**: Docker-based secure workspaces with xterm.js frontend
- **Git Operations**: Full repository management with commit, branch, and merge support
- **File Import System**: Drag-and-drop project import with file tree visualization
- **Resizable UI Layout**: Flexible panel system for optimal workspace organization
- **Chat Session Persistence**: Local storage with session history and restoration
- **Monaco Code Editor**: Full-featured code editing with syntax highlighting
- **Project Export**: Download entire projects as JSON with file structure
- **File Save/Load**: Individual file save functionality with local storage backup

### Future Integration Points
- **Authentication**: User/session management infrastructure in place
- **Cloud Storage**: Backend ready for cloud-based project persistence
- **Real-time Collaboration**: Multi-user workspace support architecture exists
- **Plugin System**: Extensible agent architecture for custom integrations