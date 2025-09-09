import typer

from . import llm_api
from . import context_collector

class DeveloperAgent:
    """
    The primary agent responsible for understanding a task, 
    gathering context, and generating code.
    """
    def __init__(self, project_root: str = "."):
        self.context_collector = context_collector.ContextCollector(root_path=project_root)
        self.agent_type = "developer"

    def execute_task(self, dev_context: str) -> str:
        """
        Generates the initial code based on a detailed context from the MCP.
        """
        prompt = self._construct_initial_prompt(dev_context)
        generated_code = llm_api.call_gemini(
            prompt=prompt, 
            task_type=llm_api.ModelType.CODE_GENERATION,
            agent_type=self.agent_type
        )
        return generated_code

    def fix_code(self, critique: str, original_code: str) -> str:
        """
        Fixes the code based on the reviewer's critique.
        """
        prompt = self._construct_fix_prompt(critique, original_code)
        fixed_code = llm_api.call_gemini(
            prompt=prompt,
            task_type=llm_api.ModelType.CODE_GENERATION,
            agent_type=self.agent_type
        )
        return fixed_code

    def _construct_initial_prompt(self, context: str) -> str:
        return f"""You are a creative and efficient senior Python developer.
Your primary goal is to write clean, functional code that makes the provided test case pass.

Based on the following context and test case, please generate the required Python code.
Only output the raw code, without any surrounding text or explanations.

--- CONTEXT & TEST CASE ---
{context}
--- END CONTEXT ---

Generated Code:"""

    def _construct_fix_prompt(self, critique: str, original_code: str) -> str:
        return f"""You are a senior Python developer. A reviewer has found issues in your code.
Your task is to carefully analyze their critique and provide a fixed version of the code that addresses all the points raised.
Only output the raw, fixed code.

--- REVIEWER'S CRITIQUE ---
{critique}

--- YOUR ORIGINAL CODE ---
{original_code}

--- FIXED CODE ---"""

class ReviewerAgent:
    """
    The agent responsible for quality control, writing tests, and reviewing code.
    Its goal is to be a critical and meticulous gatekeeper.
    """
    def __init__(self):
        self.agent_type = "reviewer"

    def write_test(self, user_prompt: str, constitution: str) -> str:
        """
        Generates a rigorous and effective failing test case based on the user prompt.
        """
        prompt = f"""You are a meticulous QA Engineer specializing in Test-Driven Development (TDD).
Your goal is to write a rigorous and effective failing test case using the pytest framework, based on the user's requirement.
The test must cover potential edge cases and serve as a clear, unambiguous specification for the feature.
Only output the raw Python code for the test.

{constitution}

--- USER REQUIREMENT ---
{user_prompt}
--- END REQUIREMENT ---

Failing Pytest Code:"""
        
        typer.secho("Reviewer Agent: Generating failing test case...", fg=typer.colors.MAGENTA)
        failing_test = llm_api.call_gemini(
            prompt=prompt,
            task_type=llm_api.ModelType.TEST_GENERATION,
            agent_type=self.agent_type
        )
        return failing_test

    def review_code(self, code_to_review: str, constitution: str) -> str:
        """
        Reviews code with a highly critical eye to find any potential flaws.
        """
        prompt = f"""You are a principal software engineer acting as a strict code reviewer.
Your sole objective is to find any possible flaw, bug, or deviation from best practices in the provided code.
Be ruthless and meticulous. Your reputation depends on finding even the smallest errors.
Provide a concise code review. If there are issues, list them clearly as bullet points. If and only if the code is absolutely perfect, respond with 'LGTM!'.

{constitution}

--- CODE TO REVIEW ---
{code_to_review}
--- END CODE ---

Code Review:"""

        typer.secho("Reviewer Agent: Reviewing generated code...", fg=typer.colors.MAGENTA)
        review = llm_api.call_gemini(
            prompt=prompt,
            task_type=llm_api.ModelType.CODE_REVIEW,
            agent_type=self.agent_type
        )
        return review
