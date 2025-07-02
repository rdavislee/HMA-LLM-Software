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

// New interfaces for two-way code streaming
export interface EditorDiff {
  start: number;  // Start position in the document
  end: number;    // End position in the document
  text: string;   // Text to insert (empty string for deletions)
}

export interface EditorEdit {
  projectId: string;
  filePath: string;
  opId: string;
  diff: EditorDiff;
  cursor?: { line: number; column: number };
  revision?: string;  // File revision hash for conflict detection
}

export interface EditorAck {
  opId: string;
  success: boolean;
  revision?: string;  // New revision after applying the edit
  error?: string;
}

export interface EditorSync {
  filePath: string;
  content: string;
  revision: string;
  cursors?: Array<{ userId: string; line: number; column: number }>;
}

// New interfaces for interactive terminal
export interface TerminalData {
  sessionId: string;
  data: string;
}

export interface TerminalResize {
  sessionId: string;
  cols: number;
  rows: number;
}

export interface TerminalSession {
  sessionId: string;
  projectId: string;
  containerId?: string;
  status: 'starting' | 'running' | 'stopped' | 'error';
}

// Git-related interfaces
export interface GitFileChange {
  file_path: string;
  status: 'M' | 'A' | 'D' | 'R' | 'C' | 'U' | '??' | '!!';
  staged: boolean;
  old_path?: string;
}

export interface GitStatus {
  staged_files: GitFileChange[];
  unstaged_files: GitFileChange[];
  untracked_files: GitFileChange[];
  current_branch: string;
  ahead: number;
  behind: number;
  is_dirty: boolean;
  is_detached: boolean;
}

export interface GitDiff {
  file_path: string;
  diff_content: string;
  added_lines: number;
  removed_lines: number;
  is_binary: boolean;
}

export interface GitCommit {
  hash: string;
  short_hash: string;
  author_name: string;
  author_email: string;
  committer_name: string;
  committer_email: string;
  message: string;
  timestamp: string;
  parents: string[];
  files_changed: string[];
}

export interface GitBranch {
  name: string;
  is_current: boolean;
  is_remote: boolean;
  tracking_branch?: string;
  last_commit_hash?: string;
  last_commit_message?: string;
  last_commit_time?: string;
}

export interface GitUpdate {
  eventType: string;
  projectPath: string;
  data: Record<string, any>;
  timestamp: string;
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
  // Code streaming events
  editor_edit: (edit: EditorEdit) => void;
  editor_ack: (ack: EditorAck) => void;
  editor_sync: (sync: EditorSync) => void;
  // New terminal events
  terminal_data: (data: TerminalData) => void;
  terminal_session: (session: TerminalSession) => void;
  // Git events
  git_update: (update: GitUpdate) => void;
  git_status: (data: { status: GitStatus | null }) => void;
  git_diff: (data: { diff: GitDiff | null }) => void;
  git_commits: (data: { commits: GitCommit[] }) => void;
  git_branches: (data: { branches: GitBranch[] }) => void;
  git_stage_result: (data: { filePath: string; success: boolean }) => void;
  git_unstage_result: (data: { filePath: string; success: boolean }) => void;
  git_commit_result: (data: { success: boolean; commitHash?: string; error?: string }) => void;
  git_checkout_result: (data: { branchName: string; success: boolean }) => void;
  git_push_result: (data: { success: boolean; remoteName: string; branchName?: string }) => void;
  git_pull_result: (data: { success: boolean; remoteName: string }) => void;
}

class WebSocketService {
  private socket: Socket | null = null;
  private eventListeners: Partial<WebSocketEvents> = {};
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageQueue: any[] = [];
  private isConnecting = false;
  
  // New properties for operation tracking
  private pendingOps: Map<string, EditorEdit> = new Map();
  private fileRevisions: Map<string, string> = new Map();
  private opCounter = 0;

  // Terminal session tracking
  private terminalSessions: Map<string, TerminalSession> = new Map();

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
      
