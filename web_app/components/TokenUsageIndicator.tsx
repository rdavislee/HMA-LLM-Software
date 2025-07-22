import { useLLM } from '../contexts/LLMContext';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { TrendingUp, Zap } from 'lucide-react';
import { cn } from './ui/utils';
import { getContextWindowForModel } from '../services/llm';

interface TokenUsageIndicatorProps {
  className?: string;
  variant?: 'default' | 'compact';
}

export function TokenUsageIndicator({ className, variant = 'default' }: TokenUsageIndicatorProps) {
  const { totalTokensUsed, config, activeAgents } = useLLM();
  
  const contextWindow = getContextWindowForModel(config.model);
  const usagePercentage = (totalTokensUsed / contextWindow) * 100;
  
  // Calculate estimated cost (rough estimates)
  const estimatedCost = (() => {
    const costPer1kTokens = {
      'gpt-4o': 0.005,
      'gpt-4.1': 0.01,
      'claude-opus-4': 0.015,
      'claude-sonnet-4': 0.003,
      'gemini-2.5-pro': 0.0025,
      'deepseek-v3': 0.001,
    };
    const rate = costPer1kTokens[config.model as keyof typeof costPer1kTokens] || 0.005;
    return (totalTokensUsed / 1000) * rate;
  })();

  if (variant === 'compact') {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <Zap className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">
          {totalTokensUsed.toLocaleString()} tokens
        </span>
        {estimatedCost > 0 && (
          <Badge variant="outline" className="text-xs">
            ~${estimatedCost.toFixed(3)}
          </Badge>
        )}
      </div>
    );
  }

  return (
    <div className={cn("space-y-3 p-4 border rounded-lg bg-card", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-primary" />
          <h3 className="font-medium">Token Usage</h3>
        </div>
        <Badge variant={usagePercentage > 80 ? "destructive" : "secondary"}>
          {usagePercentage.toFixed(1)}%
        </Badge>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Total Tokens</span>
          <span className="font-mono">{totalTokensUsed.toLocaleString()}</span>
        </div>
        
        <Progress value={usagePercentage} className="h-2" />
        
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>0</span>
          <span>{contextWindow.toLocaleString()} (max)</span>
        </div>
      </div>

      {activeAgents.length > 0 && (
        <div className="pt-2 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Active Agents</span>
            <span>{activeAgents.length}</span>
          </div>
        </div>
      )}

      {estimatedCost > 0 && (
        <div className="pt-2 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              Estimated Cost
            </span>
            <span className="font-mono text-primary">
              ${estimatedCost.toFixed(4)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}