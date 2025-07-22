import { useLLM } from '../contexts/LLMContext';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { 
  Activity, 
  Bot, 
  Code, 
  FolderTree, 
  Loader2, 
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react';
import { cn } from './ui/utils';

interface AgentStatusPanelProps {
  className?: string;
  compact?: boolean;
}

const STATUS_ICONS = {
  active: <Activity className="h-4 w-4 text-green-500" />,
  inactive: <Clock className="h-4 w-4 text-gray-400" />,
  waiting: <Loader2 className="h-4 w-4 text-yellow-500 animate-spin" />,
  delegating: <FolderTree className="h-4 w-4 text-blue-500" />,
  completed: <CheckCircle className="h-4 w-4 text-green-600" />,
  error: <AlertCircle className="h-4 w-4 text-red-500" />,
};

const AGENT_ICONS = {
  master: <Bot className="h-4 w-4" />,
  manager: <FolderTree className="h-4 w-4" />,
  coder: <Code className="h-4 w-4" />,
  tester: <CheckCircle className="h-4 w-4" />,
  ephemeral: <Activity className="h-4 w-4" />,
};

export function AgentStatusPanel({ className, compact = false }: AgentStatusPanelProps) {
  const { agents, rootAgentId, activeAgents, agentTokenUsage } = useLLM();

  // Build agent hierarchy
  const buildHierarchy = (agentId: string, level = 0): JSX.Element[] => {
    const agent = agents[agentId];
    if (!agent) return [];

    const elements: JSX.Element[] = [];
    
    // Add current agent
    elements.push(
      <div
        key={agentId}
        className={cn(
          "flex items-center gap-2 py-2 px-3 rounded-lg transition-colors",
          agent.status === 'active' && "bg-primary/5",
          agent.status === 'error' && "bg-red-50 dark:bg-red-950"
        )}
        style={{ marginLeft: `${level * 20}px` }}
      >
        <div className="flex items-center gap-2 flex-1">
          {STATUS_ICONS[agent.status]}
          {AGENT_ICONS[agent.type]}
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium truncate max-w-[200px]" title={agent.path}>
                {agent.path.split('/').pop() || agent.path}
              </span>
              <Badge variant="outline" className="text-xs">
                {agent.type}
              </Badge>
            </div>
            {agent.task && (
              <p className="text-xs text-muted-foreground truncate mt-1" title={agent.task}>
                {agent.task}
              </p>
            )}
          </div>
          {agent.contextSize !== undefined && agent.maxContextSize && (
            <div className="flex flex-col items-end gap-1">
              <span className="text-xs text-muted-foreground">
                {agent.contextSize.toLocaleString()} / {agent.maxContextSize.toLocaleString()}
              </span>
              <Progress 
                value={(agent.contextSize / agent.maxContextSize) * 100} 
                className="w-[60px] h-1"
              />
            </div>
          )}
          {(agentTokenUsage[agentId] || 0) > 0 && (
            <Badge variant="secondary" className="text-xs">
              {(agentTokenUsage[agentId] || 0).toLocaleString()} tokens
            </Badge>
          )}
        </div>
      </div>
    );

    // Add children recursively
    if (agent.children) {
      agent.children.forEach(childId => {
        elements.push(...buildHierarchy(childId, level + 1));
      });
    }

    return elements;
  };

  if (compact) {
    return (
      <div className={cn("flex items-center gap-4", className)}>
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            {activeAgents.length} active agents
          </span>
        </div>
        {activeAgents.length > 0 && (
          <div className="flex items-center gap-2">
            {activeAgents.slice(0, 3).map(agent => (
              <Badge key={agent.id} variant="secondary" className="text-xs">
                {agent.path.split('/').pop()}
              </Badge>
            ))}
            {activeAgents.length > 3 && (
              <span className="text-xs text-muted-foreground">
                +{activeAgents.length - 3} more
              </span>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center justify-between">
          <span>Agent Hierarchy</span>
          <Badge variant="outline" className="font-normal">
            {Object.keys(agents).length} agents
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px] px-6 pb-4">
          {rootAgentId ? (
            <div className="space-y-1">
              {buildHierarchy(rootAgentId)}
            </div>
          ) : (
            <div className="flex items-center justify-center h-[200px] text-muted-foreground">
              <div className="text-center">
                <Bot className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No agents active</p>
                <p className="text-xs mt-1">Agents will appear here when a project starts</p>
              </div>
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}