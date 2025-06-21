import React, { useRef, useEffect } from 'react';
import type { Agent } from './AgentHierarchy';

interface CodeDisplayProps {
  selectedAgent: Agent | null;
  codeContent: string;
  streamingCode: string;
  isGenerating: boolean;
}

const CodeDisplay: React.FC<CodeDisplayProps> = ({
  selectedAgent,
  codeContent,
  streamingCode,
  isGenerating
}) => {
  const codeEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isGenerating) {
      codeEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [streamingCode, isGenerating]);

  const getLineNumbers = (content: string) => {
    const lines = content.split('\n');
    return lines.map((_, index) => index + 1);
  };

  const displayContent = isGenerating ? streamingCode : codeContent;
  const lineNumbers = getLineNumbers(displayContent || '');

  return (
    <div className="flex-1 bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-300">
            {selectedAgent ? `${selectedAgent.path}` : 'No file selected'}
          </span>
          {isGenerating && (
            <span className="text-xs text-blue-400 flex items-center gap-1">
              <span className="animate-pulse">●</span> Generating...
            </span>
          )}
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>{displayContent ? displayContent.split('\n').length : 0} lines</span>
          {selectedAgent?.type === 'coder' && (
            <span className="text-gray-600">Python</span>
          )}
        </div>
      </div>
      
      {/* Code Editor */}
      <div className="flex-1 overflow-auto relative">
        <div className="flex">
          {/* Line Numbers */}
          <div className="bg-gray-850 text-gray-600 text-sm font-mono p-4 pr-2 select-none">
            {displayContent && lineNumbers.map(num => (
              <div key={num} className="leading-6">{num}</div>
            ))}
          </div>
          
          {/* Code Content */}
          <div className="flex-1 p-4 pl-3 font-mono text-sm">
            <pre className="text-gray-300 whitespace-pre leading-6">
              {isGenerating ? (
                <span>
                  {streamingCode}
                  <span className="code-cursor bg-blue-400 text-blue-400">|</span>
                </span>
              ) : (
                displayContent || (
                  <span className="text-gray-600">
                    {selectedAgent?.type === 'coder' 
                      ? '# Code will appear here when generated...' 
                      : selectedAgent?.type === 'manager'
                      ? '# Manager agents delegate tasks to children...'
                      : '# Select a coder agent to generate code...'}
                  </span>
                )
              )}
            </pre>
            <div ref={codeEndRef} />
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-gray-850 border-t border-gray-700 px-4 py-1 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>{selectedAgent?.type || 'No agent'}</span>
          <span>UTF-8</span>
        </div>
        <div className="flex items-center gap-4">
          {isGenerating && <span>Writing...</span>}
          <span>LLM: Active</span>
        </div>
      </div>
    </div>
  );
};

export default CodeDisplay; 