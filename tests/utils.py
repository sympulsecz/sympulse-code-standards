"""Utility functions for testing."""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch


def create_mock_file(path: Path, content: str = "") -> None:
    """Create a mock file with given content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def create_mock_directory(path: Path) -> None:
    """Create a mock directory."""
    path.mkdir(parents=True, exist_ok=True)


def assert_file_exists(path: Path, expected_content: str = None) -> None:
    """Assert that a file exists and optionally check its content."""
    assert path.exists(), f"File {path} does not exist"
    if expected_content is not None:
        actual_content = path.read_text()
        assert actual_content == expected_content, f"File content mismatch for {path}"


def assert_directory_exists(path: Path) -> None:
    """Assert that a directory exists."""
    assert path.exists(), f"Directory {path} does not exist"
    assert path.is_dir(), f"Path {path} is not a directory"


def assert_file_contains(path: Path, expected_text: str) -> None:
    """Assert that a file contains expected text."""
    assert path.exists(), f"File {path} does not exist"
    content = path.read_text()
    assert (
        expected_text in content
    ), f"Expected text '{expected_text}' not found in {path}"


def create_mock_project_structure(base_path: Path, structure: Dict[str, Any]) -> None:
    """Create a mock project structure for testing."""
    for item, details in structure.items():
        item_path = base_path / item

        if isinstance(details, dict):
            # Directory with sub-items
            create_mock_directory(item_path)
            create_mock_project_structure(item_path, details)
        elif isinstance(details, str):
            # File with content
            create_mock_file(item_path, details)
        elif isinstance(details, list):
            # List of files or directories
            for sub_item in details:
                sub_path = item_path / sub_item
                if sub_item.endswith("/"):
                    create_mock_directory(sub_path)
                else:
                    create_mock_file(sub_path)


def mock_rich_prompts():
    """Context manager to mock all Rich prompts."""
    return patch.multiple(
        "src.cli.prompts",
        Prompt=Mock(),
        Confirm=Mock(),
        IntPrompt=Mock(),
        Console=Mock(),
        Panel=Mock(),
    )


def mock_rich_prompt_responses(**responses):
    """Create mock responses for Rich prompts."""
    mock_prompt = Mock()
    mock_confirm = Mock()
    mock_int_prompt = Mock()

    # Set up responses
    for key, value in responses.items():
        if key.startswith("prompt_"):
            mock_prompt.ask.return_value = value
        elif key.startswith("confirm_"):
            mock_confirm.ask.return_value = value
        elif key.startswith("int_"):
            mock_int_prompt.ask.return_value = value

    return {
        "Prompt": mock_prompt,
        "Confirm": mock_confirm,
        "IntPrompt": mock_int_prompt,
    }


def create_mock_template_config(
    name: str = "Test Template",
    description: str = "A test template",
    languages: List[str] = None,
    structure: Dict[str, Any] = None,
    dependencies: Dict[str, List[str]] = None,
    features: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Create a mock template configuration."""
    if languages is None:
        languages = ["python"]
    if structure is None:
        structure = {
            "directories": ["src", "tests"],
            "empty_files": ["src/__init__.py", "tests/__init__.py"],
        }
    if dependencies is None:
        dependencies = {"python": ["pytest", "black"]}
    if features is None:
        features = {
            "contributing_enabled": True,
            "code_of_conduct_enabled": True,
            "issue_templates_enabled": True,
            "pr_templates_enabled": True,
            "git_commit_template": True,
            "ci_cd_enabled": False,
            "documentation_enabled": False,
            "security_enabled": False,
        }

    return {
        "name": name,
        "description": description,
        "languages": languages,
        "structure": structure,
        "dependencies": dependencies,
        "features": features,
    }


def create_mock_project_config(
    name: str = "test-project", language: str = "python", **overrides
) -> Dict[str, Any]:
    """Create a mock project configuration."""
    base_config = {
        "name": name,
        "language": language,
        "description": f"A {name} project with coding standards",
        "author": "Test Author",
        "email": "test@example.com",
        "license": "MIT",
        "git_enabled": True,
        "contributing_enabled": True,
        "code_of_conduct_enabled": True,
        "issue_templates_enabled": True,
        "pr_templates_enabled": True,
        "git_commit_template": True,
        "ci_cd_enabled": False,
        "documentation_enabled": False,
        "security_enabled": False,
        "contributing": {
            "branch_strategy": "github-flow",
            "conventional_commits": True,
            "pr_required": True,
            "review_required": True,
            "reviewers_count": 1,
            "issue_template_enabled": True,
            "cla_required": False,
        },
        "code_quality": {
            "pre_commit_enabled": True,
            "testing_enabled": True,
            "coverage_enabled": True,
            "coverage_threshold": 80,
            "formatter": "black",
            "linter": "flake8",
            "type_checker": "mypy",
            "import_sorter": "isort",
        },
    }

    base_config.update(overrides)
    return base_config


def mock_subprocess_commands():
    """Context manager to mock subprocess commands."""
    return patch.multiple(
        "subprocess",
        run=Mock(),
    )


def mock_git_commands():
    """Context manager to mock git commands."""
    mock_run = Mock()
    mock_run.return_value.returncode = 0

    return patch("subprocess.run", mock_run)


def mock_pre_commit_commands():
    """Context manager to mock pre-commit commands."""
    mock_run = Mock()
    mock_run.return_value.returncode = 0

    return patch("subprocess.run", mock_run)


def cleanup_test_project(project_path: Path) -> None:
    """Clean up a test project directory."""
    if project_path.exists():
        shutil.rmtree(project_path)


def assert_project_structure(
    project_path: Path, expected_structure: Dict[str, Any]
) -> None:
    """Assert that a project has the expected structure."""
    for item, details in expected_structure.items():
        item_path = project_path / item

        if isinstance(details, dict):
            # Directory with sub-items
            assert_directory_exists(item_path)
            assert_project_structure(item_path, details)
        elif isinstance(details, str):
            # File with content
            assert_file_exists(item_path)
            if details:  # If content is specified
                assert_file_contains(item_path, details)
        elif isinstance(details, list):
            # List of files or directories
            for sub_item in details:
                sub_path = item_path / sub_item
                if sub_item.endswith("/"):
                    assert_directory_exists(sub_path)
                else:
                    assert_file_exists(sub_path)


def create_mock_click_context(**params):
    """Create a mock Click context with given parameters."""
    context = Mock()
    context.params = {
        "language": "python",
        "name": "test-project",
        "path": None,
        "template": None,
        "force": False,
        "interactive": True,
        "non_interactive": False,
        **params,
    }
    return context
