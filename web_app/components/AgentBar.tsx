import { useState } from 'react';
import { Badge } from './ui/badge';
import { AgentUpdate } from '../services/websocket';
import { useSocketEvent } from '../hooks/useSocketEvent';

interface Agent {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'waiting' | 'completed' | 'error' | 'delegating';
  task?: string;
  progress?: number;
  parentId?: string;
  phase?: 'spec' | 'test' | 'impl';
  tokens?: number;
  cost?: number;
}

interface AgentBarProps {
  agents?: Agent[];
}

export function AgentBar({ agents: externalAgents }: AgentBarProps) {
  const [agents, setAgents] = useState<Map<string, Agent>>(new Map());

  // Handle agent updates from WebSocket
  useSocketEvent('agent_update', (update: AgentUpdate) => {
    setAgents(prev => {
      const newAgents = new Map(prev);
      
      if (update.status === 'inactive' || update.status === 'completed') {
        // Remove inactive/completed agents after a delay
        setTimeout(() => {
          setAgents(current => {
            const updated = new Map(current);
            updated.delete(update.agentId);
            return updated;
          });
        }, 3000);
      } else {
        // Update or add agent
        const agent: Agent = {
          id: update.agentId,
          name: update.agentId.split('-')[0] || update.agentId,
          status: update.status,
          task: update.task,
          progress: update.progress,
          parentId: update.parentId,
          phase: determinePhase(update.agentId, update.task),
          tokens: Math.floor(Math.random() * 5000), // Mock for now
          cost: Math.random() * 0.5 // Mock for now
        };
        newAgents.set(update.agentId, agent);
      }
      
      return newAgents;
    });
  });

  // Helper to determine phase from agent ID or task
  const determinePhase = (agentId: string, task?: string): 'spec' | 'test' | 'impl' => {
    const lowerTask = (task || '').toLowerCase();
    const lowerId = agentId.toLowerCase();
    
    if (lowerTask.includes('spec') || lowerTask.includes('design') || lowerId.includes('architect')) {
      return 'spec';
    } else if (lowerTask.includes('test') || lowerTask.includes('valid') || lowerId.includes('validator')) {
      return 'test';
    } else {
      return 'impl';
    }
  };

  // Use external agents if provided, otherwise use WebSocket agents
  const agentList = externalAgents || Array.from(agents.values());

  // Mock data for demonstration when no agents
  const defaultAgents: Agent[] = [
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

  const displayAgents = agentList.length > 0 ? agentList : defaultAgents;

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active': return '#10B981'; // green
      case 'delegating': return '#3B82F6'; // blue
      case 'waiting': return '#F59E0B'; // yellow
      case 'completed': return '#8B5CF6'; // purple
      case 'inactive': return '#6B7280'; // gray
      case 'error': return '#EF4444'; // red
      default: return '#6B7280';
    }
  };

  const getPhaseColor = (phase: Agent['phase']) => {
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
        {/* Agents List */}
        <div className="flex items-center gap-4 flex-1">
          {displayAgents.map((agent) => (
            <div key={agent.id} className="flex items-center gap-2 min-w-0">
              {/* Status Dot */}
              <div 
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ 
                  backgroundColor: getStatusColor(agent.status),
                  boxShadow: `0 0 6px ${getStatusColor(agent.status)}60`
                }}
              />
              
              {/* Agent Name */}
              <span className="text-sm font-semibold text-white truncate">
                {agent.name}
              </span>
              
              {/* Phase Badge */}
              {agent.phase && (
                <Badge 
                  variant="outline" 
                  className={`text-xs px-2 py-0.5 border ${getPhaseColor(agent.phase)}`}
                >
                  {agent.phase}
                </Badge>
              )}
              
              {/* Task */}
              {agent.task && (
                <span className="text-xs text-muted-foreground truncate max-w-[200px]">
                  {agent.task}
                </span>
              )}
            </div>
          ))}
        </div>

        {/* Live Counters */}
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
}