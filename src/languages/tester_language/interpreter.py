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
from .ast import DirectiveType, ReadDirective, RunDirective, ChangeDirective, ReplaceDirective, FinishDirective, ReplaceItem
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
            elif isinstance(directive, ReplaceDirective):
                self._execute_replace(directive)
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
        command = directive.command

        if not any(command.startswith(allowed) for allowed in ALLOWED_COMMANDS):
            self._queue_self_prompt(f"RUN failed: Invalid command: {command}")
            return

        try:
            if os.name == "nt":
                from types import SimpleNamespace
                full_cmd = ["powershell.exe", "-Command", command]
                try:
                    proc = subprocess.Popen(
                        full_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        cwd=self.project_root,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    )
                    stdout_output, stderr_output = proc.communicate(timeout=120)
                    # Clip oversized outputs to avoid context issues
                    MAX_RUN_OUTPUT_CHARS = 100000
                    def _clip(s: str, limit: int = MAX_RUN_OUTPUT_CHARS):
                        return s if len(s) <= limit else s[:limit] + f"\n... [truncated {len(s) - limit} chars]"
                    stdout_output = _clip(stdout_output)
                    stderr_output = _clip(stderr_output)

                    # Wrap the captured output in a SimpleNamespace so we can
                    # uniformly reference `completed.stdout` / `completed.stderr`
                    # later, matching the pattern used in the manager & master
                    # interpreters.
                    completed = SimpleNamespace(stdout=stdout_output,
                                                stderr=stderr_output,
                                                returncode=proc.returncode)
                except subprocess.TimeoutExpired:
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)])
                    stdout_output, stderr_output = proc.communicate()
                    # Clip oversized outputs to avoid context issues
                    MAX_RUN_OUTPUT_CHARS = 100000
                    def _clip(s: str, limit: int = MAX_RUN_OUTPUT_CHARS):
                        return s if len(s) <= limit else s[:limit] + f"\n... [truncated {len(s) - limit} chars]"
                    stdout_output = _clip(stdout_output)
                    stderr_output = _clip(stderr_output)
                    prompt_msg = (
                        "RUN failed: Timed-out after 120 s. Most likely an infinite loop in the code. If this is test cases, try breaking up the test suite into multiple commands. If this is machine learning or data processing, ask the master agent to run this command as only the master agent can run commands without timeout.\n"
                        f"Output:\n{stdout_output}\nError:\n{stderr_output}"
                    )
                    self._queue_self_prompt(prompt_msg)
                    return

            stdout_output = completed.stdout.strip()
            stderr_output = completed.stderr.strip()

            if completed.returncode == 0:
                prompt = f"RUN succeeded: Output:\n{stdout_output}"
            else:
                if stdout_output and stderr_output:
                    prompt = f"RUN failed: Output:\n{stdout_output}\nError:\n{stderr_output}"
                elif stdout_output:
                    prompt = f"RUN failed: Output:\n{stdout_output}"
                elif stderr_output:
                    prompt = f"RUN failed: Error:\n{stderr_output}"
                else:
                    prompt = f"RUN failed with return code {completed.returncode}"

            self._queue_self_prompt(prompt)

        except Exception as e:
            self._queue_self_prompt(f"RUN failed: {str(e)}")

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

    def _execute_replace(self, directive: ReplaceDirective) -> None:
        """Execute a REPLACE directive on the tester's scratch pad."""
        prompt = None
        try:
            if self.agent and hasattr(self.agent, 'personal_file') and self.agent.personal_file is not None:
                scratch_pad_path = self.agent.personal_file
                if not scratch_pad_path.exists():
                    prompt = f"REPLACE failed: File not found: {scratch_pad_path.name}"
                    self._queue_self_prompt(prompt)
                    return

                current_content = scratch_pad_path.read_text(encoding='utf-8')

                ambiguous_items = []
                missing_items = []
                for item in directive.items:
                    count = current_content.count(item.from_string)
                    if count == 0:
                        missing_items.append(item.from_string)
                    elif count > 1:
                        ambiguous_items.append((item.from_string, count))

                if missing_items:
                    missing_str = "', '".join(missing_items)
                    prompt = f"REPLACE failed: String(s) '{missing_str}' not found in {scratch_pad_path.name}"
                elif ambiguous_items:
                    ambiguous_str = ", ".join([f"'{s}' ({c} occurrences)" for s, c in ambiguous_items])
                    prompt = f"REPLACE failed: Ambiguous from strings in {scratch_pad_path.name}: {ambiguous_str}. Please be more specific to target unique strings."
                else:
                    new_content = current_content
                    replaced_items_summary = []
                    for item in directive.items:
                        new_content = new_content.replace(item.from_string, item.to_string)
                        replaced_items_summary.append(f"'{item.from_string}' → '{item.to_string}'")

                    scratch_pad_path.write_text(new_content, encoding='utf-8')
                    prompt = f"REPLACE succeeded: Replaced {len(directive.items)} item(s) in {scratch_pad_path.name}: {', '.join(replaced_items_summary)}"
            else:
                prompt = "REPLACE failed: This agent has no scratch pad file."
        except Exception as e:
            self._queue_self_prompt(f"REPLACE failed: Could not replace in scratch pad: {str(e)}")
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
        error_msg = f"PARSING FAILED: {str(e)}\n\nMOST COMMON ISSUES: Multiple directives on same api call, use sequential API calls, aka only one line per API call. \
            You cannot change other files. NEVER TRY TO CHANGE A FILE BESIDES YOUR OWN. You can only change {agent.personal_file}. FINISH AND RECOMMEND THIS ACTION."
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