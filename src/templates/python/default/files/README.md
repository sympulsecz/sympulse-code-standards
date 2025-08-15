# {{ project_name }}

A Python project following Sympulse coding standards.

## Description

Brief description of your project goes here.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{{ project_name }}.git
cd {{ project_name }}

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Usage

```python
from {{ project_name }} import main

# Your usage examples here
```

## Development

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

### Running Quality Checks

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Run linter
flake8 src/ tests/

# Run type checker
mypy src/

# Run tests
pytest

# Run all checks
pre-commit run --all-files
```

### Pre-commit Hooks

Pre-commit hooks are automatically installed and will run on every commit to ensure code quality.

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src/{{ project_name }}

# Run specific test file
pytest tests/test_example.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Standards Compliance

This project follows Sympulse coding standards. To validate compliance:

```bash
scs project validate
```

To update to the latest standards:

```bash
scs project update
```
