import re
from pathlib import Path
import typer

from . import tools

class ContextCollector:
    """
    Gathers and assembles context based on a user prompt and project structure.
    """
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()

    def collect(self, user_prompt: str) -> str:
        """
        Collects context based on file/dir paths found in the user prompt.

        This is a very basic MVP implementation. Future versions will use more
        sophisticated techniques (AST, git status, etc.).

        Args:
            user_prompt: The initial user command.

        Returns:
            A string containing all the collected context.
        """
        typer.secho(f"Collecting context from prompt: '{user_prompt}'", fg=typer.colors.CYAN)
        
        # A simple regex to find potential file/directory paths mentioned in the prompt.
        potential_paths = re.findall(r'[\w\./-]+\.[\w]+|[\w\./-]+/', user_prompt)
        
        collected_context = []
        collected_context.append("--- Initial User Prompt ---")
        collected_context.append(user_prompt)
        
        if not potential_paths:
            typer.secho("No file/directory paths found in prompt. Using prompt as the only context.", fg=typer.colors.YELLOW)
            return user_prompt

        collected_context.append("\n--- Collected File Context ---")
        for path_str in set(potential_paths): # Use set to avoid duplicate processing
            # Ensure path is relative to the project root for security and consistency
            path = self.root_path / Path(path_str).name
            
            if path.is_file():
                collected_context.append(f"\n--- Content of file: {Path(path_str).name} ---")
                content = tools.read_file(str(path))
                collected_context.append(content)
            else:
                typer.secho(f"Path '{path_str}' mentioned in prompt is not a valid file in the project root. Skipping.", fg=typer.colors.YELLOW)
        
        return "\n".join(collected_context)