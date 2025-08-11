"""Initialize a new project with coding standards."""

from pathlib import Path
from typing import Optional

import click
from rich import print as rprint

from src.generators import ProjectGenerator
from src.cli.commands.base import (
    create_progress_bar,
    handle_generic_error,
)


@click.command()
@click.option(
    "--language", "-l", required=True, help="Programming language for the project"
)
@click.option("--name", "-n", required=True, help="Project name")
@click.option(
    "--path",
    "-p",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    help="Project path (defaults to current directory)",
)
@click.option("--template", "-t", help="Template to use")
@click.option("--force", "-f", is_flag=True, help="Force overwrite existing files")
def init_project(
    language: str,
    name: str,
    path: Optional[Path],
    template: Optional[str],
    force: bool,
):
    """Initialize a new project with coding standards."""
    try:
        if path is None:
            path = Path.cwd() / name
        else:
            path = path / name

        if path.exists() and not force:
            if not click.confirm(f"Directory {path} already exists. Overwrite?"):
                raise click.Abort()

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
                raise click.Abort()

    except Exception as e:
        handle_generic_error(e, "init")
