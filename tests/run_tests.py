#!/usr/bin/env python3
"""Test runner script for the project init command tests."""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests for the project init command."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent

    print("🧪 Running tests for project init command...")
    print(f"📁 Project root: {project_root}")
    print()

    # Run unit tests
    print("🔬 Running unit tests...")
    unit_result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
        cwd=project_root,
    )

    print()

    # Run integration tests
    print("🔗 Running integration tests...")
    integration_result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration/", "-v", "--tb=short"],
        cwd=project_root,
    )

    print()

    # Summary
    print("📊 Test Results Summary:")
    print(
        f"   Unit tests: {'✅ PASSED' if unit_result.returncode == 0 else '❌ FAILED'}"
    )
    print(
        f"   Integration tests: {'✅ PASSED' if integration_result.returncode == 0 else '❌ FAILED'}"
    )

    if unit_result.returncode == 0 and integration_result.returncode == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
