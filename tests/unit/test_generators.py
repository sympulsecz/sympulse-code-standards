"""Unit tests for the ProjectGenerator class."""

import pytest
from unittest.mock import patch

from src.generators import ProjectGenerator, ProjectTemplate


class TestProjectGenerator:
    """Test ProjectGenerator class."""

    def test_init_default_templates_path(self):
        """Test ProjectGenerator initialization with default templates path."""
        generator = ProjectGenerator()
        assert generator.templates_path is not None
        assert "templates" in str(generator.templates_path)

    def test_init_custom_templates_path(self, tmp_path):
        """Test ProjectGenerator initialization with custom templates path."""
        custom_path = tmp_path / "custom-templates"
        generator = ProjectGenerator(templates_path=custom_path)
        assert generator.templates_path == custom_path

    def test_prepare_template_vars(self, mock_config):
        """Test template variable preparation."""
        generator = ProjectGenerator()

        template_vars = generator._prepare_template_vars(
            "python", mock_config, additional_var="test"
        )

        # Check that duplicated keys were removed
        assert "language" not in template_vars
        assert "contributing" not in template_vars
        assert "code_quality" not in template_vars

        # Check that additional variables were added
        assert template_vars["additional_var"] == "test"

        # Check that other config values are preserved
        assert template_vars["name"] == "test-project"
        assert template_vars["description"] == "A test project with coding standards"

    def test_render_template_success(self):
        """Test successful template rendering."""
        generator = ProjectGenerator()
        template_content = "Hello {{ name }}!"
        template_vars = {"name": "World"}

        result = generator._render_template(template_content, **template_vars)
        assert result == "Hello World!"

    def test_render_template_with_author_info(self):
        """Test template rendering with author information."""
        generator = ProjectGenerator()
        template_content = "Author: {{ author_name }}, Email: {{ author_email }}"
        template_vars = {
            "author_name": "John Doe",
            "author_email": "john.doe@example.com",
        }

        result = generator._render_template(template_content, **template_vars)
        assert result == "Author: John Doe, Email: john.doe@example.com"

    @patch("src.generators.yaml.safe_load")
    def test_load_template_success(self, mock_yaml_load, tmp_path):
        """Test successful template loading."""
        mock_yaml_load.return_value = {
            "name": "Test Template",
            "description": "A test template",
            "languages": ["python"],
            "structure": {"directories": ["src"]},
            "dependencies": {"python": ["pytest"]},
            "features": {"contributing_enabled": True},
        }

        # Create mock template directory structure
        template_dir = tmp_path / "test-template"
        template_dir.mkdir()
        (template_dir / "template.yaml").touch()

        generator = ProjectGenerator(tmp_path)
        template = generator._load_template(template_dir)

        assert template.name == "Test Template"
        assert template.description == "A test template"
        assert template.languages == ["python"]
        assert template.structure == {"directories": ["src"]}
        assert template.dependencies == {"python": ["pytest"]}
        assert template.features == {"contributing_enabled": True}

    def test_load_template_missing_config(self, tmp_path):
        """Test template loading with missing configuration file."""
        template_dir = tmp_path / "test-template"
        template_dir.mkdir()
        # No template.yaml file

        generator = ProjectGenerator(tmp_path)

        with pytest.raises(ValueError, match="Template configuration not found"):
            generator._load_template(template_dir)

    def test_get_default_template_python(self, sample_template_files):
        """Test getting default template for Python."""
        generator = ProjectGenerator(sample_template_files)
        template = generator._get_default_template("python")

        assert template is not None
        assert template.name == "Python Project Template"
        assert "python" in template.languages

    def test_get_default_template_not_found(self, tmp_path):
        """Test getting default template for unsupported language."""
        generator = ProjectGenerator(tmp_path)
        template = generator._get_default_template("unsupported")

        assert template is None

    def test_get_template_by_name(self, sample_template_files):
        """Test getting template by name."""
        generator = ProjectGenerator(sample_template_files)
        template = generator._get_template("default")

        assert template is not None
        assert template.name == "Python Project Template"

    def test_get_template_by_name_not_found(self, tmp_path):
        """Test getting template by name when it doesn't exist."""
        generator = ProjectGenerator(tmp_path)
        template = generator._get_template("nonexistent")

        assert template is None

    def test_generate_structure(self, tmp_path):
        """Test project structure generation."""
        generator = ProjectGenerator()
        template = ProjectTemplate(
            name="test",
            description="test",
            languages=["python"],
            structure={
                "directories": ["src", "tests"],
                "empty_files": ["src/__init__.py", "tests/__init__.py"],
            },
            files={},
            dependencies={},
            features={},
        )

        generator._generate_structure(tmp_path, template)

        # Check directories were created
        assert (tmp_path / "src").exists()
        assert (tmp_path / "tests").exists()

        # Check empty files were created
        assert (tmp_path / "src" / "__init__.py").exists()
        assert (tmp_path / "tests" / "__init__.py").exists()

    def test_get_template_vars_python(self, mock_config):
        """Test template variables for Python."""
        generator = ProjectGenerator()
        template_vars = generator._get_template_vars("python", mock_config)

        assert template_vars["formatter"] == "black"
        assert template_vars["linter"] == "flake8"
        assert template_vars["type_checker"] == "mypy"
        assert template_vars["line_length"] == 88
        assert template_vars["python_version"] == "3.11"
        assert template_vars["author_name"] == "Test Author"
        assert template_vars["author_email"] == "test@example.com"

    def test_get_template_vars_unknown_language(self, mock_config):
        """Test template variables for unknown language."""
        generator = ProjectGenerator()
        template_vars = generator._get_template_vars("unknown", mock_config)

        # Should return config as-is for unknown languages
        assert template_vars["name"] == "test-project"
        assert template_vars["language"] == "python"
        assert template_vars["author_name"] == "Test Author"
        assert template_vars["author_email"] == "test@example.com"

    def test_get_template_vars_without_author_info(self):
        """Test template variables when author info is not provided."""
        generator = ProjectGenerator()
        config_without_author = {
            "name": "test-project",
            "language": "python",
            "description": "A test project",
        }

        template_vars = generator._get_template_vars("python", config_without_author)

        # Should use defaults when author/email not provided
        assert template_vars["author_name"] == "Your Name"
        assert template_vars["author_email"] == "your.email@example.com"

    def test_get_template_vars_typescript(self, mock_config):
        """Test template variables for TypeScript."""
        generator = ProjectGenerator()

        # Create a TypeScript-specific config to avoid conflicts with Python defaults
        ts_config = {
            "name": "test-project",
            "language": "typescript",
            "description": "A test project",
            "author": "Test Author",
            "email": "test@example.com",
            "code_quality": {
                "formatter": "prettier",
                "linter": "eslint",
            },
        }

        template_vars = generator._get_template_vars("typescript", ts_config)

        assert template_vars["formatter"] == "prettier"
        assert template_vars["linter"] == "eslint"
        assert template_vars["type_checker"] == "typescript"
        assert template_vars["line_length"] == 80
        assert template_vars["node_version"] == "20"
        assert template_vars["es_target"] == "ES2024"
        assert template_vars["author_name"] == "Test Author"
        assert template_vars["author_email"] == "test@example.com"

    @patch("subprocess.run")
    def test_init_git_repo_success(self, mock_subprocess, tmp_path, mock_config):
        """Test successful git repository initialization."""
        mock_subprocess.return_value.returncode = 0

        generator = ProjectGenerator()
        generator._init_git_repo(tmp_path, mock_config)

        # Check git commands were called
        assert mock_subprocess.call_count >= 3  # git init, add, commit

    @patch("subprocess.run")
    def test_init_git_repo_git_not_available(
        self, mock_subprocess, tmp_path, mock_config
    ):
        """Test git repository initialization when git is not available."""
        mock_subprocess.side_effect = FileNotFoundError("git: command not found")

        generator = ProjectGenerator()
        generator._init_git_repo(tmp_path, mock_config)

        # Should not raise exception, just log warning

    def test_get_gitignore_content_python(self, tmp_path):
        """Test gitignore content for Python project."""
        generator = ProjectGenerator()

        # Create a Python project file
        (tmp_path / "pyproject.toml").touch()

        gitignore_content = generator._get_gitignore_content(tmp_path)

        assert "# Python" in gitignore_content
        assert "__pycache__/" in gitignore_content
        assert (
            "*.py[cod]" in gitignore_content
        )  # This is the actual pattern in the code
        assert ".venv" in gitignore_content

    def test_get_gitignore_content_typescript(self, tmp_path):
        """Test gitignore content for TypeScript project."""
        generator = ProjectGenerator()

        # Create a TypeScript project file
        (tmp_path / "package.json").touch()

        gitignore_content = generator._get_gitignore_content(tmp_path)

        assert "# Dependencies" in gitignore_content
        assert "node_modules/" in gitignore_content
        assert "build/" in gitignore_content
        assert ".env" in gitignore_content

    def test_get_gitignore_content_general(self, tmp_path):
        """Test gitignore content for general project."""
        generator = ProjectGenerator()

        # No specific project files

        gitignore_content = generator._get_gitignore_content(tmp_path)

        assert "# General" in gitignore_content
        assert ".DS_Store" in gitignore_content
        assert "*.log" in gitignore_content

    @patch("subprocess.run")
    def test_install_pre_commit_hooks_success(self, mock_subprocess, tmp_path):
        """Test successful pre-commit hooks installation."""
        mock_subprocess.return_value.returncode = 0

        generator = ProjectGenerator()
        generator._install_pre_commit_hooks(tmp_path, "python")

        # Check pre-commit commands were called
        pre_commit_calls = [
            call for call in mock_subprocess.call_args_list if "pre-commit" in str(call)
        ]
        assert len(pre_commit_calls) >= 2  # install + pre-push

    def test_generate_files_with_author_info(self, tmp_path, mock_config):
        """Test file generation with author information in templates."""
        generator = ProjectGenerator()

        # Create a mock template with author variables
        template = ProjectTemplate(
            name="Test Template",
            description="A test template",
            languages=["python"],
            structure={},
            files={"test.txt": "Author: {{ author_name }}, Email: {{ author_email }}"},
            dependencies={},
            features={},
        )

        # Generate files
        generator._generate_files(tmp_path, template, "python", mock_config)

        # Check that the file was generated with author info
        test_file = tmp_path / "test.txt"
        assert test_file.exists()

        with open(test_file) as f:
            content = f.read()

        assert content == "Author: Test Author, Email: test@example.com"

    def test_create_python_project_with_author_info(self, tmp_path):
        """Test end-to-end Python project creation with author information."""
        generator = ProjectGenerator()

        # Create a simple Python template structure
        template_dir = tmp_path / "templates" / "python" / "default"
        template_dir.mkdir(parents=True)

        # Create template.yaml
        template_config = {
            "name": "Python Project Template",
            "description": "Standard Python project with Sympulse coding standards",
            "languages": ["python"],
            "structure": {
                "directories": ["src", "tests"],
                "empty_files": ["src/__init__.py", "tests/__init__.py"],
            },
            "dependencies": {"python": ["pytest"]},
            "features": {"contributing_enabled": True},
        }

        with open(template_dir / "template.yaml", "w") as f:
            import yaml

            yaml.dump(template_config, f)

        # Create pyproject.toml template
        files_dir = template_dir / "files"
        files_dir.mkdir()

        pyproject_content = """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{{ project_name }}"
version = "0.1.0"
description = "A Python project following Sympulse coding standards"
readme = "README.md"
license = { text = "MIT" }
authors = [{ name = "{{ author_name }}", email = "{{ author_email }}" }]
requires-python = ">=3.11"
dependencies = []
"""

        with open(files_dir / "pyproject.toml", "w") as f:
            f.write(pyproject_content)

        # Create project with author info
        project_path = tmp_path / "test-project"
        config = {
            "name": "test-project",
            "language": "python",
            "description": "A test project",
            "author": "John Doe",
            "email": "john.doe@example.com",
        }

        success = generator.create_project(
            path=project_path, language="python", template="default", config=config
        )

        assert success
        assert project_path.exists()

        # Check that pyproject.toml was generated with author info
        pyproject_file = project_path / "pyproject.toml"
        assert pyproject_file.exists()

        with open(pyproject_file) as f:
            content = f.read()

        assert 'name = "{{ project_name }}"' not in content
        assert 'name = "test-project"' in content
        assert "{{ author_name }}" not in content
        assert "{{ author_email }}" not in content
        assert 'name = "John Doe"' in content
        assert 'email = "john.doe@example.com"' in content

    def test_create_typescript_project_with_author_info(self, tmp_path):
        """Test end-to-end TypeScript project creation with author information."""
        generator = ProjectGenerator(templates_path=tmp_path / "templates")

        # Create a simple TypeScript template structure
        template_dir = tmp_path / "templates" / "typescript" / "default"
        template_dir.mkdir(parents=True)

        # Create template.yaml
        template_config = {
            "name": "TypeScript Project Template",
            "description": "Standard TypeScript project with Sympulse coding standards",
            "languages": ["typescript"],
            "structure": {
                "directories": ["src", "tests"],
                "empty_files": ["src/index.ts", "tests/index.test.ts"],
            },
            "dependencies": {"typescript": ["jest"]},
            "features": {"contributing_enabled": True},
        }

        with open(template_dir / "template.yaml", "w") as f:
            import yaml

            yaml.dump(template_config, f)

        # Create package.json template
        files_dir = template_dir / "files"
        files_dir.mkdir()

        package_json_content = """{
  "name": "{{ project_name }}",
  "version": "0.1.0",
  "description": "A TypeScript project following Sympulse coding standards",
  "author": "{{ author_name }} <{{ author_email }}>",
  "license": "MIT"
}
"""

        with open(files_dir / "package.json", "w") as f:
            f.write(package_json_content)

        # Create project with author info
        project_path = tmp_path / "test-ts-project"
        config = {
            "name": "test-ts-project",
            "language": "typescript",
            "description": "A test TypeScript project",
            "author": "Jane Smith",
            "email": "jane.smith@example.com",
        }

        success = generator.create_project(
            path=project_path, language="typescript", template="default", config=config
        )

        assert success
        assert project_path.exists()

        # Check that package.json was generated with author info
        package_file = project_path / "package.json"
        assert package_file.exists()

        with open(package_file) as f:
            content = f.read()

        assert '"name": "{{ project_name }}"' not in content
        assert '"name": "test-ts-project"' in content
        assert "{{ author_name }}" not in content
        assert "{{ author_email }}" not in content
        assert "Jane Smith" in content
        assert "jane.smith@example.com" in content

    @patch("subprocess.run")
    def test_install_pre_commit_hooks_not_available(self, mock_subprocess, tmp_path):
        """Test pre-commit hooks installation when pre-commit is not available."""
        mock_subprocess.side_effect = FileNotFoundError("pre-commit: command not found")

        generator = ProjectGenerator()
        generator._install_pre_commit_hooks(tmp_path, "python")

        # Should not raise exception, just log warning

    def test_list_templates(self, sample_template_files):
        """Test listing available templates."""
        generator = ProjectGenerator(sample_template_files)
        templates = generator.list_templates()

        assert len(templates) > 0
        assert any(t["name"] == "Python Project Template" for t in templates)
        assert any(t["language"] == "python" for t in templates)


class TestProjectTemplate:
    """Test ProjectTemplate dataclass."""

    def test_project_template_creation(self):
        """Test ProjectTemplate instance creation."""
        template = ProjectTemplate(
            name="Test Template",
            description="A test template",
            languages=["python"],
            structure={"directories": ["src"]},
            files={"README.md": "# Test"},
            dependencies={"python": ["pytest"]},
            features={"contributing_enabled": True},
        )

        assert template.name == "Test Template"
        assert template.description == "A test template"
        assert template.languages == ["python"]
        assert template.structure == {"directories": ["src"]}
        assert template.files == {"README.md": "# Test"}
        assert template.dependencies == {"python": ["pytest"]}
        assert template.features == {"contributing_enabled": True}
