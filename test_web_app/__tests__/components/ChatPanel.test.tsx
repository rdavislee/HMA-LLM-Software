import React from 'react';
import { describe, it, expect, beforeEach, vi, afterEach } from '@jest/globals';
import { render, screen, waitFor } from '../../setup/testUtils';
import { ChatPanel } from '@/components/ChatPanel';
import { useSocketEvent } from '@/hooks/useSocketEvent';
import { createMockChatMessage } from '../../setup/testUtils';

// Mock the useSocketEvent hook
jest.mock('@/hooks/useSocketEvent');

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

describe('ChatPanel Component', () => {
  const mockUseSocketEvent = useSocketEvent as jest.MockedFunction<typeof useSocketEvent>;
  const mockOnNewChat = jest.fn();
  const mockOnMessagesUpdate = jest.fn();
  const mockOnLoadingChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseSocketEvent.mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('should render without messages', () => {
      render(
        <ChatPanel 
          messages={[]} 
          onNewChat={mockOnNewChat}
        />
      );
      
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should render user messages', () => {
      const messages = [
        createMockChatMessage({
          id: '1',
          text: 'Hello from user',
          sender: 'user',
          timestamp: '10:30:00 AM'
        })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      expect(screen.getByText('Hello from user')).toBeInTheDocument();
      expect(screen.getByText('10:30:00 AM')).toBeInTheDocument();
    });

    it('should render assistant messages', () => {
      const messages = [
        createMockChatMessage({
          id: '1',
          text: 'Hello from assistant',
          sender: 'assistant',
          timestamp: '10:31:00 AM'
        })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      expect(screen.getByText('Hello from assistant')).toBeInTheDocument();
    });

    it('should render system messages', () => {
      const messages = [
        createMockChatMessage({
          id: '1',
          text: 'System notification',
          sender: 'system',
          timestamp: '10:32:00 AM'
        })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      expect(screen.getByText('System notification')).toBeInTheDocument();
    });

    it('should render mixed message types', () => {
      const messages = [
        createMockChatMessage({ id: '1', text: 'User message', sender: 'user' }),
        createMockChatMessage({ id: '2', text: 'Assistant response', sender: 'assistant' }),
        createMockChatMessage({ id: '3', text: 'System info', sender: 'system' }),
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      expect(screen.getByText('User message')).toBeInTheDocument();
      expect(screen.getByText('Assistant response')).toBeInTheDocument();
      expect(screen.getByText('System info')).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('should show loading indicator when isLoading is true', () => {
      render(
        <ChatPanel 
          messages={[]} 
          onNewChat={mockOnNewChat}
          isLoading={true}
        />
      );
      
      expect(screen.getByText('Thinking...')).toBeInTheDocument();
    });

    it('should not show loading indicator when isLoading is false', () => {
      render(
        <ChatPanel 
          messages={[]} 
          onNewChat={mockOnNewChat}
          isLoading={false}
        />
      );
      
      expect(screen.queryByText('Thinking...')).not.toBeInTheDocument();
    });
  });

  describe('New Chat Button', () => {
    it('should call onNewChat when plus button is clicked', async () => {
      const { user } = render(
        <ChatPanel 
          messages={[]} 
          onNewChat={mockOnNewChat}
        />
      );
      
      const newChatButton = screen.getByRole('button');
      await user.click(newChatButton);
      
      expect(mockOnNewChat).toHaveBeenCalledTimes(1);
    });
  });

  describe('Auto-scrolling', () => {
    it('should scroll to bottom when messages change', async () => {
      const { rerender } = render(
        <ChatPanel 
          messages={[]} 
          onNewChat={mockOnNewChat}
        />
      );
      
      const newMessages = [
        createMockChatMessage({ id: '1', text: 'New message' })
      ];
      
      rerender(
        <ChatPanel 
          messages={newMessages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      await waitFor(() => {
        expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth' });
      });
    });
  });

  describe('WebSocket Integration', () => {
    it('should register message event listener', () => {
      render(
        <ChatPanel 
          messages={[]} 
          onNewChat={mockOnNewChat}
        />
      );
      
      expect(mockUseSocketEvent).toHaveBeenCalledWith(
        'message',
        expect.any(Function)
      );
    });

    it('should register agent_update event listener', () => {
      render(
        <ChatPanel 
          messages={[]} 
          onNewChat={mockOnNewChat}
        />
      );
      
      expect(mockUseSocketEvent).toHaveBeenCalledWith(
        'agent_update',
        expect.any(Function)
      );
    });

    it('should handle incoming WebSocket messages', async () => {
      let messageHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'message') {
          messageHandler = handler;
        }
      });

      const existingMessages = [
        createMockChatMessage({ id: '1', text: 'Existing message' })
      ];

      render(
        <ChatPanel 
          messages={existingMessages} 
          onNewChat={mockOnNewChat}
          onMessagesUpdate={mockOnMessagesUpdate}
        />
      );

      // Simulate WebSocket message
      const wsMessage = {
        id: '2',
        content: 'New WebSocket message',
        sender: 'ai',
        timestamp: new Date().toISOString(),
        agentId: 'agent-1'
      };

      messageHandler(wsMessage);

      expect(mockOnMessagesUpdate).toHaveBeenCalledWith([
        ...existingMessages,
        expect.objectContaining({
          id: '2',
          text: 'New WebSocket message',
          sender: 'assistant',
          agentId: 'agent-1'
        })
      ]);
    });

    it('should handle agent updates and show loading state', async () => {
      let agentHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'agent_update') {
          agentHandler = handler;
        }
      });

      const messages = [
        createMockChatMessage({ 
          id: '1', 
          text: 'Processing...', 
          sender: 'assistant',
          agentId: 'agent-1'
        })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
          onLoadingChange={mockOnLoadingChange}
        />
      );

      // Simulate agent becoming active
      agentHandler({
        agentId: 'agent-1',
        status: 'active',
        task: 'Analyzing code'
      });

      expect(mockOnLoadingChange).toHaveBeenCalledWith(true);

      // Simulate agent completing
      agentHandler({
        agentId: 'agent-1',
        status: 'completed'
      });

      expect(mockOnLoadingChange).toHaveBeenCalledWith(false);
    });

    it('should show agent task status for active agents', () => {
      let agentHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'agent_update') {
          agentHandler = handler;
        }
      });

      const messages = [
        createMockChatMessage({ 
          id: '1', 
          text: 'Working on your request', 
          sender: 'assistant',
          agentId: 'agent-1'
        })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );

      // Activate agent
      agentHandler({
        agentId: 'agent-1',
        status: 'active',
        task: 'Writing unit tests'
      });

      expect(screen.getByText('Writing unit tests')).toBeInTheDocument();
    });
  });

  describe('Message Styling', () => {
    it('should apply correct styles for user messages', () => {
      const messages = [
        createMockChatMessage({ id: '1', text: 'User message', sender: 'user' })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      const messageElement = screen.getByText('User message').closest('div');
      expect(messageElement).toHaveClass('bg-gradient-to-r', 'from-primary/80', 'to-accent/80');
    });

    it('should apply correct styles for assistant messages', () => {
      const messages = [
        createMockChatMessage({ id: '1', text: 'Assistant message', sender: 'assistant' })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      const messageElement = screen.getByText('Assistant message').closest('div');
      expect(messageElement).toHaveClass('bg-gradient-to-r', 'from-secondary/50', 'to-card/50');
    });

    it('should apply correct styles for system messages', () => {
      const messages = [
        createMockChatMessage({ id: '1', text: 'System message', sender: 'system' })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      const messageElement = screen.getByText('System message').closest('div');
      expect(messageElement).toHaveClass('bg-muted/50');
    });
  });

  describe('Icons', () => {
    it('should show user icon for user messages', () => {
      const messages = [
        createMockChatMessage({ id: '1', text: 'User message', sender: 'user' })
      ];

      const { container } = render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      const userIcon = container.querySelector('.lucide-user');
      expect(userIcon).toBeInTheDocument();
    });

    it('should show bot icon for assistant messages', () => {
      const messages = [
        createMockChatMessage({ id: '1', text: 'Assistant message', sender: 'assistant' })
      ];

      const { container } = render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      const botIcon = container.querySelector('.lucide-bot');
      expect(botIcon).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty message text', () => {
      const messages = [
        createMockChatMessage({ id: '1', text: '', sender: 'user' })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      // Should render without crashing
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should handle very long messages', () => {
      const longText = 'A'.repeat(1000);
      const messages = [
        createMockChatMessage({ id: '1', text: longText, sender: 'user' })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      expect(screen.getByText(longText)).toBeInTheDocument();
    });

    it('should handle messages with line breaks', () => {
      const multilineText = 'Line 1\nLine 2\nLine 3';
      const messages = [
        createMockChatMessage({ id: '1', text: multilineText, sender: 'user' })
      ];

      render(
        <ChatPanel 
          messages={messages} 
          onNewChat={mockOnNewChat}
        />
      );
      
      const messageElement = screen.getByText(multilineText);
      expect(messageElement).toHaveClass('whitespace-pre-wrap');
    });
  });
});