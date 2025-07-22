# HMA-LLM Software Construction

A hierarchical multi-agent system for automated software construction using Large Language Models (LLMs).

## 🎯 Overview

HMA-LLM is a sophisticated system that uses multiple AI agents working in a hierarchical structure to automatically generate software projects. The system consists of:

- **Manager Agents**: High-level agents that plan and coordinate project structure
- **Coder Agents**: Specialized agents that write and modify code files
- **Real-time Frontend**: Modern React interface for interacting with the system
- **Socket.IO Backend**: Real-time communication between frontend and agents

## ✨ Features

### 🤖 Hierarchical Agent System
- **Manager Agents**: Plan project structure, delegate tasks, manage directories
- **Coder Agents**: Write code, implement features, handle file operations
- **Intelligent Delegation**: Agents automatically delegate tasks to appropriate children
- **Context Awareness**: Each agent maintains context about their scope and responsibilities

### 💻 Modern Frontend
- **Real-time Chat Interface**: Communicate with agents through natural language
- **Live File Tree**: Watch project structure evolve in real-time
- **Code Viewer**: Syntax-highlighted code display with live updates
- **Agent Status Tracking**: See which agents are active and what they're working on
- **Responsive Design**: Works on desktop and mobile devices

### 🔧 Backend Infrastructure
- **Socket.IO Server**: Real-time bidirectional communication
- **Multi-LLM Support**: OpenAI, Anthropic, Google AI, DeepSeek integration
- **Project Management**: Automatic project creation and file management
- **Error Handling**: Robust error handling and recovery

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **npm or yarn**
- **LLM API Key** (OpenAI, Anthropic, Google AI, or DeepSeek)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd HMA-LLM-Software
   ```

2. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure backend environment:**
   ```bash
   # Copy the example environment file
   cp config/env.example .env
   
   # Edit .env and add your API keys
   # You need at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_GEMINI_API_KEY, or DEEPSEEK_API_KEY
   ```

5. **Configure frontend environment (optional):**
   ```bash
   # Copy the example frontend environment file
   cp frontend/config/env.example frontend/.env.development
   
   # Edit frontend/.env.development to customize backend connection settings if needed
   # Default values work for local development
   ```

### Running the System

1. **Start the backend server:**
   ```bash
   python scripts/start_dev.py
   ```
   
   You should see:
   ```
   ✅ Server starting on http://localhost:8080
   📝 To start the frontend, run: cd frontend && npm run dev
   ```

2. **In a new terminal, start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   
   The frontend will start on `http://localhost:5173`

3. **Open your browser** and navigate to `http://localhost:5173`

## 📖 Usage

### Creating a Project

1. **Wait for connection**: The chat panel will show "Connected" when ready
2. **Describe your project** in the chat interface:
   - "Create a React todo app with TypeScript"
   - "Build a Python Flask API with user authentication"
   - "Make a Node.js Express server with MongoDB"
3. **Watch agents work**: 
   - See real-time messages as agents plan and implement
   - Watch the file tree grow as files are created
   - View generated code in the code editor
4. **Monitor progress**: 
   - Agent status indicators show which agents are active
   - Progress messages appear in the chat
   - Files appear in the tree as they're created

### Example Prompts

- "Create a simple Flask web API with user authentication"
- "Build a React todo app with TypeScript and Tailwind CSS"
- "Make a Python data analysis script that processes CSV files"
- "Create a Node.js microservice with Express and MongoDB"
- "Build a Vue.js dashboard with charts and real-time data"

### Agent Status Indicators

- 🟢 **Active** - Agent is currently working
- 🔵 **Delegating** - Agent is assigning tasks to children
- 🟡 **Waiting** - Agent is waiting for dependencies
- 🟣 **Completed** - Agent has finished its task
- ⚪ **Inactive** - Agent is idle
- 🔴 **Error** - Agent encountered an error

## 🏗️ Architecture

### Agent Hierarchy

```
Root Manager Agent (Project Coordinator)
├── Frontend Manager Agent
│   ├── React Component Coder
│   ├── CSS Styles Coder
│   └── TypeScript Types Coder
├── Backend Manager Agent
│   ├── API Routes Coder
│   ├── Database Models Coder
│   └── Authentication Coder
└── Documentation Manager Agent
    └── README Coder
```

### Communication Flow

1. **User Input** → Socket.IO → Backend Server
2. **Task Creation** → Root Manager Agent
3. **Task Delegation** → Child Agents (recursive)
4. **Code Generation** → Real-time streaming to frontend
5. **Status Updates** → Live UI updates

### Message Protocol

The system uses Socket.IO for real-time communication with these message types:

- **prompt**: User input to agents
- **message**: Agent responses and status updates
- **code_stream**: Real-time code generation
- **agent_update**: Agent status changes
- **file_tree_update**: File system changes
- **project_status**: Overall project status

## 🧪 Testing

### Run Backend Tests
```bash
python -m pytest test/
```

### Run Integration Tests
```bash
python test/test_server_integration.py
python test/test_full_integration.py
```

### Test Socket.IO Connection
```bash
# Run the test server
python test_socketio_connection.py

# Then open the frontend and check the connection
```

### Manual Testing
```bash
# Run the demo script
python scripts/demo.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# LLM Provider API Keys (need at least one)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_GEMINI_API_KEY=your_google_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here

# Server Configuration
HOST=localhost
PORT=8080

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

### LLM Providers

The system supports multiple LLM providers:

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3 Sonnet, Claude-3 Opus
- **Google AI**: Gemini Pro, Gemini Flash
- **DeepSeek**: DeepSeek V3, DeepSeek R1

## 📁 Project Structure

```
HMA-LLM-Software/
├── src/                    # Backend source code
│   ├── agents/            # Agent implementations
│   ├── llm/              # LLM provider integrations
│   ├── languages/        # Agent communication languages
│   │   ├── manager_language/ # Manager agent DSL
│   │   ├── coder_language/   # Coder agent DSL
│   │   └── tester_language/  # Tester agent DSL
│   └── server.py         # Socket.IO server
├── frontend/              # React frontend
│   ├── src/              # Frontend source
│   ├── components/       # React components
│   └── package.json      # Frontend dependencies
├── test/                  # Test suite
├── scripts/              # Utility scripts
├── prompts/              # Agent prompt templates
└── requirements.txt      # Python dependencies
```

## 🚨 Troubleshooting

### Connection Issues

If the frontend shows "Disconnected":
1. Check the backend server is running
2. Verify the Socket.IO URL matches (default: `ws://localhost:8080`)
3. Check browser console for errors
4. Try the test server: `python test_socketio_connection.py`

### Socket.IO Specific Issues

If you see WebSocket errors:
1. Make sure both `socket.io-client` (frontend) and `python-socketio` (backend) are installed
2. Check that the Socket.IO path is `/ws` on both frontend and backend
3. Verify CORS is enabled on the backend (`cors_allowed_origins='*'`)

### No Agent Responses

If agents don't respond:
1. Check you have at least one API key configured in `.env`
2. Verify the API key is valid and has credits
3. Check the backend server logs for errors

### File Creation Issues

If files aren't appearing:
1. Check the `generated_projects` directory exists
2. Verify write permissions
3. Check backend logs for file system errors

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with React, TypeScript, Python, and Socket.IO
- Powered by advanced LLMs from OpenAI, Anthropic, Google, and DeepSeek
- Inspired by hierarchical software development practices

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Check the docs for detailed information

---

**Built with ❤️ by the HMA-LLM team**
