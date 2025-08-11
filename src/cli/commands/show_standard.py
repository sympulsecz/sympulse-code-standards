"""Show details of a specific coding standard."""

import typer
from rich.panel import Panel

from ...core import StandardsManager
from .base import create_command_app, add_help_callback, handle_generic_error, console

# Create the command app
app = create_command_app(
    name="show-standard", help_text="Show details of a specific coding standard"
)
add_help_callback(app)


@app.command()
def standard(
    standard_name: str = typer.Argument(..., help="Name of the standard to show"),
):
    """Show details of a specific coding standard."""
    try:
        manager = StandardsManager()

        # Get all standards to find the one by name
        all_standards = manager.get_available_standards()
        standard = None

        for std in all_standards:
            if std.name.lower() == standard_name.lower():
                standard = std
                break

        if not standard:
            console.print(f"[red]Error: Standard '{standard_name}' not found[/red]")
            raise typer.Exit(1)

        # Display standard details
        _display_standard_details(standard)

    except Exception as e:
        handle_generic_error(e, "show-standard")


def _display_standard_details(standard):
    """Display detailed information about a standard."""
    # Basic information
    console.print(
        Panel.fit(
            f"[bold]Name:[/bold] {standard.name}\n"
            f"[bold]Version:[/bold] {standard.version}\n"
            f"[bold]Description:[/bold] {standard.description}\n"
            f"[bold]Languages:[/bold] {', '.join(standard.languages)}\n"
            f"[bold]Last Updated:[/bold] {standard.last_updated}\n"
            f"[bold]Maintainer:[/bold] {standard.maintainer}",
            title="Standard Details",
        )
    )

    # Try to get more detailed information
    try:
        manager = StandardsManager()

        # Get detailed standard info for each language
        for language in standard.languages:
            try:
                detailed_standard = manager.get_standard(language)
                _display_language_details(language, detailed_standard)
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Could not load details for {language}: {e}[/yellow]"
                )

    except Exception as e:
        console.print(
            f"[yellow]Warning: Could not load detailed information: {e}[/yellow]"
        )


def _display_language_details(language: str, standard_data: dict):
    """Display language-specific standard details."""
    console.print(f"\n[bold cyan]Language: {language}[/bold cyan]")

    # Show tools and frameworks
    if "tools" in standard_data:
        tools = standard_data["tools"]
        console.print(
            f"[green]Formatters:[/green] {', '.join(tools.get('formatters', []))}"
        )
        console.print(f"[green]Linters:[/green] {', '.join(tools.get('linters', []))}")
        console.print(
            f"[green]Type Checkers:[/green] {', '.join(tools.get('type_checkers', []))}"
        )
        console.print(
            f"[green]Test Frameworks:[/green] {', '.join(tools.get('test_frameworks', []))}"
        )

    # Show rules if available
    if "rules" in standard_data:
        rules = standard_data["rules"]
        console.print("\n[bold]Rules:[/bold]")

        if "file_structure" in rules:
            console.print(f"  [cyan]File Structure:[/cyan] {rules['file_structure']}")

        if "naming" in rules:
            console.print(f"  [cyan]Naming Conventions:[/cyan] {rules['naming']}")

        if "formatting" in rules:
            console.print(f"  [cyan]Formatting:[/cyan] {rules['formatting']}")
