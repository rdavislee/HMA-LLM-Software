import { useEffect, useRef } from 'react';

interface KeyboardShortcutsProps {
  onNewChat?: () => void;
  onSaveFile?: () => void;
  onToggleTerminal?: () => void;
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
  }, []);
}; 