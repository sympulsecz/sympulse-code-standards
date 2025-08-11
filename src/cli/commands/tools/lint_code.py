import typer


def lint_code(
    path: str = typer.Argument(".", help="Path to lint (file or directory)"),
    strict: bool = typer.Option(
        False, "--strict", "-s", help="Enable strict linting rules"
    ),
):
    """Lint code according to coding standards."""
    typer.echo(f"Linting code at {path}")
    if strict:
        typer.echo("Using strict linting rules")
    # Implementation would go here
    typer.echo("Linting completed!")