      // Replay pending operations on reconnection
      this.replayPendingOps();
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
          // Code streaming cases
          case 'editor_edit':
            this.handleRemoteEdit(parsedData.payload);
            break;
          case 'editor_ack':
            this.handleEditorAck(parsedData.payload);
            break;
          case 'editor_sync':
            this.handleEditorSync(parsedData.payload);
            break;
          // New terminal cases
          case 'terminal_data':
            this.emit('terminal_data', parsedData.payload);
            break;
          case 'terminal_session':
            this.handleTerminalSession(parsedData.payload);
            break;
          // Git cases
          case 'git_update':
            this.emit('git_update', parsedData.payload);
            break;
          case 'git_status':
            this.emit('git_status', parsedData.payload);
            break;
          case 'git_diff':
            this.emit('git_diff', parsedData.payload);
            break;
          case 'git_commits':
            this.emit('git_commits', parsedData.payload);
            break;
          case 'git_branches':
            this.emit('git_branches', parsedData.payload);
            break;
          case 'git_stage_result':
            this.emit('git_stage_result', parsedData.payload);
            break;
          case 'git_unstage_result':
            this.emit('git_unstage_result', parsedData.payload);
            break;
          case 'git_commit_result':
            this.emit('git_commit_result', parsedData.payload);
            break;
          case 'git_checkout_result':
            this.emit('git_checkout_result', parsedData.payload);
            break;
          case 'git_push_result':
            this.emit('git_push_result', parsedData.payload);
            break;
          case 'git_pull_result':
            this.emit('git_pull_result', parsedData.payload);
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

