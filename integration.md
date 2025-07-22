# HMA-LLM Frontend-Backend Integration Game Plan

## Overview
This document outlines the comprehensive integration plan for connecting the React frontend with the Python Socket.IO backend in the HMA-LLM Software Construction system.

## Current State Analysis

### Backend Architecture (Implemented)
- **Hierarchical Agent System**: Master Agent → Manager Agents → Coder Agents
- **Socket.IO Server**: Real-time communication on port 8080 (`src/server.py`)
- **Agent Orchestration**: Task delegation, code streaming, file management
- **Container Manager**: Docker workspace isolation (partially implemented)
- **Project Structure**: File-based project storage in `generated_projects/`
- **LLM Integration**: Multiple provider support (OpenAI, Anthropic, Google, DeepSeek)

### Frontend Architecture (Implemented)
- **React + TypeScript**: Modern UI with Vite build system
- **Socket.IO Client**: Real-time websocket communication
- **Chat Interface**: AI conversation panel with agent status tracking
- **Monaco Editor**: Code editing with syntax highlighting
- **File Tree**: Project structure visualization
- **Terminal Component**: xterm.js integration (UI only)
- **Git Panel**: Version control interface (UI only)
- **Local Storage**: Browser-based chat history persistence

### Integration Gaps
1. **Storage**: Chat persistence in localStorage vs backend database
2. **Terminal**: UI exists but no backend container integration
3. **Git Operations**: Frontend UI exists but backend implementation incomplete
4. **Project Lifecycle**: No download/export functionality
5. **Environment Configuration**: Hardcoded URLs and settings

---

## 1. Runtime Topology & Deployment Strategy

### Development Environment
- **Backend**: Python aiohttp + Socket.IO server on `localhost:8080`
- **Frontend**: Vite dev server on `localhost:5173`
- **Cross-origin communication**: Frontend connects to backend websocket

### Production Environment
- **Single Domain Deployment**: Reverse proxy both services
- **Static Assets**: nginx serves React build
- **WebSocket**: Same domain for `wss://<host>/ws` connection
- **Security**: HTTPS/WSS for production deployment

### Containerization Strategy
```yaml
# docker-compose.yml structure
services:
  backend:
    - Python + gunicorn/uvicorn
    - Socket.IO server
    - Database and file storage
  frontend:
    - nginx serving React build
    - Proxy /ws to backend
  docker:
    - Optional: docker-in-docker for workspace containers
```

---

## 2. Persistent Storage Architecture

### A. Chat & Session History
**Technology Choice**: SQLite with SQLModel (zero-config, file-based)

**Database Schema**:
```sql
-- Chat sessions
chat_session:
  - id (UUID, primary key)
  - user_id (UUID, for future auth)
  - title (string)
  - created_at (timestamp)
  - last_modified (timestamp)
  - project_id (UUID, optional)

-- Individual messages
chat_message:
  - id (UUID, primary key)
  - session_id (UUID, foreign key)
  - type (enum: user, assistant, system)
  - content (text)
  - timestamp (timestamp)
  - agent_id (string, optional)
  - metadata (JSON, optional)

-- Project files metadata
imported_file:
  - id (UUID, primary key)
  - session_id (UUID, foreign key)
  - name (string)
  - path (string)
  - size (integer)
  - content_hash (string)

-- Project metadata
project_meta:
  - id (UUID, primary key)
  - session_id (UUID, foreign key)
  - project_path (string)
  - language (string)
  - status (enum: active, completed, archived)
  - created_at (timestamp)
```

### B. Project Workspace Storage
**Current Approach**: File-based storage in `generated_projects/<project_id>/`
**Enhancement Plan**:
- Keep current disk-based model (fast for agents & Git operations)
- Add automatic project archiving for idle projects (after 30 days)
- Add project compression for long-term storage (after 90 days)
- Implement project cleanup policies (delete after 180 days)

### C. Git Operations
**Technology**: GitPython (already partially implemented)
**Storage**: Native `.git` directories within project workspaces
**No additional database state needed**

---

## 3. Backend Implementation Plan

