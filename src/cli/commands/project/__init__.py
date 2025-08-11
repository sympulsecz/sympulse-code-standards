"""Project command group for Sympulse Coding Standards."""

from src.cli.commands.base import NestedCommandGroup
from .audit import audit_project
from .init import init_project
from .update import update_project
from .validate import validate_project


class ProjectCommandGroup(NestedCommandGroup):
    """Command group for project-related commands."""

    def __init__(self):
        super().__init__(name="project", help_text="Manage project coding standards")

    def register_commands(self):
        """Register all project subcommands."""

        self.add_command(
            init_project,
            name="init",
            help_text="Initialize a new project with coding standards",
        )

        self.add_command(
            validate_project,
            name="validate",
            help_text="Validate a project against coding standards",
        )

        self.add_command(
            update_project,
            name="update",
            help_text="Update project standards to latest version",
        )

        self.add_command(
            audit_project,
            name="audit",
            help_text="Audit project compliance with coding standards",
        )


# Create the project command group instance
project_group = ProjectCommandGroup()

__all__ = ["project_group", "ProjectCommandGroup"]
