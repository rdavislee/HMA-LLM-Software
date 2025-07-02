import asyncio
import time
import uuid
import sys
import traceback
from typing import Optional, Any, Dict, List, Callable, Awaitable
from src.agents.master_agent import MasterAgent
from src.messages.protocol import *
from src.languages.master_language.ast import (
    DelegateDirective, FinishDirective, ReadDirective, 
    WaitDirective, RunDirective, UpdateDocumentationDirective
)

async def master_prompter(
    agent: MasterAgent, 
    prompt: str, 
    message: Optional[Message] = None
) -> None:
    """
    First stage of the master agent prompting system - handles prompting and getting LLM response.
    
    PSEUDOCODE:
    
    1. ACTIVATION PHASE:
       - if message is TaskMessage:
           - activate agent with the task
           - handle activation errors (send to human if fails)
    
    2. CHILD RESULT HANDLING PHASE:
       - if message is ResultMessage:
           - identify which child sent the result (root agent)
           - remove child from agent's active status
    
    3. LLM RESPONSE PHASE:
       - add prompt to agent's prompt queue using agent.process_task(prompt)
    
    ERROR HANDLING:
       - catch all exceptions in try/catch
       - if error occurs:
           - reprompt with error message.
       - return
    """
    try:
        # 1. ACTIVATION PHASE
        if message is not None and isinstance(message, TaskMessage):
            try:
                # Master agent activation is different - it doesn't use the same activate method
                # Just set the active task and update state
                agent.active_task = message
                agent.update_activity()
            except Exception as activation_error:
                error_message = f"Activation failed for master agent: {str(activation_error)}"
                print(f"[master_prompter] {error_message}", file=sys.stderr)
                return
        
        # 2. CHILD RESULT HANDLING PHASE
        if message is not None and isinstance(message, ResultMessage):
            # Handle result from root manager agent
            child_sender = message.sender
            
            # Check if this is the root agent
            if child_sender == agent.root:
                # Update child active status
                agent.child_active_boolean = getattr(agent.root, 'is_active', False)
                
                # Prepend child's name and original task to the prompt
                from pathlib import Path
                child_name = Path(str(child_sender.path)).name if hasattr(child_sender, 'path') else "root"
                
                # Include original task information from the result message
                original_task = ""
                if hasattr(message, 'task') and hasattr(message.task, 'task_string'):
                    original_task = f" (Task: {message.task.task_string})"
                elif hasattr(message, 'task') and isinstance(message.task, str):
                    original_task = f" (Task: {message.task})"
                    
                prompt = f"[{child_name}{original_task}] {prompt}"
            else:
                # Check if this is an ephemeral agent result
                from src.agents.ephemeral_agent import EphemeralAgent
                if isinstance(child_sender, EphemeralAgent):
                    # Handle ephemeral agent result - remove from tracking
                    agent.remove_ephemeral_agent(child_sender)
                    
                    # Include original task information from the result message
                    original_task = ""
                    if hasattr(message, 'task') and hasattr(message.task, 'task_string'):
                        original_task = f" (Task: {message.task.task_string})"
                    elif hasattr(message, 'task') and isinstance(message.task, str):
                        original_task = f" (Task: {message.task})"
                        
                    prompt = f"[ephemeral{original_task}] {prompt}"
        
        # 3. LLM RESPONSE PHASE
        # Add prompt to agent's prompt queue using agent.process_task(prompt)
        await agent.process_task(prompt)
        
    except Exception as error:
        # ERROR HANDLING: catch all exceptions in try/catch
        error_prompt = f"Error occurred during processing: {str(error)}"
        try:
            await agent.process_task(error_prompt)
        except Exception as reprompt_error:
            print(f"[master_prompter] Failed to reprompt master agent: {reprompt_error}", file=sys.stderr)
            traceback.print_exc()
        return


async def master_finisher(
    agent: MasterAgent,
    completion_message: str,
    human_interface_fn: Callable[[str], Awaitable[str]]
) -> None:
    """
    Handle FINISH directive from master agent - sends completion message to human and waits for response.
    Master agent keeps context during this interaction.
    
    Args:
        agent: The master agent that finished
        completion_message: The completion message from the FINISH directive
        human_interface_fn: Async function that takes completion message and returns human response
    """
    try:
        # Call the provided human interface function with the completion message
        # This function should:
        # 1. Send completion_message to the human (frontend, terminal, etc.)
        # 2. Wait for and return the human response
        human_response = await human_interface_fn(completion_message)
        
        # Send human response back to master agent (no message parameter since it's a response to finish)
        await master_prompter(agent, human_response, message=None)
        
    except Exception as e:
        error_prompt = f"Error in master finisher: {str(e)}"
        try:
            await agent.process_task(error_prompt)
        except Exception as reprompt_error:
            print(f"[master_finisher] Failed to reprompt master agent: {reprompt_error}", file=sys.stderr)
            traceback.print_exc()


# Example human interface functions:

async def terminal_human_interface(completion_message: str) -> str:
    """Example terminal-based human interface function."""
    print(f"\n[Master Agent Completed]: {completion_message}")
    return input("Your response: ")

async def frontend_human_interface(completion_message: str) -> str:
    """Example frontend-based human interface function (would integrate with web UI)."""
    # TODO: Send to frontend and wait for response
    # This would integrate with the Socket.IO server or similar
    print(f"[Frontend] Master completed: {completion_message}")
    return "Frontend response received" 