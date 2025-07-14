import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Terminal as TerminalIcon, X, Minus, Play, RefreshCw } from 'lucide-react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import websocketService, { TerminalSession, TerminalData } from '../../src/services/websocket';
import { useSocketEvent } from '../../src/hooks/useSocketEvent';
import '@xterm/xterm/css/xterm.css';

interface TerminalProps {
  projectId?: string;
}

const InteractiveTerminal: React.FC<TerminalProps> = ({ projectId }) => {
  const [isMinimized, setIsMinimized] = useState(false);
  const [terminalSession, setTerminalSession] = useState<TerminalSession | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPulsing, setIsPulsing] = useState(false);
  
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const resizeTimeoutRef = useRef<number | null>(null);

  const handleResize = useCallback(() => {
    if (fitAddonRef.current && !isMinimized && xtermRef.current) {
      // Ensure consistent font metrics before fitting
      setTimeout(() => {
        if (fitAddonRef.current && xtermRef.current) {
          try {
            // Force a refresh of the terminal before fitting
            xtermRef.current.refresh(0, xtermRef.current.rows - 1);
            fitAddonRef.current.fit();
          } catch (error) {
            console.warn('Terminal resize error:', error);
          }
        }
      }, 100);
    }
  }, [isMinimized]);

  // Debounced resize handler for sending updates to the server
  const debouncedResize = useCallback((cols: number, rows: number) => {
    if (resizeTimeoutRef.current) {
      clearTimeout(resizeTimeoutRef.current);
    }
    resizeTimeoutRef.current = window.setTimeout(() => {
      if (terminalSession?.sessionId) {
        websocketService.resizeTerminal(terminalSession.sessionId, cols, rows);
      }
    }, 200);
  }, [terminalSession]);

  // Initialize xterm.js terminal
  const initializeTerminal = useCallback(() => {
    if (!terminalRef.current || xtermRef.current) return;

    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: '"Consolas", "Monaco", "Lucida Console", "Liberation Mono", "DejaVu Sans Mono", "Bitstream Vera Sans Mono", "Courier New", monospace',
      fontWeight: 'normal',
      fontWeightBold: 'bold',
      lineHeight: 1.0,
      letterSpacing: 0,
      allowTransparency: false,
      convertEol: true,
      rows: 24,
      cols: 80,
      theme: {
        background: '#0C0C0C',
        foreground: '#CCCCCC',
        cursor: '#FFFFFF',
        selectionBackground: '#264F78',
        black: '#0C0C0C',
        red: '#C50F1F',
        green: '#13A10E',
        yellow: '#C19C00',
        blue: '#0037DA',
        magenta: '#881798',
        cyan: '#3A96DD',
        white: '#CCCCCC',
        brightBlack: '#767676',
        brightRed: '#E74856',
        brightGreen: '#16C60C',
        brightYellow: '#F9F1A5',
        brightBlue: '#3B78FF',
        brightMagenta: '#B4009E',
        brightCyan: '#61D6D6',
        brightWhite: '#F2F2F2'
      },
      allowProposedApi: true,
    });

    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();

    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);
    terminal.open(terminalRef.current);

    xtermRef.current = terminal;
    fitAddonRef.current = fitAddon;

    terminal.onData((data) => {
      if (terminalSession?.sessionId && terminalSession.status === 'running') {
        websocketService.sendTerminalData(terminalSession.sessionId, data);
      }
    });

    terminal.onResize(({ cols, rows }) => {
      debouncedResize(cols, rows);
    });

    setTimeout(() => handleResize(), 100);

    if (xtermRef.current) {
      xtermRef.current.writeln('\x1b[33mRequesting container workspace...\x1b[0m');
    }
  }, [terminalSession, handleResize, debouncedResize]);

  // Create terminal session
  const createSession = useCallback(async () => {
    const effectiveProjectId = projectId || 'default';
    if (!effectiveProjectId || terminalSession?.status === 'starting' || terminalSession?.status === 'running') return;

    setError(null);
    websocketService.createTerminalSession(effectiveProjectId);
      
    if (xtermRef.current) {
      xtermRef.current.writeln('\x1b[33mRequesting container workspace...\x1b[0m');
    }
  }, [projectId, terminalSession]);

  // Initialize terminal and create session on mount
  useEffect(() => {
    if (!isMinimized && terminalRef.current) {
      initializeTerminal();
      if (!terminalSession) {
        createSession();
      }
    }
  }, [isMinimized, initializeTerminal, createSession, terminalSession]);

  // Cleanup effect
  useEffect(() => {
    return () => {
      if (terminalSession?.sessionId) {
        websocketService.closeTerminal(terminalSession.sessionId);
      }
      if (xtermRef.current) {
        xtermRef.current.dispose();
        xtermRef.current = null;
      }
      if (resizeTimeoutRef.current) {
        clearTimeout(resizeTimeoutRef.current);
      }
    };
  }, [terminalSession]);

  // WebSocket event handlers
  useSocketEvent('terminal_data', (data: TerminalData) => {
    if (data.sessionId === terminalSession?.sessionId && xtermRef.current && !isMinimized) {
      xtermRef.current.write(data.data);
      // Pulse animation to show activity when minimized
      if (isMinimized) {
        setIsPulsing(true);
        setTimeout(() => setIsPulsing(false), 500);
      }
    }
  });

  useSocketEvent('terminal_session', (session: TerminalSession) => {
    const effectiveProjectId = projectId || 'default';
    if (session.projectId === effectiveProjectId) {
      setTerminalSession(session);
      
      if (xtermRef.current) {
        switch (session.status) {
          case 'running':
            if (terminalSession?.status !== 'running') {
              xtermRef.current.writeln('\x1b[32m✓ Container ready! Welcome to your workspace.\x1b[0m');
              xtermRef.current.writeln('');
              handleResize();
            }
            break;
          case 'error':
            xtermRef.current.writeln('\x1b[31m✗ Failed to start container workspace.\x1b[0m');
            setError('Container failed to start');
            break;
          case 'stopped':
            if (terminalSession?.status !== 'stopped') {
              xtermRef.current.writeln('\x1b[33m○ Container workspace stopped.\x1b[0m');
            }
            break;
        }
      }
    }
  });

  // Handle window resize
  useEffect(() => {
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [handleResize]);

  // Fit terminal when expanded
  useEffect(() => {
    if (!isMinimized) {
      setTimeout(() => handleResize(), 100);
    }
  }, [isMinimized, handleResize]);

  // Handle layout changes - add a resize observer for better responsiveness
  useEffect(() => {
    if (!terminalRef.current || isMinimized) return;

    const resizeObserver = new ResizeObserver(() => {
      handleResize();
    });

    resizeObserver.observe(terminalRef.current);

    return () => {
      resizeObserver.disconnect();
    };
  }, [handleResize, isMinimized]);


  if (isMinimized) {
    const statusClass = terminalSession?.status === 'running' ? 'bg-green-400' : 'bg-yellow-400';
    return (
      <div className="p-2 flex items-center justify-between rounded-b-lg" style={{ backgroundColor: '#1F1F1F', fontFamily: '"Inter", system-ui, sans-serif' }}>
        <button
          onClick={() => setIsMinimized(false)}
          className="flex items-center gap-2 text-yellow-400 hover:text-yellow-300 transition-colors"
        >
          <TerminalIcon className="w-4 h-4" />
          <span className="text-sm font-medium">Terminal</span>
        </button>
        <div className="flex items-center gap-2">
          {terminalSession?.status && (
            <span className={`text-xs capitalize px-2 py-0.5 rounded-full ${
              terminalSession.status === 'running' ? 'text-green-900 bg-green-400' : 'text-yellow-900 bg-yellow-400'
            }`}>
              {terminalSession.status}
            </span>
          )}
          <div className={`w-2 h-2 rounded-full ${statusClass} ${isPulsing ? 'animate-pulse' : ''}`} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-64 rounded-b-lg" style={{ backgroundColor: '#1F1F1F', fontFamily: '"Inter", system-ui, sans-serif' }}>
      {/* Header */}
      <div className="flex items-center justify-between p-2 border-b border-yellow-400/20" style={{ backgroundColor: '#1F1F1F' }}>
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-4 h-4 text-yellow-400" />
          <span className="text-yellow-400 font-medium text-sm">
            Terminal
          </span>
          {terminalSession?.status === 'running' && (
            <span className="text-green-400 text-xs flex items-center gap-1">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Running
            </span>
          )}
          {(terminalSession?.status === 'starting') && (
            <span className="text-yellow-400 text-xs flex items-center gap-1">
              <RefreshCw className="w-3 h-3 animate-spin" />
              Starting
            </span>
          )}
          {terminalSession?.containerId && (
            <span className="text-gray-500 text-xs font-mono">
              {terminalSession.containerId.substring(0, 12)}
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-1">
          {(terminalSession?.status === 'stopped' || terminalSession?.status === 'error') && (
            <button
              onClick={createSession}
              className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
              title="Start terminal"
            >
              <Play className="w-3 h-3" />
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
              if (terminalSession?.sessionId) {
                websocketService.closeTerminal(terminalSession.sessionId);
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
      <div className="flex-1 overflow-hidden p-2" style={{ backgroundColor: '#1F1F1F' }}>
        <div 
          ref={terminalRef}
          className="h-full w-full"
        />
      </div>
    </div>
  );
};

export default InteractiveTerminal;
