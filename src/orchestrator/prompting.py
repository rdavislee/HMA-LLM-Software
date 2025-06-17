import asyncio
import time
import uuid
from typing import Optional, Any, Dict, List
from ..agents.manager_agent import ManagerAgent
from ..agents.coder_agent import CoderAgent
from ..messages.protocol import *
from ..manager_language.interpreter import ManagerLanguageInterpreter
from ..manager_language.parser import ManagerLanguageParser
from ..manager_language.ast import (
    DelegateDirective, FinishDirective, ActionDirective, 
    WaitDirective, RunDirective, UpdateReadmeDirective
)

async def manager_prompt(
    agent: ManagerAgent, 
    prompt: str, 
    message: Optional[Message] = None
) -> None:
    """
    Recursive function that handles the prompting loop for the hierarchical agent system.
    
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
       - call agent.api_call(prompt) to get manager language response
       - response should contain manager language directives
    
    4. PARSING PHASE:
       - use ManagerLanguageParser to parse the response
       - if parsing fails:
           - create error prompt with parsing error
           - recursively call manager_prompt(agent, error_prompt, message)
           - return early
    
    5. EXECUTION & ROUTING PHASE:
       - use ManagerLanguageInterpreter to execute each directive
       - for each parsed directive:
           
           if DELEGATE:
               - for each delegation target:
                   - get/create child agent
                   - create TaskMessage with delegation prompt
                   - if child is manager: call manager_prompt(child, prompt, task_msg)
                   - if child is coder: call coder_prompt(child, prompt, task_msg)
               - return (delegation started, wait for children)
           
           elif FINISH:
               - create ResultMessage with finish prompt
               - get parent agent
               - try to deactivate agent
               - if agent has active children, this will cause an error, will be caught by exception handler and agent will be reprompted
               - call manager_prompt(parent, continuation_prompt, result_msg)
               - return (task complete, control returned to parent)
           
           elif ACTION (CREATE/DELETE/READ):
               - interpreter already executed the file operations
               - check for action failures and handle errors
               - continue to next directive (don't return)
           
           elif WAIT:
               - set agent to waiting state
               - return (pause execution until children report back)
           
           elif RUN:
               - interpreter already executed the command
               - check command results and handle failures
               - continue to next directive (don't return)
           
           elif UPDATE_README:
               - interpreter already queued readme update
               - execute the readme update to agent's personal file
                               - continue to next directive (don't return)
    
    6. CONTINUATION PHASE:
       - if we processed directives but didn't DELEGATE/FINISH/WAIT:
           - create continuation prompt: "Actions completed. What next?"
           - recursively call manager_prompt(agent, continuation_prompt, message)
    
    7. ERROR HANDLING:
       - catch all exceptions in try/catch
       - if error occurs:
           - reprompt with error message.
       - return
    
    
    HELPER FUNCTIONS NEEDED:
    - _get_or_create_child_agent(parent, child_name, is_folder)
    - _get_parent_agent(agent)
    - _send_error_to_parent(agent, original_message, error)
    - coder_prompt(agent, prompt, message) [separate implementation]
    
    KEY DESIGN DECISIONS:
    - Recursive calls handle the message passing and state transitions
    - Each agent activation is self-contained (activate -> process -> deactivate)
    - Parse errors are handled by retrying with error context
    - Local actions (CREATE/DELETE/READ/RUN/UPDATE_README) continue execution
    - Control flow actions (DELEGATE/FINISH/WAIT) change execution path
    - Error propagation flows up the hierarchy
    """
    pass


# TODO:
# async def coder_prompt(agent, prompt, message) -> None