### Phase 1: Database Integration
**Files to Create**:
```
src/storage/
├── __init__.py
├── models.py          # SQLModel definitions
├── db.py             # Database connection helpers
└── migrations.py     # Schema initialization
```

**Key Functions**:
- `init_database()` - Create tables on startup
- `save_chat_session(session)` - Persist chat data
- `load_chat_sessions(user_id)` - Retrieve user sessions
- `delete_chat_session(session_id)` - Remove session
- `archive_old_projects()` - Background cleanup task

### Phase 2: Enhanced Socket.IO Handlers
**New Message Types to Implement**:
```python
# In src/server.py HMAServer.handle_message()
"load_chat_history" → handle_load_chat_history()
"delete_chat_session" → handle_delete_chat_session()
"save_chat_session" → handle_save_chat_session()
"download_project" → handle_download_project()
```

### Phase 3: Terminal Container Integration
**Current State**: `ContainerManager` exists but not wired to server
**Implementation**:
```python
# In HMAServer.__init__()
self.container_manager = ContainerManager()

# Wire existing websocket events:
"create_terminal_session" → container_manager.create_workspace_container()
"send_terminal_data" → container_manager.exec_command()
"resize_terminal" → container_manager.resize_pty()
"close_terminal" → container_manager.stop_container()
```

**Security Features** (already implemented):
- Non-root user execution
- Memory/CPU limits (512MB, 0.5 CPU)
- No network access by default
- Capability dropping for security hardening

### Phase 4: Git Operations Backend
**Implement websocket handlers for**:
```python
git_status() → GitPython status, staged/unstaged files
git_diff(file_path, staged) → GitPython diff output
git_stage_file(file_path) → GitPython add
git_unstage_file(file_path) → GitPython reset
git_commit(message, author) → GitPython commit
git_push/pull(remote, branch) → GitPython remote operations
git_checkout_branch(branch) → GitPython checkout
git_list_branches() → GitPython branch list
```

**Credential Handling**:
- HTTPS: Accept username/password via websocket (session-scoped)
- SSH: Support key files mounted into container (future enhancement)

### Phase 5: HTTP Endpoints for Downloads
**Add to aiohttp app**:
```python
# In src/server.py
app.router.add_get('/download/{project_id}', handle_project_download)

async def handle_project_download(request):
    # Create zip of project directory
    # Return as application/zip with appropriate headers
```

---

## 4. Frontend Integration Updates

### Phase 1: Environment Configuration
**Create environment files**:
```bash
# .env.development
VITE_BACKEND_URL=http://localhost:8080
VITE_WS_URL=ws://localhost:8080

# .env.production
VITE_BACKEND_URL=
VITE_WS_URL=wss://yourdomain.com
```

**Update websocket connection**:
```typescript
// frontend/src/services/websocket.ts
const backendUrl = import.meta.env.VITE_BACKEND_URL || window.location.origin;
```

### Phase 2: Chat Storage Migration
**Replace LocalStorage with Backend Calls**:
```typescript
// frontend/src/services/chatStorage.ts
class WebChatStorage implements StorageProvider {
  async saveChatSession(session: ChatSession): Promise<void> {
    websocketService.send({
      type: 'save_chat_session',
      payload: { session }
    });
  }
  
  async loadChatSessions(): Promise<ChatSession[]> {
    return new Promise((resolve) => {
      websocketService.send({ type: 'load_chat_history' });
      websocketService.once('chat_history_response', resolve);
    });
  }
}
```

**Fallback Strategy**: Keep LocalStorage as backup when backend is offline

### Phase 3: Terminal Integration
**Wire existing terminal UI to backend**:
```typescript
// frontend/components/editor/Terminal.tsx
// Already implemented - just ensure websocket events are properly connected:
// - terminal_session
// - terminal_data  
// - terminal_resize
```

### Phase 4: Git Operations Integration
**Complete git panel functionality**:
```typescript
// frontend/components/git/GitPanel.tsx
// Already has UI - wire to backend websocket events:
// - git_status_response
// - git_diff_response
// - git_operation_result
```

