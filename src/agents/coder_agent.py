from .base_agent import BaseAgent
from typing import Optional
from ..llm.base import BaseLLMClient

class CoderAgent(BaseAgent):
    """
    Coder agent that manages a single code file.
    Implements only the api_call method, which handles prompt processing and LLM interaction.
    """
    def __init__(
        self,
        path: str,
        parent: Optional[BaseAgent] = None,
        llm_client: Optional[BaseLLMClient] = None,
        max_context_size: int = 8000
    ) -> None:
        super().__init__(path, parent, llm_client, max_context_size)

    async def api_call(self) -> None:
        '''
        Make an API call with current context and memory for coder agent.
        Concatenates all prompts in the queue, gets context, and calls the LLM client.
        '''
        # Set stall to true to prevent concurrent API calls
        self.stall = True

        # Concatenate all prompts in queue (numbered)
        numbered_prompts = []
        for i, prompt in enumerate(self.prompt_queue, 1):
            numbered_prompts.append(f"{i}. {prompt}")
        full_prompt = "\n".join(numbered_prompts)

        # Get context string for LLM
        context_string = await self.get_context_string()

        # Make API call
        if self.llm_client:
            response = await self.llm_client.generate_response(
                prompt=full_prompt,
                context=context_string
            )
            # Add to context (prompt -> response)
            self.context[full_prompt] = response
            # (Optional) Post-process response here if needed

        # Clear prompt queue
        self.prompt_queue.clear()

        
