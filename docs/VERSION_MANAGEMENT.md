# Version Management System

The Sympulse Code Standards project includes a centralized version management system that allows you to update versions across all relevant files from a single location.

## Overview

Previously, versions were scattered across multiple files:

- `pyproject.toml`
- `src/standards/python/config.toml`
- `src/standards/typescript/config.toml`
- `src/standards/python/rules.yaml`
- `src/standards/typescript/rules.yaml`
- `install.sh`
- `src/generators.py`
- And more...

Now, all major versions are centralized in `src/versions.toml`, and the system automatically updates all related files when you change a version.

## Central Version Configuration

The main configuration file is located at `src/versions.toml`:

```toml
[versions]
# Project version
project = "0.2.0"

# Python versions
python = "3.13"
python_min = "3.11"
python_target = "py313"

# Node.js versions  
node = "24"
node_min = "22"

# Package versions (major tools)
black = "23.0.0"
isort = "5.12.0"
# ... more tools

# GitHub Actions versions
actions_checkout = "v4"
actions_setup_python = "v4"
# ... more actions
```

## Usage

### CLI Commands (Interactive)

The system provides CLI commands under the `admin` group:

```bash
# Show current versions
scs admin versions show

# Update specific versions
scs admin versions update --python 3.14 --node 26

# Bump versions using semantic versioning
scs admin versions bump python minor
scs admin versions bump project patch

# Validate version consistency
scs admin versions validate

# Dry run to see what would change
scs admin versions update --python 3.14 --dry-run
```

### Standalone Script (Automation)

For CI/CD pipelines and automation, use the standalone script:

```bash
# Update versions
python scripts/update_versions.py --python 3.14 --node 26

# Bump versions
python scripts/update_versions.py --bump python minor
python scripts/update_versions.py --bump project patch

# Validate
python scripts/update_versions.py --validate

# Show current versions
python scripts/update_versions.py --show

# Dry run
python scripts/update_versions.py --python 3.14 --dry-run

# Quiet mode for automation
python scripts/update_versions.py --python 3.14 --quiet
```

### Programmatic Usage

You can also use the VersionManager class directly in Python code:

```python
from src.version_manager import VersionManager

manager = VersionManager()

# Update Python version
manager.update_python_version("3.14")

# Update Node.js version
manager.update_node_version("26")

# Update project version
manager.update_project_version("0.3.0")

# Update multiple versions at once
manager.update_all_versions(python="3.14", node="26")

# Show current versions
manager.show_current_versions()

# Validate versions
errors = manager.validate_versions()
```

## What Gets Updated

When you update a version, the system automatically updates:

### Python Version Updates

- `src/versions.toml` - Central configuration
- `pyproject.toml` - Project configuration
- `src/standards/python/config.toml` - Python standards config
- `src/standards/python/rules.yaml` - Python rules
- `install.sh` - Installation script
- `src/generators.py` - GitHub Actions templates

### Node.js Version Updates

- `src/versions.toml` - Central configuration
- `src/standards/typescript/config.toml` - TypeScript standards config
- `src/standards/typescript/rules.yaml` - TypeScript rules
- `src/generators.py` - GitHub Actions templates

### Project Version Updates

- `src/versions.toml` - Central configuration
- `src/standards/config.toml` - Standards config
- `src/__init__.py` - Package version

## Version Validation

The system includes validation to ensure version consistency:

- Python version must be >= minimum Python version
- Node.js version must be >= minimum Node.js version
- All version formats are validated

## Safety Features

- **Dry Run Mode**: Use `--dry-run` to see what would change without making changes
- **Confirmation Prompts**: CLI commands ask for confirmation before making changes
- **Validation**: Automatic validation after updates
- **Error Handling**: Graceful error handling with informative messages

## Automation Workflows

### CI/CD Pipeline Example

```yaml
# .github/workflows/bump-versions.yml
name: Bump Versions

on:
  workflow_dispatch:
    inputs:
      python_version:
        description: 'New Python version'
        required: false
        default: ''
      node_version:
        description: 'New Node.js version'
        required: false
        default: ''

jobs:
  bump-versions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Bump versions
        run: |
          python scripts/update_versions.py \
            --python ${{ inputs.python_version }} \
            --node ${{ inputs.node_version }} \
            --quiet
      
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "Bump versions"
          title: "Bump versions"
          body: "Automated version bump"
```

### Release Workflow Example

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  bump-project-version:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Extract version from tag
        id: get_version
        run: echo "version=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT
      
      - name: Update project version
        run: |
          python scripts/update_versions.py \
            --project ${{ steps.get_version.outputs.version }} \
            --quiet
      
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Bump project version to ${{ steps.get_version.outputs.version }}"
          git push
```

## Best Practices

1. **Always use dry-run first**: Test your changes before applying them
2. **Update versions incrementally**: Don't jump multiple major versions at once
3. **Validate after updates**: Use the validation command to check consistency
4. **Commit changes separately**: Keep version updates in their own commits
5. **Test generated projects**: After updating versions, test that new projects work correctly

## Troubleshooting

### Common Issues

1. **File not found errors**: Ensure all files listed in `src/versions.toml` exist
2. **Permission errors**: Make sure you have write access to all project files
3. **Version format errors**: Check that version strings match expected formats

### Debug Mode

For debugging, you can examine what the system is doing:

```python
from src.version_manager import VersionManager

manager = VersionManager()
print(manager.versions)  # See current configuration
print(manager.versions["file_patterns"])  # See file patterns
```

## Contributing

When adding new files that contain version information:

1. Add the file path to the appropriate section in `src/versions.toml`
2. Update the `VersionManager` class to handle the new file type
3. Add tests for the new functionality
4. Update this documentation

## Security Considerations

- The version management system modifies multiple files
- Always review changes before committing
- Use dry-run mode in automated workflows
- Consider using branch protection rules for version updates
