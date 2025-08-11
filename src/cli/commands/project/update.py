"""Update project standards to latest version."""

from pathlib import Path
from typing import Optional

import click

from src.core import StandardsManager
from src.cli.commands.base import (
    create_progress_bar,
    handle_path_validation,
    handle_generic_error,
    console,
)


@click.command()
@click.argument(
    "path",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    default=Path.cwd(),
)
@click.option("--language", "-l", help="Specific language to update")
@click.option("--version", "-v", help="Standards version to update to")
@click.option(
    "--force", "-f", is_flag=True, help="Force update even if conflicts exist"
)
def update_project(
    path: Path,
    language: Optional[str],
    version: Optional[str],
    force: bool,
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
                raise click.Abort()

    except Exception as e:
        handle_generic_error(e, "update")
