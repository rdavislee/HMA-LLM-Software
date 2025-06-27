# HMA-LLM Software Construction

A hierarchical multi-agent system for automated software construction using Large Language Models (LLMs).

## 🎯 Overview

HMA-LLM is a sophisticated system that uses multiple AI agents working in a hierarchical structure to automatically generate software projects. The system consists of:

- **Manager Agents**: High-level agents that plan and coordinate project structure
- **Coder Agents**: Specialized agents that write and modify code files
- **Real-time Frontend**: Modern React interface for interacting with the system
- **WebSocket Backend**: Real-time communication between frontend and agents

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
- **WebSocket Server**: Real-time bidirectional communication
- **Multi-LLM Support**: OpenAI, Anthropic, Google AI integration
- **Project Management**: Automatic project creation and file management
- **Error Handling**: Robust error handling and recovery

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **npm or yarn**
- **LLM API Key** (OpenAI, Anthropic, or Google AI)

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
   cd new_frontend
   npm install
   cd ..
   ```

4. **Configure environment:**
   ```bash
   cp config/env_example .env
   # Edit .env and add your API keys
   ```

### Running the System

1. **Start the backend server:**
   ```bash
   python scripts/start_dev.py
   ```

2. **In a new terminal, start the frontend:**
   ```bash
   cd new_frontend
   npm run dev
   ```

3. **Open your browser** to the URL shown by Vite (usually `http://localhost:5173`)

## 📖 Usage

### Creating a Project

1. **Describe your project** in the chat interface
2. **Watch agents work** - The system will create a hierarchical structure
3. **Monitor progress** - See real-time updates in the file tree and chat
4. **View generated code** - Click on files to see the generated content

### Example Prompts

- "Create a simple Flask web API with user authentication"
- "Build a React todo app with TypeScript and Tailwind CSS"
- "Make a Python data analysis script that processes CSV files"
- "Create a Node.js microservice with Express and MongoDB"

### Agent Status Indicators

- 🟢 **Active** - Agent is currently working
- 🔵 **Delegating** - Agent is assigning tasks to children
- 🟡 **Waiting** - Agent is waiting for dependencies
- 🟣 **Completion** - Agent is finishing up
- ⚪ **Inactive** - Agent is idle

## 🏗️ Architecture

### Agent Hierarchy

```
Root Manager Agent
├── Project Manager Agent
│   ├── Frontend Coder Agent
│   ├── Backend Coder Agent
│   └── Database Coder Agent
└── Documentation Manager Agent
    └── README Coder Agent
```

### Communication Protocol

Agents communicate through a hierarchical message protocol:

- **Delegation Messages**: Parent → Child task assignment
- **Result Messages**: Child → Parent task completion
- **Status Updates**: Real-time agent state changes
- **Code Streaming**: Live code generation updates

### Frontend-Backend Integration

- **WebSocket Connection**: Real-time bidirectional communication
- **Message Types**: Prompts, agent updates, code streams, delegations
- **Auto-reconnect**: Handles connection loss gracefully
- **Error Handling**: Robust error recovery and user feedback

## 🧪 Testing

### Run Backend Tests
```bash
python -m pytest test/
```

### Run Frontend Tests
```bash
cd new_frontend
npm test
```

### Run Integration Tests
```bash
python test/test_server_integration.py
```

## 🎬 Demo

Run the demo to see the system in action:

```bash
python scripts/demo.py
```

This will show:
- Agent hierarchy creation
- Task delegation
- Code generation
- Project structure evolution

## 🔧 Configuration

### Environment Variables

Copy `config/env_example` to `.env` and configure:

```bash
# LLM Provider (choose one)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

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
- **Anthropic**: Claude-3 Sonnet, Claude-3 Haiku
- **Google AI**: Gemini Pro, Gemini Flash

## 📁 Project Structure

```
HMA-LLM-Software/
├── src/                    # Backend source code
│   ├── agents/            # Agent implementations
│   ├── llm/               # LLM provider integrations
│   ├── messages/          # Communication protocol
│   ├── orchestrator/      # Agent orchestration
│   └── server.py          # WebSocket server
├── new_frontend/          # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # WebSocket service
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx        # Main app component
│   └── package.json
├── scripts/               # Utility scripts
├── test/                  # Test files
├── config/                # Configuration files
└── requirements.txt       # Python dependencies
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run tests** to ensure everything works
6. **Submit a pull request**

### Development Guidelines

- **Code Style**: Follow PEP 8 for Python, ESLint for TypeScript
- **Testing**: Add tests for new features
- **Documentation**: Update docs for API changes
- **Commits**: Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models
- **Anthropic** for Claude models
- **Google AI** for Gemini models
- **React** and **Vite** for the frontend framework
- **Tailwind CSS** for styling

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Check the docs for detailed information

---

**Built with ❤️ by the HMA-LLM team**
