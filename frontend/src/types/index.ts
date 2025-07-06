/**
 * This file contains shared TypeScript types used across the frontend.
 */

// From App.tsx / components
export interface Settings {
  theme: 'light' | 'dark' | 'system';
  tabSize: number;
  showLineNumbers: boolean;
  showTimestamps: boolean;
  performanceMode: 'balanced' | 'performance' | 'quality';
  accentColor: string;
  fontSize: number;
  autoSave: boolean;
}

export interface ImportedFile {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  content?: string;
}

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  content?: string;
  children?: FileNode[];
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  agentId?: string;
  metadata?: {
    filePath?: string;
    codeBlock?: boolean;
    syntax?: string;
  };
}

// Project Initialization types
export interface Language {
  code: string;
  name: string;
  extension: string;
}

export interface ProjectInitializationState {
  isActive: boolean;
  phase: 1 | 2 | 3 | null;
  phaseTitle: 'Product Understanding' | 'Structure Stage' | 'Implementation' | null;
  status: 'active' | 'waiting_approval' | 'completed' | 'error' | null;
  projectId?: string;
  projectPath?: string;
  requiresApproval: boolean;
  selectedLanguage?: Language;
} 