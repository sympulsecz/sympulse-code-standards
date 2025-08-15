"""Project generation and scaffolding functionality."""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Any, Union
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
    languages: list[str]
    structure: dict[str, Any]
    files: dict[str, str]  # filename -> template content
    dependencies: dict[str, list[str]]  # language -> list of deps
    features: dict[str, Any]  # feature flags and configuration


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

    def _prepare_template_vars(
        self, language: str, config: dict[str, Any], **additional_vars
    ) -> dict[str, Any]:
        """Prepare template variables by removing duplicates and adding additional variables.

        Args:
            language: Programming language
            config: Project configuration
            **additional_vars: Additional variables to include

        Returns:
            Cleaned template variables dictionary
        """
        template_vars = self._get_template_vars(language, config)

        # Remove commonly duplicated keys to prevent conflicts
        keys_to_remove = ["language", "contributing", "code_quality"]
        for key in keys_to_remove:
            template_vars.pop(key, None)

        # Add additional variables
        template_vars.update(additional_vars)

        return template_vars

    def _render_template(self, template_content: str, **template_vars) -> str:
        """Render a Jinja2 template with the given variables.

        Args:
            template_content: Raw template content
            **template_vars: Variables to render the template with

        Returns:
            Rendered template content
        """
        try:
            jinja_template = Template(template_content)
            return jinja_template.render(**template_vars)
        except Exception as e:
            logger.warning(f"Failed to render template: {e}")
            return template_content

    def create_project(
        self,
        path: Union[str, Path],
        language: str,
        template: Optional[str] = None,
        force: bool = False,
        config: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Create a new project with coding standards.

        Args:
            path: Path where to create the project
            language: Programming language for the project
            template: Specific template to use (optional)
            force: Force overwrite existing files
            config: Project configuration from interactive prompts

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
            self._generate_files(path, template, language, config)

            # Generate additional files based on configuration
            if config:
                self._generate_configured_files(path, template, language, config)

            # Initialize git repository
            if config and config.get("git_enabled", True):
                self._init_git_repo(path, config)

            # Install pre-commit hooks
            if config and config.get("code_quality", {}).get(
                "pre_commit_enabled", True
            ):
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
            features=config.get("features", {}),
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

    def _generate_files(
        self,
        path: Path,
        template: ProjectTemplate,
        language: str,
        config: Optional[dict[str, Any]] = None,
    ):
        """Generate project files from templates."""
        for file_path, content in template.files.items():
            try:
                # Prepare template variables
                template_vars = self._prepare_template_vars(
                    language, config or {}, project_name=path.name
                )

                # Render template content
                rendered_content = self._render_template(content, **template_vars)

                # Create target file
                target_path = path / file_path
                target_path.parent.mkdir(parents=True, exist_ok=True)

                with open(target_path, "w") as f:
                    f.write(rendered_content)

                logger.debug(f"Generated file: {target_path}")

            except Exception as e:
                logger.warning(f"Failed to generate {file_path}: {e}")

    def _generate_configured_files(
        self,
        path: Path,
        template: ProjectTemplate,
        language: str,
        config: dict[str, Any],
    ):
        """Generate additional files based on configuration."""
        try:
            # Generate CONTRIBUTING.md if enabled
            if config.get("contributing_enabled", False):
                self._generate_contributing_file(path, language, config)

            # Generate CODE_OF_CONDUCT.md if enabled
            if config.get("code_of_conduct_enabled", False):
                self._generate_code_of_conduct_file(path, config)

            # Generate GitHub templates if enabled
            if config.get("issue_templates_enabled", False):
                self._generate_issue_templates(path, config)

            if config.get("pr_templates_enabled", False):
                self._generate_pr_template(path, config)

            # Generate conventional commit template if enabled
            if config.get("git_commit_template", False):
                self._generate_commit_template(path, config)

            # Generate CI/CD configuration if enabled
            if config.get("ci_cd_enabled", False):
                self._generate_ci_cd_config(path, language, config)

            # Generate documentation if enabled
            if config.get("documentation_enabled", False):
                self._generate_documentation_files(path, language, config)

        except Exception as e:
            logger.warning(f"Failed to generate configured files: {e}")

    def _generate_contributing_file(
        self, path: Path, language: str, config: dict[str, Any]
    ):
        """Generate CONTRIBUTING.md file."""
        contributing_template = self.templates_path / "common" / "CONTRIBUTING.md.j2"
        if contributing_template.exists():
            with open(contributing_template) as f:
                template_content = f.read()

            # Prepare template variables
            template_vars = self._prepare_template_vars(
                language,
                config,
                project_name=path.name,
                contributing=config.get("contributing", {}),
                code_quality=config.get("code_quality", {}),
            )

            # Render template
            rendered_content = self._render_template(template_content, **template_vars)

            # Write file
            contributing_path = path / "CONTRIBUTING.md"
            with open(contributing_path, "w") as f:
                f.write(rendered_content)

            logger.debug(f"Generated CONTRIBUTING.md")

    def _generate_code_of_conduct_file(self, path: Path, config: dict[str, Any]):
        """Generate CODE_OF_CONDUCT.md file."""
        coc_template = self.templates_path / "common" / "CODE_OF_CONDUCT.md.j2"
        if coc_template.exists():
            with open(coc_template) as f:
                template_content = f.read()

            # Prepare template variables
            template_vars = self._prepare_template_vars(
                config.get("language", "unknown"), config, project_name=path.name
            )

            # Render template
            rendered_content = self._render_template(template_content, **template_vars)

            # Write file
            coc_path = path / "CODE_OF_CONDUCT.md"
            with open(coc_path, "w") as f:
                f.write(rendered_content)

            logger.debug(f"Generated CODE_OF_CONDUCT.md")

    def _generate_issue_templates(self, path: Path, config: dict[str, Any]):
        """Generate GitHub issue templates."""
        templates_dir = path / ".github" / "ISSUE_TEMPLATE"
        templates_dir.mkdir(parents=True, exist_ok=True)

        # Bug report template
        bug_template = (
            self.templates_path
            / "common"
            / ".github"
            / "ISSUE_TEMPLATE"
            / "bug_report.md.j2"
        )
        if bug_template.exists():
            with open(bug_template) as f:
                template_content = f.read()

            # Prepare template variables
            template_vars = self._prepare_template_vars(
                config.get("language", "unknown"), config, project_name=path.name
            )

            # Render template
            rendered_content = self._render_template(template_content, **template_vars)

            # Write file
            bug_path = templates_dir / "bug_report.md"
            with open(bug_path, "w") as f:
                f.write(rendered_content)

        # Feature request template
        feature_template = (
            self.templates_path
            / "common"
            / ".github"
            / "ISSUE_TEMPLATE"
            / "feature_request.md.j2"
        )
        if feature_template.exists():
            with open(feature_template) as f:
                template_content = f.read()

            # Prepare template variables
            template_vars = self._prepare_template_vars(
                config.get("language", "unknown"), config, project_name=path.name
            )

            # Render template
            rendered_content = self._render_template(template_content, **template_vars)

            # Write file
            feature_path = templates_dir / "feature_request.md"
            with open(feature_path, "w") as f:
                f.write(rendered_content)

        logger.debug(f"Generated issue templates")

    def _generate_pr_template(self, path: Path, config: dict[str, Any]):
        """Generate pull request template."""
        pr_template = (
            self.templates_path / "common" / ".github" / "PULL_REQUEST_TEMPLATE.md.j2"
        )
        if pr_template.exists():
            with open(pr_template) as f:
                template_content = f.read()

            # Prepare template variables
            template_vars = self._prepare_template_vars(
                config.get("language", "unknown"), config, project_name=path.name
            )

            # Render template
            rendered_content = self._render_template(template_content, **template_vars)

            # Write file
            pr_path = path / ".github" / "PULL_REQUEST_TEMPLATE.md"
            pr_path.parent.mkdir(parents=True, exist_ok=True)
            with open(pr_path, "w") as f:
                f.write(rendered_content)

            logger.debug(f"Generated pull request template")

    def _generate_commit_template(self, path: Path, config: dict[str, Any]):
        """Generate conventional commit template."""
        commit_template = self.templates_path / "common" / ".gitmessage.j2"
        if commit_template.exists():
            with open(commit_template) as f:
                template_content = f.read()

            # Prepare template variables
            template_vars = self._prepare_template_vars(
                config.get("language", "unknown"), config
            )

            # Render template
            rendered_content = self._render_template(template_content, **template_vars)

            # Write file
            gitmessage_path = path / ".gitmessage"
            with open(gitmessage_path, "w") as f:
                f.write(rendered_content)

            logger.debug(f"Generated commit template")

    def _generate_ci_cd_config(self, path: Path, language: str, config: dict[str, Any]):
        """Generate CI/CD configuration files."""
        ci_cd_config = config.get("ci_cd", {})
        platform = ci_cd_config.get("platform")

        if platform == "github-actions":
            self._generate_github_actions(path, language, ci_cd_config)
        elif platform == "gitlab-ci":
            self._generate_gitlab_ci(path, language, ci_cd_config)
        # Add other platforms as needed

    def _generate_github_actions(
        self, path: Path, language: str, ci_cd_config: dict[str, Any]
    ):
        """Generate GitHub Actions workflow."""
        workflows_dir = path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Basic CI workflow
        workflow_content = self._get_github_actions_workflow(language, ci_cd_config)
        workflow_path = workflows_dir / "ci.yml"
        with open(workflow_path, "w") as f:
            f.write(workflow_content)

        logger.debug(f"Generated GitHub Actions workflow")

    def _get_github_actions_workflow(
        self, language: str, ci_cd_config: dict[str, Any]
    ) -> str:
        """Get GitHub Actions workflow content."""
        triggers = ci_cd_config.get("triggers", ["push", "pull_request"])
        jobs = ci_cd_config.get("jobs", ["test", "lint"])

        workflow = """name: CI

on:
"""
        for trigger in triggers:
            if trigger == "push":
                workflow += """  push:
    branches: [ main, develop ]
"""
            elif trigger == "pull_request":
                workflow += """  pull_request:
    branches: [ main, develop ]
"""
            elif trigger == "tags":
                workflow += """  tags:
    - 'v*'
"""

        workflow += """
jobs:
"""
        if "test" in jobs:
            workflow += self._get_test_job(language)
        if "lint" in jobs:
            workflow += self._get_lint_job(language)
        if "security" in jobs:
            workflow += self._get_security_job(language)

        return workflow

    def _get_test_job(self, language: str) -> str:
        """Get test job configuration."""
        if language == "python":
            return """  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
"""
        elif language == "typescript":
            return """  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: ["18", "20", "22"]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
    - name: Install dependencies
      run: npm ci
    - name: Run tests
      run: npm test
"""
        else:
            return ""

    def _get_lint_job(self, language: str) -> str:
        """Get lint job configuration."""
        if language == "python":
            return """  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 black isort mypy
    - name: Run linters
      run: |
        flake8 src/ tests/
        black --check src/ tests/
        isort --check-only src/ tests/
        mypy src/
"""
        elif language == "typescript":
            return """  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: "20"
    - name: Install dependencies
      run: npm ci
    - name: Run linters
      run: |
        npm run lint
        npm run type-check
"""
        else:
            return ""

    def _get_security_job(self, language: str) -> str:
        """Get security job configuration."""
        return """  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run security scan
      uses: github/codeql-action/init@v2
      with:
        languages: python
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
"""

    def _generate_documentation_files(
        self, path: Path, language: str, config: dict[str, Any]
    ):
        """Generate documentation files."""
        docs_config = config.get("documentation", {})

        # Generate CHANGELOG.md if enabled
        if docs_config.get("changelog_enabled", False):
            changelog_path = path / "CHANGELOG.md"
            changelog_content = self._get_changelog_content()
            with open(changelog_path, "w") as f:
                f.write(changelog_content)

        # Generate documentation configuration files
        if docs_config.get("generator") == "mkdocs":
            self._generate_mkdocs_config(path, config)
        elif docs_config.get("generator") == "sphinx":
            self._generate_sphinx_config(path, language, config)

    def _get_changelog_content(self) -> str:
        """Get CHANGELOG.md content."""
        return """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0] - YYYY-MM-DD
- Initial release
"""

    def _generate_mkdocs_config(self, path: Path, config: dict[str, Any]):
        """Generate MkDocs configuration."""
        mkdocs_path = path / "mkdocs.yml"
        mkdocs_content = f"""site_name: {path.name}
site_description: {config.get('description', 'Project documentation')}
site_author: {config.get('author', '')}

theme:
  name: material

nav:
  - Home: index.md
  - API: api.md
  - Contributing: contributing.md

markdown_extensions:
  - admonition
  - codehilite
  - pymdownx.superfences
  - pymdownx.tabbed
  - toc:
      permalink: true

plugins:
  - search
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          paths: [src]
"""
        with open(mkdocs_path, "w") as f:
            f.write(mkdocs_content)

    def _get_template_vars(
        self, language: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Get template variables for a language."""
        vars = {
            "python": {
                "formatter": config.get("code_quality", {}).get("formatter", "black"),
                "linter": config.get("code_quality", {}).get("linter", "flake8"),
                "type_checker": config.get("code_quality", {}).get(
                    "type_checker", "mypy"
                ),
                "test_framework": "pytest",
                "line_length": config.get("code_quality", {}).get("line_length", 88),
                "python_version": config.get("code_quality", {}).get(
                    "python_version", "3.11"
                ),
                "poetry_enabled": config.get("code_quality", {}).get(
                    "poetry_enabled", False
                ),
                "author_name": config.get("author", "Your Name"),
                "author_email": config.get("email", "your.email@example.com"),
            },
            "typescript": {
                "formatter": config.get("code_quality", {}).get(
                    "formatter", "prettier"
                ),
                "linter": config.get("code_quality", {}).get("linter", "eslint"),
                "type_checker": "typescript",
                "test_framework": "jest",
                "line_length": config.get("code_quality", {}).get("line_length", 80),
                "node_version": config.get("code_quality", {}).get(
                    "node_version", "20"
                ),
                "es_target": config.get("code_quality", {}).get("es_target", "ES2024"),
                "author_name": config.get("author", "Your Name"),
                "author_email": config.get("email", "your.email@example.com"),
            },
            "go": {
                "formatter": "gofmt",
                "linter": config.get("code_quality", {}).get("linter", "golangci-lint"),
                "test_framework": "testing",
                "go_version": config.get("code_quality", {}).get("go_version", "1.21"),
                "author_name": config.get("author", "Your Name"),
                "author_email": config.get("email", "your.email@example.com"),
            },
        }

        base_vars = vars.get(language, {})
        base_vars.update(config)

        # Ensure author variables are always available, even for unknown languages
        if "author_name" not in base_vars:
            base_vars["author_name"] = config.get("author", "Your Name")
        if "author_email" not in base_vars:
            base_vars["author_email"] = config.get("email", "your.email@example.com")

        return base_vars

    def _init_git_repo(self, path: Path, config: dict[str, Any]):
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

            # Configure commit template if enabled
            if config.get("git_commit_template", False):
                gitmessage_path = path / ".gitmessage"
                if gitmessage_path.exists():
                    subprocess.run(
                        ["git", "config", "commit.template", ".gitmessage"],
                        cwd=path,
                        check=True,
                    )

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

    def list_templates(self) -> list[dict[str, Any]]:
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
