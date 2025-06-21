# HMA-LLM Frontend

This is the frontend interface for the Hierarchical Multi-Agent LLM Software Construction System.

## Overview

The frontend provides a visual interface for interacting with the hierarchical agent system where:
- **Manager agents** control directories and delegate tasks to children
- **Coder agents** handle individual files and generate code
- All agents work in a hierarchical structure mirroring the project's file system

## Features

### 1. Agent Hierarchy View (Middle Panel)
- Visual representation of the agent tree structure
- Real-time status indicators:
  - ○ Idle (gray)
  - ● Active (blue)
  - ◐ Delegating (yellow)
  - ◑ Waiting (purple)
- Expandable/collapsible folders
- Agent selection for interaction

### 2. Chat Interface (Left Panel)
- **Top section**: Agent status display showing current agent details and task
- **Middle section**: Chat history with color-coded messages
- **Bottom section**: Input area for prompting selected agents

### 3. Code Display (Right Panel)
- Real-time code streaming as it's generated
- Line numbers and syntax highlighting
- Status bar showing file info and generation status
- Animated cursor during code generation

### 4. WebSocket Integration
- Real-time communication with backend agents
- Automatic reconnection on disconnect
- Fallback to demo mode when backend is unavailable

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

```bash
npm install
```

### Development

Run the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Architecture

### Components

- **`AgentHierarchy`**: Displays and manages the agent tree structure
- **`ChatInterface`**: Handles user prompts and displays agent communication
- **`CodeDisplay`**: Shows generated code with streaming support

### Services

- **`WebSocketService`**: Manages real-time communication with the backend

### State Management

The app uses React hooks for state management:
- Agent hierarchy state
- Chat messages
- Code generation state
- WebSocket connection status

## Usage

1. **Select an Agent**: Click on any agent in the hierarchy to select it
2. **Send a Prompt**: Type your task in the chat input and press Enter
3. **Watch Execution**:
   - Manager agents will delegate to their children
   - Coder agents will generate code in real-time
4. **View Results**: Generated code appears in the right panel

## Demo Mode

When the backend is not connected, the frontend runs in demo mode:
- Simulates agent responses
- Generates sample code for demonstration
- Shows the full interaction flow

## Customization

### Adding New Agent Types

Extend the `Agent` interface in `AgentHierarchy.tsx`:

```typescript
interface Agent {
  // ... existing fields
  customField?: any;
}
```

### Styling

The app uses Tailwind CSS. Modify styles in:
- Component files for component-specific styles
- `App.css` for global styles
- `tailwind.config.js` for theme customization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is part of the HMA-LLM Software Construction System.
