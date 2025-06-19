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
       - call await agent.api_call(prompt) to get coder language response
       - response should contain coder language directives
       - call coder_receive_stage(agent, response_string)
    
    ERROR HANDLING:
       - catch all exceptions in try/catch
       - if error occurs:
           - reprompt with error message.
       - return
    """
    pass


