"""Initialize a new project with coding standards."""

from pathlib import Path
from typing import Optional

import click
from rich import print as rprint

from src.generators import ProjectGenerator
from src.cli.prompts import ProjectConfigurator
from src.cli.commands.base import (
    create_progress_bar,
    handle_generic_error,
)


@click.command()
@click.option(
    "--language",
    "-l",
    help="Programming language for the project (will prompt if not provided)",
)
@click.option("--name", "-n", help="Project name (will prompt if not provided)")
@click.option(
    "--path",
    "-p",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    help="Project path (defaults to current directory)",
)
@click.option("--template", "-t", help="Template to use")
@click.option("--force", "-f", is_flag=True, help="Force overwrite existing files")
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    default=True,
    help="Use interactive configuration (default: True)",
)
@click.option("--non-interactive", is_flag=True, help="Skip interactive configuration")
def init_project(
    language: Optional[str],
    name: Optional[str],
    path: Optional[Path],
    template: Optional[str],
    force: bool,
    interactive: bool,
    non_interactive: bool,
):
    """Initialize a new project with coding standards."""
    try:
        # Determine if we should use interactive mode
        use_interactive = interactive and not non_interactive

        # Get project configuration
        config = {}
        if use_interactive:
            configurator = ProjectConfigurator()
            # If name or language are not provided, they will be prompted for in the interactive flow
            config = configurator.configure_project(language, name)
            # Get the name and language from the configuration (either provided or selected interactively)
            name = config.get("name", name)
            language = config.get("language", language)
        else:
            # Use default configuration for non-interactive mode
            # Both name and language must be provided for non-interactive mode
            if not name:
                raise click.UsageError(
                    "Project name must be specified when using --non-interactive mode"
                )
            if not language:
                raise click.UsageError(
                    "Language must be specified when using --non-interactive mode"
                )

            config = {
                "name": name,
                "language": language,
                "description": f"A {name} project with coding standards",
                "author": "Your Name",
                "email": "your.email@example.com",
                "license": "MIT",
                "git_enabled": True,
                "contributing_enabled": True,
                "code_of_conduct_enabled": True,
                "issue_templates_enabled": True,
                "pr_templates_enabled": True,
                "git_commit_template": True,
                "ci_cd_enabled": False,
                "documentation_enabled": False,
                "security_enabled": False,
                "contributing": {
                    "branch_strategy": "github-flow",
                    "conventional_commits": True,
                    "pr_required": True,
                    "review_required": True,
                    "reviewers_count": 1,
                    "issue_template_enabled": True,
                    "cla_required": False,
                },
                "code_quality": {
                    "pre_commit_enabled": True,
                    "testing_enabled": True,
                    "coverage_enabled": True,
                    "coverage_threshold": 80,
                },
            }

        # Ensure we have both name and language
        if not name:
            raise click.UsageError(
                "Project name must be specified or selected interactively"
            )
        if not language:
            raise click.UsageError(
                "Language must be specified or selected interactively"
            )

        # Set up project path
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
                path=path,
                language=language,
                template=template,
                force=force,
                config=config,
            )

            if success:
                progress.update(task, description="Project created successfully!")
                rprint(
                    f"\n✅ Project '{name}' initialized with {language} standards at {path}"
                )

                # Show what was created
                if config:
                    rprint(f"\n📋 Project Configuration:")
                    if config.get("description"):
                        rprint(f"  Description: {config['description']}")
                    if config.get("author"):
                        rprint(f"  Author: {config['author']}")
                    if config.get("license"):
                        rprint(f"  License: {config['license']}")

                    features = []
                    if config.get("contributing_enabled"):
                        features.append("Contributing Guidelines")
                    if config.get("code_of_conduct_enabled"):
                        features.append("Code of Conduct")
                    if config.get("issue_templates_enabled"):
                        features.append("Issue Templates")
                    if config.get("pr_templates_enabled"):
                        features.append("Pull Request Templates")
                    if config.get("git_commit_template"):
                        features.append("Conventional Commits")
                    if config.get("ci_cd_enabled"):
                        features.append("CI/CD Pipeline")
                    if config.get("documentation_enabled"):
                        features.append("Documentation")
                    if config.get("security_enabled"):
                        features.append("Security Features")

                    if features:
                        rprint(f"  Features: {', '.join(features)}")

                rprint(f"\n🚀 Next steps:")
                rprint(f"  cd {path}")
                if config.get("git_enabled", True):
                    rprint(f"  git status")
                rprint(f"  scs project validate")

                if config.get("contributing_enabled"):
                    rprint(
                        f"\n📖 Review the generated CONTRIBUTING.md for contribution guidelines"
                    )

                if config.get("code_of_conduct_enabled"):
                    rprint(
                        f"📜 Review the generated CODE_OF_CONDUCT.md for community guidelines"
                    )

            else:
                progress.update(task, description="Failed to create project")
                raise click.Abort()

    except Exception as e:
        handle_generic_error(e, "init")
