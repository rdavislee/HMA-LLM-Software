"""
Manager Language Interpreter.
Executes parsed manager language directives and performs the described actions.
"""

import os
import json
import asyncio
import subprocess
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from .ast import DirectiveType, DelegateDirective, SpawnDirective, FinishDirective, ActionDirective, WaitDirective, RunDirective, UpdateReadmeDirective
from src.messages.protocol import TaskMessage, Task, MessageType, ResultMessage
from src.config import ALLOWED_COMMANDS
from .parser import parse_directive
import src


class ManagerLanguageInterpreter:
    """
    Interpreter for the Manager Language.
    Executes directives and performs file system operations.
    """
    
    def __init__(self, agent=None):
        """
        Initialize the interpreter.
        Args:
            agent: The agent that sent the command
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
            elif isinstance(directive, ActionDirective):
                self._execute_action(directive)
            elif isinstance(directive, WaitDirective):
                self._execute_wait(directive)
            elif isinstance(directive, RunDirective):
                self._execute_run(directive)
            elif isinstance(directive, UpdateReadmeDirective):
                self._execute_update_readme(directive)
            else:
                # Unknown directive type – queue a self prompt rather than invoking manager_prompter directly
                self._queue_self_prompt(f"Unknown directive type: {type(directive)}")
        except Exception as e:
            # Queue the error instead of calling manager_prompter directly so that
            # exactly one follow-up turn is scheduled by execute_directive().
            self._queue_self_prompt(f"Error executing directive {type(directive).__name__}: {str(e)}")

    def _execute_delegate(self, directive: DelegateDirective) -> None:
        """Execute a DELEGATE directive."""
        if not self.agent:
            return
        if not hasattr(self.agent, 'children'):
            return

        # Normalize all paths to POSIX-style (forward slashes) so comparisons are
        # consistent across operating systems. On Windows, Path.__str__() uses
        # backslashes, which breaks look-ups when the directive string contains
        # forward slashes. Converting both sides to POSIX eliminates this issue.

        def _rel_posix(child):
            return Path(child.path).relative_to(self.root_dir).as_posix()

        child_map = {_rel_posix(child): child for child in self.agent.children}

        def _to_posix(s: str) -> str:
            # Avoid Path failures for strings like "some/child" that might contain
            # wildcard characters – fall back to simple replace.
            try:
                return Path(s).as_posix()
            except Exception:
                return s.replace("\\", "/")

        # --- BEGIN: Adopt on-disk paths that are inside the manager scope but
        #            don’t yet have an attached child agent ------------------
        for item in directive.items:
            target_posix = _to_posix(item.target.name)
            if target_posix in child_map:
                continue  # already have a child agent

            potential_path = self.root_dir / target_posix  # absolute path from project root
            
            # NEW: Accept only immediate children of this manager. If the target lives deeper
            # than one directory level below the manager's own folder, ignore it so that the
            # intermediate manager can handle the delegation instead.
            if potential_path.parent != Path(self.agent.path).resolve():
                # Target is nested further down the hierarchy – skip adoption here.
                continue
            
            try:
                # Ensure path is within this manager's directory tree
                potential_path.resolve().relative_to(Path(self.agent.path).resolve())
            except ValueError:
                # Outside manager scope – skip, will be reported as missing later
                continue

            if potential_path.exists():
                try:
                    if potential_path.is_dir():
                        from src.agents.manager_agent import ManagerAgent  # local import to avoid circular deps
                        new_child = ManagerAgent(
                            path=str(potential_path),
                            parent=self.agent,
                            llm_client=self.agent.llm_client if hasattr(self.agent, 'llm_client') else None
                        )
                    else:
                        from src.agents.coder_agent import CoderAgent
                        new_child = CoderAgent(
                            path=str(potential_path),
                            parent=self.agent,
                            llm_client=self.agent.llm_client if hasattr(self.agent, 'llm_client') else None
                        )
                    # Register new child
                    self.agent.children.append(new_child)
                    child_map[target_posix] = new_child
                except Exception as e:
                    # Could not create agent – continue and let normal error flow handle it
                    pass
        # --- END adopt logic -------------------------------------------------

        missing_children = []
        for item in directive.items:
            target_posix = _to_posix(item.target.name)
            if target_posix not in child_map:
                missing_children.append(item.target.name)

        if missing_children:
            missing_list = ", ".join(sorted(missing_children))
            error_msg = f"DELEGATE failed: The following targets are not within this manager's scope – {missing_list}"
            self._queue_self_prompt(error_msg)
            return

        # Call appropriate prompter based on child type
        for item in directive.items:
            target_posix = _to_posix(item.target.name)
            child_agent = child_map[target_posix]

            # Create TaskMessage for the child
            task = Task(
                task_id=str(hash(target_posix + item.prompt.value)),
                task_string=item.prompt.value
            )
            task_message = TaskMessage(
                message_type=MessageType.DELEGATION,
                sender=self.agent,
                recipient=child_agent,
                message_id=str(hash(task.task_id)),
                task=task
            )
            # Call appropriate prompter based on child type
            if hasattr(child_agent, 'is_manager') and child_agent.is_manager:
                from src.orchestrator.manager_prompter import manager_prompter
                asyncio.create_task(manager_prompter(child_agent, item.prompt.value, task_message))
            else:
                from src.orchestrator.coder_prompter import coder_prompter
                asyncio.create_task(coder_prompter(child_agent, item.prompt.value, task_message))
            # Track delegation in agent (call delegate_task)
            self.agent.delegate_task(child_agent, item.prompt.value)

        return None
    
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
                task = Task(
                    task_id=str(hash(ephemeral_type + prompt + str(time.time()))),
                    task_string=prompt
                )
                
                from src.orchestrator.tester_spawner import tester_spawner
                asyncio.create_task(tester_spawner(self.agent, prompt, task))
            else:
                self._queue_self_prompt(f"SPAWN failed: Unknown ephemeral type: {ephemeral_type}")
                return

    
    def _execute_finish(self, directive: FinishDirective) -> None:
        """Execute a FINISH directive."""
        if not self.agent:
            return
        
        # Check if there are active ephemeral agents
        if hasattr(self.agent, 'active_ephemeral_agents') and self.agent.active_ephemeral_agents:
            self._queue_self_prompt(f"FINISH failed: Cannot finish with {len(self.agent.active_ephemeral_agents)} active ephemeral agents still running")
            return
            
        try:
            self.agent.deactivate()
            # Notify parent with ResultMessage
            parent = getattr(self.agent, 'parent', None)
            if parent:
                task = self.agent.active_task
                if task is None:
                    # Fallback: create a dummy task
                    task = Task(task_id=str(hash(str(self.agent.path))), task_string="Task finished")
                result_message = ResultMessage(
                    message_type=MessageType.RESULT,
                    sender=self.agent,
                    recipient=parent,
                    message_id=str(hash(str(self.agent.path))),
                    task=task,
                    result=directive.prompt.value
                )
                
                # Check if parent is a MasterAgent and use appropriate prompter
                from src.agents.master_agent import MasterAgent
                if isinstance(parent, MasterAgent):
                    from src.orchestrator.master_prompter import master_prompter
                    asyncio.create_task(master_prompter(parent, directive.prompt.value, result_message))
                else:
                    from src.orchestrator.manager_prompter import manager_prompter
                    asyncio.create_task(manager_prompter(parent, directive.prompt.value, result_message))
            else:
                # Manager agents should always have a parent (either another manager or a master)
                # If no parent exists, this indicates a configuration error
                self._queue_self_prompt("FINISH failed: Manager agent has no parent - this should not happen")
        except Exception as e:
            # Queue the error instead of calling prompter directly so that
            # exactly one follow-up turn is scheduled by execute_directive().
            self._queue_self_prompt(f"Failed to finish: {str(e)}")
    
    def _execute_action(self, directive: ActionDirective) -> None:
        """Execute a CREATE, DELETE, or READ action directive."""
        results = []
        for target in directive.targets:
            if directive.action_type == "CREATE":
                result = self._create_target(target)
            elif directive.action_type == "DELETE":
                result = self._delete_target(target)
            elif directive.action_type == "READ":
                result = self._read_target(target)
            else:
                result = f"Unknown action type: {directive.action_type}"
            results.append(result)
        # Reprompt self with action results
        if self.agent:
            prompt = f"Action {directive.action_type} completed:\n" + "\n".join(results)
            self._queue_self_prompt(prompt)
    
    def _execute_wait(self, directive: WaitDirective) -> None:
        """Execute a WAIT directive.

        If the manager currently has no active children or ephemeral agents the instruction makes
        no sense – in that case immediately queue a follow-up prompt so that
        the LLM can react instead of stalling indefinitely.
        """
        if not self.agent:
            return

        active_children = getattr(self.agent, "active_children", {})
        active_ephemeral_agents = getattr(self.agent, "active_ephemeral_agents", [])

        if active_children or active_ephemeral_agents:
            # There are still running children or ephemeral agents – do nothing (the prompt loop
            # will naturally resume once they complete).
            return None

        # No active children or ephemeral agents ➔ inform the LLM so it can decide the next step.
        self._queue_self_prompt("WAIT failed: No active children or ephemeral agents to wait for")
        return None
    
    def _execute_run(self, directive: RunDirective) -> None:
        command = directive.command

        if not any(command.startswith(allowed) for allowed in ALLOWED_COMMANDS):
            result = "Invalid command"
        else:
            try:
                if os.name == "nt":
                    full_cmd = ["powershell.exe", "-Command", command]
                    from types import SimpleNamespace
                    try:
                        proc = subprocess.Popen(
                            full_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            cwd=self.root_dir,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                        )
                        stdout_output, stderr_output = proc.communicate(timeout=120)
                        # Clip potentially huge outputs
                        MAX_RUN_OUTPUT_CHARS = 100000
                        def _clip(s: str, limit: int = MAX_RUN_OUTPUT_CHARS):
                            return s if len(s) <= limit else s[:limit] + f"\n... [truncated {len(s) - limit} chars]"
                        stdout_output = _clip(stdout_output)
                        stderr_output = _clip(stderr_output)
                        completed = SimpleNamespace(stdout=stdout_output, stderr=stderr_output, returncode=proc.returncode)
                    except subprocess.TimeoutExpired:
                        subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)])
                        stdout_output, stderr_output = proc.communicate()
                        # Clip potentially huge outputs
                        MAX_RUN_OUTPUT_CHARS = 100000
                        def _clip(s: str, limit: int = MAX_RUN_OUTPUT_CHARS):
                            return s if len(s) <= limit else s[:limit] + f"\n... [truncated {len(s) - limit} chars]"
                        stdout_output = _clip(stdout_output)
                        stderr_output = _clip(stderr_output)
                        prompt_msg = (
                            "RUN failed: Timed-out after 120 s. Most likely an infinite loop in the code.\n"
                            f"Output:\n{stdout_output}\nError:\n{stderr_output}"
                        )
                        self._queue_self_prompt(prompt_msg)
                        return

                stdout_output = completed.stdout.strip()
                stderr_output = completed.stderr.strip()

                if completed.returncode == 0:
                    result = stdout_output
                else:
                    if stdout_output and stderr_output:
                        result = f"Command failed: Output:\n{stdout_output}\nError:\n{stderr_output}"
                    elif stdout_output:
                        result = f"Command failed: Output:\n{stdout_output}"
                    elif stderr_output:
                        result = f"Command failed: Error:\n{stderr_output}"
                    else:
                        result = f"Command failed with return code {completed.returncode}"

            except Exception as e:
                result = f"Failed to execute command '{command}': {str(e)}"

        if self.agent:
            prompt = f"Run command result:\n{result}"
            self._queue_self_prompt(prompt)
    
    def _execute_update_readme(self, directive: UpdateReadmeDirective) -> None:
        if not self.agent or not hasattr(self.agent, 'path'):
            result = "No agent path available"
        else:
            agent_path = Path(self.agent.path)
            agent_path = self.root_dir / agent_path.relative_to(self.root_dir)
            if not agent_path.is_dir():
                result = "Agent path is not a directory"
            else:
                # Prefer the personal_file reference directly from the agent
                if hasattr(self.agent, "personal_file") and self.agent.personal_file is not None:
                    # Ensure we resolve against ROOT_DIR so that relative paths behave as expected
                    readme_path = Path(self.agent.personal_file)
                    # Guard against a personal_file located outside the agent_path (shouldn't happen but stay safe)
                    try:
                        readme_path.resolve().relative_to(agent_path.resolve())
                    except ValueError:
                        # Fallback to constructing within the agent's directory
                        readme_path = agent_path / readme_path.name
                else:
                    # Legacy behaviour – construct the filename based on folder name
                    folder_name = agent_path.name
                    readme_path = agent_path / f"{folder_name}_README.md"

                try:
                    readme_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(directive.content)
                    result = f"Successfully updated {readme_path.name}"
                except Exception as e:
                    result = f"Failed to update readme: {str(e)}"
        # Queue a single follow-up prompt on the agent itself so that exactly one
        # subsequent LLM call is triggered (handled by execute_directive below).
        if self.agent:
            self._queue_self_prompt(f"Update README result:\n{result}")
    
    def _create_target(self, target) -> str:
        """Create a file or folder at the path relative to the project root, but only if within the manager's scope.
        Also creates the appropriate agent object and adds it to the manager's children."""
        if not self.agent or not hasattr(self.agent, 'path'):
            return "No agent path available"
        
        agent_path = self.root_dir / Path(self.agent.path).relative_to(self.root_dir)
        target_path = self.root_dir / target.name
        # Check if destination is out of scope (outside agent's directory)
        try:
            target_path.resolve().relative_to(agent_path.resolve())
        except ValueError:
            return f"Action failed: Destination {target.name} is out of scope"
        
        # Check if agent already exists for this target
        if hasattr(self.agent, 'children'):
            for child in self.agent.children:
                if str(child.path) == str(target_path):
                    return f"Action failed: Agent already exists for {target.name}"
        
        try:
            if target.is_folder:
                if target_path.exists():
                    return f"Action failed: Folder {target.name} already exists"
                target_path.mkdir(parents=True, exist_ok=True)
                
                # Create manager agent for the folder
                # Import locally to avoid circular imports
                from src.agents.manager_agent import ManagerAgent
                child_agent = ManagerAgent(
                    path=str(target_path),
                    parent=self.agent,
                    llm_client=self.agent.llm_client if hasattr(self.agent, 'llm_client') else None
                )
                
                # Add to manager's children
                if hasattr(self.agent, 'children'):
                    self.agent.children.append(child_agent)
                
                return f"Action succeeded: Created folder {target.name} with manager agent"
            else:
                if target_path.exists():
                    return f"Action failed: File {target.name} already exists"
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.touch()
                
                # Create coder agent for the file
                # Import locally to avoid circular imports
                from src.agents.coder_agent import CoderAgent
                child_agent = CoderAgent(
                    path=str(target_path),
                    parent=self.agent,
                    llm_client=self.agent.llm_client if hasattr(self.agent, 'llm_client') else None
                )
                
                # Add to manager's children
                if hasattr(self.agent, 'children'):
                    self.agent.children.append(child_agent)
                
                return f"Action succeeded: Created file {target.name} with coder agent"
        except Exception as e:
            return f"Action failed: {str(e)}"
    
    def _delete_target(self, target) -> str:
        """Delete a file or folder at the path relative to the project root, but only if within the manager's scope.
        Also checks if the corresponding agent is active and removes it from the manager's children."""
        if not self.agent or not hasattr(self.agent, 'path'):
            return "No agent path available"
        
        agent_path = self.root_dir / Path(self.agent.path).relative_to(self.root_dir)
        target_path = self.root_dir / target.name
        # Check if destination is out of scope (outside agent's directory)
        try:
            target_path.resolve().relative_to(agent_path.resolve())
        except ValueError:
            return f"Action failed: Destination {target.name} is out of scope"
        
        # Find the corresponding agent in children
        agent_to_remove = None
        if hasattr(self.agent, 'children'):
            for child in self.agent.children:
                if str(child.path) == str(target_path):
                    agent_to_remove = child
                    break
        
        # Check if the agent is active
        if agent_to_remove is not None:
            if hasattr(agent_to_remove, 'is_active') and agent_to_remove.is_active:
                return f"Action failed: Cannot delete {target.name} - agent is currently active"
        
        try:
            if not target_path.exists():
                return f"Action failed: {target.name} does not exist"
            
            if target.is_folder:
                import shutil
                shutil.rmtree(target_path)
                result_msg = f"Action succeeded: Deleted folder {target.name}"
            else:
                target_path.unlink()
                result_msg = f"Action succeeded: Deleted file {target.name}"
            
            # Remove the agent from manager's children if it exists
            if agent_to_remove is not None and hasattr(self.agent, 'children'):
                try:
                    self.agent.children.remove(agent_to_remove)
                    result_msg += " and removed agent"
                except ValueError:
                    # Agent not in children list, that's okay
                    pass
            
            return result_msg
        except Exception as e:
            return f"Action failed: {str(e)}"
    
    def _read_target(self, target) -> str:
        """Read a file and add it to the agent's memory using the agent's read_file method."""
        if not self.agent or not hasattr(self.agent, 'read_file'):
            return "No agent or read_file method available"

        if target.is_folder:
            # Treat target.name as a path relative to the project root
            folder_path = self.root_dir / target.name
            if not folder_path.exists() or not folder_path.is_dir():
                return f"Folder {target.name} was not added to memory: folder not found"

            # Determine README filename(s)
            folder_name = folder_path.name
            candidate_names = [f"{folder_name}_README.md"]
            readme_path = None
            for cname in candidate_names:
                potential = folder_path / cname
                if potential.exists():
                    readme_path = potential
                    break

            if not readme_path:
                return f"Folder {target.name} has no README file to add to memory"

            try:
                self.agent.read_file(str(readme_path))
                return f"Folder {target.name} README ({readme_path.name}) was added to memory"
            except Exception as e:
                return f"Folder {target.name} README was not added to memory: {str(e)}"
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

        We avoid calling manager_prompter() from within the interpreter to
        prevent overlapping api_call() invocations, which in turn duplicate
        the ConsoleLLMClient output. By simply queuing the prompt, the
        execute_directive() epilogue (which un-stalls and schedules a single
        api_call()) guarantees exactly one follow-up LLM turn.
        """
        if not self.agent:
            return
        # Ensure prompt is queued only once.
        if prompt not in self.agent.prompt_queue:
            self.agent.prompt_queue.append(prompt)


# Convenience function
def execute_directive(directive_text: str, agent=None) -> None:
    """
    Convenience function to parse and execute a single directive string.
    After execution, sets agent.stall to False if agent is provided.
    
    Args:
        directive_text: The directive string to parse and execute
        base_path: Base directory for file operations
        agent: The agent that sent the command
    """
    interpreter = ManagerLanguageInterpreter(agent)

    try:
        directive = parse_directive(directive_text)
    except Exception as e:
        # Bubble parsing issues back to the manager agent so the LLM can react
        error_msg = f"PARSING FAILED: {str(e)}\n\nDirective was: {directive_text}\n\nMOST COMMON ISSUE: Multiple directives on same api call, use sequential API calls, aka only one line per API call"
        interpreter._queue_self_prompt(error_msg)

        # Make sure the agent is unstalled so that the queued prompt is processed
        if agent is not None:
            # Always unstall the agent so it can process future prompts
            agent.stall = False

            if getattr(agent, 'prompt_queue', []):
                if hasattr(agent, 'api_call'):
                    try:
                        asyncio.create_task(agent.api_call())
                    except Exception:
                        pass
        return  # Parsing failed; do not continue to execute.

    # Normal execution path if parsing succeeded
    interpreter.execute(directive)

    if agent is not None:
        # Always unstall the agent so it can process future prompts
        agent.stall = False
        
        # If there are queued prompts, schedule api_call to process them
        if hasattr(agent, 'prompt_queue') and hasattr(agent, 'api_call') and agent.prompt_queue:
            asyncio.create_task(agent.api_call())