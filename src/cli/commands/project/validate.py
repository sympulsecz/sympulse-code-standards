"""Validate a project against coding standards."""

from pathlib import Path

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
@click.option("--strict", "-s", is_flag=True, help="Enable strict validation")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json", "html"]),
    default="text",
    help="Output format (text, json, html)",
)
def validate_project(
    path: Path,
    strict: bool,
    output: str,
):
    """Validate a project against coding standards."""
    try:
        handle_path_validation(path, "validate")

        with create_progress_bar("Validating project...") as progress:
            task = progress.add_task("Validating project...", total=None)

            manager = StandardsManager()
            result = manager.validate_project(path)

            progress.update(task, description="Validation complete!")

        # Display results
        _display_validation_result(result, output)

        if not result.is_compliant and strict:
            raise click.Abort()

    except Exception as e:
        handle_generic_error(e, "validate")


def _display_validation_result(result, output: str):
    """Display validation results in the specified format."""
    if output == "json":
        import json

        console.print(
            json.dumps(
                {
                    "is_compliant": result.is_compliant,
                    "score": result.score,
                    "violations": result.violations,
                    "warnings": result.warnings,
                    "suggestions": result.suggestions,
                },
                indent=2,
            )
        )
        return

    # Text output
    if result.is_compliant:
        console.print(f"\n[green]✅ Project is compliant with standards![/green]")
        console.print(f"[green]Compliance Score: {result.score:.1f}%[/green]")
    else:
        console.print(f"\n[red]❌ Project has compliance issues[/red]")
        console.print(f"[red]Compliance Score: {result.score:.1f}%[/red]")

    if result.violations:
        console.print(f"\n[red]Violations ({len(result.violations)}):[/red]")
        for violation in result.violations:
            console.print(f"  ❌ {violation}")

    if result.warnings:
        console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/yellow]")
        for warning in result.warnings:
            console.print(f"  ⚠️  {warning}")

    if result.suggestions:
        console.print(f"\n[blue]Suggestions ({len(result.suggestions)}):[/blue]")
        for suggestion in result.suggestions:
            console.print(f"  💡 {suggestion}")
