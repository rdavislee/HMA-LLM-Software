import { useState } from 'react';
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from './ui/resizable';
import { TabbedChatPanel } from './TabbedChatPanel';
import { UserInput } from './UserInput';
import { FileTree } from './FileTree';
import { CodeEditor } from './CodeEditor';
import { Terminal } from './Terminal';
import { PhaseIndicator } from './PhaseIndicator';
import { Button } from './ui/button';
import { 
  PanelLeftOpen,
  PanelBottomOpen
} from 'lucide-react';
import { ImportedNode } from '../services/fileImport';

interface ChatMessage {
  id: string;
  text: string;
  timestamp: string;
  sender: 'user' | 'assistant' | 'system';
  threadId?: string;
  agentId?: string;
}

interface ResizableLayoutProps {
  messages: ChatMessage[];
  onSendMessage: (message: string, files?: any[]) => void;
  onNewChat: () => void;
  currentPhase?: 'spec' | 'test' | 'impl';
  isConnected?: boolean;
  onMessagesUpdate?: (messages: ChatMessage[]) => void;
  isLoading?: boolean;
  onLoadingChange?: (loading: boolean) => void;
  importedProject?: ImportedNode[];
}

export function ResizableLayout({ 
  messages, 
  onSendMessage, 
  onNewChat, 
  currentPhase = 'spec',
  isConnected = false,
  onMessagesUpdate,
  isLoading = false,
  onLoadingChange,
  importedProject = []
}: ResizableLayoutProps) {
  const [chatCollapsed, setChatCollapsed] = useState(false);
  const [terminalCollapsed, setTerminalCollapsed] = useState(false);
  const [chatSize] = useState(42); // 5/12 = 41.67%
  const [terminalSize] = useState(30);
  const [selectedFile, setSelectedFile] = useState<{ path: string; content: string; language?: string } | null>(null);

  const handleChatCollapse = () => {
    setChatCollapsed(!chatCollapsed);
  };

  const handleTerminalCollapse = () => {
    setTerminalCollapsed(!terminalCollapsed);
  };

  const handleFileSelect = (path: string, content?: string, language?: string) => {
    if (content) {
      setSelectedFile({ path, content, language });
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Main horizontal layout */}
      <ResizablePanelGroup direction="horizontal" className="h-full">
        {/* Chat Panel - Borderless, Full Space */}
        <ResizablePanel 
          defaultSize={chatSize}
          minSize={chatCollapsed ? 5 : 25}
          maxSize={chatCollapsed ? 5 : 60}
          collapsible={true}
          onCollapse={() => setChatCollapsed(true)}
          onExpand={() => setChatCollapsed(false)}
        >
          <div className="h-full flex flex-col bg-card">
            {/* Chat content area - fills available space above UserInput */}
            <div className="flex-1 min-h-0 overflow-hidden">
              {chatCollapsed ? (
                <div className="h-full flex items-center justify-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleChatCollapse}
                    className="rotate-0 hover:rotate-12 transition-transform"
                  >
                    <PanelLeftOpen className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <TabbedChatPanel 
                  messages={messages} 
                  onNewChat={onNewChat}
                  isConnected={isConnected}
                  onMessagesUpdate={onMessagesUpdate}
                  isLoading={isLoading}
                  onLoadingChange={onLoadingChange}
                />
              )}
            </div>
            
            {/* User Input - fixed at bottom */}
            {!chatCollapsed && (
              <div className="flex-shrink-0 px-4 py-4 border-t border-border bg-card">
                <PhaseIndicator 
                  currentPhase={currentPhase}
                />
                <UserInput 
                  onSendMessage={onSendMessage}
                  isLoading={isLoading}
                  disabled={!isConnected}
                />
              </div>
            )}
          </div>
        </ResizablePanel>

        <ResizableHandle withHandle />

        {/* Merged File Tree + Code Editor + Terminal - Single Panel */}
        <ResizablePanel defaultSize={100 - chatSize}>
          <div className="h-full flex flex-col">
            {/* Merged File Tree and Code Editor - No Resizing Between Them */}
            <div className="flex-1 min-h-0">
              <ResizablePanelGroup direction="vertical">
                {/* Combined File Tree + Code Editor Area */}
                <ResizablePanel 
                  defaultSize={terminalCollapsed ? 100 : (100 - terminalSize)}
                  minSize={terminalCollapsed ? 100 : 40}
                >
                  <div className="h-full flex">
                    {/* File Tree - Fixed Width, No Padding */}
                    <div className="w-64 h-full border border-border rounded-l-lg bg-card">
                      <FileTree 
                        onFileSelect={handleFileSelect}
                        importedProject={importedProject}
                      />
                    </div>
                    
                    {/* Code Editor - Remaining Space, No Left Padding */}
                    <div className="flex-1 h-full border-t border-r border-b border-border rounded-r-lg bg-black">
                      <CodeEditor 
                        currentPhase={currentPhase} 
                        selectedFile={selectedFile}
                      />
                    </div>
                  </div>
                </ResizablePanel>

                {/* Terminal */}
                {!terminalCollapsed && (
                  <>
                    <ResizableHandle withHandle />
                    <ResizablePanel 
                      defaultSize={terminalSize}
                      minSize={15}
                      maxSize={60}
                      collapsible={true}
                      onCollapse={() => setTerminalCollapsed(true)}
                    >
                      <div className="h-full">
                        <Terminal />
                      </div>
                    </ResizablePanel>
                  </>
                )}
              </ResizablePanelGroup>

              {/* Terminal collapse/expand button when collapsed */}
              {terminalCollapsed && (
                <div className="absolute bottom-3 left-1/2 transform -translate-x-1/2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleTerminalCollapse}
                    className="bg-background/80 backdrop-blur-sm border-border/50 hover:bg-background/90"
                  >
                    <PanelBottomOpen className="h-4 w-4 mr-2" />
                    Terminal
                  </Button>
                </div>
              )}
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}