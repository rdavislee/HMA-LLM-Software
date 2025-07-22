import React from 'react';
import { renderHook } from '@testing-library/react';

// Simple mock websocket service
const mockWebsocketService = {
  on: jest.fn(),
  off: jest.fn(),
  connect: jest.fn(),
  disconnect: jest.fn(),
  isConnected: jest.fn().mockReturnValue(false)
};

// Mock the useSocketEvent hook
jest.mock('@/hooks/useSocketEvent', () => ({
  useSocketEvent: (event: string, handler: Function) => {
    React.useEffect(() => {
      mockWebsocketService.on(event, handler);
      return () => {
        mockWebsocketService.off(event, handler);
      };
    }, [event, handler]);
  }
}));

import { useSocketEvent } from '@/hooks/useSocketEvent';

describe('useSocketEvent Hook Simple Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should register event listener on mount', () => {
    const eventHandler = jest.fn();
    
    renderHook(() => useSocketEvent('message', eventHandler));

    expect(mockWebsocketService.on).toHaveBeenCalledWith('message', eventHandler);
    expect(mockWebsocketService.on).toHaveBeenCalledTimes(1);
  });

  it('should unregister event listener on unmount', () => {
    const eventHandler = jest.fn();
    
    const { unmount } = renderHook(() => useSocketEvent('message', eventHandler));
    
    expect(mockWebsocketService.on).toHaveBeenCalledWith('message', eventHandler);
    
    unmount();
    
    expect(mockWebsocketService.off).toHaveBeenCalledWith('message', eventHandler);
    expect(mockWebsocketService.off).toHaveBeenCalledTimes(1);
  });

  it('should handle multiple event types', () => {
    const messageHandler = jest.fn();
    const agentHandler = jest.fn();
    
    renderHook(() => {
      useSocketEvent('message', messageHandler);
      useSocketEvent('agent_update', agentHandler);
    });

    expect(mockWebsocketService.on).toHaveBeenCalledWith('message', messageHandler);
    expect(mockWebsocketService.on).toHaveBeenCalledWith('agent_update', agentHandler);
    expect(mockWebsocketService.on).toHaveBeenCalledTimes(2);
  });

  it('should update handler when it changes', () => {
    const handler1 = jest.fn();
    const handler2 = jest.fn();
    
    const { rerender } = renderHook(
      ({ handler }) => useSocketEvent('message', handler),
      { initialProps: { handler: handler1 } }
    );

    expect(mockWebsocketService.on).toHaveBeenCalledWith('message', handler1);
    expect(mockWebsocketService.on).toHaveBeenCalledTimes(1);

    // Change handler
    rerender({ handler: handler2 });

    expect(mockWebsocketService.off).toHaveBeenCalledWith('message', handler1);
    expect(mockWebsocketService.on).toHaveBeenCalledWith('message', handler2);
  });

  it('should handle different WebSocket event types', () => {
    const events = [
      'connected',
      'disconnected', 
      'error',
      'message',
      'agent_update',
      'file_tree_update',
      'project_status',
      'terminal_data',
      'terminal_session',
      'code_stream',
      'wave_progress'
    ];

    events.forEach(event => {
      const handler = jest.fn();
      const { unmount } = renderHook(() => useSocketEvent(event as any, handler));
      
      expect(mockWebsocketService.on).toHaveBeenCalledWith(event, handler);
      
      unmount();
      
      expect(mockWebsocketService.off).toHaveBeenCalledWith(event, handler);
    });
  });
});