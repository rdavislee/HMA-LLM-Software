import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import ChatPanel from '../components/chat/ChatPanel';
import CodePanel from '../components/editor/CodePanel';
import FileTree from '../components/filetree/FileStructure';
import Terminal from '../components/editor/Terminal';
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import websocketService, { CodeStream, FileTreeUpdate, ProjectStatus } from './services/websocket';

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

interface ImportedFile {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  content?: string;
}

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  content?: string;
  children?: FileNode[];
}

function App() {
  const [isChatCollapsed, setIsChatCollapsed] = useState(false);
  const [isFileTreeCollapsed, setIsFileTreeCollapsed] = useState(false);
  const [currentFile, setCurrentFile] = useState<{ name: string; content: string; language: string } | null>(null);
  const [clearCodeEditor, setClearCodeEditor] = useState<(() => void) | null>(null);
  const [importedFiles, setImportedFiles] = useState<ImportedFile[]>([]);
  const [projectFiles, setProjectFiles] = useState<FileNode[]>([]);
  const [streamingContent, setStreamingContent] = useState<Map<string, string>>(new Map());
  const [projectStatus, setProjectStatus] = useState<ProjectStatus | null>(null);
  const [settings, setSettings] = useState<Settings>(() => {
    // Load settings from localStorage
    const saved = localStorage.getItem('hive-settings');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        // Fallback to defaults if parsing fails
      }
    }
    return {
      theme: 'dark',
      tabSize: 2,
      showLineNumbers: true,
      showTimestamps: true,
      performanceMode: 'balanced',
      accentColor: '#facc15',
      fontSize: 14,
      autoSave: true
    };
  });

  // Set up WebSocket event listeners for real-time updates
  useEffect(() => {
    // Handle code streaming
    websocketService.on('code_stream', (stream: CodeStream) => {
      console.log('Code stream received:', stream);
      
      setStreamingContent(prev => {
        const newMap = new Map(prev);
        if (stream.isComplete) {
          // Final content, update the file tree
          updateFileContent(stream.filePath, stream.content);
          newMap.delete(stream.filePath);
        } else {
          // Accumulate streaming content
          const existing = newMap.get(stream.filePath) || '';
          newMap.set(stream.filePath, existing + stream.content);
        }
        return newMap;
      });

      // If this is the currently selected file, update the editor
      if (currentFile && stream.filePath === currentFile.name) {
        const content = stream.isComplete 
          ? stream.content 
          : (streamingContent.get(stream.filePath) || '') + stream.content;
        
        setCurrentFile(prev => prev ? {
          ...prev,
          content: content
        } : null);
      }
    });

    // Handle file tree updates
    websocketService.on('file_tree_update', (update: FileTreeUpdate) => {
      console.log('File tree update:', update);
      
      switch (update.action) {
        case 'create':
          if (update.fileType === 'file') {
            createFile(update.filePath, update.content || '');
          } else {
            createFolder(update.filePath);
          }
          break;
        case 'update':
          updateFileContent(update.filePath, update.content || '');
          break;
        case 'delete':
          deleteFileOrFolder(update.filePath);
          break;
      }
    });

    // Handle project status updates
    websocketService.on('project_status', (status: ProjectStatus) => {
      console.log('Project status:', status);
      setProjectStatus(status);
      
      // Clear imported files when project becomes active (files have been processed)
      if (status.status === 'active') {
        setImportedFiles([]);
      }
    });

    // Cleanup
    return () => {
      websocketService.off('code_stream');
      websocketService.off('file_tree_update');
      websocketService.off('project_status');
    };
  }, [currentFile, streamingContent]);

  // File tree manipulation functions
  const createFile = (filePath: string, content: string) => {
    const parts = filePath.split('/');
    const fileName = parts.pop() || '';
    
    setProjectFiles(prev => {
      const newFiles = [...prev];
      let current = { children: newFiles } as any;
      
      // Navigate to the parent directory
      for (const part of parts) {
        let found = current.children?.find((f: FileNode) => f.name === part && f.type === 'directory');
        if (!found) {
          // Create directory if it doesn't exist
          found = {
            name: part,
            path: parts.slice(0, parts.indexOf(part) + 1).join('/'),
            type: 'directory',
            children: []
          };
          current.children.push(found);
        }
        current = found;
      }
      
      // Add the file if it doesn't exist
      if (!current.children?.find((f: FileNode) => f.name === fileName)) {
        current.children.push({
          name: fileName,
          path: filePath,
          type: 'file',
          content: content
        });
      }
      
      return newFiles;
    });
  };

  const createFolder = (folderPath: string) => {
    const parts = folderPath.split('/');
    
    setProjectFiles(prev => {
      const newFiles = [...prev];
      let current = { children: newFiles } as any;
      
      for (const part of parts) {
        let found = current.children?.find((f: FileNode) => f.name === part && f.type === 'directory');
        if (!found) {
          found = {
            name: part,
            path: parts.slice(0, parts.indexOf(part) + 1).join('/'),
            type: 'directory',
            children: []
          };
          current.children.push(found);
        }
        current = found;
      }
      
      return newFiles;
    });
  };

  const updateFileContent = (filePath: string, content: string) => {
    setProjectFiles(prev => {
      const updateNode = (nodes: FileNode[]): FileNode[] => {
        return nodes.map(node => {
          if (node.path === filePath && node.type === 'file') {
            return { ...node, content };
          } else if (node.children) {
            return { ...node, children: updateNode(node.children) };
          }
          return node;
        });
      };
      
      return updateNode(prev);
    });

    // Update current file if it's the one being updated
    if (currentFile && filePath === currentFile.name) {
      setCurrentFile(prev => prev ? { ...prev, content } : null);
    }
  };

  const deleteFileOrFolder = (path: string) => {
    setProjectFiles(prev => {
      const deleteFromNodes = (nodes: FileNode[]): FileNode[] => {
        return nodes.filter(node => {
          if (node.path === path) {
            return false;
          }
          if (node.children) {
            node.children = deleteFromNodes(node.children);
          }
          return true;
        });
      };
      
      return deleteFromNodes(prev);
    });

    // Clear current file if it was deleted
    if (currentFile && path === currentFile.name) {
      setCurrentFile(null);
    }
  };

  // Apply accent color changes
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--accent-color', settings.accentColor);
    
    // Generate hover color (slightly darker)
    const color = settings.accentColor;
    const darkerColor = color.replace(/^#/, '').match(/.{2}/g)?.map(hex => {
      const num = parseInt(hex, 16);
      return Math.max(0, num - 20).toString(16).padStart(2, '0');
    }).join('');
    root.style.setProperty('--accent-color-hover', `#${darkerColor}`);
  }, [settings.accentColor]);

  // Apply performance mode
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('performance-mode-performance', 'performance-mode-quality');
    
    if (settings.performanceMode === 'performance') {
      root.classList.add('performance-mode-performance');
    } else if (settings.performanceMode === 'quality') {
      root.classList.add('performance-mode-quality');
    }
  }, [settings.performanceMode]);

  // Apply font size
  useEffect(() => {
    const root = document.documentElement;
    root.style.fontSize = `${settings.fontSize}px`;
  }, [settings.fontSize]);

  const handleImportClick = () => {
    console.log('Importing project...');
    // Here you would typically open a file dialog or import modal
  };

  const handleProjectImport = (files: ImportedFile[]) => {
    console.log('Project imported with files:', files);
    setImportedFiles(files);
    
    // Send to backend
    websocketService.importProject(files);
    
    // Don't clear imported files - let them be cleared when backend successfully processes them
  };

  const getLanguageFromExtension = (filename: string): string => {
    const extension = filename.split('.').pop()?.toLowerCase();
    const languageMap: { [key: string]: string } = {
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'html': 'html',
      'css': 'css',
      'scss': 'scss',
      'sass': 'sass',
      'json': 'json',
      'md': 'markdown',
      'txt': 'text',
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
    return languageMap[extension || ''] || 'text';
  };

  const handleNewChat = () => {
    // Clear the code editor if the function is available
    if (clearCodeEditor) {
      clearCodeEditor();
    }
    
    // Clear project files
    setProjectFiles([]);
    setStreamingContent(new Map());
    setCurrentFile(null);
    setProjectStatus(null);
  };

  const handleSaveFile = () => {
    console.log('Saving file...');
    // Here you would typically save the current file
  };

  const handleToggleTerminal = () => {
    console.log('Toggle terminal...');
    // Here you would typically toggle the terminal visibility
  };

  const handleToggleSidebar = () => {
    setIsFileTreeCollapsed(!isFileTreeCollapsed);
  };

  const handleOpenSettings = () => {
    console.log('Opening settings...');
    // The settings modal is handled by the Header component
  };

  const handleCommandPalette = () => {
    console.log('Opening command palette...');
    // Here you would typically open a command palette
  };

  // Use keyboard shortcuts
  useKeyboardShortcuts({
    onNewChat: handleNewChat,
    onSaveFile: handleSaveFile,
    onToggleTerminal: handleToggleTerminal,
    onToggleSidebar: handleToggleSidebar,
    onOpenSettings: handleOpenSettings,
    onCommandPalette: handleCommandPalette
  });

  const handleSettingsChange = (newSettings: Settings) => {
    setSettings(newSettings);
    // Apply theme changes
    if (newSettings.theme === 'light') {
      document.documentElement.classList.remove('dark');
    } else if (newSettings.theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      // System theme - check system preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  };

  // Calculate dynamic status bar data
  const getStatusBarData = () => {
    if (!currentFile) {
      return {
        lines: 0,
        characters: 0,
        language: 'No file selected',
        encoding: 'UTF-8',
        lineEnding: 'LF'
      };
    }
    
    const lines = currentFile.content.split('\n').length;
    const characters = currentFile.content.length;
    
    return {
      lines,
      characters,
      language: currentFile.language,
      encoding: 'UTF-8',
      lineEnding: 'LF'
    };
  };

  const statusData = getStatusBarData();

  return (
    <div className="h-screen bg-black text-white flex flex-col overflow-hidden">
      {/* Header */}
      <Header 
        onSettingsClick={() => console.log('Opening settings...')}
        onProfileClick={() => console.log('Profile clicked')}
        onImportClick={handleImportClick}
        onSettingsChange={handleSettingsChange}
        onProjectImport={handleProjectImport}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel */}
        <div className={`transition-all duration-300 ${
          isChatCollapsed ? 'w-0' : 'w-1/3'
        } min-w-0 flex flex-col`}>
          {!isChatCollapsed && <ChatPanel onNewChat={handleNewChat} settings={settings} />}
        </div>

        {/* Chat Toggle Button */}
        <button
          onClick={() => setIsChatCollapsed(!isChatCollapsed)}
          className="w-6 bg-gray-800 hover:bg-gray-700 border-r border-yellow-400/20 flex items-center justify-center transition-colors group"
        >
          {isChatCollapsed ? (
            <PanelLeftOpen className="w-4 h-4 text-yellow-400 group-hover:text-yellow-300" />
          ) : (
            <PanelLeftClose className="w-4 h-4 text-yellow-400 group-hover:text-yellow-300" />
          )}
        </button>

        {/* Right Panel - Code/Preview and File Tree */}
        <div className="flex-1 flex overflow-hidden">
          {/* File Tree */}
          <div className={`transition-all duration-300 ${
            isFileTreeCollapsed ? 'w-0' : 'w-64'
          } min-w-0`}>
            {!isFileTreeCollapsed && (
              <FileTree 
                onFileSelect={(filePath, content) => {
                  console.log('App: File selected:', filePath);
                  console.log('App: File content length:', content?.length || 0);
                  
                  if (content !== undefined) {
                    const fileName = filePath.split('/').pop() || 'Unknown';
                    const language = getLanguageFromExtension(filePath);
                    
                    setCurrentFile({
                      name: filePath,
                      content: content,
                      language: language
                    });
                    
                    // Notify backend of file selection
                    websocketService.selectFile(filePath);
                    
                    console.log('App: Set current file:', fileName, 'Language:', language);
                  } else {
                    console.warn('App: No content provided for file:', filePath);
                  }
                }}
                importedFiles={importedFiles}
                projectFiles={projectFiles}
              />
            )}
          </div>

          {/* File Tree Toggle */}
          <button
            onClick={() => setIsFileTreeCollapsed(!isFileTreeCollapsed)}
            className="w-6 bg-gray-800 hover:bg-gray-700 border-r border-yellow-400/20 flex items-center justify-center transition-colors group"
          >
            {isFileTreeCollapsed ? (
              <PanelLeftOpen className="w-4 h-4 text-yellow-400 group-hover:text-yellow-300" />
            ) : (
              <PanelLeftClose className="w-4 h-4 text-yellow-400 group-hover:text-yellow-300" />
            )}
          </button>

          {/* Code/Preview Panel */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-hidden">
              <CodePanel 
                onClearCode={(clearFn) => setClearCodeEditor(() => clearFn)} 
                settings={settings}
                importedContent={currentFile?.content}
                currentFileName={currentFile?.name}
              />
            </div>
            
            {/* Terminal */}
            <div className="flex-shrink-0">
              <Terminal 
                onFileTreeUpdate={() => {
                  // This would trigger a file tree refresh
                  console.log('File tree update triggered');
                }}
                onCodeEditorUpdate={(content) => {
                  // This would update the code editor content
                  console.log('Code editor update triggered');
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-6 bg-gray-900 border-t border-yellow-400/20 flex items-center justify-between px-4 text-xs">
        <div className="flex items-center gap-4">
          <span className="text-yellow-400">● {projectStatus?.status || 'Ready'}</span>
          <span className="text-gray-400">Lines: {statusData.lines}</span>
          <span className="text-gray-400">Characters: {statusData.characters.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-gray-400">{statusData.language}</span>
          <span className="text-gray-400">{statusData.encoding}</span>
          <span className="text-gray-400">{statusData.lineEnding}</span>
        </div>
      </div>
    </div>
  );
}

export default App;
