import { useEffect, useRef, useCallback } from 'react';
import { Button } from './ui/button';
import { Plus, Bot, User, Loader2 } from 'lucide-react';
import { ChatMessage as WSChatMessage, AgentUpdate } from '../services/websocket';
import { useSocketEvent } from '../hooks/useSocketEvent';

interface ChatMessage {
  id: string;
  text: string;
  timestamp: string;
  sender: 'user' | 'assistant' | 'system';
  agentId?: string;
  isStreaming?: boolean;
}

interface ChatPanelProps {
  messages: ChatMessage[];
  onNewChat: () => void;
  onMessagesUpdate?: (messages: ChatMessage[]) => void;
  isLoading?: boolean;
  onLoadingChange?: (loading: boolean) => void;
}

export function ChatPanel({ messages, onNewChat, onMessagesUpdate, isLoading = false, onLoadingChange }: ChatPanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const activeAgents = useRef<Map<string, AgentUpdate>>(new Map());

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Handle incoming WebSocket messages - use callback to avoid closure issues
  const handleMessage = useCallback((wsMessage: WSChatMessage) => {
    const newMessage: ChatMessage = {
      id: wsMessage.id,
      text: wsMessage.content,
      timestamp: new Date(wsMessage.timestamp).toLocaleTimeString(),
      sender: wsMessage.sender === 'ai' ? 'assistant' : wsMessage.sender === 'user' ? 'user' : 'system',
      agentId: wsMessage.agentId
    };

    // Simply pass the new array - the parent will handle state updates
    if (onMessagesUpdate) {
      const updatedMessages = [...messages, newMessage];
      onMessagesUpdate(updatedMessages);
    }
  }, [onMessagesUpdate, messages]);

  useSocketEvent('message', handleMessage);

  // Handle agent updates - use callback to avoid closure issues
  const handleAgentUpdate = useCallback((update: AgentUpdate) => {
    if (update.status === 'inactive' || update.status === 'completed' || update.status === 'error') {
      activeAgents.current.delete(update.agentId);
    } else {
      activeAgents.current.set(update.agentId, update);
    }
    
    const hasActiveAgents = activeAgents.current.size > 0;
    onLoadingChange?.(hasActiveAgents);
  }, [onLoadingChange]);

  useSocketEvent('agent_update', handleAgentUpdate);
  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header with + button - no border */}
      <div className="p-4 bg-gradient-to-r from-background to-transparent relative">
        <div className="flex items-center justify-end">
          <Button
            variant="ghost"
            size="sm"
            onClick={onNewChat}
            className="p-2 hover:bg-transparent"
          >
            <Plus className="h-4 w-4 text-white" />
          </Button>
        </div>
      </div>

      {/* Chat Messages Window - with icons */}
      <div className="flex-1 overflow-y-auto px-4 pt-2 pb-4 space-y-4 bg-background">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {/* Assistant/System icon */}
            {message.sender !== 'user' && (
              <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-primary" />
              </div>
            )}
            
            <div className={`max-w-[80%] ${message.sender === 'user' ? 'order-first' : ''}`}>
              <div
                className={`p-3 rounded-lg backdrop-blur-sm ${
                  message.sender === 'user'
                    ? 'bg-gradient-to-r from-primary/80 to-accent/80 text-primary-foreground ml-auto border border-primary/30'
                    : message.sender === 'system'
                    ? 'bg-muted/50 text-muted-foreground border border-border/50'
                    : 'bg-gradient-to-r from-secondary/50 to-card/50 text-secondary-foreground border border-border/30'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.text}</p>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-muted-foreground">{message.timestamp}</span>
                {message.agentId && activeAgents.current.has(message.agentId) && (
                  <div className="flex items-center gap-1">
                    <Loader2 className="w-3 h-3 animate-spin text-primary" />
                    <span className="text-xs text-primary">
                      {activeAgents.current.get(message.agentId)?.task || 'Working...'}
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {/* User icon */}
            {message.sender === 'user' && (
              <div className="w-8 h-8 rounded-full bg-card border border-border flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-foreground" />
              </div>
            )}
          </div>
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-primary" />
            </div>
            <div className="bg-gradient-to-r from-secondary/50 to-card/50 text-secondary-foreground border border-border/30 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}