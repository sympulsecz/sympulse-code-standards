"""Base classes and utilities for CLI commands."""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from typing import Optional, Any, Callable

console = Console()


def create_command_app(
    name: str,
    help_text: str,
    add_completion: bool = False,
    invoke_without_command: bool = True,
    no_args_is_help: bool = False,
) -> typer.Typer:
    """Create a command app with common configuration."""
    return typer.Typer(
        name=name,
        help=help_text,
        add_completion=add_completion,
        invoke_without_command=invoke_without_command,
        no_args_is_help=no_args_is_help,
    )


def add_help_callback(app: typer.Typer) -> None:
    """Add a help callback that shows help when no subcommand is provided."""

    @app.callback(invoke_without_command=True)
    def help_callback(ctx: typer.Context):
        """Main callback that shows help when no subcommand is provided."""
        if ctx.invoked_subcommand is None:
            # No subcommand was invoked, show help and exit cleanly
            typer.echo(ctx.get_help())
            raise typer.Exit(0)


def create_command_with_main_function(
    name: str,
    help_text: str,
    main_function: callable,
    add_completion: bool = False,
) -> typer.Typer:
    """Create a command app that directly uses the main function as the command."""
    # Create a simple Typer app without subcommands
    app = typer.Typer(
        name=name,
        help=help_text,
        add_completion=add_completion,
        no_args_is_help=True,
    )

    # Add the main function directly as the command
    app.command()(main_function)

    return app


def create_direct_command(
    name: str,
    help_text: str,
    main_function: callable,
) -> callable:
    """Create a command function that can be added directly to the main app."""
    return main_function


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
        raise typer.Exit(1)


def handle_generic_error(error: Exception, command_name: str) -> None:
    """Handle common error handling logic."""
    console.print(f"[red]Error in {command_name}: {error}[/red]")
    raise typer.Exit(1)


class BaseCommand:
    """Base class for command implementations."""

    def __init__(self, name: str, help_text: str):
        self.name = name
        self.help_text = help_text
        self.app = create_command_app(name, help_text)
        add_help_callback(self.app)

    def add_command(self, func: Callable, **kwargs) -> None:
        """Add a command to the app."""
        self.app.command(**kwargs)(func)

    def get_app(self) -> typer.Typer:
        """Get the Typer app instance."""
        return self.app
