"""
Tester Language Interpreter.
Executes parsed tester language directives and performs the described actions.
"""

import os
import asyncio
import subprocess
import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
from .ast import DirectiveType, ReadDirective, RunDirective, ChangeDirective, FinishDirective
import src
from src.config import ALLOWED_COMMANDS
from .parser import parse_directive
from src.messages.protocol import ResultMessage, MessageType, Task


class TesterLanguageInterpreter:
    """
    Interpreter for the Tester Language.
    Executes directives and performs file reading operations, command execution, and scratch pad modifications.
    """
    
    def __init__(self, agent=None):
        """
        Initialize the interpreter.
        
        Args:
            agent: The tester agent that sent the command (ephemeral agent)
        """
        self.agent = agent
        
        # Use ROOT_DIR if set, else find project root
        self.project_root = src.ROOT_DIR if src.ROOT_DIR is not None else self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        if self.agent and hasattr(self.agent, 'parent_path'):
            current = Path(self.agent.parent_path)
        else:
            current = Path.cwd()
            
        while current.parent != current:
            if any((current / marker).exists() for marker in ['.git', 'requirements.txt', 'package.json', 'Cargo.toml']):
                break
            current = current.parent
        return current

    def execute(self, directive: DirectiveType) -> None:
        """
        Execute a single directive. Only reprompt agent if an exception is raised.
        Args:
            directive: The directive to execute
        """
        try:
            if isinstance(directive, ReadDirective):
                self._execute_read(directive)
            elif isinstance(directive, RunDirective):
                self._execute_run(directive)
            elif isinstance(directive, ChangeDirective):
                self._execute_change(directive)
            elif isinstance(directive, FinishDirective):
                self._execute_finish(directive)
            else:
                # Unknown directive type – queue a self prompt instead of directly invoking tester_spawner
                self._queue_self_prompt(f"Unknown directive type: {type(directive)}")
        except Exception as e:
            # Surface the exception back to the LLM via a queued prompt so that exactly
            # one follow-up turn is scheduled by the execute_directive() epilogue.
            self._queue_self_prompt(f"Exception during execution: {str(e)}")

    def _execute_read(self, directive: ReadDirective) -> None:
        """Execute a READ directive."""
        filename = directive.filename
        # Treat filename as a path relative to the project root
        file_path = self.project_root / filename
        prompt = None
        
        if file_path.exists():
            if self.agent and hasattr(self.agent, 'read_file'):
                self.agent.read_file(str(file_path))  # Let exceptions propagate to main execute method
                prompt = f"READ succeeded: {filename} was added to memory for future reads"
            else:
                prompt = f"READ failed: No agent or read_file method available"
        else:
            prompt = f"READ failed: File not found: {filename}"
        
        self._queue_self_prompt(prompt)

    def _execute_run(self, directive: RunDirective) -> None:
        """Execute a RUN directive and reprompt with the result string."""
        command = directive.command
        prompt = None
        try:
            if any(command.startswith(allowed) for allowed in ALLOWED_COMMANDS):
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=300
                )
                if result.returncode == 0:
                    prompt = f"RUN succeeded: Output:\n{result.stdout.strip()}"
                else:
                    # Show both stdout and stderr so agent can see test results even when tests fail
                    output = result.stdout.strip() if result.stdout.strip() else ""
                    error = result.stderr.strip() if result.stderr.strip() else ""
                    if output and error:
                        prompt = f"RUN failed: Output:\n{output}\nError:\n{error}"
                    elif output:
                        prompt = f"RUN failed: Output:\n{output}"
                    elif error:
                        prompt = f"RUN failed: Error:\n{error}"
                    else:
                        prompt = f"RUN failed: Command failed with return code {result.returncode}"
            else:
                prompt = f"RUN failed: Invalid command: {command}"
        except subprocess.TimeoutExpired:
            prompt = f"RUN failed: Command timed out after 5 minutes: {command}"
        except Exception as e:
            self._queue_self_prompt(f"RUN failed: {str(e)}")
            return
        self._queue_self_prompt(prompt)

    def _execute_change(self, directive: ChangeDirective) -> None:
        """Execute a CHANGE directive for the tester's scratch pad."""
        prompt = None
        try:
            if self.agent and hasattr(self.agent, 'personal_file') and self.agent.personal_file is not None:
                scratch_pad_path = self.agent.personal_file
                scratch_pad_path.parent.mkdir(parents=True, exist_ok=True)
                with open(scratch_pad_path, 'w', encoding='utf-8') as f:
                    f.write(directive.content)
                prompt = f"CHANGE succeeded: {scratch_pad_path.name} was updated with new content"
            else:
                prompt = "CHANGE failed: This agent has no scratch pad file."
        except Exception as e:
            self._queue_self_prompt(f"CHANGE failed: Could not write to scratch pad: {str(e)}")
            return
        self._queue_self_prompt(prompt)

    def _execute_finish(self, directive: FinishDirective) -> None:
        """Execute a FINISH directive for ephemeral tester agent."""
        if self.agent:
            # Clean up scratch pad before finishing
            if hasattr(self.agent, 'cleanup_scratch_pad'):
                self.agent.cleanup_scratch_pad()
            
            # Disable the watchdog before finishing
            if hasattr(self.agent, '_watchdog_task') and self.agent._watchdog_task is not None:
                try:
                    if not self.agent._watchdog_task.done():
                        self.agent._watchdog_task.cancel()
                except Exception:
                    pass
                self.agent._watchdog_task = None
                self.agent._watchdog_started = False
            
            # Ephemeral agents report their results back to the parent using proper orchestrator functions
            parent = getattr(self.agent, 'parent', None)
            if parent is not None:
                # Create a proper ResultMessage
                task = self.agent.active_task
                if task is None:
                    # Create a dummy task for ephemeral agents
                    task = Task(task_id=str(uuid.uuid4()), task_string="Ephemeral tester task")
                
                result_message = ResultMessage(
                    message_type=MessageType.RESULT,
                    sender=self.agent,  # Use the ephemeral agent itself as sender
                    recipient=parent,
                    message_id=str(uuid.uuid4()),
                    task=task.task if hasattr(task, 'task') else task,
                    result=directive.prompt.value
                )
                
                # Use appropriate prompter based on parent type
                result_prompt = f"Tester agent completed: {directive.prompt.value}"
                if hasattr(parent, 'is_manager') and parent.is_manager:
                    # Parent is a manager agent
                    from src.orchestrator.manager_prompter import manager_prompter
                    asyncio.create_task(manager_prompter(parent, result_prompt, result_message))
                else:
                    # Parent is a coder agent
                    from src.orchestrator.coder_prompter import coder_prompter
                    asyncio.create_task(coder_prompter(parent, result_prompt, result_message))
            else:
                # No parent: store result on agent for caller to access
                setattr(self.agent, "final_result", directive.prompt.value)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _queue_self_prompt(self, prompt: str) -> None:
        """Add a follow-up prompt directly to the tester agent's queue once.

        This avoids calling tester_spawner() from inside the interpreter, which
        could schedule overlapping api_call() invocations and duplicate console
        output. The wrapper at the end of execute_directive() will unstall and
        schedule exactly one api_call(), ensuring a single LLM turn.
        """
        if self.agent is None:
            return
        if prompt not in self.agent.prompt_queue:
            self.agent.prompt_queue.append(prompt)




