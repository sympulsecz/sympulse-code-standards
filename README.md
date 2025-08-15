# Sympulse Coding Standards

A comprehensive, portable coding standards system for the Sympulse team that enforces consistent code quality, formatting, and project structure across multiple languages and repositories.

## 🚀 Features

- **Multi-language Support**: Python, TypeScript, and extensible for more languages
- **Automated Enforcement**: Pre-commit hooks, CI/CD integration, and validation tools
- **Project Scaffolding**: Quick project setup with standardized templates
- **Standards Validation**: Built-in validation against team coding standards
- **Easy Updates**: Version-controlled standards that can be updated incrementally
- **CLI Interface**: Simple `scs` command for all operations

## 📋 What's Included

| Layer | Tools & Standards |
|-------|-------------------|
| **Code Formatting** | dprint, Black, Prettier, Biome |
| **Linting** | Biome, flake8, golangci-lint, ESLint |
| **Testing** | pytest, Jest, standardized test structure |
| **Git Hooks** | pre-commit, Lefthook integration |
| **CI/CD** | GitHub Actions, GitLab CI templates |
| **Documentation** | CONTRIBUTING.md, style guides per language |
| **Project Structure** | Modular architecture, dependency management |

## ��️ Installation

### Prerequisites

- **Python 3.11+** - The installation script will check your Python version
- **Poetry** - For dependency management and virtual environment handling
- **Git** - For cloning the repository
- **Shell access** - For running the installation script

#### Installing Poetry

If you don't have Poetry installed, you can install it using one of these methods:

**Official installer (recommended):**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Using pip:**

```bash
pip install poetry
```

**Using Homebrew (macOS):**

```bash
brew install poetry
```

After installation, you may need to add Poetry to your PATH. See the [official Poetry installation guide](https://python-poetry.org/docs/#installation) for more details.

### From Source

```bash
git clone https://github.com/sympulse/sympulse-coding-standards.git
cd sympulse-coding-standards

# Run the installation script
chmod +x install.sh
./install.sh
```

**Note**: The `install.sh` script automatically:

- Creates a virtual environment (`.venv`)
- Installs the package and all dependencies using Poetry
- Sets up pre-commit hooks

### Alternative: Manual Installation

If you prefer to set up manually, you can use Poetry to manage dependencies:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install using Poetry
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

## 🔗 Making `scs` Available System-Wide

After installation, make the `scs` command available from anywhere on your system:

### Option 1: Add Virtual Environment to PATH

```bash
# Add the virtual environment's bin directory to your PATH
echo 'export PATH="$HOME/path/to/sympulse-coding-standards/.venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Option 2: Create Shell Alias

```bash
# Add alias to your shell configuration (replace with actual path)
echo 'alias scs="source /path/to/sympulse-coding-standards/.venv/bin/activate && scs"' >> ~/.zshrc
source ~/.zshrc
```

### Option 3: Create Symbolic Link

```bash
# Create a symbolic link in a directory that's already in your PATH
ln -s /path/to/sympulse-coding-standards/.venv/bin/scs ~/.local/bin/scs

# Or add ~/.local/bin to PATH if not already there
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Note**: Replace `/path/to/sympulse-coding-standards` with the actual path where you cloned the repository. Poetry automatically creates and manages the virtual environment.

## 🎯 Quick Start

### 1. Create a new project with standards

```bash
scs project init --language python --name my-awesome-project
cd my-awesome-project
```

### 2. Validate existing project against standards

```bash
scs tools validate --path /path/to/project
```

### 3. Update standards in a project

```bash
scs project update --path /path/to/project
```

### 4. Check project compliance

```bash
scs project audit --path /path/to/project
```

## 📖 Usage

### CLI Commands

```bash
# Initialize new project
scs project init [OPTIONS]

# Validate project against standards
scs project validate [OPTIONS]

# Update project standards
scs project update [OPTIONS]

# Audit project compliance
scs project audit [OPTIONS]

# List available standards
scs standards list

# Show standards details
scs standards show <STANDARD_NAME>
```

### Configuration

The system uses a hierarchical configuration approach:

1. **Global Standards** (in this repo)
2. **Language-specific Standards** (Python, TypeScript, etc.)
3. **Project-specific Overrides** (`.scs/config.toml`)

### Example Configuration

```toml
# .scs/config.toml
[standards]
version = "0.1.0"
languages = ["python", "typescript"]

[python]
formatter = "black"
linter = "flake8"
test_framework = "pytest"
line_length = 88

[typescript]
formatter = "prettier"
linter = "eslint"
test_framework = "jest"
```

## 🔧 Standards Enforcement

### Pre-commit Hooks

Automatically installed with:

- Code formatting (Black, Prettier, dprint)
- Linting (flake8, ESLint, Biome)
- Type checking (mypy, TypeScript compiler)
- Test running
- Security scanning

### CI/CD Integration

GitHub Actions workflows that:

- Validate code against standards
- Run tests and quality checks
- Generate compliance reports
- Block merges on violations

### Branch Protection

Automated rules for:

- Required status checks
- Code review requirements
- Commit message formatting
- Branch naming conventions

## 📚 Language Support

### Python

- **Formatter**: Black
- **Linter**: flake8 + plugins
- **Type Checker**: mypy
- **Testing**: pytest
- **Dependencies**: Poetry/pip-tools

### TypeScript

- **Formatter**: Prettier + dprint
- **Linter**: ESLint + Biome
- **Type Checker**: TypeScript compiler
- **Testing**: Jest
- **Build**: tsc, esbuild

### Extending for New Languages

Add new language support by creating:

1. Standards definition in `standards/<language>/`
2. Template in `templates/<language>/`
3. Validator in `validators/<language>.py`
4. Configuration in `standards/<language>/config.toml`

## 🔄 Updating Standards

### 1. Modify standards in this repo

### 2. Version and tag the changes

### 3. Projects can update with `scs project update`

```bash
# Update to latest standards
scs project update --path /path/to/project

# Update to specific version
scs project update --path /path/to/project --version 1.2.0
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_validators.py::test_python_validation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/sympulse/sympulse-coding-standards/issues)
- **Documentation**: [Wiki](https://github.com/sympulse/sympulse-coding-standards/wiki)
