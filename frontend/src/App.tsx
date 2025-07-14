import { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import ChatPanel from '../components/chat/ChatPanel';
import MonacoEditor from '../components/editor/MonacoEditor';
import FileTree from '../components/filetree/FileStructure';
import GitPanel from '../components/git/GitPanel';
import InteractiveTerminal from '../components/editor/Terminal';
import { Folder, GitBranch } from 'lucide-react';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import websocketService, { 
  CodeStream, 
  FileTreeUpdate, 
  ProjectStatus, 
  GitStatus,
  ProjectInitStatus
} from './services/websocket';
import { Settings, FileNode, ImportedFile, ProjectInitializationState, Language, ChatSession, ChatMessage as Message } from './types';
import { useSocketEvent } from './hooks/useSocketEvent';
import { chatStorage } from './services/chatStorage';

function App() {
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

  // Chat session state
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<Message[]>([]);

  // Generate a unique session ID
  const generateSessionId = () => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Save current session to history
  const saveCurrentSession = useCallback(async () => {
    if (!currentSessionId || chatMessages.length === 0) return;

    const session: ChatSession = {
      id: currentSessionId,
      title: `Chat ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`,
      createdAt: new Date(),
      lastModified: new Date(),
      messages: chatMessages,
      projectFiles: importedFiles,
      currentFile: currentFile,
      projectInitState: projectInitState.isActive ? projectInitState : undefined
    };

    try {
      await chatStorage.saveChatSession(session);
    } catch (error) {
      console.error('Error saving chat session:', error);
    }
  }, [currentSessionId, chatMessages, importedFiles, currentFile, projectInitState]);

  // Create a new chat session
  const startNewSession = useCallback(() => {
    const newSessionId = generateSessionId();
    setCurrentSessionId(newSessionId);
    setChatMessages([]);
  }, []);

  // Load a chat session from history
  const loadChatSession = useCallback(async (session: ChatSession) => {
    try {
      // Save current session first if it has content
      await saveCurrentSession();

      // Load the selected session
      setCurrentSessionId(session.id);
      setChatMessages(session.messages);
      setImportedFiles(session.projectFiles);
      setCurrentFile(session.currentFile || null);
      
      if (session.projectInitState) {
        setProjectInitState(session.projectInitState);
      } else {
        setProjectInitState({
          isActive: false,
          phase: null,
          phaseTitle: null,
          status: null,
          requiresApproval: false
        });
      }

      // Set as current session
      await chatStorage.setCurrentSession(session.id);
    } catch (error) {
      console.error('Error loading chat session:', error);
    }
  }, [saveCurrentSession]);

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

  // Initialize chat session on app start
  useEffect(() => {
    if (!currentSessionId) {
      startNewSession();
    }
  }, [currentSessionId, startNewSession]);

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
    // Save current session before starting new one
    if (currentSessionId && chatMessages.length > 0) {
      saveCurrentSession();
    }
    
    // Start new session
    startNewSession();
    
    // Clear project state
    setImportedFiles([]);
    setProjectFiles([]);
    setCurrentFile(null);
    clearCodeEditor?.();
    setProjectInitState({
      isActive: false,
      phase: null,
      phaseTitle: null,
      status: null,
      requiresApproval: false
    });
    
    // Clear project on backend
    websocketService.newChat();
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
    <div className="h-screen text-white flex flex-col overflow-hidden" style={{ backgroundColor: '#1F1F1F', fontFamily: '"Inter", system-ui, sans-serif' }}>
      {/* Header */}
      <Header 
        onImportClick={handleImportClick}
        onNewProjectClick={() => {}}
        onSettingsChange={handleSettingsChange}
        onProjectImport={handleProjectImport}
        onProjectStart={handleProjectStart}
        onClearProject={handleClearProject}
        onChatHistorySelect={loadChatSession}
        hasProjectFiles={importedFiles.length > 0 || projectFiles.length > 0}
        connectionStatus={connectionStatus}
      />

      {/* Main Content with Padding */}
      <div className="flex-1 flex overflow-hidden p-4 gap-4">
        {/* Chat Panel - Positioned at 7/20 screen width */}
        <div className="flex flex-col rounded-lg border border-amber-400/20" style={{ width: '35%', backgroundColor: '#1F1F1F' }}>
          <ChatPanel 
            isConnected={connectionStatus === 'connected'}
            onNewChat={handleNewChat}
            onProjectStart={handleProjectStart}
            projectInitState={projectInitState}
            messages={chatMessages}
            onMessagesChange={setChatMessages}
          />
        </div>

        {/* Right Section - Files, Code, and Terminal */}
        <div className="flex-1 flex flex-col overflow-hidden gap-0">
          {/* Top Section - File Tree and Code Panel */}
          <div className="flex-1 flex overflow-hidden">
            {/* Sidebar with Tabs */}
            <div className="w-80 min-w-0 flex flex-col rounded-tl-lg border-l border-t border-b border-r border-amber-400/20" style={{ backgroundColor: '#1F1F1F' }}>
              {/* Sidebar Tabs */}
              <div className="flex border-b border-amber-400/20 rounded-tl-lg" style={{ backgroundColor: '#1F1F1F' }}>
                <button
                  onClick={() => setActiveSidebarTab('files')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors rounded-tl-lg ${
                    activeSidebarTab === 'files'
                      ? 'text-amber-400 border-b-2 border-amber-400 bg-amber-400/5'
                      : 'text-gray-400 hover:text-amber-400 hover:bg-amber-400/5'
                  }`}
                >
                  <Folder className="w-4 h-4" />
                  Files
                </button>
                <button
                  onClick={() => setActiveSidebarTab('git')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                    activeSidebarTab === 'git'
                      ? 'text-amber-400 border-b-2 border-amber-400 bg-amber-400/5'
                      : 'text-gray-400 hover:text-amber-400 hover:bg-amber-400/5'
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
            </div>

            {/* Code Panel */}
            <div className="flex-1 flex flex-col overflow-hidden rounded-tr-lg border-t border-r border-amber-400/20" style={{ backgroundColor: '#1F1F1F' }}>
              <div className="flex-1 overflow-hidden rounded-tr-lg">
                <MonacoEditor 
                  onClearCode={(clearFn) => setClearCodeEditor(() => clearFn)} 
                  settings={settings}
                  importedContent={currentFile?.content}
                  currentFileName={currentFile?.name}
                  projectId={projectStatus?.projectId || 'default'}
                />
              </div>
            </div>
          </div>
          
          {/* Terminal Section - Full Width with Divider */}
          <div className="flex-shrink-0">
            {/* Divider */}
            <div className="border-t border-amber-400/20"></div>
            
            {/* Terminal */}
            <div className="rounded-b-lg border-l border-r border-b border-amber-400/20 overflow-hidden" style={{ backgroundColor: '#1F1F1F' }}>
              <InteractiveTerminal 
                projectId={projectStatus?.projectId || 'default'}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
