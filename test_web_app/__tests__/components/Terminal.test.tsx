import React from 'react';
import { describe, it, expect, beforeEach, vi } from '@jest/globals';
import { render, screen, waitFor } from '../../setup/testUtils';
import { Terminal } from '@/components/Terminal';
import { useSocketEvent } from '@/hooks/useSocketEvent';
import websocketService from '@/services/websocket';

// Mock dependencies
jest.mock('@/hooks/useSocketEvent');
jest.mock('@/services/websocket');

describe('Terminal Component', () => {
  const mockUseSocketEvent = useSocketEvent as jest.MockedFunction<typeof useSocketEvent>;
  const mockWebSocketService = websocketService as jest.Mocked<typeof websocketService>;
  let mockTerminal: any;
  let mockFitAddon: any;

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseSocketEvent.mockImplementation(() => {});
    
    // Create mock instances
    mockTerminal = {
      open: jest.fn(),
      write: jest.fn(),
      writeln: jest.fn(),
      clear: jest.fn(),
      dispose: jest.fn(),
      onData: jest.fn(),
      onKey: jest.fn(),
      onResize: jest.fn(),
      resize: jest.fn(),
      focus: jest.fn(),
      blur: jest.fn(),
      loadAddon: jest.fn(),
      options: {},
    };
    
    mockFitAddon = {
      fit: jest.fn(),
      dispose: jest.fn(),
      activate: jest.fn(),
    };
    
    // Mock Terminal constructor
    const { Terminal: XTerm } = require('@xterm/xterm');
    XTerm.mockImplementation(() => mockTerminal);
    
    // Mock FitAddon constructor
    const { FitAddon } = require('@xterm/addon-fit');
    FitAddon.mockImplementation(() => mockFitAddon);
  });

  describe('Rendering', () => {
    it('should render terminal container', () => {
      const { container } = render(<Terminal />);
      
      const terminalElement = container.querySelector('[style*="backgroundColor"]');
      expect(terminalElement).toBeInTheDocument();
    });

    it('should show terminal header', () => {
      render(<Terminal />);
      
      expect(screen.getByText('Terminal')).toBeInTheDocument();
    });

    it('should initialize xterm on mount', () => {
      render(<Terminal />);
      
      const { Terminal: XTerm } = require('@xterm/xterm');
      expect(XTerm).toHaveBeenCalledWith(expect.objectContaining({
        theme: expect.objectContaining({
          background: expect.any(String),
          foreground: expect.any(String),
        }),
        fontSize: 13,
        fontFamily: expect.stringContaining('JetBrains Mono'),
      }));
    });
  });

  describe('WebSocket Integration', () => {
    it('should register terminal event listeners', () => {
      render(<Terminal />);
      
      expect(mockUseSocketEvent).toHaveBeenCalledWith('terminal_session', expect.any(Function));
      expect(mockUseSocketEvent).toHaveBeenCalledWith('terminal_data', expect.any(Function));
    });

    it('should create terminal session on mount', () => {
      render(<Terminal />);
      
      expect(mockWebSocketService.createTerminalSession).toHaveBeenCalledWith('default');
    });

    it('should create terminal session with custom project ID', () => {
      render(<Terminal projectId="custom-project" />);
      
      expect(mockWebSocketService.createTerminalSession).toHaveBeenCalledWith('custom-project');
    });

    it('should handle terminal session updates', () => {
      let sessionHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'terminal_session') {
          sessionHandler = handler;
        }
      });

      render(<Terminal />);
      
      sessionHandler({ 
        sessionId: 'test-session', 
        status: 'connected',
        shell: '/bin/bash',
        cwd: '/home/user' 
      });
      
      expect(screen.getByText('connected')).toBeInTheDocument();
    });

    it('should handle terminal data', () => {
      let dataHandler: any;
      let sessionHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'terminal_data') {
          dataHandler = handler;
        } else if (event === 'terminal_session') {
          sessionHandler = handler;
        }
      });

      render(<Terminal />);
      
      // Set session first
      sessionHandler({ sessionId: 'test-session', status: 'connected' });
      
      // Send data
      dataHandler({ sessionId: 'test-session', data: 'Hello Terminal' });
      
      expect(mockTerminal.write).toHaveBeenCalledWith('Hello Terminal');
    });

    it('should send terminal input', () => {
      let onDataCallback: any;
      mockTerminal.onData.mockImplementation((callback: any) => {
        onDataCallback = callback;
      });
      
      let sessionHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'terminal_session') {
          sessionHandler = handler;
        }
      });

      render(<Terminal />);
      sessionHandler({ sessionId: 'test-session', status: 'connected' });
      
      // Type in terminal
      onDataCallback('ls -la');
      
      expect(mockWebSocketService.sendTerminalData).toHaveBeenCalledWith('test-session', 'ls -la');
    });
  });

  describe('Terminal Status', () => {
    it('should show initializing state', () => {
      render(<Terminal />);
      
      expect(screen.getByText('Initializing...')).toBeInTheDocument();
    });

    it('should show connected status', () => {
      let sessionHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'terminal_session') {
          sessionHandler = handler;
        }
      });

      render(<Terminal />);
      sessionHandler({ sessionId: 'test-session', status: 'connected' });
      
      expect(screen.getByText('connected')).toBeInTheDocument();
    });

    it('should show error status', () => {
      let sessionHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'terminal_session') {
          sessionHandler = handler;
        }
      });

      render(<Terminal />);
      sessionHandler({ 
        sessionId: 'test-session', 
        status: 'error',
        error: 'Connection failed' 
      });
      
      expect(screen.getByText('error')).toBeInTheDocument();
      expect(mockTerminal.writeln).toHaveBeenCalledWith(expect.stringContaining('Error: Connection failed'));
    });
  });

  describe('Terminal Resize', () => {
    it('should handle terminal resize', () => {
      let resizeCallback: any;
      mockTerminal.onResize.mockImplementation((callback: any) => {
        resizeCallback = callback;
      });
      
      let sessionHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'terminal_session') {
          sessionHandler = handler;
        }
      });

      render(<Terminal />);
      sessionHandler({ sessionId: 'test-session', status: 'connected' });
      
      resizeCallback({ cols: 80, rows: 24 });
      
      expect(mockWebSocketService.resizeTerminal).toHaveBeenCalledWith('test-session', 80, 24);
    });

    it('should fit terminal on window resize', () => {
      render(<Terminal />);
      
      // Trigger window resize
      global.dispatchEvent(new Event('resize'));
      
      // Wait for debounced resize
      setTimeout(() => {
        expect(mockFitAddon.fit).toHaveBeenCalled();
      }, 150);
    });
  });

  describe('Cleanup', () => {
    it('should dispose terminal on unmount', () => {
      const { unmount } = render(<Terminal />);
      
      unmount();
      
      expect(mockTerminal.dispose).toHaveBeenCalled();
      expect(mockFitAddon.dispose).toHaveBeenCalled();
    });

    it('should close terminal session on unmount', () => {
      let sessionHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'terminal_session') {
          sessionHandler = handler;
        }
      });

      const { unmount } = render(<Terminal />);
      sessionHandler({ sessionId: 'test-session', status: 'connected' });
      
      unmount();
      
      expect(mockWebSocketService.closeTerminal).toHaveBeenCalledWith('test-session');
    });

    it('should remove resize listener on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');
      
      const { unmount } = render(<Terminal />);
      unmount();
      
      expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));
    });
  });

  describe('Error Handling', () => {
    it('should handle terminal creation errors', () => {
      mockWebSocketService.createTerminalSession.mockImplementation(() => {
        throw new Error('Failed to create session');
      });
      
      expect(() => render(<Terminal />)).not.toThrow();
    });

    it('should handle write errors gracefully', () => {
      mockTerminal.write.mockImplementation(() => {
        throw new Error('Write failed');
      });
      
      let dataHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'terminal_data') {
          dataHandler = handler;
        }
      });

      render(<Terminal />);
      
      expect(() => dataHandler({ sessionId: 'test', data: 'test' })).not.toThrow();
    });
  });

  describe('Session Info Display', () => {
    it('should display shell info when available', () => {
      let sessionHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'terminal_session') {
          sessionHandler = handler;
        }
      });

      render(<Terminal />);
      sessionHandler({ 
        sessionId: 'test-session', 
        status: 'connected',
        shell: '/bin/bash',
        cwd: '/home/user'
      });
      
      expect(screen.getByText('/bin/bash')).toBeInTheDocument();
      expect(screen.getByText('/home/user')).toBeInTheDocument();
    });
  });
});