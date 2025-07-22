import { useState, useEffect } from "react";
import { ResizableLayout } from "./components/ResizableLayout";
import { ChatHistorySidebar } from "./components/ChatHistorySidebar";
import { WaveProgress } from "./components/WaveProgress";
import { ModelSelector } from "./components/ModelSelector";
import { ImportDialog } from "./components/ImportDialog";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { Button } from "./components/ui/button";
import { Menu, Zap, Upload } from "lucide-react";
import websocketService from "./services/websocket";
import { useSocketEvent } from "./hooks/useSocketEvent";
import chatStorage from "./services/chatStorage";
import { LLMProvider } from "./contexts/LLMContext";
import { ImportedNode } from "./services/fileImport";

interface ChatMessage {
  id: string;
  text: string;
  timestamp: string;
  sender: "user" | "assistant" | "system";
  threadId?: string;
  agentId?: string;
}

function AppContent() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentPhase, setCurrentPhase] = useState<"spec" | "test" | "impl">("spec");
  const [waveProgress, setWaveProgress] = useState(0);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isImportDialogOpen, setIsImportDialogOpen] = useState(false);
  const [importedProject, setImportedProject] = useState<ImportedNode[]>([]);

  // Initialize WebSocket connection
  useEffect(() => {
    websocketService.connect();
    
    // Load existing session or create new one
    const currentSession = chatStorage.getCurrentSession();
    if (currentSession) {
      setMessages(currentSession.messages.map(msg => ({
        id: msg.id,
        text: msg.content,
        timestamp: new Date(msg.timestamp).toLocaleTimeString(),
        sender: msg.sender as "user" | "assistant" | "system",
        agentId: msg.agentId
      })));
      setCurrentSessionId(currentSession.id);
    } else {
      const newSession = chatStorage.createNewSession();
      setCurrentSessionId(newSession.id);
    }

    return () => {
      websocketService.disconnect();
    };
  }, []);

  // WebSocket event handlers
  useSocketEvent('connected', () => {
    setIsConnected(true);
    console.log('Connected to WebSocket server');
  });

  useSocketEvent('disconnected', () => {
    setIsConnected(false);
    console.log('Disconnected from WebSocket server');
  });

  const handleSendMessage = (messageText: string, files?: any[]) => {
    if (!messageText.trim() && (!files || files.length === 0)) return;

    const threadId = `task-${Date.now()}`;
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      text: messageText,
      timestamp: new Date().toLocaleTimeString(),
      sender: "user",
      threadId,
    };

    setMessages((prev) => [...prev, newMessage]);
    setIsLoading(true);

    // Send message via WebSocket
    websocketService.sendPrompt(messageText);

    // Save to storage
    if (currentSessionId) {
      const session = chatStorage.getCurrentSession();
      if (session) {
        session.messages.push({
          id: newMessage.id,
          content: messageText,
          sender: 'user',
          timestamp: new Date().toISOString()
        });
        chatStorage.saveChatSession(session);
      }
    }
  };

  const handleMessagesUpdate = (updatedMessages: ChatMessage[]) => {
    setMessages(updatedMessages);
    
    // Save to storage
    if (currentSessionId) {
      const session = chatStorage.getCurrentSession();
      if (session) {
        session.messages = updatedMessages.map(msg => ({
          id: msg.id,
          content: msg.text,
          sender: msg.sender as 'user' | 'ai' | 'system',
          timestamp: new Date().toISOString(),
          agentId: msg.agentId
        }));
        session.lastModified = new Date();
        chatStorage.saveChatSession(session);
      }
    }
  };

  const handleLoadingChange = (loading: boolean) => {
    setIsLoading(loading);
  };

  const handleNewChat = () => {
    setMessages([
      {
        id: "1",
        text: "Hello! I'm Colony AI. I can help you generate code for your project. What would you like me to create?",
        timestamp: new Date().toLocaleTimeString(),
        sender: "assistant",
        threadId: "welcome-thread",
      },
    ]);

    // Simulate phase progression
    setTimeout(() => {
      setWaveProgress(65);
      setTimeout(() => {
        setCurrentPhase("test");
        setWaveProgress(30);
        setTimeout(() => {
          setWaveProgress(80);
          setTimeout(() => {
            setCurrentPhase("impl");
            setWaveProgress(15);
          }, 2000);
        }, 1500);
      }, 2000);
    }, 1000);
  };

  const handleImport = (nodes: ImportedNode[]) => {
    setImportedProject(prev => [...prev, ...nodes]);
  };

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Header with expanded height (64px) and repositioned elements */}
      <header className="sticky top-0 z-50 w-full bg-background border-b border-border">
        <div className="h-16 flex items-center px-4">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="lg"
              className="p-2 hover:bg-card focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary/60"
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu className="h-6 w-6" />
            </Button>

            {/* Title moved closer to menu button */}
            <h1
              className="text-foreground ml-2"
              style={{
                fontFamily: "Quicksand, sans-serif",
                fontSize: "28px",
                fontWeight: 400,
                letterSpacing: "-0.5px",
              }}
            >
              [Name]
            </h1>
          </div>

          {/* Right side - Model Selector, Import and Upgrade buttons */}
          <div className="flex-1 flex justify-end items-center gap-4">
            <ModelSelector />
            <Button
              size="sm"
              onClick={() => setIsImportDialogOpen(true)}
              className="minimalist-button"
            >
              <Upload className="h-4 w-4 mr-1" />
              Import
            </Button>
            <Button
              size="sm"
              className="minimalist-button border-primary text-primary hover:bg-primary/5"
            >
              <Zap className="h-4 w-4 mr-1" />
              Upgrade
            </Button>
          </div>
        </div>

        {/* Wave Progress Bar */}
        <WaveProgress
          currentPhase={currentPhase}
          progress={waveProgress}
        />
      </header>

      {/* Main Content Area - adjusted for larger header */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <ResizableLayout
          messages={messages}
          onSendMessage={handleSendMessage}
          onNewChat={handleNewChat}
          currentPhase={currentPhase}
          isConnected={isConnected}
          onMessagesUpdate={handleMessagesUpdate}
          isLoading={isLoading}
          onLoadingChange={handleLoadingChange}
          importedProject={importedProject}
        />
      </div>

      {/* Chat History Sidebar */}
      <ChatHistorySidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Import Dialog */}
      <ImportDialog
        isOpen={isImportDialogOpen}
        onClose={() => setIsImportDialogOpen(false)}
        onImport={handleImport}
      />
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <LLMProvider>
        <AppContent />
      </LLMProvider>
    </ErrorBoundary>
  );
}