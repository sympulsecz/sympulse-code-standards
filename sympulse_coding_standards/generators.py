"""Project generation and scaffolding functionality."""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

import yaml
import toml
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)


@dataclass
class ProjectTemplate:
    """A project template configuration."""

    name: str
    description: str
    languages: List[str]
    structure: Dict[str, Any]
    files: Dict[str, str]  # filename -> template content
    dependencies: Dict[str, List[str]]  # language -> list of deps


class ProjectGenerator:
    """Generates new projects with coding standards."""

    def __init__(self, templates_path: Optional[Union[str, Path]] = None):
        """Initialize the project generator.

        Args:
            templates_path: Path to templates directory. If None, uses default.
        """
        if templates_path is None:
            # Use the templates directory in this package
            package_dir = Path(__file__).parent
            self.templates_path = package_dir / "templates"
        else:
            self.templates_path = Path(templates_path)

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def create_project(
        self,
        path: Union[str, Path],
        language: str,
        template: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """Create a new project with coding standards.

        Args:
            path: Path where to create the project
            language: Programming language for the project
            template: Specific template to use (optional)
            force: Force overwrite existing files

        Returns:
            True if successful, False otherwise
        """
        path = Path(path)

        try:
            # Create project directory
            path.mkdir(parents=True, exist_ok=True)

            # Get template
            if template is None:
                template = self._get_default_template(language)
            else:
                template = self._get_template(template)

            if template is None:
                raise ValueError(f"No template found for language: {language}")

            # Generate project structure
            self._generate_structure(path, template)

            # Generate files
            self._generate_files(path, template, language)

            # Initialize git repository
            self._init_git_repo(path)

            # Install pre-commit hooks
            self._install_pre_commit_hooks(path, language)

            logger.info(f"Project created successfully at {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            if path.exists() and force:
                shutil.rmtree(path)
            return False

    def _get_default_template(self, language: str) -> Optional[ProjectTemplate]:
        """Get the default template for a language."""
        template_dir = self.templates_path / language
        if not template_dir.exists():
            return None

        # Look for default template
        default_template = template_dir / "default"
        if default_template.exists():
            return self._load_template(default_template)

        # Fall back to first available template
        for template_subdir in template_dir.iterdir():
            if template_subdir.is_dir():
                return self._load_template(template_subdir)

        return None

    def _get_template(self, template_name: str) -> Optional[ProjectTemplate]:
        """Get a specific template by name."""
        # Search in all language directories
        for lang_dir in self.templates_path.iterdir():
            if lang_dir.is_dir():
                template_dir = lang_dir / template_name
                if template_dir.exists():
                    return self._load_template(template_dir)

        return None

    def _load_template(self, template_dir: Path) -> ProjectTemplate:
        """Load a template from directory."""
        # Load template configuration
        config_file = template_dir / "template.yaml"
        if not config_file.exists():
            raise ValueError(f"Template configuration not found: {config_file}")

        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Load file templates
        files = {}
        files_dir = template_dir / "files"
        if files_dir.exists():
            for file_path in files_dir.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(files_dir)
                    with open(file_path) as f:
                        files[str(rel_path)] = f.read()

        return ProjectTemplate(
            name=config.get("name", template_dir.name),
            description=config.get("description", ""),
            languages=config.get("languages", []),
            structure=config.get("structure", {}),
            files=files,
            dependencies=config.get("dependencies", {}),
        )

    def _generate_structure(self, path: Path, template: ProjectTemplate):
        """Generate the project directory structure."""
        structure = template.structure

        # Create directories
        for dir_name in structure.get("directories", []):
            dir_path = path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {dir_path}")

        # Create empty files
        for file_name in structure.get("empty_files", []):
            file_path = path / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            logger.debug(f"Created empty file: {file_path}")

    def _generate_files(self, path: Path, template: ProjectTemplate, language: str):
        """Generate project files from templates."""
        for file_path, content in template.files.items():
            try:
                # Render template content
                jinja_template = Template(content)
                rendered_content = jinja_template.render(
                    language=language,
                    project_name=path.name,
                    **self._get_template_vars(language),
                )

                # Create target file
                target_path = path / file_path
                target_path.parent.mkdir(parents=True, exist_ok=True)

                with open(target_path, "w") as f:
                    f.write(rendered_content)

                logger.debug(f"Generated file: {target_path}")

            except Exception as e:
                logger.warning(f"Failed to generate {file_path}: {e}")

    def _get_template_vars(self, language: str) -> Dict[str, Any]:
        """Get template variables for a language."""
        vars = {
            "python": {
                "formatter": "black",
                "linter": "flake8",
                "type_checker": "mypy",
                "test_framework": "pytest",
                "line_length": 88,
                "python_version": "3.11",
            },
            "typescript": {
                "formatter": "prettier",
                "linter": "eslint",
                "type_checker": "typescript",
                "test_framework": "jest",
                "line_length": 80,
                "node_version": "20",
                "es_target": "ES2024",
            },
            "go": {
                "formatter": "gofmt",
                "linter": "golangci-lint",
                "test_framework": "testing",
                "go_version": "1.21",
            },
        }

        return vars.get(language, {})

    def _init_git_repo(self, path: Path):
        """Initialize a git repository."""
        try:
            # Check if git is available
            import subprocess

            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.warning("Git not available, skipping repository initialization")
                return

            # Initialize git repository
            subprocess.run(["git", "init"], cwd=path, check=True)

            # Create initial .gitignore
            gitignore_content = self._get_gitignore_content(path)
            if gitignore_content:
                gitignore_path = path / ".gitignore"
                with open(gitignore_path, "w") as f:
                    f.write(gitignore_content)

            # Create initial commit
            subprocess.run(["git", "add", "."], cwd=path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit with coding standards"],
                cwd=path,
                check=True,
            )

            logger.info("Git repository initialized")

        except Exception as e:
            logger.warning(f"Failed to initialize git repository: {e}")

    def _get_gitignore_content(self, path: Path) -> str:
        """Get appropriate .gitignore content for the project."""
        # Detect project type and return appropriate .gitignore
        if (path / "pyproject.toml").exists():
            return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/
.nox/
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
"""
        elif (path / "package.json").exists():
            return """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production builds
build/
dist/
.next/
out/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
.nyc_output

# TypeScript
*.tsbuildinfo
"""
        else:
            return """# General
.DS_Store
Thumbs.db
*.log
*.tmp
*.temp

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Build artifacts
build/
dist/
target/
"""

    def _install_pre_commit_hooks(self, path: Path, language: str):
        """Install pre-commit hooks for the project."""
        try:
            # Check if pre-commit is available
            import subprocess

            result = subprocess.run(
                ["pre-commit", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.warning("pre-commit not available, skipping hook installation")
                return

            # Install pre-commit hooks
            subprocess.run(["pre-commit", "install"], cwd=path, check=True)

            # Install additional hooks based on language
            if language == "python":
                subprocess.run(
                    ["pre-commit", "install", "--hook-type", "pre-push"],
                    cwd=path,
                    check=True,
                )

            logger.info("Pre-commit hooks installed")

        except Exception as e:
            logger.warning(f"Failed to install pre-commit hooks: {e}")

    def list_templates(self) -> List[Dict[str, Any]]:
        """List available project templates."""
        templates = []

        for lang_dir in self.templates_path.iterdir():
            if lang_dir.is_dir() and not lang_dir.name.startswith("."):
                for template_dir in lang_dir.iterdir():
                    if template_dir.is_dir():
                        try:
                            template = self._load_template(template_dir)
                            templates.append(
                                {
                                    "name": template.name,
                                    "language": lang_dir.name,
                                    "description": template.description,
                                    "path": str(
                                        template_dir.relative_to(self.templates_path)
                                    ),
                                }
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to load template {template_dir}: {e}"
                            )

        return templates
