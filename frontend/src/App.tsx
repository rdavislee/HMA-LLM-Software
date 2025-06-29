import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import ChatPanel from '../components/chat/ChatPanel';
import CodePanel from '../components/editor/CodePanel';
import FileTree from '../components/filetree/FileStructure';
import Terminal from '../components/editor/Terminal';
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

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

function App() {
  const [isChatCollapsed, setIsChatCollapsed] = useState(false);
  const [isFileTreeCollapsed, setIsFileTreeCollapsed] = useState(false);
  const [currentFile, setCurrentFile] = useState<{ name: string; content: string; language: string } | null>(null);
  const [clearCodeEditor, setClearCodeEditor] = useState<(() => void) | null>(null);
  const [importedFiles, setImportedFiles] = useState<ImportedFile[]>([]);
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
    
    // If there are files, load the first one into the code editor
    if (files.length > 0) {
      const firstFile = files[0];
      if (firstFile.content) {
        setCurrentFile({
          name: firstFile.name,
          content: firstFile.content,
          language: getLanguageFromExtension(firstFile.name)
        });
      }
    }
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
                  console.log('File selected:', filePath);
                  if (content) {
                    setCurrentFile({
                      name: filePath.split('/').pop() || 'Unknown',
                      content: content,
                      language: getLanguageFromExtension(filePath)
                    });
                  }
                }}
                importedFiles={importedFiles}
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
          <span className="text-yellow-400">● Ready</span>
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
