import React, { useState } from 'react';
import { Send, User, Bot, Plus, History, MessageSquare } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
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
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m here to help you build amazing applications. What would you like to create today?',
      timestamp: new Date(Date.now() - 300000)
    },
    {
      id: '2',
      type: 'user',
      content: 'I want to create a modern web application with a beautiful interface.',
      timestamp: new Date(Date.now() - 240000)
    },
    {
      id: '3',
      type: 'assistant',
      content: 'Great! I\'ll help you create a stunning modern web application. Let me start by setting up the project structure and implementing the core components.',
      timestamp: new Date(Date.now() - 180000)
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async () => {
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

      try {
        // Simulate AI response with error handling
        await new Promise((resolve, reject) => {
          setTimeout(() => {
            // Simulate occasional network errors
            if (Math.random() < 0.1) {
              reject(new Error('Network error occurred'));
            } else {
              resolve(true);
            }
          }, 1000);
        });

        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: 'I understand your request. Let me work on that for you...',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiResponse]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        console.error('Chat error:', err);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleNewChat = () => {
    // Clear all messages
    setMessages([]);
    
    // Clear any error state
    setError(null);
    
    // Call the parent callback to clear the code editor
    onNewChat?.();
    
    // Add the initial AI greeting message after a 500ms delay
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
        <p className="text-gray-400 text-sm">Ready to help you build</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.type === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-yellow-400 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-black" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-yellow-400 text-black ml-auto'
                  : 'bg-gray-800 text-gray-100 border border-yellow-400/20'
              }`}
            >
              <p className="text-sm leading-relaxed">{message.content}</p>
              {settings?.showTimestamps && (
                <p className={`text-xs mt-1 ${
                  message.type === 'user' ? 'text-black/70' : 'text-gray-400'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              )}
            </div>
            {message.type === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-yellow-400" />
              </div>
            )}
          </div>
        ))}
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
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder={isLoading ? "AI is thinking..." : "Type your message..."}
            disabled={isLoading}
            className="flex-1 bg-gray-700 border border-yellow-400/20 rounded-lg px-3 py-2 text-gray-100 placeholder-gray-400 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400 disabled:opacity-50"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="bg-yellow-400 hover:bg-yellow-300 disabled:bg-gray-600 disabled:cursor-not-allowed text-black px-4 py-2 rounded-lg transition-colors duration-200 flex items-center justify-center"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
