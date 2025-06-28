import { useEffect } from 'react';

interface KeyboardShortcutsProps {
  onNewChat?: () => void;
  onSaveFile?: () => void;
  onToggleTerminal?: () => void;
  onToggleSidebar?: () => void;
  onOpenSettings?: () => void;
  onCommandPalette?: () => void;
}

export const useKeyboardShortcuts = ({
  onNewChat,
  onSaveFile,
  onToggleTerminal,
  onToggleSidebar,
  onOpenSettings,
  onCommandPalette
}: KeyboardShortcutsProps) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Prevent shortcuts when typing in input fields
      if (event.target instanceof HTMLInputElement || 
          event.target instanceof HTMLTextAreaElement ||
          (event.target as HTMLElement).contentEditable === 'true') {
        return;
      }

      // Ctrl+N - New chat
      if (event.ctrlKey && event.key === 'n') {
        event.preventDefault();
        onNewChat?.();
      }

      // Ctrl+S - Save file
      if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        onSaveFile?.();
      }

      // Ctrl+Shift+P - Command palette
      if (event.ctrlKey && event.shiftKey && event.key === 'P') {
        event.preventDefault();
        onCommandPalette?.();
      }

      // Ctrl+` - Toggle terminal
      if (event.ctrlKey && event.key === '`') {
        event.preventDefault();
        onToggleTerminal?.();
      }

      // Ctrl+B - Toggle sidebar
      if (event.ctrlKey && event.key === 'b') {
        event.preventDefault();
        onToggleSidebar?.();
      }

      // F1 - Open settings
      if (event.key === 'F1') {
        event.preventDefault();
        onOpenSettings?.();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [onNewChat, onSaveFile, onToggleTerminal, onToggleSidebar, onOpenSettings, onCommandPalette]);
}; 