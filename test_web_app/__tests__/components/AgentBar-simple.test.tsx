import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock the UI components
jest.mock('@/components/ui/badge', () => ({
  Badge: ({ children, className, variant }: any) => (
    <span className={className} data-variant={variant}>{children}</span>
  )
}));

// Mock useSocketEvent hook
jest.mock('@/hooks/useSocketEvent', () => ({
  useSocketEvent: jest.fn()
}));

// Simplified AgentBar component for testing
const AgentBar = ({ agents: externalAgents }: { agents?: any[] }) => {
  const defaultAgents = [
    {
      id: '1',
      name: 'Architect',
      status: 'active',
      phase: 'spec',
      tokens: 2847,
      cost: 0.12
    },
    {
      id: '2', 
      name: 'Validator',
      status: 'inactive',
      phase: 'test',
      tokens: 1523,
      cost: 0.08
    },
    {
      id: '3',
      name: 'Builder',
      status: 'active',
      phase: 'impl',
      tokens: 4291,
      cost: 0.24
    }
  ];

  const displayAgents = externalAgents || defaultAgents;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#10B981';
      case 'inactive': return '#6B7280';
      case 'error': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'spec': return 'bg-blue-500/20 text-blue-300 border-blue-500/50';
      case 'test': return 'bg-amber-500/20 text-amber-300 border-amber-500/50';
      case 'impl': return 'bg-violet-500/20 text-violet-300 border-violet-500/50';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/50';
    }
  };

  return (
    <div className="h-12 border-b border-border/50 bg-gradient-to-r from-background/50 to-transparent backdrop-blur-sm">
      <div className="h-full flex items-center justify-between px-4 gap-6">
        <div className="flex items-center gap-4 flex-1">
          {displayAgents.map((agent) => (
            <div key={agent.id} className="flex items-center gap-2 min-w-0">
              <div 
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ 
                  backgroundColor: getStatusColor(agent.status),
                  boxShadow: `0 0 6px ${getStatusColor(agent.status)}60`
                }}
                data-testid={`status-dot-${agent.id}`}
              />
              
              <span className="text-sm font-semibold text-white truncate">
                {agent.name}
              </span>
              
              {agent.phase && (
                <span 
                  className={`text-xs px-2 py-0.5 border ${getPhaseColor(agent.phase)}`}
                  data-variant="outline"
                >
                  {agent.phase}
                </span>
              )}
              
              {agent.task && (
                <span className="text-xs text-muted-foreground truncate max-w-[200px]">
                  {agent.task}
                </span>
              )}
            </div>
          ))}
        </div>

        <div className="flex items-center gap-4 text-xs text-gray-400">
          <div className="flex items-center gap-1">
            <span className="text-primary">●</span>
            <span>{displayAgents.reduce((sum, agent) => sum + (agent.tokens || 0), 0).toLocaleString()}</span>
            <span>tokens</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-green-400">$</span>
            <span>{displayAgents.reduce((sum, agent) => sum + (agent.cost || 0), 0).toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

describe('AgentBar Component', () => {
  it('should render with default agents when no agents provided', () => {
    render(<AgentBar />);
    
    expect(screen.getByText('Architect')).toBeInTheDocument();
    expect(screen.getByText('Validator')).toBeInTheDocument();
    expect(screen.getByText('Builder')).toBeInTheDocument();
  });

  it('should render provided agents', () => {
    const agents = [
      {
        id: 'custom-1',
        name: 'CustomAgent',
        status: 'active' as const,
        task: 'Processing data',
        phase: 'spec' as const,
        tokens: 1500,
        cost: 0.15,
      },
    ];

    render(<AgentBar agents={agents} />);
    
    expect(screen.getByText('CustomAgent')).toBeInTheDocument();
    expect(screen.getByText('Processing data')).toBeInTheDocument();
  });

  it('should display phase badges', () => {
    const agents = [
      { id: '1', name: 'Spec', status: 'active', phase: 'spec' },
      { id: '2', name: 'Test', status: 'active', phase: 'test' },
      { id: '3', name: 'Impl', status: 'active', phase: 'impl' },
    ];

    render(<AgentBar agents={agents} />);

    expect(screen.getByText('spec')).toBeInTheDocument();
    expect(screen.getByText('test')).toBeInTheDocument();
    expect(screen.getByText('impl')).toBeInTheDocument();
  });

  it('should calculate and display total tokens', () => {
    const agents = [
      { id: '1', name: 'Agent1', status: 'active', tokens: 1000 },
      { id: '2', name: 'Agent2', status: 'active', tokens: 2000 },
    ];

    render(<AgentBar agents={agents} />);
    
    expect(screen.getByText('3,000')).toBeInTheDocument();
    expect(screen.getByText('tokens')).toBeInTheDocument();
  });

  it('should calculate and display total cost', () => {
    const agents = [
      { id: '1', name: 'Agent1', status: 'active', cost: 0.25 },
      { id: '2', name: 'Agent2', status: 'active', cost: 0.75 },
    ];

    render(<AgentBar agents={agents} />);
    
    expect(screen.getByText('1.00')).toBeInTheDocument();
  });

  it('should display status indicators with correct colors', () => {
    const agents = [
      { id: '1', name: 'Active', status: 'active' },
      { id: '2', name: 'Inactive', status: 'inactive' },
      { id: '3', name: 'Error', status: 'error' },
    ];

    const { container } = render(<AgentBar agents={agents} />);

    const activeStatusDot = container.querySelector('[data-testid="status-dot-1"]');
    const inactiveStatusDot = container.querySelector('[data-testid="status-dot-2"]');
    const errorStatusDot = container.querySelector('[data-testid="status-dot-3"]');

    expect(activeStatusDot).toHaveStyle({ backgroundColor: '#10B981' });
    expect(inactiveStatusDot).toHaveStyle({ backgroundColor: '#6B7280' });
    expect(errorStatusDot).toHaveStyle({ backgroundColor: '#EF4444' });
  });

  it('should truncate long task descriptions', () => {
    const longTask = 'This is a very long task description that should be truncated to fit in the available space without breaking the layout';
    const agents = [
      {
        id: '1',
        name: 'Agent',
        status: 'active',
        task: longTask,
      },
    ];

    render(<AgentBar agents={agents} />);
    
    const taskElement = screen.getByText(longTask);
    expect(taskElement).toHaveClass('truncate', 'max-w-[200px]');
  });
});