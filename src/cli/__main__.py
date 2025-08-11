"""Main CLI application for Sympulse Coding Standards."""

import click
from src.cli.commands import project_group, standards_group, tools_group
from src.cli.commands.base import CommandRegistry


def create_main_app() -> click.Group:
    """Create the main CLI application with command groups."""
    app = click.Group(
        name="scs",
        help="Sympulse Coding Standards - Manage coding standards across projects",
    )

    # Register command groups
    registry = CommandRegistry()
    registry.register_group(project_group)
    registry.register_group(standards_group)
    registry.register_group(tools_group)

    # Add command groups to main app
    for group_name, group in registry.get_all_groups().items():
        app.add_command(group.get_group(), name=group_name)

    return app


# Create the main app
app = create_main_app()


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
