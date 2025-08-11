"""Core standards management functionality."""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Any, Union
from dataclasses import dataclass, field

import yaml
import toml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


@dataclass
class StandardMetadata:
    """Metadata for a coding standard."""

    name: str
    version: str
    description: str
    languages: list[str]
    last_updated: str
    maintainer: str


@dataclass
class ValidationResult:
    """Result of standards validation."""

    is_compliant: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    score: float = 0.0


class StandardsConfig(BaseModel):
    """Configuration for standards."""

    version: str = Field(..., description="Standards version")
    languages: list[str] = Field(
        default_factory=list, description="Supported languages"
    )
    strict_mode: bool = Field(default=False, description="Enable strict validation")
    auto_fix: bool = Field(
        default=True, description="Auto-fix violations when possible"
    )


class StandardsManager:
    """Main class for managing coding standards."""

    def __init__(self, standards_path: Optional[Union[str, Path]] = None):
        """Initialize the standards manager.

        Args:
            standards_path: Path to standards directory. If None, uses default.
        """
        if standards_path is None:
            # Use the standards directory in this package
            package_dir = Path(__file__).parent
            self.standards_path = package_dir / "standards"
        else:
            self.standards_path = Path(standards_path)

        self.config = self._load_config()
        self.standards_cache: dict[str, Any] = {}

    def _load_config(self) -> StandardsConfig:
        """Load the main standards configuration."""
        config_file = self.standards_path / "config.toml"
        if config_file.exists():
            config_data = toml.load(config_file)
            return StandardsConfig(**config_data)
        else:
            # Return default config
            return StandardsConfig(
                version="0.1.0",
                languages=["python", "typescript"],
                strict_mode=False,
                auto_fix=True,
            )

    def get_available_standards(self) -> list[StandardMetadata]:
        """Get list of available standards."""
        standards = []

        for lang_dir in self.standards_path.iterdir():
            if lang_dir.is_dir() and not lang_dir.name.startswith("."):
                metadata_file = lang_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        data = json.load(f)
                        standards.append(StandardMetadata(**data))

        return standards

    def get_standard(self, language: str) -> dict[str, Any]:
        """Get standards for a specific language."""
        if language in self.standards_cache:
            return self.standards_cache[language]

        lang_dir = self.standards_path / language
        if not lang_dir.exists():
            raise ValueError(f"Standards for language '{language}' not found")

        # Load all configuration files for the language
        standard = {}

        # Load main config
        config_file = lang_dir / "config.toml"
        if config_file.exists():
            standard.update(toml.load(config_file))

        # Load rules
        rules_file = lang_dir / "rules.yaml"
        if rules_file.exists():
            with open(rules_file) as f:
                standard["rules"] = yaml.safe_load(f)

        # Load templates
        templates_dir = lang_dir / "templates"
        if templates_dir.exists():
            standard["templates"] = self._load_templates(templates_dir)

        self.standards_cache[language] = standard
        return standard

    def _load_templates(self, templates_dir: Path) -> dict[str, str]:
        """Load template files from directory."""
        templates = {}
        for template_file in templates_dir.rglob("*"):
            if template_file.is_file():
                rel_path = template_file.relative_to(templates_dir)
                with open(template_file) as f:
                    templates[str(rel_path)] = f.read()
        return templates

    def validate_project(self, project_path: Union[str, Path]) -> ValidationResult:
        """Validate a project against standards."""
        project_path = Path(project_path)

        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        # Detect project languages
        languages = self._detect_languages(project_path)

        violations = []
        warnings = []
        suggestions = []

        for language in languages:
            try:
                standard = self.get_standard(language)
                result = self._validate_language(project_path, language, standard)
                violations.extend(result.violations)
                warnings.extend(result.warnings)
                suggestions.extend(result.suggestions)
            except Exception as e:
                logger.warning(f"Failed to validate {language}: {e}")
                warnings.append(f"Failed to validate {language}: {e}")

        # Calculate compliance score
        total_checks = len(violations) + len(warnings)
        if total_checks == 0:
            score = 100.0
        else:
            score = max(0.0, 100.0 - (len(violations) * 10) - (len(warnings) * 2))

        return ValidationResult(
            is_compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            suggestions=suggestions,
            score=score,
        )

    def _detect_languages(self, project_path: Path) -> list[str]:
        """Detect languages used in a project."""
        languages = []

        # Check for language-specific files
        if (project_path / "pyproject.toml").exists() or (
            project_path / "requirements.txt"
        ).exists():
            languages.append("python")

        if (project_path / "package.json").exists() or (
            project_path / "tsconfig.json"
        ).exists():
            languages.append("typescript")

        if (project_path / "go.mod").exists():
            languages.append("go")

        if (project_path / "Cargo.toml").exists():
            languages.append("rust")

        return languages

    def _validate_language(
        self, project_path: Path, language: str, standard: dict[str, Any]
    ) -> ValidationResult:
        """Validate a project against language-specific standards."""
        # This is a simplified validation - in practice, you'd have more sophisticated logic
        violations = []
        warnings = []
        suggestions = []

        rules = standard.get("rules", {})

        # Check file structure
        if "file_structure" in rules:
            violations.extend(
                self._check_file_structure(project_path, rules["file_structure"])
            )

        # Check naming conventions
        if "naming" in rules:
            violations.extend(
                self._check_naming_conventions(project_path, rules["naming"])
            )

        # Check formatting
        if "formatting" in rules:
            warnings.extend(self._check_formatting(project_path, rules["formatting"]))

        return ValidationResult(
            is_compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            suggestions=suggestions,
        )

    def _check_file_structure(
        self, project_path: Path, rules: dict[str, Any]
    ) -> list[str]:
        """Check project file structure against rules."""
        violations = []

        required_dirs = rules.get("required_directories", [])
        for required_dir in required_dirs:
            if not (project_path / required_dir).exists():
                violations.append(f"Missing required directory: {required_dir}")

        required_files = rules.get("required_files", [])
        for required_file in required_files:
            if not (project_path / required_file).exists():
                violations.append(f"Missing required file: {required_file}")

        return violations

    def _check_naming_conventions(
        self, project_path: Path, rules: dict[str, Any]
    ) -> list[str]:
        """Check naming conventions against rules."""
        violations = []

        # This is a simplified check - in practice, you'd scan actual files
        naming_patterns = rules.get("patterns", {})

        # Check module naming
        if "modules" in naming_patterns:
            pattern = naming_patterns["modules"]
            # Implementation would scan Python files for module names

        return violations

    def _check_formatting(self, project_path: Path, rules: dict[str, Any]) -> list[str]:
        """Check code formatting against rules."""
        warnings = []

        # This would integrate with actual formatters like Black, Prettier, etc.
        formatter = rules.get("formatter")
        if formatter:
            # Check if formatter is configured and run it
            pass

        return warnings

    def update_project_standards(
        self,
        project_path: Union[str, Path],
        language: Optional[str] = None,
        version: Optional[str] = None,
    ) -> bool:
        """Update standards in a project."""
        project_path = Path(project_path)

        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        if language is None:
            languages = self._detect_languages(project_path)
        else:
            languages = [language]

        success = True

        for lang in languages:
            try:
                standard = self.get_standard(lang)
                success &= self._update_language_standards(
                    project_path, lang, standard, version
                )
            except Exception as e:
                logger.error(f"Failed to update {lang} standards: {e}")
                success = False

        return success

    def _update_language_standards(
        self,
        project_path: Path,
        language: str,
        standard: dict[str, Any],
        version: Optional[str] = None,
    ) -> bool:
        """Update standards for a specific language in a project."""
        try:
            # Update configuration files
            self._update_config_files(project_path, language, standard)

            # Update templates
            self._update_templates(project_path, language, standard)

            # Update CI/CD workflows
            self._update_workflows(project_path, language, standard)

            return True
        except Exception as e:
            logger.error(f"Failed to update {language} standards: {e}")
            return False

    def _update_config_files(
        self, project_path: Path, language: str, standard: dict[str, Any]
    ):
        """Update configuration files for a language."""
        config_templates = standard.get("templates", {})

        for config_file, template_content in config_templates.items():
            if config_file.endswith((".toml", ".yaml", ".yml", ".json")):
                target_path = project_path / config_file

                # Create parent directories if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Write the configuration file
                with open(target_path, "w") as f:
                    f.write(template_content)

    def _update_templates(
        self, project_path: Path, language: str, standard: dict[str, Any]
    ):
        """Update template files for a language."""
        # Implementation would copy/update template files
        pass

    def _update_workflows(
        self, project_path: Path, language: str, standard: dict[str, Any]
    ):
        """Update CI/CD workflows for a language."""
        # Implementation would update GitHub Actions, GitLab CI, etc.
        pass
