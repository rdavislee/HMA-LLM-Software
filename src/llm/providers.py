"""Concrete LLM client classes for various providers/models.

Each class wraps the provider SDK (if available) and implements the
BaseLLMClient interface so the rest of the codebase can remain provider
agnostic.

Supports:
- OpenAI: GPT-4.1, o3, o3-pro
- Anthropic: Claude Sonnet 4, Claude Opus 4, Claude 3.7 Sonnet, Claude 3.5 Sonnet
- Google: Gemini 2.5 Flash, Gemini 2.5 Pro
- DeepSeek: DeepSeek V3, DeepSeek R1
"""

from __future__ import annotations

import os
from typing import List, Dict, Any, Optional, Union

from .base import BaseLLMClient

from dotenv import load_dotenv
load_dotenv()

# Load environment variables
ENV_OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ENV_ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
ENV_GOOGLE_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
ENV_DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
ENV_XAI_KEY = os.getenv("XAI_API_KEY")


def _ensure_api_key(var_name: str, value: Optional[str]):
    if not value:
        raise RuntimeError(
            f"Environment variable {var_name} not set – please add it to your .env file"
        )


# OpenAI family --------------------------------------------------------------

class OpenAIClient(BaseLLMClient):
    """Supports GPT-4.1 and standard OpenAI models."""

    def __init__(self, model: str = "gpt-4o") -> None:
        _ensure_api_key("OPENAI_API_KEY", ENV_OPENAI_KEY)
        import openai  # local import so package optional

        self.model = model

    @property
    def supports_system_role(self) -> bool:
        return True

    async def generate_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=ENV_OPENAI_KEY)

        if isinstance(messages, str):
            msgs = [{"role": "user", "content": messages}]
            if system_prompt:
                msgs.insert(0, {"role": "system", "content": system_prompt})
        else:
            msgs = messages

        response = await client.chat.completions.create(
            model=self.model,
            messages=msgs,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    async def generate_structured_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=ENV_OPENAI_KEY)
        
        if isinstance(messages, str):
            msgs = [{"role": "user", "content": messages}]
            if system_prompt:
                msgs.insert(0, {"role": "system", "content": system_prompt})
        else:
            msgs = messages
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=msgs,
            temperature=temperature,
            response_format={"type": "json_object", "schema": schema}
        )
        
        import json
        return json.loads(response.choices[0].message.content)


class GPT41Client(OpenAIClient):
    """GPT-4.1 specific client."""
    
    def __init__(self) -> None:
        super().__init__(model="gpt-4.1-2025-04-14")


