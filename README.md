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

## 🙏 Acknowledgments

- Built with React, TypeScript, Python, and Socket.IO
- Powered by advanced LLMs from OpenAI, Anthropic, Google, and DeepSeek
- Inspired by hierarchical software development practices
