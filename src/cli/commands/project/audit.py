"""Audit project compliance with coding standards."""

from pathlib import Path

import typer
from rich.panel import Panel

from src.core import StandardsManager
from src.cli.commands.base import (
    create_progress_bar,
    handle_path_validation,
    handle_generic_error,
    console,
)


def audit_project(
    path: Path = typer.Argument(Path.cwd(), help="Project path to audit"),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed audit report"
    ),
):
    """Audit project compliance with coding standards."""
    try:
        handle_path_validation(path, "audit")

        with create_progress_bar("Auditing project...") as progress:
            task = progress.add_task("Auditing project...", total=None)

            manager = StandardsManager()
            result = manager.validate_project(path)

            progress.update(task, description="Audit complete!")

        # Display audit results
        _display_audit_result(result, detailed)

    except Exception as e:
        handle_generic_error(e, "audit")


def _display_audit_result(result, detailed: bool):
    """Display audit results."""
    # Create a summary panel
    status_color = "green" if result.is_compliant else "red"
    status_icon = "✅" if result.is_compliant else "❌"

    summary = f"{status_icon} Compliance Score: {result.score:.1f}%\n"
    summary += f"Violations: {len(result.violations)}\n"
    summary += f"Warnings: {len(result.warnings)}\n"
    summary += f"Suggestions: {len(result.suggestions)}"

    console.print(
        Panel.fit(
            summary,
            title=f"[bold {status_color}]Audit Summary[/bold {status_color}]",
            border_style=status_color,
        )
    )

    if detailed:
        _display_detailed_results(result)


def _display_detailed_results(result):
    """Display detailed validation results."""
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
