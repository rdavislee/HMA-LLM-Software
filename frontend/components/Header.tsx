import React, { useState } from 'react';
import { Settings, User, Upload, Hexagon, Trash2, Rocket, Plus, History } from 'lucide-react';
import SettingsModal from './ui/SettingsModal';
import ImportModal from './ui/ImportModal';
import NewProjectModal from './ui/NewProjectModal';
import ChatHistoryModal from './ui/ChatHistoryModal';
import { ImportedFile, Language, ChatSession, Settings as AppSettings } from '../src/types';

interface HeaderProps {
  onSettingsClick?: () => void;
  onProfileClick?: () => void;
  onImportClick?: () => void;
  onNewProjectClick?: () => void;
  onSettingsChange?: (settings: AppSettings) => void;
  onProjectImport?: (files: ImportedFile[]) => void;
  onProjectStart?: (language: Language, prompt: string, projectName?: string) => void;
  onClearProject?: () => void;
  onChatHistorySelect?: (session: ChatSession) => void;
  hasProjectFiles?: boolean;
  connectionStatus?: 'connected' | 'connecting' | 'disconnected';
}

const Header: React.FC<HeaderProps> = ({
  onSettingsClick,
  onProfileClick,
  onImportClick,
  onNewProjectClick,
  onSettingsChange,
  onProjectImport,
  onProjectStart,
  onClearProject,
  onChatHistorySelect,
  hasProjectFiles = false,
  connectionStatus = 'connecting'
}) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [isNewProjectOpen, setIsNewProjectOpen] = useState(false);
  const [isChatHistoryOpen, setIsChatHistoryOpen] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [settings, setSettings] = useState<AppSettings>(() => {
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

  const handleSettingsChange = (newSettings: AppSettings) => {
    setSettings(newSettings);
    localStorage.setItem('hive-settings', JSON.stringify(newSettings));
    onSettingsChange?.(newSettings);
  };

  const handleSettingsClick = () => {
    setIsSettingsOpen(true);
    onSettingsClick?.();
  };

  const handleImportClick = () => {
    setIsImportOpen(true);
    onImportClick?.();
  };

  const handleNewProjectClick = () => {
    setIsNewProjectOpen(true);
    onNewProjectClick?.();
  };

  const handleChatHistoryClick = () => {
    setIsChatHistoryOpen(true);
  };

  const handleChatHistorySelect = (session: ChatSession) => {
    onChatHistorySelect?.(session);
  };

  const handleProjectImport = (files: ImportedFile[]) => {
    console.log('Importing project files:', files);
    onProjectImport?.(files);
  };

  const handleProjectStart = (language: Language, prompt: string, projectName?: string) => {
    onProjectStart?.(language, prompt, projectName);
  };

  const handleClearProject = () => {
    if (showClearConfirm) {
      onClearProject?.();
      setShowClearConfirm(false);
    } else {
      setShowClearConfirm(true);
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-400';
      case 'connecting': return 'bg-yellow-400';
      case 'disconnected': return 'bg-red-400';
    }
  };
  
  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting';
      case 'disconnected': return 'Disconnected';
    }
  };

  return (
    <>
      <header className="bg-gray-900 px-6 py-4 mt-2" style={{ backgroundColor: '#1F1F1F', fontFamily: '"Inter", system-ui, sans-serif' }}>
        <div className="flex items-center justify-between">
          {/* Left Section - Logo and Title */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-4">
              <div className="relative">
                {/* Three hexagons in triangle formation */}
                <div className="relative w-12 h-10">
                  {/* Top hexagon */}
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2">
                    <Hexagon className="w-6 h-6 text-amber-400 fill-amber-400/20" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></div>
                    </div>
                  </div>
                  
                  {/* Bottom left hexagon */}
                  <div className="absolute bottom-0 left-0">
                    <Hexagon className="w-6 h-6 text-amber-400 fill-amber-400/20" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" style={{ animationDelay: '0.33s' }}></div>
                    </div>
                  </div>
                  
                  {/* Bottom right hexagon */}
                  <div className="absolute bottom-0 right-0">
                    <Hexagon className="w-6 h-6 text-amber-400 fill-amber-400/20" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" style={{ animationDelay: '0.66s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
              <h1 className="text-amber-400 font-semibold text-3xl">Hive</h1>
            </div>
          </div>

          {/* Right Section - Controls */}
          <div className="flex items-center gap-4 ml-auto">
            <button
              onClick={handleChatHistoryClick}
              className="flex items-center justify-center w-10 h-10 bg-amber-400/10 hover:bg-amber-400/20 text-amber-400 rounded-lg transition-colors border border-amber-400/30"
              title="Chat History"
            >
              <History className="w-4 h-4" />
            </button>

            <button
              onClick={handleImportClick}
              className="flex items-center justify-center w-10 h-10 bg-amber-400/10 hover:bg-amber-400/20 text-amber-400 rounded-lg transition-colors border border-amber-400/30"
              title="Import Project"
            >
              <Upload className="w-4 h-4" />
            </button>

            {/* Clear Project Button - only show when there are project files */}
            {hasProjectFiles && (
              <button
                onClick={handleClearProject}
                className={`flex items-center justify-center w-10 h-10 rounded-lg transition-colors border ${
                  showClearConfirm
                    ? 'bg-red-500/20 hover:bg-red-500/30 text-red-400 border-red-400/30'
                    : 'bg-amber-400/10 hover:bg-amber-400/20 text-amber-400 border-amber-400/30'
                }`}
                title={showClearConfirm ? 'Click again to confirm' : 'Clear current project'}
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}

            <button
              onClick={handleNewProjectClick}
              className="flex items-center justify-center w-10 h-10 bg-amber-400/10 hover:bg-amber-400/20 text-amber-400 rounded-lg transition-colors border border-amber-400/30"
              title="New Project"
            >
              <Plus className="w-4 h-4" />
            </button>

            <button
              onClick={handleSettingsClick}
              className="flex items-center justify-center w-10 h-10 bg-amber-400/10 hover:bg-amber-400/20 text-amber-400 rounded-lg transition-colors border border-amber-400/30"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSettingsChange={handleSettingsChange}
        currentSettings={settings}
      />

      {/* Import Modal */}
      <ImportModal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        onImport={handleProjectImport}
      />

      {/* New Project Modal */}
      <NewProjectModal
        isOpen={isNewProjectOpen}
        onClose={() => setIsNewProjectOpen(false)}
        onStartProject={handleProjectStart}
      />

      {/* Chat History Modal */}
      <ChatHistoryModal
        isOpen={isChatHistoryOpen}
        onClose={() => setIsChatHistoryOpen(false)}
        onSelectChat={handleChatHistorySelect}
      />
    </>
  );
};

export default Header;
