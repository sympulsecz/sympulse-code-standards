"""List available coding standards."""

import typer
from rich.console import Console
from rich.table import Table

from ...core import StandardsManager

app = typer.Typer(
    name="list-standards",
    help="List available coding standards",
    add_completion=False,
)

console = Console()


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
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
