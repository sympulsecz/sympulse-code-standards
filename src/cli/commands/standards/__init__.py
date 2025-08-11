"""Standards command group for Sympulse Coding Standards."""

from src.cli.commands.base import CommandGroup
from .list import list_standards
from .show import show_standards


class StandardsCommandGroup(CommandGroup):
    """Command group for standards-related commands."""

    def __init__(self):
        super().__init__(
            name="standards", help_text="Manage and explore coding standards"
        )

    def register_commands(self):
        """Register all standards subcommands."""
        self.group.add_command(list_standards, name="list")
        self.group.add_command(show_standards, name="show")


# Create the standards command group instance
standards_group = StandardsCommandGroup()

__all__ = ["standards_group", "StandardsCommandGroup"]
