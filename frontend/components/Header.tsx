import React, { useState } from 'react';
import { Settings, User, Upload, Hexagon, Trash2, Rocket } from 'lucide-react';
import SettingsModal from './ui/SettingsModal';
import ImportModal from './ui/ImportModal';
import NewProjectModal from './ui/NewProjectModal';
import { Language, Settings as AppSettings, ImportedFile } from '../src/types';

interface HeaderProps {
  onSettingsClick?: () => void;
  onProfileClick?: () => void;
  onImportClick?: () => void;
  onNewProjectClick?: () => void;
  onSettingsChange?: (settings: AppSettings) => void;
  onProjectImport?: (files: ImportedFile[]) => void;
  onProjectStart?: (language: Language, prompt: string, projectName?: string) => void;
  onClearProject?: () => void;
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
  hasProjectFiles = false,
  connectionStatus = 'connecting'
}) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [isNewProjectOpen, setIsNewProjectOpen] = useState(false);
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
      <div className="h-14 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 border-b border-yellow-400/20 flex items-center px-6">
        {/* Left Section - Logo and Title */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Hexagon className="w-8 h-8 text-yellow-400 fill-yellow-400/20" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
              </div>
            </div>
            <h1 className="text-yellow-400 font-semibold text-lg">Hive</h1>
          </div>
        </div>

        {/* Right Section - Controls */}
        <div className="flex items-center gap-4 ml-auto">
          <button
            onClick={handleImportClick}
            className="flex items-center gap-2 px-3 py-2 bg-yellow-400 hover:bg-yellow-300 text-black rounded-lg transition-colors font-medium text-sm"
          >
            <Upload className="w-4 h-4" />
            <span className="hidden sm:inline">Import</span>
          </button>

          {/* Clear Project Button - only show when there are project files */}
          {hasProjectFiles && (
            <button
              onClick={handleClearProject}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors font-medium text-sm ${
                showClearConfirm
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white'
              }`}
              title={showClearConfirm ? 'Click again to confirm' : 'Clear current project'}
            >
              <Trash2 className="w-4 h-4" />
              <span className="hidden sm:inline">
                {showClearConfirm ? 'Confirm Clear' : 'Clear'}
              </span>
            </button>
          )}

          <button
            onClick={handleNewProjectClick}
            className="flex items-center gap-2 px-3 py-2 bg-yellow-400 hover:bg-yellow-300 text-black rounded-lg transition-colors font-medium text-sm"
          >
            <Rocket className="w-4 h-4" />
            <span className="hidden sm:inline">New Project</span>
          </button>

          <button
            onClick={handleSettingsClick}
            className="p-2 rounded-lg hover:bg-yellow-400/10 transition-colors group"
          >
            <Settings className="w-5 h-5 text-gray-400 group-hover:text-yellow-400" />
          </button>

          <button
            onClick={onProfileClick}
            className="flex items-center gap-2 p-2 rounded-lg hover:bg-yellow-400/10 transition-colors group"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-black" />
            </div>
            <span className="text-gray-300 group-hover:text-yellow-400 text-sm font-medium">Developer</span>
          </button>

          {/* Connection Status */}
          <div className="flex items-center gap-2 ml-2" title={getConnectionStatusText()}>
            <div className={`w-2 h-2 rounded-full ${getConnectionStatusColor()} ${connectionStatus !== 'disconnected' ? 'animate-pulse' : ''}`}></div>
            <span className="text-sm text-gray-400 hidden md:inline">{getConnectionStatusText()}</span>
          </div>
        </div>
      </div>

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
    </>
  );
};

export default Header;
