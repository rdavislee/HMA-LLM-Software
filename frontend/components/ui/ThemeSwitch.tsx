import React, { useState, useEffect } from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';

type Theme = 'light' | 'dark' | 'system';

interface ThemeSwitchProps {
  defaultTheme?: Theme;
  onThemeChange?: (theme: Theme) => void;
}

const ThemeSwitch: React.FC<ThemeSwitchProps> = ({
  defaultTheme = 'dark',
  onThemeChange
}) => {
  const [currentTheme, setCurrentTheme] = useState<Theme>(defaultTheme);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
      setCurrentTheme(savedTheme);
      onThemeChange?.(savedTheme);
    }
  }, [onThemeChange]);

  const themes: { key: Theme; icon: React.ReactNode; label: string }[] = [
    { key: 'light', icon: <Sun className="w-4 h-4" />, label: 'Light' },
    { key: 'dark', icon: <Moon className="w-4 h-4" />, label: 'Dark' },
    { key: 'system', icon: <Monitor className="w-4 h-4" />, label: 'System' }
  ];

  const handleThemeChange = (theme: Theme) => {
    setCurrentTheme(theme);
    localStorage.setItem('theme', theme);
    onThemeChange?.(theme);
  };

  return (
    <div className="relative">
      <div className="flex items-center bg-gray-800 rounded-lg p-1">
        {themes.map(({ key, icon, label }) => (
          <button
            key={key}
            onClick={() => handleThemeChange(key)}
            className={`flex items-center gap-2 px-3 py-1 rounded transition-colors text-sm ${
              currentTheme === key
                ? 'bg-yellow-400 text-black'
                : 'text-gray-400 hover:text-yellow-400 hover:bg-gray-700'
            }`}
            title={label}
          >
            {icon}
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ThemeSwitch;
