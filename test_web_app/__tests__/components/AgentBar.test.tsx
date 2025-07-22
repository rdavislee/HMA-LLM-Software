import { render, screen, waitFor } from '../../setup/testUtils';
import { AgentBar } from '@/components/AgentBar';
import { useSocketEvent } from '@/hooks/useSocketEvent';

// Mock the useSocketEvent hook
jest.mock('@/hooks/useSocketEvent');

describe('AgentBar Component', () => {
  const mockUseSocketEvent = useSocketEvent as any;

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseSocketEvent.mockImplementation(() => {});
  });

  describe('Rendering', () => {
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
  });

  describe('Agent Status Display', () => {
    it('should display correct status indicators', () => {
      const agents = [
        { id: '1', name: 'Active', status: 'active' as const },
        { id: '2', name: 'Waiting', status: 'waiting' as const },
        { id: '3', name: 'Error', status: 'error' as const },
        { id: '4', name: 'Complete', status: 'completed' as const },
      ];

      const { container } = render(<AgentBar agents={agents} />);

      // Check for status dots with correct colors
      const statusDots = container.querySelectorAll('[style*="backgroundColor"]');
      expect(statusDots.length).toBeGreaterThan(0);
      
      // Check agent names are displayed
      expect(screen.getByText('Active')).toBeInTheDocument();
      expect(screen.getByText('Waiting')).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Complete')).toBeInTheDocument();
    });

    it('should show correct status colors', () => {
      const agents = [
        { id: '1', name: 'Worker', status: 'active' as const },
      ];

      const { container } = render(<AgentBar agents={agents} />);
      
      // Check for green status dot for active agent
      const statusDot = container.querySelector('[style*="backgroundColor: #10B981"]');
      expect(statusDot).toBeInTheDocument();
    });
  });

  describe('Phase Badges', () => {
    it('should display phase badges with correct styling', () => {
      const agents = [
        { id: '1', name: 'Spec', status: 'active' as const, phase: 'spec' as const },
        { id: '2', name: 'Test', status: 'active' as const, phase: 'test' as const },
        { id: '3', name: 'Impl', status: 'active' as const, phase: 'impl' as const },
      ];

      render(<AgentBar agents={agents} />);

      expect(screen.getByText('spec')).toHaveClass('bg-blue-500/20');
      expect(screen.getByText('test')).toHaveClass('bg-amber-500/20');
      expect(screen.getByText('impl')).toHaveClass('bg-violet-500/20');
    });
  });

  describe('Live Counters', () => {
    it('should calculate and display total tokens', () => {
      const agents = [
        { id: '1', name: 'Agent1', status: 'active' as const, tokens: 1000 },
        { id: '2', name: 'Agent2', status: 'active' as const, tokens: 2000 },
      ];

      render(<AgentBar agents={agents} />);
      
      expect(screen.getByText('3,000')).toBeInTheDocument();
      expect(screen.getByText('tokens')).toBeInTheDocument();
    });

    it('should calculate and display total cost', () => {
      const agents = [
        { id: '1', name: 'Agent1', status: 'active' as const, cost: 0.25 },
        { id: '2', name: 'Agent2', status: 'active' as const, cost: 0.75 },
      ];

      render(<AgentBar agents={agents} />);
      
      expect(screen.getByText('1.00')).toBeInTheDocument();
      expect(screen.getByText('$')).toBeInTheDocument();
    });
  });

  describe('WebSocket Integration', () => {
    it('should register agent_update event listener', () => {
      render(<AgentBar />);
      
      expect(mockUseSocketEvent).toHaveBeenCalledWith(
        'agent_update',
        expect.any(Function)
      );
    });

    it('should handle agent updates from WebSocket', async () => {
      let agentUpdateHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'agent_update') {
          agentUpdateHandler = handler;
        }
      });

      render(<AgentBar />);

      // Simulate WebSocket update
      const update = {
        agentId: 'new-agent',
        status: 'active',
        task: 'New task',
        progress: 75,
      };

      agentUpdateHandler(update);

      await waitFor(() => {
        expect(screen.getByText('new')).toBeInTheDocument(); // agent name from ID
        expect(screen.getByText('New task')).toBeInTheDocument();
      });
    });

    it('should remove completed agents after delay', async () => {
      let agentUpdateHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'agent_update') {
          agentUpdateHandler = handler;
        }
      });

      render(<AgentBar />);

      // Add agent
      agentUpdateHandler({
        agentId: 'temp-agent',
        status: 'active',
        task: 'Temporary task',
      });

      await waitFor(() => {
        expect(screen.getByText('temp')).toBeInTheDocument();
      });

      // Mark as completed
      agentUpdateHandler({
        agentId: 'temp-agent',
        status: 'completed',
      });

      // Should still be visible immediately
      expect(screen.getByText('temp')).toBeInTheDocument();

      // Wait for removal delay (3 seconds)
      await waitFor(() => {
        expect(screen.queryByText('temp')).not.toBeInTheDocument();
      }, { timeout: 4000 });
    });
  });

  describe('Task Display', () => {
    it('should truncate long task descriptions', () => {
      const longTask = 'This is a very long task description that should be truncated to fit in the available space without breaking the layout';
      const agents = [
        {
          id: '1',
          name: 'Agent',
          status: 'active' as const,
          task: longTask,
        },
      ];

      render(<AgentBar agents={agents} />);
      
      const taskElement = screen.getByText(longTask);
      expect(taskElement).toHaveClass('truncate', 'max-w-[200px]');
    });
  });

  describe('Phase Detection', () => {
    it('should determine phase from task content', async () => {
      let agentUpdateHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'agent_update') {
          agentUpdateHandler = handler;
        }
      });

      render(<AgentBar />);

      const testCases = [
        { task: 'Writing specification', expectedPhase: 'spec' },
        { task: 'Running tests', expectedPhase: 'test' },
        { task: 'Implementing feature', expectedPhase: 'impl' },
      ];

      for (const { task, expectedPhase } of testCases) {
        agentUpdateHandler({
          agentId: `agent-${expectedPhase}`,
          status: 'active',
          task,
        });

        await waitFor(() => {
          const phaseElements = screen.getAllByText(expectedPhase);
          expect(phaseElements.length).toBeGreaterThan(0);
        });
      }
    });

    it('should determine phase from agent ID', async () => {
      let agentUpdateHandler: any;
      mockUseSocketEvent.mockImplementation((event: string, handler: any) => {
        if (event === 'agent_update') {
          agentUpdateHandler = handler;
        }
      });

      render(<AgentBar />);

      agentUpdateHandler({
        agentId: 'architect-123',
        status: 'active',
      });

      await waitFor(() => {
        expect(screen.getByText('spec')).toBeInTheDocument();
      });
    });
  });

  describe('Empty State', () => {
    it('should show default agents when agent list is empty', () => {
      render(<AgentBar agents={[]} />);
      
      // Should show default agents
      expect(screen.getByText('Architect')).toBeInTheDocument();
      expect(screen.getByText('Validator')).toBeInTheDocument();
      expect(screen.getByText('Builder')).toBeInTheDocument();
    });
  });
});