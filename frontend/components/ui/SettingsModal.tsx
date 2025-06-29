import React, { useState, useEffect } from 'react';
import { X, Sun, Moon, Monitor, RotateCcw, Keyboard, Zap, Palette } from 'lucide-react';
import Slider from './Slider';

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

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSettingsChange: (settings: Settings) => void;
  currentSettings: Settings;
}

const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  onSettingsChange,
  currentSettings
}) => {
  const [settings, setSettings] = useState<Settings>(currentSettings);
  const [activeTab, setActiveTab] = useState<'appearance' | 'editor' | 'performance' | 'keyboard'>('appearance');

  const themes = [
    { key: 'light', icon: <Sun className="w-4 h-4" />, label: 'Light' },
    { key: 'dark', icon: <Moon className="w-4 h-4" />, label: 'Dark' },
    { key: 'system', icon: <Monitor className="w-4 h-4" />, label: 'System' }
  ];

  const accentColors = [
    { name: 'Yellow', value: '#facc15', class: 'bg-yellow-400' },
    { name: 'Blue', value: '#3b82f6', class: 'bg-blue-500' },
    { name: 'Green', value: '#10b981', class: 'bg-green-500' },
    { name: 'Purple', value: '#8b5cf6', class: 'bg-purple-500' },
    { name: 'Pink', value: '#ec4899', class: 'bg-pink-500' },
    { name: 'Orange', value: '#f97316', class: 'bg-orange-500' }
  ];

  const performanceModes = [
    { key: 'performance', label: 'Performance', description: 'Optimized for speed' },
    { key: 'balanced', label: 'Balanced', description: 'Good balance of speed and quality' },
    { key: 'quality', label: 'Quality', description: 'Best visual quality' }
  ];

  const keyboardShortcuts = [
    { key: 'Ctrl+N', description: 'New chat' },
    { key: 'Ctrl+S', description: 'Save file' },
    { key: 'Ctrl+Shift+P', description: 'Command palette' },
    { key: 'Ctrl+`', description: 'Toggle terminal' },
    { key: 'Ctrl+B', description: 'Toggle sidebar' },
    { key: 'F1', description: 'Open settings' }
  ];

  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    onSettingsChange(newSettings);
  };

  const resetToDefaults = () => {
    const defaultSettings: Settings = {
      theme: 'dark',
      tabSize: 2,
      showLineNumbers: true,
      showTimestamps: true,
      performanceMode: 'balanced',
      accentColor: '#facc15',
      fontSize: 14,
      autoSave: true
    };
    setSettings(defaultSettings);
    onSettingsChange(defaultSettings);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-yellow-400/20 rounded-lg w-full max-w-4xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-yellow-400/20">
          <h2 className="text-yellow-400 font-semibold text-xl">Settings</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-yellow-400/10 transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <div className="w-64 bg-gray-800/50 border-r border-yellow-400/20 p-4">
            <nav className="space-y-2">
              <button
                onClick={() => setActiveTab('appearance')}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  activeTab === 'appearance'
                    ? 'bg-yellow-400/10 text-yellow-400'
                    : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/5'
                }`}
              >
                <Palette className="w-4 h-4" />
                <span>Appearance</span>
              </button>
              <button
                onClick={() => setActiveTab('editor')}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  activeTab === 'editor'
                    ? 'bg-yellow-400/10 text-yellow-400'
                    : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/5'
                }`}
              >
                <Monitor className="w-4 h-4" />
                <span>Editor</span>
              </button>
              <button
                onClick={() => setActiveTab('performance')}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  activeTab === 'performance'
                    ? 'bg-yellow-400/10 text-yellow-400'
                    : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/5'
                }`}
              >
                <Zap className="w-4 h-4" />
                <span>Performance</span>
              </button>
              <button
                onClick={() => setActiveTab('keyboard')}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  activeTab === 'keyboard'
                    ? 'bg-yellow-400/10 text-yellow-400'
                    : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-400/5'
                }`}
              >
                <Keyboard className="w-4 h-4" />
                <span>Keyboard</span>
              </button>
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {activeTab === 'appearance' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-yellow-400 font-medium text-lg mb-4">Theme</h3>
                  <div className="grid grid-cols-3 gap-3">
                    {themes.map((theme) => (
                      <button
                        key={theme.key}
                        onClick={() => updateSetting('theme', theme.key as Settings['theme'])}
                        className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                          settings.theme === theme.key
                            ? 'border-yellow-400 bg-yellow-400/10 text-yellow-400'
                            : 'border-gray-700 text-gray-400 hover:border-yellow-400/50 hover:text-yellow-400'
                        }`}
                      >
                        {theme.icon}
                        <span>{theme.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-yellow-400 font-medium text-lg mb-4">Accent Color</h3>
                  <div className="grid grid-cols-6 gap-3">
                    {accentColors.map((color) => (
                      <button
                        key={color.value}
                        onClick={() => updateSetting('accentColor', color.value)}
                        className={`w-12 h-12 rounded-lg border-2 transition-all ${
                          settings.accentColor === color.value
                            ? 'border-yellow-400 scale-110'
                            : 'border-gray-700 hover:border-yellow-400/50'
                        }`}
                        style={{ backgroundColor: color.value }}
                        title={color.name}
                      />
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-yellow-400 font-medium text-lg mb-4">Font Size</h3>
                  <Slider
                    min={10}
                    max={20}
                    step={1}
                    value={settings.fontSize}
                    onChange={(value) => updateSetting('fontSize', value)}
                    label="Font Size"
                    showValue={true}
                  />
                </div>
              </div>
            )}

            {activeTab === 'editor' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-yellow-400 font-medium text-lg mb-4">Editor Settings</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-gray-300 text-sm mb-2 block">Tab Size</label>
                      <select
                        value={settings.tabSize}
                        onChange={(e) => updateSetting('tabSize', parseInt(e.target.value))}
                        className="w-full bg-gray-800 border border-yellow-400/20 rounded-lg px-3 py-2 text-gray-100 focus:outline-none focus:border-yellow-400"
                      >
                        <option value={2}>2 spaces</option>
                        <option value={4}>4 spaces</option>
                        <option value={8}>8 spaces</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <label className="text-gray-300 text-sm">Show Line Numbers</label>
                        <p className="text-gray-500 text-xs">Display line numbers in the code editor</p>
                      </div>
                      <button
                        onClick={() => updateSetting('showLineNumbers', !settings.showLineNumbers)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.showLineNumbers ? 'bg-yellow-400' : 'bg-gray-700'
                        }`}
                      >
                        <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                          settings.showLineNumbers ? 'translate-x-6' : 'translate-x-1'
                        }`} />
                      </button>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <label className="text-gray-300 text-sm">Show Timestamps</label>
                        <p className="text-gray-500 text-xs">Display timestamps in chat messages</p>
                      </div>
                      <button
                        onClick={() => updateSetting('showTimestamps', !settings.showTimestamps)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.showTimestamps ? 'bg-yellow-400' : 'bg-gray-700'
                        }`}
                      >
                        <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                          settings.showTimestamps ? 'translate-x-6' : 'translate-x-1'
                        }`} />
                      </button>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <label className="text-gray-300 text-sm">Auto Save</label>
                        <p className="text-gray-500 text-xs">Automatically save changes</p>
                      </div>
                      <button
                        onClick={() => updateSetting('autoSave', !settings.autoSave)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.autoSave ? 'bg-yellow-400' : 'bg-gray-700'
                        }`}
                      >
                        <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                          settings.autoSave ? 'translate-x-6' : 'translate-x-1'
                        }`} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'performance' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-yellow-400 font-medium text-lg mb-4">Performance Mode</h3>
                  <div className="space-y-3">
                    {performanceModes.map((mode) => (
                      <button
                        key={mode.key}
                        onClick={() => updateSetting('performanceMode', mode.key as Settings['performanceMode'])}
                        className={`w-full flex items-center justify-between p-4 rounded-lg border transition-colors ${
                          settings.performanceMode === mode.key
                            ? 'border-yellow-400 bg-yellow-400/10 text-yellow-400'
                            : 'border-gray-700 text-gray-400 hover:border-yellow-400/50 hover:text-yellow-400'
                        }`}
                      >
                        <div className="text-left">
                          <div className="font-medium">{mode.label}</div>
                          <div className="text-sm opacity-75">{mode.description}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'keyboard' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-yellow-400 font-medium text-lg mb-4">Keyboard Shortcuts</h3>
                  <div className="space-y-3">
                    {keyboardShortcuts.map((shortcut) => (
                      <div key={shortcut.key} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                        <span className="text-gray-300">{shortcut.description}</span>
                        <kbd className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-sm font-mono">
                          {shortcut.key}
                        </kbd>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-yellow-400/20">
          <button
            onClick={resetToDefaults}
            className="flex items-center gap-2 px-4 py-2 text-gray-400 hover:text-yellow-400 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset to Defaults</span>
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-yellow-400 hover:bg-yellow-300 text-black rounded-lg transition-colors font-medium"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal; 
