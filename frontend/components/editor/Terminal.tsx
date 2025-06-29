import React, { useState, useRef, useEffect } from 'react';
import { Terminal as TerminalIcon, X, Minus, Square } from 'lucide-react';

interface TerminalLine {
  id: string;
  type: 'command' | 'output' | 'error' | 'system';
  content: string;
  timestamp: Date;
  isRunning?: boolean;
}

interface TerminalProps {
  onFileTreeUpdate?: () => void;
  onCodeEditorUpdate?: (content: string) => void;
}

const Terminal: React.FC<TerminalProps> = ({ onFileTreeUpdate, onCodeEditorUpdate }) => {
  const [lines, setLines] = useState<TerminalLine[]>([
    {
      id: '1',
      type: 'system',
      content: 'Welcome to Hive Terminal v1.0.0',
      timestamp: new Date()
    },
    {
      id: '2',
      type: 'system',
      content: 'Type "help" for available commands',
      timestamp: new Date()
    }
  ]);
  const [currentCommand, setCurrentCommand] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [currentWorkingDir, setCurrentWorkingDir] = useState('~');
  const [runningProcess, setRunningProcess] = useState<{ id: string; command: string } | null>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Security: Restricted commands that could be dangerous
  const RESTRICTED_COMMANDS = [
    'rm -rf', 'rm -r', 'rm -f', 'rm -rf /', 'rm -rf /*',
    'format', 'fdisk', 'mkfs', 'dd', 'shutdown', 'reboot',
    'sudo', 'su', 'chmod 777', 'chown root', 'passwd',
    'wget', 'curl', 'nc', 'telnet', 'ssh', 'scp'
  ];

  // Check if command is restricted
  const isCommandRestricted = (command: string): boolean => {
    const lowerCommand = command.toLowerCase();
    return RESTRICTED_COMMANDS.some(restricted => 
      lowerCommand.includes(restricted.toLowerCase())
    );
  };

  // Add a line to the terminal
  const addLine = (type: TerminalLine['type'], content: string, isRunning = false) => {
    const newLine: TerminalLine = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
      isRunning
    };
    setLines(prev => [...prev, newLine]);
  };

  // Execute a command using Node.js child_process
  const executeCommand = async (command: string): Promise<{ stdout: string; stderr: string; code: number }> => {
    return new Promise((resolve) => {
      // For now, we'll simulate command execution since we can't run real processes in the browser
      // In a real implementation, this would use a backend API or WebSocket connection
      
      setTimeout(() => {
        let stdout = '';
        let stderr = '';
        let code = 0;

        // Simulate different command responses
        if (command === 'pwd') {
          stdout = currentWorkingDir;
        } else if (command.startsWith('cd ')) {
          const newDir = command.substring(3).trim();
          if (newDir === '~' || newDir === '') {
            setCurrentWorkingDir('~');
            stdout = `Changed directory to: ~`;
          } else if (newDir === '..' && currentWorkingDir !== '~') {
            // Go up one directory
            const parts = currentWorkingDir.split('/');
            if (parts.length > 1) {
              parts.pop();
              const parentDir = parts.join('/') || '~';
              setCurrentWorkingDir(parentDir);
              stdout = `Changed directory to: ${parentDir}`;
            } else {
              setCurrentWorkingDir('~');
              stdout = `Changed directory to: ~`;
            }
          } else if (newDir && newDir !== '..') {
            // Navigate to new directory
            const fullPath = currentWorkingDir === '~' ? newDir : `${currentWorkingDir}/${newDir}`;
            setCurrentWorkingDir(fullPath);
            stdout = `Changed directory to: ${fullPath}`;
          } else {
            stderr = `cd: ${newDir}: No such file or directory`;
            code = 1;
          }
        } else if (command === 'ls' || command === 'dir') {
          stdout = 'src/  public/  node_modules/  package.json  vite.config.ts  tailwind.config.js';
        } else if (command === 'npm run dev') {
          stdout = '> dev server started at http://localhost:5173';
        } else if (command === 'npm install') {
          stdout = 'added 389 packages, and audited 390 packages in 25s';
        } else if (command === 'git status') {
          stdout = 'On branch main\nnothing to commit, working tree clean';
        } else if (command === 'help') {
          stdout = `Available commands:
- Navigation: cd, pwd, ls, dir
- Development: npm run dev, npm install, npm build
- Git: git status, git add, git commit, git log
- File operations: cat, touch, mkdir
- System: clear, help
- Long-running: npm run dev (use Ctrl+C to cancel)`;
        } else if (command === 'clear') {
          setLines([]);
          resolve({ stdout: '', stderr: '', code: 0 });
          return;
        } else {
          stdout = `Command executed: ${command}`;
        }

        resolve({ stdout, stderr, code });
      }, 100);
    });
  };

  const handleCommand = async (command: string) => {
    if (!command.trim()) return;

    // Check for restricted commands
    if (isCommandRestricted(command)) {
      addLine('error', `Command restricted for security: ${command}`);
      setCurrentCommand('');
      return;
    }

    // Add to command history
    setCommandHistory(prev => [...prev, command]);
    setHistoryIndex(-1);

    // Add command line
    addLine('command', `$ ${command}`);

    // Handle long-running commands
    if (command === 'npm run dev') {
      const processId = Date.now().toString();
      setRunningProcess({ id: processId, command });
      addLine('output', 'Starting development server...', true);
      
      // Simulate long-running process
      setTimeout(async () => {
        const result = await executeCommand(command);
        setRunningProcess(null);
        
        // Remove the running indicator line
        setLines(prev => prev.filter(line => !line.isRunning));
        
        if (result.stderr) {
          addLine('error', result.stderr);
        } else {
          addLine('output', result.stdout);
        }
        
        // Update file tree if needed
        onFileTreeUpdate?.();
      }, 2000);
    } else {
      // Regular command execution
      const result = await executeCommand(command);
      
      if (result.stderr) {
        addLine('error', result.stderr);
      } else if (result.stdout) {
        addLine('output', result.stdout);
      }
    }

    setCurrentCommand('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && currentCommand.trim()) {
      handleCommand(currentCommand.trim());
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIndex < commandHistory.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        setCurrentCommand(commandHistory[commandHistory.length - 1 - newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setCurrentCommand(commandHistory[commandHistory.length - 1 - newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setCurrentCommand('');
      }
    } else if (e.key === 'c' && e.ctrlKey && runningProcess) {
      e.preventDefault();
      // Cancel running process
      setRunningProcess(null);
      setLines(prev => prev.filter(line => !line.isRunning));
      addLine('system', `Process cancelled: ${runningProcess.command}`);
    }
  };

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [lines]);

  if (isMinimized) {
    return (
      <div className="bg-gray-900 border-t border-yellow-400/20 p-2">
        <button
          onClick={() => setIsMinimized(false)}
          className="flex items-center gap-2 text-yellow-400 hover:text-yellow-300 transition-colors"
        >
          <TerminalIcon className="w-4 h-4" />
          <span className="text-sm font-medium">
            Terminal {runningProcess ? '(running)' : '(minimized)'}
          </span>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 border-t border-yellow-400/20 flex flex-col h-64">
      {/* Header */}
      <div className="flex items-center justify-between p-2 border-b border-yellow-400/20 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-4 h-4 text-yellow-400" />
          <span className="text-yellow-400 font-medium text-sm">
            Terminal {runningProcess && <span className="text-green-400">●</span>}
          </span>
          <span className="text-gray-500 text-xs">({currentWorkingDir})</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsMinimized(true)}
            className="w-6 h-6 rounded hover:bg-yellow-400/20 flex items-center justify-center transition-colors"
          >
            <Minus className="w-3 h-3 text-gray-400" />
          </button>
          <button className="w-6 h-6 rounded hover:bg-yellow-400/20 flex items-center justify-center transition-colors">
            <Square className="w-3 h-3 text-gray-400" />
          </button>
          <button className="w-6 h-6 rounded hover:bg-red-500/20 flex items-center justify-center transition-colors">
            <X className="w-3 h-3 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Terminal Content */}
      <div 
        ref={terminalRef}
        className="flex-1 overflow-y-auto p-3 font-mono text-sm"
      >
        {lines.map((line) => (
          <div key={line.id} className={`mb-1 ${
            line.type === 'command' ? 'text-yellow-400' : 
            line.type === 'error' ? 'text-red-400' : 
            line.type === 'system' ? 'text-blue-400' :
            line.isRunning ? 'text-green-400' : 'text-gray-300'
          }`}>
            {line.content}
            {line.isRunning && <span className="animate-pulse">...</span>}
          </div>
        ))}
        
        {/* Current Input */}
        <div className="flex items-center gap-1">
          <span className="text-yellow-400">$</span>
          <input
            ref={inputRef}
            type="text"
            value={currentCommand}
            onChange={(e) => setCurrentCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!!runningProcess}
            className="flex-1 bg-transparent text-gray-300 outline-none caret-yellow-400 disabled:opacity-50"
            placeholder={runningProcess ? "Process running... (Ctrl+C to cancel)" : "Type a command..."}
            autoFocus
          />
        </div>
      </div>
    </div>
  );
};

export default Terminal;
