import { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import ChatPanel from '../components/chat/ChatPanel';
import MonacoEditor from '../components/editor/MonacoEditor';
import FileTree from '../components/filetree/FileStructure';
import GitPanel from '../components/git/GitPanel';
import InteractiveTerminal from '../components/editor/Terminal';
import { PanelLeftClose, PanelLeftOpen, Folder, GitBranch } from 'lucide-react';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import websocketService, { 
  CodeStream, 
  FileTreeUpdate, 
  ProjectStatus, 
  GitStatus,
  ProjectInitStatus
} from './services/websocket';
import { Settings, FileNode, ImportedFile, ProjectInitializationState, Language } from './types';
import { useSocketEvent } from './hooks/useSocketEvent';

function App() {
  const [isChatCollapsed, setIsChatCollapsed] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [activeSidebarTab, setActiveSidebarTab] = useState<'files' | 'git'>('files');
  const [currentFile, setCurrentFile] = useState<{ name: string; content: string; language: string } | null>(null);
  const [clearCodeEditor, setClearCodeEditor] = useState<(() => void) | null>(null);
  const [importedFiles, setImportedFiles] = useState<ImportedFile[]>([]);
  const [projectFiles, setProjectFiles] = useState<FileNode[]>([]);
  const [projectStatus, setProjectStatus] = useState<ProjectStatus | null>(null);
  const [gitStatus, setGitStatus] = useState<{ branch: string; isDirty: boolean } | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('disconnected');
  
  // Project initialization state
  const [projectInitState, setProjectInitState] = useState<ProjectInitializationState>({
    isActive: false,
    phase: null,
    phaseTitle: null,
    status: null,
    requiresApproval: false
  });

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

  // Manage WebSocket connection lifecycle
  useEffect(() => {
    if (websocketService.getConnectionStatus() === 'disconnected') {
      websocketService.connect();
    }
  }, []);

  const handleConnectionStatus = useCallback(() => {
    setConnectionStatus(websocketService.getConnectionStatus());
  }, []);

  useSocketEvent('connected', handleConnectionStatus);
  useSocketEvent('disconnected', handleConnectionStatus);

  /* ---------- File tree manipulation callbacks ---------- */

  const createFile = useCallback((filePath: string, content: string) => {
    const parts = filePath.split('/');
    const fileName = parts.pop() || '';
    setProjectFiles((prev: FileNode[]) => {
      const newFiles = [...prev];
      let current: FileNode = { name: '', path: '', type: 'directory', children: newFiles };
      for (const part of parts) {
        let found = current.children?.find((f: FileNode) => f.name === part && f.type === 'directory');
        if (!found) {
          found = { name: part, path: parts.slice(0, parts.indexOf(part) + 1).join('/'), type: 'directory', children: [] };
          if (!current.children) current.children = [];
          current.children.push(found);
        }
        current = found;
      }
      if (!current.children) current.children = [];
      if (!current.children.find((f: FileNode) => f.name === fileName)) {
        current.children.push({ name: fileName, path: filePath, type: 'file', content });
      }
      return newFiles;
    });
  }, []);

  const createFolder = useCallback((folderPath: string) => {
    const parts = folderPath.split('/');
    setProjectFiles((prev: FileNode[]) => {
      const newFiles = [...prev];
      let current: FileNode = { name: '', path: '', type: 'directory', children: newFiles };
      for (const part of parts) {
        let found = current.children?.find((f: FileNode) => f.name === part && f.type === 'directory');
        if (!found) {
          found = { name: part, path: parts.slice(0, parts.indexOf(part) + 1).join('/'), type: 'directory', children: [] };
          if (!current.children) current.children = [];
          current.children.push(found);
        }
        current = found;
      }
      return newFiles;
    });
  }, []);

  const updateFileContent = useCallback((filePath: string, content: string) => {
    setProjectFiles((prev: FileNode[]) => {
      const mutate = (nodes: FileNode[]): FileNode[] => nodes.map(node => {
        if (node.path === filePath && node.type === 'file') return { ...node, content };
        if (node.children) return { ...node, children: mutate(node.children) };
        return node;
      });
      return mutate(prev);
    });

    setCurrentFile(prev => (prev && prev.name === filePath ? { ...prev, content } : prev));
  }, []);

  const deleteFileOrFolder = useCallback((path: string) => {
    setProjectFiles((prev: FileNode[]) => {
      const filter = (nodes: FileNode[]): FileNode[] => nodes.filter(node => {
        if (node.path === path) return false;
        if (node.children) node.children = filter(node.children);
        return true;
      });
      return filter(prev);
    });
    setCurrentFile(prev => (prev && prev.name === path ? null : prev));
  }, []);

  /* ---------- WebSocket setup effect ---------- */

  useEffect(() => {
    // Handle code streaming
    const handleCodeStream = (stream: CodeStream) => {
      if (stream.isComplete) {
        updateFileContent(stream.filePath, stream.content);
      }

      // If this is the currently selected file, update the editor
      setCurrentFile(prev => {
        if (prev && prev.name === stream.filePath) {
          const newContent = stream.isComplete 
            ? stream.content 
            : (prev.content || '') + stream.content;
          return { ...prev, content: newContent };
        }
        return prev;
      });
    };

    // Handle file tree updates
    const handleFileTreeUpdate = (update: FileTreeUpdate) => {
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
    };

    // Handle project status updates
    const handleProjectStatus = (status: ProjectStatus) => {
      setProjectStatus(status);
      
      // Clear imported files when project becomes active (files have been processed)
      if (status.status === 'active') {
        setImportedFiles([]);
      }
    };

    // Handle git status updates
    const handleGitStatus = (data: { status: GitStatus | null }) => {
      if (data.status) {
        setGitStatus({
          branch: data.status.current_branch,
          isDirty: data.status.is_dirty
        });
      }
    };

    // Handle project initialization status updates
    const handleProjectInitStatus = (status: ProjectInitStatus) => {
      setProjectInitState({
        isActive: true,
        phase: status.phase,
        phaseTitle: status.phaseTitle,
        status: status.status,
        projectId: status.projectId,
        projectPath: status.projectPath,
        requiresApproval: status.requiresApproval
      });
    };

    // Register listeners
    websocketService.on('code_stream', handleCodeStream);
    websocketService.on('file_tree_update', handleFileTreeUpdate);
    websocketService.on('project_status', handleProjectStatus);
    websocketService.on('git_status', handleGitStatus);
    websocketService.on('project_init_status', handleProjectInitStatus);

    // Cleanup
    return () => {
      websocketService.off('code_stream');
      websocketService.off('file_tree_update');
      websocketService.off('project_status');
      websocketService.off('git_status');
      websocketService.off('project_init_status');
    };
  }, [createFile, createFolder, updateFileContent, deleteFileOrFolder]);

  // Apply accent color changes
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--accent-color', settings.accentColor);
    
    // Generate hover color (slightly darker)
    const color = settings.accentColor;
    const darkerColor = color.replace(/^#/, '').match(/.{2}/g)?.map((hex: string) => {
      const num = parseInt(hex, 16);
      return Math.max(0, num - 20).toString(16).padStart(2, '0');
    }).join('');
    if (darkerColor) {
      root.style.setProperty('--accent-color-hover', `#${darkerColor}`);
    }
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
    // Here you would typically open a file dialog or import modal
  };

  const handleProjectImport = (files: ImportedFile[]) => {
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
    setCurrentFile(null);
    setProjectStatus(null);
  };

  const handleClearProject = () => {
    // Clear the code editor if the function is available
    if (clearCodeEditor) {
      clearCodeEditor();
    }
    
    // Clear all project state
    setProjectFiles([]);
    setImportedFiles([]);
    setCurrentFile(null);
    setProjectStatus(null);
    
    // Notify backend to clear project
    websocketService.clearProject();
  };

  const handleSaveFile = () => {
    // Here you would typically save the current file
  };

  const handleToggleTerminal = () => {
    // Here you would typically toggle the terminal visibility
  };

  const handleToggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  const handleToggleGitPanel = () => {
    // If sidebar is collapsed, expand it first
    if (isSidebarCollapsed) {
      setIsSidebarCollapsed(false);
    }
    // Switch to Git tab
    setActiveSidebarTab('git');
  };

  const handleOpenSettings = () => {
    // The settings modal is handled by the Header component
  };

  const handleCommandPalette = () => {
    // Here you would typically open a command palette
  };

  // Use keyboard shortcuts
  useKeyboardShortcuts({
    onNewChat: handleNewChat,
    onSaveFile: handleSaveFile,
    onToggleTerminal: handleToggleTerminal,
    onToggleSidebar: handleToggleSidebar,
    onToggleGitPanel: handleToggleGitPanel,
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

  // Handle project start
  const handleProjectStart = (language: Language, prompt: string, projectName?: string) => {
    // Start project initialization
    websocketService.startProjectInitialization(language.code, prompt, projectName);
    
    // Update UI state
    setProjectInitState({
      isActive: true,
      phase: 1,
      phaseTitle: 'Product Understanding',
      status: 'active',
      requiresApproval: false,
      selectedLanguage: language
    });
  };

  return (
    <div className="h-screen bg-black text-white flex flex-col overflow-hidden">
      {/* Header */}
      <Header 
        onSettingsClick={() => {}}
        onProfileClick={() => {}}
        onImportClick={handleImportClick}
        onNewProjectClick={() => {}}
        onSettingsChange={handleSettingsChange}
        onProjectImport={handleProjectImport}
        onProjectStart={handleProjectStart}
        onClearProject={handleClearProject}
        hasProjectFiles={projectFiles.length > 0 || importedFiles.length > 0}
        connectionStatus={connectionStatus}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel */}
        <div className={`transition-all duration-300 ${
          isChatCollapsed ? 'w-0' : 'w-1/3'
        } min-w-0 flex flex-col`}>
          {!isChatCollapsed && (
            <ChatPanel 
              isConnected={connectionStatus === 'connected'}
              onNewChat={handleNewChat}
              onProjectStart={handleProjectStart}
              projectInitState={projectInitState}
            />
          )}
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
          {/* Sidebar with Tabs */}
          <div className={`transition-all duration-300 ${
            isSidebarCollapsed ? 'w-0' : 'w-80'
          } min-w-0 flex flex-col`}>
            {!isSidebarCollapsed && (
              <>
                {/* Sidebar Tabs */}
                <div className="flex border-b border-yellow-400/20 bg-gray-900">
                  <button
                    onClick={() => setActiveSidebarTab('files')}
                    className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                      activeSidebarTab === 'files'
                        ? 'text-yellow-400 border-b-2 border-yellow-400 bg-yellow-400/5'
                        : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/5'
                    }`}
                  >
                    <Folder className="w-4 h-4" />
                    Files
                  </button>
                  <button
                    onClick={() => setActiveSidebarTab('git')}
                    className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                      activeSidebarTab === 'git'
                        ? 'text-yellow-400 border-b-2 border-yellow-400 bg-yellow-400/5'
                        : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/5'
                    }`}
                  >
                    <GitBranch className="w-4 h-4" />
                    Git
                  </button>
                </div>

                {/* Tab Content */}
                <div className="flex-1 overflow-hidden">
                  {activeSidebarTab === 'files' && (
                    <FileTree 
                      onFileSelect={(filePath, content) => {
                        if (content !== undefined) {
                          const language = getLanguageFromExtension(filePath);
                          
                          setCurrentFile({
                            name: filePath,
                            content: content,
                            language: language
                          });
                          
                          // Notify backend of file selection
                          websocketService.selectFile(filePath);
                        }
                      }}
                      importedFiles={importedFiles}
                      projectFiles={projectFiles}
                    />
                  )}

                  {activeSidebarTab === 'git' && (
                    <GitPanel 
                      isOpen={true}
                    />
                  )}
                </div>
              </>
            )}
          </div>

          {/* Sidebar Toggle */}
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="w-6 bg-gray-800 hover:bg-gray-700 border-r border-yellow-400/20 flex items-center justify-center transition-colors group"
          >
            {isSidebarCollapsed ? (
              <PanelLeftOpen className="w-4 h-4 text-yellow-400 group-hover:text-yellow-300" />
            ) : (
              <PanelLeftClose className="w-4 h-4 text-yellow-400 group-hover:text-yellow-300" />
            )}
          </button>

          {/* Code/Preview Panel */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-hidden">
              <MonacoEditor 
                onClearCode={(clearFn) => setClearCodeEditor(() => clearFn)} 
                settings={settings}
                importedContent={currentFile?.content}
                currentFileName={currentFile?.name}
                projectId={projectStatus?.projectId || 'default'}
              />
            </div>
            
            {/* Terminal */}
            <div className="flex-shrink-0">
              <InteractiveTerminal 
                projectId={projectStatus?.projectId || 'default'}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-6 bg-gray-900 border-t border-yellow-400/20 flex items-center justify-between px-4 text-xs">
        <div className="flex items-center gap-4">
          <span className="text-yellow-400">● {projectStatus?.status || 'Ready'}</span>
          {gitStatus && (
            <span className="text-gray-400 flex items-center gap-1">
              <GitBranch className="w-3 h-3" />
              {gitStatus.branch}
              {gitStatus.isDirty && <span className="text-yellow-400">*</span>}
            </span>
          )}
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
