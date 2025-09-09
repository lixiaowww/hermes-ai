import typer
from . import mcp

def main(
    user_prompt: str = typer.Argument(..., help="The development task for the agent to perform."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Auto-approve all confirmation prompts for non-interactive testing.")
):
    """ZSCE-Agent: A multi-agent system for automated software development."""
    typer.secho(f"Received task: {user_prompt}", fg=typer.colors.BLUE)
    
    # Initialize and run the MCP Core workflow
    mcp_core = mcp.MCP_Core()
    mcp_core.run_workflow(user_prompt, auto_approve=yes)

if __name__ == "__main__":
    typer.run(main)