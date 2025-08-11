"""Standards validation functionality."""

import re
import ast
import logging
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """A validation issue found during standards checking."""

    severity: str  # "error", "warning", "suggestion"
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    rule_id: Optional[str] = None


class BaseValidator:
    """Base class for language-specific validators."""

    def __init__(self, rules: dict[str, Any]):
        """Initialize validator with rules."""
        self.rules = rules

    def validate(self, project_path: Path) -> list[ValidationIssue]:
        """Validate a project against standards."""
        raise NotImplementedError("Subclasses must implement validate method")


class PythonValidator(BaseValidator):
    """Python-specific standards validator."""

    def validate(self, project_path: Path) -> list[ValidationIssue]:
        """Validate Python project against standards."""
        issues = []

        # Check file structure
        issues.extend(self._check_file_structure(project_path))

        # Check Python files
        python_files = list(project_path.rglob("*.py"))
        for py_file in python_files:
            if not self._should_skip_file(py_file):
                issues.extend(self._validate_python_file(py_file))

        # Check configuration files
        issues.extend(self._check_config_files(project_path))

        return issues

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a file should be skipped during validation."""
        skip_patterns = [
            r"__pycache__",
            r"\.venv",
            r"venv",
            r"env",
            r"\.git",
            r"build",
            r"dist",
            r"\.tox",
            r"\.pytest_cache",
        ]

        file_str = str(file_path)
        return any(re.search(pattern, file_str) for pattern in skip_patterns)

    def _check_file_structure(self, project_path: Path) -> list[ValidationIssue]:
        """Check project file structure."""
        issues = []
        structure_rules = self.rules.get("file_structure", {})

        # Check required directories
        required_dirs = structure_rules.get("required_directories", [])
        for required_dir in required_dirs:
            dir_path = project_path / required_dir
            if not dir_path.exists():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"Missing required directory: {required_dir}",
                        rule_id="file_structure.missing_directory",
                    )
                )

        # Check required files
        required_files = structure_rules.get("required_files", [])
        for required_file in required_files:
            file_path = project_path / required_file
            if not file_path.exists():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"Missing required file: {required_file}",
                        rule_id="file_structure.missing_file",
                    )
                )

        return issues

    def _validate_python_file(self, file_path: Path) -> list[ValidationIssue]:
        """Validate a single Python file."""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"Syntax error: {e.msg}",
                        file_path=str(file_path),
                        line_number=e.lineno,
                        column=e.offset or 0,
                        rule_id="python.syntax_error",
                    )
                )
                return issues

            # Check naming conventions
            issues.extend(self._check_naming_conventions(tree, file_path))

            # Check imports
            issues.extend(self._check_imports(tree, file_path))

            # Check function/class structure
            issues.extend(self._check_code_structure(tree, file_path))

        except Exception as e:
            logger.warning(f"Failed to validate {file_path}: {e}")
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message=f"Failed to validate file: {e}",
                    file_path=str(file_path),
                    rule_id="python.validation_error",
                )
            )

        return issues

    def _check_naming_conventions(
        self, tree: ast.AST, file_path: Path
    ) -> list[ValidationIssue]:
        """Check Python naming conventions."""
        issues = []
        naming_rules = self.rules.get("naming", {})

        # Check module naming
        module_pattern = naming_rules.get("modules", r"^[a-z_][a-z0-9_]*$")
        if module_pattern and not re.match(module_pattern, file_path.stem):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message=f"Module name '{file_path.stem}' doesn't follow convention: {module_pattern}",
                    file_path=str(file_path),
                    rule_id="python.naming.module_convention",
                )
            )

        # Check class naming
        class_pattern = naming_rules.get("classes", r"^[A-Z][a-zA-Z0-9]*$")
        if class_pattern:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if not re.match(class_pattern, node.name):
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                message=f"Class name '{node.name}' doesn't follow convention: {class_pattern}",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                rule_id="python.naming.class_convention",
                            )
                        )

        # Check function naming
        function_pattern = naming_rules.get("functions", r"^[a-z_][a-z0-9_]*$")
        if function_pattern:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not re.match(function_pattern, node.name):
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                message=f"Function name '{node.name}' doesn't follow convention: {function_pattern}",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                rule_id="python.naming.function_convention",
                            )
                        )

        # Check constant naming
        constant_pattern = naming_rules.get("constants", r"^[A-Z][A-Z0-9_]*$")
        if constant_pattern:
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Check if it's a constant (all caps)
                            if target.id.isupper() and not re.match(
                                constant_pattern, target.id
                            ):
                                issues.append(
                                    ValidationIssue(
                                        severity="warning",
                                        message=f"Constant name '{target.id}' doesn't follow convention: {constant_pattern}",
                                        file_path=str(file_path),
                                        line_number=node.lineno,
                                        rule_id="python.naming.constant_convention",
                                    )
                                )

        return issues

    def _check_imports(self, tree: ast.AST, file_path: Path) -> list[ValidationIssue]:
        """Check import statements."""
        issues = []
        import_rules = self.rules.get("imports", {})

        # Check import order
        import_order = import_rules.get("order", ["stdlib", "third_party", "local"])
        if import_order:
            issues.extend(self._check_import_order(tree, file_path, import_order))

        # Check unused imports
        if import_rules.get("check_unused", True):
            issues.extend(self._check_unused_imports(tree, file_path))

        return issues

    def _check_import_order(
        self, tree: ast.AST, file_path: Path, expected_order: list[str]
    ) -> list[ValidationIssue]:
        """Check that imports follow the expected order."""
        issues = []

        # This is a simplified check - in practice, you'd need more sophisticated logic
        # to categorize imports as stdlib, third_party, or local

        return issues

    def _check_unused_imports(
        self, tree: ast.AST, file_path: Path
    ) -> list[ValidationIssue]:
        """Check for unused imports."""
        issues = []

        # This is a simplified check - in practice, you'd use tools like pyflakes
        # or integrate with existing linters

        return issues

    def _check_code_structure(
        self, tree: ast.AST, file_path: Path
    ) -> list[ValidationIssue]:
        """Check code structure and organization."""
        issues = []
        structure_rules = self.rules.get("code_structure", {})

        # Check function length
        max_function_length = structure_rules.get("max_function_length", 50)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, "end_lineno") and node.end_lineno:
                    function_length = node.end_lineno - node.lineno
                    if function_length > max_function_length:
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                message=f"Function '{node.name}' is too long ({function_length} lines, max: {max_function_length})",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                rule_id="python.structure.function_length",
                            )
                        )

        # Check class length
        max_class_length = structure_rules.get("max_class_length", 200)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if hasattr(node, "end_lineno") and node.end_lineno:
                    class_length = node.end_lineno - node.lineno
                    if class_length > max_class_length:
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                message=f"Class '{node.name}' is too long ({class_length} lines, max: {max_class_length})",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                rule_id="python.structure.class_length",
                            )
                        )

        return issues

    def _check_config_files(self, project_path: Path) -> list[ValidationIssue]:
        """Check configuration files."""
        issues = []
        config_rules = self.rules.get("configuration", {})

        # Check pyproject.toml
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            issues.extend(self._check_pyproject_toml(pyproject_path, config_rules))

        # Check requirements.txt or similar
        requirements_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "Pipfile",
            "poetry.lock",
        ]
        for req_file in requirements_files:
            req_path = project_path / req_file
            if req_path.exists():
                issues.extend(self._check_requirements_file(req_path, config_rules))

        return issues

    def _check_pyproject_toml(
        self, file_path: Path, config_rules: dict[str, Any]
    ) -> list[ValidationIssue]:
        """Check pyproject.toml configuration."""
        issues = []

        try:
            import toml

            with open(file_path) as f:
                config = toml.load(f)

            # Check for required tools
            required_tools = config_rules.get("required_tools", [])
            for tool in required_tools:
                if tool not in config.get("tool", {}):
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=f"Missing configuration for tool: {tool}",
                            file_path=str(file_path),
                            rule_id="python.config.missing_tool",
                        )
                    )

            # Check Python version
            if "project" in config:
                requires_python = config["project"].get("requires-python", "")
                if requires_python:
                    min_version = config_rules.get("min_python_version", "3.11")
                    if requires_python < min_version:
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                message=f"Python version requirement '{requires_python}' is below minimum '{min_version}'",
                                file_path=str(file_path),
                                rule_id="python.config.python_version",
                            )
                        )

        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Failed to parse pyproject.toml: {e}",
                    file_path=str(file_path),
                    rule_id="python.config.parse_error",
                )
            )

        return issues

    def _check_requirements_file(
        self, file_path: Path, config_rules: dict[str, Any]
    ) -> list[ValidationIssue]:
        """Check requirements file."""
        issues = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Check for pinned versions
            if config_rules.get("require_pinned_versions", False):
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if (
                        line
                        and not line.startswith("#")
                        and "==" not in line
                        and ">=" not in line
                    ):
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                message=f"Unpinned dependency: {line}",
                                file_path=str(file_path),
                                line_number=i,
                                rule_id="python.config.unpinned_dependency",
                            )
                        )

        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Failed to read requirements file: {e}",
                    file_path=str(file_path),
                    rule_id="python.config.read_error",
                )
            )

        return issues


class TypeScriptValidator(BaseValidator):
    """TypeScript-specific standards validator."""

    def validate(self, project_path: Path) -> list[ValidationIssue]:
        """Validate TypeScript project against standards."""
        issues = []

        # Check file structure
        issues.extend(self._check_file_structure(project_path))

        # Check TypeScript files
        ts_files = list(project_path.rglob("*.ts")) + list(project_path.rglob("*.tsx"))
        for ts_file in ts_files:
            if not self._should_skip_file(ts_file):
                issues.extend(self._validate_typescript_file(ts_file))

        # Check configuration files
        issues.extend(self._check_config_files(project_path))

        return issues

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a file should be skipped during validation."""
        skip_patterns = [
            r"node_modules",
            r"\.git",
            r"build",
            r"dist",
            r"\.next",
            r"out",
            r"coverage",
        ]

        file_str = str(file_path)
        return any(re.search(pattern, file_str) for pattern in skip_patterns)

    def _check_file_structure(self, project_path: Path) -> list[ValidationIssue]:
        """Check project file structure."""
        issues = []
        structure_rules = self.rules.get("file_structure", {})

        # Check required directories
        required_dirs = structure_rules.get("required_directories", [])
        for required_dir in required_dirs:
            dir_path = project_path / required_dir
            if not dir_path.exists():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"Missing required directory: {required_dir}",
                        rule_id="typescript.file_structure.missing_directory",
                    )
                )

        # Check required files
        required_files = structure_rules.get("required_files", [])
        for required_file in required_files:
            file_path = project_path / required_file
            if not file_path.exists():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"Missing required file: {required_file}",
                        rule_id="typescript.file_structure.missing_file",
                    )
                )

        return issues

    def _validate_typescript_file(self, file_path: Path) -> list[ValidationIssue]:
        """Validate a single TypeScript file."""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check naming conventions
            issues.extend(self._check_naming_conventions(content, file_path))

            # Check imports
            issues.extend(self._check_imports(content, file_path))

            # Check code structure
            issues.extend(self._check_code_structure(content, file_path))

        except Exception as e:
            logger.warning(f"Failed to validate {file_path}: {e}")
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message=f"Failed to validate file: {e}",
                    file_path=str(file_path),
                    rule_id="typescript.validation_error",
                )
            )

        return issues

    def _check_naming_conventions(
        self, content: str, file_path: Path
    ) -> list[ValidationIssue]:
        """Check TypeScript naming conventions."""
        issues = []
        naming_rules = self.rules.get("naming", {})

        # Check interface naming
        interface_pattern = naming_rules.get("interfaces", r"^[A-Z][a-zA-Z0-9]*$")
        if interface_pattern:
            interface_matches = re.finditer(r"interface\s+(\w+)", content)
            for match in interface_matches:
                interface_name = match.group(1)
                if not re.match(interface_pattern, interface_name):
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=f"Interface name '{interface_name}' doesn't follow convention: {interface_pattern}",
                            file_path=str(file_path),
                            line_number=content[: match.start()].count("\n") + 1,
                            rule_id="typescript.naming.interface_convention",
                        )
                    )

        # Check type naming
        type_pattern = naming_rules.get("types", r"^[A-Z][a-zA-Z0-9]*$")
        if type_pattern:
            type_matches = re.finditer(r"type\s+(\w+)", content)
            for match in type_matches:
                type_name = match.group(1)
                if not re.match(type_pattern, type_name):
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=f"Type name '{type_name}' doesn't follow convention: {type_pattern}",
                            file_path=str(file_path),
                            line_number=content[: match.start()].count("\n") + 1,
                            rule_id="typescript.naming.type_convention",
                        )
                    )

        return issues

    def _check_imports(self, content: str, file_path: Path) -> list[ValidationIssue]:
        """Check import statements."""
        issues = []
        import_rules = self.rules.get("imports", {})

        # Check import order
        import_order = import_rules.get("order", ["external", "internal", "relative"])
        if import_order:
            issues.extend(self._check_import_order(content, file_path, import_order))

        return issues

    def _check_import_order(
        self, content: str, file_path: Path, expected_order: list[str]
    ) -> list[ValidationIssue]:
        """Check that imports follow the expected order."""
        issues = []

        # This is a simplified check - in practice, you'd need more sophisticated logic
        # to categorize imports as external, internal, or relative

        return issues

    def _check_code_structure(
        self, content: str, file_path: Path
    ) -> list[ValidationIssue]:
        """Check code structure and organization."""
        issues = []
        structure_rules = self.rules.get("code_structure", {})

        # Check function length
        max_function_length = structure_rules.get("max_function_length", 50)
        function_matches = re.finditer(r"function\s+\w+\s*\([^)]*\)\s*\{", content)
        for match in function_matches:
            # This is a simplified check - in practice, you'd need to parse the AST
            # to accurately determine function boundaries and length
            pass

        return issues

    def _check_config_files(self, project_path: Path) -> list[ValidationIssue]:
        """Check configuration files."""
        issues = []
        config_rules = self.rules.get("configuration", {})

        # Check package.json
        package_path = project_path / "package.json"
        if package_path.exists():
            issues.extend(self._check_package_json(package_path, config_rules))

        # Check tsconfig.json
        tsconfig_path = project_path / "tsconfig.json"
        if tsconfig_path.exists():
            issues.extend(self._check_tsconfig_json(tsconfig_path, config_rules))

        return issues

    def _check_package_json(
        self, file_path: Path, config_rules: dict[str, Any]
    ) -> list[ValidationIssue]:
        """Check package.json configuration."""
        issues = []

        try:
            import json

            with open(file_path) as f:
                config = json.load(f)

            # Check for required scripts
            required_scripts = config_rules.get("required_scripts", [])
            scripts = config.get("scripts", {})
            for script in required_scripts:
                if script not in scripts:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=f"Missing required script: {script}",
                            file_path=str(file_path),
                            rule_id="typescript.config.missing_script",
                        )
                    )

            # Check for required dependencies
            required_deps = config_rules.get("required_dependencies", [])
            dependencies = config.get("dependencies", {})
            for dep in required_deps:
                if dep not in dependencies:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=f"Missing required dependency: {dep}",
                            file_path=str(file_path),
                            rule_id="typescript.config.missing_dependency",
                        )
                    )

        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Failed to parse package.json: {e}",
                    file_path=str(file_path),
                    rule_id="typescript.config.parse_error",
                )
            )

        return issues

    def _check_tsconfig_json(
        self, file_path: Path, config_rules: dict[str, Any]
    ) -> list[ValidationIssue]:
        """Check tsconfig.json configuration."""
        issues = []

        try:
            import json

            with open(file_path) as f:
                config = json.load(f)

            # Check for required compiler options
            required_options = config_rules.get("required_compiler_options", [])
            compiler_options = config.get("compilerOptions", {})
            for option in required_options:
                if option not in compiler_options:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=f"Missing required compiler option: {option}",
                            file_path=str(file_path),
                            rule_id="typescript.config.missing_compiler_option",
                        )
                    )

        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Failed to parse tsconfig.json: {e}",
                    file_path=str(file_path),
                    rule_id="typescript.config.parse_error",
                )
            )

        return issues


def get_validator(language: str, rules: dict[str, Any]) -> BaseValidator:
    """Get a validator for a specific language."""
    validators = {
        "python": PythonValidator,
        "typescript": TypeScriptValidator,
    }

    validator_class = validators.get(language)
    if validator_class is None:
        raise ValueError(f"No validator available for language: {language}")

    return validator_class(rules)
