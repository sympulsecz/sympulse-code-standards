"""Admin command for managing versions across the project."""

import click
from typing import Optional

from src.lib.version_manager import VersionManager


@click.group(name="versions")
@click.pass_context
def versions_group(ctx: click.Context) -> None:
    """Manage versions across the project.

    This command group is for repository administrators and maintainers.
    Use with caution as it modifies multiple files across the project.
    """
    pass


@versions_group.command(name="show")
@click.pass_context
def show_versions(ctx: click.Context) -> None:
    """Show current versions across the project."""
    try:
        manager = VersionManager()
        manager.show_current_versions()
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        ctx.exit(1)


@versions_group.command(name="update")
@click.option("--python", help="Update Python version (e.g., 3.14)")
@click.option("--node", help="Update Node.js version (e.g., 26)")
@click.option("--project", help="Update project version (e.g., 0.3.0)")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be changed without making changes"
)
@click.pass_context
def update_versions(
    ctx: click.Context,
    python: Optional[str],
    node: Optional[str],
    project: Optional[str],
    dry_run: bool,
) -> None:
    """Update versions across the project.

    This command updates versions in multiple files. Use with caution.
    """
    if not any([python, node, project]):
        click.echo("❌ Please specify at least one version to update")
        click.echo("Use --help for usage information")
        ctx.exit(1)

    try:
        manager = VersionManager()

        if dry_run:
            click.echo("🔍 DRY RUN MODE - No changes will be made")
            click.echo("Current versions:")
            manager.show_current_versions()
            click.echo("\nWould update:")
            if python:
                click.echo(f"  Python: {manager.get_version('python')} → {python}")
            if node:
                click.echo(f"  Node.js: {manager.get_version('node')} → {node}")
            if project:
                click.echo(f"  Project: {manager.get_version('project')} → {project}")
        else:
            # Confirm the action
            click.echo(
                "⚠️  WARNING: This will modify multiple files across the project!"
            )
            if not click.confirm("Are you sure you want to continue?"):
                click.echo("Operation cancelled")
                return

            # Perform updates
            updates = {}
            if python:
                updates["python"] = python
            if node:
                updates["node"] = node
            if project:
                updates["project"] = project

            manager.update_all_versions(**updates)

            click.echo("\n✅ Version updates completed!")
            click.echo("Please review the changes and commit them to version control.")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        ctx.exit(1)


@versions_group.command(name="validate")
@click.pass_context
def validate_versions(ctx: click.Context) -> None:
    """Validate version consistency across the project."""
    try:
        manager = VersionManager()
        errors = manager.validate_versions()

        if not errors:
            click.echo("✅ All versions are consistent")
        else:
            click.echo("❌ Version validation errors found:")
            for error in errors:
                click.echo(f"  - {error}")
            ctx.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        ctx.exit(1)


@versions_group.command(name="bump")
@click.argument("component", type=click.Choice(["python", "node", "project"]))
@click.argument("bump_type", type=click.Choice(["patch", "minor", "major"]))
@click.option(
    "--dry-run", is_flag=True, help="Show what would be changed without making changes"
)
@click.pass_context
def bump_version(
    ctx: click.Context, component: str, bump_type: str, dry_run: bool
) -> None:
    """Bump a version using semantic versioning.

    COMPONENT: Which component to bump (python, node, project)
    BUMP_TYPE: Type of bump (patch, minor, major)
    """
    try:
        manager = VersionManager()
        current_version = manager.get_version(component)

        if not current_version:
            click.echo(f"❌ No current version found for {component}")
            ctx.exit(1)

        # Parse current version
        if component == "project":
            # Semantic versioning for project
            parts = current_version.split(".")
            if len(parts) != 3:
                click.echo(f"❌ Invalid project version format: {current_version}")
                ctx.exit(1)

            major, minor, patch = map(int, parts)

            if bump_type == "patch":
                new_version = f"{major}.{minor}.{patch + 1}"
            elif bump_type == "minor":
                new_version = f"{major}.{minor + 1}.0"
            else:  # major
                new_version = f"{major + 1}.0.0"

        elif component == "python":
            # Python version
               if len(parts) != 2:
                click.echo(f"❌ Invalid Python version format: {current_version}")
                ctx.exit(1)

            major, minor = map(int, parts)

            if bump_type == "patch":
                new_version = f"{major}.{minor + 1}"
            elif bump_type == "minor":
                new_version = f"{major + 1}.0"
            else:  # major
                new_version = f"{major + 1}.0"

        elif component == "node":
            # Node.js version (e.g., "24")
            try:
                version_num = int(current_version)
                if bump_type == "patch":
                    new_version = str(version_num + 1)
                elif bump_type == "minor":
                    new_version = str(version_num + 2)
                else:  # major
                    new_version = str(version_num + 6)  # LTS cycle
            except ValueError:
                click.echo(f"❌ Invalid Node.js version format: {current_version}")
                ctx.exit(1)

        if dry_run:
            click.echo(f"🔍 DRY RUN MODE - No changes will be made")
            click.echo(
                f"Would bump {component} from {current_version} to {new_version}"
            )
        else:
            # Confirm the action
            click.echo(
                f"⚠️  WARNING: This will bump {component} from {current_version} to {new_version}"
            )
            if not click.confirm("Are you sure you want to continue?"):
                click.echo("Operation cancelled")
                return

            # Perform the update
            if component == "python":
                manager.update_python_version(new_version)
            elif component == "node":
                manager.update_node_version(new_version)
            elif component == "project":
                manager.update_project_version(new_version)

            click.echo(f"✅ {component} version bumped to {new_version}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        ctx.exit(1)
