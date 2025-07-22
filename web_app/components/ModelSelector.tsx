import { useState, useEffect } from 'react';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Slider } from './ui/slider';
import { Badge } from './ui/badge';
import { Settings, Key, AlertCircle, Check } from 'lucide-react';
import {
  AVAILABLE_MODELS,
  getModelsByProvider,
  getRequiredApiKeys,
  validateApiKey,
  loadLLMPreferences,
  saveLLMPreferences,
  type LLMConfig,
  type LLMProvider,
} from '../services/llm';
import websocketService from '../services/websocket';

interface ModelSelectorProps {
  onConfigChange?: (config: LLMConfig) => void;
  className?: string;
}

export function ModelSelector({ onConfigChange, className }: ModelSelectorProps) {
  const [selectedModel, setSelectedModel] = useState<string>('gpt-4o');
  const [temperature, setTemperature] = useState<number>(0.7);
  const [maxTokens, setMaxTokens] = useState<number>(1000);
  const [apiKeys, setApiKeys] = useState<Partial<Record<LLMProvider, string>>>({});
  const [showSettings, setShowSettings] = useState(false);
  const [showApiKeyDialog, setShowApiKeyDialog] = useState(false);
  const [requiredProvider, setRequiredProvider] = useState<LLMProvider | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [apiKeyError, setApiKeyError] = useState('');

  // Load saved preferences on mount
  useEffect(() => {
    const preferences = loadLLMPreferences();
    if (preferences.model && AVAILABLE_MODELS[preferences.model]) {
      setSelectedModel(preferences.model);
    }
    if (preferences.temperature !== undefined) {
      setTemperature(preferences.temperature);
    }
    if (preferences.maxTokens !== undefined) {
      setMaxTokens(preferences.maxTokens);
    }
  }, []);

  // Handle model selection
  const handleModelSelect = (modelId: string) => {
    setSelectedModel(modelId);
    saveLLMPreferences({ model: modelId });

    // Check if API key is required
    const provider = getRequiredApiKeys(modelId);
    if (provider && !apiKeys[provider]) {
      setRequiredProvider(provider);
      setShowApiKeyDialog(true);
    } else {
      // Send configuration to backend
      updateConfig(modelId);
    }
  };

  // Update configuration
  const updateConfig = (modelId?: string) => {
    const config: LLMConfig = {
      model: modelId || selectedModel,
      temperature,
      maxTokens,
      apiKeys,
    };

    // Save preferences
    saveLLMPreferences(config);

    // Send to backend
    websocketService.configureLLM(config);

    // Notify parent component
    onConfigChange?.(config);
  };

  // Handle API key submission
  const handleApiKeySubmit = () => {
    if (!requiredProvider) return;

    if (!validateApiKey(apiKeyInput)) {
      setApiKeyError('Please enter a valid API key');
      return;
    }

    // Save API key
    const newApiKeys = { ...apiKeys, [requiredProvider]: apiKeyInput };
    setApiKeys(newApiKeys);
    
    // Send to backend
    websocketService.setApiKey(requiredProvider, apiKeyInput);

    // Clear dialog
    setApiKeyInput('');
    setApiKeyError('');
    setShowApiKeyDialog(false);
    setRequiredProvider(null);

    // Update configuration
    updateConfig();
  };

  // Group models by provider
  const modelsByProvider = {
    openai: getModelsByProvider('openai'),
    anthropic: getModelsByProvider('anthropic'),
    google: getModelsByProvider('google'),
    deepseek: getModelsByProvider('deepseek'),
    xai: getModelsByProvider('xai'),
  };

  const currentModel = AVAILABLE_MODELS[selectedModel];

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Select value={selectedModel} onValueChange={handleModelSelect}>
        <SelectTrigger className="w-[240px]">
          <SelectValue placeholder="Select a model" />
        </SelectTrigger>
        <SelectContent>
          {/* OpenAI Models */}
          {modelsByProvider.openai.length > 0 && (
            <SelectGroup>
              <SelectLabel>OpenAI</SelectLabel>
              {modelsByProvider.openai.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  <div className="flex items-center justify-between w-full">
                    <span>{model.name}</span>
                    {apiKeys.openai && <Check className="h-3 w-3 ml-2 text-green-500" />}
                  </div>
                </SelectItem>
              ))}
            </SelectGroup>
          )}

          {/* Anthropic Models */}
          {modelsByProvider.anthropic.length > 0 && (
            <SelectGroup>
              <SelectLabel>Anthropic</SelectLabel>
              {modelsByProvider.anthropic.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  <div className="flex items-center justify-between w-full">
                    <span>{model.name}</span>
                    {apiKeys.anthropic && <Check className="h-3 w-3 ml-2 text-green-500" />}
                  </div>
                </SelectItem>
              ))}
            </SelectGroup>
          )}

          {/* Google Models */}
          {modelsByProvider.google.length > 0 && (
            <SelectGroup>
              <SelectLabel>Google</SelectLabel>
              {modelsByProvider.google.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  <div className="flex items-center justify-between w-full">
                    <span>{model.name}</span>
                    {apiKeys.google && <Check className="h-3 w-3 ml-2 text-green-500" />}
                  </div>
                </SelectItem>
              ))}
            </SelectGroup>
          )}

          {/* DeepSeek Models */}
          {modelsByProvider.deepseek.length > 0 && (
            <SelectGroup>
              <SelectLabel>DeepSeek</SelectLabel>
              {modelsByProvider.deepseek.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  <div className="flex items-center justify-between w-full">
                    <span>{model.name}</span>
                    {apiKeys.deepseek && <Check className="h-3 w-3 ml-2 text-green-500" />}
                  </div>
                </SelectItem>
              ))}
            </SelectGroup>
          )}

          {/* xAI Models */}
          {modelsByProvider.xai.length > 0 && (
            <SelectGroup>
              <SelectLabel>xAI</SelectLabel>
              {modelsByProvider.xai.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  <div className="flex items-center justify-between w-full">
                    <span>{model.name}</span>
                    {apiKeys.xai && <Check className="h-3 w-3 ml-2 text-green-500" />}
                  </div>
                </SelectItem>
              ))}
            </SelectGroup>
          )}
        </SelectContent>
      </Select>

      <Button
        variant="outline"
        size="icon"
        onClick={() => setShowSettings(true)}
        title="Model Settings"
      >
        <Settings className="h-4 w-4" />
      </Button>

      {/* Settings Dialog */}
      <Dialog open={showSettings} onOpenChange={setShowSettings}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Model Settings</DialogTitle>
            <DialogDescription>
              Configure parameters for {currentModel?.name || 'the selected model'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Model Info */}
            <div className="space-y-2">
              <Label>Current Model</Label>
              <div className="p-3 border rounded-lg bg-card">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{currentModel?.name}</span>
                  <Badge variant="secondary">{currentModel?.provider}</Badge>
                </div>
                <p className="text-sm text-muted-foreground">{currentModel?.description}</p>
                <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                  <span>Context: {currentModel?.contextWindow.toLocaleString()} tokens</span>
                  {currentModel?.supportsStreaming && <Badge variant="outline" className="text-xs">Streaming</Badge>}
                </div>
              </div>
            </div>

            {/* Temperature */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="temperature">Temperature</Label>
                <span className="text-sm text-muted-foreground">{temperature}</span>
              </div>
              <Slider
                id="temperature"
                min={0}
                max={2}
                step={0.1}
                value={[temperature]}
                onValueChange={(value) => setTemperature(value[0] || 0.7)}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Controls randomness. Lower values make output more focused and deterministic.
              </p>
            </div>

            {/* Max Tokens */}
            <div className="space-y-2">
              <Label htmlFor="maxTokens">Max Tokens</Label>
              <Input
                id="maxTokens"
                type="number"
                min={1}
                max={currentModel?.contextWindow || 100000}
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value) || 1000)}
              />
              <p className="text-xs text-muted-foreground">
                Maximum number of tokens to generate in the response.
              </p>
            </div>

            {/* API Keys Status */}
            <div className="space-y-2">
              <Label>API Keys</Label>
              <div className="space-y-2">
                {Object.entries(apiKeys).map(([provider, key]) => (
                  <div key={provider} className="flex items-center justify-between p-2 border rounded">
                    <span className="text-sm capitalize">{provider}</span>
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span className="text-xs text-muted-foreground">
                        {key.substring(0, 6)}...{key.substring(key.length - 4)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Button onClick={() => updateConfig()} className="w-full">
              Apply Settings
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* API Key Dialog */}
      <Dialog open={showApiKeyDialog} onOpenChange={setShowApiKeyDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>API Key Required</DialogTitle>
            <DialogDescription>
              Please enter your {requiredProvider} API key to use this model.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="flex items-center gap-2 p-3 border rounded-lg bg-amber-50 dark:bg-amber-950 border-amber-200 dark:border-amber-800">
              <AlertCircle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
              <p className="text-sm text-amber-900 dark:text-amber-100">
                Your API key will be sent securely to the backend server.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="apiKey">
                <Key className="h-4 w-4 inline mr-2" />
                API Key
              </Label>
              <Input
                id="apiKey"
                type="password"
                placeholder={`Enter your ${requiredProvider} API key`}
                value={apiKeyInput}
                onChange={(e) => {
                  setApiKeyInput(e.target.value);
                  setApiKeyError('');
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleApiKeySubmit();
                  }
                }}
              />
              {apiKeyError && (
                <p className="text-sm text-red-500">{apiKeyError}</p>
              )}
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowApiKeyDialog(false);
                  setApiKeyInput('');
                  setApiKeyError('');
                }}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button onClick={handleApiKeySubmit} className="flex-1">
                Save API Key
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}