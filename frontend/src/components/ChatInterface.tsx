import React, { useRef, useEffect } from 'react';
import type { Agent } from './AgentHierarchy';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'system' | 'agent';
  agentId?: string;
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  messages: ChatMessage[];
  selectedAgent: Agent | null;
  currentPrompt: string;
  onPromptChange: (value: string) => void;
  onSendPrompt: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  selectedAgent,
  currentPrompt,
  onPromptChange,
  onSendPrompt
}) => {
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendPrompt();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Status/Description Panel */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-400 mb-3">AGENT STATUS</h2>
        {selectedAgent ? (
          <div className="bg-gray-800 rounded p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-200">{selectedAgent.name}</span>
              <span className={`text-xs px-2 py-1 rounded ${
                selectedAgent.status === 'active' ? 'bg-blue-900 text-blue-300' :
                selectedAgent.status === 'delegating' ? 'bg-yellow-900 text-yellow-300' :
                selectedAgent.status === 'waiting' ? 'bg-purple-900 text-purple-300' :
                'bg-gray-700 text-gray-400'
              }`}>
                {selectedAgent.status.toUpperCase()}
              </span>
            </div>
            <p className="text-xs text-gray-400 mb-1">Type: {selectedAgent.type}</p>
            <p className="text-xs text-gray-400 mb-1">Path: {selectedAgent.path}</p>
            {selectedAgent.currentTask && (
              <div className="mt-2">
                <p className="text-xs text-gray-500 mb-1">Current Task:</p>
                <p className="text-xs text-gray-300 bg-gray-900 rounded p-2">{selectedAgent.currentTask}</p>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500">Select an agent to view details</p>
        )}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg) => (
          <div key={msg.id} className={`text-sm chat-message-enter ${
            msg.sender === 'user' ? 'text-right' : 'text-left'
          }`}>
            <div className={`inline-block max-w-[80%] p-3 rounded-lg ${
              msg.sender === 'user' ? 'bg-blue-900 text-blue-100' :
              msg.sender === 'agent' ? 'bg-gray-800 text-gray-200' :
              'bg-gray-700 text-gray-300'
            }`}>
              {msg.sender === 'agent' && msg.agentId && (
                <div className="text-xs text-gray-400 mb-1 font-mono">{msg.agentId}</div>
              )}
              <div className="whitespace-pre-wrap">{msg.content}</div>
              <div className="text-xs opacity-50 mt-1">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Chat Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <textarea
            value={currentPrompt}
            onChange={(e) => onPromptChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={selectedAgent ? `Prompt ${selectedAgent.name}...` : 'Select an agent first...'}
            disabled={!selectedAgent}
            className="flex-1 bg-gray-800 text-gray-200 px-3 py-2 rounded border border-gray-700 focus:border-blue-500 focus:outline-none text-sm disabled:opacity-50 disabled:cursor-not-allowed resize-none"
            rows={2}
          />
          <button
            onClick={onSendPrompt}
            disabled={!selectedAgent || !currentPrompt.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded text-sm font-medium transition-colors self-end"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          {selectedAgent ? 
            `Prompting ${selectedAgent.type} agent: ${selectedAgent.name}` : 
            'Select an agent from the hierarchy to start'
          }
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;