import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  Send,
  User,
  Bot,
  Plus,
  MessageSquare,
  Loader2,
  AlertCircle,
  Square,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';
import websocketService, {
  ChatMessage as WSChatMessage,
  AgentUpdate,
  ProjectInitStatus
} from '../../src/services/websocket';
import { useSocketEvent } from '../../src/hooks/useSocketEvent';
import { ChatMessage as Message, ProjectInitializationState, Language } from '../../src/types';

// More compatible UUID generation function
const generateId = (): string => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    try {
      return crypto.randomUUID();
    } catch {
      // Fallback if crypto.randomUUID fails
    }
  }
  // Fallback UUID generation for older browsers
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

interface ChatPanelProps {
  isConnected: boolean;
  onNewChat?: () => void;
  onProjectStart?: (language: Language, prompt: string, projectName?: string) => void;
  projectInitState?: ProjectInitializationState;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ 
  isConnected, 
  onNewChat,
  projectInitState 
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeAgents, setActiveAgents] = useState<Map<string, AgentUpdate>>(new Map());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasWelcomedRef = useRef(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Manage WebSocket connection lifecycle
  useEffect(() => {
    let reconnectInterval: NodeJS.Timeout | null = null;
    
    const connect = () => {
      if (websocketService.getConnectionStatus() === 'disconnected') {
        try {
          websocketService.connect();
        } catch (err) {
          console.error('Failed to initialize WebSocket connection:', err);
          setError('Failed to initialize WebSocket connection');
        }
      }
    };

    connect();

    // Reconnect on unmount/mount cycles or network drops
    reconnectInterval = setInterval(connect, 10_000); // light heartbeat retry

    return () => {
      if (reconnectInterval) {
        clearInterval(reconnectInterval);
      }
      try {
        if (websocketService.disconnect) {
          websocketService.disconnect();
        }
      } catch (err) {
        console.error('Error during WebSocket cleanup:', err);
      }
    };
  }, []);

  const handleConnectionStatus = useCallback(() => {
    const status = websocketService.getConnectionStatus();
    if (status === 'connected') {
      setError(null);
      if (!hasWelcomedRef.current) {
        try {
          websocketService.newChat();
          hasWelcomedRef.current = true;
        } catch (err) {
          console.error('Failed to send welcome message:', err);
          setError('Failed to initialize chat');
        }
      }
    } else if (status === 'disconnected') {
      setError('Disconnected from server');
      hasWelcomedRef.current = false; // allow welcome after reconnect
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
  });

  /**
   * Track agent lifecycle; derive loading state from activeAgents size.
   */
  useSocketEvent('agent_update', (update: AgentUpdate) => {
    setActiveAgents(prev => {
      const next = new Map(prev);
      if (update.status === 'inactive' || update.status === 'completed' || update.status === 'error') {
        next.delete(update.agentId);
      } else {
        next.set(update.agentId, update);
      }
      setIsLoading(next.size > 0);
      return next;
    });
  });

  useSocketEvent('error', (errorMessage: string) => {
    setError(errorMessage);
    setIsLoading(false);
  });

  // Handle project initialization events
  useSocketEvent('project_init_status', (status: ProjectInitStatus) => {
    console.log('Project initialization status:', status);
    
    // Add system message about phase changes
    if (status.message) {
      const systemMessage: Message = {
        id: generateId(),
        type: 'system',
        content: status.message,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, systemMessage]);
    }
  });

  const handleApprove = () => {
    if (!projectInitState?.isActive || !projectInitState?.phase) {
      return;
    }

    try {
      websocketService.approvePhase(projectInitState.phase);
      
      const approvalMessage: Message = {
        id: generateId(),
        type: 'user',
        content: `Approved Phase ${projectInitState.phase}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, approvalMessage]);
    } catch (err) {
      console.error('Failed to approve phase:', err);
      setError('Failed to approve phase');
    }
  };

  const handleReject = () => {
    if (!projectInitState?.isActive || !projectInitState?.phase) {
      return;
    }

    const feedback = inputValue.trim();
    
    try {
      websocketService.rejectPhase(projectInitState.phase, feedback || undefined);
      
      const rejectionMessage: Message = {
        id: generateId(),
        type: 'user',
        content: feedback ? `Rejected Phase ${projectInitState.phase}: ${feedback}` : `Rejected Phase ${projectInitState.phase}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, rejectionMessage]);
      setInputValue('');
    } catch (err) {
      console.error('Failed to reject phase:', err);
      setError('Failed to reject phase');
    }
  };

  const handleSendMessage = async () => {
    // If in project initialization mode and waiting for approval
    if (projectInitState?.isActive && projectInitState?.requiresApproval) {
      // Don't send regular messages during approval phase
      return;
    }

    if (isLoading) {
      // Already thinking → user wants to stop the agent(s)
      try {
        websocketService.stopAgentThinking();
        
        const stopMessage: Message = {
          id: generateId(),
          type: 'system',
          content: 'Agent stopped successfully.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, stopMessage]);
        
        // Immediately clear loading state and active agents
        setIsLoading(false);
        setActiveAgents(new Map());
        setError(null);
      } catch (err) {
        console.error('Failed to stop agent thinking:', err);
        setError('Failed to stop agent');
      }
      return;
    }

    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: generateId(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');
    setError(null);
    setIsLoading(true); // optimistic until first agent_update

    try {
      websocketService.sendPrompt(inputValue);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message');
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    if (isLoading) {
      try {
        websocketService.stopAgentThinking();
      } catch (err) {
        console.error('Failed to stop agent thinking:', err);
      }
    }

    setIsLoading(false);
    setMessages([]);
    setError(null);
    setActiveAgents(new Map());
    onNewChat?.();
    
    // Directly send new chat message to backend - let backend handle welcome message
    try {
      websocketService.newChat();
    } catch (err) {
      console.error('Failed to start new chat:', err);
      setError('Failed to start new chat');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Derived placeholder string for clarity
  const inputPlaceholder = useMemo(() => {
    if (!isConnected) return 'Connecting to server...';
    return isLoading ? 'Agent is thinking... Click Stop to cancel' : 'Describe what you want to build...';
  }, [isConnected, isLoading]);

  return (
    <div className="h-full bg-gray-900 border-r border-yellow-400/20 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-yellow-400/20 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-yellow-400" />
            <h2 className="text-yellow-400 font-semibold text-lg">AI Assistant</h2>
          </div>
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-3 py-1.5 bg-yellow-400 hover:bg-yellow-300 text-black rounded-lg transition-colors text-sm font-medium"
          >
            <Plus className="w-4 h-4" />
            New Chat
          </button>
        </div>
        <p className="text-gray-400 text-sm">
          {activeAgents.size > 0 ? `${activeAgents.size} agent${activeAgents.size > 1 ? 's' : ''} working...` : 'Ready to help you build'}
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(message => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
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
              className={`max-w-[80%] rounded-lg p-3 ${message.type === 'user' ? 'bg-yellow-400 text-black ml-auto' : message.type === 'system' ? 'bg-gray-800/50 text-gray-400 border border-gray-700' : 'bg-gray-800 text-gray-100 border border-yellow-400/20'}`}
            >
              {message.metadata?.codeBlock ? (
                <pre className="text-sm font-mono overflow-x-auto">
                  <code className={`language-${message.metadata.syntax || 'text'}`}>{message.content}</code>
                </pre>
              ) : (
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
              )}
              <p className={`text-xs mt-1 ${message.type === 'user' ? 'text-black/70' : 'text-gray-400'}`}>{message.timestamp.toLocaleTimeString()}</p>
              {message.agentId && activeAgents.has(message.agentId) && (
                <div className="mt-2 flex items-center gap-2">
                  <Loader2 className="w-3 h-3 animate-spin text-yellow-400" />
                  <span className="text-xs text-yellow-400">{activeAgents.get(message.agentId)?.task || 'Working...'}</span>
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

      {/* Input Section */}
      <div className="p-4 bg-gray-900 border-t border-yellow-400/20">
        {/* Error Message */}
        {error && (
          <div className="mb-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span className="text-red-400 text-sm">{error}</span>
          </div>
        )}

        {/* Project Initialization Status */}
        {projectInitState?.isActive && (
          <div className="mb-4 p-3 bg-yellow-400/10 border border-yellow-400/20 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-yellow-400" />
              <span className="text-yellow-400 font-medium">
                Phase {projectInitState.phase}: {projectInitState.phaseTitle}
              </span>
              <div className={`px-2 py-1 rounded text-xs ${
                projectInitState.status === 'waiting_approval' 
                  ? 'bg-yellow-400/20 text-yellow-400' 
                  : 'bg-blue-400/20 text-blue-400'
              }`}>
                {projectInitState.status === 'waiting_approval' ? 'Waiting for Approval' : 'Active'}
              </div>
            </div>
            {projectInitState.requiresApproval && (
              <div className="text-sm text-gray-300 mb-3">
                The AI has completed this phase and is waiting for your approval to continue.
              </div>
            )}
          </div>
        )}

        {/* Approval Buttons or Regular Input */}
        {projectInitState?.isActive && projectInitState?.requiresApproval ? (
          <div className="space-y-3">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Add feedback (optional) or approve to continue..."
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-yellow-400 resize-none"
              rows={2}
            />
            <div className="flex items-center gap-3">
              <button
                onClick={handleApprove}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
              >
                <CheckCircle className="w-4 h-4" />
                Approve Phase {projectInitState.phase}
              </button>
              <button
                onClick={handleReject}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium"
              >
                <XCircle className="w-4 h-4" />
                Reject & Give Feedback
              </button>
            </div>
          </div>
        ) : (
          <div className="flex gap-3">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={inputPlaceholder}
              className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-yellow-400 resize-none"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
            <button
              onClick={handleSendMessage}
              disabled={(!inputValue.trim() && !isLoading) || !isConnected}
              className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                isLoading
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-yellow-400 hover:bg-yellow-300 disabled:bg-gray-600 disabled:cursor-not-allowed text-black'
              }`}
            >
              {isLoading ? (
                <>
                  <Square className="w-4 h-4" />
                  Stop
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Send
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPanel;
