"""Base classes and utilities for CLI commands."""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from typing import Optional, Callable

from abc import ABC, abstractmethod

console = Console()


class CommandGroup(ABC):
    """Abstract base class for command groups."""

    def __init__(self, name: str, help_text: str):
        self.name = name
        self.help_text = help_text
        self.group = click.Group(
            name=name,
            help=help_text,
        )

    @abstractmethod
    def register_commands(self):
        """Register all commands for this group. Must be implemented by subclasses."""
        pass

    def get_group(self) -> click.Group:
        """Get the Click group instance."""
        return self.group


class NestedCommandGroup(CommandGroup):
    """Command group that can contain other command groups (nested subcommands)."""

    def __init__(self, name: str, help_text: str):
        super().__init__(name, help_text)
        self.subgroups: dict[str, CommandGroup] = {}

    def add_subgroup(self, subgroup: CommandGroup):
        """Add a subgroup to this command group."""
        self.subgroups[subgroup.name] = subgroup
        self.group.add_command(subgroup.get_group(), name=subgroup.name)

    def add_command(self, func: Callable, name: str, help_text: str = ""):
        """Add a direct command to this group."""
        # Check if the function is already a Click command
        if hasattr(func, "name") and hasattr(func, "callback"):
            # Function is already decorated, just add it directly
            self.group.add_command(func, name=name)
        else:
            # Create a Click command from the function
            cmd = click.command(name=name, help=help_text)(func)
            self.group.add_command(cmd)


class CommandRegistry:
    """Registry for managing command groups and their registration."""

    def __init__(self):
        self.groups: dict[str, CommandGroup] = {}

    def register_group(self, group: CommandGroup):
        """Register a command group."""
        self.groups[group.name] = group
        group.register_commands()

    def get_group(self, name: str) -> Optional[CommandGroup]:
        """Get a command group by name."""
        return self.groups.get(name)

    def get_all_groups(self) -> dict[str, CommandGroup]:
        """Get all registered command groups."""
        return self.groups.copy()

    def add_to_group(self, group_name: str, subgroup: CommandGroup):
        """Add a subgroup to an existing group."""
        if group_name in self.groups:
            group = self.groups[group_name]
            if isinstance(group, NestedCommandGroup):
                group.add_subgroup(subgroup)
            else:
                raise ValueError(f"Group {group_name} does not support subgroups")


def create_command_group(
    name: str,
    help_text: str,
) -> click.Group:
    """Create a command group with common configuration."""
    return click.Group(
        name=name,
        help=help_text,
    )


def create_progress_bar(description: str) -> Progress:
    """Create a progress bar with common configuration."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def handle_path_validation(path: Path, command_name: str) -> None:
    """Handle common path validation logic."""
    if not path.exists():
        console.print(f"[red]Error: Path {path} does not exist[/red]")
        raise click.Abort()


def handle_generic_error(error: Exception, command_name: str) -> None:
    """Handle common error handling logic."""
    console.print(f"[red]Error in {command_name}: {error}[/red]")
    raise click.Abort()


class BaseCommand:
    """Base class for command implementations."""

    def __init__(self, name: str, help_text: str):
        self.name = name
        self.help_text = help_text
        self.group = create_command_group(name, help_text)

    def add_command(self, func: Callable, **kwargs) -> None:
        """Add a command to the group."""
        cmd = click.command(**kwargs)(func)
        self.group.add_command(cmd)

    def get_group(self) -> click.Group:
        """Get the Click group instance."""
        return self.group
