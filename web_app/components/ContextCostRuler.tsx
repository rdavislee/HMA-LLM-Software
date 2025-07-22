import { useMemo } from 'react';

interface ContextCostRulerProps {
  currentTokens: number;
  maxTokens: number;
  className?: string;
}

export function ContextCostRuler({ currentTokens, maxTokens, className = '' }: ContextCostRulerProps) {
  const percentage = useMemo(() => {
    return Math.min((currentTokens / maxTokens) * 100, 100);
  }, [currentTokens, maxTokens]);

  // Create segments for the ruler
  const segments = [
    { start: 0, end: 70, label: 'Safe' },
    { start: 70, end: 90, label: 'Warning' },
    { start: 90, end: 100, label: 'Critical' }
  ];

  const formatTokenCount = (tokens: number) => {
    if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(1)}K`;
    }
    return tokens.toString();
  };

  return (
    <div className={`context-cost-ruler ${className}`}>
      {/* Token count display */}
      <div className="text-xs text-muted-foreground mb-2 text-center">
        <div className="font-mono">{formatTokenCount(currentTokens)}</div>
        <div className="text-xs opacity-60">/ {formatTokenCount(maxTokens)}</div>
      </div>

      {/* Vertical ruler */}
      <div className="relative w-4 h-32 bg-background/50 rounded-sm border border-border/30 overflow-hidden">
        {/* Background segments */}
        {segments.map((segment, index) => (
          <div
            key={index}
            className="absolute w-full border-b border-border/20"
            style={{
              height: `${(segment.end - segment.start)}%`,
              top: `${100 - segment.end}%`,
              backgroundColor: 'rgba(255, 255, 255, 0.05)'
            }}
          />
        ))}

        {/* Filled progress */}
        <div
          className="absolute bottom-0 w-full transition-all duration-300 ease-out"
          style={{
            height: `${percentage}%`,
            background: percentage <= 70 
              ? 'linear-gradient(to top, rgb(34, 197, 94), rgb(34, 197, 94))' 
              : percentage <= 90
                ? 'linear-gradient(to top, rgb(34, 197, 94), rgb(245, 158, 11))'
                : 'linear-gradient(to top, rgb(34, 197, 94), rgb(245, 158, 11), rgb(239, 68, 68))'
          }}
        />

        {/* Threshold markers */}
        <div 
          className="absolute w-full h-px bg-white/40"
          style={{ top: '30%' }}
        />
        <div 
          className="absolute w-full h-px bg-white/40"
          style={{ top: '10%' }}
        />

        {/* Current level indicator */}
        <div
          className="absolute w-full h-0.5 bg-white shadow-lg transition-all duration-300"
          style={{ 
            top: `${100 - percentage}%`,
            boxShadow: '0 0 6px rgba(255, 255, 255, 0.8)'
          }}
        />
      </div>

      {/* Percentage display */}
      <div className="text-xs text-center mt-2">
        <div 
          className={`font-mono font-medium ${
            percentage <= 70 
              ? 'text-green-400' 
              : percentage <= 90 
                ? 'text-amber-400' 
                : 'text-red-400'
          }`}
        >
          {percentage.toFixed(0)}%
        </div>
      </div>

      {/* Status indicator */}
      <div className="flex items-center justify-center mt-1">
        <div 
          className={`w-2 h-2 rounded-full transition-colors duration-300 ${
            percentage <= 70 
              ? 'bg-green-400' 
              : percentage <= 90 
                ? 'bg-amber-400' 
                : 'bg-red-400'
          }`}
          style={{
            boxShadow: `0 0 8px ${
              percentage <= 70 
                ? 'rgb(34, 197, 94)' 
                : percentage <= 90 
                  ? 'rgb(245, 158, 11)' 
                  : 'rgb(239, 68, 68)'
            }`
          }}
        />
      </div>
    </div>
  );
}