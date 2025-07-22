import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { 
  LLMConfig, 
  AgentInfo,
  getDefaultConfig,
  loadLLMPreferences,
  saveLLMPreferences,
} from '../services/llm';
import websocketService from '../services/websocket';
import { useSocketEvent } from '../hooks/useSocketEvent';

interface LLMContextType {
  // Configuration
  config: LLMConfig;
  updateConfig: (config: Partial<LLMConfig>) => void;
  
  // Agent hierarchy
  agents: Record<string, AgentInfo>;
  rootAgentId: string | null;
  activeAgents: AgentInfo[];
  
  // Token usage
  totalTokensUsed: number;
  agentTokenUsage: Record<string, number>;
  
  // Streaming
  streamingMessages: Record<string, string>; // messageId -> accumulated content
  isStreaming: Record<string, boolean>; // messageId -> streaming status
  
  // Status
  isConnected: boolean;
  isConfigured: boolean;
}

const LLMContext = createContext<LLMContextType | undefined>(undefined);

export function useLLM() {
  const context = useContext(LLMContext);
  if (!context) {
    throw new Error('useLLM must be used within an LLMProvider');
  }
  return context;
}

interface LLMProviderProps {
  children: ReactNode;
}

export function LLMProvider({ children }: LLMProviderProps) {
  // Configuration state
  const [config, setConfig] = useState<LLMConfig>(() => {
    const saved = loadLLMPreferences();
    return { ...getDefaultConfig(), ...saved };
  });
  
  // Agent hierarchy state
  const [agents, setAgents] = useState<Record<string, AgentInfo>>({});
  const [rootAgentId, setRootAgentId] = useState<string | null>(null);
  
  // Token usage state
  const [totalTokensUsed, setTotalTokensUsed] = useState(0);
  const [agentTokenUsage, setAgentTokenUsage] = useState<Record<string, number>>({});
  
  // Streaming state
  const [streamingMessages, setStreamingMessages] = useState<Record<string, string>>({});
  const [isStreaming, setIsStreaming] = useState<Record<string, boolean>>({});
  
  // Connection state
  const [isConnected, setIsConnected] = useState(false);
  const [isConfigured, setIsConfigured] = useState(false);

  // Listen to WebSocket connection events
  useSocketEvent('connected', () => {
    setIsConnected(true);
    // Send current configuration when connected
    if (config.model) {
      websocketService.configureLLM(config);
      setIsConfigured(true);
    }
  });

  useSocketEvent('disconnected', () => {
    setIsConnected(false);
    setIsConfigured(false);
  });

  // Listen to LLM-specific events
  useSocketEvent('llm_config_update', (update) => {
    setConfig(update.config);
    setIsConfigured(true);
  });

  useSocketEvent('llm_stream', (update) => {
    const { messageId, chunk } = update;
    
    if (messageId) {
      if (chunk.isComplete) {
        // Streaming complete
        setIsStreaming(prev => ({ ...prev, [messageId]: false }));
      } else {
        // Accumulate content
        setStreamingMessages(prev => ({
          ...prev,
          [messageId]: (prev[messageId] || '') + chunk.content
        }));
        setIsStreaming(prev => ({ ...prev, [messageId]: true }));
      }
    }
  });

  useSocketEvent('agent_hierarchy', (update) => {
    setAgents(update.agents);
    setRootAgentId(update.rootAgentId);
  });

  useSocketEvent('token_usage', (update) => {
    const { agentId, tokensUsed } = update;
    
    // Update agent-specific usage
    setAgentTokenUsage(prev => ({
      ...prev,
      [agentId]: (prev[agentId] || 0) + tokensUsed
    }));
    
    // Update total usage
    setTotalTokensUsed(prev => prev + tokensUsed);
    
    // Update agent info if exists
    setAgents(prev => {
      const agent = prev[agentId];
      if (!agent) return prev;
      
      return {
        ...prev,
        [agentId]: {
          ...agent,
          contextSize: update.contextSize,
          maxContextSize: update.maxContextSize,
        } as AgentInfo
      };
    });
  });

  // Update configuration
  const updateConfig = (partialConfig: Partial<LLMConfig>) => {
    const newConfig = { ...config, ...partialConfig };
    setConfig(newConfig);
    saveLLMPreferences(newConfig);
    
    // Send to backend if connected
    if (isConnected) {
      websocketService.configureLLM(newConfig);
      setIsConfigured(true);
    }
  };

  // Get active agents
  const activeAgents = Object.values(agents).filter(
    agent => agent.status === 'active' || agent.status === 'delegating'
  );

  // Request agent hierarchy periodically when connected
  useEffect(() => {
    if (isConnected && isConfigured) {
      // Request immediately
      websocketService.requestAgentHierarchy();
      
      // Then request every 5 seconds
      const interval = setInterval(() => {
        websocketService.requestAgentHierarchy();
      }, 5000);
      
      return () => clearInterval(interval);
    }
  }, [isConnected, isConfigured]);

  const value: LLMContextType = {
    config,
    updateConfig,
    agents,
    rootAgentId,
    activeAgents,
    totalTokensUsed,
    agentTokenUsage,
    streamingMessages,
    isStreaming,
    isConnected,
    isConfigured,
  };

  return <LLMContext.Provider value={value}>{children}</LLMContext.Provider>;
}