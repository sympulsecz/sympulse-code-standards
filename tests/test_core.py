"""Tests for the core module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from sympulse_coding_standards.core import (
    StandardsManager,
    StandardsConfig,
    StandardMetadata,
    ValidationResult,
)


class TestStandardsConfig:
    """Test StandardsConfig class."""

    def test_standards_config_creation(self):
        """Test creating a StandardsConfig instance."""
        config = StandardsConfig(
            version="1.0.0",
            languages=["python", "typescript"],
            strict_mode=True,
            auto_fix=False,
        )

        assert config.version == "1.0.0"
        assert config.languages == ["python", "typescript"]
        assert config.strict_mode is True
        assert config.auto_fix is False

    def test_standards_config_defaults(self):
        """Test StandardsConfig default values."""
        config = StandardsConfig(version="1.0.0")

        assert config.languages == []
        assert config.strict_mode is False
        assert config.auto_fix is True


class TestValidationResult:
    """Test ValidationResult class."""

    def test_validation_result_creation(self):
        """Test creating a ValidationResult instance."""
        result = ValidationResult(
            is_compliant=True,
            violations=["error1"],
            warnings=["warning1"],
            suggestions=["suggestion1"],
            score=95.0,
        )

        assert result.is_compliant is True
        assert result.violations == ["error1"]
        assert result.warnings == ["warning1"]
        assert result.suggestions == ["suggestion1"]
        assert result.score == 95.0

    def test_validation_result_defaults(self):
        """Test ValidationResult default values."""
        result = ValidationResult(is_compliant=False)

        assert result.violations == []
        assert result.warnings == []
        assert result.suggestions == []
        assert result.score == 0.0


class TestStandardsManager:
    """Test StandardsManager class."""

    def test_standards_manager_creation(self):
        """Test creating a StandardsManager instance."""
        manager = StandardsManager()

        assert manager.standards_path is not None
        assert isinstance(manager.config, StandardsConfig)
        assert manager.standards_cache == {}

    def test_standards_manager_custom_path(self, tmp_path):
        """Test creating StandardsManager with custom path."""
        manager = StandardsManager(standards_path=tmp_path)

        assert manager.standards_path == tmp_path

    @patch("sympulse_coding_standards.core.toml.load")
    def test_load_config_with_file(self, mock_toml_load, tmp_path):
        """Test loading config from file."""
        mock_config = {
            "version": "2.0.0",
            "languages": ["python"],
            "strict_mode": True,
            "auto_fix": False,
        }
        mock_toml_load.return_value = mock_config

        config_file = tmp_path / "config.toml"
        config_file.touch()

        manager = StandardsManager(standards_path=tmp_path)

        assert manager.config.version == "2.0.0"
        assert manager.config.languages == ["python"]
        assert manager.config.strict_mode is True
        assert manager.config.auto_fix is False

    def test_load_config_defaults(self):
        """Test loading default config when no file exists."""
        manager = StandardsManager()

        assert manager.config.version == "0.2.0"
        assert "python" in manager.config.languages
        assert "typescript" in manager.config.languages

    def test_get_available_standards_no_standards(self, tmp_path):
        """Test getting available standards when none exist."""
        manager = StandardsManager(standards_path=tmp_path)
        standards = manager.get_available_standards()

        assert standards == []

    @patch("builtins.open")
    @patch("json.load")
    def test_get_available_standards(self, mock_json_load, mock_open, tmp_path):
        """Test getting available standards."""
        mock_metadata = {
            "name": "python",
            "version": "1.0.0",
            "description": "Python standards",
            "languages": ["python"],
            "last_updated": "2024-01-01",
            "maintainer": "Team",
        }
        mock_json_load.return_value = mock_metadata

        # Create standards directory structure
        python_dir = tmp_path / "python"
        python_dir.mkdir()
        metadata_file = python_dir / "metadata.json"
        metadata_file.touch()

        manager = StandardsManager(standards_path=tmp_path)
        standards = manager.get_available_standards()

        assert len(standards) == 1
        assert standards[0].name == "python"
        assert standards[0].version == "1.0.0"

    def test_get_standard_not_found(self):
        """Test getting a standard that doesn't exist."""
        manager = StandardsManager()

        with pytest.raises(
            ValueError, match="Standards for language 'nonexistent' not found"
        ):
            manager.get_standard("nonexistent")

    def test_detect_languages_python(self, tmp_path):
        """Test detecting Python language."""
        # Create pyproject.toml
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.touch()

        manager = StandardsManager()
        languages = manager._detect_languages(tmp_path)

        assert "python" in languages

    def test_detect_languages_typescript(self, tmp_path):
        """Test detecting TypeScript language."""
        # Create package.json
        package_file = tmp_path / "package.json"
        package_file.touch()

        manager = StandardsManager()
        languages = manager._detect_languages(tmp_path)

        assert "typescript" in languages

    def test_detect_languages_multiple(self, tmp_path):
        """Test detecting multiple languages."""
        # Create both Python and TypeScript files
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.touch()
        package_file = tmp_path / "package.json"
        package_file.touch()

        manager = StandardsManager()
        languages = manager._detect_languages(tmp_path)

        assert "python" in languages
        assert "typescript" in languages

    def test_validate_project_path_not_exists(self):
        """Test validating a project that doesn't exist."""
        manager = StandardsManager()

        with pytest.raises(ValueError, match="Project path does not exist"):
            manager.validate_project("/nonexistent/path")

    @patch.object(StandardsManager, "_validate_language")
    def test_validate_project_success(self, mock_validate_language, tmp_path):
        """Test successful project validation."""
        # Create a Python project
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.touch()

        mock_result = ValidationResult(
            is_compliant=True,
            violations=[],
            warnings=[],
            suggestions=[],
        )
        mock_validate_language.return_value = mock_result

        manager = StandardsManager()
        result = manager.validate_project(tmp_path)

        assert result.is_compliant is True
        assert result.score == 100.0

    @patch.object(StandardsManager, "_validate_language")
    def test_validate_project_with_violations(self, mock_validate_language, tmp_path):
        """Test project validation with violations."""
        # Create a Python project
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.touch()

        mock_result = ValidationResult(
            is_compliant=False,
            violations=["Missing required file"],
            warnings=[],
            suggestions=[],
        )
        mock_validate_language.return_value = mock_result

        manager = StandardsManager()
        result = manager.validate_project(tmp_path)

        assert result.is_compliant is False
        assert result.score < 100.0
        assert len(result.violations) == 1

    def test_update_project_standards_path_not_exists(self):
        """Test updating standards for a project that doesn't exist."""
        manager = StandardsManager()

        with pytest.raises(ValueError, match="Project path does not exist"):
            manager.update_project_standards("/nonexistent/path")
