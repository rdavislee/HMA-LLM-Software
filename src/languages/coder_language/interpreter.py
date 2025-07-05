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
from .ast import DirectiveType, ReadDirective, RunDirective, ChangeDirective, ReplaceDirective, InsertDirective, SpawnDirective, WaitDirective, FinishDirective
import src
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
        self.project_root = src.ROOT_DIR if src.ROOT_DIR is not None else self._find_project_root()
    
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
            elif isinstance(directive, ReplaceDirective):
                self._execute_replace(directive)
            elif isinstance(directive, InsertDirective):
                self._execute_insert(directive)
            elif isinstance(directive, SpawnDirective):
                self._execute_spawn(directive)
            elif isinstance(directive, WaitDirective):
                self._execute_wait(directive)
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
        """Execute a RUN directive (simplified sync call – watchdog handles hard hangs)."""
        command = directive.command

        # Disallow commands outside the approved list
        if not any(command.startswith(allowed) for allowed in ALLOWED_COMMANDS):
            self._queue_self_prompt(f"RUN failed: Invalid command: {command}")
            return

        try:
            if os.name == "nt":
                full_cmd = ["powershell.exe", "-Command", command]
                completed = subprocess.run(
                    full_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.project_root,
                    check=False,
                )
            else:
                completed = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.project_root,
                    check=False,
                )

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

    def _execute_replace(self, directive: ReplaceDirective) -> None:
        """Execute a REPLACE directive with multiple items and ambiguity detection."""
        prompt = None
        try:
            if self.own_file is not None:
                file_path = self.base_path / self.own_file
                # If file does not exist, throw error and do not create it
                if not file_path.exists():
                    prompt = f"REPLACE failed: File not found: {self.own_file}"
                    self._queue_self_prompt(prompt)
                    return
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                # Check for ambiguous from_strings (multiple occurrences)
                ambiguous_items = []
                missing_items = []
                for item in directive.items:
                    count = current_content.count(item.from_string)
                    if count == 0:
                        missing_items.append(item.from_string)
                    elif count > 1:
                        ambiguous_items.append((item.from_string, count))
                # Report missing strings
                if missing_items:
                    missing_str = "', '".join(missing_items)
                    prompt = f"REPLACE failed: String(s) '{missing_str}' not found in {self.own_file}"
                # Report ambiguous strings
                elif ambiguous_items:
                    ambiguous_str = ", ".join([f"'{s}' ({c} occurrences)" for s, c in ambiguous_items])
                    prompt = f"REPLACE failed: Ambiguous from strings in {self.own_file}: {ambiguous_str}. Please be more specific to target unique strings."
                else:
                    # All strings are present and unique, proceed with replacements
                    new_content = current_content
                    replaced_items = []
                    for item in directive.items:
                        new_content = new_content.replace(item.from_string, item.to_string)
                        replaced_items.append(f"'{item.from_string}' → '{item.to_string}'")
                    # Write back to file (robust like CHANGE)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        f.flush()
                    replaced_str = ", ".join(replaced_items)
                    prompt = f"REPLACE succeeded: Replaced {len(directive.items)} item(s) in {self.own_file}: {replaced_str}"
            else:
                prompt = "REPLACE failed: This agent has no assigned file."
        except Exception as e:
            self._queue_self_prompt(f"REPLACE failed: Could not replace in {self.own_file}: {str(e)}")
            return
        self._queue_self_prompt(prompt)

    def _execute_insert(self, directive: InsertDirective) -> None:
        """Execute an INSERT directive."""
        prompt = None
        try:
            if self.own_file is not None:
                file_path = self.base_path / self.own_file
                # If file does not exist, throw error and do not create it
                if not file_path.exists():
                    prompt = f"INSERT failed: File not found: {self.own_file}"
                    self._queue_self_prompt(prompt)
                    return
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                # Check for from_string existence and ambiguity
                count = current_content.count(directive.from_string)
                if count == 0:
                    prompt = f"INSERT failed: String '{directive.from_string}' not found in {self.own_file}"
                elif count > 1:
                    prompt = f"INSERT failed: Ambiguous from string '{directive.from_string}' in {self.own_file}: {count} occurrences. Please be more specific to target a unique string."
                else:
                    # Perform string insertion - insert to_string at the end of from_string
                    new_content = current_content.replace(directive.from_string, directive.from_string + directive.to_string)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        f.flush()
                    prompt = f"INSERT succeeded: Inserted '{directive.to_string}' after '{directive.from_string}' in {self.own_file}"
            else:
                prompt = "INSERT failed: This agent has no assigned file."
        except Exception as e:
            self._queue_self_prompt(f"INSERT failed: Could not insert in {self.own_file}: {str(e)}")
            return
        self._queue_self_prompt(prompt)

    def _execute_spawn(self, directive: SpawnDirective) -> None:
        """Execute a SPAWN directive for ephemeral agents."""
        if not self.agent:
            return

        # Spawn ephemeral agents for each item
        for item in directive.items:
            ephemeral_type = item.ephemeral_type.type_name
            prompt = item.prompt.value
            
            # Currently only support tester ephemeral agents
            if ephemeral_type == "tester":
                # Create a proper Task object for the tester
                from src.messages.protocol import Task
                task = Task(
                    task_id=str(hash(ephemeral_type + prompt + str(time.time()))),
                    task_string=prompt
                )
                
                from src.orchestrator.tester_spawner import tester_spawner
                asyncio.create_task(tester_spawner(self.agent, prompt, task))
            else:
                self._queue_self_prompt(f"SPAWN failed: Unknown ephemeral type: {ephemeral_type}")
                return


    def _execute_wait(self, directive: WaitDirective) -> None:
        """Execute a WAIT directive.
        
        If the coder currently has no active ephemeral agents the instruction makes
        no sense – in that case immediately queue a follow-up prompt so that
        the LLM can react instead of stalling indefinitely.
        """
        if not self.agent:
            return

        active_ephemeral_agents = getattr(self.agent, "active_ephemeral_agents", [])

        if active_ephemeral_agents:
            # There are still running ephemeral agents – do nothing (the prompt loop
            # will naturally resume once they complete).
            return None

        # No active ephemeral agents ➔ inform the LLM so it can decide the next step.
        self._queue_self_prompt("WAIT failed: No active ephemeral agents to wait for")
        return None

    def _execute_finish(self, directive: FinishDirective) -> None:
        """Execute a FINISH directive."""
        if self.agent:
            # Check if there are active ephemeral agents
            if hasattr(self.agent, 'active_ephemeral_agents') and self.agent.active_ephemeral_agents:
                self._queue_self_prompt(f"FINISH failed: Cannot finish with {len(self.agent.active_ephemeral_agents)} active ephemeral agents still running")
                return
                
            # Save task BEFORE deactivating (deactivate sets active_task to None)
            task = self.agent.active_task
            parent = getattr(self.agent, 'parent', None)
            
            try:
                self.agent.deactivate()
            except Exception as e:
                self._queue_self_prompt(f"FINISH failed: {str(e)}")
                return
                
            # Propagate result to parent if possible
            if parent is not None:
                # Build ResultMessage
                # Fallback: create a dummy task if needed
                if task is None:
                    from src.messages.protocol import Task
                    task = Task(task_id=str(uuid.uuid4()), task_string="Task finished")
                result_message = ResultMessage(
                    message_type=MessageType.RESULT,
                    sender=self.agent,
                    recipient=parent,
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
        error_msg = f"PARSING FAILED: {str(e)}\n\nMOST COMMON ISSUE: Multiple directives on same api call, use sequential API calls, aka only one line per API call"
        # If we have an agent attached make sure to enqueue the error so the next
        # LLM turn can react accordingly. This avoids silent failures where the
        # stack-trace only ends up in the console.
        interpreter._queue_self_prompt(error_msg)

        # Ensure the agent is unstalled so that the follow-up api_call can run.
        if agent is not None:
            if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
                try:
                    asyncio.create_task(agent.api_call())
                except Exception:
                    pass
        return  # Abort further execution since parsing did not succeed.

    # Normal execution path if parsing succeeded
    interpreter.execute(directive)

    if agent is not None:
        # Always unstall the agent so it can process future prompts
        agent.stall = False
        
        # If there are queued prompts, schedule api_call to process them
        if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
            asyncio.create_task(agent.api_call())