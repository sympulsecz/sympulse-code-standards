"""List available coding standards."""

import typer
from rich.table import Table

from ...core import StandardsManager
from .base import create_command_app, add_help_callback, handle_generic_error, console

# Create the command app
app = create_command_app(
    name="list-standards", help_text="List available coding standards"
)
add_help_callback(app)


@app.command()
def standards():
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
