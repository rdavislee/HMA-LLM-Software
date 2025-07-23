import { 
  FileCode, 
  TestTube, 
  Wrench,
  Sparkles
} from 'lucide-react';

interface PhaseIndicatorProps {
  currentPhase: 'spec' | 'test' | 'impl';
}

export function PhaseIndicator({ currentPhase }: PhaseIndicatorProps) {
  const getPhaseIcon = () => {
    switch (currentPhase) {
      case 'spec':
        return <FileCode className="h-4 w-4" />;
      case 'test':
        return <TestTube className="h-4 w-4" />;
      case 'impl':
        return <Wrench className="h-4 w-4" />;
    }
  };

  const getPhaseColor = () => {
    switch (currentPhase) {
      case 'spec':
        return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      case 'test':
        return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'impl':
        return 'text-violet-500 bg-violet-500/10 border-violet-500/20';
    }
  };

  const getPhaseLabel = () => {
    switch (currentPhase) {
      case 'spec':
        return 'Specification Phase';
      case 'test':
        return 'Testing Phase';
      case 'impl':
        return 'Implementation Phase';
    }
  };

  const getPhaseDescription = () => {
    switch (currentPhase) {
      case 'spec':
        return 'Defining project structure and requirements';
      case 'test':
        return 'Writing test cases and validation logic';
      case 'impl':
        return 'Implementing the actual code and features';
    }
  };

  const phases: Array<{ key: 'spec' | 'test' | 'impl'; label: string; icon: JSX.Element }> = [
    { key: 'spec', label: 'Specification', icon: <FileCode className="h-3 w-3" /> },
    { key: 'test', label: 'Testing', icon: <TestTube className="h-3 w-3" /> },
    { key: 'impl', label: 'Implementation', icon: <Wrench className="h-3 w-3" /> }
  ];

  return (
    <div className="mb-3">
      {/* Main Phase Indicator - Non-interactive */}
      <div 
        className={`rounded-lg border p-3 transition-all duration-300 ${getPhaseColor()}`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              {getPhaseIcon()}
              <span className="font-medium text-sm">{getPhaseLabel()}</span>
            </div>
            <span className="text-xs opacity-75">
              {getPhaseDescription()}
            </span>
          </div>
          <Sparkles className="h-3 w-3 opacity-50" />
        </div>

        {/* Progress dots */}
        <div className="flex items-center gap-1 mt-2">
          {phases.map((phase, index) => (
            <div key={phase.key} className="flex items-center">
              <div 
                className={`h-1.5 w-1.5 rounded-full transition-all duration-300 ${
                  phase.key === currentPhase 
                    ? 'bg-current w-8' 
                    : phases.indexOf(phases.find(p => p.key === currentPhase)!) > index
                      ? 'bg-current opacity-50'
                      : 'bg-current opacity-20'
                }`}
              />
              {index < phases.length - 1 && (
                <div className={`h-0.5 w-4 mx-1 bg-current transition-opacity duration-300 ${
                  phases.indexOf(phases.find(p => p.key === currentPhase)!) > index
                    ? 'opacity-50'
                    : 'opacity-20'
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}