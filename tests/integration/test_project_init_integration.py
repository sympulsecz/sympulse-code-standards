"""Integration tests for the project init command."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import subprocess
import sys

from src.cli.commands.project.init import init_project
from src.cli.prompts import ProjectConfigurator
from src.generators import ProjectGenerator


class TestProjectInitIntegration:
    """Integration tests for project initialization."""

    @patch("subprocess.run")
    def test_full_project_initialization_python(
        self, mock_subprocess, sample_template_files, sample_common_templates
    ):
        """Test full project initialization for Python with all features enabled."""
        # Setup subprocess mocks
        mock_subprocess.return_value.returncode = 0

        # Create a temporary project directory
        project_dir = Path("/tmp/test-integration-project")
        project_dir.mkdir(exist_ok=True)

        try:
            # Test the full flow
            result = init_project(
                language="python",
                name="test-integration-project",
                path=Path("/tmp"),
                template=None,
                force=True,
                interactive=False,
                non_interactive=True,
            )

            # Verify the result
            assert result is True

            # Verify project structure was created
            project_path = Path("/tmp") / "test-integration-project"
            assert project_path.exists()

            # Verify basic project files
            assert (project_path / "src").exists()
            assert (project_path / "tests").exists()
            assert (project_path / "docs").exists()

            # Verify template files were rendered
            if (project_path / "pyproject.toml").exists():
                pyproject_content = (project_path / "pyproject.toml").read_text()
                assert "test-integration-project" in pyproject_content

            if (project_path / "README.md").exists():
                readme_content = (project_path / "README.md").read_text()
                assert "test-integration-project" in readme_content
                assert "python" in readme_content.lower()

            # Verify git repository was initialized
            git_calls = [
                call
                for call in mock_subprocess.call_args_list
                if "git init" in str(call)
            ]
            assert len(git_calls) > 0

            # Verify pre-commit hooks were installed
            pre_commit_calls = [
                call
                for call in mock_subprocess.call_args_list
                if "pre-commit" in str(call)
            ]
            assert len(pre_commit_calls) > 0

        finally:
            # Cleanup
            if project_dir.exists():
                import shutil

                shutil.rmtree(project_dir)

    @patch("subprocess.run")
    def test_full_project_initialization_typescript(
        self, mock_subprocess, sample_template_files, sample_common_templates
    ):
        """Test full project initialization for TypeScript with all features enabled."""
        # Setup subprocess mocks
        mock_subprocess.return_value.returncode = 0

        # Create a temporary project directory
        project_dir = Path("/tmp/test-typescript-project")
        project_dir.mkdir(exist_ok=True)

        try:
            # Test the full flow
            result = init_project(
                language="typescript",
                name="test-typescript-project",
                path=Path("/tmp"),
                template=None,
                force=True,
                interactive=False,
                non_interactive=True,
            )

            # Verify the result
            assert result is True

            # Verify project structure was created
            project_path = Path("/tmp") / "test-typescript-project"
            assert project_path.exists()

            # Verify basic project files
            assert (project_path / "src").exists()
            assert (project_path / "tests").exists()
            assert (project_path / "docs").exists()

            # Verify template files were rendered
            if (project_path / "package.json").exists():
                package_content = (project_path / "package.json").read_text()
                assert "test-typescript-project" in package_content

            if (project_path / "README.md").exists():
                readme_content = (project_path / "README.md").read_text()
                assert "test-typescript-project" in readme_content
                assert "typescript" in readme_content.lower()

        finally:
            # Cleanup
            if project_dir.exists():
                import shutil

                shutil.rmtree(project_dir)

    @patch("subprocess.run")
    def test_project_initialization_with_custom_template(
        self, mock_subprocess, sample_template_files, sample_common_templates
    ):
        """Test project initialization with a custom template."""
        # Setup subprocess mocks
        mock_subprocess.return_value.returncode = 0

        # Create a custom template
        custom_template_dir = sample_template_files / "python" / "custom"
        custom_template_dir.mkdir()

        # Create custom template.yaml
        template_yaml = custom_template_dir / "template.yaml"
        template_yaml.write_text(
            """
name: "Custom Python Template"
description: "A custom Python template for testing"
languages: ["python"]
structure:
  directories:
    - "custom_src"
    - "custom_tests"
  empty_files:
    - "custom_src/__init__.py"
    - "custom_tests/__init__.py"
