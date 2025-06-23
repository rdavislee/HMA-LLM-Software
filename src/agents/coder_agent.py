from .base_agent import BaseAgent, ContextEntry
from typing import Optional
from src.llm.base import BaseLLMClient
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

        # TODO: Load language examples for coder agent if they exist

        # Define agent role and commands
        agent_role = "You are a Coder agent. Your primary role is to write and modify code in a single file. You can read other files for context, but you can only change your assigned file."
        available_commands = """
        ### Testing Commands
        - `python -m pytest tests/` - Run all tests
        - `python -m pytest tests/ -v` - Run tests with verbose output
        - `python -m pytest tests/ -k "test_name"` - Run specific test
        - `python -m pytest tests/test_file.py::test_function` - Run specific test function
        - `python -m unittest discover tests` - Run tests using unittest

        ### Code Quality
        - `flake8 filename.py` - Run linting on specific file
        - `black filename.py` - Format code with black
        - `isort filename.py` - Sort imports in file
        - `mypy filename.py` - Run type checking on file

        ### File Operations
        - `cat filename` - Display file contents
        - `head -n 20 filename` - Show first 20 lines of file
        - `tail -n 20 filename` - Show last 20 lines of file
        - `grep -n "pattern" filename` - Search for pattern with line numbers
        - `wc -l filename` - Count lines in file

        ### Development Tools
        - `python -c "import filename; help(filename)"` - Get help on module
        - `python -m doctest filename.py` - Run doctests in file
        - `python -m py_compile filename.py` - Check syntax without executing
        """

        # Render template
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
            language_examples="", # No examples for now
            current_prompt=current_prompt
        )

        # Make API call
        if self.llm_client:
            response = await self.llm_client.generate_response(
                prompt=formatted_prompt,
                context="" # Context is included in the prompt
            )
            # Add to context (prompt -> response)
            self.context.append(ContextEntry(prompt=current_prompt, response=response))
            # (Optional) Post-process response here if needed

        # Clear prompt queue
        self.prompt_queue.clear()

        
