"""Shared fixtures for tests."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from src.cli.prompts import ProjectConfigurator
from src.generators import ProjectGenerator


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock project configuration."""
    return {
        "name": "test-project",
        "language": "python",
        "description": "A test project with coding standards",
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


@pytest.fixture
def mock_project_configurator() -> ProjectConfigurator:
    """Mock ProjectConfigurator instance."""
    configurator = ProjectConfigurator()
    configurator.config = {
        "name": "test-project",
        "language": "python",
        "description": "A test project with coding standards",
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
    return configurator


@pytest.fixture
def mock_project_generator(tmp_path: Path) -> ProjectGenerator:
    """Mock ProjectGenerator instance."""
    generator = ProjectGenerator(templates_path=tmp_path / "templates")
    return generator


@pytest.fixture
def mock_click_context() -> Mock:
    """Mock Click context for CLI commands."""
    context = Mock()
    context.params = {
        "language": "python",
        "name": "test-project",
        "path": None,
        "template": None,
        "force": False,
        "interactive": True,
        "non_interactive": False,
    }
    return context


@pytest.fixture
def mock_rich_console() -> Mock:
    """Mock Rich console for testing."""
    console = Mock()
    console.print = Mock()
    return console


@pytest.fixture
def mock_rich_prompt() -> Mock:
    """Mock Rich prompt for testing."""
    prompt = Mock()
    prompt.ask = Mock(return_value="test-value")
    return prompt


@pytest.fixture
def mock_rich_confirm() -> Mock:
    """Mock Rich confirm for testing."""
    confirm = Mock()
    confirm.ask = Mock(return_value=True)
    return confirm


@pytest.fixture
def mock_rich_int_prompt() -> Mock:
    """Mock Rich int prompt for testing."""
    int_prompt = Mock()
    int_prompt.ask = Mock(return_value=1)
    return int_prompt


@pytest.fixture
def mock_subprocess() -> Mock:
    """Mock subprocess for testing."""
    subprocess = Mock()
    subprocess.run = Mock()
    subprocess.run.return_value.returncode = 0
    return subprocess


@pytest.fixture
def sample_template_files(tmp_path: Path) -> Path:
    """Create sample template files for testing."""
    templates_dir = tmp_path / "templates"
    python_template = templates_dir / "python" / "default"
    python_template.mkdir(parents=True)

    # Create template.yaml
    template_yaml = python_template / "template.yaml"
    template_yaml.write_text(
        """
name: "Python Project Template"
description: "Standard Python project with Sympulse coding standards"
languages: ["python"]
structure:
  directories:
    - "src"
    - "tests"
    - "docs"
  empty_files:
    - "src/__init__.py"
    - "tests/__init__.py"
dependencies:
  python:
    - "black"
    - "isort"
    - "flake8"
    - "mypy"
    - "pytest"
    - "pytest-cov"
features:
  contributing_enabled: true
  code_of_conduct_enabled: true
  issue_templates_enabled: true
  pr_templates_enabled: true
  git_commit_template: true
  ci_cd_enabled: false
  documentation_enabled: false
  security_enabled: false
"""
    )

    # Create files directory
    files_dir = python_template / "files"
    files_dir.mkdir()

    # Create sample files
    (files_dir / "pyproject.toml").write_text(
        """
[project]
name = "{{ project_name }}"
version = "0.1.0"
description = "{{ description }}"
"""
    )

    (files_dir / "README.md").write_text(
        """
# {{ project_name }}

{{ description }}

## Language: {{ language }}
"""
    )

    return templates_dir


@pytest.fixture
def sample_common_templates(tmp_path: Path) -> Path:
    """Create sample common templates for testing."""
    common_dir = tmp_path / "templates" / "common"
    common_dir.mkdir(parents=True)

    # Create CONTRIBUTING.md.j2
    contributing_template = common_dir / "CONTRIBUTING.md.j2"
    contributing_template.write_text(
        """
# Contributing to {{ project_name }}

Thank you for contributing to {{ project_name }}!

## Language: {{ language }}
## Formatter: {{ formatter }}
## Linter: {{ linter }}
"""
    )

    # Create CODE_OF_CONDUCT.md.j2
    coc_template = common_dir / "CODE_OF_CONDUCT.md.j2"
    coc_template.write_text(
        """
# Code of Conduct

Project: {{ project_name }}
Language: {{ language }}
"""
    )

    # Create .gitmessage.j2
    gitmessage_template = common_dir / ".gitmessage.j2"
    gitmessage_template.write_text(
        """
# Conventional Commits Template

# <type>[optional scope]: <description>
"""
    )

    # Create GitHub templates
    github_dir = common_dir / ".github"
    github_dir.mkdir()

    # Issue templates
    issue_dir = github_dir / "ISSUE_TEMPLATE"
    issue_dir.mkdir()

    (issue_dir / "bug_report.md.j2").write_text(
        """
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

## Bug Description

Project: {{ project_name }}
Language: {{ language }}
"""
    )

    (issue_dir / "feature_request.md.j2").write_text(
        """
---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: ['enhancement', 'needs-triage']
assignees: ''
---

## Problem Statement

Project: {{ project_name }}
Language: {{ language }}
"""
    )

    # PR template
    (github_dir / "PULL_REQUEST_TEMPLATE.md.j2").write_text(
        """
## Description

Project: {{ project_name }}
Language: {{ language }}

## Type of Change
"""
    )

    return templates_dir
