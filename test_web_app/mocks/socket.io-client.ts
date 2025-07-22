// Mock implementation of socket.io-client

export interface MockSocket {
  on: any;
  off: any;
  emit: any;
  send: any;
  connect: any;
  disconnect: any;
  connected: boolean;
  id: string;
  io: {
    opts: any;
  };
}

const createMockSocket = (): MockSocket => {
  const listeners: { [event: string]: Function[] } = {};

  const mockSocket: MockSocket = {
    on: jest.fn((event: string, handler: Function) => {
      if (!listeners[event]) {
        listeners[event] = [];
      }
      listeners[event].push(handler);
      return mockSocket;
    }),
    
    off: jest.fn((event: string, handler?: Function) => {
      if (!listeners[event]) return mockSocket;
      
      if (handler) {
        listeners[event] = listeners[event].filter(h => h !== handler);
      } else {
        delete listeners[event];
      }
      return mockSocket;
    }),
    
    emit: jest.fn((event: string, ...args: any[]) => {
      // Simulate server response for certain events
      setTimeout(() => {
        switch (event) {
          case 'connect':
            mockSocket.connected = true;
            if (listeners['connect']) {
              listeners['connect'].forEach(handler => handler());
            }
            break;
            
          case 'disconnect':
            mockSocket.connected = false;
            if (listeners['disconnect']) {
              listeners['disconnect'].forEach(handler => handler());
            }
            break;
            
          // Remove old event handling as we use send() method now
        }
      }, 10);
      
      return mockSocket;
    }),
    
    send: jest.fn((data: string) => {
      // Mock send behavior
      return mockSocket;
    }),
    
    connect: jest.fn(() => {
      mockSocket.connected = true;
      if (listeners['connect']) {
        listeners['connect'].forEach(handler => handler());
      }
      return mockSocket;
    }),
    
    disconnect: jest.fn(() => {
      mockSocket.connected = false;
      if (listeners['disconnect']) {
        listeners['disconnect'].forEach(handler => handler());
      }
      return mockSocket;
    }),
    
    connected: false,
    id: 'mock-socket-id',
    io: {
      opts: {},
    },
  };

  // Helper method to trigger events in tests
  (mockSocket as any).__trigger = (event: string, data: any) => {
    if (listeners[event]) {
      listeners[event].forEach(handler => handler(data));
    }
  };

  return mockSocket;
};

export const io = jest.fn(() => createMockSocket());

export type Socket = MockSocket;

export default io;