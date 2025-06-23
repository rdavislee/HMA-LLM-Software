"""
Abstract base class for LLM interfaces.
Will define:
- Common interface for all LLM providers
- Usage tracking
- Error handling
- Retry logic
"""

from abc import ABC, abstractmethod # "Abstract Base Classes"
from typing import List, Dict, Any, Optional

class BaseLLMClient(ABC):
    '''
    Abstract base class for LLM clients.
    '''
    
    @abstractmethod
    async def generate_response(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None,
        temperature: float = 0.7, max_tokens: int = 1000
    ) -> str:
        '''
        Generate a response from the LLM.
        '''
        pass

    @abstractmethod
    async def generate_structured_response(
        self, messages: List[Dict[str, str]], schema: Dict[str, Any],
        system_prompt: Optional[str] = None, temperature: float = 0.7
    ) -> Dict[str, Any]:
        '''
        Generate a structured response matching the provided schema.
        '''
        pass

    @property
    def supports_system_role(self) -> bool:
        """Return True if the provider supports a dedicated `system` role.

        Providers that only accept a single prompt string (legacy completion
        style) should override this to return False so that the agents can
        fall back to the monolithic Jinja2 template.
        """
        return True