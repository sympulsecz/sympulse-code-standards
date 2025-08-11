# Quick Start Guide

Get up and running with Sympulse Coding Standards in minutes!

## 🚀 Quick Installation

### Option 1: Install from source (recommended for development)

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

### Option 2: Install with pip

```bash
pip install sympulse-coding-standards
```

## 🎯 Your First Project

### 1. Create a new Python project with standards

```bash
# Create a new Python project
scs init --language python --name my-awesome-project
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
scs init --language typescript --name my-ts-project
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
scs validate

# Validate specific project
scs validate --path /path/to/project

# Strict validation (fails on any violations)
scs validate --strict
```

### Get detailed compliance report

```bash
# Basic audit
scs audit

# Detailed audit with suggestions
scs audit --detailed
```

## 🔄 Update Standards

### Update project to latest standards

```bash
# Update current project
scs update

# Update specific project
scs update --path /path/to/project

# Update to specific version
scs update --version 1.2.0
```

## 📋 Available Commands

```bash
# Show all available commands
scs --help

# List available standards
scs list-standards

# Show details of a specific standard
scs show-standard python

# Initialize new project
scs init --language python --name project-name

# Validate project
scs validate [--strict] [--output json]

# Update standards
scs update [--force]

# Audit compliance
scs audit [--detailed]
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
