#!/bin/bash

# Sympulse Coding Standards Installation Script

set -e

echo "🚀 Installing Sympulse Coding Standards..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version+ is required, but you have $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install the package in development mode
echo "📥 Installing package in development mode..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To use the coding standards CLI:"
echo "  source .venv/bin/activate"
echo "  scs --help"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To format code:"
echo "  black ."
echo "  isort ."
echo ""
echo "To lint code:"
echo "  flake8 ."
echo "  mypy ."
