import { io, Socket } from 'socket.io-client';
import { ImportedFile } from '../types';

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
  data: Record<string, unknown>;
  timestamp: string;
}

// Project Initialization interfaces
export interface ProjectInitRequest {
  language: string;
  initialPrompt: string;
  projectName?: string;
}

export interface ProjectInitStatus {
  phase: 1 | 2 | 3;
  phaseTitle: 'Product Understanding' | 'Structure Stage' | 'Implementation';
  status: 'active' | 'waiting_approval' | 'completed' | 'error';
  projectId?: string;
  projectPath?: string;
  message?: string;
  requiresApproval: boolean;
}

export interface PhaseApproval {
  phase: 1 | 2 | 3;
  approved: boolean;
  feedback?: string;
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
  file_save_ack: (data: { filePath: string; success: boolean; error?: string }) => void;
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
  // Project Initialization events
  project_init_status: (status: ProjectInitStatus) => void;
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
      console.log('Connected to server');
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

    // Handle different message types from the server
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
          case 'file_save_ack':
            this.emit('file_save_ack', parsedData.payload);
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
          // Project Initialization cases
          case 'project_init_status':
            this.emit('project_init_status', parsedData.payload);
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
      // Queue the message if not connected
      this.messageQueue.push({ event: 'prompt', data: messageData });
      this.emit('error', 'Not connected to server. Message queued.');
    }
  }

  stopAgentThinking() {
    const messageData = {
      type: 'stop',
      payload: {}
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
      console.log('Sent stop command to server');
    }
  }

  importProject(files: ImportedFile[]) {
    const messageData = {
      type: 'import_project',
      payload: { files }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'import_project', data: messageData });
      this.emit('error', 'Not connected to server. Message queued.');
    }
  }

  selectFile(filePath: string) {
    const messageData = {
      type: 'file_select',
      payload: {
        filePath
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  clearProject() {
    const messageData = {
      type: 'clear_project',
      payload: {}
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'clear_project', data: messageData });
    }
  }

  newChat() {
    const messageData = {
      type: 'new_chat',
      payload: {}
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'new_chat', data: messageData });
    }
  }

  editCode(filePath: string, content: string) {
    const messageData = {
      type: 'code_edit',
      payload: {
        filePath,
        content
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
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
    
    const messageData = {
      type: 'editor_edit',
      payload: edit
    };
    
    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'editor_edit', data: messageData });
      this.emit('error', 'Not connected to server. Edit queued.');
    }
    
    return opId;
  }
  
  sendEditorContent(projectId: string, filePath: string, content: string) {
    const messageData = {
      type: 'editor_content_change',
      payload: { projectId, filePath, content }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'editor_content_change', data: messageData });
    }
  }
  
  saveFile(filePath: string, content: string) {
    const messageData = {
      type: 'file_save',
      payload: { filePath, content }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'file_save', data: messageData });
    }
  }
  
  requestFileSync(filePath: string) {
    const messageData = {
      type: 'editor_sync_request',
      payload: { filePath }
    };
    
    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
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

  // Terminal methods
  createTerminalSession(projectId: string) {
    const messageData = {
      type: 'terminal_create',
      payload: { projectId } // Let server generate the session ID
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
  
  private handleTerminalSession(session: TerminalSession) {
    this.terminalSessions.set(session.sessionId, session);
    this.emit('terminal_session', session);
  }
  
  getTerminalSession(sessionId: string): TerminalSession | undefined {
    return this.terminalSessions.get(sessionId);
  }

  // Git-related methods

  requestGitStatus() {
    const messageData = {
      type: 'git_status',
      payload: {}
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  requestGitDiff(filePath: string, staged: boolean = false) {
    const messageData = {
      type: 'git_diff',
      payload: {
        filePath,
        staged
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  stageFile(filePath: string) {
    const messageData = {
      type: 'git_stage',
      payload: {
        filePath
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  unstageFile(filePath: string) {
    const messageData = {
      type: 'git_unstage',
      payload: {
        filePath
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  commitChanges(message: string, authorName?: string, authorEmail?: string) {
    const messageData = {
      type: 'git_commit',
      payload: {
        message,
        authorName,
        authorEmail
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  requestGitBranches() {
    const messageData = {
      type: 'git_branches',
      payload: {}
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  checkoutBranch(branchName: string) {
    const messageData = {
      type: 'git_checkout',
      payload: {
        branchName
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  pushChanges(remoteName: string = 'origin', branchName?: string) {
    const messageData = {
      type: 'git_push',
      payload: {
        remoteName,
        branchName
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  pullChanges(remoteName: string = 'origin') {
    const messageData = {
      type: 'git_pull',
      payload: {
        remoteName
      }
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    }
  }

  requestGitCommits(maxCount: number = 50) {
    if (!this.socket?.connected) {
      console.warn('Cannot request git commits: not connected');
      return;
    }

    this.socket.emit('git_commits', { maxCount });
  }

  // Project Initialization methods
  
  /**
   * Start a new project initialization process
   * @param language - Programming language for the project
   * @param initialPrompt - Initial description of what to build
   * @param projectName - Optional project name (auto-generated if not provided)
   */
  startProjectInitialization(language: string, initialPrompt: string, projectName?: string) {
    const request: ProjectInitRequest = {
      language,
      initialPrompt,
      projectName
    };

    const messageData = {
      type: 'start_project_init',
      payload: request
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'start_project_init', data: messageData });
      this.emit('error', 'Not connected to server. Project initialization queued.');
    }
  }

  /**
   * Approve the current phase of project initialization
   * @param phase - Current phase number (1, 2, or 3)
   */
  approvePhase(phase: 1 | 2 | 3) {
    const approval: PhaseApproval = {
      phase,
      approved: true
    };

    const messageData = {
      type: 'approve_phase',
      payload: approval
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'approve_phase', data: messageData });
      this.emit('error', 'Not connected to server. Phase approval queued.');
    }
  }

  /**
   * Reject the current phase with optional feedback
   * @param phase - Current phase number (1, 2, or 3)
   * @param feedback - Optional feedback for why the phase was rejected
   */
  rejectPhase(phase: 1 | 2 | 3, feedback?: string) {
    const rejection: PhaseApproval = {
      phase,
      approved: false,
      feedback
    };

    const messageData = {
      type: 'reject_phase',
      payload: rejection
    };

    if (this.socket?.connected) {
      this.socket.send(JSON.stringify(messageData));
    } else {
      this.messageQueue.push({ event: 'reject_phase', data: messageData });
      this.emit('error', 'Not connected to server. Phase rejection queued.');
    }
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();
export default websocketService;
