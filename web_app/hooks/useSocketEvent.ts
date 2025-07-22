import { useEffect } from 'react';
import websocketService, { WebSocketEvents } from '../services/websocket';

export function useSocketEvent<T extends keyof WebSocketEvents>(
  event: T,
  handler: WebSocketEvents[T]
) {
  useEffect(() => {
    websocketService.on(event, handler);
    
    return () => {
      websocketService.off(event, handler);
    };
  }, [event, handler]);
}