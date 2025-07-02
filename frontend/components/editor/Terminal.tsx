import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Terminal as TerminalIcon, X, Minus, Square, Play, RefreshCw } from 'lucide-react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import websocketService, { TerminalSession, TerminalData } from '../../src/services/websocket';
import '@xterm/xterm/css/xterm.css';

interface TerminalProps {
  projectId?: string;
}

const InteractiveTerminal: React.FC<TerminalProps> = ({ projectId }) => {
  const [isMinimized, setIsMinimized] = useState(false);
  const [terminalSession, setTerminalSession] = useState<TerminalSession | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  // Initialize xterm.js terminal
  const initializeTerminal = useCallback(() => {
    if (!terminalRef.current || xtermRef.current) return;

    // Create terminal instance
    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: '"Fira Code", "Consolas", "Monaco", monospace',
      theme: {
        background: '#111827', // gray-900
        foreground: '#f9fafb', // gray-50
        cursor: '#facc15', // yellow-400
        selectionBackground: '#374151', // gray-700
        black: '#1f2937',
        red: '#ef4444',
        green: '#10b981',
        yellow: '#facc15',
        blue: '#3b82f6',
        magenta: '#a855f7',
        cyan: '#06b6d4',
        white: '#f9fafb',
        brightBlack: '#6b7280',
        brightRed: '#f87171',
        brightGreen: '#34d399',
        brightYellow: '#fbbf24',
        brightBlue: '#60a5fa',
        brightMagenta: '#c084fc',
        brightCyan: '#22d3ee',
        brightWhite: '#ffffff'
      }
    });

    // Create addons
    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();

    // Load addons
    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);

    // Open terminal in DOM
    terminal.open(terminalRef.current);

    // Store references
    xtermRef.current = terminal;
    fitAddonRef.current = fitAddon;

    // Handle terminal input
    terminal.onData((data) => {
      if (sessionIdRef.current) {
        websocketService.sendTerminalData(sessionIdRef.current, data);
      }
    });

    // Handle terminal resize
    terminal.onResize(({ cols, rows }) => {
      if (sessionIdRef.current) {
        websocketService.resizeTerminal(sessionIdRef.current, cols, rows);
      }
    });

    // Fit terminal to container
    setTimeout(() => {
      try {
        fitAddon.fit();
      } catch (err) {
      }
    }, 100);

    // Show welcome message
    terminal.writeln('\x1b[1;33m╭─ Hive Interactive Terminal ─╮\x1b[0m');
    terminal.writeln('\x1b[1;33m│ Container-backed workspace  │\x1b[0m');
    terminal.writeln('\x1b[1;33m╰─────────────────────────────╯\x1b[0m');
    terminal.writeln('');

    return terminal;
  }, []);

  // Create terminal session
  const createSession = useCallback(async () => {
    const effectiveProjectId = projectId || 'default';
    if (!effectiveProjectId || isConnecting) return;

    setIsConnecting(true);
    setError(null);

    try {
      const sessionId = websocketService.createTerminalSession(effectiveProjectId);
      sessionIdRef.current = sessionId;
      
      if (xtermRef.current) {
        xtermRef.current.writeln('\x1b[33mStarting container workspace...\x1b[0m');
      }
    } catch (err) {
      setError('Failed to create terminal session');
      setIsConnecting(false);
    }
  }, [projectId, isConnecting]);

  // Restart terminal session
  const restartSession = useCallback(() => {
    if (sessionIdRef.current) {
      websocketService.closeTerminal(sessionIdRef.current);
      sessionIdRef.current = null;
    }
    setTerminalSession(null);
    setError(null);
    
    if (xtermRef.current) {
      xtermRef.current.clear();
    }
    
    setTimeout(() => {
      createSession();
    }, 500);
  }, [createSession]);

  // Initialize terminal on mount
  useEffect(() => {
    if (!isMinimized && terminalRef.current) {
      initializeTerminal();
      
      // Always create a session when terminal is initialized, use default project if none provided
      const effectiveProjectId = projectId || 'default';
      if (effectiveProjectId && !sessionIdRef.current) {
        createSession();
      }
    }

    return () => {
      // Cleanup on unmount
      if (sessionIdRef.current) {
        websocketService.closeTerminal(sessionIdRef.current);
      }
      if (xtermRef.current) {
        xtermRef.current.dispose();
        xtermRef.current = null;
      }
    };
  }, [isMinimized, initializeTerminal, createSession, projectId]);

  // Handle WebSocket events
  useEffect(() => {
    const handleTerminalData = (data: TerminalData) => {
      if (data.sessionId === sessionIdRef.current && xtermRef.current) {
        xtermRef.current.write(data.data);
      }
    };

    const handleTerminalSession = (session: TerminalSession) => {
      if (session.sessionId === sessionIdRef.current) {
        setTerminalSession(session);
        setIsConnecting(false);
        
        if (xtermRef.current) {
          switch (session.status) {
            case 'running':
              xtermRef.current.writeln('\x1b[32m✓ Container ready! Welcome to your workspace.\x1b[0m');
              xtermRef.current.writeln('');
              break;
            case 'error':
              xtermRef.current.writeln('\x1b[31m✗ Failed to start container workspace.\x1b[0m');
              setError('Container failed to start');
              break;
            case 'stopped':
              xtermRef.current.writeln('\x1b[33m○ Container workspace stopped.\x1b[0m');
              break;
          }
        }
      }
    };

    websocketService.on('terminal_data', handleTerminalData);
    websocketService.on('terminal_session', handleTerminalSession);

    return () => {
      websocketService.off('terminal_data');
      websocketService.off('terminal_session');
    };
  }, []);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (fitAddonRef.current && !isMinimized) {
        setTimeout(() => {
          try {
            fitAddonRef.current?.fit();
          } catch (err) {
          }
        }, 100);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isMinimized]);

  // Fit terminal when expanded
  useEffect(() => {
    if (!isMinimized && fitAddonRef.current) {
      setTimeout(() => {
        try {
          fitAddonRef.current?.fit();
        } catch (err) {
        }
      }, 100);
    }
  }, [isMinimized]);

  if (isMinimized) {
    return (
      <div className="bg-gray-900 border-t border-yellow-400/20 p-2">
        <button
          onClick={() => setIsMinimized(false)}
          className="flex items-center gap-2 text-yellow-400 hover:text-yellow-300 transition-colors"
        >
          <TerminalIcon className="w-4 h-4" />
          <span className="text-sm font-medium">
            Terminal {terminalSession?.status === 'running' ? '(running)' : '(minimized)'}
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
            Interactive Terminal
          </span>
          {terminalSession?.status === 'running' && (
            <span className="text-green-400 text-xs">●</span>
          )}
          {isConnecting && (
            <RefreshCw className="w-3 h-3 text-yellow-400 animate-spin" />
          )}
          {terminalSession?.containerId && (
            <span className="text-gray-500 text-xs font-mono">
              {terminalSession.containerId.substring(0, 12)}
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-1">
          {!terminalSession && !isConnecting && (
            <button
              onClick={createSession}
              className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
              title="Start terminal"
            >
              <Play className="w-3 h-3" />
            </button>
          )}
          
          {(error || terminalSession?.status === 'error') && (
            <button
              onClick={restartSession}
              className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
              title="Restart terminal"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          )}
          
          <button
            onClick={() => setIsMinimized(true)}
            className="w-6 h-6 rounded hover:bg-yellow-400/20 flex items-center justify-center transition-colors"
            title="Minimize"
          >
            <Minus className="w-3 h-3 text-gray-400" />
          </button>
          
          <button 
            onClick={() => {
              if (sessionIdRef.current) {
                websocketService.closeTerminal(sessionIdRef.current);
              }
            }}
            className="w-6 h-6 rounded hover:bg-red-500/20 flex items-center justify-center transition-colors"
            title="Close"
          >
            <X className="w-3 h-3 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="px-3 py-2 bg-red-500/10 border-b border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Terminal Container */}
      <div className="flex-1 overflow-hidden">
        <div 
          ref={terminalRef}
          className="h-full w-full"
          style={{ 
            backgroundColor: '#111827',
            padding: '8px'
          }}
        />
      </div>
    </div>
  );
};

export default InteractiveTerminal;
