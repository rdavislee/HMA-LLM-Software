import { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from './ui/sheet';
import { Textarea } from './ui/textarea';
import { ThreadedChatSkeleton } from './LoadingSkeleton';
import { 
  ChevronDown, 
  ChevronRight, 
  AlertCircle, 
  Clock, 
  MessageSquare,
  RefreshCw,
  Loader2
} from 'lucide-react';
// import { useSocketEvent } from '../hooks/useSocketEvent';
import websocketService from '../services/websocket';

// Types for task-centric threading
interface TaskThread {
  taskId: string;
  summary: string;
  agentName: string;
  agentState: 'idle' | 'working' | 'error' | 'complete';
  createdAt: string;
  lastActivity: string;
  messageCount: number;
  errorCount: number;
  hasUnread: boolean;
  isCollapsed: boolean;
  messages: ThreadMessage[];
}

interface ThreadMessage {
  id: string;
  threadId: string;
  text: string;
  timestamp: string;
  sender: 'user' | 'assistant';
  type: 'normal' | 'error' | 'system';
  isRead: boolean;
}

interface ChatMessage {
  id: string;
  text: string;
  timestamp: string;
  sender: 'user' | 'assistant' | 'system';
  threadId?: string;
  agentId?: string;
}

interface ThreadedChatProps {
  onNewChat?: () => void;
  messages?: ChatMessage[];
  isConnected?: boolean;
  onMessagesUpdate?: (messages: ChatMessage[]) => void;
  isLoading?: boolean;
  onLoadingChange?: (loading: boolean) => void;
}

// Mock data for demonstration (commented out to remove unused variable)
/*
const mockThreads: TaskThread[] = [
  {
    taskId: 'task-1',
    summary: 'Create user authentication system',
    agentName: 'AuthAgent',
    agentState: 'working',
    createdAt: '2024-01-15T10:00:00Z',
    lastActivity: '2024-01-15T14:30:00Z',
    messageCount: 8,
    errorCount: 0,
    hasUnread: true,
    isCollapsed: false,
    messages: []
  }
];
*/

export function ThreadedChat({ 
  onNewChat: _onNewChat,
  messages = [],
  isConnected = false,
  onMessagesUpdate,
  isLoading: externalLoading = false,
  onLoadingChange: _onLoadingChange
}: ThreadedChatProps) {
  const [threads, setThreads] = useState<TaskThread[]>([]);
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(0);
  const [rePromptText, setRePromptText] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const threadRefs = useRef<Map<string, HTMLDivElement>>(new Map());

  // Convert messages to threads
  useEffect(() => {
    const threadMap = new Map<string, TaskThread>();
    
    messages.forEach(msg => {
      if (!msg.threadId) return;
      
      if (!threadMap.has(msg.threadId)) {
        threadMap.set(msg.threadId, {
          taskId: msg.threadId,
          summary: `Task ${msg.threadId}`,
          agentName: msg.agentId || 'Agent',
          agentState: 'working',
          createdAt: new Date().toISOString(),
          lastActivity: msg.timestamp,
          messageCount: 0,
          errorCount: 0,
          hasUnread: false,
          isCollapsed: true,
          messages: []
        });
      }
      
      const thread = threadMap.get(msg.threadId)!;
      thread.messages.push({
        id: msg.id,
        threadId: msg.threadId,
        text: msg.text,
        timestamp: msg.timestamp,
        sender: msg.sender === 'user' ? 'user' : 'assistant',
        type: 'normal',
        isRead: false
      });
      thread.messageCount++;
      thread.lastActivity = msg.timestamp;
    });
    
    setThreads(Array.from(threadMap.values()));
    setIsLoading(false);
  }, [messages]);

  // Handle WebSocket task updates - commented out as task_update event doesn't exist
  /*
  useSocketEvent('task_update', (update: any) => {
    setThreads(prev => {
      const existing = prev.find(t => t.taskId === update.taskId);
      if (existing) {
        return prev.map(t => t.taskId === update.taskId ? {
          ...t,
          agentState: update.status || t.agentState,
          agentName: update.agentId || t.agentName
        } : t);
      } else {
        return [...prev, {
          taskId: update.taskId,
          summary: update.summary || \`Task \${update.taskId}\`,
          agentName: update.agentId || 'Agent',
          agentState: update.status || 'working',
          createdAt: new Date().toISOString(),
          lastActivity: new Date().toISOString(),
          messageCount: 0,
          errorCount: 0,
          hasUnread: true,
          isCollapsed: true,
          messages: []
        }];
      }
    });
  });
  */

  // Load collapse states from localStorage
  useEffect(() => {
    const savedStates = localStorage.getItem('threadCollapseStates');
    if (savedStates) {
      const states = JSON.parse(savedStates);
      setThreads(prev => prev.map(thread => ({
        ...thread,
        isCollapsed: states[thread.taskId] ?? thread.isCollapsed
      })));
    }
  }, []);

  // Save collapse states to localStorage
  const saveCollapseStates = useCallback((updatedThreads: TaskThread[]) => {
    const states: Record<string, boolean> = {};
    updatedThreads.forEach(thread => {
      states[thread.taskId] = thread.isCollapsed;
    });
    localStorage.setItem('threadCollapseStates', JSON.stringify(states));
  }, []);

  // Agent state styling
  const getAgentStateBadge = (state: TaskThread['agentState']) => {
    const styles = {
      idle: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
      working: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      error: 'bg-red-500/20 text-red-300 border-red-500/30',
      complete: 'bg-green-500/20 text-green-300 border-green-500/30'
    };
    
    const icons = {
      idle: Clock,
      working: RefreshCw,
      error: AlertCircle,
      complete: ChevronRight
    };
    
    const Icon = icons[state];
    
    return (
      <Badge 
        variant="outline" 
        className={`${styles[state]} text-xs px-2 py-0.5 flex items-center gap-1`}
      >
        <Icon className={`h-3 w-3 ${state === 'working' ? 'animate-spin' : ''}`} />
        {state}
      </Badge>
    );
  };

  // Format timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    
    if (diffMins < 1) return 'now';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    return date.toLocaleDateString();
  };

  // Toggle thread collapse
  const toggleThread = useCallback((taskId: string) => {
    setThreads(prev => {
      const updated = prev.map(thread => 
        thread.taskId === taskId 
          ? { ...thread, isCollapsed: !thread.isCollapsed, hasUnread: false }
          : thread
      );
      saveCollapseStates(updated);
      return updated;
    });
  }, [saveCollapseStates]);

  // Open task drawer
  const openDrawer = useCallback((taskId: string) => {
    setSelectedThreadId(taskId);
    setIsDrawerOpen(true);
    setRePromptText('');
  }, []);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!containerRef.current?.contains(document.activeElement)) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setFocusedIndex(prev => Math.min(prev + 1, threads.length - 1));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setFocusedIndex(prev => Math.max(prev - 1, 0));
          break;
        case 'ArrowRight':
          e.preventDefault();
          if (threads[focusedIndex]?.isCollapsed) {
            toggleThread(threads[focusedIndex].taskId);
          }
          break;
        case 'ArrowLeft':
          e.preventDefault();
          if (threads[focusedIndex] && !threads[focusedIndex].isCollapsed) {
            toggleThread(threads[focusedIndex].taskId);
          }
          break;
        case 'Enter':
          e.preventDefault();
          if (threads[focusedIndex]) {
            openDrawer(threads[focusedIndex].taskId);
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [focusedIndex, threads, toggleThread, openDrawer]);

  // Handle re-prompt submission
  const handleRePrompt = () => {
    if (!rePromptText.trim() || !selectedThreadId) return;
    
    // Send re-prompt via WebSocket
    if (isConnected) {
      websocketService.sendPrompt(rePromptText, selectedThreadId || 'root');
    }
    
    // Add new message to the thread
    const newMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      text: rePromptText,
      timestamp: new Date().toISOString(),
      sender: 'user',
      threadId: selectedThreadId
    };
    
    if (onMessagesUpdate) {
      onMessagesUpdate([...messages, newMessage]);
    }
    
    setThreads(prev => prev.map(thread => 
      thread.taskId === selectedThreadId
        ? {
            ...thread,
            messages: [
              ...thread.messages,
              {
                id: newMessage.id,
                threadId: selectedThreadId,
                text: rePromptText,
                timestamp: newMessage.timestamp,
                sender: 'user' as const,
                type: 'normal' as const,
                isRead: true
              }
            ],
            messageCount: thread.messageCount + 1,
            lastActivity: newMessage.timestamp,
            agentState: 'working' as const
          }
        : thread
    ));
    
    setRePromptText('');
    setIsDrawerOpen(false);
  };

  const selectedThread = threads.find(t => t.taskId === selectedThreadId);

  // Show loading skeleton
  if (isLoading || externalLoading) {
    return (
      <div className="h-full flex flex-col">
        <div className="p-4 flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin text-primary" />
          <span className="text-sm text-muted-foreground">Loading tasks...</span>
        </div>
        <ThreadedChatSkeleton />
      </div>
    );
  }

  // Show empty state if no threads
  if (threads.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No active tasks</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="h-full flex flex-col"
      role="tree"
      aria-label="Task threads"
      tabIndex={0}
    >
      {/* Thread list - moved up by removing header */}
      <div className="flex-1">
        <ScrollArea className="h-full">
          <div className="p-2 space-y-2">
            {threads.map((thread, index) => (
              <div
                key={thread.taskId}
                ref={(el) => {
                  if (el) {
                    threadRefs.current.set(thread.taskId, el);
                  }
                }}
                role="group"
                aria-expanded={!thread.isCollapsed}
                aria-label={`Task: ${thread.summary}`}
                className={`border border-border/30 rounded-lg transition-all duration-200 ${
                  index === focusedIndex ? 'ring-2 ring-primary/50' : ''
                }`}
              >
                {/* Thread Header */}
                <div
                  className="p-3 cursor-pointer hover:bg-secondary/10 transition-colors"
                  onClick={() => toggleThread(thread.taskId)}
                  onDoubleClick={() => openDrawer(thread.taskId)}
                  role="article"
                  tabIndex={0}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      {/* Collapse indicator */}
                      <div className="flex-shrink-0 mt-1">
                        {thread.isCollapsed ? (
                          <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-muted-foreground" />
                        )}
                      </div>
                      
                      {/* Thread content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-sm font-medium text-foreground truncate">
                            {thread.summary}
                          </h3>
                          {thread.hasUnread && (
                            <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                          )}
                        </div>
                        
                        <div className="flex items-center gap-2 mb-2">
                          {getAgentStateBadge(thread.agentState)}
                          <span className="text-xs text-muted-foreground">
                            {thread.agentName}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <MessageSquare className="h-3 w-3" />
                            {thread.messageCount} msgs
                          </span>
                          {thread.errorCount > 0 && (
                            <span className="flex items-center gap-1 text-red-400">
                              <AlertCircle className="h-3 w-3" />
                              {thread.errorCount} errors
                            </span>
                          )}
                          <span>{formatTime(thread.lastActivity)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Expanded Messages */}
                {!thread.isCollapsed && (
                  <div className="border-t border-border/20">
                    <div className="p-3 space-y-2 max-h-64 overflow-y-auto">
                      {thread.messages.map((message) => (
                        <div
                          key={message.id}
                          className={`p-2 rounded text-sm ${
                            message.sender === 'user'
                              ? 'bg-primary/10 text-primary-foreground ml-6'
                              : message.type === 'error'
                              ? 'bg-red-500/10 text-red-300 border border-red-500/20'
                              : 'bg-secondary/10 text-secondary-foreground mr-6'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <p className="flex-1">{message.text}</p>
                            <span className="text-xs text-muted-foreground flex-shrink-0">
                              {formatTime(message.timestamp)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Task Detail Drawer */}
      <Sheet open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
        <SheetContent side="right" className="w-[500px] sm:w-[600px]">
          <SheetHeader>
            <SheetTitle className="flex items-center gap-2">
              {selectedThread?.summary}
              {selectedThread && getAgentStateBadge(selectedThread.agentState)}
            </SheetTitle>
          </SheetHeader>
          
          {selectedThread && (
            <div className="mt-6 space-y-4">
              {/* Task Details */}
              <div className="p-4 bg-secondary/10 rounded-lg">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Agent:</span>
                    <span className="ml-2">{selectedThread.agentName}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Created:</span>
                    <span className="ml-2">{formatTime(selectedThread.createdAt)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Messages:</span>
                    <span className="ml-2">{selectedThread.messageCount}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Errors:</span>
                    <span className="ml-2 text-red-400">{selectedThread.errorCount}</span>
                  </div>
                </div>
              </div>

              {/* Full Conversation */}
              <div>
                <h4 className="font-medium mb-2">Full Conversation</h4>
                <ScrollArea className="h-64 border border-border/30 rounded-lg">
                  <div className="p-3 space-y-3">
                    {selectedThread.messages.map((message) => (
                      <div
                        key={message.id}
                        className={`p-3 rounded-lg ${
                          message.sender === 'user'
                            ? 'bg-primary/10 text-primary-foreground'
                            : message.type === 'error'
                            ? 'bg-red-500/10 text-red-300 border border-red-500/20'
                            : 'bg-secondary/10 text-secondary-foreground'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <span className="text-xs font-medium">
                            {message.sender === 'user' ? 'You' : selectedThread.agentName}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {formatTime(message.timestamp)}
                          </span>
                        </div>
                        <p className="text-sm">{message.text}</p>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* Re-prompt Box */}
              <div>
                <h4 className="font-medium mb-2">Re-prompt</h4>
                <div className="space-y-2">
                  <Textarea
                    value={rePromptText}
                    onChange={(e) => setRePromptText(e.target.value)}
                    placeholder="Add additional instructions or corrections..."
                    className="min-h-24 resize-none"
                  />
                  <div className="flex gap-2">
                    <Button 
                      onClick={handleRePrompt}
                      disabled={!rePromptText.trim()}
                      className="minimalist-button"
                    >
                      Send Re-prompt
                    </Button>
                    <Button 
                      variant="outline" 
                      onClick={() => setIsDrawerOpen(false)}
                      className="minimalist-button"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}