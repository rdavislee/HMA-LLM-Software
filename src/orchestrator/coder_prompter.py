import asyncio
import time
import uuid
from typing import Optional, Any, Dict, List
from src.agents.coder_agent import CoderAgent
from src.messages.protocol import *
from src.coder_language.ast import (
    ReadDirective, RunDirective, ChangeDirective, FinishDirective
)

async def coder_prompt_stage(
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
    pass


