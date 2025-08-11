"""Main CLI application for Sympulse Coding Standards."""

import typer

from .commands import (
    init_app,
    validate_app,
    update_app,
    audit_app,
    list_standards_app,
    show_standard_app,
)

# Create the main Typer app
app = typer.Typer(
    name="scs",
    help="Sympulse Coding Standards - Manage coding standards across projects",
    add_completion=False,
    invoke_without_command=True,
)

# Add all command groups
app.add_typer(
    init_app, name="init", help="Initialize a new project with coding standards"
)
app.add_typer(
    validate_app, name="validate", help="Validate a project against coding standards"
)
app.add_typer(
    update_app, name="update", help="Update project standards to latest version"
)
app.add_typer(
    audit_app, name="audit", help="Audit project compliance with coding standards"
)
app.add_typer(
    list_standards_app, name="list-standards", help="List available coding standards"
)
app.add_typer(
    show_standard_app,
    name="show-standard",
    help="Show details of a specific coding standard",
)


# Main callback for when no command is provided
@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Main callback that shows help when no command is provided."""
    if ctx.invoked_subcommand is None:
        # No subcommand was invoked, show help and exit cleanly
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
