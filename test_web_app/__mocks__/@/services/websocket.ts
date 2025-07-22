// Manual mock for websocket service
const mockWebSocketService = {
  connect: jest.fn(),
  disconnect: jest.fn(),
  on: jest.fn(),
  off: jest.fn(),
  sendPrompt: jest.fn(),
  sendTerminalInput: jest.fn(),
  createTerminalSession: jest.fn(),
  closeTerminalSession: jest.fn(),
  resizeTerminal: jest.fn(),
  selectFile: jest.fn(),
  isConnected: jest.fn().mockReturnValue(true),
  sendLLMConfig: jest.fn(),
  sendChatMessage: jest.fn(),
};

export default mockWebSocketService;

// Export types
export type ChatMessage = {
  id: string;
  content: string;
  sender: 'user' | 'ai' | 'system';
  timestamp: string;
  agentId?: string;
  threadId?: string;
};

export type AgentUpdate = {
  agentId: string;
  status: 'active' | 'inactive' | 'waiting' | 'completed' | 'error' | 'delegating' | 'working';
  task?: string;
  progress?: number;
  parentId?: string;
};

export type WaveProgressUpdate = {
  phase: 'spec' | 'test' | 'impl';
  progress: number;
  message?: string;
};

export type FileTreeUpdate = {
  name: string;
  type: 'file' | 'folder';
  path?: string;
  children?: FileTreeUpdate[];
};

export type FileContent = {
  path: string;
  content: string;
  language?: string;
};

export type TerminalOutput = {
  sessionId: string;
  data: string;
};

export type TerminalSession = {
  sessionId: string;
};

export type TerminalData = TerminalOutput;

export type WebSocketEvents = {
  connected: () => void;
  disconnected: () => void;
  error: (error: Error) => void;
  message: (message: ChatMessage) => void;
  agent_update: (update: AgentUpdate) => void;
  file_tree_update: (tree: FileTreeUpdate) => void;
  file_content: (content: FileContent) => void;
  terminal_created: (session: TerminalSession) => void;
  terminal_output: (output: TerminalOutput) => void;
  terminal_closed: (session: TerminalSession) => void;
  wave_progress: (progress: WaveProgressUpdate) => void;
  task_update: (update: any) => void;
};