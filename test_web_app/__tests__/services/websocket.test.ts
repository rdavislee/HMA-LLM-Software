import websocketService from '@/services/websocket';
import { io } from 'socket.io-client';

// Mock socket.io-client
jest.mock('socket.io-client');

describe('WebSocketService', () => {
  let mockSocket: any;

  beforeEach(() => {
    // Reset the service state
    websocketService.disconnect();
    jest.clearAllMocks();
    
    // Create a new mock socket for each test
    mockSocket = {
      on: jest.fn().mockReturnThis(),
      off: jest.fn().mockReturnThis(),
      emit: jest.fn().mockReturnThis(),
      send: jest.fn().mockReturnThis(),
      connect: jest.fn().mockReturnThis(),
      disconnect: jest.fn().mockReturnThis(),
      connected: false,
      id: 'test-socket-id',
      __trigger: (event: string, data?: any) => {
        const handler = mockSocket.on.mock.calls.find((call: any[]) => call[0] === event)?.[1];
        if (handler) handler(data);
      }
    };
    
    (io as any).mockReturnValue(mockSocket);
  });

  afterEach(() => {
    websocketService.disconnect();
  });

  describe('Connection Management', () => {
    it('should connect to WebSocket server', () => {
      websocketService.connect();
      
      expect(io).toHaveBeenCalledWith('http://localhost:8080', {
        transports: ['websocket'],
        path: '/ws',
        timeout: 20000,
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
      });
      
      expect(mockSocket.on).toHaveBeenCalledWith('connect', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('disconnect', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('error', expect.any(Function));
    });

    it('should handle connection with custom URL', () => {
      websocketService.connect('ws://custom-server:3000');
      
      expect(io).toHaveBeenCalledWith('http://custom-server:3000', expect.any(Object));
    });

    it('should not create multiple connections', () => {
      websocketService.connect();
      websocketService.connect();
      
      expect(io).toHaveBeenCalledTimes(1);
    });

    it('should disconnect from server', () => {
      websocketService.connect();
      websocketService.disconnect();
      
      expect(mockSocket.disconnect).toHaveBeenCalled();
    });

    it('should report connection status', () => {
      expect(websocketService.isConnected()).toBe(false);
      
      websocketService.connect();
      mockSocket.connected = true;
      
      expect(websocketService.isConnected()).toBe(true);
    });
  });

  describe('Event Handling', () => {
    beforeEach(() => {
      websocketService.connect();
    });

    it('should handle connect event', () => {
      const connectHandler = jest.fn();
      websocketService.on('connected', connectHandler);
      
      mockSocket.__trigger('connect');
      
      expect(connectHandler).toHaveBeenCalled();
    });

    it('should handle disconnect event', () => {
      const disconnectHandler = jest.fn();
      websocketService.on('disconnected', disconnectHandler);
      
      mockSocket.__trigger('disconnect');
      
      expect(disconnectHandler).toHaveBeenCalled();
    });

    it('should handle error event', () => {
      const errorHandler = jest.fn();
      websocketService.on('error', errorHandler);
      
      const error = new Error('Connection failed');
      mockSocket.__trigger('error', error);
      
      expect(errorHandler).toHaveBeenCalledWith('Connection failed');
    });

    it('should handle message event', () => {
      const messageHandler = jest.fn();
      websocketService.on('message', messageHandler);
      
      const message = {
        id: '123',
        content: 'Test message',
        sender: 'ai' as const,
        timestamp: new Date().toISOString()
      };
      
      const data = {
        type: 'message',
        payload: message
      };
      
      mockSocket.__trigger('message', data);
      
      expect(messageHandler).toHaveBeenCalledWith(message);
    });

    it('should handle agent_update event', () => {
      const agentHandler = jest.fn();
      websocketService.on('agent_update', agentHandler);
      
      const update = {
        agentId: 'agent-1',
        status: 'active' as const,
        task: 'Processing',
        progress: 50
      };
      
      const data = {
        type: 'agent_update',
        payload: update
      };
      
      mockSocket.__trigger('message', data);
      
      expect(agentHandler).toHaveBeenCalledWith(update);
    });

    it('should remove event listeners', () => {
      const handler = jest.fn();
      websocketService.on('message', handler);
      websocketService.off('message', handler);
      
      mockSocket.__trigger('message', { content: 'test' });
      
      expect(handler).not.toHaveBeenCalled();
    });
  });

  describe('Message Sending', () => {
    beforeEach(() => {
      websocketService.connect();
      mockSocket.connected = true;
    });

    it('should send prompt message', () => {
      const prompt = 'Test prompt';
      const agentId = 'root';
      
      websocketService.sendPrompt(prompt, agentId);
      
      expect(mockSocket.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'prompt',
        payload: {
          prompt,
          agentId
        }
      }));
    });

    it('should handle terminal commands', () => {
      const sessionId = 'term-1';
      const projectId = 'project-1';
      
      // Create session
      websocketService.createTerminalSession(projectId);
      expect(mockSocket.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'terminal_create',
        payload: { projectId }
      }));
      
      // Send data
      websocketService.sendTerminalData(sessionId, 'ls -la');
      expect(mockSocket.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'terminal_data',
        payload: { sessionId, data: 'ls -la' }
      }));
      
      // Resize
      websocketService.resizeTerminal(sessionId, 80, 24);
      expect(mockSocket.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'terminal_resize',
        payload: { sessionId, cols: 80, rows: 24 }
      }));
      
      // Close session
      websocketService.closeTerminal(sessionId);
      expect(mockSocket.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'terminal_close',
        payload: { sessionId }
      }));
    });

    it('should handle file selection', () => {
      const filePath = '/src/test.ts';
      
      websocketService.selectFile(filePath);
      
      expect(mockSocket.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'file_select',
        payload: { filePath }
      }));
    });
  });

  describe('Terminal Session Events', () => {
    beforeEach(() => {
      websocketService.connect();
    });

    it('should handle terminal_session event', () => {
      const handler = jest.fn();
      websocketService.on('terminal_session', handler);
      
      const session = {
        sessionId: 'term-123',
        projectId: 'project-1',
        status: 'running' as const
      };
      
      const data = {
        type: 'terminal_session',
        payload: session
      };
      
      mockSocket.__trigger('message', data);
      
      expect(handler).toHaveBeenCalledWith(session);
    });

    it('should handle terminal_data event', () => {
      const handler = jest.fn();
      websocketService.on('terminal_data', handler);
      
      const terminalData = {
        sessionId: 'term-123',
        data: 'Hello from terminal'
      };
      
      const data = {
        type: 'terminal_data',
        payload: terminalData
      };
      
      mockSocket.__trigger('message', data);
      
      expect(handler).toHaveBeenCalledWith(terminalData);
    });
  });

  describe('File System Events', () => {
    beforeEach(() => {
      websocketService.connect();
    });

    it('should handle file_tree_update event', () => {
      const handler = jest.fn();
      websocketService.on('file_tree_update', handler);
      
      const update = {
        action: 'create' as const,
        filePath: '/src/test.ts',
        fileType: 'file' as const,
        content: 'test content'
      };
      
      const data = {
        type: 'file_tree_update',
        payload: update
      };
      
      mockSocket.__trigger('message', data);
      
      expect(handler).toHaveBeenCalledWith(update);
    });

    it('should handle code_stream event', () => {
      const handler = jest.fn();
      websocketService.on('code_stream', handler);
      
      const stream = {
        agentId: 'agent-1',
        filePath: '/src/test.ts',
        content: 'export const test = () => {};',
        isComplete: true,
        syntax: 'typescript'
      };
      
      const data = {
        type: 'code_stream',
        payload: stream
      };
      
      mockSocket.__trigger('message', data);
      
      expect(handler).toHaveBeenCalledWith(stream);
    });
  });

  describe('Error Handling', () => {
    it('should handle connection errors gracefully', () => {
      const errorHandler = jest.fn();
      websocketService.on('error', errorHandler);
      
      websocketService.connect();
      const error = new Error('Connection refused');
      mockSocket.__trigger('error', error);
      
      expect(errorHandler).toHaveBeenCalledWith('Connection refused');
    });

    it('should not throw when disconnecting without connection', () => {
      expect(() => websocketService.disconnect()).not.toThrow();
    });

    it('should queue messages when not connected', () => {
      mockSocket.connected = false;
      websocketService.sendPrompt('test');
      expect(mockSocket.send).not.toHaveBeenCalled();
    });
  });
});