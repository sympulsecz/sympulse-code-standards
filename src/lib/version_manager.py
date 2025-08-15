"""Version management system for Sympulse Code Standards."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import tomllib
import tomli_w

from rich.console import Console
from rich.table import Table


class VersionManager:
    """Manages versions across the entire project."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the version manager.

        Args:
            project_root: Root directory of the project. Defaults to current working directory.
        """
        self.project_root = project_root or Path.cwd()
        self.versions_file = self.project_root / "src" / "versions.toml"
        self.console = Console()

        if not self.versions_file.exists():
            raise FileNotFoundError(f"Versions file not found: {self.versions_file}")

        self.versions = self._load_versions()

    def _load_versions(self) -> Dict[str, Any]:
        """Load the central versions configuration."""
        with open(self.versions_file, "rb") as f:
            return tomllib.load(f)

    def _save_versions(self) -> None:
        """Save the current versions configuration."""
        with open(self.versions_file, "wb") as f:
            tomli_w.dump(self.versions, f)

    def get_version(self, key: str) -> str:
        """Get a specific version by key."""
        return self.versions["versions"].get(key, "")

    def set_version(self, key: str, value: str) -> None:
        """Set a specific version by key."""
        self.versions["versions"][key] = value
        self._save_versions()

    def update_python_version(self, version: str) -> None:
        """Update Python version across all relevant files.

        Args:
            version: New Python version (e.g., "3.14")
        """
        self.console.print(f"🔄 Updating Python version to {version}")

        # Update central config
        self.set_version("python", version)

        # Calculate target version (e.g., "3.14" -> "py314")
        target_version = f"py{version.replace('.', '')}"
        self.set_version("python_target", target_version)

        # Update files
        self._update_python_configs(version, target_version)
        self._update_python_classifiers(version)
        self._update_install_script(version)
        self._update_generators(version, "python")

        self.console.print(f"✅ Python version updated to {version}")

    def update_node_version(self, version: str) -> None:
        """Update Node.js version across all relevant files.

        Args:
            version: New Node.js version (e.g., "26")
        """
        self.console.print(f"🔄 Updating Node.js version to {version}")

        # Update central config
        self.set_version("node", version)

        # Update files
        self._update_typescript_configs(version)
        self._update_generators(version, "node")

        self.console.print(f"✅ Node.js version updated to {version}")

    def update_project_version(self, version: str) -> None:
        """Update project version across all relevant files.

        Args:
            version: New project version (e.g., "0.3.0")
        """
        self.console.print(f"🔄 Updating project version to {version}")

        # Update central config
        self.set_version("project", version)

        # Update files
        self._update_project_configs(version)

        self.console.print(f"✅ Project version updated to {version}")

    def _calculate_python_versions_to_support(self, version: str) -> List[str]:
        """Calculate the three Python versions to support.
        
        Args:
            version: New Python version (e.g., "3.14")
            
        Returns:
            List of Python versions to support (e.g., ["3.12", "3.13", "3.14"])
        """
        try:
            major, minor = map(int, version.split("."))
            versions_to_support = []
            
            # Add the new version
            versions_to_support.append(f"{major}.{minor}")
            
            # Add two previous versions
            if minor >= 2:
                versions_to_support.append(f"{major}.{minor - 1}")
            if minor >= 3:
                versions_to_support.append(f"{major}.{minor - 2}")
            elif minor >= 1:
                versions_to_support.append(f"{major}.{minor - 1}")
            
            # Ensure we have at least 3 versions, add more previous if needed
            while len(versions_to_support) < 3:
                if minor > 0:
                    minor -= 1
                    versions_to_support.append(f"{major}.{minor}")
                else:
                    major -= 1
                    minor = 9
                    if major >= 3:
                        versions_to_support.append(f"{major}.{minor}")
                    else:
                        break
            
            # Sort versions to ensure they're in ascending order
            versions_to_support.sort(key=lambda v: tuple(map(int, v.split("."))))
            
            return versions_to_support
            
        except ValueError as e:
            self.console.print(f"❌ Error parsing Python version {version}: {e}")
            return []

    def _update_python_configs(self, version: str, target_version: str) -> None:
        """Update Python configuration files."""
        files = self.versions["file_patterns"]["python_configs"]

        for file_path in files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.console.print(f"⚠️  File not found: {file_path}")
                continue

            self._update_file_content(
                full_path,
                [
                    (r'python_version\s*=\s*"[^"]*"', f'python_version = "{version}"'),
                    (
                        r"target_version\s*=\s*\[[^\]]*\]",
                        f'target_version = ["{target_version}"]',
                    ),
                    (
                        r"target-version\s*=\s*\[[^\]]*\]",
                        f'target-version = ["{target_version}"]',
                    ),
                    (
                        r'min_python_version:\s*"[^"]*"',
                        f'min_python_version: "{version}"',
                    ),
                ],
            )

    def _update_typescript_configs(self, version: str) -> None:
        """Update TypeScript configuration files."""
        files = self.versions["file_patterns"]["typescript_configs"]

        for file_path in files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.console.print(f"⚠️  File not found: {file_path}")
                continue

            self._update_file_content(
                full_path,
                [
                    (r'node_version\s*=\s*"[^"]*"', f'node_version = "{version}"'),
                    (r'min_node_version:\s*"[^"]*"', f'min_node_version: "{version}"'),
                ],
            )

    def _update_project_configs(self, version: str) -> None:
        """Update project configuration files."""
        files = self.versions["file_patterns"]["project_configs"]

        for file_path in files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.console.print(f"⚠️  File not found: {file_path}")
                continue

            if file_path.endswith(".toml"):
                # For toml files, we need to be more specific about which version field to update
                if file_path == "pyproject.toml":
                    # Main project version in pyproject.toml (not at beginning of file)
                    self._update_file_content(
                        full_path,
                        [(r'^version\s*=\s*"[^"]*"', f'version = "{version}"')],
                    )
                elif file_path in [
                    "src/standards/python/config.toml",
                    "src/standards/typescript/config.toml",
                ]:
                    # Standards config version (not python_version or node_version)
                    self._update_file_content(
                        full_path,
                        [(r'^version\s*=\s*"[^"]*"', f'version = "{version}"')],
                    )
                else:
                    # Other toml files
                    self._update_file_content(
                        full_path,
                        [(r'^version\s*=\s*"[^"]*"', f'version = "{version}"')],
                    )
            elif file_path.endswith(".py"):
                self._update_file_content(
                    full_path,
                    [(r'__version__\s*=\s*"[^"]*"', f'__version__ = "{version}"')],
                )
            elif file_path.endswith(".json"):
                self._update_file_content(
                    full_path,
                    [(r'"version":\s*"[^"]*"', f'"version": "{version}"')],
                )

    def _update_install_script(self, version: str) -> None:
        """Update the install.sh script."""
        install_path = self.project_root / "install.sh"
        if not install_path.exists():
            self.console.print("⚠️  install.sh not found")
            return

        self._update_file_content(
            install_path,
            [(r'required_version="[^"]*"', f'required_version="{version}"')],
        )

    def _update_generators(self, version: str, version_type: str = "python") -> None:
        """Update the generators.py file.

        Args:
            version: New version string
            version_type: Type of version being updated ("python" or "node")
        """
        generators_path = self.project_root / "src" / "generators.py"
        if not generators_path.exists():
            self.console.print("⚠️  generators.py not found")
            return

        try:
            # Read the file content first
            content = generators_path.read_text()
            original_content = content

            if version_type == "python":
                # Calculate the three Python versions to support (same logic as classifiers)
                versions_to_support = self._calculate_python_versions_to_support(version)
                if not versions_to_support:
                    return
                
                self.console.print(f"📋 CI will test Python versions: {', '.join(versions_to_support)}")
                
                # Update Python versions in GitHub Actions matrix
                content = self._update_ci_matrix_versions(
                    content, "python-version", versions_to_support
                )

                # Update specific Python version references (like in lint job)
                content = re.sub(
                    r'python-version:\s*"[^"]*"', f'python-version: "{version}"', content
                )
                
            elif version_type == "node":
                # Update Node.js versions in GitHub Actions matrix
                # Find the current Node.js version array and update it intelligently
                node_matrix_match = re.search(r"node-version:\s*\[([^\]]*)\]", content)
                if node_matrix_match:
                    current_versions = node_matrix_match.group(1)
                    # Extract current versions and replace the last one with the new version
                    version_list = [
                        v.strip().strip("\"'") for v in current_versions.split(",")
                    ]
                    if version_list:
                        # Keep the first few versions but replace the last one
                        if len(version_list) >= 2:
                            # Keep 18, 20 and replace the last one
                            new_versions = version_list[:-1] + [f'"{version}"']
                        else:
                            # If we have fewer versions, just add the new one
                            new_versions = version_list + [f'"{version}"']

                        new_matrix = f'node-version: [{", ".join(new_versions)}]'
                        content = re.sub(r"node-version:\s*\[[^\]]*\]", new_matrix, content)

                # Update specific Node.js version references
                content = re.sub(
                    r'node-version:\s*"[^"]*"', f'node-version: "{version}"', content
                )

            # Only write if content has changed
            if content != original_content:
                generators_path.write_text(content)
                self.console.print(
                    f"✅ Updated generators.py for {version_type} version {version}"
                )
            else:
                self.console.print(
                    f"ℹ️  No changes needed in generators.py for {version_type} version {version}"
                )

        except Exception as e:
            self.console.print(f"❌ Error updating generators.py: {e}")

    def _update_ci_matrix_versions(self, content: str, matrix_key: str, versions: List[str]) -> str:
        """Update CI matrix versions for a given key.
        
        Args:
            content: File content to update
            matrix_key: Matrix key (e.g., "python-version", "node-version")
            versions: List of versions to use
            
        Returns:
            Updated content
        """
        matrix_match = re.search(f"{matrix_key}:\\s*\\[([^\\]]*)\\]", content)
        if matrix_match:
            # Replace with our calculated versions
            new_versions = [f'"{v}"' for v in versions]
            new_matrix = f'{matrix_key}: [{", ".join(new_versions)}]'
            content = re.sub(f"{matrix_key}:\\s*\\[[^\\]]*\\]", new_matrix, content)
        
        return content

    def _update_file_content(
        self, file_path: Path, patterns: List[Tuple[str, str]]
    ) -> None:
        """Update file content using regex patterns.

        Args:
            file_path: Path to the file to update
            patterns: List of (regex_pattern, replacement) tuples
        """
        try:
            content = file_path.read_text()
            original_content = content

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                file_path.write_text(content)
                self.console.print(f"✅ Updated {file_path}")
            else:
                self.console.print(f"ℹ️  No changes needed in {file_path}")

        except Exception as e:
            self.console.print(f"❌ Error updating {file_path}: {e}")

    def show_current_versions(self) -> None:
        """Display current versions in a nice table."""
        table = Table(title="Current Versions")
        table.add_column("Component", style="cyan")
        table.add_column("Version", style="green")

        versions = self.versions["versions"]

        # Group versions by category
        categories = {
            "Project": ["project"],
            "Python": ["python", "python_min", "python_target"],
            "Node.js": ["node", "node_min"],
            "Tools": [
                "black",
                "isort",
                "flake8",
                "mypy",
                "pytest",
                "prettier",
                "eslint",
                "jest",
                "typescript",
            ],
            "GitHub Actions": [
                "actions_checkout",
                "actions_setup_python",
                "actions_setup_node",
                "codeql_init",
                "codeql_analyze",
            ],
        }

        for category, keys in categories.items():
            for key in keys:
                if key in versions:
                    table.add_row(key.replace("_", " ").title(), versions[key])
            if category != "GitHub Actions":  # Add separator between categories
                table.add_row("", "")

        self.console.print(table)

    def validate_versions(self) -> List[str]:
        """Validate that all version references are consistent.

        Returns:
            List of validation errors
        """
        errors = []
        versions = self.versions["versions"]

        # Check Python version consistency
        python_version = versions.get("python", "")
        python_min = versions.get("python_min", "")

        if python_version and python_min:
            try:
                if tuple(map(int, python_version.split("."))) < tuple(
                    map(int, python_min.split("."))
                ):
                    errors.append(
                        f"Python version {python_version} is below minimum {python_min}"
                    )
            except ValueError:
                errors.append("Invalid Python version format")

        # Check Node.js version consistency
        node_version = versions.get("node", "")
        node_min = versions.get("node_min", "")

        if node_version and node_min:
            try:
                if int(node_version) < int(node_min):
                    errors.append(
                        f"Node.js version {node_version} is below minimum {node_min}"
                    )
            except ValueError:
                errors.append("Invalid Node.js version format")

        return errors

    def update_all_versions(self, **kwargs: str) -> None:
        """Update multiple versions at once.

        Args:
            **kwargs: Version updates (e.g., python="3.14", node="26")
        """
        for key, value in kwargs.items():
            if key == "python":
                self.update_python_version(value)
            elif key == "node":
                self.update_node_version(value)
            elif key == "project":
                self.update_project_version(value)
            else:
                self.console.print(f"⚠️  Unknown version key: {key}")

        # Validate after updates
        errors = self.validate_versions()
        if errors:
            self.console.print("⚠️  Validation warnings:")
            for error in errors:
                self.console.print(f"  - {error}")
        else:
            self.console.print("✅ All versions updated successfully")

    def _update_python_classifiers(self, version: str) -> None:
        """Update Python classifiers in pyproject.toml and templates.
        
        Args:
            version: New Python version (e.g., "3.14")
        """
        # Calculate the three Python versions to support
        versions_to_support = self._calculate_python_versions_to_support(version)
        if not versions_to_support:
            return
            
        self.console.print(f"📋 Supporting Python versions: {', '.join(versions_to_support)}")
        
        # Update main pyproject.toml
        self._update_pyproject_classifiers(versions_to_support)
        
        # Update Python template config
        self._update_python_template_classifiers(versions_to_support)
        
        # Update CI configurations in templates
        self._update_ci_configurations(versions_to_support)

    def _update_pyproject_classifiers(self, versions: List[str]) -> None:
        """Update Python classifiers in the main pyproject.toml file.
        
        Args:
            versions: List of Python versions to support (e.g., ["3.11", "3.12", "3.13"])
        """
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            self.console.print("⚠️  pyproject.toml not found")
            return
        
        self._update_classifiers_in_file(pyproject_path, versions, "pyproject.toml")

    def _update_python_template_classifiers(self, versions: List[str]) -> None:
        """Update Python classifiers in the Python template config.
        
        Args:
            versions: List of Python versions to support (e.g., ["3.11", "3.12", "3.13"])
        """
        # Update the Python template's pyproject.toml.j2 if it exists
        template_pyproject = self.project_root / "src" / "templates" / "python" / "default" / "files" / "pyproject.toml"
        if template_pyproject.exists():
            self._update_classifiers_in_file(template_pyproject, versions, "template pyproject.toml")

    def _update_classifiers_in_file(self, file_path: Path, versions: List[str], file_description: str) -> None:
        """Update Python classifiers in a given file.
        
        Args:
            file_path: Path to the file to update
            versions: List of Python versions to support
            file_description: Description of the file for logging
        """
        try:
            content = file_path.read_text()
            original_content = content
            
            # Update the Programming Language :: Python :: 3.x classifiers
            for version in versions:
                classifier = f'  "Programming Language :: Python :: {version}",'
                if classifier not in content:
                    # Find the last Python classifier and add after it
                    last_classifier_match = re.search(
                        r'(\s+"Programming Language :: Python :: [^"]+",\s*\n)',
                        content
                    )
                    if last_classifier_match:
                        # Add the new classifier after the last one
                        content = re.sub(
                            r'(\s+"Programming Language :: Python :: [^"]+",\s*\n)',
                            r'\1' + classifier + '\n',
                            content,
                            count=1
                        )
                    else:
                        # If no existing classifiers, add after the classifiers line
                        classifiers_match = re.search(r'(classifiers\s*=\s*\[)', content)
                        if classifiers_match:
                            content = re.sub(
                                r'(classifiers\s*=\s*\[)',
                                r'\1\n' + classifier,
                                content
                            )
            
            # Remove outdated classifiers that are not in our supported versions
            # Find all Programming Language :: Python :: 3.x classifiers
            classifier_pattern = r'\s+"Programming Language :: Python :: 3\.\d+",\s*\n'
            existing_classifiers = re.findall(classifier_pattern, content)
            
            for classifier_match in existing_classifiers:
                # Extract version from classifier
                version_match = re.search(r'3\.(\d+)', classifier_match)
                if version_match:
                    classifier_version = f"3.{version_match.group(1)}"
                    if classifier_version not in versions:
                        # Remove this classifier
                        content = content.replace(classifier_match, '')
            
            # Clean up any double newlines that might have been created
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            if content != original_content:
                file_path.write_text(content)
                self.console.print(f"✅ Updated Python classifiers in {file_description}")
            else:
                self.console.print(f"ℹ️  No changes needed in {file_description} classifiers")
                
        except Exception as e:
            self.console.print(f"❌ Error updating {file_description} classifiers: {e}")

    def _update_ci_configurations(self, versions: List[str]) -> None:
        """Update CI configurations in templates to use the correct Python versions.
        
        Args:
            versions: List of Python versions to support (e.g., ["3.11", "3.12", "3.13"])
        """
        # Update the Python template's CI configuration
        ci_template_path = self.project_root / "src" / "templates" / "python" / "default" / "files" / ".github" / "workflows" / "ci.yml"
        if ci_template_path.exists():
            try:
                content = ci_template_path.read_text()
                original_content = content
                
                # Update the Python version matrix in the CI configuration
                content = self._update_ci_matrix_versions(content, "python-version", versions)
                
                # Also update the specific Python version used in other jobs
                latest_version = versions[-1]  # Use the latest version for other jobs
                content = re.sub(
                    r'python-version:\s*"[^"]*"', f'python-version: "{latest_version}"', content
                )
                
                if content != original_content:
                    ci_template_path.write_text(content)
                    self.console.print("✅ Updated CI configuration in Python template")
                else:
                    self.console.print("ℹ️  No changes needed in CI configuration")
                    
            except Exception as e:
                self.console.print(f"❌ Error updating CI configuration: {e}")