### Phase 5: Project Download Feature
**Add download button**:
```tsx
// In frontend/components/Header.tsx
const handleDownloadProject = () => {
  const url = `${backendUrl}/download/${projectId}`;
  window.open(url, '_blank');
};
```

---

## 5. Development Workflow & Tooling

### Environment Setup
**Backend**:
```bash
# .env in project root
DATABASE_URL=sqlite:///./hma_llm.db
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_GEMINI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
```

**Frontend**:
```bash
# .env.development in frontend/
VITE_BACKEND_URL=http://localhost:8080
VITE_WS_URL=ws://localhost:8080
```

### Development Scripts
**Enhanced start_dev.py**:
```python
# scripts/start_dev.py
# Add database initialization
# Add container manager startup
# Add cleanup task scheduling
```

### Testing Strategy
**Integration Tests**:
- End-to-end: Import project → Agent generation → Git commit → Terminal usage → Download
- Websocket message flow validation
- Database persistence verification
- Container lifecycle testing

---

## 6. Implementation Timeline

### Week 1: Foundation
- [ ] Create `src/storage/` package with SQLModel schema
- [ ] Implement database initialization and basic CRUD operations
- [ ] Add environment configuration to both frontend and backend
- [ ] Update websocket connection to use environment variables

### Week 2: Core Integration
- [ ] Migrate chat persistence from LocalStorage to backend database
- [ ] Wire ContainerManager into HMAServer socket handlers
- [ ] Implement basic Git operations (status, diff, stage, commit)
- [ ] Add project download HTTP endpoint

### Week 3: Advanced Features
- [ ] Complete Git operations (push, pull, branch management)
- [ ] Add project archiving and cleanup policies
- [ ] Implement proper error handling and recovery
- [ ] Add comprehensive logging and monitoring

### Week 4: Polish & Testing
- [ ] End-to-end integration testing
- [ ] Performance optimization and memory leak detection
- [ ] Documentation updates and deployment guides
- [ ] Security review and hardening

---

## 7. Risk Mitigation

### Data Loss Prevention
- **Automatic backups**: Regular SQLite database backups
- **Project snapshots**: Git-based project versioning
- **Graceful degradation**: LocalStorage fallback for chat history

### Performance Considerations
- **Connection pooling**: Limit concurrent Socket.IO connections
- **Resource limits**: Container memory/CPU quotas already implemented
- **Database optimization**: Indexed queries and pagination for chat history

### Security Measures
- **Container isolation**: Already implemented with capability dropping
- **Input validation**: Sanitize all user inputs and file paths
- **Resource quotas**: Prevent abuse with rate limiting and timeouts

### Operational Concerns
- **Health monitoring**: Add endpoint for system health checks
- **Graceful shutdown**: Proper cleanup of containers and database connections
- **Error recovery**: Automatic restart of failed agent tasks

---

## 8. Future Enhancements

### Authentication & Multi-tenancy
- User account system with JWT tokens
- Project sharing and collaboration features
- Role-based access control for advanced features

### Advanced Git Features
- SSH key management for private repositories
- Automatic branch protection and PR workflows
- Integration with GitHub/GitLab APIs

### Enhanced AI Capabilities
- Custom agent personalities and specializations
- Multi-language project support (beyond TypeScript)
- Intelligent code review and suggestions

### Deployment & Scaling
- Kubernetes deployment configurations
- Load balancing for multiple backend instances
- Distributed storage for large projects

---

## Conclusion

This integration plan provides a comprehensive roadmap for connecting the HMA-LLM frontend and backend into a fully functional, production-ready system. The phased approach ensures minimal disruption to existing functionality while systematically adding new capabilities.

The key success factors are:
1. **Incremental delivery** - Each phase adds value independently
2. **Backward compatibility** - Fallback mechanisms prevent data loss
3. **Security first** - Container isolation and input validation throughout
4. **Performance awareness** - Resource limits and optimization from the start

Upon completion, users will have a seamless experience: natural language project requests → AI agent collaboration → live code generation → integrated development environment → project download/deployment. 