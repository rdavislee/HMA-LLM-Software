import React from 'react';
import { describe, it, expect, beforeEach, vi } from '@jest/globals';
import { render, screen, waitFor, fireEvent } from '../../setup/testUtils';
import { UserInput } from '@/components/UserInput';
import { createMockFile } from '../../setup/testUtils';

describe('UserInput Component', () => {
  const mockOnSendMessage = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render with default props', () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      expect(screen.getByPlaceholderText('Enter a prompt')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    });

    it('should render with custom placeholder', () => {
      render(
        <UserInput 
          onSendMessage={mockOnSendMessage} 
          placeholder="Type your message..."
        />
      );
      
      expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    });

    it('should disable input when disabled prop is true', () => {
      render(
        <UserInput 
          onSendMessage={mockOnSendMessage} 
          disabled={true}
        />
      );
      
      const textarea = screen.getByPlaceholderText('Enter a prompt') as HTMLTextAreaElement;
      expect(textarea).toBeDisabled();
    });

    it('should show loading state', () => {
      render(
        <UserInput 
          onSendMessage={mockOnSendMessage} 
          isLoading={true}
        />
      );
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toContainHTML('animate-spin');
    });
  });

  describe('Text Input', () => {
    it('should update input value on change', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('Enter a prompt') as HTMLTextAreaElement;
      await user.type(textarea, 'Hello world');
      
      expect(textarea.value).toBe('Hello world');
    });

    it('should send message on button click', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('Enter a prompt');
      await user.type(textarea, 'Test message');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      expect(mockOnSendMessage).toHaveBeenCalledWith('Test message', []);
      expect(textarea).toHaveValue('');
    });

    it('should send message on Enter key', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('Enter a prompt');
      await user.type(textarea, 'Test message');
      
      fireEvent.keyPress(textarea, { key: 'Enter', code: 'Enter', charCode: 13 });
      
      expect(mockOnSendMessage).toHaveBeenCalledWith('Test message', []);
      expect(textarea).toHaveValue('');
    });

    it('should not send message on Shift+Enter', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('Enter a prompt');
      await user.type(textarea, 'Test message');
      
      fireEvent.keyPress(textarea, { 
        key: 'Enter', 
        code: 'Enter', 
        charCode: 13,
        shiftKey: true 
      });
      
      expect(mockOnSendMessage).not.toHaveBeenCalled();
      expect(textarea).toHaveValue('Test message');
    });

    it('should not send empty messages', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      expect(mockOnSendMessage).not.toHaveBeenCalled();
    });

    it('should trim whitespace from messages', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('Enter a prompt');
      await user.type(textarea, '   ');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toBeDisabled();
    });
  });

  describe('File Attachments', () => {
    it('should show file attachment button', () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const attachButton = screen.getAllByRole('button')[0]; // First button is paperclip
      expect(attachButton).toContainHTML('lucide-paperclip');
    });

    it('should handle file selection', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const file = createMockFile('test content', 'test.txt', 'text/plain');
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText('test.txt')).toBeInTheDocument();
        expect(screen.getByText('(12 B)')).toBeInTheDocument();
      });
    });

    it('should handle multiple file selection', async () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const file1 = createMockFile('content 1', 'file1.txt', 'text/plain');
      const file2 = createMockFile('content 2', 'file2.txt', 'text/plain');
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      
      Object.defineProperty(input, 'files', {
        value: [file1, file2],
        writable: false,
      });
      
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText('file1.txt')).toBeInTheDocument();
        expect(screen.getByText('file2.txt')).toBeInTheDocument();
      });
    });

    it('should read text file content', async () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const fileContent = 'Hello from file';
      const file = createMockFile(fileContent, 'test.txt', 'text/plain');
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText('test.txt')).toBeInTheDocument();
      });
      
      // Send message with file
      const sendButton = screen.getByRole('button', { name: /send/i });
      fireEvent.click(sendButton);
      
      await waitFor(() => {
        expect(mockOnSendMessage).toHaveBeenCalledWith('', [
          expect.objectContaining({
            name: 'test.txt',
            content: fileContent
          })
        ]);
      });
    });

    it('should remove attached files', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const file = createMockFile('test', 'test.txt', 'text/plain');
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText('test.txt')).toBeInTheDocument();
      });
      
      // Click remove button
      const removeButton = screen.getByRole('button', { name: '' }); // X button has no text
      await user.click(removeButton);
      
      expect(screen.queryByText('test.txt')).not.toBeInTheDocument();
    });

    it('should format file sizes correctly', async () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const testCases = [
        { size: 500, expected: '500 B' },
        { size: 1500, expected: '1.5 KB' },
        { size: 1500000, expected: '1.4 MB' }
      ];
      
      for (const { size, expected } of testCases) {
        const file = new File(['a'.repeat(size)], 'test.txt', { type: 'text/plain' });
        Object.defineProperty(file, 'size', { value: size });
        
        const input = document.querySelector('input[type="file"]') as HTMLInputElement;
        Object.defineProperty(input, 'files', {
          value: [file],
          writable: false,
        });
        
        fireEvent.change(input);
        
        await waitFor(() => {
          expect(screen.getByText(`(${expected})`)).toBeInTheDocument();
        });
        
        // Clean up for next iteration
        const removeButton = screen.getByRole('button', { name: '' });
        fireEvent.click(removeButton);
      }
    });

    it('should accept only specified file types', () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      expect(input.accept).toContain('text/*');
      expect(input.accept).toContain('.md');
      expect(input.accept).toContain('.json');
      expect(input.accept).toContain('.js');
      expect(input.accept).toContain('.tsx');
    });
  });

  describe('Send Button State', () => {
    it('should disable send button when empty', () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toBeDisabled();
    });

    it('should enable send button with text', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const textarea = screen.getByPlaceholderText('Enter a prompt');
      await user.type(textarea, 'Hello');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).not.toBeDisabled();
    });

    it('should enable send button with files only', async () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const file = createMockFile('test', 'test.txt', 'text/plain');
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);
      
      await waitFor(() => {
        const sendButton = screen.getByRole('button', { name: /send/i });
        expect(sendButton).not.toBeDisabled();
      });
    });

    it('should disable send button when loading', () => {
      render(
        <UserInput 
          onSendMessage={mockOnSendMessage} 
          isLoading={true}
        />
      );
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toBeDisabled();
    });

    it('should disable all controls when disabled', () => {
      render(
        <UserInput 
          onSendMessage={mockOnSendMessage} 
          disabled={true}
        />
      );
      
      const textarea = screen.getByPlaceholderText('Enter a prompt');
      const sendButton = screen.getByRole('button', { name: /send/i });
      const attachButton = screen.getAllByRole('button')[0];
      
      expect(textarea).toBeDisabled();
      expect(sendButton).toBeDisabled();
      expect(attachButton).toBeDisabled();
    });
  });

  describe('Message Clearing', () => {
    it('should clear input and files after sending', async () => {
      const { user } = render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      // Add text
      const textarea = screen.getByPlaceholderText('Enter a prompt');
      await user.type(textarea, 'Test message');
      
      // Add file
      const file = createMockFile('test', 'test.txt', 'text/plain');
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText('test.txt')).toBeInTheDocument();
      });
      
      // Send
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      // Check cleared
      expect(textarea).toHaveValue('');
      expect(screen.queryByText('test.txt')).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle file read errors gracefully', async () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const file = createMockFile('test', 'test.txt', 'text/plain');
      // Mock file.text() to throw error
      file.text = jest.fn().mockRejectedValue(new Error('Read error'));
      
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);
      
      // Should handle error without crashing
      await waitFor(() => {
        expect(screen.queryByText('test.txt')).toBeInTheDocument();
      });
    });

    it('should handle files without type', async () => {
      render(<UserInput onSendMessage={mockOnSendMessage} />);
      
      const file = new File(['content'], 'test.unknown');
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);
      
      await waitFor(() => {
        expect(screen.getByText('test.unknown')).toBeInTheDocument();
      });
    });
  });
});