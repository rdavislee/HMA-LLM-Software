# Master Language

The Master Language is a specialized language for master agents in the hierarchical multi-agent software development framework. It provides a high-level coordination interface for orchestrating the entire system through a single root manager agent.

## Overview

Master agents are the top-level orchestrators in the agent hierarchy. They coordinate all other agents and manage the overall workflow through their single child - the root manager agent. The Master Language is based on the Manager Language but simplified for high-level coordination.

## Architecture

```
Master Agent (uses Master Language)
└── Root Manager Agent (uses Manager Language)
    ├── Child Manager Agents
    ├── Coder Agents
    └── Ephemeral Agents
```

## Key Differences from Manager Language

1. **Single Delegation**: DELEGATE only needs a prompt (always delegates to root agent)
2. **No File Creation/Deletion**: Only READ operations are allowed
3. **Documentation Focus**: UPDATE_README becomes UPDATE_DOCUMENTATION
4. **High-Level Coordination**: Designed for system-wide orchestration

## Directives

The Master Language supports the following directives:

### DELEGATE
Delegate a task to the root manager agent (no target needed).

**Syntax:** `DELEGATE PROMPT="task description"`
**Example:** `DELEGATE PROMPT="Create a web application with authentication"`

### READ
Read files or folder documentation to understand the system state.

**Syntax:** `READ target1, target2, ...`
**Example:** `READ file "big_picture.md", folder "src"`

### SPAWN
Create ephemeral agents for specialized tasks (same as Manager Language).

**Syntax:** `SPAWN ephemeral_type PROMPT="task", ...`
**Example:** `SPAWN tester PROMPT="Analyze system performance and bottlenecks"`

### UPDATE_DOCUMENTATION
Update the master agent's high-level documentation.

**Syntax:** `UPDATE_DOCUMENTATION CONTENT="documentation content"`
**Example:** `UPDATE_DOCUMENTATION CONTENT="System now supports microservices architecture"`

### RUN
Execute system-level commands for monitoring and analysis.

**Syntax:** `RUN "command"`
**Example:** `RUN "find . -name '*.py' | wc -l"`

### WAIT
Wait for the root agent or ephemeral agents to complete their tasks.

**Syntax:** `WAIT`

### FINISH
Complete the overall system coordination task.

**Syntax:** `FINISH PROMPT="completion message"`
**Example:** `FINISH PROMPT="System successfully orchestrated and all requirements met"`

## Typical Workflow

A typical master agent workflow:

1. **System Analysis**: Read high-level documentation and project structure
2. **Root Delegation**: Delegate the main task to the root manager agent
3. **Monitoring**: Spawn ephemeral agents for system monitoring if needed
4. **Coordination**: Wait for completion and handle any system-wide issues
5. **Documentation**: Update high-level documentation with system changes
6. **Completion**: Finish with system-wide summary

## Example Usage

```python
from src.languages.master_language import MasterLanguageInterpreter

# Initialize interpreter for a master agent
interpreter = MasterLanguageInterpreter(agent=master_agent)

# Read system documentation
interpreter.execute('READ file "big_picture.md"')
interpreter.execute('READ folder "src"')

# Delegate main task to root agent
interpreter.execute('DELEGATE PROMPT="Build a microservices application"')

# Monitor progress
interpreter.execute('SPAWN tester PROMPT="Monitor system resource usage during build"')

# Wait for completion
interpreter.execute('WAIT')

# Update high-level documentation
interpreter.execute('UPDATE_DOCUMENTATION CONTENT="System successfully migrated to microservices"')

# Complete coordination
interpreter.execute('FINISH PROMPT="All system requirements successfully implemented"')
```

## Context Management

The interpreter maintains execution context that tracks:

- `delegations`: Single delegation to root agent
- `spawns`: List of ephemeral agents spawned
- `reads`: List of files/folders read for system understanding
- `commands`: List of system commands executed
- `documentation_updates`: Updates to master's documentation
- `finished`: Boolean indicating if coordination is complete
- `waiting`: Whether waiting for agents to complete

## Integration with Agent Hierarchy

The Master Language integrates with the broader agent system:

- **Master Agent**: Uses Master Language for high-level coordination
- **Root Manager Agent**: Receives delegations and uses Manager Language
- **System Monitoring**: Spawns ephemeral agents for system-wide analysis
- **Documentation**: Maintains high-level system documentation

## Key Principles

1. **Single Root**: Master only delegates to one root manager agent
2. **High-Level Focus**: Deals with system-wide concerns, not implementation details
3. **Coordination**: Orchestrates rather than implements
4. **Documentation**: Maintains system-level documentation
5. **Monitoring**: Can spawn ephemeral agents for system analysis

## Error Handling

The language includes comprehensive error handling:

- Validation that root agent exists before delegation
- Command validation using system-allowed commands
- File system error handling for READ operations
- Parsing errors with helpful error messages

## Future Enhancements

Potential future additions to the Master Language:

- Support for multiple root agents in distributed systems
- Integration with deployment and orchestration tools
- Enhanced system monitoring and alerting capabilities
- Support for system-wide rollback and recovery operations
- Integration with external APIs and services

## Differences from Other Agent Languages

| Feature | Master Language | Manager Language | Coder Language |
|---------|----------------|------------------|----------------|
| Delegation | Single item | Multiple items | None |
| File Operations | Read only | Create/Delete/Read | Own file only |
| Documentation | UPDATE_DOCUMENTATION | UPDATE_README | None |
| Scope | System-wide | Directory-level | File-level |
| Purpose | Coordination | Management | Implementation | 