# Broad Picture

- API costs get very high when using coding agents in large software construction projects because the context window gets very large. Also, as the context window get larger, the AI degrades in performance. This is why entire software construction projects cannot be completed in one prompt.
- Solution: Utilize chain of LLM ideas and a hierarchical structure mirroring a GitHub repository to split large software construction tasks into smaller easier-to-complete tasks.
- How: each folder and file will get its own agent, that is only active when called upon by its parent. Folders will have manager agents and files will have coder agents. We will use a hierarchical structure, where parent agents can decide which of their children become active by prompting them with a task. Agents will "forget" everything upon completion of their task, and report what they did back to their parent, who can review their work. All agents will maintain a readme for future iterations of itself to use as a guide. In this manner, we can keep context windows small but filled with enough information for the job to be finished, saving API costs.
- **Master agents** sit at the top of the hierarchy, orchestrating the entire project through a single child: the root manager agent. Master agents are responsible for high-level coordination, documentation, and phase management (see below).
- Manager agents will have the ability to create and delete files inside of their folder. They will be able to Delegate tasks to their children. The delegation process will be set up so that a manager will be able to delegate many tasks at once, which will all run concurrently, if the manager decides the tasks are not interdependent. Therefore, the manager will also have a wait command, which they can use when one of their children finishes their task but another hasn't. In this case, they will also be able to re-task the returning child instead of waiting, as well, or do another action. If codes are interdependent, the manager agent can decide to do them one by one by simply delegating one at a time.
- All agents will be able to read all codes in the code base if they deem necessary, and the entire codebase structure will be part of every prompt. All agents will also be able to run terminal commands, although this should be relatively limited, maybe to just running tests.
- A main goal of this project, in order to keep context windows small, is that agents will produce interfaces (the initial language we will apply this to is typescript), and then there will be separate files with implementations. This way, readers only have to read the interface, where the spec, contract of each function, preconditions, postconditions, etc exist so that other agents can use those functions with out having to process thousands of lines of the actual implementation. Also, it enables more concurrent development, because other agents can use the functions before they have been implementing, knowing that they will be implemented eventually.
- Coder agents will automatically read their own code in their first prompt, and have the ability to read any other codes and modify their own code.
- Test first programming will be ingrained into the agents, mirroring how it is actually done in real life. This can be pictured as a project starting as a wave of prompts going down the src side for agents to spec their ADTs, then the wave returns to the top after specs are done, and the wave travels to the test side of the repository, where agents partition and then build their test suites based on the specs. Then, the wave travels back up the agent tree, and then back down the src side, where agents can begin implementation, using the tests along the way. The agents will continue waving up and down the tree until the entire project is finished.
- There will exist a documentation folder, which is filled with necessary readings, files, libraries, etc by the human, which models will be able to access. Managers will inform children which of these documentations will be necessary for their task.

## Master Agents: System Orchestration and Three-Phase Workflow

**Master agents** are the top-level orchestrators in the agent hierarchy. Each master agent manages exactly one child: the root manager agent, which in turn manages the rest of the agent tree (managers, coders, ephemeral agents). Master agents are responsible for high-level project coordination, maintaining system-level documentation (typically in `documentation.md`), and guiding the project through three distinct phases:

### Phase 1: Product Understanding
- The master agent interacts directly with the human, asking clarifying questions to deeply understand the project requirements, constraints, and success criteria.
- No delegation or child agent activation occurs in this phase.
- The master agent continuously updates the high-level documentation with its growing understanding.
- This phase continues until the master agent is confident it has a clear, actionable specification.

### Phase 2: Structure Stage
- The master agent sets up the project repository structure, creating directories and placeholder files as needed (using commands like `mkdir` and `touch`).
- The structure is designed to match the scale and needs of the project, following best practices for the chosen technology stack.
- No delegation occurs in this phase; the master agent acts directly on the file system.
- The master agent ensures the structure supports parallel development and clear separation of concerns.

### Phase 3: Delegation and Project Phases
- Only after completing phases 1 and 2 does the master agent begin delegating work to the root manager agent.
- The master agent breaks the project into logical phases (e.g., interfaces, tests, implementations, integration, verification) and delegates each phase to the root manager.
- Between phases, the master agent can spawn ephemeral tester agents for system-wide verification, update documentation, and wait for completion of delegated tasks.
- The master agent ensures quality gates are met before moving to the next phase and maintains a high-level view of project progress.

**Key responsibilities of the master agent:**
- Maintain and update high-level documentation (`documentation.md`)
- Coordinate the overall workflow and phase transitions
- Ensure the project structure is appropriate and scalable
- Delegate work only to the root manager agent (never directly to lower-level agents)
- Use tester agents for system-wide analysis and verification
- Interact with the human for clarification, progress updates, and final approval

**Master agents do not implement code directly or manage individual files/folders.** Their focus is on system-level architecture, documentation, and orchestration.

---

## Ephemeral Agents for Context-Heavy Operations

- **Ephemeral Agent Concept**: To further optimize context management and API costs, the system includes ephemeral agents that are spawned temporarily by regular coder or manager agents to handle specific context-heavy operations. These agents are designed to be created for a task, execute it, report results, and then be destroyed - never maintaining persistent state.

- **Tester Agents**: The primary implementation of ephemeral agents are tester agents, which specialize in testing and diagnostic operations. Manager and coder agents can spawn tester agents when they need to:
  - Run comprehensive test suites and analyze failures
  - Debug complex issues that require temporary debugging code
  - Perform code analysis, linting, and coverage reporting  
  - Investigate test failures without cluttering the parent agent's context
  - Experiment with different testing approaches using temporary scratch code

- **Scratch Pad System**: Each tester agent gets a personal scratch pad file for writing debugging code, temporary functions, and testing experiments. This allows them to:
  - Write and execute debugging scripts without affecting project files
  - Test hypotheses about code behavior in isolation
  - Create temporary helper functions for analysis
  - The scratch pad is automatically cleaned up when the tester agent completes its task

- **Context Isolation**: Ephemeral agents prevent context pollution by handling all the messy details of testing and debugging in their own isolated context. The parent agent receives only a concise summary of findings rather than pages of test output, debug traces, and experimental code.

- **Workflow Integration**: Tester agents integrate seamlessly with the test-first programming approach:
  - When coder agents need to understand test failures, they spawn tester agents to investigate
  - Manager agents can delegate testing verification tasks to tester agents
  - Tester agents can run comprehensive test suites and report which areas need attention
  - Results feed back into the main agent hierarchy for informed decision-making

- **Cost Optimization**: By using ephemeral agents for context-heavy operations, we achieve additional API cost savings:
  - Testing output and debug information doesn't accumulate in persistent agent contexts  
  - Expensive diagnostic operations are isolated and cleaned up immediately
  - Parent agents get actionable summaries instead of raw debugging data
  - Multiple tester agents can work in parallel without context interference