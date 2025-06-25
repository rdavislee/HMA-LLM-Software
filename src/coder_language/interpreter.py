"""
Coder Language Interpreter.
Executes parsed coder language directives and performs the described actions.
"""

import os
import asyncio
import subprocess
import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
from .ast import DirectiveType, ReadDirective, RunDirective, ChangeDirective, FinishDirective
from src import ROOT_DIR
from src.config import ALLOWED_COMMANDS
from .parser import parse_directive
from src.messages.protocol import ResultMessage, MessageType
from src.orchestrator.manager_prompter import manager_prompter

class CoderLanguageInterpreter:
    """
    Interpreter for the Coder Language.
    Executes directives and performs file system operations and command execution.
    """
    
    def __init__(self, base_path: str = ".", agent=None, own_file: str = None):
        """
        Initialize the interpreter.
        
        Args:
            base_path: Base directory for file operations (default: current directory)
            agent: The agent that sent the command
            own_file: The file this coder agent is responsible for
        """
        self.base_path = Path(base_path).resolve()
        self.agent = agent
        self.own_file = own_file
        
        # Use ROOT_DIR if set, else find project root
        self.project_root = ROOT_DIR if ROOT_DIR is not None else self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = self.base_path
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
                # Unknown directive type – queue a self prompt instead of directly invoking coder_prompter
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
        try:
            if file_path.exists():
                if self.agent and hasattr(self.agent, 'read_file'):
                    self.agent.read_file(str(file_path))
                    prompt = f"READ succeeded: {filename} was added to memory for future reads"
                else:
                    prompt = f"READ failed: No agent or read_file method available"
            else:
                prompt = f"READ failed: File not found: {filename}"
        except Exception as e:
            self._queue_self_prompt(f"READ failed: {filename} could not be added to memory: {str(e)}")
            return
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
                    prompt = f"RUN failed: {result.stderr.strip() or f'Command failed with return code {result.returncode}'}"
            else:
                prompt = f"RUN failed: Invalid command: {command}"
        except subprocess.TimeoutExpired:
            prompt = f"RUN failed: Command timed out after 5 minutes: {command}"
        except Exception as e:
            self._queue_self_prompt(f"RUN failed: {str(e)}")
            return
        self._queue_self_prompt(prompt)

    def _execute_change(self, directive: ChangeDirective) -> None:
        """Execute a CHANGE directive."""
        prompt = None
        try:
            if self.own_file is not None:
                file_path = self.base_path / self.own_file
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(directive.content)
                prompt = f"CHANGE succeeded: {self.own_file} was replaced with new content"
            else:
                prompt = "CHANGE failed: This agent has no assigned file."
        except Exception as e:
            self._queue_self_prompt(f"CHANGE failed: Could not write to {self.own_file}: {str(e)}")
            return
        self._queue_self_prompt(prompt)

    def _execute_finish(self, directive: FinishDirective) -> None:
        """Execute a FINISH directive."""
        if self.agent:
            try:
                self.agent.deactivate()
            except Exception as e:
                self._queue_self_prompt(f"FINISH failed: {str(e)}")
                return
            # Propagate result to parent if possible
            parent = getattr(self.agent, 'parent', None)
            if parent is not None:
                # Build ResultMessage
                task = getattr(self.agent, 'active_task', None)
                if task is None and hasattr(self.agent, 'active_task'):
                    task = self.agent.active_task
                # Fallback: create a dummy task if needed
                if task is None:
                    from src.messages.protocol import Task
                    task = Task(task_id=str(uuid.uuid4()), task_string="Task finished")
                result_message = ResultMessage(
                    message_type=MessageType.RESULT,
                    sender_id=str(self.agent.path),
                    recipient_id=str(parent.path),
                    message_id=str(uuid.uuid4()),
                    task=task.task if hasattr(task, 'task') else task,
                    result=directive.prompt.value
                )
                # Schedule parent's manager_prompter
                asyncio.create_task(manager_prompter(parent, directive.prompt.value, result_message))
            else:
                # No parent: store result on agent
                setattr(self.agent, "final_result", directive.prompt.value)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _queue_self_prompt(self, prompt: str) -> None:
        """Add a follow-up prompt directly to the coder agent's queue once.

        This avoids calling coder_prompter() from inside the interpreter, which
        could schedule overlapping api_call() invocations and duplicate console
        output. The wrapper at the end of execute_directive() will unstall and
        schedule exactly one api_call(), ensuring a single LLM turn.
        """
        if self.agent is None:
            return
        if prompt not in self.agent.prompt_queue:
            self.agent.prompt_queue.append(prompt)


# Convenience function
def execute_directive(directive_text: str, base_path: str = ".", agent=None, own_file: str = None) -> None:
    """
    Convenience function to parse and execute a single directive string.
    After execution, sets agent.stall to False if agent is provided.
    
    Args:
        directive_text: The directive string to parse and execute
        base_path: Base directory for file operations
        agent: The agent that sent the command
        own_file: The file this coder agent is responsible for
    """
    # Always instantiate interpreter so we can reuse its helper to queue prompts
    interpreter = CoderLanguageInterpreter(base_path=base_path, agent=agent, own_file=own_file)

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
            agent.stall = False
            if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
                try:
                    asyncio.create_task(agent.api_call())
                except Exception:
                    pass
        return  # Abort further execution since parsing did not succeed.

    # Normal execution path if parsing succeeded
    interpreter.execute(directive)

    if agent is not None:
        # Check agent prompt queue and if not empty, call api_call
        if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
            asyncio.create_task(agent.api_call())
        else:
            agent.stall = False