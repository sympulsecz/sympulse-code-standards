"""Main CLI application for Sympulse Coding Standards."""

import typer
import src.cli.commands as commands


# Static command configurations to keep code DRY
COMMAND_CONFIGS = [
    {
        "command": commands.init_project,
        "name": "project-init",
        "help": "Initialize a new project with coding standards",
    },
    {
        "command": commands.validate_project,
        "name": "project-validate",
        "help": "Validate a project against coding standards",
    },
    {
        "command": commands.update_project,
        "name": "project-update",
        "help": "Update project standards to latest version",
    },
    {
        "command": commands.audit_project,
        "name": "project-audit",
        "help": "Audit project compliance with coding standards",
    },
    {
        "command": commands.list_standards,
        "name": "standards-list",
        "help": "List available coding standards",
    },
    {
        "command": commands.show_standards,
        "name": "standards-show",
        "help": "Show details of a specific coding standard",
    },
]

# Create the main Typer app
app = typer.Typer(
    name="scs",
    help="Sympulse Coding Standards - Manage coding standards across projects",
    add_completion=False,
    invoke_without_command=True,
)

# Add all commands directly to the main app
for config in COMMAND_CONFIGS:
    app.command(name=config["name"], help=config["help"])(config["command"])


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
