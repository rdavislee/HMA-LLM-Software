import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Custom render function that includes common providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  return {
    user: userEvent.setup(),
    ...render(ui, { ...options }),
  };
};

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };

// Utility to create mock WebSocket events
export const createMockSocketEvent = (event: string, data: any) => {
  return new CustomEvent('socket-event', {
    detail: { event, data },
  });
};

// Utility to wait for async updates
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0));

// Mock file creator for file input tests
export const createMockFile = (
  content: string,
  fileName: string,
  mimeType: string
): File => {
  const blob = new Blob([content], { type: mimeType });
  return new File([blob], fileName, { type: mimeType });
};

// Mock chat message factory
export const createMockChatMessage = (overrides = {}) => ({
  id: Date.now().toString(),
  text: 'Test message',
  timestamp: new Date().toISOString(),
  sender: 'user' as const,
  threadId: 'test-thread',
  agentId: 'test-agent',
  ...overrides,
});

// Mock agent factory
export const createMockAgent = (overrides = {}) => ({
  id: 'agent-1',
  name: 'TestAgent',
  status: 'active' as const,
  task: 'Test task',
  progress: 50,
  phase: 'spec' as const,
  tokens: 1000,
  cost: 0.05,
  ...overrides,
});

// Mock file tree node factory
export const createMockFileNode = (overrides = {}) => ({
  id: 'file-1',
  name: 'test.ts',
  type: 'file' as const,
  path: '/test.ts',
  content: 'test content',
  ...overrides,
});

export const createMockFolderNode = (overrides = {}) => ({
  id: 'folder-1',
  name: 'src',
  type: 'folder' as const,
  path: '/src',
  children: [],
  ...overrides,
});

// Mock WebSocket service
export const mockWebSocketService = {
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
};

// Mock chat storage service
export const mockChatStorage = {
  saveChatSession: jest.fn(),
  getChatSession: jest.fn(),
  getAllSessions: jest.fn(),
  deleteSession: jest.fn(),
  clearAllSessions: jest.fn(),
  getCurrentSession: jest.fn(),
  createNewSession: jest.fn().mockReturnValue({
    id: 'test-session',
    messages: [],
    createdAt: new Date(),
    lastModified: new Date(),
  }),
};