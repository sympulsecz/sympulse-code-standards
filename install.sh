#!/bin/bash

# Sympulse Coding Standards Installation Script

set -e

echo "🚀 Installing Sympulse Coding Standards..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version+ is required, but you have $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is required but not installed. Please install Poetry first."
    echo "   Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "✅ Poetry detected"

echo "📥 Installing the package..."
poetry install

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
poetry run pre-commit install

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To use the coding standards CLI:"
echo "  poetry run scs --help"
echo ""
echo "To run tests:"
echo "  poetry run pytest"
echo ""
echo "To format code:"
echo "  poetry run black ."
echo "  poetry run isort ."
echo ""
echo "To lint code:"
echo "  poetry run flake8 ."
echo "  poetry run mypy ."
