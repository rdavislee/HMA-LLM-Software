// LLM Service - Types and utilities for LLM integration
// This service provides TypeScript types and utilities that mirror the backend LLM providers

// Available LLM model types matching backend providers
export type LLMProvider = 'openai' | 'anthropic' | 'google' | 'deepseek' | 'xai';

export interface LLMModel {
  id: string;
  name: string;
  provider: LLMProvider;
  contextWindow: number;
  description: string;
  requiresApiKey: boolean;
  supportsStreaming: boolean;
  supportsStructuredOutput: boolean;
}

// Available models matching src/llm/providers.py MODEL_CLIENTS
export const AVAILABLE_MODELS: Record<string, LLMModel> = {
  // OpenAI models
  'gpt-4o': {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'openai',
    contextWindow: 128000,
    description: 'OpenAI GPT-4 Optimized - Fast and efficient',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: true,
  },
  'gpt-4.1': {
    id: 'gpt-4.1',
    name: 'GPT-4.1',
    provider: 'openai',
    contextWindow: 128000,
    description: 'OpenAI GPT-4.1 - Latest improvements',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: true,
  },
  'o3': {
    id: 'o3',
    name: 'O3',
    provider: 'openai',
    contextWindow: 100000,
    description: 'OpenAI O3 - Advanced reasoning model',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  'o3-pro': {
    id: 'o3-pro',
    name: 'O3 Pro',
    provider: 'openai',
    contextWindow: 100000,
    description: 'OpenAI O3 Pro - Enhanced reasoning capabilities',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  
  // Anthropic models
  'claude-sonnet-4': {
    id: 'claude-sonnet-4',
    name: 'Claude Sonnet 4',
    provider: 'anthropic',
    contextWindow: 200000,
    description: 'Claude Sonnet 4 - Enhanced reasoning and coding',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  'claude-opus-4': {
    id: 'claude-opus-4',
    name: 'Claude Opus 4',
    provider: 'anthropic',
    contextWindow: 200000,
    description: 'Claude Opus 4 - Most powerful Claude model',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  'claude-3.7-sonnet': {
    id: 'claude-3.7-sonnet',
    name: 'Claude 3.7 Sonnet',
    provider: 'anthropic',
    contextWindow: 200000,
    description: 'Claude 3.7 Sonnet - Hybrid reasoning model',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  'claude-3.5-sonnet': {
    id: 'claude-3.5-sonnet',
    name: 'Claude 3.5 Sonnet',
    provider: 'anthropic',
    contextWindow: 200000,
    description: 'Claude 3.5 Sonnet - Balanced performance',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  
  // Google models
  'gemini-2.5-flash': {
    id: 'gemini-2.5-flash',
    name: 'Gemini 2.5 Flash',
    provider: 'google',
    contextWindow: 100000,
    description: 'Google Gemini 2.5 Flash - Fast and efficient',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  'gemini-2.5-pro': {
    id: 'gemini-2.5-pro',
    name: 'Gemini 2.5 Pro',
    provider: 'google',
    contextWindow: 100000,
    description: 'Google Gemini 2.5 Pro - Powerful reasoning',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  
  // DeepSeek models
  'deepseek-v3': {
    id: 'deepseek-v3',
    name: 'DeepSeek V3',
    provider: 'deepseek',
    contextWindow: 65536,
    description: 'DeepSeek V3 - General purpose model',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  'deepseek-r1': {
    id: 'deepseek-r1',
    name: 'DeepSeek R1',
    provider: 'deepseek',
    contextWindow: 65536,
    description: 'DeepSeek R1 - Reasoning model',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  
  // xAI Grok models
  'grok-3': {
    id: 'grok-3',
    name: 'Grok 3',
    provider: 'xai',
    contextWindow: 100000,
    description: 'xAI Grok 3 - Flagship model for enterprise tasks',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
  'grok-3-mini': {
    id: 'grok-3-mini',
    name: 'Grok 3 Mini',
    provider: 'xai',
    contextWindow: 100000,
    description: 'xAI Grok 3 Mini - Lightweight for math and quantitative tasks',
    requiresApiKey: true,
    supportsStreaming: true,
    supportsStructuredOutput: false,
  },
};

// LLM configuration that will be sent to the backend
export interface LLMConfig {
  model: string;
  temperature?: number;
  maxTokens?: number;
  apiKeys?: Partial<Record<LLMProvider, string>>;
}

// Agent types matching backend agent hierarchy
export interface AgentInfo {
  id: string;
  type: 'master' | 'manager' | 'coder' | 'tester' | 'ephemeral';
  path: string;
  status: 'active' | 'inactive' | 'waiting' | 'delegating' | 'completed' | 'error';
  task?: string;
  parentId?: string;
  children?: string[];
  personalFile?: string;
  contextSize?: number;
  maxContextSize?: number;
}

// LLM response types
export interface LLMResponse {
  content: string;
  model: string;
  tokensUsed?: number;
  finishReason?: 'stop' | 'length' | 'error';
}

// Streaming response chunk
export interface LLMStreamChunk {
  content: string;
  isComplete: boolean;
  model?: string;
  error?: string;
}

// Helper functions
export function getModelsByProvider(provider: LLMProvider): LLMModel[] {
  return Object.values(AVAILABLE_MODELS).filter(model => model.provider === provider);
}

export function getRequiredApiKeys(modelId: string): LLMProvider | null {
  const model = AVAILABLE_MODELS[modelId];
  return model?.requiresApiKey ? model.provider : null;
}

export function validateApiKey(key: string): boolean {
  // Basic validation - just check it's not empty and has reasonable length
  return key.trim().length > 20;
}

export function getDefaultConfig(): LLMConfig {
  return {
    model: 'gpt-4o', // Default to GPT-4o
    temperature: 0.7,
    maxTokens: 1000,
    apiKeys: {},
  };
}

// Context window management
export function estimateTokenCount(text: string): number {
  // Rough estimation: ~4 characters per token for English text
  return Math.ceil(text.length / 4);
}

export function getContextWindowForModel(modelId: string): number {
  return AVAILABLE_MODELS[modelId]?.contextWindow || 8000;
}

// Storage keys for persisting settings
export const LLM_STORAGE_KEYS = {
  MODEL: 'hma_llm_selected_model',
  TEMPERATURE: 'hma_llm_temperature',
  MAX_TOKENS: 'hma_llm_max_tokens',
  // Note: API keys should be stored securely, not in localStorage
} as const;

// Load saved preferences
export function loadLLMPreferences(): Partial<LLMConfig> {
  try {
    const model = localStorage.getItem(LLM_STORAGE_KEYS.MODEL);
    const temperature = localStorage.getItem(LLM_STORAGE_KEYS.TEMPERATURE);
    const maxTokens = localStorage.getItem(LLM_STORAGE_KEYS.MAX_TOKENS);
    
    return {
      model: model || undefined,
      temperature: temperature ? parseFloat(temperature) : undefined,
      maxTokens: maxTokens ? parseInt(maxTokens, 10) : undefined,
    };
  } catch {
    return {};
  }
}

// Save preferences
export function saveLLMPreferences(config: Partial<LLMConfig>): void {
  try {
    if (config.model) {
      localStorage.setItem(LLM_STORAGE_KEYS.MODEL, config.model);
    }
    if (config.temperature !== undefined) {
      localStorage.setItem(LLM_STORAGE_KEYS.TEMPERATURE, config.temperature.toString());
    }
    if (config.maxTokens !== undefined) {
      localStorage.setItem(LLM_STORAGE_KEYS.MAX_TOKENS, config.maxTokens.toString());
    }
  } catch (error) {
    console.error('Failed to save LLM preferences:', error);
  }
}