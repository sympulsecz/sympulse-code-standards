#!/usr/bin/env python3
"""Standalone script for updating versions across the project.

This script can be called programmatically from CI/CD pipelines or other automation tools.
It provides a non-interactive way to update versions without user confirmation.

Usage:
    python scripts/update_versions.py --python 3.14 --node 26 --project 0.3.0
    python scripts/update_versions.py --bump python minor
    python scripts/update_versions.py --validate
"""

import argparse
import sys
from pathlib import Path
from src.lib.version_manager import VersionManager

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))



def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Update versions across the Sympulse Code Standards project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update specific versions
  python scripts/update_versions.py --python 3.14 --node 26
  
  # Bump Python version by minor
  python scripts/update_versions.py --bump python minor
  
  # Validate current versions
  python scripts/update_versions.py --validate
  
  # Show current versions
  python scripts/update_versions.py --show
        """,
    )

    # Version update options
    parser.add_argument("--python", help="Update Python version (e.g., 3.14)")
    parser.add_argument("--node", help="Update Node.js version (e.g., 26)")
    parser.add_argument("--project", help="Update project version (e.g., 0.3.0)")

    # Bump options
    parser.add_argument(
        "--bump",
        nargs=2,
        metavar=("COMPONENT", "TYPE"),
        choices=[
            ("python", "patch"),
            ("python", "minor"),
            ("python", "major"),
            ("node", "patch"),
            ("node", "minor"),
            ("node", "major"),
            ("project", "patch"),
            ("project", "minor"),
            ("project", "major"),
        ],
        help="Bump version using semantic versioning",
    )

    # Other options
    parser.add_argument(
        "--validate", action="store_true", help="Validate version consistency"
    )
    parser.add_argument("--show", action="store_true", help="Show current versions")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress output except errors"
    )

    args = parser.parse_args()

    # Check if any action was specified
    if not any(
        [args.python, args.node, args.project, args.bump, args.validate, args.show]
    ):
        parser.print_help()
        sys.exit(1)

    try:
        manager = VersionManager()

        # Handle show command
        if args.show:
            if not args.quiet:
                manager.show_current_versions()
            return

        # Handle validate command
        if args.validate:
            errors = manager.validate_versions()
            if not errors:
                if not args.quiet:
                    print("✅ All versions are consistent")
                return 0
            else:
                print("❌ Version validation errors found:", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
                return 1

        # Handle bump command
        if args.bump:
            component, bump_type = args.bump
            current_version = manager.get_version(component)

            if not current_version:
                print(f"❌ No current version found for {component}", file=sys.stderr)
                return 1

            # Calculate new version based on bump type
            if component == "project":
                parts = current_version.split(".")
                if len(parts) != 3:
                    print(
                        f"❌ Invalid project version format: {current_version}",
                        file=sys.stderr,
                    )
                    return 1

                major, minor, patch = map(int, parts)

                if bump_type == "patch":
                    new_version = f"{major}.{minor}.{patch + 1}"
                elif bump_type == "minor":
                    new_version = f"{major}.{minor + 1}.0"
                else:  # major
                    new_version = f"{major + 1}.0.0"

            elif component == "python":
                parts = current_version.split(".")
                if len(parts) != 2:
                    print(
                        f"❌ Invalid Python version format: {current_version}",
                        file=sys.stderr,
                    )
                    return 1

                major, minor = map(int, parts)

                if bump_type == "patch":
                    new_version = f"{major}.{minor + 1}"
                elif bump_type == "minor":
                    new_version = f"{major + 1}.0"
                else:  # major
                    new_version = f"{major + 1}.0"

            elif component == "node":
                try:
                    version_num = int(current_version)
                    if bump_type == "patch":
                        new_version = str(version_num + 1)
                    elif bump_type == "minor":
                        new_version = str(version_num + 2)
                    else:  # major
                        new_version = str(version_num + 6)  # LTS cycle
                except ValueError:
                    print(
                        f"❌ Invalid Node.js version format: {current_version}",
                        file=sys.stderr,
                    )
                    return 1

            if args.dry_run:
                if not args.quiet:
                    print(
                        f"Would bump {component} from {current_version} to {new_version}"
                    )
                return 0

            # Perform the update
            if component == "python":
                manager.update_python_version(new_version)
            elif component == "node":
                manager.update_node_version(new_version)
            elif component == "project":
                manager.update_project_version(new_version)

            if not args.quiet:
                print(f"✅ {component} version bumped to {new_version}")
            return 0

        # Handle direct version updates
        updates = {}
        if args.python:
            updates["python"] = args.python
        if args.node:
            updates["node"] = args.node
        if args.project:
            updates["project"] = args.project

        if updates:
            if args.dry_run:
                if not args.quiet:
                    print("Would update:")
                    for key, value in updates.items():
                        current = manager.get_version(key)
                        print(f"  {key}: {current} → {value}")
                return 0

            # Perform updates
            manager.update_all_versions(**updates)

            if not args.quiet:
                print("✅ All versions updated successfully")
            return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
