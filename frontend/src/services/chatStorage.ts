import { ChatSession, ChatHistoryStorage, StorageProvider } from '../types';

// Local storage implementation
class LocalChatStorage implements StorageProvider {
  private readonly STORAGE_KEY = 'hive-chat-history';
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

  async saveChatSession(session: ChatSession): Promise<void> {
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

  async loadChatSessions(): Promise<ChatSession[]> {
    const storage = this.getStorage();
    const cleanedSessions = this.cleanOldSessions(storage.sessions);
    
    // If we cleaned any sessions, update storage
    if (cleanedSessions.length !== storage.sessions.length) {
      storage.sessions = cleanedSessions;
      this.setStorage(storage);
    }
    
    return cleanedSessions.sort((a, b) => b.lastModified.getTime() - a.lastModified.getTime());
  }

  async deleteChatSession(sessionId: string): Promise<void> {
    const storage = this.getStorage();
    storage.sessions = storage.sessions.filter(s => s.id !== sessionId);
    
    if (storage.currentSessionId === sessionId) {
      storage.currentSessionId = undefined;
    }
    
    this.setStorage(storage);
  }

  async getCurrentSession(): Promise<ChatSession | null> {
    const storage = this.getStorage();
    if (storage.currentSessionId) {
      const session = storage.sessions.find(s => s.id === storage.currentSessionId);
      return session || null;
    }
    return null;
  }

  async setCurrentSession(sessionId: string): Promise<void> {
    const storage = this.getStorage();
    storage.currentSessionId = sessionId;
    this.setStorage(storage);
  }

  async clearCurrentSession(): Promise<void> {
    const storage = this.getStorage();
    storage.currentSessionId = undefined;
    this.setStorage(storage);
  }
}

// Web storage implementation (placeholder for future)
class WebChatStorage implements StorageProvider {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async saveChatSession(session: ChatSession): Promise<void> {
    // TODO: Implement web API calls
    throw new Error('Web storage not implemented yet');
  }

  async loadChatSessions(): Promise<ChatSession[]> {
    // TODO: Implement web API calls
    throw new Error('Web storage not implemented yet');
  }

  async deleteChatSession(sessionId: string): Promise<void> {
    // TODO: Implement web API calls
    throw new Error('Web storage not implemented yet');
  }

  async getCurrentSession(): Promise<ChatSession | null> {
    // TODO: Implement web API calls
    throw new Error('Web storage not implemented yet');
  }

  async setCurrentSession(sessionId: string): Promise<void> {
    // TODO: Implement web API calls
    throw new Error('Web storage not implemented yet');
  }
}

// Factory function to create storage provider
export function createChatStorage(useWebStorage = false, baseUrl?: string): StorageProvider {
  if (useWebStorage && baseUrl) {
    return new WebChatStorage(baseUrl);
  }
  return new LocalChatStorage();
}

// Default export for easy use
export const chatStorage = createChatStorage(); 