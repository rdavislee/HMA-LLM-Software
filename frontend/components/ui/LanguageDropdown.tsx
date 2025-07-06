import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Code } from 'lucide-react';
import { Language } from '../../src/types';

interface LanguageDropdownProps {
    defaultLanguage?: string;
    onLanguageChange?: (language: Language) => void;
}

const LanguageDropdown: React.FC<LanguageDropdownProps> = ({
    defaultLanguage,
    onLanguageChange
}) => {
    const [ isOpen, setIsOpen ] = useState(false);
    const [ selectedLanguage, setSelectedLanguage ] = useState(defaultLanguage || '');
    const dropdownRef = useRef<HTMLDivElement>(null);

    const languages: Language[] = [
        { code: 'javascript', name: 'JavaScript', extension: '.js' },
        { code: 'typescript', name: 'TypeScript', extension: '.ts' },
        { code: 'python', name: 'Python', extension: '.py' },
        { code: 'java', name: 'Java', extension: '.java' },
        { code: 'csharp', name: 'C#', extension: '.cs' },
        { code: 'cpp', name: 'C++', extension: '.cpp' },
        { code: 'html', name: 'HTML', extension: '.html' },
        { code: 'css', name: 'CSS', extension: '.css' },
        { code: 'react', name: 'React', extension: '.jsx' },
        { code: 'vue', name: 'Vue.js', extension: '.vue' },
        { code: 'php', name: 'PHP', extension: '.php' },
        { code: 'ruby', name: 'Ruby', extension: '.rb' },
        { code: 'go', name: 'Go', extension: '.go' },
        { code: 'rust', name: 'Rust', extension: '.rs' },
        { code: 'swift', name: 'Swift', extension: '.swift' },
        { code: 'kotlin', name: 'Kotlin', extension: '.kt' }
      ];

      const currentLanguage = languages.find(lang => lang.code === selectedLanguage);

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
            className={`flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 border rounded-lg transition-colors text-sm w-full ${
              !currentLanguage ? 'border-gray-600 text-gray-500' : 'border-yellow-400/20 text-gray-300'
            }`}
          >
            <Code className="w-4 h-4 text-gray-400" />
            <span className="flex-1 text-left">
              {currentLanguage ? currentLanguage.name : 'Select a programming language...'}
            </span>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${
              isOpen ? 'rotate-180' : ''
            }`} />
          </button>
    
          {isOpen && (
            <div className="absolute top-full left-0 mt-2 w-full bg-gray-800 border border-yellow-400/20 rounded-lg shadow-xl z-50 max-h-80 overflow-y-auto">
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
                    <Code className="w-4 h-4 text-gray-400" />
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
