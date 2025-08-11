"""Unit tests for the CLI init command."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import click
from click.testing import CliRunner

from src.cli.commands.project.init import init_project


class TestInitCommand:
    """Test the init command."""

    @patch("src.cli.commands.project.init.ProjectConfigurator")
    @patch("src.cli.commands.project.init.ProjectGenerator")
    @patch("src.cli.commands.project.init.Path")
    def test_init_project_interactive_mode(
        self, mock_path, mock_generator_class, mock_configurator_class, mock_config
    ):
        """Test project initialization in interactive mode."""
        # Setup mocks
        mock_path.cwd.return_value = Path("/tmp")
        mock_path.return_value.__truediv__.return_value = Path("/tmp/test-project")

        mock_configurator = Mock()
        mock_configurator.configure_project.return_value = mock_config
        mock_configurator_class.return_value = mock_configurator

        mock_generator = Mock()
        mock_generator.create_project.return_value = True
        mock_generator_class.return_value = mock_generator

        # Call the command function directly (for unit testing)
        result = init_project(
            language="python",
            name="test-project",
            path=None,
            template=None,
            force=False,
            interactive=True,
            non_interactive=False,
        )

        # Verify configurator was called
        mock_configurator.configure_project.assert_called_once_with(
            "python", "test-project"
        )

        # Verify generator was called with config
        mock_generator.create_project.assert_called_once()
        call_args = mock_generator.create_project.call_args
        assert call_args[1]["config"] == mock_config

        # Verify project path was set correctly
        mock_path.return_value.__truediv__.assert_called_once_with("test-project")

    @patch("src.cli.commands.project.init.ProjectGenerator")
    @patch("src.cli.commands.project.init.Path")
    def test_init_project_non_interactive_mode(
        self, mock_path, mock_generator_class, mock_config
    ):
        """Test project initialization in non-interactive mode."""
        # Setup mocks
        mock_path.cwd.return_value = Path("/tmp")
        mock_path.return_value.__truediv__.return_value = Path("/tmp/test-project")

        mock_generator = Mock()
        mock_generator.create_project.return_value = True
        mock_generator_class.return_value = mock_generator

        # Call the command function directly (for unit testing)
        result = init_project(
            language="python",
            name="test-project",
            path=None,
            template=None,
            force=False,
            interactive=False,
            non_interactive=True,
        )

        # Verify generator was called with default config
        mock_generator.create_project.assert_called_once()
        call_args = mock_generator.create_project.call_args
        assert call_args[1]["config"]["name"] == "test-project"
        assert call_args[1]["config"]["language"] == "python"

    def test_init_project_missing_name_non_interactive(self):
        """Test that missing name raises error in non-interactive mode."""
        with pytest.raises(
            click.UsageError,
            match="Project name must be specified when using --non-interactive mode",
        ):
            init_project(
                language="python",
                name=None,
                path=None,
                template=None,
                force=False,
                interactive=False,
                non_interactive=True,
            )

    def test_init_project_missing_language_non_interactive(self):
        """Test that missing language raises error in non-interactive mode."""
        with pytest.raises(
            click.UsageError,
            match="Language must be specified when using --non-interactive mode",
        ):
            init_project(
                language=None,
                name="test-project",
                path=None,
                template=None,
                force=False,
                interactive=False,
                non_interactive=True,
            )

    def test_init_project_missing_name_interactive(self):
        """Test that missing name raises error in interactive mode."""
        with pytest.raises(
            click.UsageError,
            match="Project name must be specified or selected interactively",
        ):
            init_project(
                language="python",
                name=None,
                path=None,
                template=None,
                force=False,
                interactive=True,
                non_interactive=False,
            )

    def test_init_project_missing_language_interactive(self):
        """Test that missing language raises error in interactive mode."""
        with pytest.raises(
            click.UsageError,
            match="Language must be specified or selected interactively",
        ):
            init_project(
                language=None,
                name="test-project",
                path=None,
                template=None,
                force=False,
                interactive=True,
                non_interactive=False,
            )

    @patch("src.cli.commands.project.init.ProjectConfigurator")
    @patch("src.cli.commands.project.init.ProjectGenerator")
    @patch("src.cli.commands.project.init.Path")
    def test_init_project_custom_path(
        self, mock_path, mock_generator_class, mock_configurator_class, mock_config
    ):
        """Test project initialization with custom path."""
        # Setup mocks
        custom_path = Path("/custom/path")
        mock_path.return_value.__truediv__.return_value = custom_path / "test-project"

        mock_configurator = Mock()
        mock_configurator.configure_project.return_value = mock_config
        mock_configurator_class.return_value = mock_configurator

        mock_generator = Mock()
        mock_generator.create_project.return_value = True
        mock_generator_class.return_value = mock_generator

        # Call the command function directly (for unit testing)
        result = init_project(
            language="python",
            name="test-project",
            path=custom_path,
            template=None,
            force=False,
            interactive=True,
            non_interactive=False,
        )

        # Verify custom path was used
        mock_path.return_value.__truediv__.assert_called_once_with("test-project")

    @patch("src.cli.commands.project.init.ProjectConfigurator")
    @patch("src.cli.commands.project.init.ProjectGenerator")
    @patch("src.cli.commands.project.init.Path")
    def test_init_project_custom_template(
        self, mock_path, mock_generator_class, mock_configurator_class, mock_config
    ):
        """Test project initialization with custom template."""
        # Setup mocks
        mock_path.cwd.return_value = Path("/tmp")
        mock_path.return_value.__truediv__.return_value = Path("/tmp/test-project")

        mock_configurator = Mock()
        mock_configurator.configure_project.return_value = mock_config
        mock_configurator_class.return_value = mock_configurator

        mock_generator = Mock()
        mock_generator.create_project.return_value = True
        mock_generator_class.return_value = mock_generator

        # Call the command function directly (for unit testing)
        result = init_project(
            language="python",
            name="test-project",
            path=None,
            template="custom-template",
            force=False,
            interactive=True,
            non_interactive=False,
        )

        # Verify custom template was passed to generator
        mock_generator.create_project.assert_called_once()
        call_args = mock_generator.create_project.call_args
        assert call_args[1]["template"] == "custom-template"

    @patch("src.cli.commands.project.init.ProjectConfigurator")
    @patch("src.cli.commands.project.init.ProjectGenerator")
    @patch("src.cli.commands.project.init.Path")
    def test_init_project_force_flag(
        self, mock_path, mock_generator_class, mock_configurator_class, mock_config
    ):
        """Test project initialization with force flag."""
        # Setup mocks
        mock_path.cwd.return_value = Path("/tmp")
        mock_path.return_value.__truediv__.return_value = Path("/tmp/test-project")

        mock_configurator = Mock()
        mock_configurator.configure_project.return_value = mock_config
        mock_configurator_class.return_value = mock_configurator

        mock_generator = Mock()
        mock_generator.create_project.return_value = True
        mock_generator_class.return_value = mock_generator

        # Call the command function directly (for unit testing)
        result = init_project(
            language="python",
            name="test-project",
            path=None,
            template=None,
            force=True,
            interactive=True,
            non_interactive=False,
        )

        # Verify force flag was passed to generator
        mock_generator.create_project.assert_called_once()
        call_args = mock_generator.create_project.call_args
        assert call_args[1]["force"] is True

    @patch("src.cli.commands.project.init.ProjectConfigurator")
    @patch("src.cli.commands.project.init.ProjectGenerator")
    @patch("src.cli.commands.project.init.Path")
    def test_init_project_generator_failure(
        self, mock_path, mock_generator_class, mock_configurator_class, mock_config
    ):
        """Test project initialization when generator fails."""
        # Setup mocks
        mock_path.cwd.return_value = Path("/tmp")
        mock_path.return_value.__truediv__.return_value = Path("/tmp/test-project")

        mock_configurator = Mock()
        mock_configurator.configure_project.return_value = mock_config
        mock_configurator_class.return_value = mock_configurator

        mock_generator = Mock()
        mock_generator.create_project.return_value = False  # Failure
        mock_generator_class.return_value = mock_generator

        # Call the command function directly (for unit testing)
        result = init_project(
            language="python",
            name="test-project",
            path=None,
            template=None,
            force=False,
            interactive=True,
            non_interactive=False,
        )

        # Verify result is False on failure
        assert result is False

    @patch("src.cli.commands.project.init.ProjectConfigurator")
    @patch("src.cli.commands.project.init.ProjectGenerator")
    @patch("src.cli.commands.project.init.Path")
    def test_init_project_interactive_mode_name_from_config(
        self, mock_path, mock_generator_class, mock_configurator_class, mock_config
    ):
        """Test that name from config is used in interactive mode."""
        # Setup mocks
        mock_path.cwd.return_value = Path("/tmp")
        mock_path.return_value.__truediv__.return_value = Path("/tmp/config-name")

        # Override name in config
        config_with_name = mock_config.copy()
        config_with_name["name"] = "config-name"

        mock_configurator = Mock()
        mock_configurator.configure_project.return_value = config_with_name
        mock_configurator_class.return_value = mock_configurator

        mock_generator = Mock()
        mock_generator.create_project.return_value = True
        mock_generator_class.return_value = mock_generator

        # Call the command function directly (for unit testing)
        result = init_project(
            language="python",
            name=None,
            path=None,
            template=None,
            force=False,
            interactive=True,
            non_interactive=False,
        )

        # Verify config name was used for path
        mock_path.return_value.__truediv__.assert_called_once_with("config-name")

    @patch("src.cli.commands.project.init.ProjectConfigurator")
    @patch("src.cli.commands.project.init.ProjectGenerator")
    @patch("src.cli.commands.project.init.Path")
    def test_init_project_interactive_mode_language_from_config(
        self, mock_path, mock_generator_class, mock_configurator_class, mock_config
    ):
        """Test that language from config is used in interactive mode."""
        # Setup mocks
        mock_path.cwd.return_value = Path("/tmp")
        mock_path.return_value.__truediv__.return_value = Path("/tmp/test-project")

        # Override language in config
        config_with_language = mock_config.copy()
        config_with_language["language"] = "typescript"

        mock_configurator = Mock()
        mock_configurator.configure_project.return_value = config_with_language
        mock_configurator_class.return_value = mock_configurator

        mock_generator = Mock()
        mock_generator.create_project.return_value = True
        mock_generator_class.return_value = mock_generator

        # Call the command function directly (for unit testing)
        result = init_project(
            language=None,
            name="test-project",
            path=None,
            template=None,
            force=False,
            interactive=True,
            non_interactive=False,
        )

        # Verify config language was passed to generator
        mock_generator.create_project.assert_called_once()
        call_args = mock_generator.create_project.call_args
        assert call_args[1]["language"] == "typescript"

    def test_init_project_interactive_mode_detection(self):
        """Test that interactive mode is correctly detected."""
        # Test interactive mode
        with patch(
            "src.cli.commands.project.init.ProjectConfigurator"
        ) as mock_configurator_class:
            with patch(
                "src.cli.commands.project.init.ProjectGenerator"
            ) as mock_generator_class:
                with patch("src.cli.commands.project.init.Path") as mock_path:
                    mock_path.cwd.return_value = Path("/tmp")
                    mock_path.return_value.__truediv__.return_value = Path(
                        "/tmp/test-project"
                    )

                    mock_configurator = Mock()
                    mock_configurator.configure_project.return_value = {
                        "name": "test-project",
                        "language": "python",
                    }
                    mock_configurator_class.return_value = mock_configurator

                    mock_generator = Mock()
                    mock_generator.create_project.return_value = True
                    mock_generator_class.return_value = mock_generator

                    # Test interactive=True, non_interactive=False
                    result = init_project(
                        language="python",
                        name="test-project",
                        path=None,
                        template=None,
                        force=False,
                        interactive=True,
                        non_interactive=False,
                    )

                    # Should use interactive mode
                    mock_configurator_class.assert_called_once()

                    # Test interactive=False, non_interactive=True
                    mock_configurator_class.reset_mock()
                    result = init_project(
                        language="python",
                        name="test-project",
                        path=None,
                        template=None,
                        force=False,
                        interactive=False,
                        non_interactive=True,
                    )

                    # Should not use interactive mode
                    mock_configurator_class.assert_not_called()
