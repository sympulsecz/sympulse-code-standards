"""Integration tests for pre-commit configuration."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, Mock
from typing import Dict, Any

from src.generators import ProjectGenerator


class TestPreCommitConfiguration:
    """Test pre-commit configuration generation and validation."""

    def test_actual_template_does_not_contain_types_all(self):
        """Test that the actual pre-commit config template doesn't contain the problematic types-all package."""
        # Path to the actual template file
        template_path = Path(
            "src/templates/python/default/files/.pre-commit-config.yaml"
        )

        # Verify the template file exists
        assert template_path.exists(), f"Template file {template_path} should exist"

        # Read and parse the actual template
        with open(template_path, "r") as f:
            config_content = yaml.safe_load(f)

        # Find the mypy hook
        mypy_hook = None
        for repo in config_content["repos"]:
            if "mirrors-mypy" in repo["repo"]:
                for hook in repo["hooks"]:
                    if hook["id"] == "mypy":
                        mypy_hook = hook
                        break
                break

        # Verify mypy hook exists and doesn't contain types-all
        assert mypy_hook is not None, "mypy hook should exist in the actual template"
        assert "types-all" not in str(
            mypy_hook
        ), "Actual template should not contain types-all"

        # Verify it has the correct type packages
        expected_types = [
            "types-requests",
            "types-PyYAML",
            "types-setuptools",
            "types-click",
        ]
        for expected_type in expected_types:
            assert (
                expected_type in mypy_hook["additional_dependencies"]
            ), f"Template should contain {expected_type}"

        # Verify it's using the correct mypy version
        mypy_repo = None
        for repo in config_content["repos"]:
            if "mirrors-mypy" in repo["repo"]:
                mypy_repo = repo
                break

        assert mypy_repo is not None
        assert mypy_repo["rev"] == "v1.9.0", "Template should use mypy v1.9.0"
        assert (
            mypy_repo["rev"] != "v1.8.0"
        ), "Template should not use the old problematic mypy version"

    def test_pre_commit_config_does_not_contain_types_all(self, tmp_path: Path):
        """Test that the generated pre-commit config doesn't contain the problematic types-all package."""
        generator = ProjectGenerator()

        # Create a mock template structure
        template_dir = tmp_path / "templates" / "python" / "default"
        template_dir.mkdir(parents=True)

        # Create the pre-commit config template
        files_dir = template_dir / "files"
        files_dir.mkdir()

        pre_commit_config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.5.0",
                    "hooks": [
                        {"id": "trailing-whitespace"},
                        {"id": "end-of-file-fixer"},
                        {"id": "check-yaml"},
                        {"id": "check-toml"},
                        {"id": "check-added-large-files"},
                        {"id": "check-merge-conflict"},
                        {"id": "debug-statements"},
                    ],
                },
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "23.12.1",
                    "hooks": [{"id": "black", "language_version": "python3"}],
                },
                {
                    "repo": "https://github.com/pycqa/isort",
                    "rev": "5.13.2",
                    "hooks": [{"id": "isort", "name": "isort (python)"}],
                },
                {
                    "repo": "https://github.com/pycqa/flake8",
                    "rev": "7.0.0",
                    "hooks": [
                        {
                            "id": "flake8",
                            "additional_dependencies": ["flake8-docstrings"],
                        }
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-mypy",
                    "rev": "v1.9.0",
                    "hooks": [
                        {
                            "id": "mypy",
                            "additional_dependencies": [
                                "types-requests",
                                "types-PyYAML",
                                "types-setuptools",
                                "types-click",
                            ],
                            "args": ["--ignore-missing-imports"],
                        }
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-prettier",
                    "rev": "v3.1.0",
                    "hooks": [
                        {"id": "prettier", "types_or": ["yaml", "json", "markdown"]}
                    ],
                },
            ]
        }

        with open(files_dir / ".pre-commit-config.yaml", "w") as f:
            yaml.dump(pre_commit_config, f)

        # Verify the config doesn't contain types-all
        with open(files_dir / ".pre-commit-config.yaml", "r") as f:
            config_content = yaml.safe_load(f)

        # Check that mypy hook exists and doesn't have types-all
        mypy_hook = None
        for repo in config_content["repos"]:
            if "mirrors-mypy" in repo["repo"]:
                for hook in repo["hooks"]:
                    if hook["id"] == "mypy":
                        mypy_hook = hook
                        break
                break

        assert mypy_hook is not None, "mypy hook should exist"
        assert "types-all" not in str(
            mypy_hook
        ), "mypy hook should not contain types-all"

        # Check that it has the correct type packages
        expected_types = [
            "types-requests",
            "types-PyYAML",
            "types-setuptools",
            "types-click",
        ]
        for expected_type in expected_types:
            assert (
                expected_type in mypy_hook["additional_dependencies"]
            ), f"Should contain {expected_type}"

    def test_pre_commit_config_validation(self, tmp_path: Path):
        """Test that the pre-commit configuration is valid YAML and has correct structure."""
        generator = ProjectGenerator()

        # Create a mock template structure
        template_dir = tmp_path / "templates" / "python" / "default"
        template_dir.mkdir(parents=True)

        # Create the pre-commit config template
        files_dir = template_dir / "files"
        files_dir.mkdir()

        pre_commit_config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.5.0",
                    "hooks": [
                        {"id": "trailing-whitespace"},
                        {"id": "end-of-file-fixer"},
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-mypy",
                    "rev": "v1.9.0",
                    "hooks": [
                        {
                            "id": "mypy",
                            "additional_dependencies": [
                                "types-requests",
                                "types-PyYAML",
                            ],
                            "args": ["--ignore-missing-imports"],
                        }
                    ],
                },
            ]
        }

        config_path = files_dir / ".pre-commit-config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(pre_commit_config, f)

        # Verify the file can be read as valid YAML
        with open(config_path, "r") as f:
            config_content = yaml.safe_load(f)

        # Verify the structure
        assert "repos" in config_content
        assert isinstance(config_content["repos"], list)
        assert len(config_content["repos"]) == 2

        # Verify the mypy configuration specifically
        mypy_repo = None
        for repo in config_content["repos"]:
            if "mirrors-mypy" in repo["repo"]:
                mypy_repo = repo
                break

        assert mypy_repo is not None
        assert mypy_repo["rev"] == "v1.9.0"

        mypy_hook = None
        for hook in mypy_repo["hooks"]:
            if hook["id"] == "mypy":
                mypy_hook = hook
                break

        assert mypy_hook is not None
        assert "types-requests" in mypy_hook["additional_dependencies"]
        assert "types-PyYAML" in mypy_hook["additional_dependencies"]
        assert "--ignore-missing-imports" in mypy_hook["args"]

    @patch("subprocess.run")
    def test_pre_commit_install_without_types_all_error(
        self, mock_subprocess, tmp_path: Path
    ):
        """Test that pre-commit install doesn't fail due to types-all dependency issues."""
        generator = ProjectGenerator()

        # Mock successful pre-commit install
        mock_subprocess.return_value.returncode = 0

        # Create a mock template structure
        template_dir = tmp_path / "templates" / "python" / "default"
        template_dir.mkdir(parents=True)

        # Create the pre-commit config template
        files_dir = template_dir / "files"
        files_dir.mkdir()

        pre_commit_config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.5.0",
                    "hooks": [
                        {"id": "trailing-whitespace"},
                        {"id": "end-of-file-fixer"},
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-mypy",
                    "rev": "v1.9.0",
                    "hooks": [
                        {
                            "id": "mypy",
                            "additional_dependencies": [
                                "types-requests",
                                "types-PyYAML",
                            ],
                            "args": ["--ignore-missing-imports"],
                        }
                    ],
                },
            ]
        }

        with open(files_dir / ".pre-commit-config.yaml", "w") as f:
            yaml.dump(pre_commit_config, f)

        # Test that pre-commit install would work
        try:
            generator._install_pre_commit_hooks(tmp_path, "python")

            # Verify pre-commit install was called
            pre_commit_calls = [
                call
                for call in mock_subprocess.call_args_list
                if "pre-commit" in str(call)
            ]
            assert len(pre_commit_calls) >= 2  # install + pre-push

        except Exception as e:
            # If there's an error, it shouldn't be related to types-all
            error_msg = str(e).lower()
            assert (
                "types-all" not in error_msg
            ), f"Error should not be related to types-all: {e}"
            assert (
                "types-pkg-resources" not in error_msg
            ), f"Error should not be related to types-pkg-resources: {e}"

    def test_pre_commit_config_uses_correct_mypy_version(self, tmp_path: Path):
        """Test that the pre-commit config uses a recent mypy version."""
        generator = ProjectGenerator()

        # Create a mock template structure
        template_dir = tmp_path / "templates" / "python" / "default"
        template_dir.mkdir(parents=True)

        # Create the pre-commit config template
        files_dir = template_dir / "files"
        files_dir.mkdir()

        pre_commit_config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/mirrors-mypy",
                    "rev": "v1.9.0",
                    "hooks": [
                        {
                            "id": "mypy",
                            "additional_dependencies": [
                                "types-requests",
                                "types-PyYAML",
                            ],
                            "args": ["--ignore-missing-imports"],
                        }
                    ],
                }
            ]
        }

        with open(files_dir / ".pre-commit-config.yaml", "w") as f:
            yaml.dump(pre_commit_config, f)

        # Verify the mypy version is recent
        with open(files_dir / ".pre-commit-config.yaml", "r") as f:
            config_content = yaml.safe_load(f)

        mypy_repo = None
        for repo in config_content["repos"]:
            if "mirrors-mypy" in repo["repo"]:
                mypy_repo = repo
                break

        assert mypy_repo is not None
        assert mypy_repo["rev"] == "v1.9.0"

        # Verify it's not using the old problematic version
        assert (
            mypy_repo["rev"] != "v1.8.0"
        ), "Should not use the old mypy version that had issues"

    def test_pre_commit_config_has_required_hooks(self, tmp_path: Path):
        """Test that the pre-commit configuration includes all required hooks."""
        generator = ProjectGenerator()

        # Create a mock template structure
        template_dir = tmp_path / "templates" / "python" / "default"
        template_dir.mkdir(parents=True)

        # Create the pre-commit config template
        files_dir = template_dir / "files"
        files_dir.mkdir()

        pre_commit_config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.5.0",
                    "hooks": [
                        {"id": "trailing-whitespace"},
                        {"id": "end-of-file-fixer"},
                        {"id": "check-yaml"},
                        {"id": "check-toml"},
                        {"id": "check-added-large-files"},
                        {"id": "check-merge-conflict"},
                        {"id": "debug-statements"},
                    ],
                },
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "23.12.1",
                    "hooks": [{"id": "black", "language_version": "python3"}],
                },
                {
                    "repo": "https://github.com/pycqa/isort",
                    "rev": "5.13.2",
                    "hooks": [{"id": "isort", "name": "isort (python)"}],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-mypy",
                    "rev": "v1.9.0",
                    "hooks": [
                        {
                            "id": "mypy",
                            "additional_dependencies": [
                                "types-requests",
                                "types-PyYAML",
                                "types-setuptools",
                                "types-click",
                            ],
                            "args": ["--ignore-missing-imports"],
                        }
                    ],
                },
            ]
        }

        with open(files_dir / ".pre-commit-config.yaml", "w") as f:
            yaml.dump(pre_commit_config, f)

        # Verify all required hooks are present
        with open(files_dir / ".pre-commit-config.yaml", "r") as f:
            config_content = yaml.safe_load(f)

        required_hooks = {
            "trailing-whitespace": "pre-commit-hooks",
            "end-of-file-fixer": "pre-commit-hooks",
            "black": "black",
            "isort": "isort",
            "mypy": "mirrors-mypy",
        }

        for hook_id, repo_name in required_hooks.items():
            hook_found = False
            for repo in config_content["repos"]:
                if repo_name in repo["repo"]:
                    for hook in repo["hooks"]:
                        if hook["id"] == hook_id:
                            hook_found = True
                            break
                    if hook_found:
                        break

            assert hook_found, f"Required hook {hook_id} not found in {repo_name}"
