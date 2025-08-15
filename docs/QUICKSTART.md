# Quick Start Guide

Get up and running with Sympulse Coding Standards in minutes!

## 🚀 Quick Installation

```bash
# Clone the repository
git clone https://github.com/sympulse/sympulse-coding-standards.git
cd sympulse-coding-standards

# Run the installation script
chmod +x install.sh
./install.sh

# Activate the virtual environment
source .venv/bin/activate
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

### Option 4: Use the Installation Script

The included `install.sh` script automatically sets up the environment:

```bash
chmod +x install.sh
./install.sh
```

**Note**: Replace `/path/to/sympulse-coding-standards` with the actual path where you cloned the repository.

## 🎯 Your First Project

### 1. Create a new Python project with standards

```bash
# Create a new Python project
scs project init --language python --name my-awesome-project
cd my-awesome-project

# The project is now set up with:
# - Standardized project structure
# - Pre-commit hooks
# - CI/CD workflows
# - All necessary configuration files
```

### 2. Create a new TypeScript project with standards

```bash
# Create a new TypeScript project
scs project init --language typescript --name my-ts-project
cd my-ts-project

# The project is now set up with:
# - Standardized project structure
# - ESLint and Prettier configuration
# - Jest testing setup
# - CI/CD workflows
```

## 🔍 Validate Existing Projects

### Check if a project follows standards

```bash
# Validate current directory
scs project validate

# Validate specific project
scs project validate --path /path/to/project

# Strict validation (fails on any violations)
scs project validate --strict
```

### Get detailed compliance report

```bash
# Basic audit
scs project audit

# Detailed audit with suggestions
scs project audit --detailed
```

## 🔄 Update Standards

### Update project to latest standards

```bash
# Update current project
scs project update

# Update specific project
scs project update --path /path/to/project

# Update to specific version
scs project update --version 1.2.0
```

## 📋 Available Commands

```bash
# Show all available commands
scs --help

# List available standards
scs standards list

# Show details of a specific standard
scs standards show python

# Initialize new project
scs project init --language python --name project-name

# Validate project
scs project validate [--strict] [--output json]

# Update standards
scs project update [--force]

# Audit compliance
scs project audit [--detailed]
```

## 🛠️ Development Workflow

### 1. Make changes to your code

### 2. Pre-commit hooks automatically run quality checks

### 3. Commit your changes

### 4. CI/CD pipeline validates standards compliance

### 5. Merge when all checks pass

## 📚 What's Included

### Python Standards

- **Formatting**: Black, isort
- **Linting**: flake8, mypy
- **Testing**: pytest with coverage
- **Structure**: Modular architecture
- **CI/CD**: GitHub Actions workflows

### TypeScript Standards

- **Formatting**: Prettier
- **Linting**: ESLint with TypeScript rules
- **Testing**: Jest with coverage
- **Structure**: Modern ES modules
- **CI/CD**: GitHub Actions workflows

### Common Features

- Pre-commit hooks
- Automated testing
- Code coverage reporting
- Security scanning
- Standards compliance validation

## 🆘 Need Help?

- **Documentation**: Check the [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/sympulse/sympulse-coding-standards/issues)
- **Team**: <team@sympulse.com>

## 🎉 You're Ready

You now have a powerful, scalable coding standards system that will help your team maintain consistent, high-quality code across all projects!
