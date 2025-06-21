import type { Agent } from '../components/AgentHierarchy';
import type { ChatMessage } from '../components/ChatInterface';

export interface AgentUpdate {
  agentId: string;
  status: Agent['status'];
  task?: string;
}

export interface CodeStreamUpdate {
  agentId: string;
  content: string;
  isComplete: boolean;
}

export interface DelegationUpdate {
  parentId: string;
  childId: string;
  task: string;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectInterval: number = 5000;
  private reconnectTimer: number | null = null;
  
  // Event handlers
  public onAgentUpdate?: (update: AgentUpdate) => void;
  public onCodeStream?: (update: CodeStreamUpdate) => void;
  public onDelegation?: (update: DelegationUpdate) => void;
  public onMessage?: (message: ChatMessage) => void;
  public onConnectionChange?: (connected: boolean) => void;
  
  private url: string;

  constructor(url: string = 'ws://localhost:8080/ws') {
    this.url = url;
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.onConnectionChange?.(true);
        if (this.reconnectTimer) {
          window.clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.onConnectionChange?.(false);
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (!this.reconnectTimer) {
      this.reconnectTimer = window.setTimeout(() => {
        console.log('Attempting to reconnect...');
        this.connect();
      }, this.reconnectInterval);
    }
  }

  private handleMessage(data: { type: string; payload: unknown }) {
    switch (data.type) {
      case 'agent_update':
        this.onAgentUpdate?.(data.payload as AgentUpdate);
        break;
      
      case 'code_stream':
        this.onCodeStream?.(data.payload as CodeStreamUpdate);
        break;
      
      case 'delegation':
        this.onDelegation?.(data.payload as DelegationUpdate);
        break;
      
      case 'message':
        this.onMessage?.(data.payload as ChatMessage);
        break;
      
      default:
        console.warn('Unknown message type:', data.type);
    }
  }

  sendPrompt(agentId: string, prompt: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'prompt',
        payload: {
          agentId,
          prompt
        }
      }));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default WebSocketService; 