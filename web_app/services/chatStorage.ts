import { ChatMessage } from './websocket';

export interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
  lastModified: Date;
  messages: ChatMessage[];
  projectPath?: string;
}

export interface ChatHistoryStorage {
  sessions: ChatSession[];
  currentSessionId?: string;
}

class ChatStorageService {
  private readonly STORAGE_KEY = 'colony-chat-history';
  private readonly MAX_AGE_DAYS = 90;

  private getStorage(): ChatHistoryStorage {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Convert date strings back to Date objects
        parsed.sessions = parsed.sessions.map((session: any) => ({
          ...session,
          createdAt: new Date(session.createdAt),
          lastModified: new Date(session.lastModified),
          messages: session.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        }));
        return parsed;
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
    return { sessions: [] };
  }

  private setStorage(data: ChatHistoryStorage): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('Error saving chat history:', error);
    }
  }

  private cleanOldSessions(sessions: ChatSession[]): ChatSession[] {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - this.MAX_AGE_DAYS);
    
    return sessions.filter(session => session.lastModified > cutoffDate);
  }

  saveChatSession(session: ChatSession): void {
    const storage = this.getStorage();
    const existingIndex = storage.sessions.findIndex(s => s.id === session.id);
    
    if (existingIndex >= 0) {
      storage.sessions[existingIndex] = session;
    } else {
      storage.sessions.push(session);
    }
    
    // Clean old sessions
    storage.sessions = this.cleanOldSessions(storage.sessions);
    
    // Sort by last modified (newest first)
    storage.sessions.sort((a, b) => b.lastModified.getTime() - a.lastModified.getTime());
    
    this.setStorage(storage);
  }

  loadChatSessions(): ChatSession[] {
    const storage = this.getStorage();
    const cleanedSessions = this.cleanOldSessions(storage.sessions);
    
    // If we cleaned any sessions, update storage
    if (cleanedSessions.length !== storage.sessions.length) {
      storage.sessions = cleanedSessions;
      this.setStorage(storage);
    }
    
    return cleanedSessions.sort((a, b) => b.lastModified.getTime() - a.lastModified.getTime());
  }

  deleteChatSession(sessionId: string): void {
    const storage = this.getStorage();
    storage.sessions = storage.sessions.filter(s => s.id !== sessionId);
    
    if (storage.currentSessionId === sessionId) {
      storage.currentSessionId = undefined;
    }
    
    this.setStorage(storage);
  }

  getCurrentSession(): ChatSession | null {
    const storage = this.getStorage();
    if (storage.currentSessionId) {
      const session = storage.sessions.find(s => s.id === storage.currentSessionId);
      return session || null;
    }
    return null;
  }

  setCurrentSession(sessionId: string): void {
    const storage = this.getStorage();
    storage.currentSessionId = sessionId;
    this.setStorage(storage);
  }

  clearCurrentSession(): void {
    const storage = this.getStorage();
    storage.currentSessionId = undefined;
    this.setStorage(storage);
  }

  createNewSession(title?: string): ChatSession {
    const session: ChatSession = {
      id: `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      title: title || `Chat ${new Date().toLocaleString()}`,
      createdAt: new Date(),
      lastModified: new Date(),
      messages: []
    };
    
    this.saveChatSession(session);
    this.setCurrentSession(session.id);
    
    return session;
  }
}

// Create singleton instance
export const chatStorage = new ChatStorageService();
export default chatStorage;