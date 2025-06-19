import asyncio
import time
import uuid
from typing import Optional, Any, Dict, List
from ..agents.coder_agent import CoderAgent
from ..messages.protocol import *
from ..coder_language.interpreter import CoderLanguageInterpreter
from ..coder_language.parser import CoderLanguageParser
from ..coder_language.ast import (
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


async def coder_receive_stage(
    agent: CoderAgent,
    directive_string: str
) -> None:
    """
    Second stage of the coder agent prompting system - handles parsing and execution of directives.
    
    Args:
        agent: The coder agent executing the directives
        directive_string: Unparsed coder language directive string from LLM response
    
    PSEUDOCODE:
    
    3. PARSING PHASE:
       - use CoderLanguageParser to parse the directive_string
       - if parsing fails:
           - create error prompt with parsing error
           - recursively call coder_prompt_stage(agent, error_prompt, message)
           - return early
    
    4. EXECUTION & ROUTING PHASE:
       - use CoderLanguageInterpreter to execute each directive
       - for each parsed directive:
           
           if READ:
               - interpreter already executed the file read operation
               - check for read failures and handle errors
               - continue to next directive (don't return)
           
           elif RUN:
               - interpreter already executed the command
               - check command results and handle failures
               - continue to next directive (don't return)
           
           elif CHANGE:
               - interpreter already executed the file change operation
               - check for change failures and handle errors
               - continue to next directive (don't return)
           
           elif FINISH:
               - create ResultMessage with finish prompt
               - get parent agent
               - try to deactivate agent
               - call manager_prompt_stage(parent, continuation_prompt, result_msg)
               - return (task complete, control returned to parent)
    
    5. CONTINUATION PHASE:
       - if we processed directives but didn't FINISH:
           - create continuation prompt: "Actions completed. What next?"
           - recursively call coder_prompt_stage(agent, continuation_prompt, message)
    
    6. ERROR HANDLING:
       - catch all exceptions in try/catch
       - if error occurs:
           - reprompt with error message by calling coder_prompt_stage.
       - return
    
    
    HELPER FUNCTIONS NEEDED:
    - _get_parent_agent(agent)
    - _send_error_to_parent(agent, original_message, error)
    
    KEY DESIGN DECISIONS:
    - Recursive calls handle the message passing and state transitions
    - Each agent activation is self-contained (activate -> process -> deactivate)
    - Parse errors are handled by retrying with error context
    - Local actions (READ/RUN/CHANGE) continue execution
    - Control flow actions (FINISH) change execution path
    - Error propagation flows up the hierarchy
    - Coders have no children, so no delegation or waiting logic needed
    """
    pass
