import asyncio
import time
import uuid
from typing import Optional, Any, Dict, List
from src.agents.coder_agent import CoderAgent
from src.messages.protocol import *
from src.coder_language.ast import (
    ReadDirective, RunDirective, ChangeDirective, FinishDirective
)

async def coder_prompter(
    agent: CoderAgent, 
    prompt: str, 
    message: Optional[TaskMessage] = None
) -> None:
    """
    First stage of the coder agent prompting system - handles prompting and getting LLM response.
    
    PSEUDOCODE:
    
    1. ACTIVATION PHASE:
       - if message is TaskMessage:
           - activate agent with the task from message
           - handle activation errors (send to parent if fails)
    
    2. LLM RESPONSE PHASE:
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
        
        # 2. LLM RESPONSE PHASE
        # Add prompt to agent's prompt queue using agent.process_task(prompt)
        await agent.process_task(prompt)
        
    except Exception as error:
        # ERROR HANDLING: catch all exceptions in try/catch
        # If error occurs: reprompt with error message
        error_prompt = f"Error occurred during processing: {str(error)}"
        try:
            await agent.process_task(error_prompt)
        except:
            # If even the error reprompt fails, we can't do much more
            pass
        return


