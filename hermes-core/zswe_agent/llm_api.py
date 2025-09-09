import os
import typer
import google.generativeai as genai
from enum import Enum
import random

# --- API Key Configuration ---
API_KEY_CONFIGURED = False
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API Key not found. Please set the GOOGLE_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    API_KEY_CONFIGURED = True
except ValueError as e:
    typer.secho(f"Warning: {e}", fg=typer.colors.YELLOW)

# --- Available Models for Anti-Collusion (Only verified working models) ---
AVAILABLE_MODELS = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest"
]

# --- Model Selection Enum ---
class ModelType(Enum):
    """Enum to represent different types of tasks for model selection."""
    CODE_GENERATION = "CODE_GENERATION"
    CODE_REVIEW = "CODE_REVIEW"
    TEST_GENERATION = "TEST_GENERATION"

# --- Model Assignment Strategy ---
class ModelAssigner:
    """Assigns different models to different agents to prevent collusion."""
    
    def __init__(self):
        self.agent_models = {}
        self._assign_models_to_agents()
    
    def _assign_models_to_agents(self):
        """Assign different models to different agent types."""
        # Developer Agent gets one model
        dev_model = random.choice(AVAILABLE_MODELS)
        self.agent_models['developer'] = dev_model
        
        # Reviewer Agent gets a different model
        remaining_models = [m for m in AVAILABLE_MODELS if m != dev_model]
        rev_model = remaining_models[0] if remaining_models else dev_model
        self.agent_models['reviewer'] = rev_model
        
        typer.secho(f"🔒 Anti-Collusion Model Assignment:", fg=typer.colors.GREEN)
        typer.secho(f"   Developer Agent: {dev_model}", fg=typer.colors.CYAN)
        typer.secho(f"   Reviewer Agent: {rev_model}", fg=typer.colors.MAGENTA)
    
    def get_model_for_agent(self, agent_type: str) -> str:
        """Get the assigned model for a specific agent type."""
        return self.agent_models.get(agent_type, AVAILABLE_MODELS[0])
    
    def get_model_for_task(self, task_type: ModelType, agent_type: str = None) -> str:
        """Get the appropriate model for a task, considering agent type."""
        if agent_type and agent_type in self.agent_models:
            return self.agent_models[agent_type]
        
        # Fallback to task-based selection
        if task_type == ModelType.CODE_GENERATION:
            return self.agent_models.get('developer', AVAILABLE_MODELS[0])
        elif task_type == ModelType.CODE_REVIEW:
            return self.agent_models.get('reviewer', AVAILABLE_MODELS[1] if len(AVAILABLE_MODELS) > 1 else AVAILABLE_MODELS[0])
        else:
            return AVAILABLE_MODELS[0]

# Global model assigner instance
model_assigner = ModelAssigner()

# --- Model Call Function ---
def call_gemini(prompt: str, task_type: ModelType = ModelType.CODE_GENERATION, agent_type: str = None) -> str:
    """
    Sends a prompt to the appropriate Gemini model based on the task type and agent type.
    Implements anti-collusion by using different models for different agents.

    Args:
        prompt: The text prompt to send to the model.
        task_type: The type of task, used to select the right model.
        agent_type: The type of agent making the call (for anti-collusion).

    Returns:
        The generated text from the model or an error message.
    """
    if not API_KEY_CONFIGURED:
        return "Error: Gemini API key is not configured. Cannot make API calls."

    model_name = model_assigner.get_model_for_task(task_type, agent_type)
    typer.secho(f"Calling model '{model_name}' for {agent_type or task_type.value}...", fg=typer.colors.CYAN)

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_message = f"An unexpected error occurred while calling the Gemini API: {e}"
        typer.secho(error_message, fg=typer.colors.RED)
        return f"Error: {error_message}"