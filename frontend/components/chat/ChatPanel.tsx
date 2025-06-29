import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Plus, History, MessageSquare, Loader2, AlertCircle, Square } from 'lucide-react';
import websocketService, { ChatMessage as WSChatMessage, AgentUpdate } from '../../src/services/websocket';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  agentId?: string;
  metadata?: {
    filePath?: string;
    codeBlock?: boolean;
    syntax?: string;
  };
}

interface Settings {
  theme: 'light' | 'dark' | 'system';
  tabSize: number;
  showLineNumbers: boolean;
  showTimestamps: boolean;
  performanceMode: 'balanced' | 'performance' | 'quality';
  accentColor: string;
  fontSize: number;
  autoSave: boolean;
}

interface ChatPanelProps {
  onNewChat?: () => void;
  settings?: Settings;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ onNewChat, settings }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('disconnected');
  const [activeAgents, setActiveAgents] = useState<Map<string, AgentUpdate>>(new Map());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize WebSocket connection
  useEffect(() => {
    // Connect to WebSocket server
    websocketService.connect();

    // Set up event listeners
    websocketService.on('connected', () => {
      setConnectionStatus('connected');
      setError(null);
      console.log('ChatPanel: Connected to server');
    });

    websocketService.on('disconnected', () => {
      setConnectionStatus('disconnected');
      setError('Disconnected from server');
    });

    websocketService.on('message', (wsMessage: WSChatMessage) => {
      const message: Message = {
        id: wsMessage.id,
        type: wsMessage.sender === 'user' ? 'user' : wsMessage.sender === 'system' ? 'system' : 'assistant',
        content: wsMessage.content,
        timestamp: new Date(wsMessage.timestamp),
        agentId: wsMessage.agentId,
        metadata: wsMessage.metadata
      };
      
      setMessages(prev => [...prev, message]);
      setIsLoading(false);
    });

    websocketService.on('agent_update', (update: AgentUpdate) => {
      setActiveAgents(prev => {
        const newMap = new Map(prev);
        if (update.status === 'inactive' || update.status === 'completed') {
          newMap.delete(update.agentId);
        } else {
          newMap.set(update.agentId, update);
        }
        return newMap;
      });

      // Add agent status messages to chat
      if (update.status === 'active' && update.task) {
        const statusMessage: Message = {
          id: `agent-status-${Date.now()}`,
          type: 'system',
          content: `🤖 Agent ${update.agentId} started: ${update.task}`,
          timestamp: new Date(),
          agentId: update.agentId
        };
        setMessages(prev => [...prev, statusMessage]);
      }
    });

    websocketService.on('error', (errorMessage: string) => {
      setError(errorMessage);
      setIsLoading(false);
    });

    // Check initial connection status
    setConnectionStatus(websocketService.getConnectionStatus());

    // Cleanup
    return () => {
      websocketService.off('connected');
      websocketService.off('disconnected');
      websocketService.off('message');
      websocketService.off('agent_update');
      websocketService.off('error');
    };
  }, []);

  const handleSendMessage = async () => {
    // If already loading (agent is thinking), stop the current thinking
    if (isLoading) {
      websocketService.stopAgentThinking();
      setIsLoading(false);
      setError(null);
      
      // Add a system message indicating the task was stopped
      const stopMessage: Message = {
        id: Date.now().toString(),
        type: 'system',
        content: 'Previous task stopped.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, stopMessage]);
      
      // Clear active agents
      setActiveAgents(new Map());
      return;
    }
    
    if (inputValue.trim() && !isLoading && connectionStatus === 'connected') {
      const newMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: inputValue,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, newMessage]);
      setInputValue('');
      setIsLoading(true);
      setError(null);

      // Send message through WebSocket
      websocketService.sendPrompt(inputValue);
    }
  };

  const handleNewChat = () => {
    // Stop any ongoing thinking
    if (isLoading) {
      websocketService.stopAgentThinking();
      setIsLoading(false);
    }
    
    // Clear all messages
    setMessages([]);
    
    // Clear any error state
    setError(null);
    
    // Clear active agents
    setActiveAgents(new Map());
    
    // Call the parent callback to clear the code editor
    onNewChat?.();
    
    // Add the initial AI greeting message after a delay
    setTimeout(() => {
      const initialMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: 'Hello! I\'m here to help you build amazing applications. What would you like to create today?',
        timestamp: new Date()
      };
      setMessages([initialMessage]);
    }, 300);
    
    console.log('Starting new chat...');
  };

  const handleHistoryClick = () => {
    console.log('Opening chat history...');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-400';
      case 'connecting': return 'text-yellow-400';
      case 'disconnected': return 'text-red-400';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'disconnected': return 'Disconnected';
    }
  };

  return (
    <div className="h-full bg-gray-900 border-r border-yellow-400/20 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-yellow-400/20 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-yellow-400" />
            <h2 className="text-yellow-400 font-semibold text-lg">AI Assistant</h2>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-xs ${getConnectionStatusColor()}`}>
              {getConnectionStatusText()}
            </span>
            <button
              onClick={handleHistoryClick}
              className="p-2 rounded-lg hover:bg-yellow-400/10 transition-colors group"
              title="Chat History"
            >
              <History className="w-4 h-4 text-gray-400 group-hover:text-yellow-400" />
            </button>
            <button
              onClick={handleNewChat}
              className="flex items-center gap-2 px-3 py-1.5 bg-yellow-400 hover:bg-yellow-300 text-black rounded-lg transition-colors text-sm font-medium"
            >
              <Plus className="w-4 h-4" />
              New Chat
            </button>
          </div>
        </div>
        <p className="text-gray-400 text-sm">
          {activeAgents.size > 0 
            ? `${activeAgents.size} agent${activeAgents.size > 1 ? 's' : ''} working...`
            : 'Ready to help you build'
          }
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.type === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-yellow-400 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-black" />
              </div>
            )}
            {message.type === 'system' && (
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
                <AlertCircle className="w-4 h-4 text-yellow-400" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-yellow-400 text-black ml-auto'
                  : message.type === 'system'
                  ? 'bg-gray-800/50 text-gray-400 border border-gray-700'
                  : 'bg-gray-800 text-gray-100 border border-yellow-400/20'
              }`}
            >
              {message.metadata?.codeBlock ? (
                <pre className="text-sm font-mono overflow-x-auto">
                  <code className={`language-${message.metadata.syntax || 'text'}`}>
                    {message.content}
                  </code>
                </pre>
              ) : (
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
              )}
              {settings?.showTimestamps && (
                <p className={`text-xs mt-1 ${
                  message.type === 'user' ? 'text-black/70' : 'text-gray-400'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              )}
              {message.agentId && activeAgents.has(message.agentId) && (
                <div className="mt-2 flex items-center gap-2">
                  <Loader2 className="w-3 h-3 animate-spin text-yellow-400" />
                  <span className="text-xs text-yellow-400">
                    {activeAgents.get(message.agentId)?.task || 'Working...'}
                  </span>
                </div>
              )}
            </div>
            {message.type === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-yellow-400" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-yellow-400 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-black" />
            </div>
            <div className="bg-gray-800 text-gray-100 border border-yellow-400/20 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-yellow-400/20 bg-gray-800/50">
        {error && (
          <div className="mb-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-xs">
            {error}
          </div>
        )}
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              connectionStatus !== 'connected' 
                ? "Connecting to server..."
                : isLoading
                ? "Agent is thinking... Click Stop to cancel"
                : "Describe what you want to build..." 
            }
            disabled={connectionStatus !== 'connected'}
            className="flex-1 bg-gray-900 text-gray-100 border border-yellow-400/20 rounded-lg px-4 py-2 focus:outline-none focus:border-yellow-400 text-sm placeholder-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSendMessage}
            disabled={(!inputValue.trim() && !isLoading) || connectionStatus !== 'connected'}
            className={`p-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              isLoading 
                ? 'bg-red-500 hover:bg-red-600 text-white' 
                : 'bg-yellow-400 hover:bg-yellow-300 text-black'
            }`}
            title={isLoading ? 'Stop thinking' : 'Send message'}
          >
            {isLoading ? (
              <Square className="w-5 h-5" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
