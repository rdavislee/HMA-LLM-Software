"""
Master Language Interpreter.
Executes parsed master language directives and performs the described actions.
Based on the manager language but simplified for top-level coordination.
"""

import os
import json
import asyncio
import subprocess
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from .ast import DirectiveType, DelegateDirective, SpawnDirective, FinishDirective, ReadDirective, WaitDirective, RunDirective, UpdateDocumentationDirective
from src.messages.protocol import TaskMessage, Task, MessageType, ResultMessage
from src.config import ALLOWED_COMMANDS
from .parser import parse_directive
import src


class MasterLanguageInterpreter:
    """
    Interpreter for the Master Language.
    Executes directives and performs high-level coordination operations.
    """
    
    def __init__(self, agent=None):
        """
        Initialize the interpreter.
        Args:
            agent: The master agent that sent the command
        """
        self.agent = agent
        if src.ROOT_DIR is None:
            raise RuntimeError("ROOT_DIR is not set. Please call set_root_dir(path) before using the interpreter.")
        self.root_dir = src.ROOT_DIR
    
    def execute(self, directive: DirectiveType) -> None:
        """
        Execute a single directive.
        
        Args:
            directive: The directive to execute
        """
        try:
            if isinstance(directive, DelegateDirective):
                self._execute_delegate(directive)
            elif isinstance(directive, SpawnDirective):
                self._execute_spawn(directive)
            elif isinstance(directive, FinishDirective):
                self._execute_finish(directive)
            elif isinstance(directive, ReadDirective):
                self._execute_read(directive)
            elif isinstance(directive, WaitDirective):
                self._execute_wait(directive)
            elif isinstance(directive, RunDirective):
                self._execute_run(directive)
            elif isinstance(directive, UpdateDocumentationDirective):
                self._execute_update_documentation(directive)
            else:
                # Unknown directive type – queue a self prompt rather than invoking master_prompter directly
                self._queue_self_prompt(f"Unknown directive type: {type(directive)}")
        except Exception as e:
            # Queue the error instead of calling master_prompter directly so that
            # exactly one follow-up turn is scheduled by execute_directive().
            self._queue_self_prompt(f"Error executing directive {type(directive).__name__}: {str(e)}")

    def _execute_delegate(self, directive: DelegateDirective) -> None:
        """Execute a DELEGATE directive (always delegates to root agent)."""
        if not self.agent:
            return
            
        # Master agent delegates to its single root agent
        if not hasattr(self.agent, 'root') or not self.agent.root:
            self._queue_self_prompt("DELEGATE failed: No root agent available")
            return
        
        prompt = directive.prompt.value
        root_agent = self.agent.root
        
        # Create TaskMessage for the root agent
        task = Task(
            task_id=str(hash("root" + prompt + str(time.time()))),
            task_string=prompt
        )
        task_message = TaskMessage(
            message_type=MessageType.DELEGATION,
            sender=self.agent,
            recipient=root_agent,
            message_id=str(hash(task.task_id)),
            task=task
        )
        
        # Call appropriate prompter based on root agent type
        if hasattr(root_agent, 'is_manager') and root_agent.is_manager:
            from src.orchestrator.manager_prompter import manager_prompter
            asyncio.create_task(manager_prompter(root_agent, prompt, task_message))
        else:
            from src.orchestrator.coder_prompter import coder_prompter
            asyncio.create_task(coder_prompter(root_agent, prompt, task_message))
        
        # Track delegation in master agent
        if hasattr(self.agent, 'delegate_task'):
            self.agent.delegate_task(root_agent, prompt)
        
        # Update child active status
        self.agent.child_active_boolean = True

        # Queue completion message
        self._queue_self_prompt("Delegate complete")

    def _execute_spawn(self, directive: SpawnDirective) -> None:
        """Execute a SPAWN directive for ephemeral agents (same as manager)."""
        if not self.agent:
            return

        # Spawn ephemeral agents for each item
        for item in directive.items:
            ephemeral_type = item.ephemeral_type.type_name
            prompt = item.prompt.value
            
            # Currently only support tester ephemeral agents
            if ephemeral_type == "tester":
                # Create a proper Task object for the tester
                task = Task(
                    task_id=str(hash(ephemeral_type + prompt + str(time.time()))),
                    task_string=prompt
                )
                
                from src.orchestrator.tester_spawner import tester_spawner
                asyncio.create_task(tester_spawner(self.agent, prompt, task))
            else:
                self._queue_self_prompt(f"SPAWN failed: Unknown ephemeral type: {ephemeral_type}")
                return

        # Queue completion message
        self._queue_self_prompt("Spawn complete")

    def _execute_finish(self, directive: FinishDirective) -> None:
        """Execute a FINISH directive (calls orchestration for human input)."""
        if not self.agent:
            return
        
        # Check if there are active ephemeral agents
        if hasattr(self.agent, 'active_ephemeral_agents') and self.agent.active_ephemeral_agents:
            self._queue_self_prompt(f"FINISH failed: Cannot finish with {len(self.agent.active_ephemeral_agents)} active ephemeral agents still running")
            return
        
        # Check if root agent is still active
        if hasattr(self.agent, 'child_active_boolean') and self.agent.child_active_boolean:
            self._queue_self_prompt("FINISH failed: Cannot finish with root agent still active")
            return
        
        # Call orchestration function for human input (master agent keeps context)
        completion_message = directive.prompt.value
        
        # Check if human interface function is available
        if hasattr(self.agent, 'human_interface_fn') and self.agent.human_interface_fn is not None:
            from src.orchestrator.master_prompter import master_finisher
            asyncio.create_task(master_finisher(self.agent, completion_message, self.agent.human_interface_fn))
        else:
            pass

    def _execute_read(self, directive: ReadDirective) -> None:
        """Execute a READ directive (same as manager)."""
        results = []
        for target in directive.targets:
            result = self._read_target(target)
            results.append(result)
        
        # Queue completion message
        if self.agent:
            prompt = f"READ completed:\n" + "\n".join(results)
            self._queue_self_prompt(prompt)

    def _execute_wait(self, directive: WaitDirective) -> None:
        """Execute a WAIT directive (same as manager but checks root agent)."""
        if not self.agent:
            return

        # Check if master has active root agent or ephemeral agents
        active_root = getattr(self.agent, "child_active_boolean", False)
        active_ephemeral_agents = getattr(self.agent, "active_ephemeral_agents", [])

        if active_root or active_ephemeral_agents:
            # There are still running agents – do nothing (the prompt loop
            # will naturally resume once they complete).
            return None

        # No active agents ➔ inform the LLM so it can decide the next step.
        self._queue_self_prompt("WAIT failed: No active root agent or ephemeral agents to wait for")
        return None

    def _execute_run(self, directive: RunDirective) -> None:
        """Execute a RUN directive (no file operation restrictions for master)."""
        command = directive.command
        
        # Check if the command is in the allowed list
        if any(command.strip().startswith(allowed) for allowed in ALLOWED_COMMANDS):
            try:
                # Use PowerShell explicitly on Windows
                if os.name == 'nt':  # Windows
                    # Use PowerShell instead of cmd.exe
                    full_command = ['powershell.exe', '-Command', command]
                    result_obj = subprocess.run(
                        full_command,
                        capture_output=True,
                        text=True,
                        cwd=self.root_dir,
                        timeout=300
                    )
                else:
                    # Unix/Linux - use shell=True
                    result_obj = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=self.root_dir,
                        timeout=300
                    )
                    
                if result_obj.returncode == 0:
                    result = f"RUN succeeded: Output:\n{result_obj.stdout.strip()}" if result_obj.stdout.strip() else "RUN succeeded"
                else:
                    output = result_obj.stdout.strip() if result_obj.stdout.strip() else ""
                    error = result_obj.stderr.strip() if result_obj.stderr.strip() else ""
                    if output and error:
                        result = f"RUN failed: Output:\n{output}\nError:\n{error}"
                    elif output:
                        result = f"RUN failed: Output:\n{output}"
                    elif error:
                        result = f"RUN failed: Error:\n{error}"
                    else:
                        result = f"RUN failed with return code {result_obj.returncode}"
            except subprocess.TimeoutExpired:
                result = f"RUN failed: Command timed out after 5 minutes: {command}"
            except Exception as e:
                result = f"Failed to execute command '{command}': {str(e)}"
        else:
            result = "Invalid command"
        
        # Queue result
        if self.agent:
            prompt = f"Run command result:\n{result}"
            self._queue_self_prompt(prompt)

    def _execute_update_documentation(self, directive: UpdateDocumentationDirective) -> None:
        """Execute an UPDATE_DOCUMENTATION directive (writes to documentation.md)."""
        if not self.agent:
            result = "No agent available"
        else:
            try:
                # Write to documentation.md in the project root
                doc_path = self.root_dir / "documentation.md"
                doc_path.parent.mkdir(parents=True, exist_ok=True)
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(directive.content)
                result = f"Successfully updated documentation.md"
            except Exception as e:
                result = f"Failed to update documentation: {str(e)}"
        
        # Queue result
        if self.agent:
            self._queue_self_prompt(f"Update documentation result:\n{result}")

    def _read_target(self, target) -> str:
        """Read a file and add it to the agent's memory using the agent's read_file method (same as manager)."""
        if not self.agent or not hasattr(self.agent, 'read_file'):
            return "No agent or read_file method available"

        if target.is_folder:
            # Treat target.name as a path relative to the project root
            folder_path = self.root_dir / target.name
            if not folder_path.exists() or not folder_path.is_dir():
                return f"Folder {target.name} was not added to memory: folder not found"

            # Look for documentation files in the folder
            folder_name = folder_path.name
            candidate_names = [f"{folder_name}_README.md", f"{folder_name}_DOCUMENTATION.md", "README.md", "DOCUMENTATION.md"]
            doc_path = None
            for cname in candidate_names:
                potential = folder_path / cname
                if potential.exists():
                    doc_path = potential
                    break

            if not doc_path:
                return f"Folder {target.name} has no documentation file to add to memory"

            try:
                self.agent.read_file(str(doc_path))
                return f"Folder {target.name} documentation ({doc_path.name}) was added to memory"
            except Exception as e:
                return f"Folder {target.name} documentation was not added to memory: {str(e)}"
        else:
            # It's a file target. Treat target.name as a path relative to the project root
            found_path = self.root_dir / target.name
            if not found_path.exists() or not found_path.is_file():
                return f"File {target.name} was not added to memory: file not found"
            try:
                self.agent.read_file(str(found_path))
                return f"File {target.name} was added to memory"
            except Exception as e:
                return f"File {target.name} was not added to memory: {str(e)}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _queue_self_prompt(self, prompt: str) -> None:
        """Add *prompt* to the agent's queue in a deduplicated way.

        We avoid calling master_prompter() from within the interpreter to
        prevent overlapping api_call() invocations. By simply queuing the prompt, the
        execute_directive() epilogue (which un-stalls and schedules a single
        api_call()) guarantees exactly one follow-up LLM turn.
        """
        if not self.agent:
            return
        # Ensure prompt is queued only once.
        if hasattr(self.agent, 'prompt_queue') and prompt not in self.agent.prompt_queue:
            self.agent.prompt_queue.append(prompt)


# Convenience function
def execute_directive(directive_text: str, agent=None) -> None:
    """
    Convenience function to parse and execute a single directive string.
    After execution, sets agent.stall to False if agent is provided.
    
    Args:
        directive_text: The directive string to parse and execute
        agent: The master agent that sent the command
    """
    interpreter = MasterLanguageInterpreter(agent)

    try:
        directive = parse_directive(directive_text)
    except Exception as e:
        # Bubble parsing issues back to the master agent so the LLM can react
        error_msg = f"PARSING FAILED: {str(e)}"
        interpreter._queue_self_prompt(error_msg)

        # Make sure the agent is unstalled so that the queued prompt is processed
        if agent is not None:
            # Always unstall the agent so it can process future prompts
            agent.stall = False

            if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
                asyncio.create_task(agent.api_call())
        return  # Parsing failed; do not continue to execute.

    # Normal execution path if parsing succeeded
    interpreter.execute(directive)

    if agent is not None:
        # Always unstall the agent so it can process future prompts
        agent.stall = False
        
        # If there are queued prompts, schedule api_call to process them
        if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
            asyncio.create_task(agent.api_call()) 