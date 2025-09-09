import typer
import os
from pathlib import Path

from . import agents
from . import models
from . import tools
from . import constitution

MAX_DEBATE_ROUNDS = 3

class MCP_Core:
    """
    The Multi-Agent Collaboration Platform (MCP) Core.
    This class orchestrates the entire workflow between agents.
    """
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.developer = agents.DeveloperAgent(project_root)
        self.reviewer = agents.ReviewerAgent()
        self.constitution_generator = constitution.ConstitutionGenerator(project_root)
        self.auto_approve = False

    def run_workflow(self, user_prompt: str, auto_approve: bool = False):
        """
        Executes the full TDD + Debate workflow.
        """
        self.auto_approve = auto_approve
        project_constitution = self.constitution_generator.generate()

        # Step 1: Reviewer writes a failing test
        typer.secho("--- Step 1: Reviewer is writing a failing test ---", bold=True)
        test_code_str = self.reviewer.write_test(user_prompt, project_constitution)
        typer.secho("--- Generated Test Case ---", fg=typer.colors.YELLOW)
        typer.secho(test_code_str)
        if not self._get_human_approval("Do you approve this test case?"):
            return

        # Generate dynamic file paths based on user prompt
        test_file_path, impl_file_path = self._generate_file_paths(user_prompt)
        
        test_case = models.TestCase(file_path=test_file_path, code=test_code_str)

        # Step 2: Developer writes initial code
        typer.secho("\n--- Step 2: Developer is writing initial code ---", bold=True)
        dev_context = self._build_developer_context(user_prompt, test_case, project_constitution)
        current_code = self.developer.execute_task(dev_context)

        # Step 3: Debate loop (Code-Review-Fix cycle)
        for i in range(MAX_DEBATE_ROUNDS):
            typer.secho(f"\n--- Step 3: Debate Round {i + 1}/{MAX_DEBATE_ROUNDS} ---", bold=True)
            typer.secho("Reviewer is reviewing the code...", fg=typer.colors.MAGENTA)
            review_str = self.reviewer.review_code(current_code, project_constitution)

            if "LGTM" in review_str.upper():
                typer.secho("Code approved by Reviewer Agent!", fg=typer.colors.GREEN)
                self._finalize_workflow(test_case, current_code, impl_file_path)
                return

            typer.secho("Code needs revision. Reviewer's critique:", fg=typer.colors.YELLOW)
            typer.secho(review_str)

            typer.secho("Developer is fixing the code...", fg=typer.colors.CYAN)
            current_code = self.developer.fix_code(critique=review_str, original_code=current_code)
            typer.secho("--- Generated Fix ---", fg=typer.colors.YELLOW)
            typer.secho(current_code)

        # If loop finishes without approval, escalate to human
        self._escalate_to_human(user_prompt, test_case.code, current_code, review_str, test_file_path, impl_file_path)

    def _generate_file_paths(self, user_prompt: str) -> tuple[str, str]:
        """
        Generate dynamic file paths based on the user prompt.
        
        Args:
            user_prompt: The user's development task description
            
        Returns:
            Tuple of (test_file_path, impl_file_path)
        """
        # Extract a meaningful name from the user prompt
        words = user_prompt.lower().split()
        # Find meaningful words (not common stop words)
        stop_words = {'create', 'make', 'build', 'implement', 'add', 'write', 'a', 'an', 'the', 'that', 'this', 'is', 'are', 'was', 'were', 'will', 'can', 'should', 'would', 'could'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        if meaningful_words:
            feature_name = meaningful_words[0]
        else:
            feature_name = "new_feature"
        
        # Generate test file path
        test_file_path = f"tests/test_{feature_name}.py"
        
        # Generate implementation file path
        impl_file_path = f"zswe_agent/{feature_name}.py"
        
        typer.secho(f"📁 Generated file paths:", fg=typer.colors.BLUE)
        typer.secho(f"   Test: {test_file_path}", fg=typer.colors.CYAN)
        typer.secho(f"   Implementation: {impl_file_path}", fg=typer.colors.CYAN)
        
        return test_file_path, impl_file_path

    def _finalize_workflow(self, test_case: models.TestCase, final_code: str, impl_file_path: str):
        typer.secho("--- Final Approval Stage ---", bold=True)
        typer.secho("The following implementation has been approved by the Reviewer Agent:", fg=typer.colors.GREEN)
        typer.secho(final_code)
        if self._get_human_approval("Do you give the final approval to write these files to disk?"):
            # Ensure test directory exists
            test_dir = Path(test_case.file_path).parent
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Ensure implementation directory exists
            impl_dir = Path(impl_file_path).parent
            impl_dir.mkdir(parents=True, exist_ok=True)
            
            tools.write_file(test_case.file_path, test_case.code)
            tools.write_file(impl_file_path, final_code)
            typer.secho("\nWorkflow finished successfully. Files written to disk.", fg=typer.colors.BRIGHT_GREEN)
        else:
            typer.secho("\nWorkflow aborted by user. No files were written.", fg=typer.colors.RED)

    def _escalate_to_human(self, user_prompt, test_code, final_code, final_critique, test_file_path, impl_file_path):
        typer.secho("\n--- Escalation: Consensus Not Reached ---", bold=True, fg=typer.colors.RED)
        typer.secho(f"After {MAX_DEBATE_ROUNDS} rounds, the Developer and Reviewer agents could not reach an agreement.")
        typer.secho("\nFinal points of disagreement:", bold=True)
        typer.secho(final_critique)
        typer.secho(f"\nProposed files:")
        typer.secho(f"  Test: {test_file_path}")
        typer.secho(f"  Implementation: {impl_file_path}")
        typer.secho("\nPlease review the final proposed code and choose an action.")
        # In a real CLI, you would present choices here (e.g., using Typer prompts)
        typer.secho("Workflow halted. Please review the state and decide on the next steps.")

    def _build_developer_context(self, user_prompt: str, test_case: models.TestCase, constitution: str) -> str:
        context = f"""{constitution}

User Requirement: {user_prompt}

Failing Test Case (`{test_case.file_path}`):
```python
{test_case.code}
```

Please write the implementation code that makes the above test case pass."""
        return context

    def _get_human_approval(self, prompt: str) -> bool:
        if self.auto_approve:
            typer.secho(f"{prompt} [Auto-approved]", fg=typer.colors.BRIGHT_BLACK)
            return True
        return typer.confirm(prompt)