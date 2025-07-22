import { useState, useRef, useEffect, useCallback } from 'react';
import { Terminal as TerminalIcon, Loader2 } from 'lucide-react';
import { Terminal as XTerm } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import websocketService, { TerminalSession, TerminalData } from '../services/websocket';
import { useSocketEvent } from '../hooks/useSocketEvent';
import '@xterm/xterm/css/xterm.css';

interface TerminalProps {
  projectId?: string;
}

export function Terminal({ projectId = 'default' }: TerminalProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [terminalSession, setTerminalSession] = useState<TerminalSession | null>(null);
  const [isInitializing, setIsInitializing] = useState(false);
  
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const resizeTimeoutRef = useRef<number | null>(null);

  // Handle terminal session updates
  useSocketEvent('terminal_session', (session: TerminalSession) => {
    if (session.sessionId === sessionId) {
      setTerminalSession(session);
      setIsInitializing(false);
      
      if (session.status === 'error' && xtermRef.current) {
        xtermRef.current.write(`\r\n\x1b[31mError: ${session.error || 'Failed to start terminal'}\x1b[0m\r\n`);
      }
    }
  });

  // Handle terminal data
  useSocketEvent('terminal_data', (data: TerminalData) => {
    if (data.sessionId === sessionId && xtermRef.current) {
      xtermRef.current.write(data.data);
    }
  });

  const handleResize = useCallback(() => {
    if (fitAddonRef.current && xtermRef.current) {
      setTimeout(() => {
        if (fitAddonRef.current && xtermRef.current) {
          try {
            fitAddonRef.current.fit();
            const { cols, rows } = xtermRef.current;
            
            if (resizeTimeoutRef.current) {
              clearTimeout(resizeTimeoutRef.current);
            }
            resizeTimeoutRef.current = window.setTimeout(() => {
              if (sessionId) {
                websocketService.resizeTerminal(sessionId, cols, rows);
              }
            }, 200);
          } catch (error) {
            console.warn('Terminal resize error:', error);
          }
        }
      }, 100);
    }
  }, [sessionId]);

  // Initialize xterm.js terminal
  useEffect(() => {
    if (!terminalRef.current || xtermRef.current) return;

    const terminal = new XTerm({
      cursorBlink: true,
      fontSize: 13,
      fontFamily: "'JetBrains Mono', 'Consolas', 'Monaco', monospace",
      fontWeight: 500,
      lineHeight: 1.6,
      allowTransparency: false,
      convertEol: true,
      rows: 24,
      cols: 80,
      theme: {
        background: 'hsl(var(--card))',
        foreground: 'hsl(var(--foreground))',
        cursor: 'hsl(var(--primary))',
        selectionBackground: 'hsl(var(--primary) / 0.3)',
        black: '#000000',
        red: 'hsl(var(--destructive))',
        green: '#13A10E',
        yellow: '#C19C00',
        blue: 'hsl(var(--primary))',
        magenta: 'hsl(var(--accent))',
        cyan: '#3A96DD',
        white: 'hsl(var(--foreground))',
        brightBlack: 'hsl(var(--muted-foreground))',
        brightRed: 'hsl(var(--destructive))',
        brightGreen: '#16C60C',
        brightYellow: '#F9F1A5',
        brightBlue: 'hsl(var(--primary))',
        brightMagenta: 'hsl(var(--accent))',
        brightCyan: '#61D6D6',
        brightWhite: 'hsl(var(--foreground))'
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

    // Initial fit
    handleResize();

    // Write welcome message
    terminal.write('Welcome to Colony AI Terminal\r\n');
    terminal.write('Connecting to server...\r\n\r\n');

    // Handle terminal input
    terminal.onData((data) => {
      if (sessionId && terminalSession?.status === 'running') {
        websocketService.sendTerminalData(sessionId, data);
      }
    });

    // Handle resize
    terminal.onResize(({ cols, rows }) => {
      if (sessionId) {
        websocketService.resizeTerminal(sessionId, cols, rows);
      }
    });

    // Create terminal session
    setIsInitializing(true);
    websocketService.createTerminalSession(projectId);

    return () => {
      if (sessionId) {
        websocketService.closeTerminal(sessionId);
      }
      terminal.dispose();
      xtermRef.current = null;
      fitAddonRef.current = null;
    };
  }, [projectId]);

  // Handle WebSocket connection for session creation
  useSocketEvent('terminal_session', (session: TerminalSession) => {
    if (session.projectId === projectId && !sessionId) {
      setSessionId(session.sessionId);
    }
  });

  // Handle window resize
  useEffect(() => {
    const resizeObserver = new ResizeObserver(() => {
      handleResize();
    });

    if (terminalRef.current) {
      resizeObserver.observe(terminalRef.current);
    }

    window.addEventListener('resize', handleResize);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener('resize', handleResize);
      if (resizeTimeoutRef.current) {
        clearTimeout(resizeTimeoutRef.current);
      }
    };
  }, [handleResize]);

  return (
    <div className="h-full border border-border rounded-lg bg-card">
      <div className="h-full flex flex-col">
        {/* Terminal Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <TerminalIcon className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Terminal</span>
            {isInitializing && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span className="text-xs">Initializing...</span>
              </div>
            )}
          </div>
          {terminalSession && (
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                terminalSession.status === 'running' ? 'bg-green-500' : 
                terminalSession.status === 'error' ? 'bg-red-500' : 
                'bg-yellow-500'
              }`} />
              <span className="text-xs text-muted-foreground capitalize">
                {terminalSession.status}
              </span>
            </div>
          )}
        </div>

        {/* Terminal Content */}
        <div 
          ref={terminalRef}
          className="flex-1 p-2"
          style={{
            backgroundColor: 'hsl(var(--card))'
          }}
        />
      </div>
    </div>
  );
}