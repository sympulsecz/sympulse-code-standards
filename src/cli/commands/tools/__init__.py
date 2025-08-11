"""Tools command group for Sympulse Coding Standards."""

from src.cli.commands.base import CommandGroup
from .format_code import format_code
from .lint_code import lint_code


class ToolsCommandGroup(CommandGroup):
    """Command group for development tools and utilities."""

    def __init__(self):
        super().__init__(name="tools", help_text="Development tools and utilities")

    def register_commands(self):
        """Register all tools subcommands."""
        self.group.add_command(format_code, name="format")
        self.group.add_command(lint_code, name="lint")


# Create the tools command group instance
tools_group = ToolsCommandGroup()

__all__ = ["tools_group", "ToolsCommandGroup"]
