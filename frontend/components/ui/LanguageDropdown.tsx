import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Code } from 'lucide-react';

interface Language {
    code: string;
    name: string;
    icon: string;
    extension: string;
}

interface LanguageDropdownProps {
    defaultLanguage?: string;
    onLanguageChange?: (language: Language) => void;
}

const LanguageDropdown: React.FC<LanguageDropdownProps> = ({
    defaultLanguage = 'javascript',
    onLanguageChange
}) => {
    const [ isOpen, setIsOpen ] = useState(false);
    const [ selectedLanguage, setSelectedLanguage ] = useState(defaultLanguage);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const languages: Language[] = [
        { code: 'javascript', name: 'JavaScript', icon: '🟨', extension: '.js' },
        { code: 'typescript', name: 'TypeScript', icon: '🔷', extension: '.ts' },
        { code: 'python', name: 'Python', icon: '🐍', extension: '.py' },
        { code: 'java', name: 'Java', icon: '☕', extension: '.java' },
        { code: 'csharp', name: 'C#', icon: '🔵', extension: '.cs' },
        { code: 'cpp', name: 'C++', icon: '⚡', extension: '.cpp' },
        { code: 'html', name: 'HTML', icon: '🌐', extension: '.html' },
        { code: 'css', name: 'CSS', icon: '🎨', extension: '.css' },
        { code: 'react', name: 'React', icon: '⚛️', extension: '.jsx' },
        { code: 'vue', name: 'Vue.js', icon: '💚', extension: '.vue' },
        { code: 'php', name: 'PHP', icon: '🐘', extension: '.php' },
        { code: 'ruby', name: 'Ruby', icon: '💎', extension: '.rb' },
        { code: 'go', name: 'Go', icon: '🐹', extension: '.go' },
        { code: 'rust', name: 'Rust', icon: '🦀', extension: '.rs' },
        { code: 'swift', name: 'Swift', icon: '🍎', extension: '.swift' },
        { code: 'kotlin', name: 'Kotlin', icon: '🟣', extension: '.kt' }
      ];

      const currentLanguage = languages.find(lang => lang.code === selectedLanguage) || languages[0];

      useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
      }, []);

      const handleLanguageSelect = (language: Language) => {
        setSelectedLanguage(language.code);
        setIsOpen(false);
        onLanguageChange?.(language);
      };

      return (
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 border border-yellow-400/20 rounded-lg transition-colors text-sm"
          >
            <Code className="w-4 h-4 text-gray-400" />
            <span className="text-gray-300">{currentLanguage.icon}</span>
            <span className="hidden sm:inline text-gray-300">{currentLanguage.name}</span>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${
              isOpen ? 'rotate-180' : ''
            }`} />
          </button>
    
          {isOpen && (
            <div className="absolute top-full right-0 mt-2 w-56 bg-gray-800 border border-yellow-400/20 rounded-lg shadow-xl z-50 max-h-80 overflow-y-auto">
              <div className="p-2">
                <div className="px-3 py-2 text-xs font-medium text-yellow-400 uppercase tracking-wide border-b border-yellow-400/20 mb-2">
                  Programming Languages
                </div>
                {languages.map((language) => (
                  <button
                    key={language.code}
                    onClick={() => handleLanguageSelect(language)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-left ${
                      selectedLanguage === language.code
                        ? 'bg-yellow-400/10 text-yellow-400'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-yellow-400'
                    }`}
                  >
                    <span className="text-lg">{language.icon}</span>
                    <div className="flex-1">
                      <span className="text-sm font-medium">{language.name}</span>
                      <span className="text-xs text-gray-500 block">{language.extension}</span>
                    </div>
                    {selectedLanguage === language.code && (
                      <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      );
};

export default LanguageDropdown;
