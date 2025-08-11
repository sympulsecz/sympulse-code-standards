# Test Suite for Project Init Command

This directory contains comprehensive tests for the project init command, organized into unit and integration tests with proper fixtures, utilities, and mocks.

## 🚀 Running Tests

### Prerequisites

Install test dependencies:

```bash
poetry install --with dev
```

### Run All Tests

```bash
# Using pytest directly
poetry run pytest

# Using the test runner script
python tests/run_tests.py

# Using poetry
poetry run python tests/run_tests.py
```

### Run Specific Test Categories

```bash
# Unit tests only
poetry run pytest tests/unit/ -v

# Integration tests only
poetry run pytest tests/integration/ -v

# Specific test file
poetry run pytest tests/unit/test_prompts.py -v

# Specific test function
poetry run pytest tests/unit/test_prompts.py::TestProjectConfigurator::test_init -v
```

### Run Tests with Coverage

```bash
# With coverage report
poetry run pytest --cov=src --cov-report=html

# Coverage threshold (fails if below 80%)
poetry run pytest --cov=src --cov-fail-under=80
```

### Run Tests with Markers

```bash
# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Run CLI tests
poetry run pytest -m cli

# Run generator tests
poetry run pytest -m generators
```

## 📊 Test Configuration

The test suite is configured via `pytest.ini` with:

- **Test Discovery**: Automatically finds tests in `tests/` directory
- **Output Format**: Verbose output with short tracebacks
- **Coverage**: Generates HTML and XML coverage reports
- **Markers**: Custom markers for test categorization
- **Environment**: Sets `PYTHONPATH` and `TESTING` variables

## 🔧 Test Development

### Adding New Tests

1. **Unit Tests**: Add to appropriate file in `tests/unit/`
2. **Integration Tests**: Add to `tests/integration/`
3. **Fixtures**: Add to `conftest.py` if shared
4. **Utilities**: Add to `utils.py` if reusable

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Mocking Strategy

- **External Dependencies**: Mock subprocess, file system operations
- **User Input**: Mock Rich prompts and console output
- **Templates**: Use sample template files for realistic testing
- **Isolation**: Each test should be independent and clean

### Assertions

- Use descriptive assertion messages
- Test both positive and negative cases
- Verify file content and structure
- Check mock call counts and arguments

## 🐛 Debugging Tests

### Verbose Output

```bash
poetry run pytest -v -s --tb=long
```

### Debug Specific Test

```bash
poetry run pytest tests/unit/test_prompts.py::TestProjectConfigurator::test_init -v -s --pdb
```

### Check Test Collection

```bash
poetry run pytest --collect-only
```

### Run Tests in Parallel

```bash
poetry run pytest -n auto
```

## 📈 Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **Overall**: 85%+ coverage

## 🧹 Test Cleanup

Tests automatically clean up:

- Temporary project directories
- Mock files and directories
- Subprocess mocks
- Rich prompt mocks

## 🔄 Continuous Integration

The test suite is designed to run in CI/CD pipelines:

- Fast execution (< 30 seconds)
- Deterministic results
- Proper cleanup
- Coverage reporting
- Markdown output for GitHub

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
