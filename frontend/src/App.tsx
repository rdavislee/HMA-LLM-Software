import { useState, useEffect, useMemo, useCallback } from 'react';
import './App.css';
import AgentHierarchy from './components/AgentHierarchy';
import type { Agent } from './components/AgentHierarchy';
import ChatInterface from './components/ChatInterface';
import type { ChatMessage } from './components/ChatInterface';
import CodeDisplay from './components/CodeDisplay';
import WebSocketService from './services/websocket';

function App() {
  // State management
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: 'root',
      name: 'src',
      path: '/src',
      type: 'manager',
      status: 'idle',
      expanded: true,
      children: [
        {
          id: 'agents-manager',
          name: 'agents',
          path: '/src/agents',
          type: 'manager',
          status: 'idle',
          expanded: true,
          children: [
            { id: 'base-agent', name: 'base_agent.py', path: '/src/agents/base_agent.py', type: 'coder', status: 'idle' },
            { id: 'manager-agent', name: 'manager_agent.py', path: '/src/agents/manager_agent.py', type: 'coder', status: 'idle' },
            { id: 'coder-agent', name: 'coder_agent.py', path: '/src/agents/coder_agent.py', type: 'coder', status: 'idle' }
          ]
        },
        {
          id: 'llm-manager',
          name: 'llm',
          path: '/src/llm',
          type: 'manager',
          status: 'idle',
          expanded: false,
          children: [
            { id: 'llm-base', name: 'base.py', path: '/src/llm/base.py', type: 'coder', status: 'idle' },
            { id: 'llm-openai', name: 'openai_client.py', path: '/src/llm/openai_client.py', type: 'coder', status: 'idle' }
          ]
        }
      ]
    }
  ]);

  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'system',
      content: 'Welcome to HMA-LLM Software Construction System. Select an agent to begin.',
      timestamp: new Date()
    }
  ]);
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [codeContent, setCodeContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamingCode, setStreamingCode] = useState('');
  const [wsConnected, setWsConnected] = useState(false);

  // Initialize WebSocket service
  const ws = useMemo(() => new WebSocketService(), []);

  // Update agent status
  const updateAgentStatus = useCallback((agentId: string, status: Agent['status'], task?: string) => {
    setAgents(agents => {
      const updateStatus = (agentList: Agent[]): Agent[] => {
        return agentList.map(agent => {
          if (agent.id === agentId) {
            return { ...agent, status, currentTask: task };
          }
          if (agent.children) {
            return { ...agent, children: updateStatus(agent.children) };
          }
          return agent;
        });
      };
      return updateStatus(agents);
    });
  }, []);

  // Set up WebSocket handlers
  useEffect(() => {
    ws.onConnectionChange = (connected) => {
      setWsConnected(connected);
      setChatMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: 'system',
        content: connected ? '🟢 Connected to backend' : '🔴 Disconnected from backend',
        timestamp: new Date()
      }]);
    };

    ws.onAgentUpdate = (update) => {
      updateAgentStatus(update.agentId, update.status, update.task);
    };

    ws.onCodeStream = (update) => {
      if (update.agentId === selectedAgent?.id) {
        if (!update.isComplete) {
          setStreamingCode(prev => prev + update.content);
          setIsGenerating(true);
        } else {
          setCodeContent(streamingCode + update.content);
          setStreamingCode('');
          setIsGenerating(false);
        }
      }
    };

    ws.onDelegation = (update) => {
      setChatMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: 'system',
        content: `→ ${update.parentId} delegated to ${update.childId}: "${update.task}"`,
        timestamp: new Date()
      }]);
    };

    ws.onMessage = (message) => {
      setChatMessages(prev => [...prev, message]);
    };

    // Connect to WebSocket
    ws.connect();

    // Cleanup
    return () => {
      ws.disconnect();
    };
  }, [ws, selectedAgent, streamingCode, updateAgentStatus]);

  // Toggle agent expansion
  const toggleAgentExpansion = (agentId: string) => {
    const updateExpansion = (agents: Agent[]): Agent[] => {
      return agents.map(agent => {
        if (agent.id === agentId) {
          return { ...agent, expanded: !agent.expanded };
        }
        if (agent.children) {
          return { ...agent, children: updateExpansion(agent.children) };
        }
        return agent;
      });
    };
    setAgents(updateExpansion(agents));
  };

  // Send prompt to agent
  const sendPrompt = () => {
    if (!currentPrompt.trim() || !selectedAgent) return;

    // Add user message
    setChatMessages(prev => [...prev, {
      id: Date.now().toString(),
      sender: 'user',
      content: currentPrompt,
      timestamp: new Date()
    }]);

    // Send via WebSocket if connected, otherwise simulate
    if (wsConnected) {
      ws.sendPrompt(selectedAgent.id, currentPrompt);
    } else {
      // Simulate locally for demo
      simulateAgentResponse(selectedAgent, currentPrompt);
    }

    setCurrentPrompt('');
  };

  // Simulate agent response for demo when not connected
  const simulateAgentResponse = (agent: Agent, prompt: string) => {
    // Add agent acknowledgment
    setChatMessages(prev => [...prev, {
      id: (Date.now() + 1).toString(),
      sender: 'agent',
      agentId: agent.id,
      content: `📋 ${agent.name} received task: "${prompt}"`,
      timestamp: new Date()
    }]);

    // Update agent status
    updateAgentStatus(agent.id, 'active', prompt);

    if (agent.type === 'manager') {
      // Manager delegates to children
      updateAgentStatus(agent.id, 'delegating');
      
      setChatMessages(prev => [...prev, {
        id: (Date.now() + 2).toString(),
        sender: 'agent',
        agentId: agent.id,
        content: `🎯 Delegating tasks to child agents...`,
        timestamp: new Date()
      }]);

      // Simulate delegation
      setTimeout(() => {
        if (agent.children) {
          agent.children.forEach((child, index) => {
            setTimeout(() => {
              updateAgentStatus(child.id, 'active', `Sub-task from ${agent.name}`);
              setChatMessages(prev => [...prev, {
                id: (Date.now() + index).toString(),
                sender: 'system',
                content: `→ Delegated to ${child.name}`,
                timestamp: new Date()
              }]);
            }, index * 500);
          });
        }
        updateAgentStatus(agent.id, 'waiting');
      }, 1000);
    } else {
      // Coder starts generating code
      simulateCodeGeneration(agent);
    }
  };

  // Simulate code generation for demo
  const simulateCodeGeneration = (agent: Agent) => {
    setStreamingCode('');
    setIsGenerating(true);
    
    setChatMessages(prev => [...prev, {
      id: (Date.now() + 2).toString(),
      sender: 'agent',
      agentId: agent.id,
      content: `💻 Starting code generation...`,
      timestamp: new Date()
    }]);

    const sampleCode = `"""
${agent.name} - Implementation
Generated by ${agent.id} agent
Task: ${agent.currentTask}
"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

class ${agent.name.replace('.py', '').split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('')}:
    """
    Implementation for ${agent.name}
    This code is being generated by the LLM in response to:
    "${agent.currentTask}"
    """
    
    def __init__(self, path: str):
        self.path = Path(path)
        self.status = 'initialized'
        self.context = {}
    
    async def process(self, task: str) -> Dict[str, Any]:
        """Process the assigned task."""
        # Parse the task
        parsed_task = self.parse_task(task)
        
        # Execute based on task type
        result = await self.execute_task(parsed_task)
        
        return {
            'status': 'completed',
            'result': result,
            'agent': self.path.name
        }
    
    def parse_task(self, task: str) -> Dict[str, Any]:
        """Parse the incoming task."""
        # Implementation here
        return {'task': task, 'type': 'default'}
    
    async def execute_task(self, parsed_task: Dict[str, Any]) -> Any:
        """Execute the parsed task."""
        # Implementation continues...
        await asyncio.sleep(0.1)  # Simulate processing
        return f"Completed: {parsed_task['task']}"
`;

    let index = 0;
    const interval = setInterval(() => {
      if (index < sampleCode.length) {
        setStreamingCode(prev => prev + sampleCode[index]);
        index++;
      } else {
        clearInterval(interval);
        setIsGenerating(false);
        setCodeContent(sampleCode);
        setStreamingCode('');
        
        // Update agent status
        updateAgentStatus(agent.id, 'idle');
        
        // Add completion message
        setChatMessages(prev => [...prev, {
          id: Date.now().toString(),
          sender: 'agent',
          agentId: agent.id,
          content: `✅ Completed implementation of ${agent.name}`,
          timestamp: new Date()
        }]);
      }
    }, 15);
  };

  return (
    <div className="h-screen bg-gray-900 text-gray-100 flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold text-gray-200">HMA-LLM Software Construction</h1>
          <span className={`text-xs px-2 py-1 rounded ${
            wsConnected ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
          }`}>
            {wsConnected ? 'Connected' : 'Demo Mode'}
          </span>
        </div>
        <div className="text-xs text-gray-500">
          Hierarchical Multi-Agent System
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Chat Interface */}
        <div className="w-96 bg-gray-850 border-r border-gray-700">
          <ChatInterface
            messages={chatMessages}
            selectedAgent={selectedAgent}
            currentPrompt={currentPrompt}
            onPromptChange={setCurrentPrompt}
            onSendPrompt={sendPrompt}
          />
        </div>

        {/* Right Panel */}
        <div className="flex-1 flex">
          {/* Agent Hierarchy */}
          <AgentHierarchy
            agents={agents}
            selectedAgent={selectedAgent}
            onAgentSelect={setSelectedAgent}
            onToggleExpansion={toggleAgentExpansion}
          />

          {/* Code Display */}
          <CodeDisplay
            selectedAgent={selectedAgent}
            codeContent={codeContent}
            streamingCode={streamingCode}
            isGenerating={isGenerating}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
