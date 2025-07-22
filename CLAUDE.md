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
cd frontend

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
```

## Architecture & Key Patterns

### Agent Hierarchy
- **Master Agent**: Root coordinator that plans project structure and delegates to managers
- **Manager Agents**: Control directories, coordinate multiple coders, use manager_language DSL
- **Coder Agents**: Write individual files, use coder_language DSL for operations

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
├── llm/                  # LLM provider integrations
├── languages/            # Agent DSLs
│   ├── manager_language/ # Manager agent commands
│   └── coder_language/   # Coder agent commands
└── storage/              # Database models (SQLModel)
```

### Frontend Structure
```
frontend/
├── src/App.tsx           # Main application entry
├── components/
│   ├── chat/            # Chat interface components
│   ├── editor/          # Monaco editor & terminal
│   └── ui/              # Reusable UI components
└── services/
    ├── websocket.ts     # Socket.IO client
    └── chatStorage.ts   # Local storage persistence
```

## Testing Strategy

### Backend Testing
- Unit tests for individual components
- Integration tests for agent communication (`test/test_server_integration.py`)
- Full system tests (`test/test_full_integration.py`)
- Use pytest markers: `slow`, `integration`, `asyncio`

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

# Server Config
HOST=localhost
PORT=8080
```

### Frontend (optional .env.development)
```env
VITE_SOCKET_URL=ws://localhost:8080
```

## Common Development Tasks

### Adding a New Agent Type
1. Create agent class in `src/agents/`
2. Define DSL commands in `src/languages/`
3. Update prompt templates in `prompts/`
4. Add Socket.IO event handlers in `src/server.py`

### Modifying Frontend-Backend Communication
1. Add new event type in backend `src/server.py`
2. Update frontend WebSocket service `frontend/src/services/websocket.ts`
3. Handle event in React components
4. Test with `python test_socketio_connection.py`

### Database Schema Changes
1. Modify SQLModel models in `src/storage/`
2. Database uses SQLite (file-based, zero-config)
3. Models auto-create tables on first run

## Future Integration Points

- **Terminal Integration**: Backend container support exists but not connected to frontend xterm.js
- **Git Operations**: Frontend UI ready, backend implementation needed
- **Project Export**: Download/zip functionality planned
- **Authentication**: User/session management infrastructure in place