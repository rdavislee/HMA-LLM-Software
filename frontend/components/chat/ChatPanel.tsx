import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, User, Bot, Plus, MessageSquare, Loader2, AlertCircle, Square } from 'lucide-react';
import websocketService, { ChatMessage as WSChatMessage, AgentUpdate } from '../../src/services/websocket';
import { useSocketEvent } from '../../src/hooks/useSocketEvent';
import { Settings, ChatMessage as Message } from '../../src/types';

interface ChatPanelProps {
  onNewChat?: () => void;
  settings?: Settings;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ onNewChat, settings }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeAgents, setActiveAgents] = useState<Map<string, AgentUpdate>>(new Map());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Ensure we request a welcome message only once per browser session
  const hasWelcomedRef = useRef(false);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize and manage WebSocket connection
  useEffect(() => {
    if (websocketService.getConnectionStatus() === 'disconnected') {
      try {
        websocketService.connect();
      } catch (error) {
        setError('Failed to initialize WebSocket connection');
      }
    }
  }, []);

  const handleConnectionStatus = useCallback(() => {
    const status = websocketService.getConnectionStatus();
    if (status === 'connected') {
      setError(null);
      if (!hasWelcomedRef.current) {
        websocketService.newChat();
        hasWelcomedRef.current = true;
      }
    } else if (status === 'disconnected') {
      setError('Disconnected from server');
    }
  }, []);

  useSocketEvent('connected', handleConnectionStatus);
  useSocketEvent('disconnected', handleConnectionStatus);

  useSocketEvent('message', (wsMessage: WSChatMessage) => {
    const message: Message = {
      id: wsMessage.id,
      type: wsMessage.sender === 'user' ? 'user' : wsMessage.sender === 'system' ? 'system' : 'assistant',
      content: wsMessage.content,
      timestamp: new Date(wsMessage.timestamp),
      agentId: wsMessage.agentId,
      metadata: wsMessage.metadata
    };
    
    setMessages(prev => [...prev, message]);
    // Stop loading when a message (the response) is received.
    setIsLoading(false);
  });

  useSocketEvent('agent_update', (update: AgentUpdate) => {
    setActiveAgents(prev => {
      const newMap = new Map(prev);
      if (update.status === 'inactive' || update.status === 'completed' || update.status === 'error') {
        newMap.delete(update.agentId);
      } else {
        newMap.set(update.agentId, update);
      }
      return newMap;
    });

    if (update.status === 'completed' || update.status === 'error') {
      setIsLoading(false);
    }
  });

  useSocketEvent('error', (errorMessage: string) => {
    setError(errorMessage);
    setIsLoading(false);
  });

  const handleSendMessage = async () => {
    // If already loading (agent is thinking), stop the current thinking
    if (isLoading) {
      websocketService.stopAgentThinking();
      
      // We don't set isLoading to false immediately.
      // We wait for an 'agent_update' with a completed/error status.
      // This makes the UI more honest about the agent's state.
      const stopMessage: Message = {
        id: Date.now().toString(),
        type: 'system',
        content: 'Stop request sent. Waiting for agent to terminate...',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, stopMessage]);
      return;
    }
    
    if (inputValue.trim() && !isLoading) {
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
      try {
        websocketService.sendPrompt(inputValue);
      } catch (error) {
        setError('Failed to send message');
        setIsLoading(false);
      }
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
    
    // Send new-chat request to server (this will produce the welcome system message)
    websocketService.newChat();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
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
              websocketService.isConnected()
                ? isLoading
                  ? "Agent is thinking... Click Stop to cancel"
                  : "Describe what you want to build..." 
                : "Connecting to server..."
            }
            disabled={!websocketService.isConnected()}
            className="flex-1 bg-gray-900 text-gray-100 border border-yellow-400/20 rounded-lg px-4 py-2 focus:outline-none focus:border-yellow-400 text-sm placeholder-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSendMessage}
            disabled={(!inputValue.trim() && !isLoading) || !websocketService.isConnected()}
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
