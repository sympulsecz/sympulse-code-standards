import click


@click.command()
@click.argument("path", default=".")
@click.option("--strict", "-s", is_flag=True, help="Enable strict linting rules")
def lint_code(
    path: str,
    strict: bool,
):
    """Lint code according to coding standards."""
    click.echo(f"Linting code at {path}")
    if strict:
        click.echo("Using strict linting rules")
    # Implementation would go here
    click.echo("Linting completed!")
