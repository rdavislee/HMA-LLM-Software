import { useState, useEffect } from 'react';
import { WaveProgressUpdate } from '../services/websocket';
import { useSocketEvent } from '../hooks/useSocketEvent';

interface WaveProgressProps {
  currentPhase?: 'spec' | 'test' | 'impl';
  progress?: number; // 0-100
}

export function WaveProgress({ currentPhase: externalPhase, progress: externalProgress }: WaveProgressProps) {
  const [currentPhase, setCurrentPhase] = useState<'spec' | 'test' | 'impl'>(externalPhase || 'spec');
  const [progress, setProgress] = useState(externalProgress || 0);
  const [animatedProgress, setAnimatedProgress] = useState(0);
  const [message, setMessage] = useState<string | null>(null);

  // Handle wave progress updates from WebSocket
  useSocketEvent('wave_progress', (update: WaveProgressUpdate) => {
    setCurrentPhase(update.phase);
    setProgress(update.progress);
    if (update.message) {
      setMessage(update.message);
      // Clear message after 3 seconds
      setTimeout(() => setMessage(null), 3000);
    }
  });

  // Use external values if provided
  useEffect(() => {
    if (externalPhase !== undefined) setCurrentPhase(externalPhase);
    if (externalProgress !== undefined) setProgress(externalProgress);
  }, [externalPhase, externalProgress]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedProgress(progress);
    }, 100);
    return () => clearTimeout(timer);
  }, [progress]);

  const getPhaseColor = () => {
    switch (currentPhase) {
      case 'spec': return '#3B82F6'; // blue
      case 'test': return '#F59E0B'; // yellow/amber
      case 'impl': return '#8B5CF6'; // violet
      default: return '#3B82F6';
    }
  };

  const getPhaseGlow = () => {
    switch (currentPhase) {
      case 'spec': return 'rgba(59, 130, 246, 0.4)';
      case 'test': return 'rgba(245, 158, 11, 0.4)';
      case 'impl': return 'rgba(139, 92, 246, 0.4)';
      default: return 'rgba(59, 130, 246, 0.4)';
    }
  };

  // Function to get phase label (currently unused but may be needed later)
  // const getPhaseLabel = () => {
  //   switch (currentPhase) {
  //     case 'spec': return 'Specification';
  //     case 'test': return 'Testing';
  //     case 'impl': return 'Implementation';
  //     default: return '';
  //   }
  // };

  return (
    <div className="relative">
      {/* Phase labels */}
      <div className="absolute -top-6 left-0 right-0 flex justify-between text-xs text-muted-foreground px-4">
        <span className={`transition-colors ${currentPhase === 'spec' ? 'text-blue-400 font-medium' : ''}`}>
          Spec
        </span>
        <span className={`transition-colors ${currentPhase === 'test' ? 'text-amber-400 font-medium' : ''}`}>
          Test
        </span>
        <span className={`transition-colors ${currentPhase === 'impl' ? 'text-violet-400 font-medium' : ''}`}>
          Impl
        </span>
      </div>
      
      {/* Progress bar */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-border/30 overflow-hidden">
        <div 
          className="h-full transition-all duration-1000 ease-out relative"
          style={{ 
            width: `${animatedProgress}%`,
            backgroundColor: getPhaseColor(),
            boxShadow: `0 0 8px ${getPhaseGlow()}`,
          }}
        >
          {/* Animated shimmer effect */}
          <div 
            className="absolute top-0 left-0 h-full w-8 opacity-60 wave-shimmer"
            style={{
              background: `linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent)`,
              animation: 'shimmer 2s linear infinite'
            }}
          />
        </div>
      </div>
      
      {/* Message display */}
      {message && (
        <div className="absolute -bottom-8 left-4 text-xs text-muted-foreground animate-fade-in">
          {message}
        </div>
      )}
    </div>
  );
}