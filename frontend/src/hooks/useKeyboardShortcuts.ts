import { useEffect, useRef } from 'react';

interface KeyboardShortcutsProps {
  onNewChat?: () => void;
  onSaveFile?: () => void;
  onToggleTerminal?: () => void;
  onToggleSidebar?: () => void;
  onToggleGitPanel?: () => void;
  onOpenSettings?: () => void;
  onCommandPalette?: () => void;
}

export const useKeyboardShortcuts = (props: KeyboardShortcutsProps) => {
  const callbackRef = useRef(props);

  useEffect(() => {
    callbackRef.current = props;
  }, [props]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Prevent shortcuts when an input element is focused
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      const {
        onNewChat,
        onSaveFile,
        onToggleTerminal,
        onToggleSidebar,
        onToggleGitPanel,
        onOpenSettings,
        onCommandPalette
      } = callbackRef.current;

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

      // Ctrl+Shift+G - Toggle git panel
      if (event.ctrlKey && event.shiftKey && event.key === 'G') {
        event.preventDefault();
        onToggleGitPanel?.();
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
  }, []); // Empty dependency array ensures this effect runs only once
}; 