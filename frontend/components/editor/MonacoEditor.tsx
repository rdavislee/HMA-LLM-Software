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
      fontSize: settings?.fontSize || 14,
      tabSize: settings?.tabSize || 2,
      lineNumbers: settings?.showLineNumbers ? 'on' : 'off',
      minimap: { enabled: settings?.performanceMode !== 'performance' },
      automaticLayout: true,
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      formatOnPaste: true,
      formatOnType: true,
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
      fontSize: settings?.fontSize || 14,
      tabSize: settings?.tabSize || 2,
      lineNumbers: settings?.showLineNumbers ? 'on' : 'off',
      minimap: { enabled: settings?.performanceMode !== 'performance' },
    });
  }, [settings]);

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

  const handleSave = async () => {
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
  };

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
    <div className="h-full bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-yellow-400/20 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex items-center gap-4">
          <h2 className="text-yellow-400 font-semibold text-lg">Code Editor</h2>
          {currentFileName && (
            <span className="text-gray-400 text-sm font-mono bg-gray-800 px-2 py-1 rounded flex items-center gap-2">
              {currentFileName}
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={handleSave}
            disabled={saveStatus === 'saving' || !currentFileName}
            className={`flex items-center gap-2 px-3 py-1 transition-colors rounded-md ${
              !currentFileName || saveStatus === 'saving'
                ? 'text-gray-600 cursor-not-allowed'
                : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/10'
            }`}
            title="Save file (Ctrl+S)"
          >
            {getSaveButton()}
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