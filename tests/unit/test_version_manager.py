"""Unit tests for the version manager."""

import pytest
from unittest.mock import patch

from src.lib.version_manager import VersionManager


class TestVersionManager:
    """Test cases for VersionManager class."""

    @pytest.fixture
    def mock_versions_data(self):
        """Mock versions data for testing."""
        return {
            "versions": {
                "project": "0.2.0",
                "python": "3.13",
                "python_min": "3.11",
                "python_target": "py313",
                "node": "24",
                "node_min": "22",
            },
            "file_patterns": {
                "python_configs": [
                    "pyproject.toml",
                    "src/standards/python/config.toml",
                ],
                "typescript_configs": ["src/standards/typescript/config.toml"],
                "project_configs": ["src/standards/config.toml", "src/__init__.py"],
                "scripts": ["install.sh"],
                "templates": ["src/generators.py"],
            },
        }

    @pytest.fixture
    def version_manager(self, mock_versions_data, tmp_path):
        """Create a VersionManager instance for testing."""
        with patch("src.lib.version_manager.tomllib.load") as mock_load:
            mock_load.return_value = mock_versions_data

            # Create a mock versions file
            versions_file = tmp_path / "src" / "versions.toml"
            versions_file.parent.mkdir(parents=True)
            versions_file.touch()

            with patch("src.lib.version_manager.Path") as mock_path:
                mock_path.return_value = tmp_path
                mock_path.cwd.return_value = tmp_path

                manager = VersionManager()
                manager.versions = mock_versions_data
                return manager

    def test_get_version(self, version_manager):
        """Test getting a version by key."""
        assert version_manager.get_version("python") == "3.13"
        assert version_manager.get_version("node") == "24"
        assert version_manager.get_version("nonexistent") == ""

    def test_set_version(self, version_manager):
        """Test setting a version by key."""
        with patch("src.lib.version_manager.tomli_w.dump") as mock_dump:
            version_manager.set_version("python", "3.14")
            assert version_manager.versions["versions"]["python"] == "3.14"
            mock_dump.assert_called_once()

    def test_validate_versions_valid(self, version_manager):
        """Test version validation with valid versions."""
        errors = version_manager.validate_versions()
        assert len(errors) == 0

    def test_validate_versions_invalid_python(self, version_manager):
        """Test version validation with invalid Python version."""
        version_manager.versions["versions"]["python"] = "3.10"  # Below minimum
        errors = version_manager.validate_versions()
        assert len(errors) == 1
        assert "Python version 3.10 is below minimum 3.11" in errors[0]

    def test_validate_versions_invalid_node(self, version_manager):
        """Test version validation with invalid Node.js version."""
        version_manager.versions["versions"]["node"] = "20"  # Below minimum
        errors = version_manager.validate_versions()
        assert len(errors) == 1
        assert "Node.js version 20 is below minimum 22" in errors[0]

    @patch("src.lib.version_manager.Path")
    def test_update_python_version(self, mock_path, version_manager, tmp_path):
        """Test updating Python version."""
        mock_path.return_value = tmp_path

        with patch.object(
            version_manager, "_update_python_configs"
        ) as mock_update_configs, patch.object(
            version_manager, "_update_install_script"
        ) as mock_update_script, patch.object(
            version_manager, "_update_generators"
        ) as mock_update_generators:

            version_manager.update_python_version("3.14")

            assert version_manager.versions["versions"]["python"] == "3.14"
            assert version_manager.versions["versions"]["python_target"] == "py314"
            mock_update_configs.assert_called_once_with("3.14", "py314")
            mock_update_script.assert_called_once_with("3.14")
            mock_update_generators.assert_called_once_with("3.14")

    @patch("src.lib.version_manager.Path")
    def test_update_node_version(self, mock_path, version_manager, tmp_path):
        """Test updating Node.js version."""
        mock_path.return_value = tmp_path

        with patch.object(
            version_manager, "_update_typescript_configs"
        ) as mock_update_configs, patch.object(
            version_manager, "_update_generators"
        ) as mock_update_generators:

            version_manager.update_node_version("26")

            assert version_manager.versions["versions"]["node"] == "26"
            mock_update_configs.assert_called_once_with("26")
            mock_update_generators.assert_called_once_with("26")

    @patch("src.lib.version_manager.Path")
    def test_update_project_version(self, mock_path, version_manager, tmp_path):
        """Test updating project version."""
        mock_path.return_value = tmp_path

        with patch.object(
            version_manager, "_update_project_configs"
        ) as mock_update_configs:

            version_manager.update_project_version("0.3.0")

            assert version_manager.versions["versions"]["project"] == "0.3.0"
            mock_update_configs.assert_called_once_with("0.3.0")

    def test_update_file_content(self, version_manager, tmp_path):
        """Test updating file content with regex patterns."""
        test_file = tmp_path / "test.txt"
        test_file.write_text('python_version = "3.13"\ntarget_version = ["py313"]')

        patterns = [
            (r'python_version\s*=\s*"[^"]*"', 'python_version = "3.14"'),
            (r"target_version\s*=\s*\[[^\]]*\]", 'target_version = ["py314"]'),
        ]

        version_manager._update_file_content(test_file, patterns)

        content = test_file.read_text()
        assert 'python_version = "3.14"' in content
        assert 'target_version = ["py314"]' in content

    def test_update_file_content_no_changes(self, version_manager, tmp_path):
        """Test updating file content when no changes are needed."""
        test_file = tmp_path / "test.txt"
        test_file.write_text('python_version = "3.13"')

        patterns = [
            (r'python_version\s*=\s*"[^"]*"', 'python_version = "3.13"')  # Same version
        ]

        # Should not raise an error
        version_manager._update_file_content(test_file, patterns)

        # Content should remain the same
        assert test_file.read_text() == 'python_version = "3.13"'

    def test_update_all_versions(self, version_manager):
        """Test updating multiple versions at once."""
        with patch.object(
            version_manager, "update_python_version"
        ) as mock_python, patch.object(
            version_manager, "update_node_version"
        ) as mock_node, patch.object(
            version_manager, "validate_versions"
        ) as mock_validate:

            mock_validate.return_value = []

            version_manager.update_all_versions(python="3.14", node="26")

            mock_python.assert_called_once_with("3.14")
            mock_node.assert_called_once_with("26")
            mock_validate.assert_called_once()

    def test_update_all_versions_with_validation_errors(self, version_manager):
        """Test updating versions with validation errors."""
        with patch.object(
            version_manager, "update_python_version"
        ) as mock_python, patch.object(
            version_manager, "validate_versions"
        ) as mock_validate:

            mock_validate.return_value = ["Python version too low"]

            # Should still update but show warnings
            version_manager.update_all_versions(python="3.14")

            mock_python.assert_called_once_with("3.14")
            mock_validate.assert_called_once()
