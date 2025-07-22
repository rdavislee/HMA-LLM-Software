import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { Tabs } from './ui/tabs';
import { ThreadedChat } from './ThreadedChat';
import { 
  Plus, 
  MessageSquare,
  FileText,
  AlertCircle,
  Bot,
  User
} from 'lucide-react';

interface ChatMessage {
  id: string;
  text: string;
  timestamp: string;
  sender: 'user' | 'assistant' | 'system';
  threadId?: string;
  agentId?: string;
}

interface TabbedChatPanelProps {
  messages: ChatMessage[];
  onNewChat: () => void;
  isConnected?: boolean;
  onMessagesUpdate?: (messages: ChatMessage[]) => void;
  isLoading?: boolean;
  onLoadingChange?: (loading: boolean) => void;
}

export function TabbedChatPanel({ 
  messages, 
  onNewChat,
  isConnected = false,
  onMessagesUpdate,
  isLoading = false,
  onLoadingChange
}: TabbedChatPanelProps) {
  const [activeTab, setActiveTab] = useState('chat');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Format timestamp for display
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    
    if (diffMins < 1) return 'now';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Count different types of notifications for tabs
  const chatMessageCount = messages.length;
  const errorCount = 2; // Mock count
  const activeTaskCount = 3; // Mock count

  return (
    <div className="h-full flex flex-col">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
        {/* Tab Headers - borderless with padding */}
        <div className="flex-shrink-0 px-4 pt-4 pb-2">
          <div className="flex items-center justify-between">
            {/* Ghost-style tab chips */}
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('chat')}
                className={`ghost-chip flex items-center gap-2 ${
                  activeTab === 'chat' ? 'active' : ''
                }`}
              >
                <MessageSquare className="h-3 w-3" />
                Chat
                {chatMessageCount > 0 && (
                  <span className="bg-muted text-muted-foreground text-xs px-1.5 py-0.5 rounded ml-1">
                    {chatMessageCount}
                  </span>
                )}
              </button>
              
              <button
                onClick={() => setActiveTab('tasks')}
                className={`ghost-chip flex items-center gap-2 ${
                  activeTab === 'tasks' ? 'active' : ''
                }`}
              >
                <FileText className="h-3 w-3" />
                Tasks
                {activeTaskCount > 0 && (
                  <span className="bg-muted text-muted-foreground text-xs px-1.5 py-0.5 rounded ml-1">
                    {activeTaskCount}
                  </span>
                )}
              </button>
              
              <button
                onClick={() => setActiveTab('logs')}
                className={`ghost-chip flex items-center gap-2 ${
                  activeTab === 'logs' ? 'active' : ''
                }`}
              >
                <AlertCircle className="h-3 w-3" />
                Logs
                {errorCount > 0 && (
                  <span className="bg-destructive/20 text-destructive text-xs px-1.5 py-0.5 rounded ml-1">
                    {errorCount}
                  </span>
                )}
              </button>
            </div>
            
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={onNewChat}
              className="minimalist-button"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Tab Contents - full height, no padding constraints */}
        <div className="flex-1 min-h-0">
          {/* Chat Tab - Borderless Messages */}
          {activeTab === 'chat' && (
            <div className="h-full">
              <ScrollArea className="h-full">
                <div className="px-4 py-2">
                  {messages.length === 0 ? (
                    <div className="flex items-center justify-center h-64 text-muted-foreground">
                      <div className="text-center">
                        <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p className="text-body">Start a conversation with Colony AI</p>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {messages.map((message) => (
                        <div
                          key={message.id}
                          className="flex items-start gap-3 py-2"
                        >
                          <div className="flex-shrink-0 mt-1">
                            {message.sender === 'user' ? (
                              <div className="w-6 h-6 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center">
                                <User className="h-3 w-3 text-primary" />
                              </div>
                            ) : (
                              <div className="w-6 h-6 rounded-full bg-secondary/10 border border-border flex items-center justify-center">
                                <Bot className="h-3 w-3 text-foreground" />
                              </div>
                            )}
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-tab font-medium">
                                {message.sender === 'user' ? 'You' : 'Colony AI'}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {formatTime(message.timestamp)}
                              </span>
                            </div>
                            <div className="text-body text-foreground leading-relaxed">
                              {message.text}
                            </div>
                          </div>
                        </div>
                      ))}
                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </div>
              </ScrollArea>
            </div>
          )}

          {/* Tasks Tab - Full Height */}
          {activeTab === 'tasks' && (
            <div className="h-full">
              <ThreadedChat 
                onNewChat={onNewChat}
                messages={messages}
                isConnected={isConnected}
                onMessagesUpdate={onMessagesUpdate}
                isLoading={isLoading}
                onLoadingChange={onLoadingChange}
              />
            </div>
          )}

          {/* Logs Tab - Full Height */}
          {activeTab === 'logs' && (
            <div className="h-full">
              <ScrollArea className="h-full">
                <div className="px-4 py-2 space-y-3">
                  {/* Mock log entries with borderless styling */}
                  <div className="flex items-start gap-3 py-2 border-l-2 border-l-destructive pl-3">
                    <AlertCircle className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-tab font-medium text-destructive">Error</span>
                        <span className="text-xs text-muted-foreground">2m ago</span>
                      </div>
                      <p className="text-body text-destructive">
                        Failed to connect to database: Connection timeout
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3 py-2 border-l-2 border-l-yellow-500 pl-3">
                    <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-tab font-medium text-yellow-500">Warning</span>
                        <span className="text-xs text-muted-foreground">5m ago</span>
                      </div>
                      <p className="text-body text-yellow-500">
                        API rate limit approaching: 80% of quota used
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3 py-2 border-l-2 border-l-blue-500 pl-3">
                    <FileText className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-tab font-medium text-blue-500">Info</span>
                        <span className="text-xs text-muted-foreground">8m ago</span>
                      </div>
                      <p className="text-body text-blue-500">
                        Code generation completed successfully for Button.tsx
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3 py-2 border-l-2 border-l-green-500 pl-3">
                    <FileText className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-tab font-medium text-green-500">Success</span>
                        <span className="text-xs text-muted-foreground">12m ago</span>
                      </div>
                      <p className="text-body text-green-500">
                        All tests passed for authentication module
                      </p>
                    </div>
                  </div>
                </div>
              </ScrollArea>
            </div>
          )}
        </div>
      </Tabs>
    </div>
  );
}