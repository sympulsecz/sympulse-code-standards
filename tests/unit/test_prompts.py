"""Unit tests for the ProjectConfigurator class."""

from unittest.mock import patch

from src.cli.prompts import ProjectConfigurator


class TestProjectConfigurator:
    """Test ProjectConfigurator class."""

    def test_init(self):
        """Test ProjectConfigurator initialization."""
        configurator = ProjectConfigurator()
        assert configurator.config == {}

    @patch("src.cli.prompts.Prompt")
    @patch("src.cli.prompts.console")
    def test_get_project_name_validation(self, mock_console, mock_prompt):
        """Test project name validation and cleaning."""
        configurator = ProjectConfigurator()

        # Test with valid name
        mock_prompt.ask.return_value = "my-project"
        name = configurator._get_project_name()
        assert name == "my-project"

        # Test with name containing spaces
        mock_prompt.ask.return_value = "my awesome project"
        name = configurator._get_project_name()
        assert name == "my-awesome-project"

        # Test with name containing underscores
        mock_prompt.ask.return_value = "my_awesome_project"
        name = configurator._get_project_name()
        assert name == "my-awesome-project"

        # Test with name starting with number
        mock_prompt.ask.return_value = "123-project"
        name = configurator._get_project_name()
        assert name == "project-123-project"

        # Test with empty name (should use default)
        mock_prompt.ask.return_value = ""
        name = configurator._get_project_name()
        assert name == "my-project"

    @patch("src.cli.prompts.Prompt")
    @patch("src.cli.prompts.console")
    def test_select_language(self, mock_console, mock_prompt):
        """Test language selection."""
        configurator = ProjectConfigurator()

        # Test with default choice
        mock_prompt.ask.return_value = "python"
        language = configurator._select_language()
        assert language == "python"

        # Test with different choice
        mock_prompt.ask.return_value = "typescript"
        language = configurator._select_language()
        assert language == "typescript"

    @patch("src.cli.prompts.Prompt")
    @patch("src.cli.prompts.Confirm")
    @patch("src.cli.prompts.IntPrompt")
    @patch("src.cli.prompts.console")
    def test_configure_python_tools(
        self, mock_console, mock_int_prompt, mock_confirm, mock_prompt
    ):
        """Test Python-specific tool configuration."""
        configurator = ProjectConfigurator()

        mock_prompt.ask.side_effect = [
            "black",  # formatter
            "flake8",  # linter
            "mypy",  # type checker
            "isort",  # import sorter
        ]
        mock_confirm.ask.side_effect = [
            True,  # pre_commit_enabled
            True,  # testing_enabled
            True,  # coverage_enabled
        ]
        mock_int_prompt.ask.return_value = 80

        config = configurator._configure_code_quality_tools("python")

        # The method returns a dict with "code_quality" key
        assert "code_quality" in config
        tools = config["code_quality"]

        assert tools["formatter"] == "black"
        assert tools["linter"] == "flake8"
        assert tools["type_checker"] == "mypy"
        assert tools["import_sorter"] == "isort"
        assert tools["pre_commit_enabled"] is True
        assert tools["testing_enabled"] is True
        assert tools["coverage_enabled"] is True
        assert tools["coverage_threshold"] == 80

    @patch("src.cli.prompts.Prompt")
    @patch("src.cli.prompts.Confirm")
    @patch("src.cli.prompts.console")
    def test_configure_ci_cd(self, mock_console, mock_confirm, mock_prompt):
        """Test CI/CD configuration."""
        configurator = ProjectConfigurator()

        mock_prompt.ask.return_value = "github-actions"
        mock_confirm.ask.side_effect = [
            True,  # trigger on push
            True,  # trigger on pull request
            True,  # trigger on tags
            True,  # run tests
            True,  # run linting
            True,  # run security
            False,  # build and deploy
        ]

        config = configurator._configure_ci_cd("python")

        # The method returns a dict with "ci_cd" key
        assert "ci_cd" in config
        ci_cd_config = config["ci_cd"]

        assert ci_cd_config["platform"] == "github-actions"
        assert "push" in ci_cd_config["triggers"]
        assert "pull_request" in ci_cd_config["triggers"]
        assert "tags" in ci_cd_config["triggers"]
        assert "test" in ci_cd_config["jobs"]
        assert "lint" in ci_cd_config["jobs"]
        assert "security" in ci_cd_config["jobs"]
        assert "deploy" not in ci_cd_config["jobs"]

    @patch("src.cli.prompts.Prompt")
    @patch("src.cli.prompts.Confirm")
    @patch("src.cli.prompts.console")
    def test_configure_documentation(self, mock_console, mock_confirm, mock_prompt):
        """Test documentation configuration."""
        configurator = ProjectConfigurator()

        mock_prompt.ask.return_value = "mkdocs"
        mock_confirm.ask.side_effect = [
            True,  # api_docs
            True,  # readme_enabled
            True,  # changelog_enabled
        ]

        config = configurator._configure_documentation()

        # The method returns a dict with "documentation" key
        assert "documentation" in config
        docs_config = config["documentation"]

        assert docs_config["generator"] == "mkdocs"
        assert docs_config["api_docs"] is True
        assert docs_config["readme_enabled"] is True
        assert docs_config["changelog_enabled"] is True

    @patch("src.cli.prompts.Confirm")
    @patch("src.cli.prompts.console")
    def test_configure_security(self, mock_console, mock_confirm):
        """Test security configuration."""
        configurator = ProjectConfigurator()

        mock_confirm.ask.side_effect = [
            True,  # dependency_scanning
            True,  # code_scanning
            True,  # secrets_detection
            False,  # sbom_enabled
        ]

        config = configurator._configure_security()

        # The method returns a dict with "security" key
        assert "security" in config
        security_config = config["security"]

        assert security_config["dependency_scanning"] is True
        assert security_config["code_scanning"] is True
        assert security_config["secrets_detection"] is True
        assert security_config["sbom_enabled"] is False

    @patch("src.cli.prompts.console")
    def test_show_final_configuration(self, mock_console):
        """Test final configuration summary display."""
        configurator = ProjectConfigurator()
        configurator.config = {
            "description": "Test project",
            "author": "Test Author",
            "license": "MIT",
            "contributing_enabled": True,
            "ci_cd_enabled": True,
            "documentation_enabled": True,
            "security_enabled": True,
        }

        configurator._show_final_configuration()

        # Verify console.print was called multiple times
        assert mock_console.print.call_count > 0
