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

## 🛠️ Installation

### From Source

```bash
git clone https://github.com/sympulse/sympulse-coding-standards.git
cd sympulse-coding-standards
pip install -e .
```

### From PyPI (when published)

```bash
pip install sympulse-coding-standards
```

## 🎯 Quick Start

### 1. Create a new project with standards

```bash
scs init --language python --name my-awesome-project
cd my-awesome-project
```

### 2. Validate existing project against standards

```bash
scs validate --path /path/to/project
```

### 3. Update standards in a project

```bash
scs update --path /path/to/project
```

### 4. Check project compliance

```bash
scs audit --path /path/to/project
```

## 📖 Usage

### CLI Commands

```bash
# Initialize new project
scs init [OPTIONS]

# Validate project against standards
scs validate [OPTIONS]

# Update project standards
scs update [OPTIONS]

# Audit project compliance
scs audit [OPTIONS]

# List available standards
scs list-standards

# Show standards details
scs show-standard <STANDARD_NAME>
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

## 🏗️ Architecture

```plain
sympulse-coding-standards/
├── standards/                 # Core standards definitions
│   ├── python/              # Python-specific standards
│   ├── typescript/          # TypeScript-specific standards
│   └── common/              # Cross-language standards
├── templates/                # Project templates
│   ├── python/              # Python project template
│   ├── typescript/          # TypeScript project template
│   └── mixed/               # Multi-language template
├── validators/               # Standards validation logic
├── generators/               # Project scaffolding
├── cli/                     # Command-line interface
└── workflows/               # CI/CD templates
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

### 3. Projects can update with `scs update`

```bash
# Update to latest standards
scs update --path /path/to/project

# Update to specific version
scs update --path /path/to/project --version 1.2.0
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sympulse_coding_standards

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
- **Team**: <team@sympulse.com>

## 🗺️ Roadmap

- [ ] Go language support
- [ ] Rust language support
- [ ] Docker containerization
- [ ] VS Code extension
- [ ] Standards compliance dashboard
- [ ] Automated migration tools
- [ ] Integration with more CI/CD platforms
