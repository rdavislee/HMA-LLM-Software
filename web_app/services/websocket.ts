import { io, Socket } from 'socket.io-client';
import type { LLMConfig, AgentInfo, LLMStreamChunk } from './llm';

// WebSocket configuration
const getWebSocketUrl = (): string => {
  return (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8080';
};

// Message types
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
  status: 'active' | 'inactive' | 'waiting' | 'completed' | 'error' | 'delegating';
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

export interface TerminalData {
  sessionId: string;
  data: string;
}

export interface TerminalSession {
  sessionId: string;
  projectId: string;
  containerId?: string;
  status: 'starting' | 'running' | 'stopped' | 'error';
  error?: string;
}

// Wave progress updates
export interface WaveProgressUpdate {
  phase: 'spec' | 'test' | 'impl';
  progress: number; // 0-100
  message?: string;
}

// LLM-specific message types
export interface LLMConfigUpdate {
  config: LLMConfig;
}

export interface LLMStreamUpdate {
  agentId: string;
  chunk: LLMStreamChunk;
  messageId?: string;
}

export interface AgentHierarchyUpdate {
  agents: Record<string, AgentInfo>;
  rootAgentId: string;
}

export interface TokenUsageUpdate {
  agentId: string;
  tokensUsed: number;
  contextSize: number;
  maxContextSize: number;
}

// WebSocket event types
export interface WebSocketEvents {
  message: (message: ChatMessage) => void;
  code_stream: (stream: CodeStream) => void;
  agent_update: (update: AgentUpdate) => void;
  file_tree_update: (update: FileTreeUpdate) => void;
  project_status: (status: ProjectStatus) => void;
  error: (error: string) => void;
  connected: () => void;
  disconnected: () => void;
  terminal_data: (data: TerminalData) => void;
  terminal_session: (session: TerminalSession) => void;
  wave_progress: (update: WaveProgressUpdate) => void;
  // LLM-specific events
  llm_config_update: (update: LLMConfigUpdate) => void;
  llm_stream: (update: LLMStreamUpdate) => void;
  agent_hierarchy: (update: AgentHierarchyUpdate) => void;
  token_usage: (update: TokenUsageUpdate) => void;
}

type EventHandler<T = unknown> = (...args: T[]) => void;

interface QueuedMessage {
  event: string;
  data: unknown;
}

class WebSocketService {
  private socket: Socket | null = null;
  private eventListeners: Partial<Record<keyof WebSocketEvents, Array<EventHandler>>> = {};
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageQueue: QueuedMessage[] = [];
  private isConnecting = false;
  private terminalSessions: Map<string, TerminalSession> = new Map();

  connect(serverUrl?: string) {
    if (this.socket?.connected || this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    try {
      const wsUrl = serverUrl || getWebSocketUrl();
      const socketUrl = wsUrl.replace('ws://', 'http://').replace('wss://', 'https://');
      
      console.log(`Connecting to WebSocket server: ${socketUrl}`);
      
      this.socket = io(socketUrl, {
        transports: ['websocket'],
        path: '/ws',
        timeout: 20000,
        reconnection: true,
        reconnectionAttempts: 5,
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
      console.log('Connected to server');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.processMessageQueue();
      this.emit('connected');
    });

    this.socket.on('disconnect', (reason: string) => {
      console.log('Disconnected from server:', reason);
      this.emit('disconnected');
    });

    this.socket.on('connect_error', (error: Error) => {
      console.error('Connection error:', error);
      this.handleReconnect();
    });

    // Handle messages from server
    this.socket.on('message', (data: unknown) => {
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
          case 'terminal_data':
            this.emit('terminal_data', parsedData.payload);
            break;
          case 'terminal_session':
            this.handleTerminalSession(parsedData.payload);
            break;
          case 'wave_progress':
            this.emit('wave_progress', parsedData.payload);
            break;
          case 'llm_config_update':
            this.emit('llm_config_update', parsedData.payload);
            break;
          case 'llm_stream':
            this.emit('llm_stream', parsedData.payload);
            break;
          case 'agent_hierarchy':
            this.emit('agent_hierarchy', parsedData.payload);
            break;
          case 'token_usage':
            this.emit('token_usage', parsedData.payload);
            break;
          default:
            console.warn('Unknown message type:', parsedData.type);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    });

    this.socket.on('error', (error: Error) => {
      console.error('WebSocket error:', error);
      this.emit('error', error.message || 'WebSocket error occurred');
    });
  }

  private handleReconnect() {
    this.isConnecting = false;
    this.reconnectAttempts++;
    
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.emit('error', 'Failed to connect after multiple attempts');
      return;
    }

    setTimeout(() => {
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect();
    }, this.reconnectDelay * this.reconnectAttempts);
  }

  private processMessageQueue() {
    while (this.messageQueue.length > 0 && this.socket?.connected) {
      const message = this.messageQueue.shift();
      if (message) {
        this.socket.send(JSON.stringify(message));
      }
    }
  }

  private handleTerminalSession(session: TerminalSession) {
    this.terminalSessions.set(session.sessionId, session);
    this.emit('terminal_session', session);
  }

  // Public methods
  sendPrompt(prompt: string, agentId: string = 'root') {
    const messageData = {
      type: 'prompt',
      payload: {
        prompt,
        agentId
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'prompt', data: messageData });
      this.emit('error', 'Not connected to server. Message queued.');
    }
  }

  selectFile(filePath: string) {
    const messageData = {
      type: 'file_select',
      payload: { filePath }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  // Terminal methods
  createTerminalSession(projectId: string) {
    const messageData = {
      type: 'terminal_create',
      payload: { projectId }
    };
    
    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'terminal_create', data: messageData });
    }
  }

  sendTerminalData(sessionId: string, data: string) {
    const messageData = {
      type: 'terminal_data',
      payload: { sessionId, data }
    };
    
    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  resizeTerminal(sessionId: string, cols: number, rows: number) {
    const messageData = {
      type: 'terminal_resize',
      payload: { sessionId, cols, rows }
    };
    
    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  closeTerminal(sessionId: string) {
    const messageData = {
      type: 'terminal_close',
      payload: { sessionId }
    };
    
    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
    
    this.terminalSessions.delete(sessionId);
  }

  getTerminalSession(sessionId: string): TerminalSession | undefined {
    return this.terminalSessions.get(sessionId);
  }

  // LLM-specific methods
  configureLLM(config: LLMConfig) {
    try {
      const messageData = {
        type: 'llm_config',
        payload: config
      };

      if (this.socket?.connected) {
        this.socket.send(JSON.stringify(messageData));
      } else {
        this.messageQueue.push({ event: 'llm_config', data: messageData });
        this.emit('error', 'Not connected to server. Configuration queued.');
      }
    } catch (error) {
      console.error('Error configuring LLM:', error);
      this.emit('error', 'Failed to configure LLM');
    }
  }

  setModel(modelId: string) {
    try {
      const messageData = {
        type: 'set_model',
        payload: { model: modelId }
      };

      if (this.socket?.connected) {
        this.socket.send(JSON.stringify(messageData));
      } else {
        this.emit('error', 'Not connected to server. Please connect first.');
      }
    } catch (error) {
      console.error('Error setting model:', error);
      this.emit('error', 'Failed to set model');
    }
  }

  setApiKey(provider: string, apiKey: string) {
    try {
      if (!provider || !apiKey) {
        this.emit('error', 'Invalid API key or provider');
        return;
      }

      const messageData = {
        type: 'set_api_key',
        payload: { provider, apiKey }
      };

      if (this.socket?.connected) {
        this.socket.send(JSON.stringify(messageData));
      } else {
        this.emit('error', 'Not connected to server. Please connect first.');
      }
    } catch (error) {
      console.error('Error setting API key:', error);
      this.emit('error', 'Failed to set API key');
    }
  }

  requestAgentHierarchy() {
    const messageData = {
      type: 'get_agent_hierarchy',
      payload: {}
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  // Event handling
  on<T extends keyof WebSocketEvents>(event: T, callback: WebSocketEvents[T]) {
    if (!this.eventListeners[event]) {
      this.eventListeners[event] = [];
    }
    this.eventListeners[event]!.push(callback as EventHandler);
  }

  off<T extends keyof WebSocketEvents>(event: T, callback?: WebSocketEvents[T]) {
    if (!this.eventListeners[event]) return;
    
    if (callback) {
      const index = this.eventListeners[event]!.indexOf(callback as EventHandler);
      if (index > -1) {
        this.eventListeners[event]!.splice(index, 1);
      }
    } else {
      this.eventListeners[event] = [];
    }
  }

  private emit<T extends keyof WebSocketEvents>(event: T, ...args: Parameters<WebSocketEvents[T]>) {
    const listeners = this.eventListeners[event];
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(...args);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
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