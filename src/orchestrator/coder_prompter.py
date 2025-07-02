import asyncio
import time
import uuid
import sys
import traceback
from typing import Optional, Any, Dict, List
from src.agents.coder_agent import CoderAgent
from src.messages.protocol import *
from src.languages.coder_language.ast import (
    ReadDirective, RunDirective, ChangeDirective, FinishDirective
)

async def coder_prompter(
    agent: CoderAgent, 
    prompt: str, 
    message: Optional[Message] = None
) -> None:
    """
    First stage of the coder agent prompting system - handles prompting and getting LLM response.
    
    PSEUDOCODE:
    
    1. ACTIVATION PHASE:
       - if message is TaskMessage:
           - activate agent with the task from message
           - handle activation errors (send to parent if fails)
    
    2. EPHEMERAL RESULT HANDLING PHASE:
       - if message is ResultMessage:
           - identify which ephemeral agent sent the result
           - remove ephemeral agent from tracking (cleanup)
    
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
                agent.activate(message)
            except Exception as activation_error:
                # Handle activation errors (send to parent if fails)
                if agent.parent:
                    # Send error to parent agent
                    error_message = f"Activation failed for agent {agent.path}: {str(activation_error)}"
                    await agent.parent.process_task(error_message)
                return
        
        # 2. EPHEMERAL RESULT HANDLING PHASE
        if message is not None and isinstance(message, ResultMessage):
            # Handle result from ephemeral agent (like tester)
            ephemeral_sender = message.sender
            
            # Check if this is an ephemeral agent and remove it from tracking
            from src.agents.ephemeral_agent import EphemeralAgent
            if isinstance(ephemeral_sender, EphemeralAgent):
                agent.remove_ephemeral_agent(ephemeral_sender)
            
            # Include original task information from the result message
            original_task = ""
            if hasattr(message, 'task') and hasattr(message.task, 'task_string'):
                original_task = f" (Task: {message.task.task_string})"
            elif hasattr(message, 'task') and isinstance(message.task, str):
                original_task = f" (Task: {message.task})"
                
            prompt = f"[Ephemeral{original_task}] {prompt}"
        
        # 3. LLM RESPONSE PHASE
        # Add prompt to agent's prompt queue using agent.process_task(prompt)
        await agent.process_task(prompt)
        
    except Exception as error:
        # ERROR HANDLING: catch all exceptions in try/catch
        error_prompt = f"Error occurred during processing: {str(error)}"
        try:
            await agent.process_task(error_prompt)
        except Exception as reprompt_error:
            # If even the error reprompt fails, print details so the user can see.
            print(f"[coder_prompter] Failed to reprompt agent {agent.path}: {reprompt_error}", file=sys.stderr)
            traceback.print_exc()
        return


