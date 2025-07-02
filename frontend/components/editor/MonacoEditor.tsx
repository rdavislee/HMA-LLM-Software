import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as monaco from 'monaco-editor';
import { Copy, Download, Save, Loader2 } from 'lucide-react';
import websocketService, { EditorEdit, EditorSync, EditorDiff } from '../../src/services/websocket';

interface Settings {
  theme: 'light' | 'dark' | 'system';
  tabSize: number;
  showLineNumbers: boolean;
  showTimestamps: boolean;
  performanceMode: 'balanced' | 'performance' | 'quality';
  accentColor: string;
  fontSize: number;
  autoSave: boolean;
}

interface MonacoEditorProps {
  onClearCode?: (clearFn: () => void) => void;
  settings?: Settings;
  importedContent?: string;
  currentFileName?: string;
  projectId?: string;
}

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
  const [isSaving, setIsSaving] = useState(false);
  const [isApplyingRemote, setIsApplyingRemote] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  // Track the current model to avoid recreating it
  const currentModelRef = useRef<monaco.editor.ITextModel | null>(null);

  // Initialize Monaco editor
  useEffect(() => {
    if (!containerRef.current) return;

    // Create editor instance
    const editor = monaco.editor.create(containerRef.current, {
      value: '',
      language: 'javascript',
      theme: settings?.theme === 'dark' ? 'vs-dark' : 'vs',
      fontSize: settings?.fontSize || 14,
      tabSize: settings?.tabSize || 2,
      lineNumbers: settings?.showLineNumbers ? 'on' : 'off',
      minimap: {
        enabled: settings?.performanceMode !== 'performance'
      },
      automaticLayout: true,
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      formatOnPaste: true,
      formatOnType: true,
    });

    editorRef.current = editor;

    // Handle local changes
    const disposable = editor.onDidChangeModelContent((event) => {
      if (isApplyingRemote) return; // Don't send remote changes back
      
      setHasUnsavedChanges(true);
      
      // Convert Monaco changes to our diff format
      event.changes.forEach(change => {
        const diff: EditorDiff = {
          start: change.rangeOffset,
          end: change.rangeOffset + change.rangeLength,
          text: change.text
        };
        
        const position = editor.getPosition();
        const cursor = position ? {
          line: position.lineNumber,
          column: position.column
        } : undefined;
        
        if (currentFileName) {
          websocketService.sendEditorEdit(projectId, currentFileName, diff, cursor);
        }
      });
    });

    return () => {
      disposable.dispose();
      editor.dispose();
    };
  }, []);

  // Update editor settings
  useEffect(() => {
    if (!editorRef.current) return;

    editorRef.current.updateOptions({
      theme: settings?.theme === 'dark' ? 'vs-dark' : 'vs',
      fontSize: settings?.fontSize || 14,
      tabSize: settings?.tabSize || 2,
      lineNumbers: settings?.showLineNumbers ? 'on' : 'off',
      minimap: {
        enabled: settings?.performanceMode !== 'performance'
      },
    });
  }, [settings]);

  // Handle file changes
  useEffect(() => {
    if (!editorRef.current || !currentFileName) return;

    // Determine language from file extension
    const extension = currentFileName.split('.').pop()?.toLowerCase();
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
    const language = languageMap[extension || ''] || 'plaintext';

    // Create or update model
    const uri = monaco.Uri.parse(`file:///${currentFileName}`);
    let model = monaco.editor.getModel(uri);
    
    if (!model) {
      model = monaco.editor.createModel(importedContent || '', language, uri);
    } else {
      // Update existing model
      if (importedContent !== undefined && importedContent !== model.getValue()) {
        model.setValue(importedContent);
      }
      monaco.editor.setModelLanguage(model, language);
    }
    
    currentModelRef.current = model;
    editorRef.current.setModel(model);
    
    // Request sync from server
    websocketService.requestFileSync(currentFileName);
    
  }, [currentFileName, importedContent]);

  // Handle remote edits
  useEffect(() => {
    const handleRemoteEdit = (edit: EditorEdit) => {
      if (!editorRef.current || !currentModelRef.current) return;
      if (edit.filePath !== currentFileName) return; // Not for current file
      
      setIsApplyingRemote(true);
      
      try {
        const model = currentModelRef.current;
        const startPos = model.getPositionAt(edit.diff.start);
        const endPos = model.getPositionAt(edit.diff.end);
        
        const range = new monaco.Range(
          startPos.lineNumber,
          startPos.column,
          endPos.lineNumber,
          endPos.column
        );
        
        // Apply the edit
        model.pushEditOperations(
          [],
          [{
            range: range,
            text: edit.diff.text,
            forceMoveMarkers: true
          }],
          () => null
        );
        
        // Optionally show remote cursor
        if (edit.cursor) {
          // Could add decoration for remote cursor here
        }
      } finally {
        setIsApplyingRemote(false);
      }
    };
    
    const handleEditorSync = (sync: EditorSync) => {
      if (!editorRef.current || sync.filePath !== currentFileName) return;
      
      setIsApplyingRemote(true);
      
      try {
        const model = currentModelRef.current;
        if (model && model.getValue() !== sync.content) {
          model.setValue(sync.content);
        }
        
        // Show remote cursors if any
        if (sync.cursors) {
          // Could add decorations for remote cursors here
        }
      } finally {
        setIsApplyingRemote(false);
      }
    };
    
    websocketService.on('editor_edit', handleRemoteEdit);
    websocketService.on('editor_sync', handleEditorSync);
    
    return () => {
      websocketService.off('editor_edit');
      websocketService.off('editor_sync');
    };
  }, [currentFileName]);

  // Clear function
  const clearCode = useCallback(() => {
    if (editorRef.current && currentModelRef.current) {
      currentModelRef.current.setValue('');
      setHasUnsavedChanges(false);
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
      console.error('Failed to copy code:', err);
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

  const handleSave = async () => {
    if (!currentFileName || !hasUnsavedChanges) return;
    
    setIsSaving(true);
    
    try {
      // In a real implementation, this would trigger a save to the backend
      // For now, we just mark as saved
      setHasUnsavedChanges(false);
      
      // Auto-format on save if enabled
      if (editorRef.current) {
        await editorRef.current.getAction('editor.action.formatDocument')?.run();
      }
    } finally {
      setIsSaving(false);
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 's') {
          e.preventDefault();
          handleSave();
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [hasUnsavedChanges, currentFileName]);

  return (
    <div className="h-full bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-yellow-400/20 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex items-center gap-4">
          <h2 className="text-yellow-400 font-semibold text-lg">Code Editor</h2>
          {currentFileName && (
            <span className="text-gray-400 text-sm font-mono bg-gray-800 px-2 py-1 rounded flex items-center gap-2">
              {currentFileName}
              {hasUnsavedChanges && (
                <span className="w-2 h-2 bg-yellow-400 rounded-full" title="Unsaved changes" />
              )}
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={handleSave}
            disabled={!hasUnsavedChanges || isSaving}
            className={`flex items-center gap-2 px-3 py-1 transition-colors ${
              !hasUnsavedChanges
                ? 'text-gray-600 cursor-not-allowed'
                : 'text-gray-400 hover:text-yellow-400'
            }`}
            title="Save file (Ctrl+S)"
          >
            {isSaving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            <span className="text-sm">Save</span>
          </button>
          
          <button 
            onClick={handleCopy}
            disabled={!currentModelRef.current?.getValue()?.trim()}
            className={`flex items-center gap-2 px-3 py-1 transition-colors ${
              copySuccess 
                ? 'text-green-400' 
                : !currentModelRef.current?.getValue()?.trim()
                ? 'text-gray-600 cursor-not-allowed'
                : 'text-gray-400 hover:text-yellow-400'
            }`}
            title={copySuccess ? 'Copied!' : 'Copy code to clipboard'}
          >
            <Copy className="w-4 h-4" />
            <span className="text-sm">{copySuccess ? 'Copied!' : 'Copy'}</span>
          </button>
          
          <button 
            onClick={handleDownload}
            disabled={!currentModelRef.current?.getValue()?.trim()}
            className={`flex items-center gap-2 px-3 py-1 transition-colors ${
              !currentModelRef.current?.getValue()?.trim()
                ? 'text-gray-600 cursor-not-allowed'
                : 'text-gray-400 hover:text-yellow-400'
            }`}
            title="Download code as file"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm">Download</span>
          </button>
        </div>
      </div>

      {/* Editor Container */}
      <div className="flex-1 overflow-hidden">
        <div ref={containerRef} className="h-full w-full" />
      </div>
    </div>
  );
};

export default MonacoEditor; 