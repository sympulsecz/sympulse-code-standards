"""List available coding standards."""

import typer
from rich.table import Table

from src.core import StandardsManager
from src.cli.commands.base import (
    create_command_with_main_function,
    handle_generic_error,
    console,
)


def list_standards():
    """List available coding standards."""
    try:
        manager = StandardsManager()
        standards = manager.get_available_standards()

        if not standards:
            console.print("[yellow]No standards found.[/yellow]")
            return

        # Create table
        table = Table(title="Available Coding Standards")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", style="green")
        table.add_column("Languages", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Maintainer", style="blue")

        for standard in standards:
            languages_str = (
                ", ".join(standard.languages) if standard.languages else "N/A"
            )
            description = standard.description or "No description available"

            table.add_row(
                standard.name,
                standard.version,
                languages_str,
                description,
                standard.maintainer,
            )

        console.print(table)

    except Exception as e:
        handle_generic_error(e, "list-standards")
