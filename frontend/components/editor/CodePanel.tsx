import React, { useState, useEffect, useCallback } from 'react';
import { Code, Copy, Download } from 'lucide-react';

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

interface CodePanelProps {
  onClearCode?: (clearFn: () => void) => void;
  settings?: Settings;
  importedContent?: string;
  currentFileName?: string;
}

const CodePanel: React.FC<CodePanelProps> = ({ 
  onClearCode, 
  settings, 
  importedContent,
  currentFileName 
}) => {
  const [codeContent, setCodeContent] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);

  // Update content when imported content changes
  useEffect(() => {
    if (importedContent) {
      setCodeContent(importedContent);
    }
  }, [importedContent]);

  const clearCode = useCallback(() => {
    setCodeContent('');
  }, []);

  useEffect(() => {
    if (onClearCode) {
      onClearCode(clearCode);
    }
  }, [onClearCode, clearCode]);

  const handleCopy = async () => {
    if (!codeContent.trim()) {
      return; // Don't copy if there's no content
    }

    try {
      await navigator.clipboard.writeText(codeContent);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error('Failed to copy code:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = codeContent;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const handleDownload = () => {
    if (!codeContent.trim()) {
      return; // Don't download if there's no content
    }

    // Use current file name if available, otherwise determine extension
    let filename = 'code.js';
    if (currentFileName) {
      filename = currentFileName;
    } else {
      // Determine file extension based on content or default to .js
      let extension = '.js';
      if (codeContent.includes('import React') || codeContent.includes('export default')) {
        extension = '.tsx';
      } else if (codeContent.includes('function') && codeContent.includes('=>')) {
        extension = '.js';
      } else if (codeContent.includes('interface') || codeContent.includes('type')) {
        extension = '.ts';
      }
      filename = `code${extension}`;
    }

    const blob = new Blob([codeContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Apply tab size to content
  const formatContentWithTabSize = (content: string) => {
    const tabSize = settings?.tabSize || 2;
    return content.replace(/\t/g, ' '.repeat(tabSize));
  };

  const formattedContent = formatContentWithTabSize(codeContent);

  return (
    <div className="h-full bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-yellow-400/20 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex items-center gap-4">
          <h2 className="text-yellow-400 font-semibold text-lg">Code Editor</h2>
          {currentFileName && (
            <span className="text-gray-400 text-sm font-mono bg-gray-800 px-2 py-1 rounded">
              {currentFileName}
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <button 
            onClick={handleCopy}
            disabled={!codeContent.trim()}
            className={`flex items-center gap-2 px-3 py-1 transition-colors ${
              copySuccess 
                ? 'text-green-400' 
                : !codeContent.trim()
                ? 'text-gray-600 cursor-not-allowed'
                : 'text-gray-400 hover:text-yellow-400'
            }`}
            title={copySuccess ? 'Copied!' : 'Copy code to clipboard'}
          >
            <Copy className="w-4 h-4" />
            <span className="text-sm">{copySuccess ? 'Copied!' : 'Copy'}</span>
          </button>
          <button 
            onClick={handleDownload}
            disabled={!codeContent.trim()}
            className={`flex items-center gap-2 px-3 py-1 transition-colors ${
              !codeContent.trim()
                ? 'text-gray-600 cursor-not-allowed'
                : 'text-gray-400 hover:text-yellow-400'
            }`}
            title="Download code as file"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm">Download</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto">
          <pre className="p-4 text-sm font-mono text-gray-300 leading-relaxed">
            <code className="whitespace-pre-wrap">
              {formattedContent ? (
                formattedContent.split('\n').map((line, index) => (
                  <div key={index} className="flex">
                    {settings?.showLineNumbers && (
                      <span className="text-gray-500 select-none w-12 text-right pr-4">
                        {index + 1}
                      </span>
                    )}
                    <span className="flex-1">
                      {line.split(/(import|from|const|function|return|interface|useState|React)/g).map((part, i) => (
                        <span
                          key={i}
                          className={
                            ['import', 'from', 'const', 'function', 'return', 'interface'].includes(part)
                              ? 'text-yellow-400'
                              : part === 'React' || part === 'useState'
                              ? 'text-blue-400'
                              : part.includes('"') || part.includes("'")
                              ? 'text-green-400'
                              : ''
                          }
                        >
                          {part}
                        </span>
                      ))}
                    </span>
                  </div>
                ))
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  <div className="text-center">
                    <Code className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No code to display</p>
                    <p className="text-sm">Start typing or import a file to begin</p>
                  </div>
                </div>
              )}
            </code>
          </pre>
        </div>
      </div>
    </div>
  );
};

export default CodePanel;
