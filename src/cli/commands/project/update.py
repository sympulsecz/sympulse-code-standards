"""Update project standards to latest version."""

from pathlib import Path
from typing import Optional

import typer

from src.core import StandardsManager
from src.cli.commands.base import (
    create_progress_bar,
    handle_path_validation,
    handle_generic_error,
    console,
)


def update_project(
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
        handle_path_validation(path, "update")

        with create_progress_bar("Updating project standards...") as progress:
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
        handle_generic_error(e, "update")
