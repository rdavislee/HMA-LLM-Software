"""
Tester Agent - an ephemeral agent for testing tasks.

This agent is spawned by regular coder or manager agents to perform
context-heavy testing operations and report back concise results.
"""

from .ephemeral_agent import EphemeralAgent, ContextEntry
from .base_agent import BaseAgent
from typing import Optional
from src.llm.base import BaseLLMClient
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import src
import os

class TesterAgent(EphemeralAgent):
    """
    Tester agent that performs testing tasks for parent agents.
    Inherits from EphemeralAgent and implements the api_call method
    to handle testing-specific prompts and LLM interactions.
    
    Each tester agent gets a personal scratch pad file for debugging and temporary code.
    """
    
    def __init__(
        self,
        parent: "BaseAgent", 
        parent_path: str,
        llm_client: Optional[BaseLLMClient] = None,
        max_context_size: int = 8000
    ) -> None:
        super().__init__(parent, parent_path, llm_client, max_context_size)
        
        # Create scratch pad file
        self.personal_file = self._create_scratch_pad()
        
        # Add scratch pad to memory
        if self.personal_file:
            self.memory[self.personal_file.name] = self.personal_file
        
        # Initialize Jinja2 environment – resolve the absolute path to the
        # project-level "prompts" directory so the templates are found
        # regardless of the script's current working directory.
        project_root = Path(__file__).resolve().parent.parent.parent
        templates_dir = project_root / "prompts"

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _create_scratch_pad(self) -> Optional[Path]:
        """
        Create a scratch pad file for this tester agent.
        File is created in ROOT_DIR/scratch_pads/ with name based on parent path.
        """
        if src.ROOT_DIR is None:
            print("[TesterAgent] Warning: ROOT_DIR not set, cannot create scratch pad")
            return None
        
        try:
            # Create scratch_pads directory if it doesn't exist
            scratch_pads_dir = src.ROOT_DIR / "scratch_pads"
            scratch_pads_dir.mkdir(exist_ok=True)
            
            # Convert parent path to scratch pad filename
            # Example: src/auth/user.py -> src.auth.user.py
            try:
                relative_parent_path = Path(self.parent_path).relative_to(src.ROOT_DIR)
                scratch_pad_name = str(relative_parent_path).replace("/", ".").replace("\\", ".")
                
                # If parent path is a directory, add a suffix to distinguish it
                if Path(self.parent_path).is_dir():
                    scratch_pad_name += "_manager"
                
                # Add .py extension for Python scratch pad
                scratch_pad_name += "_scratch.py"
                
            except ValueError:
                # Fallback if parent path is not relative to ROOT_DIR
                scratch_pad_name = "tester_scratch.py"
            
            scratch_pad_path = scratch_pads_dir / scratch_pad_name
            
            # Create the scratch pad file with initial content
            initial_content = f"""# Tester Agent Scratch Pad
            # Parent: {self.parent_path}
            # Created for debugging and temporary code

            # You can write any Python code here for testing purposes
            # This file is ephemeral and will be cleaned up when the tester agent completes

            def debug_helper():
                \"\"\"Helper function for debugging.\"\"\"
                pass

            # Add your debugging code below:

            """
            
            with open(scratch_pad_path, 'w', encoding='utf-8') as f:
                f.write(initial_content)
            
            print(f"[TesterAgent] Created scratch pad: {scratch_pad_path}")
            return scratch_pad_path
            
        except Exception as e:
            print(f"[TesterAgent] Failed to create scratch pad: {e}")
            return None

    def cleanup_scratch_pad(self):
        """
        Clean up the scratch pad file when the tester agent is done.
        """
        if self.personal_file and self.personal_file.exists():
            try:
                self.personal_file.unlink()
                print(f"[TesterAgent] Cleaned up scratch pad: {self.personal_file}")
            except Exception as e:
                print(f"[TesterAgent] Failed to cleanup scratch pad: {e}")

    async def api_call(self) -> None:
        '''
        Make an API call with current context and memory for tester agent.
        Uses system_template.j2 for system prompt and tester_template.j2 for user input.
        '''
        # Set stall to true to prevent concurrent API calls
        self.stall = True
        

        # Get current prompt from queue
        current_prompt = "\n".join(self.prompt_queue) if self.prompt_queue else ""
        
        # Get memory contents
        memory_contents = self._get_memory_contents()
        
        # Get codebase structure
        codebase_structure = self._get_codebase_structure_string()
        
        # Get personal file name for template
        personal_file_name = ""
        if self.personal_file and self.personal_file.exists():
            personal_file_name = self.personal_file.name
        
        # Load testing-specific information for system prompt
        testing_commands = ""
        try:
            # Use tester commands for system prompt
            with open('prompts/tester/available_commands.md', 'r', encoding='utf-8') as f:
                testing_commands = f.read()
        except Exception as e:
            testing_commands = f"[Error reading testing commands: {str(e)}]"
        
        # Load tester agent role description
        try:
            with open('prompts/tester/agent_role.md', 'r', encoding='utf-8') as f:
                agent_role = f.read()
            # Modify role for tester context if needed
            if agent_role.strip():
                agent_role = "# Tester Agent Role\n\nYou are a **Tester Agent** - an ephemeral agent specialized in testing tasks.\n\n" + agent_role
            else:
                agent_role = "# Tester Agent Role\n\nYou are a **Tester Agent** - an ephemeral agent specialized in testing tasks."
        except Exception as e:
            agent_role = f"[Error reading agent role: {str(e)}]"
        
        # Prepend parent path information to agent role
        if src.ROOT_DIR is None:
            raise RuntimeError("ROOT_DIR is not set. Please initialize it with src.set_root_dir(<project_root_path>) before creating agents.")

        try:
            parent_path_display = str(self.parent_path.resolve().relative_to(src.ROOT_DIR))
        except ValueError:
            parent_path_display = str(self.parent_path.resolve())

        agent_role = f"**Parent Path (from project root):** {parent_path_display}\n\n" + agent_role
        
        # Add scratch pad information to role
        if self.personal_file:
            agent_role += f"\n\n**Personal Scratch Pad:** {self.personal_file.name} - Use this for debugging and temporary code."
        
        # Load grammar (use tester grammar)
        lark_grammar = ""
        try:
            with open('prompts/tester/tester_grammar.lark', 'r', encoding='utf-8') as f:
                lark_grammar = f.read()
        except Exception as e:
            lark_grammar = f"[Error reading Lark grammar: {str(e)}]"
        
        # Load language examples
        language_examples = ""
        try:
            with open('prompts/tester/language_examples.md', 'r', encoding='utf-8') as f:
                language_examples = f.read()
        except Exception as e:
            language_examples = f"[Error reading language examples: {str(e)}]"

        if self.llm_client:
            if self.llm_client.supports_system_role:
                # Render split templates
                system_template = self.jinja_env.get_template('system_template.j2')
                tester_template = self.jinja_env.get_template('tester_template.j2')

                system_prompt = system_template.render(
                    agent_role=agent_role,
                    available_commands=testing_commands,
                    lark_grammar=lark_grammar,
                    language_examples=language_examples,
                    agent_path=parent_path_display
                )

                # Determine parent type
                parent_type = 'manager' if hasattr(self.parent, 'is_manager') and self.parent.is_manager else 'coder'
                
                user_prompt = tester_template.render(
                    active_task=str(self.active_task) if self.active_task else None,
                    context=self.context,
                    memory_contents=memory_contents,
                    codebase_structure=codebase_structure,
                    parent_path=parent_path_display,
                    parent_type=parent_type,
                    current_prompt=current_prompt,
                    personal_file_name=personal_file_name
                )

                messages = [
                    {"role": "user", "content": user_prompt}
                ]
                response = await self.llm_client.generate_response(messages, system_prompt=system_prompt)
            else:
                # Fallback to monolithic template (agent_template.j2)
                template = self.jinja_env.get_template('agent_template.j2')
                formatted_prompt = template.render(
                    agent_role=agent_role,
                    active_task=str(self.active_task) if self.active_task else None,
                    context=self.context,
                    memory_contents=memory_contents,
                    personal_file_name=personal_file_name,
                    codebase_structure=codebase_structure,
                    available_commands=testing_commands,
                    lark_grammar=lark_grammar,
                    language_examples=language_examples,
                    current_prompt=current_prompt,
                    agent_path=parent_path_display,
                    children=[],  # Ephemeral agents don't have children
                    active_children=[]
                )
                response = await self.llm_client.generate_response(formatted_prompt)

            # Save context
            self.context.append(ContextEntry(prompt=current_prompt, response=response))
            
            # Clear prompt queue
            self.prompt_queue.clear()

            # Process response via tester language interpreter
            from src.languages.tester_language.interpreter import execute_directive
            execute_directive(response, agent=self)