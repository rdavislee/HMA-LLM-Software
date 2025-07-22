import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { SyntaxHighlightedEditor } from './SyntaxHighlightedEditor';
import { 
  Copy, 
  Download, 
  Play,
  MoreHorizontal,
  X,
  Code
} from 'lucide-react';

interface CodeFile {
  id: string;
  name: string;
  language: string;
  code: string;
  isActive: boolean;
}

interface CodeEditorProps {
  currentPhase?: 'spec' | 'test' | 'impl';
  selectedFile?: {
    path: string;
    content: string;
    language?: string;
  } | null;
}

export function CodeEditor({ currentPhase = 'spec', selectedFile }: CodeEditorProps) {
  const [activeTab, setActiveTab] = useState('');
  const [codeFiles, setCodeFiles] = useState<CodeFile[]>([]);

  const handleCloseTab = (fileId: string) => {
    const updatedFiles = codeFiles.filter(file => file.id !== fileId);
    setCodeFiles(updatedFiles);
    
    // If we closed the active tab, activate the first remaining tab
    if (activeTab === fileId && updatedFiles.length > 0) {
      setActiveTab(updatedFiles[0]?.id || '');
    } else if (updatedFiles.length === 0) {
      setActiveTab('');
    }
  };

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + W to close active tab
      if ((e.ctrlKey || e.metaKey) && e.key === 'w') {
        e.preventDefault();
        if (activeTab) {
          handleCloseTab(activeTab);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab, codeFiles]);

  // Handle selected file from FileTree
  useEffect(() => {
    if (selectedFile && selectedFile.content) {
      const fileName = selectedFile.path.split('/').pop() || 'untitled';
      const fileId = `file-${selectedFile.path}`;
      
      // Check if file is already open
      const existingFile = codeFiles.find(f => f.id === fileId);
      if (!existingFile) {
        // Add new file to tabs
        setCodeFiles(prev => [...prev, {
          id: fileId,
          name: fileName,
          language: selectedFile.language || 'plaintext',
          code: selectedFile.content,
          isActive: true
        }]);
      }
      
      // Switch to the file tab
      setActiveTab(fileId);
    }
  }, [selectedFile, codeFiles]);

  const handleCodeChange = (fileId: string, newCode: string) => {
    setCodeFiles(prev => prev.map(file => 
      file.id === fileId ? { ...file, code: newCode } : file
    ));
  };

  const handleCopyCode = () => {
    const activeFile = codeFiles.find(file => file.id === activeTab);
    if (activeFile) {
      navigator.clipboard.writeText(activeFile.code);
    }
  };

  const handleDownload = () => {
    const activeFile = codeFiles.find(file => file.id === activeTab);
    if (activeFile) {
      const blob = new Blob([activeFile.code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = activeFile.name;
      a.click();
      URL.revokeObjectURL(url);
    }
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

  const activeFile = codeFiles.find(file => file.id === activeTab);

  if (codeFiles.length === 0) {
    return (
      <div className="h-full flex items-center justify-center bg-[#1e1e1e]">
        <div className="text-center text-muted-foreground px-8">
          <Code className="h-12 w-12 mx-auto mb-4 opacity-30" />
          <p className="text-body mb-2">No files open</p>
          <p className="text-sm mb-4">Select a file from the file tree or import a project to start editing</p>
          <div className="text-xs space-y-1">
            <p className="opacity-60">Keyboard shortcuts:</p>
            <p className="font-mono opacity-50">Ctrl/Cmd + W - Close active tab</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-[#1e1e1e]">
      {/* Header with cleaner file tabs and action buttons */}
      <div className="p-4 border-b border-border bg-card">
        <div className="flex items-center justify-between">
          {/* Cleaner File Tabs */}
          <div className="flex gap-0.5">
            {codeFiles.map((file) => (
              <div
                key={file.id}
                className="relative flex items-center group"
              >
                {/* Phase-colored underline for active tab */}
                {activeTab === file.id && (
                  <div className={`absolute bottom-0 left-0 right-0 h-0.5 ${getPhaseColor(currentPhase)} rounded-full`} />
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
                    minWidth: '120px'
                  }}
                >
                  {/* Clickable tab name area */}
                  <button
                    onClick={() => setActiveTab(file.id)}
                    className={`flex-1 px-3 py-2 text-left truncate transition-colors ${
                      activeTab === file.id ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    {file.name}
                  </button>
                  
                  {/* Separate close button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCloseTab(file.id);
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
          
          {/* Action buttons */}
          <div className="flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="sm" 
              className="minimalist-button p-1.5"
              onClick={handleCopyCode}
            >
              <Copy className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              className="minimalist-button p-1.5"
              onClick={handleDownload}
            >
              <Download className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              className="minimalist-button p-1.5"
            >
              <Play className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              className="minimalist-button p-1.5"
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Code Content with Shiki Syntax Highlighting */}
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