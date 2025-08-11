"""Admin commands for Sympulse Code Standards."""

from src.cli.commands.base import NestedCommandGroup
from .versions import versions_group


class AdminCommandGroup(NestedCommandGroup):
    """Command group for admin-related commands."""

    def __init__(self):
        super().__init__(name="admin", help_text="Administrative commands")

    def register_commands(self):
        """Register all admin subcommands."""
        self.add_command(
            versions_group,
            name="versions",
            help_text="Manage versions across the project",
        )


admin_group = AdminCommandGroup()

__all__ = ["admin_group", "AdminCommandGroup"]
