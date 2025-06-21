import React from 'react';

export interface Agent {
  id: string;
  name: string;
  path: string;
  type: 'manager' | 'coder';
  status: 'idle' | 'active' | 'delegating' | 'waiting';
  currentTask?: string;
  children?: Agent[];
  expanded?: boolean;
}

interface AgentHierarchyProps {
  agents: Agent[];
  selectedAgent: Agent | null;
  onAgentSelect: (agent: Agent) => void;
  onToggleExpansion: (agentId: string) => void;
}

const AgentHierarchy: React.FC<AgentHierarchyProps> = ({
  agents,
  selectedAgent,
  onAgentSelect,
  onToggleExpansion
}) => {
  const statusColors = {
    idle: 'text-gray-400',
    active: 'text-blue-400',
    delegating: 'text-yellow-400',
    waiting: 'text-purple-400'
  };

  const statusIcons = {
    idle: '○',
    active: '●',
    delegating: '◐',
    waiting: '◑'
  };

  const AgentTreeItem = ({ agent, level = 0 }: { agent: Agent; level?: number }) => {
    return (
      <div className="agent-tree-item">
        <div
          className={`flex items-center py-1.5 px-2 hover:bg-gray-800 cursor-pointer text-sm ${
            selectedAgent?.id === agent.id ? 'bg-gray-800 border-l-2 border-blue-500' : ''
          }`}
          style={{ paddingLeft: `${level * 20 + 8}px` }}
          onClick={() => {
            if (agent.type === 'manager' && agent.children) {
              onToggleExpansion(agent.id);
            }
            onAgentSelect(agent);
          }}
        >
          <span className={`mr-2 status-indicator ${statusColors[agent.status]}`}>
            {statusIcons[agent.status]}
          </span>
          <span className="mr-2">
            {agent.type === 'manager' ? (
              agent.expanded ? '📂' : '📁'
            ) : (
              '🐍'
            )}
          </span>
          <span className="text-gray-300 flex-1">{agent.name}</span>
          {agent.type === 'manager' && (
            <span className="text-xs text-gray-500 ml-2">
              ({agent.children?.length || 0})
            </span>
          )}
        </div>
        {agent.type === 'manager' && agent.expanded && agent.children && (
          <div>
            {agent.children.map((child) => (
              <AgentTreeItem key={child.id} agent={child} level={level + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-64 bg-gray-850 border-r border-gray-700 overflow-y-auto">
      <div className="p-3 border-b border-gray-700">
        <h3 className="text-xs font-semibold text-gray-400 uppercase">Agent Hierarchy</h3>
      </div>
      <div className="py-2">
        {agents.map((agent) => (
          <AgentTreeItem key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
};

export default AgentHierarchy;
