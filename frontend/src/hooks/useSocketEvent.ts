import { useEffect } from 'react';
import websocketService, { WebSocketEvents } from '../services/websocket';

/**
 * A custom hook to safely subscribe to WebSocket events.
 * It handles adding the listener on component mount and removing it on unmount.
 * 
 * @param event The name of the WebSocket event to listen to.
 * @param callback The function to execute when the event is received.
 */
export const useSocketEvent = <T extends keyof WebSocketEvents>(
  event: T,
  callback: WebSocketEvents[T]
) => {
  useEffect(() => {
    // Cast the callback to 'any' to avoid type mismatches with the generic signature.
    // This is safe because the hook's signature ensures the callback matches the event.
    const handler = callback as any;

    websocketService.on(event, handler);

    return () => {
      websocketService.off(event, handler);
    };
  }, [event, callback]);
}; 