import { io, Socket } from 'socket.io-client';

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai' | 'system';
  timestamp: string;
  agentId?: string;
  metadata?: {
    filePath?: string;
    codeBlock?: boolean;
    syntax?: string;
  };
}

export interface CodeStream {
  agentId: string;
  filePath: string;
  content: string;
  isComplete: boolean;
  syntax?: string;
}

export interface AgentUpdate {
  agentId: string;
  status: 'active' | 'inactive' | 'waiting' | 'completed' | 'error';
  task?: string;
  progress?: number;
  parentId?: string;
}

export interface FileTreeUpdate {
  action: 'create' | 'update' | 'delete';
  filePath: string;
  fileType: 'file' | 'folder';
  content?: string;
}

export interface ProjectStatus {
  projectId: string;
  projectPath: string;
  status: 'initializing' | 'active' | 'completed' | 'error';
}

export interface WebSocketEvents {
  message: (message: ChatMessage) => void;
  code_stream: (stream: CodeStream) => void;
  agent_update: (update: AgentUpdate) => void;
  file_tree_update: (update: FileTreeUpdate) => void;
  project_status: (status: ProjectStatus) => void;
  error: (error: string) => void;
  connected: () => void;
  disconnected: () => void;
}

class WebSocketService {
  private socket: Socket | null = null;
  private eventListeners: Partial<WebSocketEvents> = {};
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageQueue: any[] = [];
  private isConnecting = false;

  connect(serverUrl: string = 'ws://localhost:8080') {
    if (this.socket?.connected || this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    try {
      // Convert WebSocket URL to Socket.IO URL
      const socketUrl = serverUrl.replace('ws://', 'http://').replace('wss://', 'https://');
      
      this.socket = io(socketUrl, {
        transports: ['websocket'],
        path: '/ws',
        timeout: 20000,
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay,
      });

      this.setupEventListeners();
    } catch (error) {
      console.error('Failed to connect to WebSocket server:', error);
      this.emit('error', 'Failed to connect to server');
      this.isConnecting = false;
    }
  }

  private setupEventListeners() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('Connected to WebSocket server');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.emit('connected');
      
      // Send any queued messages
      this.processMessageQueue();
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
      this.emit('disconnected');
    });

    // Handle different message types from the server
    this.socket.on('message', (data: any) => {
      try {
        const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
        
        switch (parsedData.type) {
          case 'message':
            this.emit('message', parsedData.payload);
            break;
          case 'code_stream':
            this.emit('code_stream', parsedData.payload);
            break;
          case 'agent_update':
            this.emit('agent_update', parsedData.payload);
            break;
          case 'file_tree_update':
            this.emit('file_tree_update', parsedData.payload);
            break;
          case 'project_status':
            this.emit('project_status', parsedData.payload);
            break;
          default:
            console.warn('Unknown message type:', parsedData.type);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    });

    this.socket.on('error', (error: any) => {
      console.error('WebSocket error:', error);
      this.emit('error', error.message || 'WebSocket error occurred');
    });

    this.socket.on('connect_error', (error: any) => {
      console.error('Connection error:', error);
      this.isConnecting = false;
      this.reconnectAttempts++;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.emit('error', 'Failed to connect after multiple attempts');
      }
    });
  }

  private processMessageQueue() {
    while (this.messageQueue.length > 0 && this.socket?.connected) {
      const message = this.messageQueue.shift();
      this.socket.send(message);
    }
  }

  sendPrompt(prompt: string, agentId: string = 'root') {
    const message = JSON.stringify({
      type: 'prompt',
      payload: {
        prompt,
        agentId
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    } else {
      // Queue the message if not connected
      this.messageQueue.push(message);
      this.emit('error', 'Not connected to server. Message queued.');
    }
  }

  stopAgentThinking() {
    const message = JSON.stringify({
      type: 'stop',
      payload: {}
    });

    if (this.socket?.connected) {
      this.socket.send(message);
      console.log('Sent stop command to server');
    }
  }

  importProject(files: any[]) {
    const message = JSON.stringify({
      type: 'import_project',
      payload: {
        files
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    } else {
      this.messageQueue.push(message);
      this.emit('error', 'Not connected to server. Message queued.');
    }
  }

  selectFile(filePath: string) {
    const message = JSON.stringify({
      type: 'file_select',
      payload: {
        filePath
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  editCode(filePath: string, content: string) {
    const message = JSON.stringify({
      type: 'code_edit',
      payload: {
        filePath,
        content
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  on<T extends keyof WebSocketEvents>(event: T, callback: WebSocketEvents[T]) {
    this.eventListeners[event] = callback;
  }

  off<T extends keyof WebSocketEvents>(event: T) {
    delete this.eventListeners[event];
  }

  private emit<T extends keyof WebSocketEvents>(event: T, ...args: any[]) {
    const callback = this.eventListeners[event];
    if (callback) {
      (callback as any)(...args);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.messageQueue = [];
    this.isConnecting = false;
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  getConnectionStatus(): 'connected' | 'connecting' | 'disconnected' {
    if (this.socket?.connected) return 'connected';
    if (this.isConnecting) return 'connecting';
    return 'disconnected';
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();
export default websocketService;