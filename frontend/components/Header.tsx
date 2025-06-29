import React, { useState } from 'react';
import { Settings, User, Upload, Hexagon } from 'lucide-react';
import LanguageDropdown from './ui/LanguageDropdown';
import SettingsModal from './ui/SettingsModal';
import ImportModal from './ui/ImportModal';

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

interface HeaderProps {
  onSettingsClick?: () => void;
  onProfileClick?: () => void;
  onImportClick?: () => void;
  onSettingsChange?: (settings: Settings) => void;
  onProjectImport?: (files: ImportedFile[]) => void;
}

const Header: React.FC<HeaderProps> = ({
  onSettingsClick,
  onProfileClick,
  onImportClick,
  onSettingsChange,
  onProjectImport
}) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isImportOpen, setIsImportOpen] = useState(false);
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

  const handleSettingsChange = (newSettings: Settings) => {
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

  const handleProjectImport = (files: ImportedFile[]) => {
    console.log('Importing project files:', files);
    onProjectImport?.(files);
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
          <LanguageDropdown />
          
          <div className="h-6 w-px bg-yellow-400/20"></div>
          
          <button
            onClick={handleImportClick}
            className="flex items-center gap-2 px-3 py-2 bg-yellow-400 hover:bg-yellow-300 text-black rounded-lg transition-colors font-medium text-sm"
          >
            <Upload className="w-4 h-4" />
            <span className="hidden sm:inline">Import</span>
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
          <div className="flex items-center gap-2 ml-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
            <span className="text-sm text-gray-400">Connected</span>
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
    </>
  );
};

export default Header;
