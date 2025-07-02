import asyncio
import time
import uuid
import sys
import traceback
from typing import Optional, Any, Dict, List
from src.agents.tester_agent import TesterAgent
from src.agents.base_agent import BaseAgent
from src.messages.protocol import Task
from src.llm.providers import get_llm_client

async def tester_spawner(
    parent_agent: BaseAgent, 
    prompt: str, 
    task: Optional[Task] = None,
    llm_client_name: Optional[str] = None
) -> None:
    """
    Spawns a tester ephemeral agent to handle testing tasks.
    
    PSEUDOCODE:
    
    1. CREATION PHASE:
       - create TesterAgent with parent and parent_path
       - set up LLM client if provided
       - set the task on the tester agent
    
    2. LLM RESPONSE PHASE:
       - add prompt to tester agent's prompt queue using agent.process_task(prompt)
    
    ERROR HANDLING:
       - catch all exceptions in try/catch
       - if error occurs:
           - reprompt parent with error message.
       - return
    """
    try:
        # 1. CREATION PHASE
        # Get LLM client
        llm_client = None
        if llm_client_name:
            llm_client = get_llm_client(llm_client_name)
        elif hasattr(parent_agent, 'llm_client') and parent_agent.llm_client:
            llm_client = parent_agent.llm_client
        
        # Create TesterAgent
        tester_agent = TesterAgent(
            parent=parent_agent,
            parent_path=str(parent_agent.path),
            llm_client=llm_client
        )
        
        # Set the task on the tester agent if provided
        if task is not None:
            tester_agent.active_task = task
        
        # Add the ephemeral agent to parent's tracking
        parent_agent.add_ephemeral_agent(tester_agent)
        
        # 2. LLM RESPONSE PHASE
        # Add prompt to tester agent's prompt queue using agent.process_task(prompt)
        await tester_agent.process_task(prompt)
        
    except Exception as error:
        # ERROR HANDLING: catch all exceptions in try/catch
        error_prompt = f"Error occurred during tester spawning: {str(error)}"
        try:
            await parent_agent.process_task(error_prompt)
        except Exception as reprompt_error:
            # If even the error reprompt fails, print details so the user can see.
            print(f"[tester_spawner] Failed to reprompt parent agent {parent_agent.path}: {reprompt_error}", file=sys.stderr)
            traceback.print_exc()
        return 