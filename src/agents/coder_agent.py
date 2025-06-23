from .base_agent import BaseAgent, ContextEntry
from typing import Optional
from src.llm.base import BaseLLMClient
from src.llm.providers import (
    GPT41Client, O3Client, O3ProClient,
    ClaudeSonnet4Client, ClaudeOpus4Client,
    Gemini25FlashClient, Gemini25ProClient,
    DeepSeekV3Client, DeepSeekR1Client
)
from src.llm.providers import get_llm_client
from jinja2 import Environment, FileSystemLoader

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

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader('prompts'),
            trim_blocks=True,
            lstrip_blocks=True
        )

    async def api_call(self) -> None:
        '''
        Make an API call with current context and memory for coder agent.
        Concatenates all prompts in the queue, gets context, and calls the LLM client.
        '''
        # Set stall to true to prevent concurrent API calls
        self.stall = True

        # Get current prompt from queue
        current_prompt = "\n".join(self.prompt_queue) if self.prompt_queue else ""

        # Get memory contents
        memory_contents = self._get_memory_contents()

        # Get personal file content
        personal_file_name = ""
        if self.personal_file and self.personal_file.exists():
            personal_file_name = self.personal_file.name
        
        # Get codebase structure
        codebase_structure = self._get_codebase_structure_string()

        # Load Lark grammar
        lark_grammar = ""
        try:
            with open('src/coder_language/grammar.lark', 'r', encoding='utf-8') as f:
                lark_grammar = f.read()
        except Exception as e:
            lark_grammar = f"[Error reading Lark grammar: {str(e)}]"

        # Load language examples for coder agent
        language_examples = ""
        try:
            with open('prompts/coder/language_examples.md', 'r', encoding='utf-8') as f:
                language_examples = f.read()
        except Exception as e:
            language_examples = f"[Error reading language examples: {str(e)}]"

        # Load agent role description from markdown file
        try:
            with open('prompts/coder/agent_role.md', 'r', encoding='utf-8') as f:
                agent_role = f.read()
        except Exception as e:
            agent_role = f"[Error reading agent role: {str(e)}]"

        # Define available terminal commands and utilities
        try:
            with open('prompts/coder/available_commands.md', 'r', encoding='utf-8') as f:
                available_commands = f.read()
        except Exception as e:
            available_commands = "[Error reading available commands: {}]".format(str(e))

        if self.llm_client:
            if self.llm_client.supports_system_role:
                # Render split templates
                system_template = self.jinja_env.get_template('system_template.j2')
                user_template = self.jinja_env.get_template('user_template.j2')

                system_prompt = system_template.render(
                    agent_role=agent_role,
                    available_commands=available_commands,
                    lark_grammar=lark_grammar,
                    language_examples=language_examples
                )

                user_prompt = user_template.render(
                    active_task=str(self.active_task) if self.active_task else None,
                    context=self.context,
                    memory_contents=memory_contents,
                    personal_file_name=personal_file_name,
                    codebase_structure=codebase_structure,
                    current_prompt=current_prompt
                )

                messages = [
                    {"role": "user", "content": user_prompt}
                ]
                response = await self.llm_client.generate_response(messages, system_prompt=system_prompt)
            else:
                # Fallback monolithic
                template = self.jinja_env.get_template('agent_template.j2')
                formatted_prompt = template.render(
                    agent_role=agent_role,
                    active_task=str(self.active_task) if self.active_task else None,
                    context=self.context,
                    memory_contents=memory_contents,
                    personal_file_name=personal_file_name,
                    codebase_structure=codebase_structure,
                    available_commands=available_commands,
                    lark_grammar=lark_grammar,
                    language_examples=language_examples,
                    current_prompt=current_prompt
                )
                response = await self.llm_client.generate_response(formatted_prompt)

            # Save context
            self.context.append(ContextEntry(prompt=current_prompt, response=response))

            # Process response via coder language interpreter
            from src.coder_language.interpreter import execute_directive
            execute_directive(response, base_path=str(self.path), agent=self, own_file=str(self.path.name))

        # Clear prompt queue
        self.prompt_queue.clear()

        