# Convenience function
def execute_directive(directive_text: str, agent=None) -> None:
    """
    Convenience function to parse and execute a single directive string.
    After execution, sets agent.stall to False if agent is provided.
    
    Args:
        directive_text: The directive string to parse and execute
        agent: The tester agent that sent the command
    """
    # Always instantiate interpreter so we can reuse its helper to queue prompts
    interpreter = TesterLanguageInterpreter(agent=agent)

    try:
        directive = parse_directive(directive_text)
    except Exception as e:
        # Surface parsing errors back to the agent instead of crashing the pipeline.
        error_msg = f"PARSING FAILED: {str(e)}"
        # If we have an agent attached make sure to enqueue the error so the next
        # LLM turn can react accordingly. This avoids silent failures where the
        # stack-trace only ends up in the console.
        interpreter._queue_self_prompt(error_msg)

        # Ensure the agent is unstalled so that the follow-up api_call can run.
        if agent is not None:
            if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
                asyncio.create_task(agent.api_call())
        return  # Abort further execution since parsing did not succeed.

    # Normal execution path if parsing succeeded
    interpreter.execute(directive)

    if agent is not None:
        # Always unstall the agent so it can process future prompts
        agent.stall = False
        
        # If there are queued prompts, schedule api_call to process them
        if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
            asyncio.create_task(agent.api_call()) 