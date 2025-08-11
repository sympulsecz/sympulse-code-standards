"""Update project standards to latest version."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.core import StandardsManager

app = typer.Typer(
    name="update",
    help="Update project standards to latest version",
    add_completion=False,
)

console = Console()


@app.command()
def project(
    path: Path = typer.Argument(Path.cwd(), help="Project path to update"),
    language: Optional[str] = typer.Option(
        None, "--language", "-l", help="Specific language to update"
    ),
    version: Optional[str] = typer.Option(
        None, "--version", "-v", help="Standards version to update to"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force update even if conflicts exist"
    ),
):
    """Update project standards to latest version."""
    try:
        if not path.exists():
            console.print(f"[red]Error: Path {path} does not exist[/red]")
            raise typer.Exit(1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Updating project standards...", total=None)

            manager = StandardsManager()
            success = manager.update_project_standards(path, language, version)

            if success:
                progress.update(task, description="Standards updated successfully!")
                console.print(f"\n✅ Project standards updated successfully!")
            else:
                progress.update(task, description="Failed to update standards")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
