import { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from './ui/button';
import { SyntaxHighlightedEditor } from './SyntaxHighlightedEditor';
import {
  Copy,
  Download,
  MoreHorizontal,
  X,
  Code,
} from 'lucide-react';

/* -------------------------------------------------------------------------- */
/*  Types                                                                     */
/* -------------------------------------------------------------------------- */

interface CodeFile {
  id: string;
  name: string;
  path: string;
  language: string;
  code: string;
}

interface CodeEditorProps {
  currentPhase?: 'spec' | 'test' | 'impl';
  selectedFile?: {
    path: string;
    content: string;
    language?: string;
  } | null;
}

/* -------------------------------------------------------------------------- */
/*  Component                                                                 */
/* -------------------------------------------------------------------------- */

export function CodeEditor({
  currentPhase = 'spec',
  selectedFile,
}: CodeEditorProps) {
  const [codeFiles, setCodeFiles] = useState<CodeFile[]>([]);
  const [activeTab, setActiveTab] = useState('');

  /* ──────────────────────────────────────────────────────────────────────── */
  /*  Add / focus file tabs                                                  */
  /* ──────────────────────────────────────────────────────────────────────── */
  useEffect(() => {
    if (!selectedFile) return;

    setCodeFiles((prev) => {
      const fileId = `file-${selectedFile.path}`;
      if (prev.some((f) => f.id === fileId)) return prev; // already open

      const fileName = selectedFile.path.split('/').pop() || 'untitled';
      return [
        ...prev,
        {
          id: fileId,
          name: fileName,
          path: selectedFile.path,
          language: selectedFile.language ?? 'plaintext',
          code: selectedFile.content,
        },
      ];
    });

    setActiveTab(`file-${selectedFile.path}`);
  }, [selectedFile]);

  /* ──────────────────────────────────────────────────────────────────────── */
  /*  Close tab                                                              */
  /* ──────────────────────────────────────────────────────────────────────── */
  const handleCloseTab = useCallback(
    (fileId: string) => {
      setCodeFiles((prev) => {
        const idx = prev.findIndex((f) => f.id === fileId);
        if (idx === -1) return prev;

        const nextTabs = [...prev.slice(0, idx), ...prev.slice(idx + 1)];

        // pick neighbour if we closed the active tab
        if (fileId === activeTab) {
          const neighbour = nextTabs[idx - 1] ?? nextTabs[idx] ?? null;
          setActiveTab(neighbour ? neighbour.id : '');
        }

        return nextTabs;
      });
    },
    [activeTab],
  );

  /* ──────────────────────────────────────────────────────────────────────── */
  /*  Keyboard shortcut (Ctrl/Cmd + W)                                       */
  /* ──────────────────────────────────────────────────────────────────────── */
  const activeTabRef = useRef(activeTab);
  useEffect(() => {
    activeTabRef.current = activeTab;
  }, [activeTab]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'w') {
        e.preventDefault();
        if (activeTabRef.current) handleCloseTab(activeTabRef.current);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleCloseTab]);

  /* ──────────────────────────────────────────────────────────────────────── */
  /*  Helpers                                                                */
  /* ──────────────────────────────────────────────────────────────────────── */
  const handleCodeChange = (fileId: string, newCode: string) => {
    setCodeFiles((prev) =>
      prev.map((file) => (file.id === fileId ? { ...file, code: newCode } : file)),
    );
  };

  const handleCopyCode = () => {
    const activeFile = codeFiles.find((f) => f.id === activeTab);
    if (activeFile) navigator.clipboard.writeText(activeFile.code);
  };

  const handleDownload = () => {
    const activeFile = codeFiles.find((f) => f.id === activeTab);
    if (!activeFile) return;

    const blob = new Blob([activeFile.code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = activeFile.name;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getPhaseColor = (phase: 'spec' | 'test' | 'impl') => {
    switch (phase) {
      case 'spec':
        return 'border-blue-500';
      case 'test':
        return 'border-yellow-500';
      case 'impl':
        return 'border-violet-500';
      default:
        return 'border-blue-500';
    }
  };

  const activeFile = codeFiles.find((f) => f.id === activeTab);

  /* ---------------------------------------------------------------------- */
  /*  Empty State                                                           */
  /* ---------------------------------------------------------------------- */
  if (codeFiles.length === 0) {
    return (
      <div className="h-full flex items-center justify-center bg-[#1e1e1e]">
        <div className="text-center text-muted-foreground px-8">
          <Code className="h-12 w-12 mx-auto mb-4 opacity-30" />
          <p className="text-body mb-2">No files open</p>
          <p className="text-sm">
            Select a file from the file tree or import a project to start editing
          </p>
        </div>
      </div>
    );
  }

  /* ---------------------------------------------------------------------- */
  /*  Main UI                                                               */
  /* ---------------------------------------------------------------------- */
  return (
    <div className="h-full flex flex-col bg-[#1e1e1e]">
      {/* Header */}
      <div className="p-4 border-b border-border bg-card min-h-[73px] flex items-center overflow-hidden">
        <div className="flex items-center w-full gap-4">
          {/* Tabs with scroll container */}
          <div 
            className="flex-1 min-w-0 overflow-x-auto"
            style={{
              scrollbarWidth: 'thin',
              scrollbarColor: 'rgba(255, 255, 255, 0.2) transparent',
            }}
          >
            <div className="flex gap-0.5 pr-2 w-max">
              {codeFiles.map((file) => (
                <div key={file.id} className="relative flex items-center group flex-shrink-0">
                  {/* Phase‑coloured underline */}
                  {activeTab === file.id && (
                    <div
                      className={`absolute bottom-0 left-0 right-0 h-0.5 ${getPhaseColor(
                        currentPhase,
                      )} rounded-full`}
                    />
                  )}

                  {/* Tab container */}
                  <div
                    className={`flex items-center rounded-md transition-all duration-200 ${
                      activeTab === file.id
                        ? 'bg-primary/10 border border-primary/20'
                        : 'bg-transparent border border-transparent hover:bg-muted/10'
                    }`}
                    style={{
                      fontFamily: 'Quicksand, sans-serif',
                      fontSize: '13px',
                      fontWeight: 500,
                      minWidth: '120px',
                    }}
                  >
                    {/* Clickable name */}
                    <button
                      onClick={() => setActiveTab(file.id)}
                      className={`flex-1 px-3 py-2 text-left truncate transition-colors ${
                        activeTab === file.id
                          ? 'text-primary'
                          : 'text-muted-foreground hover:text-foreground'
                      }`}
                    >
                      {file.name}
                    </button>

                    {/* Close button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        e.preventDefault();
                        handleCloseTab(file.id);
                      }}
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        e.preventDefault();
                      }}
                      className="p-1.5 mr-1 rounded hover:bg-destructive/20 hover:text-destructive transition-all duration-150 opacity-50 hover:opacity-100 focus:opacity-100"
                      title="Close file (Ctrl/Cmd + W)"
                      tabIndex={0}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Vertical separator */}
          <div className="h-8 w-px bg-border flex-shrink-0" />

          {/* Action buttons */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <Button
              variant="ghost"
              size="sm"
              className="minimalist-button p-1.5"
              onClick={handleCopyCode}
              title="Copy code"
            >
              <Copy className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="minimalist-button p-1.5"
              onClick={handleDownload}
              title="Download file"
            >
              <Download className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="minimalist-button p-1.5">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden bg-[#1e1e1e]">
        {activeFile && (
          <SyntaxHighlightedEditor
            value={activeFile.code}
            onChange={(newCode) => handleCodeChange(activeFile.id, newCode)}
            language={activeFile.language}
            placeholder="Start typing your code here..."
          />
        )}
      </div>
    </div>
  );
}
