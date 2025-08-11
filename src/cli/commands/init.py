"""Initialize a new project with coding standards."""

from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint

from src.generators import ProjectGenerator
from .base import (
    create_command_app,
    add_help_callback,
    create_progress_bar,
    handle_generic_error,
)

# Create the command app
app = create_command_app(
    name="init", help_text="Initialize a new project with coding standards"
)
add_help_callback(app)


@app.command()
def project(
    language: str = typer.Option(
        ..., "--language", "-l", help="Programming language for the project"
    ),
    name: str = typer.Option(..., "--name", "-n", help="Project name"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Project path (defaults to current directory)"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Template to use"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force overwrite existing files"
    ),
):
    """Initialize a new project with coding standards."""
    try:
        if path is None:
            path = Path.cwd() / name
        else:
            path = path / name

        if path.exists() and not force:
            if not typer.confirm(f"Directory {path} already exists. Overwrite?"):
                raise typer.Abort()

        with create_progress_bar("Initializing project...") as progress:
            task = progress.add_task("Initializing project...", total=None)

            generator = ProjectGenerator()
            success = generator.create_project(
                path=path, language=language, template=template, force=force
            )

            if success:
                progress.update(task, description="Project created successfully!")
                rprint(
                    f"\n✅ Project '{name}' initialized with {language} standards at {path}"
                )
                rprint(f"\nNext steps:")
                rprint(f"  cd {path}")
                rprint(f"  git init")
                rprint(f"  scs validate")
            else:
                progress.update(task, description="Failed to create project")
                raise typer.Exit(1)

    except Exception as e:
        handle_generic_error(e, "init")
