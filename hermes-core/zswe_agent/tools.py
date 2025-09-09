from pathlib import Path
import typer

def read_file(path: str) -> str:
    """
    Reads the content of a file and returns it as a string.

    Args:
        path: The absolute or relative path to the file.

    Returns:
        The content of the file.
    """
    file_path = Path(path)
    if not file_path.is_file():
        typer.secho(f"Error: Path {path} is not a valid file.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    try:
        with file_path.open('r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        typer.secho(f"Error reading file at {path}: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

def write_file(path: str, content: str) -> None:
    """
    Writes content to a file. Creates parent directories if they don't exist.

    Args:
        path: The absolute or relative path to the file.
        content: The content to write to the file.
    """
    file_path = Path(path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open('w', encoding='utf-8') as f:
            f.write(content)
        typer.secho(f"Successfully wrote to {path}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error writing to file at {path}: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


def list_directory(path: str) -> None:
    """
    Lists the contents of a directory.

    Args:
        path: The absolute or relative path to the directory.
    """
    dir_path = Path(path)
    if not dir_path.is_dir():
        typer.secho(f"Error: Path {path} is not a valid directory.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"Contents of {path}:")
    for item in sorted(dir_path.iterdir()):
        if item.is_dir():
            typer.secho(f"  {item.name}/", fg=typer.colors.BLUE)
        else:
            typer.secho(f"  {item.name}")