dependencies:
  python:
    - "custom_package"
features:
  contributing_enabled: false
  code_of_conduct_enabled: false
  issue_templates_enabled: false
  pr_templates_enabled: false
  git_commit_template: false
  ci_cd_enabled: false
  documentation_enabled: false
  security_enabled: false
"""
        )

        # Create custom files directory
        files_dir = custom_template_dir / "files"
        files_dir.mkdir()

        # Create custom README
        (files_dir / "README.md").write_text(
            """
# {{ project_name }}

Custom template for {{ project_name }}

Language: {{ language }}
"""
        )

        # Create a temporary project directory
        project_dir = Path("/tmp/test-custom-template-project")
        project_dir.mkdir(exist_ok=True)

        try:
            # Test the full flow with custom template
            result = init_project(
                language="python",
                name="test-custom-template-project",
                path=Path("/tmp"),
                template="custom",
                force=True,
                interactive=False,
                non_interactive=True,
            )

            # Verify the result
            assert result is True

            # Verify project structure was created with custom template
            project_path = Path("/tmp") / "test-custom-template-project"
            assert project_path.exists()

            # Verify custom directories were created
            assert (project_path / "custom_src").exists()
            assert (project_path / "custom_tests").exists()

            # Verify custom files were created
            assert (project_path / "custom_src" / "__init__.py").exists()
            assert (project_path / "custom_tests" / "__init__.py").exists()

            # Verify custom README was rendered
            if (project_path / "README.md").exists():
                readme_content = (project_path / "README.md").read_text()
                assert "test-custom-template-project" in readme_content
                assert (
                    "Custom template for test-custom-template-project" in readme_content
                )
                assert "Language: python" in readme_content

        finally:
            # Cleanup
            if project_dir.exists():
                import shutil

                shutil.rmtree(project_dir)

    @patch("subprocess.run")
    def test_project_initialization_with_contributing_features(
        self, mock_subprocess, sample_template_files, sample_common_templates
    ):
        """Test project initialization with contributing features enabled."""
        # Setup subprocess mocks
        mock_subprocess.return_value.returncode = 0

        # Create a temporary project directory
        project_dir = Path("/tmp/test-contributing-project")
        project_dir.mkdir(exist_ok=True)

        try:
            # Test the full flow
            result = init_project(
                language="python",
                name="test-contributing-project",
                path=Path("/tmp"),
                template=None,
                force=True,
                interactive=False,
                non_interactive=True,
            )

            # Verify the result
            assert result is True

            # Verify project structure was created
            project_path = Path("/tmp") / "test-contributing-project"
            assert project_path.exists()

            # Verify contributing files were generated
            assert (project_path / "CONTRIBUTING.md").exists()
            assert (project_path / "CODE_OF_CONDUCT.md").exists()
            assert (project_path / ".gitmessage").exists()

            # Verify GitHub templates were generated
            assert (
                project_path / ".github" / "ISSUE_TEMPLATE" / "bug_report.md"
            ).exists()
            assert (
                project_path / ".github" / "ISSUE_TEMPLATE" / "feature_request.md"
            ).exists()
            assert (project_path / ".github" / "PULL_REQUEST_TEMPLATE.md").exists()

            # Verify contributing content
            contributing_content = (project_path / "CONTRIBUTING.md").read_text()
            assert "test-contributing-project" in contributing_content
            assert "python" in contributing_content.lower()

            # Verify code of conduct content
            coc_content = (project_path / "CODE_OF_CONDUCT.md").read_text()
            assert "test-contributing-project" in coc_content

            # Verify commit template content
            gitmessage_content = (project_path / ".gitmessage").read_text()
            assert "Conventional Commits" in gitmessage_content

        finally:
            # Cleanup
            if project_dir.exists():
                import shutil

                shutil.rmtree(project_dir)

    @patch("subprocess.run")
    def test_project_initialization_with_ci_cd(
        self, mock_subprocess, sample_template_files, sample_common_templates
    ):
        """Test project initialization with CI/CD features enabled."""
        # Setup subprocess mocks
        mock_subprocess.return_value.returncode = 0

        # Create a temporary project directory
        project_dir = Path("/tmp/test-cicd-project")
        project_dir.mkdir(exist_ok=True)

        try:
            # Test the full flow
            result = init_project(
                language="python",
                name="test-cicd-project",
                path=Path("/tmp"),
                template=None,
                force=True,
                interactive=False,
                non_interactive=True,
            )

            # Verify the result
            assert result is True

            # Verify project structure was created
            project_path = Path("/tmp") / "test-cicd-project"
            assert project_path.exists()

            # Verify CI/CD files were generated
            assert (project_path / ".github" / "workflows" / "ci.yml").exists()

            # Verify CI workflow content
            ci_workflow = (
                project_path / ".github" / "workflows" / "ci.yml"
            ).read_text()
            assert "name: CI" in ci_workflow
            assert "on:" in ci_workflow
            assert "jobs:" in ci_workflow

        finally:
            # Cleanup
            if project_dir.exists():
                import shutil

                shutil.rmtree(project_dir)

    @patch("subprocess.run")
    def test_project_initialization_with_documentation(
        self, mock_subprocess, sample_template_files, sample_common_templates
    ):
        """Test project initialization with documentation features enabled."""
        # Setup subprocess mocks
        mock_subprocess.return_value.returncode = 0

        # Create a temporary project directory
        project_dir = Path("/tmp/test-docs-project")
        project_dir.mkdir(exist_ok=True)

        try:
            # Test the full flow
            result = init_project(
                language="python",
                name="test-docs-project",
                path=Path("/tmp"),
                template=None,
                force=True,
                interactive=False,
                non_interactive=True,
            )

            # Verify the result
            assert result is True

            # Verify project structure was created
            project_path = Path("/tmp") / "test-docs-project"
            assert project_path.exists()

            # Verify documentation files were generated
            assert (project_path / "CHANGELOG.md").exists()

            # Verify changelog content
            changelog_content = (project_path / "CHANGELOG.md").read_text()
            assert "Changelog" in changelog_content
            assert "test-docs-project" in changelog_content
            assert "Unreleased" in changelog_content

        finally:
            # Cleanup
            if project_dir.exists():
                import shutil

                shutil.rmtree(project_dir)

    def test_project_configurator_integration(self):
        """Test ProjectConfigurator integration with real prompts."""
        configurator = ProjectConfigurator()

        # Test that configurator can be instantiated
        assert configurator is not None
        assert configurator.config == {}

        # Test that configurator has all required methods
        assert hasattr(configurator, "configure_project")
        assert hasattr(configurator, "_get_project_name")
        assert hasattr(configurator, "_select_language")
        assert hasattr(configurator, "_get_basic_info")
        assert hasattr(configurator, "_configure_repository_features")
        assert hasattr(configurator, "_configure_contributing_guidelines")
        assert hasattr(configurator, "_configure_code_quality_tools")
        assert hasattr(configurator, "_configure_ci_cd")
        assert hasattr(configurator, "_configure_documentation")
        assert hasattr(configurator, "_configure_security")

    def test_project_generator_integration(self):
        """Test ProjectGenerator integration with real templates."""
        generator = ProjectGenerator()

        # Test that generator can be instantiated
        assert generator is not None
        assert generator.templates_path is not None

        # Test that generator has all required methods
        assert hasattr(generator, "create_project")
        assert hasattr(generator, "_generate_structure")
        assert hasattr(generator, "_generate_files")
        assert hasattr(generator, "_generate_configured_files")
        assert hasattr(generator, "_prepare_template_vars")
        assert hasattr(generator, "_render_template")
        assert hasattr(generator, "_get_template_vars")

        # Test that generator can list templates
        templates = generator.list_templates()
        assert isinstance(templates, list)

    def test_end_to_end_workflow(self, sample_template_files, sample_common_templates):
        """Test the complete end-to-end workflow."""
        # This test verifies that all components work together
        # without actually creating files (using mocks)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            # Test the complete flow
            result = init_project(
                language="python",
                name="test-end-to-end",
                path=Path("/tmp"),
                template=None,
                force=True,
                interactive=False,
                non_interactive=True,
            )

            # Verify the result
            assert result is True

            # Verify that subprocess was called for git and pre-commit
            assert mock_subprocess.call_count > 0

            # Verify git commands were called
            git_calls = [
                call for call in mock_subprocess.call_args_list if "git" in str(call)
            ]
            assert len(git_calls) > 0

            # Verify pre-commit commands were called
            pre_commit_calls = [
                call
                for call in mock_subprocess.call_args_list
                if "pre-commit" in str(call)
            ]
            assert len(pre_commit_calls) > 0
