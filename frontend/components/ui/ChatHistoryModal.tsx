import React, { useState, useEffect } from 'react';
import { X, MessageSquare, Trash2, Clock, Calendar } from 'lucide-react';
import { ChatSession } from '../../src/types';
import { chatStorage } from '../../src/services/chatStorage';

interface ChatHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectChat: (session: ChatSession) => void;
}

const ChatHistoryModal: React.FC<ChatHistoryModalProps> = ({
  isOpen,
  onClose,
  onSelectChat
}) => {
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadChatHistory();
    }
  }, [isOpen]);

  const loadChatHistory = async () => {
    try {
      setLoading(true);
      const sessions = await chatStorage.loadChatSessions();
      setChatSessions(sessions);
    } catch (error) {
      console.error('Error loading chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChat = async (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    
    if (deletingId === sessionId) {
      // Confirm delete
      try {
        await chatStorage.deleteChatSession(sessionId);
        setChatSessions(prev => prev.filter(s => s.id !== sessionId));
        setDeletingId(null);
      } catch (error) {
        console.error('Error deleting chat session:', error);
      }
    } else {
      // First click - show confirmation
      setDeletingId(sessionId);
      setTimeout(() => setDeletingId(null), 3000); // Reset after 3 seconds
    }
  };

  const handleSelectChat = (session: ChatSession) => {
    onSelectChat(session);
    onClose();
  };

  const formatChatTitle = (session: ChatSession) => {
    const date = session.createdAt;
    const dateStr = date.toLocaleDateString();
    const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return `${dateStr} at ${timeStr}`;
  };

  const formatLastModified = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  const getMessagePreview = (session: ChatSession) => {
    const userMessages = session.messages.filter(m => m.type === 'user');
    if (userMessages.length > 0) {
      const firstMessage = userMessages[0].content;
      return firstMessage.length > 60 ? firstMessage.substring(0, 60) + '...' : firstMessage;
    }
    return 'No messages';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-amber-400/20 rounded-lg w-full max-w-3xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-amber-400/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-400/10 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h2 className="text-amber-400 font-semibold text-xl">Chat History</h2>
              <p className="text-gray-400 text-sm">Select a previous conversation to continue</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-amber-400/10 transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-400">Loading chat history...</div>
            </div>
          ) : chatSessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <MessageSquare className="w-12 h-12 text-gray-500 mb-4" />
              <h3 className="text-gray-300 font-medium mb-2">No chat history</h3>
              <p className="text-gray-500 text-sm">
                Start a conversation and it will appear here for the next 90 days
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {chatSessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => handleSelectChat(session)}
                  className="flex items-center gap-4 p-4 bg-gray-800/50 hover:bg-gray-800 border border-gray-700 hover:border-amber-400/30 rounded-lg cursor-pointer transition-all group"
                >
                  {/* Chat Icon */}
                  <div className="w-10 h-10 bg-amber-400/10 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-amber-400/20 transition-colors">
                    <MessageSquare className="w-5 h-5 text-amber-400" />
                  </div>

                  {/* Chat Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-gray-100 font-medium text-sm group-hover:text-amber-400 transition-colors">
                        {formatChatTitle(session)}
                      </h3>
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        {formatLastModified(session.lastModified)}
                      </div>
                    </div>
                    <p className="text-gray-400 text-xs truncate">
                      {getMessagePreview(session)}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      <span>{session.messages.length} messages</span>
                      {session.projectFiles.length > 0 && (
                        <span>{session.projectFiles.length} files</span>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => handleDeleteChat(session.id, e)}
                      className={`p-2 rounded-lg transition-colors ${
                        deletingId === session.id
                          ? 'bg-red-500 hover:bg-red-600 text-white'
                          : 'hover:bg-red-500/10 text-gray-400 hover:text-red-400'
                      }`}
                      title={deletingId === session.id ? 'Click again to confirm' : 'Delete chat'}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {chatSessions.length > 0 && (
          <div className="flex items-center justify-between p-6 border-t border-amber-400/20">
            <div className="text-gray-400 text-sm">
              {chatSessions.length} conversation{chatSessions.length !== 1 ? 's' : ''} found
            </div>
            <div className="text-gray-500 text-xs">
              Chat history is automatically cleaned after 90 days
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatHistoryModal; 