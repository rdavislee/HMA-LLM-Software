
import chatStorage from '@/services/chatStorage';
import type { ChatSession, ChatMessage } from '@/services/websocket';

describe('ChatStorage Service', () => {
  // Mock localStorage
  const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
  };

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
    
    // Replace global localStorage with mock
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Session Management', () => {
    it('should create a new session', () => {
      localStorageMock.getItem.mockReturnValue(null);
      const session = chatStorage.createNewSession();
      
      expect(session).toMatchObject({
        id: expect.any(String),
        title: expect.any(String),
        messages: [],
        createdAt: expect.any(Date),
        lastModified: expect.any(Date),
      });
      
      expect(session.id).toMatch(/^session-/);
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'colony-chat-history',
        expect.stringContaining(session.id)
      );
    });

    it('should create a new session with custom title', () => {
      localStorageMock.getItem.mockReturnValue(null);
      const title = 'My Custom Chat';
      const session = chatStorage.createNewSession(title);
      
      expect(session.title).toBe(title);
    });

    it('should save a chat session', () => {
      localStorageMock.getItem.mockReturnValue(JSON.stringify({ sessions: [] }));
      
      const session: ChatSession = {
        id: 'test-session-1',
        title: 'Test Session',
        messages: [
          {
            id: 'msg-1',
            content: 'Hello',
            sender: 'user' as const,
            timestamp: new Date().toISOString(),
          },
        ],
        createdAt: new Date(),
        lastModified: new Date(),
      };

      chatStorage.saveChatSession(session);

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'colony-chat-history',
        expect.stringContaining('test-session-1')
      );
    });

    it('should load chat sessions', () => {
      const mockData = {
        sessions: [
          {
            id: 'test-session-1',
            title: 'Test Session',
            messages: [
              {
                id: 'msg-1',
                content: 'Hello',
                sender: 'user',
                timestamp: new Date().toISOString(),
              },
            ],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          },
        ],
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));

      const sessions = chatStorage.loadChatSessions();

      expect(localStorageMock.getItem).toHaveBeenCalledWith('colony-chat-history');
      expect(sessions).toHaveLength(1);
      expect(sessions[0]).toMatchObject({
        id: 'test-session-1',
        title: 'Test Session',
        messages: expect.any(Array),
        createdAt: expect.any(Date),
        lastModified: expect.any(Date),
      });
    });

    it('should return empty array when no sessions exist', () => {
      localStorageMock.getItem.mockReturnValue(null);

      const sessions = chatStorage.loadChatSessions();

      expect(sessions).toEqual([]);
    });

    it('should handle invalid JSON in storage', () => {
      localStorageMock.getItem.mockReturnValue('invalid json');

      const sessions = chatStorage.loadChatSessions();

      expect(sessions).toEqual([]);
    });
  });

  describe('Multiple Sessions', () => {
    it('should handle multiple chat sessions', () => {
      const mockData = {
        sessions: [
          {
            id: 'session-1',
            title: 'Session 1',
            messages: [],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          },
          {
            id: 'session-2',
            title: 'Session 2',
            messages: [],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          },
        ],
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));

      const allSessions = chatStorage.loadChatSessions();

      expect(allSessions).toHaveLength(2);
      expect(allSessions[0].id).toBe('session-1');
      expect(allSessions[1].id).toBe('session-2');
    });

    it('should sort sessions by last modified date', () => {
      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      
      const mockData = {
        sessions: [
          {
            id: 'session-old',
            title: 'Old Session',
            messages: [],
            createdAt: yesterday.toISOString(),
            lastModified: yesterday.toISOString(),
          },
          {
            id: 'session-new',
            title: 'New Session',
            messages: [],
            createdAt: now.toISOString(),
            lastModified: now.toISOString(),
          },
        ],
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));

      const allSessions = chatStorage.loadChatSessions();

      expect(allSessions[0].id).toBe('session-new');
      expect(allSessions[1].id).toBe('session-old');
    });
  });

  describe('Session Deletion', () => {
    it('should delete a specific session', () => {
      const mockData = {
        sessions: [
          {
            id: 'test-session-1',
            title: 'Test Session',
            messages: [],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          },
          {
            id: 'test-session-2',
            title: 'Another Session',
            messages: [],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          },
        ],
        currentSessionId: 'test-session-1',
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));
      
      chatStorage.deleteChatSession('test-session-1');

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'colony-chat-history',
        expect.not.stringContaining('test-session-1')
      );
    });

    it('should clean old sessions', () => {
      const now = new Date();
      const tooOld = new Date(now.getTime() - 91 * 24 * 60 * 60 * 1000); // 91 days old
      const recent = new Date(now.getTime() - 10 * 24 * 60 * 60 * 1000); // 10 days old
      
      const mockData = {
        sessions: [
          {
            id: 'old-session',
            title: 'Old Session',
            messages: [],
            createdAt: tooOld.toISOString(),
            lastModified: tooOld.toISOString(),
          },
          {
            id: 'recent-session',
            title: 'Recent Session',
            messages: [],
            createdAt: recent.toISOString(),
            lastModified: recent.toISOString(),
          },
        ],
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));
      
      const sessions = chatStorage.loadChatSessions();

      expect(sessions).toHaveLength(1);
      expect(sessions[0].id).toBe('recent-session');
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'colony-chat-history',
        expect.not.stringContaining('old-session')
      );
    });
  });

  describe('Current Session Management', () => {
    it('should get the current session', () => {
      const mockData = {
        sessions: [
          {
            id: 'session-1',
            title: 'Session 1',
            messages: [],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          },
        ],
        currentSessionId: 'session-1',
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));

      const current = chatStorage.getCurrentSession();

      expect(current?.id).toBe('session-1');
    });

    it('should return null if no current session', () => {
      const mockData = {
        sessions: [
          {
            id: 'session-1',
            title: 'Session 1',
            messages: [],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          },
        ],
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));

      const current = chatStorage.getCurrentSession();

      expect(current).toBeNull();
    });

    it('should set current session', () => {
      const mockData = {
        sessions: [
          {
            id: 'session-1',
            title: 'Session 1',
            messages: [],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          },
        ],
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));
      
      chatStorage.setCurrentSession('session-1');

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'colony-chat-history',
        expect.stringContaining('"currentSessionId":"session-1"')
      );
    });

    it('should clear current session', () => {
      const mockData = {
        sessions: [],
        currentSessionId: 'session-1',
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));
      
      chatStorage.clearCurrentSession();

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'colony-chat-history',
        expect.not.stringContaining('currentSessionId')
      );
    });
  });

  describe('Message Management', () => {
    it('should update existing session', () => {
      const mockData = {
        sessions: [
          {
            id: 'test-session',
            title: 'Test Session',
            messages: [
              {
                id: 'msg-1',
                content: 'First message',
                sender: 'user' as const,
                timestamp: new Date().toISOString(),
              },
            ],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          },
        ],
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockData));

      const updatedSession: ChatSession = {
        id: 'test-session',
        title: 'Test Session',
        messages: [
          {
            id: 'msg-1',
            content: 'First message',
            sender: 'user' as const,
            timestamp: new Date().toISOString(),
          },
          {
            id: 'msg-2',
            content: 'Second message',
            sender: 'ai' as const,
            timestamp: new Date().toISOString(),
          },
        ],
        createdAt: new Date(),
        lastModified: new Date(),
      };
      
      chatStorage.saveChatSession(updatedSession);

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'colony-chat-history',
        expect.stringContaining('Second message')
      );
    });
  });

  describe('Error Handling', () => {
    it('should handle localStorage quota exceeded', () => {
      localStorageMock.getItem.mockReturnValue(null);
      localStorageMock.setItem.mockImplementation(() => {
        throw new Error('QuotaExceededError');
      });

      expect(() => chatStorage.createNewSession()).not.toThrow();
    });

    it('should handle corrupted session data', () => {
      localStorageMock.getItem.mockReturnValue('{"invalid": json structure');

      const sessions = chatStorage.loadChatSessions();

      expect(sessions).toEqual([]);
    });
  });
});