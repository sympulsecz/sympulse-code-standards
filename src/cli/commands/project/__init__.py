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
        self.app.command(
            name="init", help="Initialize a new project with coding standards"
        )(init_project)

        self.app.command(
            name="validate", help="Validate a project against coding standards"
        )(validate_project)

        self.app.command(
            name="update", help="Update project standards to latest version"
        )(update_project)

        self.app.command(
            name="audit", help="Audit project compliance with coding standards"
        )(audit_project)


# Create the project command group instance
project_group = ProjectCommandGroup()

__all__ = ["project_group", "ProjectCommandGroup"]