class O3Client(BaseLLMClient):
    """OpenAI o3 reasoning model."""

    def __init__(self, model: str = "o3") -> None:
        _ensure_api_key("OPENAI_API_KEY", ENV_OPENAI_KEY)
        self.model = model

    @property
    def supports_system_role(self) -> bool:
        return True

    async def generate_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=ENV_OPENAI_KEY)

        if isinstance(messages, str):
            input_msgs = [{"role": "user", "content": messages}]
            if system_prompt:
                input_msgs.insert(0, {"role": "developer", "content": system_prompt})
        else:
            input_msgs = messages

        # o3 models use the responses API
        response = await client.responses.create(
            model=self.model,
            input=input_msgs,
            max_completion_tokens=max_tokens,
            temperature=temperature,
        )
        
        return response.output_text.strip()

    async def generate_structured_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        # For structured responses, we'll use the standard approach with prompt engineering
        import json
        
        if isinstance(messages, str):
            prompt = messages
        else:
            prompt = messages[-1]["content"] if messages else ""
        
        structured_prompt = f"""Please respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

User request: {prompt}"""
        
        response = await self.generate_response(
            structured_prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except:
            # Fallback: return empty dict if parsing fails
            return {}


class O3ProClient(O3Client):
    """OpenAI o3-pro reasoning model."""
    
    def __init__(self) -> None:
        super().__init__(model="o3-pro")


# Anthropic -------------------------------------------------------------------

class ClaudeClient(BaseLLMClient):
    """Base Anthropic Claude client."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022") -> None:
        _ensure_api_key("ANTHROPIC_API_KEY", ENV_ANTHROPIC_KEY)
        import anthropic

        self.client = anthropic.AsyncAnthropic(api_key=ENV_ANTHROPIC_KEY)
        self.model = model

    @property
    def supports_system_role(self) -> bool:
        return True

    async def generate_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        if isinstance(messages, str):
            msgs = [{"role": "user", "content": messages}]
        else:
            msgs = messages
            
        # Anthropic requires system prompt as separate parameter
        kwargs = {
            "model": self.model,
            "messages": msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
            
        response = await self.client.messages.create(**kwargs)
        return response.content[0].text.strip()

    async def generate_structured_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        import json
        
        if isinstance(messages, str):
            prompt = messages
        else:
            prompt = messages[-1]["content"] if messages else ""
        
        structured_prompt = f"""Please respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

User request: {prompt}"""
        
        response = await self.generate_response(
            structured_prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except:
            # Fallback: return empty dict if parsing fails
            return {}


class ClaudeSonnet4Client(ClaudeClient):
    """Claude Sonnet 4 - enhanced reasoning and coding."""
    
    def __init__(self) -> None:
        super().__init__(model="claude-sonnet-4-20250514")


class ClaudeOpus4Client(ClaudeClient):
    """Claude Opus 4 - most powerful Claude model."""
    
    def __init__(self) -> None:
        super().__init__(model="claude-opus-4-20250514")


class ClaudeSonnet37Client(ClaudeClient):
    """Claude 3.7 Sonnet - hybrid reasoning model."""
    
    def __init__(self) -> None:
        super().__init__(model="claude-3-7-sonnet-20250219")


class ClaudeSonnet35Client(ClaudeClient):
    """Claude 3.5 Sonnet - balanced performance."""
    
    def __init__(self) -> None:
        super().__init__(model="claude-3-5-sonnet-20241022")


# Google Gemini ---------------------------------------------------------------

class GeminiClient(BaseLLMClient):
    """Base Google Gemini client."""
    
    def __init__(self, model: str = "models/gemini-2.5-pro") -> None:
        _ensure_api_key("GOOGLE_GEMINI_API_KEY", ENV_GOOGLE_KEY)
        import google.generativeai as genai

        genai.configure(api_key=ENV_GOOGLE_KEY)
        self.model = genai.GenerativeModel(model)

    @property
    def supports_system_role(self) -> bool:
        return True

    async def generate_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 100000,
        _retries: int = 5,
    ) -> str:
        """Generate a response from Gemini with a simple retry loop.

        Gemini occasionally returns a candidate with no valid `Part` which causes
        the SDK's quick-accessors such as `response.text` to raise a *ValueError*.
        This helper will transparently retry the request a few times before
        bubbling the error up to the caller.
        """

        # Gemini SDK uses list of dict("role","parts")
        if isinstance(messages, str):
            contents = messages
            if system_prompt:
                contents = f"{system_prompt}\n\n{messages}"
        else:
            # Convert messages to Gemini format
            contents = []
            if system_prompt:
                contents.append({"role": "user", "parts": [system_prompt]})
                contents.append({"role": "model", "parts": ["I understand. How can I help you?"]})
            
            for msg in messages:
                if msg["role"] == "system":
                    # Gemini doesn't have system role, convert to user/model exchange
                    contents.append({"role": "user", "parts": [msg["content"]]})
                    contents.append({"role": "model", "parts": ["I understand."]})
                elif msg["role"] == "assistant":
                    contents.append({"role": "model", "parts": [msg["content"]]})
                else:
                    contents.append({"role": "user", "parts": [msg["content"]]})
        
        last_err: Optional[Exception] = None
        for attempt in range(1, _retries + 1):
            try:
                response = await self.model.generate_content_async(
                    contents,
                    generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
                )

                # Accessing `.text` may raise ValueError when no parts are returned.
                text = response.text.strip()
                if text:
                    return text
                # Empty string – treat as failure so we can retry.
                raise ValueError("Gemini returned an empty string response")
            except ValueError as e:
                # Capture and retry unless we've exhausted attempts
                last_err = e
                if attempt == _retries:
                    raise
                # Optionally, small exponential back-off could be added here
            except Exception as e:
                # For non-ValueError exceptions (network issues etc.) we also retry
                last_err = e
                if attempt == _retries:
                    raise

        # If we exited the loop without returning, re-raise the last error (safety)
        if last_err is not None:
            raise last_err

    async def generate_structured_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        import json
        
        if isinstance(messages, str):
            prompt = messages
        else:
            prompt = messages[-1]["content"] if messages else ""
        
        structured_prompt = f"""Please respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

User request: {prompt}"""
        
        response = await self.generate_response(
            structured_prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except:
            # Fallback: return empty dict if parsing fails
            return {}


class Gemini25FlashClient(GeminiClient):
    """Gemini 2.5 Flash - fast and efficient."""
    
    def __init__(self) -> None:
        super().__init__(model="models/gemini-2.5-flash")


class Gemini25ProClient(GeminiClient):
    """Gemini 2.5 Pro - powerful reasoning model."""
    
    def __init__(self) -> None:
        super().__init__(model="models/gemini-2.5-pro")


# DeepSeek --------------------------------------------------------------------

class DeepSeekClient(BaseLLMClient):
    """Base DeepSeek client using OpenAI-compatible API."""
    
    def __init__(self, model: str = "deepseek-chat") -> None:
        _ensure_api_key("DEEPSEEK_API_KEY", ENV_DEEPSEEK_KEY)
        self.model = model
        self.api_key = ENV_DEEPSEEK_KEY

    @property
    def supports_system_role(self) -> bool:
        return True

    async def generate_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 65536,
    ) -> str:
        from openai import AsyncOpenAI
        
        # DeepSeek uses OpenAI-compatible API
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
        if isinstance(messages, str):
            msgs = [{"role": "user", "content": messages}]
            if system_prompt:
                msgs.insert(0, {"role": "system", "content": system_prompt})
        else:
            msgs = messages

        response = await client.chat.completions.create(
            model=self.model,
            messages=msgs,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )
        
        return response.choices[0].message.content.strip()

    async def generate_structured_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        import json
        
        if isinstance(messages, str):
            prompt = messages
        else:
            prompt = messages[-1]["content"] if messages else ""
        
        structured_prompt = f"""Please respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

User request: {prompt}"""
        
        response = await self.generate_response(
            structured_prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except:
            # Fallback: return empty dict if parsing fails
            return {}


class DeepSeekV3Client(DeepSeekClient):
    """DeepSeek V3 - general purpose model."""
    
    def __init__(self) -> None:
        super().__init__(model="deepseek-chat")


class DeepSeekR1Client(DeepSeekClient):
    """DeepSeek R1 - reasoning model."""
    
    def __init__(self) -> None:
        super().__init__(model="deepseek-reasoner")


# ---------------------------------------------------------------------------
# Console / Manual testing client ------------------------------------------
# ---------------------------------------------------------------------------

class ConsoleLLMClient(BaseLLMClient):
    """A dummy LLM client that prints the prompt to stdout and reads the reply from the user.

    This is useful for manual testing – you can act as the language model yourself
    or pipe the prompt into another tool and paste back the response.
    """

    async def _async_input(self, prompt: str) -> str:
        """Non-blocking wrapper around built-in input() suitable for asyncio."""
        import asyncio
        return await asyncio.to_thread(input, prompt)

    async def generate_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        # Normalise to list[dict]
        if isinstance(messages, str):
            msgs = [{"role": "user", "content": messages}]
        else:
            msgs = messages

        print("\n======================== LLM CALL (Console) ========================")
        if system_prompt:
            print("-- System prompt --")
            print(system_prompt)
            print("------------------------------------------------------------------")
        for m in msgs:
            role = m.get("role", "user")
            print(f"[{role}] {m.get('content', '')}")
        print("==================================================================\n")

        # Read user input as the model output
        response = await self._async_input("LLM reply> ")
        return response.strip()

    async def generate_structured_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        import json
        text_response = await self.generate_response(messages, system_prompt, temperature)
        try:
            return json.loads(text_response)
        except json.JSONDecodeError:
            print("[ConsoleLLMClient] Warning: Could not parse JSON – returning empty dict.")
            return {}
        
class GrokClient(BaseLLMClient):
    """Base xAI Grok client using OpenAI-compatible API."""
    
    def __init__(self, model: str = "grok-beta") -> None:
        _ensure_api_key("XAI_API_KEY", ENV_XAI_KEY)
        self.model = model
        self.api_key = ENV_XAI_KEY

    @property
    def supports_system_role(self) -> bool:
        return True

    async def generate_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 100000,
    ) -> str:
        from openai import AsyncOpenAI
        
        # xAI uses OpenAI-compatible API
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
        
        if isinstance(messages, str):
            msgs = [{"role": "user", "content": messages}]
            if system_prompt:
                msgs.insert(0, {"role": "system", "content": system_prompt})
        else:
            msgs = messages

        response = await client.chat.completions.create(
            model=self.model,
            messages=msgs,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content.strip()

    async def generate_structured_response(
        self,
        messages: Union[str, List[Dict[str, str]]],
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        import json
        
        if isinstance(messages, str):
            prompt = messages
        else:
            prompt = messages[-1]["content"] if messages else ""
        
        structured_prompt = f"""Please respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

User request: {prompt}"""
        
        response = await self.generate_response(
            structured_prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except:
            # Fallback: return empty dict if parsing fails
            return {}


class Grok3Client(GrokClient):
    """Grok 3 - flagship model for enterprise tasks."""
    
    def __init__(self) -> None:
        super().__init__(model="grok-3-beta")


class Grok3MiniClient(GrokClient):
    """Grok 3 Mini - lightweight reasoning model for math and quantitative tasks."""
    
    def __init__(self) -> None:
        super().__init__(model="grok-3-mini")


# Convenience mapping for easy model selection
MODEL_CLIENTS = {
    # OpenAI
    "gpt-4o": OpenAIClient,
    "gpt-4.1": GPT41Client,
    "o3": O3Client,
    "o3-pro": O3ProClient,
    
    # Anthropic
    "claude-sonnet-4": ClaudeSonnet4Client,
    "claude-opus-4": ClaudeOpus4Client,
    "claude-3.7-sonnet": ClaudeSonnet37Client,
    "claude-3.5-sonnet": ClaudeSonnet35Client,
    
    # Google
    "gemini-2.5-flash": Gemini25FlashClient,
    "gemini-2.5-pro": Gemini25ProClient,
    
    # DeepSeek
    "deepseek-v3": DeepSeekV3Client,
    "deepseek-r1": DeepSeekR1Client,
    
    # xAI Grok - NEW!
    "grok-3": Grok3Client,
    "grok-3-mini": Grok3MiniClient,

    # Console
    "console": ConsoleLLMClient,
}


def _patch_quota_handler():
    """Monkey-patch all client generate_response methods to gracefully handle
    quota/context window errors. When such an error is detected we:
    1. Wait 60 seconds (simple back-off).
    2. Return a FINISH directive so the calling agent can gracefully exit and
       ask the parent to reprompt with a fresh, smaller context.
    This avoids the need for changes in every agent implementation – the
    safeguard lives in one central place.
    """

    import asyncio
    import inspect

    # Keywords signalling quota or context problems. All lowercase for easier
    # comparison.
    _ERROR_KEYWORDS = {
        "quota",                   # generic quota exceeded
        "resourceexhausted",      # Google / gRPC 429
        "context length",         # OpenAI / Anthropic style
        "maximum context",        # OpenAI style
        "token limit",            # generic token limit overrun
        "too many tokens",        # Anthropic style
        "context window",         # DeepSeek / others
    }

    def _needs_wrap(cls):
        return not getattr(cls, "_quota_wrapper_installed", False)

    def _wrap(cls):
        original = cls.generate_response

        # Ensure we keep a reference to the original for potential debugging
        setattr(cls, "_orig_generate_response", original)

        async def wrapped(self, *args, **kwargs):  # type: ignore[override]
            try:
                return await original(self, *args, **kwargs)
            except Exception as e:  # noqa: BLE001 – intentionally broad
                msg = str(e).lower()
                if any(key in msg for key in _ERROR_KEYWORDS):
                    # Detected quota/context window related error – back-off
                    print(
                        f"[providers] Quota/Context error detected from {cls.__name__}: {e}. "
                        "Sleeping 60 s then returning FINISH directive."
                    )
                    await asyncio.sleep(60)
                    return (
                        'FINISH PROMPT="Context became too large. Please reprompt me with the same task."'
                    )
                # Unknown exception – bubble up unchanged
                raise

        # Preserve metadata for nicer debugging / introspection
        wrapped = asyncio.coroutine(wrapped) if not inspect.iscoroutinefunction(original) else wrapped
        setattr(cls, "generate_response", wrapped)
        setattr(cls, "_quota_wrapper_installed", True)

    for _client_cls in set(MODEL_CLIENTS.values()):
        if _needs_wrap(_client_cls):
            _wrap(_client_cls)

# Install the handler immediately upon import
_patch_quota_handler()


def get_llm_client(model_name: str) -> BaseLLMClient:
    """Factory function to get the appropriate LLM client for a model name."""
    if model_name not in MODEL_CLIENTS:
        raise ValueError(f"Unknown model: {model_name}. Available models: {list(MODEL_CLIENTS.keys())}")
    
    return MODEL_CLIENTS[model_name]()