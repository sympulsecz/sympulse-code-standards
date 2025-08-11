#!/usr/bin/env python3
"""Demo script showing how to use the version manager programmatically.

This script demonstrates the various ways you can use the VersionManager class
to update versions across the project.
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.lib.version_manager import VersionManager


def demo_basic_usage():
    """Demonstrate basic version manager usage."""
    print("🚀 Version Manager Demo - Basic Usage")
    print("=" * 50)

    try:
        # Initialize the version manager
        manager = VersionManager()

        # Show current versions
        print("\n📋 Current versions:")
        manager.show_current_versions()

        # Get specific versions
        python_version = manager.get_version("python")
        node_version = manager.get_version("node")
        project_version = manager.get_version("project")

        print(f"\n🔍 Current versions:")
        print(f"  Python: {python_version}")
        print(f"  Node.js: {node_version}")
        print(f"  Project: {project_version}")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_version_validation():
    """Demonstrate version validation."""
    print("\n\n🔍 Version Manager Demo - Validation")
    print("=" * 50)

    try:
        manager = VersionManager()

        # Validate current versions
        print("\n✅ Validating current versions...")
        errors = manager.validate_versions()

        if not errors:
            print("✅ All versions are consistent!")
        else:
            print("❌ Validation errors found:")
            for error in errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_dry_run_update():
    """Demonstrate dry-run update functionality."""
    print("\n\n🔍 Version Manager Demo - Dry Run Update")
    print("=" * 50)

    try:
        manager = VersionManager()

        # Show what would happen if we updated Python to 3.14
        print("\n🔍 What would happen if we updated Python to 3.14?")

        current_python = manager.get_version("python")
        print(f"  Current Python version: {current_python}")
        print(f"  Would update to: 3.14")

        # Calculate what the target version would be
        target_version = "py314"
        print(f"  Target version would be: {target_version}")

        print("\n📁 Files that would be updated:")
        python_configs = manager.versions["file_patterns"]["python_configs"]
        for file_path in python_configs:
            print(f"  - {file_path}")

        print("\n⚠️  This is just a demo - no actual changes were made")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_bump_calculation():
    """Demonstrate how version bumping works."""
    print("\n\n📈 Version Manager Demo - Bump Calculation")
    print("=" * 50)

    try:
        manager = VersionManager()

        current_project = manager.get_version("project")
        current_python = manager.get_version("python")
        current_node = manager.get_version("node")

        print(f"\n📋 Current versions:")
        print(f"  Project: {current_project}")
        print(f"  Python: {current_python}")
        print(f"  Node.js: {current_node}")

        print(f"\n📈 What would happen with different bump types?")

        # Project version bumps
        if current_project:
            parts = current_project.split(".")
            if len(parts) == 3:
                major, minor, patch = map(int, parts)
                print(f"\n  Project version bumps:")
                print(
                    f"    Patch: {major}.{minor}.{patch} → {major}.{minor}.{patch + 1}"
                )
                print(f"    Minor: {major}.{minor}.{patch} → {major}.{minor + 1}.0")
                print(f"    Major: {major}.{minor}.{patch} → {major + 1}.0.0")

        # Python version bumps
        if current_python:
            parts = current_python.split(".")
            if len(parts) == 2:
                major, minor = map(int, parts)
                print(f"\n  Python version bumps:")
                print(f"    Patch: {major}.{minor} → {major}.{minor + 1}")
                print(f"    Minor: {major}.{minor} → {major + 1}.0")

        # Node.js version bumps
        if current_node:
            try:
                version_num = int(current_node)
                print(f"\n  Node.js version bumps:")
                print(f"    Patch: {version_num} → {version_num + 1}")
                print(f"    Minor: {version_num} → {version_num + 2}")
                print(f"    Major: {version_num} → {version_num + 6} (LTS cycle)")
            except ValueError:
                pass

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all demos."""
    print("🎯 Sympulse Code Standards - Version Manager Demo")
    print("=" * 60)

    # Run all demos
    demo_basic_usage()
    demo_version_validation()
    demo_dry_run_update()
    demo_bump_calculation()

    print("\n\n🎉 Demo completed!")
    print("\n💡 To actually update versions, use:")
    print("  scs admin versions update --python 3.14")
    print("  scs admin versions bump python minor")
    print("  python scripts/update_versions.py --python 3.14")


if __name__ == "__main__":
    main()
