import React from 'react';
import { renderHook } from '@testing-library/react';
import { useSocketEvent } from '@/hooks/useSocketEvent';
import websocketService from '@/services/websocket';

// Mock the websocket service
jest.mock('@/services/websocket', () => ({
  default: {
    on: jest.fn(),
    off: jest.fn(),
  },
}));

describe('useSocketEvent Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should register event listener on mount', () => {
    const eventHandler = jest.fn();
    
    renderHook(() => useSocketEvent('message', eventHandler));

    expect(websocketService.on).toHaveBeenCalledWith('message', eventHandler);
    expect(websocketService.on).toHaveBeenCalledTimes(1);
  });

  it('should unregister event listener on unmount', () => {
    const eventHandler = jest.fn();
    
    const { unmount } = renderHook(() => useSocketEvent('message', eventHandler));
    
    expect(websocketService.on).toHaveBeenCalledWith('message', eventHandler);
    
    unmount();
    
    expect(websocketService.off).toHaveBeenCalledWith('message', eventHandler);
    expect(websocketService.off).toHaveBeenCalledTimes(1);
  });

  it('should handle multiple event types', () => {
    const messageHandler = jest.fn();
    const agentHandler = jest.fn();
    
    renderHook(() => {
      useSocketEvent('message', messageHandler);
      useSocketEvent('agent_update', agentHandler);
    });

    expect(websocketService.on).toHaveBeenCalledWith('message', messageHandler);
    expect(websocketService.on).toHaveBeenCalledWith('agent_update', agentHandler);
    expect(websocketService.on).toHaveBeenCalledTimes(2);
  });

  it('should update handler when it changes', () => {
    const handler1 = jest.fn();
    const handler2 = jest.fn();
    
    const { rerender } = renderHook(
      ({ handler }) => useSocketEvent('message', handler),
      { initialProps: { handler: handler1 } }
    );

    expect(websocketService.on).toHaveBeenCalledWith('message', handler1);
    expect(websocketService.on).toHaveBeenCalledTimes(1);

    // Change handler
    rerender({ handler: handler2 });

    expect(websocketService.off).toHaveBeenCalledWith('message', handler1);
    expect(websocketService.on).toHaveBeenCalledWith('message', handler2);
  });

  it('should not re-register if event and handler remain the same', () => {
    const eventHandler = jest.fn();
    
    const { rerender } = renderHook(() => useSocketEvent('message', eventHandler));

    expect(websocketService.on).toHaveBeenCalledTimes(1);

    // Re-render with same props
    rerender();

    // Should not register again
    expect(websocketService.on).toHaveBeenCalledTimes(1);
    expect(websocketService.off).not.toHaveBeenCalled();
  });

  it('should handle event type changes', () => {
    const eventHandler = jest.fn();
    
    const { rerender } = renderHook(
      ({ event }) => useSocketEvent(event as any, eventHandler),
      { initialProps: { event: 'message' } }
    );

    expect(websocketService.on).toHaveBeenCalledWith('message', eventHandler);

    // Change event type
    rerender({ event: 'agent_update' });

    expect(websocketService.off).toHaveBeenCalledWith('message', eventHandler);
    expect(websocketService.on).toHaveBeenCalledWith('agent_update', eventHandler);
  });

  it('should handle all WebSocket event types', () => {
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
      'wave_progress',
    ];

    events.forEach(event => {
      const handler = jest.fn();
      const { unmount } = renderHook(() => useSocketEvent(event as any, handler));
      
      expect(websocketService.on).toHaveBeenCalledWith(event, handler);
      
      unmount();
      
      expect(websocketService.off).toHaveBeenCalledWith(event, handler);
    });
  });

  it('should handle rapid event changes without memory leaks', () => {
    const handler = jest.fn();
    const events = ['message', 'agent_update', 'file_tree_update'] as const;
    let currentEventIndex = 0;

    const { rerender } = renderHook(
      ({ eventIndex }) => useSocketEvent(events[eventIndex], handler),
      { initialProps: { eventIndex: 0 } }
    );

    // Rapidly change events
    for (let i = 1; i < events.length; i++) {
      rerender({ eventIndex: i });
      
      // Verify cleanup of previous event
      expect(websocketService.off).toHaveBeenCalledWith(events[i - 1], handler);
      // Verify registration of new event
      expect(websocketService.on).toHaveBeenCalledWith(events[i], handler);
    }

    // All off calls should match on calls (except the last one which happens on unmount)
    expect(websocketService.off).toHaveBeenCalledTimes(events.length - 1);
    expect(websocketService.on).toHaveBeenCalledTimes(events.length);
  });
});