  clearProject() {
    const message = JSON.stringify({
      type: 'clear_project',
      payload: {}
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    } else {
      this.messageQueue.push(message);
    }
  }

  newChat() {
    const message = JSON.stringify({
      type: 'new_chat',
      payload: {}
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    } else {
      this.messageQueue.push(message);
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

  // New methods for two-way code streaming
  sendEditorEdit(projectId: string, filePath: string, diff: EditorDiff, cursor?: { line: number; column: number }) {
    const opId = `op_${this.opCounter++}_${Date.now()}`;
    const revision = this.fileRevisions.get(filePath);
    
    const edit: EditorEdit = {
      projectId,
      filePath,
      opId,
      diff,
      cursor,
      revision
    };
    
    // Store in pending ops
    this.pendingOps.set(opId, edit);
    
    const message = JSON.stringify({
      type: 'editor_edit',
      payload: edit
    });
    
    if (this.socket?.connected) {
      this.socket.send(message);
    } else {
      this.messageQueue.push(message);
      this.emit('error', 'Not connected to server. Edit queued.');
    }
    
    return opId;
  }
  
  requestFileSync(filePath: string) {
    const message = JSON.stringify({
      type: 'editor_sync_request',
      payload: { filePath }
    });
    
    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }
  
  private handleRemoteEdit(edit: EditorEdit) {
    // Update file revision
    if (edit.revision) {
      this.fileRevisions.set(edit.filePath, edit.revision);
    }
    
    // Emit to listeners (e.g., Monaco editor)
    this.emit('editor_edit', edit);
  }
  
  private handleEditorAck(ack: EditorAck) {
    // Remove from pending ops if successful
    if (ack.success) {
      this.pendingOps.delete(ack.opId);
      
      // Update revision if provided
      if (ack.revision) {
        const edit = this.pendingOps.get(ack.opId);
        if (edit) {
          this.fileRevisions.set(edit.filePath, ack.revision);
        }
      }
    } else {
      console.error(`Editor operation ${ack.opId} failed:`, ack.error);
      // Could trigger a full sync here if needed
    }
    
    // Emit to listeners
    this.emit('editor_ack', ack);
  }
  
  private handleEditorSync(sync: EditorSync) {
    // Update file revision
    this.fileRevisions.set(sync.filePath, sync.revision);
    
    // Clear any pending ops for this file as they're now obsolete
    for (const [opId, edit] of this.pendingOps.entries()) {
      if (edit.filePath === sync.filePath) {
        this.pendingOps.delete(opId);
      }
    }
    
    // Emit to listeners
    this.emit('editor_sync', sync);
  }
  
  private async replayPendingOps() {
    // Replay pending operations after reconnection
    if (this.pendingOps.size > 0) {
      console.log(`Replaying ${this.pendingOps.size} pending operations`);
      
      for (const [_opId, edit] of this.pendingOps.entries()) {
        const message = JSON.stringify({
          type: 'editor_edit',
          payload: edit
        });
        
        if (this.socket?.connected) {
          this.socket.send(message);
        }
      }
    }
  }
  
  clearPendingOps(filePath?: string) {
    if (filePath) {
      // Clear ops for specific file
      for (const [opId, edit] of this.pendingOps.entries()) {
        if (edit.filePath === filePath) {
          this.pendingOps.delete(opId);
        }
      }
    } else {
      // Clear all pending ops
      this.pendingOps.clear();
    }
  }
  
  getFileRevision(filePath: string): string | undefined {
    return this.fileRevisions.get(filePath);
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

  // Terminal methods
  createTerminalSession(projectId: string): string {
    const sessionId = `term_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const session: TerminalSession = {
      sessionId,
      projectId,
      status: 'starting'
    };
    
    this.terminalSessions.set(sessionId, session);
    
    const message = JSON.stringify({
      type: 'terminal_create',
      payload: { sessionId, projectId }
    });
    
    if (this.socket?.connected) {
      this.socket.send(message);
    } else {
      this.messageQueue.push(message);
    }
    
    return sessionId;
  }
  
  sendTerminalData(sessionId: string, data: string) {
    const message = JSON.stringify({
      type: 'terminal_data',
      payload: { sessionId, data }
    });
    
    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }
  
  resizeTerminal(sessionId: string, cols: number, rows: number) {
    const message = JSON.stringify({
      type: 'terminal_resize',
      payload: { sessionId, cols, rows }
    });
    
    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }
  
  closeTerminal(sessionId: string) {
    const message = JSON.stringify({
      type: 'terminal_close',
      payload: { sessionId }
    });
    
    if (this.socket?.connected) {
      this.socket.send(message);
    }
    
    this.terminalSessions.delete(sessionId);
  }
  
  private handleTerminalSession(session: TerminalSession) {
    this.terminalSessions.set(session.sessionId, session);
    this.emit('terminal_session', session);
  }
  
  getTerminalSession(sessionId: string): TerminalSession | undefined {
    return this.terminalSessions.get(sessionId);
  }

  // Git-related methods

  requestGitStatus() {
    const message = JSON.stringify({
      type: 'git_status',
      payload: {}
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  requestGitDiff(filePath: string, staged: boolean = false) {
    const message = JSON.stringify({
      type: 'git_diff',
      payload: {
        filePath,
        staged
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  stageFile(filePath: string) {
    const message = JSON.stringify({
      type: 'git_stage',
      payload: {
        filePath
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  unstageFile(filePath: string) {
    const message = JSON.stringify({
      type: 'git_unstage',
      payload: {
        filePath
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  commitChanges(message: string, authorName?: string, authorEmail?: string) {
    const commitMessage = JSON.stringify({
      type: 'git_commit',
      payload: {
        message,
        authorName,
        authorEmail
      }
    });

    if (this.socket?.connected) {
      this.socket.send(commitMessage);
    }
  }

  requestGitBranches() {
    const message = JSON.stringify({
      type: 'git_branches',
      payload: {}
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  checkoutBranch(branchName: string) {
    const message = JSON.stringify({
      type: 'git_checkout',
      payload: {
        branchName
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  pushChanges(remoteName: string = 'origin', branchName?: string) {
    const message = JSON.stringify({
      type: 'git_push',
      payload: {
        remoteName,
        branchName
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  pullChanges(remoteName: string = 'origin') {
    const message = JSON.stringify({
      type: 'git_pull',
      payload: {
        remoteName
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }

  requestGitCommits(maxCount: number = 50) {
    const message = JSON.stringify({
      type: 'git_commits',
      payload: {
        maxCount
      }
    });

    if (this.socket?.connected) {
      this.socket.send(message);
    }
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();
export default websocketService;