import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as monaco from 'monaco-editor';
import { Copy, Download, Save, Loader2, Check, AlertCircle } from 'lucide-react';
import websocketService, { EditorSync } from '../../src/services/websocket';
import { useSocketEvent } from '../../src/hooks/useSocketEvent';
import { Settings } from '../../src/types';

interface MonacoEditorProps {
  onClearCode?: (clearFn: () => void) => void;
  settings?: Settings;
  importedContent?: string;
  currentFileName?: string;
  projectId?: string;
}

const languageMap: { [key: string]: string } = {
  'js': 'javascript',
  'jsx': 'javascript',
  'ts': 'typescript',
  'tsx': 'typescript',
  'html': 'html',
  'css': 'css',
  'scss': 'scss',
  'json': 'json',
  'md': 'markdown',
  'py': 'python',
  'java': 'java',
  'cpp': 'cpp',
  'c': 'c',
  'h': 'cpp',
  'php': 'php',
  'rb': 'ruby',
  'go': 'go',
  'rs': 'rust',
  'swift': 'swift',
  'kt': 'kotlin',
  'scala': 'scala'
};

const MonacoEditor: React.FC<MonacoEditorProps> = ({
  onClearCode,
  settings,
  importedContent,
  currentFileName,
  projectId = 'default'
}) => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  
  const isApplyingRemoteChange = useRef(false);
  const currentModelRef = useRef<monaco.editor.ITextModel | null>(null);
  const debounceTimeoutRef = useRef<number | null>(null);

  // Debounced content sender
  const sendContentChange = useCallback((content: string) => {
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }
    debounceTimeoutRef.current = window.setTimeout(() => {
      if (currentFileName) {
        websocketService.sendEditorContent(projectId, currentFileName, content);
      }
    }, 500); // 500ms debounce interval
  }, [projectId, currentFileName]);

  // Initialize Monaco editor
  useEffect(() => {
    if (!containerRef.current) return;

    const editor = monaco.editor.create(containerRef.current, {
      value: '',
      language: 'javascript',
      theme: settings?.theme === 'dark' ? 'vs-dark' : 'vs',
      fontSize: 14,
      fontFamily: '"JetBrains Mono", "Consolas", "Courier New", monospace',
      tabSize: (settings?.tabSize || 2) * 2,
      insertSpaces: true,
      detectIndentation: false,
      lineNumbers: settings?.showLineNumbers ? 'on' : 'off',
      lineNumbersMinChars: 3,
      renderLineHighlight: 'line',
      renderIndentGuides: true,
      guides: {
        indentation: true,
        bracketPairs: false,
        bracketPairsHorizontal: false,
        highlightActiveIndentation: true
      },
      minimap: { enabled: settings?.performanceMode !== 'performance' },
      automaticLayout: true,
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      formatOnPaste: true,
      formatOnType: true,
      padding: { top: 16, bottom: 16 },
      lineHeight: 22,
      letterSpacing: 0.5,
    });
    editorRef.current = editor;

    const disposable = editor.onDidChangeModelContent(() => {
      if (isApplyingRemoteChange.current) return;
      setSaveStatus('idle'); // Any edit resets save status
      const value = editor.getModel()?.getValue() || '';
      sendContentChange(value);
    });

    return () => {
      disposable.dispose();
      editor.dispose();
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [sendContentChange]);

  // Update editor settings
  useEffect(() => {
    if (!editorRef.current) return;
    editorRef.current.updateOptions({
      theme: settings?.theme === 'dark' ? 'vs-dark' : 'vs',
      fontSize: 14,
      fontFamily: '"JetBrains Mono", "Consolas", "Courier New", monospace',
      tabSize: (settings?.tabSize || 2) * 2,
      insertSpaces: true,
      detectIndentation: false,
      lineNumbers: settings?.showLineNumbers ? 'on' : 'off',
      lineNumbersMinChars: 3,
      renderLineHighlight: 'line',
      renderIndentGuides: true,
      guides: {
        indentation: true,
        bracketPairs: false,
        bracketPairsHorizontal: false,
        highlightActiveIndentation: true
      },
      minimap: { enabled: settings?.performanceMode !== 'performance' },
      padding: { top: 16, bottom: 16 },
      lineHeight: 22,
      letterSpacing: 0.5,
    });
  }, [settings?.theme, settings?.tabSize, settings?.showLineNumbers, settings?.performanceMode]);

  // Handle file changes and initial content
  useEffect(() => {
    if (!editorRef.current) return;

    if (!currentFileName) {
      editorRef.current.setModel(null);
      if (currentModelRef.current) {
        currentModelRef.current.dispose();
        currentModelRef.current = null;
      }
      return;
    }

    const extension = currentFileName.split('.').pop()?.toLowerCase();
    const language = languageMap[extension || ''] || 'plaintext';
    const uri = monaco.Uri.parse(`file:///${currentFileName}`);
    let model = monaco.editor.getModel(uri);
    
    // Dispose of the old model if it's different
    if (currentModelRef.current && currentModelRef.current.uri.toString() !== uri.toString()) {
        currentModelRef.current.dispose();
    }
    
    if (!model) {
      model = monaco.editor.createModel(importedContent || '', language, uri);
    } else {
      monaco.editor.setModelLanguage(model, language);
      if (model.getValue() !== (importedContent || '')) {
        isApplyingRemoteChange.current = true;
        model.setValue(importedContent || '');
        isApplyingRemoteChange.current = false;
      }
    }
    
    currentModelRef.current = model;
    editorRef.current.setModel(model);
    setSaveStatus('idle');
    
    websocketService.requestFileSync(currentFileName);
    
  }, [currentFileName, importedContent]);

  // Handle remote sync from the server
  useSocketEvent('editor_sync', (sync: EditorSync) => {
    if (!editorRef.current || !currentModelRef.current || sync.filePath !== currentFileName) return;
    
    isApplyingRemoteChange.current = true;
    try {
      const model = currentModelRef.current;
      if (model.getValue() !== sync.content) {
        model.setValue(sync.content);
        setSaveStatus('idle');
      }
    } finally {
      isApplyingRemoteChange.current = false;
    }
  });

  // Handle save acknowledgement
  useSocketEvent('file_save_ack', (data) => {
    if (data.filePath === currentFileName) {
      if (data.success) {
        setSaveStatus('success');
      } else {
        setSaveStatus('error');
      }
      // Reset status after a delay
      setTimeout(() => setSaveStatus('idle'), 2000);
    }
  });

  // Clear function
  const clearCode = useCallback(() => {
    if (editorRef.current && currentModelRef.current) {
      isApplyingRemoteChange.current = true;
      currentModelRef.current.setValue('');
      isApplyingRemoteChange.current = false;
    }
  }, []);

  useEffect(() => {
    if (onClearCode) {
      onClearCode(clearCode);
    }
  }, [onClearCode, clearCode]);

  const handleCopy = async () => {
    const content = currentModelRef.current?.getValue();
    if (!content?.trim()) return;

    try {
      await navigator.clipboard.writeText(content);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleDownload = () => {
    const content = currentModelRef.current?.getValue();
    if (!content?.trim()) return;

    const filename = currentFileName || 'code.txt';
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSave = useCallback(async () => {
    if (!currentFileName || !currentModelRef.current || saveStatus === 'saving') return;
    
    setSaveStatus('saving');
    
    try {
      // Auto-format on save if enabled
      if (editorRef.current) {
        await editorRef.current.getAction('editor.action.formatDocument')?.run();
      }
      const content = currentModelRef.current.getValue();
      websocketService.saveFile(currentFileName, content);
    } catch (err) {
      console.error('Save failed:', err);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 2000);
    }
  }, [currentFileName, saveStatus]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
    };
    
    const editorElement = containerRef.current;
    editorElement?.addEventListener('keydown', handleKeyDown);
    
    return () => editorElement?.removeEventListener('keydown', handleKeyDown);
  }, [handleSave]);
  
  const getSaveButton = () => {
    switch (saveStatus) {
      case 'saving':
        return <><Loader2 className="w-4 h-4 animate-spin" /> <span className="text-sm">Saving...</span></>;
      case 'success':
        return <><Check className="w-4 h-4 text-green-400" /> <span className="text-sm text-green-400">Saved!</span></>;
      case 'error':
        return <><AlertCircle className="w-4 h-4 text-red-400" /> <span className="text-sm text-red-400">Failed</span></>;
      default:
        return <><Save className="w-4 h-4" /> <span className="text-sm">Save</span></>;
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Editor Container */}
      <div className="flex-1 overflow-hidden">
        <div ref={containerRef} className="h-full w-full" />
      </div>
    </div>
  );
};

export default MonacoEditor; 