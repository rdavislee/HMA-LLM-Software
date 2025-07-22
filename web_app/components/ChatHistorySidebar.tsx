import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { 
  Search, 
  MessageCircle, 
  Settings, 
  X, 
  Star,
  Clock
} from 'lucide-react';

interface ChatHistoryItem {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  messageCount: number;
  isStarred?: boolean;
}

interface ChatHistorySidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChatHistorySidebar({ isOpen, onClose }: ChatHistorySidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [chatHistory] = useState<ChatHistoryItem[]>([
    {
      id: '1',
      title: 'React Component Development',
      lastMessage: 'Create a React component for a todo list',
      timestamp: '2 hours ago',
      messageCount: 12,
      isStarred: true
    },
    {
      id: '2',
      title: 'Python Data Validation',
      lastMessage: 'Generate a Python function for data validation',
      timestamp: '1 day ago',
      messageCount: 8
    },
    {
      id: '3',
      title: 'JavaScript Debugging',
      lastMessage: 'Help me debug this JavaScript error',
      timestamp: '2 days ago',
      messageCount: 15,
      isStarred: true
    },
    {
      id: '4',
      title: 'CSS Animation',
      lastMessage: 'Create a CSS animation for loading spinner',
      timestamp: '1 week ago',
      messageCount: 6
    },
    {
      id: '5',
      title: 'API Integration',
      lastMessage: 'Help with REST API integration',
      timestamp: '1 week ago',
      messageCount: 10
    }
  ]);

  const [recentChats] = useState<ChatHistoryItem[]>([
    {
      id: '6',
      title: 'Database Schema Design',
      lastMessage: 'Design a database schema for user management',
      timestamp: '3 hours ago',
      messageCount: 7
    },
    {
      id: '7',
      title: 'TypeScript Types',
      lastMessage: 'Create TypeScript interfaces for API responses',
      timestamp: '5 hours ago',
      messageCount: 4
    },
    {
      id: '8',
      title: 'Authentication System',
      lastMessage: 'Implement JWT authentication in Node.js',
      timestamp: '6 hours ago',
      messageCount: 18
    }
  ]);

  const starredChats = chatHistory.filter(chat => chat.isStarred);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm" 
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className="relative w-80 h-full bg-card/95 backdrop-blur-sm border-r border-border/50 shadow-2xl">
        {/* Header */}
        <div className="p-4 border-b border-border/50 bg-gradient-to-r from-card to-card/80">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-primary/20 text-primary border border-primary/30">
                  CA
                </AvatarFallback>
              </Avatar>
              <div>
                <h3 className="font-medium text-sm">Chat History</h3>
                <p className="text-xs text-muted-foreground">Colony AI</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <Settings className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-input-background/50 border-border/50 focus:border-primary/50 focus:bg-input-background/80"
            />
          </div>
        </div>

        {/* Navigation */}
        <div className="p-4 border-b border-border/50">
          <div className="space-y-2">
            <Button variant="secondary" className="w-full justify-start gap-2 bg-primary/10 hover:bg-primary/20 border-primary/20">
              <MessageCircle className="h-4 w-4" />
              Conversations
              <Badge variant="secondary" className="ml-auto bg-primary/20 text-primary">
                {chatHistory.length}
              </Badge>
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2 hover:bg-secondary/50">
              <Star className="h-4 w-4" />
              Starred
              <Badge variant="secondary" className="ml-auto">
                {starredChats.length}
              </Badge>
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2 hover:bg-secondary/50">
              <Clock className="h-4 w-4" />
              Recent
              <Badge variant="secondary" className="ml-auto">
                {recentChats.length}
              </Badge>
            </Button>
          </div>
        </div>

        {/* Chat History List */}
        <div className="flex-1 overflow-y-auto">
          {/* Starred Section */}
          {starredChats.length > 0 && (
            <div className="p-4 border-b border-border/50">
              <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
                Starred
              </h4>
              <div className="space-y-2">
                {starredChats.map((chat) => (
                  <div
                    key={chat.id}
                    className="p-3 rounded-lg bg-gradient-to-r from-secondary/30 to-secondary/10 hover:from-secondary/50 hover:to-secondary/20 cursor-pointer transition-all duration-200 border border-border/30 hover:border-primary/30"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Star className="h-3 w-3 text-yellow-400 fill-yellow-400" />
                        <p className="font-medium text-sm line-clamp-1">{chat.title}</p>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                      {chat.lastMessage}
                    </p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{chat.messageCount} messages</span>
                      <span>{chat.timestamp}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Conversations */}
          <div className="p-4">
            <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
              Recent Conversations
            </h4>
            <div className="space-y-2">
              {chatHistory.map((chat) => (
                <div
                  key={chat.id}
                  className="p-3 rounded-lg bg-secondary/10 hover:bg-secondary/20 cursor-pointer transition-all duration-200 border border-transparent hover:border-border/50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <p className="font-medium text-sm line-clamp-1">{chat.title}</p>
                    {chat.isStarred && (
                      <Star className="h-3 w-3 text-yellow-400 fill-yellow-400" />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                    {chat.lastMessage}
                  </p>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{chat.messageCount} messages</span>
                    <span>{chat.timestamp}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}