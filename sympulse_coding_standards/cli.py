"""Command-line interface for Sympulse Coding Standards."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from .core import StandardsManager, ValidationResult
from .generators import ProjectGenerator

app = typer.Typer(
    name="scs",
    help="Sympulse Coding Standards - Manage coding standards across projects",
    add_completion=False,
)

console = Console()


@app.command()
def init(
    language: str = typer.Option(
        ..., "--language", "-l", help="Programming language for the project"
    ),
    name: str = typer.Option(..., "--name", "-n", help="Project name"),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Project path (defaults to current directory)"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Template to use"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force overwrite existing files"
    ),
):
    """Initialize a new project with coding standards."""
    try:
        if path is None:
            path = Path.cwd() / name
        else:
            path = path / name

        if path.exists() and not force:
            if not typer.confirm(f"Directory {path} already exists. Overwrite?"):
                raise typer.Abort()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing project...", total=None)

            generator = ProjectGenerator()
            success = generator.create_project(
                path=path, language=language, template=template, force=force
            )

            if success:
                progress.update(task, description="Project created successfully!")
                rprint(
                    f"\n✅ Project '{name}' initialized with {language} standards at {path}"
                )
                rprint(f"\nNext steps:")
                rprint(f"  cd {path}")
                rprint(f"  git init")
                rprint(f"  scs validate")
            else:
                progress.update(task, description="Failed to create project")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    path: Path = typer.Argument(Path.cwd(), help="Project path to validate"),
    strict: bool = typer.Option(
        False, "--strict", "-s", help="Enable strict validation"
    ),
    output: str = typer.Option(
        "text", "--output", "-o", help="Output format (text, json, html)"
    ),
):
    """Validate a project against coding standards."""
    try:
        if not path.exists():
            console.print(f"[red]Error: Path {path} does not exist[/red]")
            raise typer.Exit(1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validating project...", total=None)

            manager = StandardsManager()
            result = manager.validate_project(path)

            progress.update(task, description="Validation complete!")

        # Display results
        _display_validation_result(result, output)

        if not result.is_compliant and strict:
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def update(
    path: Path = typer.Argument(Path.cwd(), help="Project path to update"),
    language: Optional[str] = typer.Option(
        None, "--language", "-l", help="Specific language to update"
    ),
    version: Optional[str] = typer.Option(
        None, "--version", "-v", help="Standards version to update to"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force update even if conflicts exist"
    ),
):
    """Update project standards to latest version."""
    try:
        if not path.exists():
            console.print(f"[red]Error: Path {path} does not exist[/red]")
            raise typer.Exit(1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Updating standards...", total=None)

            manager = StandardsManager()
            success = manager.update_project_standards(
                project_path=path, language=language, version=version
            )

            if success:
                progress.update(task, description="Standards updated successfully!")
                rprint(f"\n✅ Standards updated for project at {path}")
            else:
                progress.update(task, description="Failed to update standards")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def audit(
    path: Path = typer.Argument(Path.cwd(), help="Project path to audit"),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed audit report"
    ),
):
    """Audit project compliance with coding standards."""
    try:
        if not path.exists():
            console.print(f"[red]Error: Path {path} does not exist[/red]")
            raise typer.Exit(1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Auditing project...", total=None)

            manager = StandardsManager()
            result = manager.validate_project(path)

            progress.update(task, description="Audit complete!")

        # Display audit results
        _display_audit_result(result, detailed)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_standards():
    """List available coding standards."""
    try:
        manager = StandardsManager()
        standards = manager.get_available_standards()

        if not standards:
            console.print("[yellow]No standards found[/yellow]")
            return

        table = Table(title="Available Coding Standards")
        table.add_column("Language", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Description", style="white")
        table.add_column("Last Updated", style="yellow")
        table.add_column("Maintainer", style="blue")

        for standard in standards:
            table.add_row(
                standard.name,
                standard.version,
                standard.description,
                standard.last_updated,
                standard.maintainer,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def show_standard(
    standard_name: str = typer.Argument(..., help="Name of the standard to show"),
):
    """Show details of a specific coding standard."""
    try:
        manager = StandardsManager()
        standard = manager.get_standard(standard_name)

        # Display standard details
        console.print(
            Panel.fit(
                f"[bold cyan]{standard_name.upper()} Standards[/bold cyan]\n"
                f"[green]Version:[/green] {standard.get('version', 'N/A')}\n"
                f"[green]Formatters:[/green] {', '.join(standard.get('formatters', []))}\n"
                f"[green]Linters:[/green] {', '.join(standard.get('linters', []))}\n"
                f"[green]Test Frameworks:[/green] {', '.join(standard.get('test_frameworks', []))}",
                title="Standard Details",
            )
        )

        # Show rules if available
        if "rules" in standard:
            rules = standard["rules"]
            console.print("\n[bold]Rules:[/bold]")

            if "file_structure" in rules:
                console.print(
                    f"  [cyan]File Structure:[/cyan] {rules['file_structure']}"
                )

            if "naming" in rules:
                console.print(f"  [cyan]Naming Conventions:[/cyan] {rules['naming']}")

            if "formatting" in rules:
                console.print(f"  [cyan]Formatting:[/cyan] {rules['formatting']}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _display_validation_result(result: ValidationResult, output: str):
    """Display validation results in the specified format."""
    if output == "json":
        import json

        console.print(
            json.dumps(
                {
                    "is_compliant": result.is_compliant,
                    "score": result.score,
                    "violations": result.violations,
                    "warnings": result.warnings,
                    "suggestions": result.suggestions,
                },
                indent=2,
            )
        )
        return

    # Text output
    if result.is_compliant:
        console.print(f"\n[green]✅ Project is compliant with standards![/green]")
        console.print(f"[green]Compliance Score: {result.score:.1f}%[/green]")
    else:
        console.print(f"\n[red]❌ Project has compliance issues[/red]")
        console.print(f"[red]Compliance Score: {result.score:.1f}%[/red]")

    if result.violations:
        console.print(f"\n[red]Violations ({len(result.violations)}):[/red]")
        for violation in result.violations:
            console.print(f"  ❌ {violation}")

    if result.warnings:
        console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/yellow]")
        for warning in result.warnings:
            console.print(f"  ⚠️  {warning}")

    if result.suggestions:
        console.print(f"\n[blue]Suggestions ({len(result.suggestions)}):[/blue]")
        for suggestion in result.suggestions:
            console.print(f"  💡 {suggestion}")


def _display_audit_result(result: ValidationResult, detailed: bool):
    """Display audit results."""
    # Create a summary panel
    status_color = "green" if result.is_compliant else "red"
    status_icon = "✅" if result.is_compliant else "❌"

    summary = f"{status_icon} Compliance Score: {result.score:.1f}%\n"
    summary += f"Violations: {len(result.violations)}\n"
    summary += f"Warnings: {len(result.warnings)}\n"
    summary += f"Suggestions: {len(result.suggestions)}"

    console.print(
        Panel.fit(
            summary,
            title=f"[bold {status_color}]Audit Summary[/bold {status_color}]",
            border_style=status_color,
        )
    )

    if detailed:
        _display_validation_result(result, "text")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
