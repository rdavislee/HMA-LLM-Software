import asyncio
import time
import uuid
from typing import Optional, Any, Dict, List
from src.agents.manager_agent import ManagerAgent
from src.agents.coder_agent import CoderAgent
from src.messages.protocol import *
from src.manager_language.ast import (
    DelegateDirective, FinishDirective, ActionDirective, 
    WaitDirective, RunDirective, UpdateReadmeDirective
)

async def manager_prompt_stage(
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
    pass

