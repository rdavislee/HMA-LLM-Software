import asyncio
import time
import uuid
import sys
import traceback
from typing import Optional, Any, Dict, List
from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.messages.protocol import *
from src.languages.manager_language.ast import (
    DelegateDirective, FinishDirective, ActionDirective, 
    WaitDirective, RunDirective, UpdateReadmeDirective
)

async def manager_prompter(
    agent: ManagerAgent, 
    prompt: str, 
    message: Optional[Message] = None
) -> None:
    """
    First stage of the hierarchical agent prompting system - handles prompting and getting LLM response.
    
    PSEUDOCODE:
    
    1. ACTIVATION PHASE:
       - if message is TaskMessage:
           - activate agent with the task
           - handle activation errors (send to parent if fails)
    
    2. CHILD RESULT HANDLING PHASE:
       - if message is ResultMessage:
           - identify which child sent the result
           - remove child from agent's active_children list
    
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
        
        # 2. CHILD RESULT HANDLING PHASE
        if message is not None and isinstance(message, ResultMessage):
            # Identify which child sent the result
            child_sender_id = message.sender_id
            # Find the child agent that sent this result
            for child in list(agent.active_children.keys()):
                if str(child.path) == child_sender_id:
                    # Remove child from agent's active_children list
                    agent.receive_child_result(child, message.result)
                    # Prepend child's name to the prompt
                    from pathlib import Path
                    child_name = Path(child_sender_id).name
                    prompt = f"[{child_name}] {prompt}"
                    break
        
        # 3. LLM RESPONSE PHASE
        # Add prompt to agent's prompt queue using agent.process_task(prompt)
        await agent.process_task(prompt)
        
    except Exception as error:
        # ERROR HANDLING: catch all exceptions in try/catch
        error_prompt = f"Error occurred during processing: {str(error)}"
        try:
            await agent.process_task(error_prompt)
        except Exception as reprompt_error:
            print(f"[manager_prompter] Failed to reprompt agent {agent.path}: {reprompt_error}", file=sys.stderr)
            traceback.print_exc()
        return

