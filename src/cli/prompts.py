"""Interactive prompts for project initialization."""

from typing import Any, Dict, List, Optional
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.text import Text

console = Console()


class ProjectConfigurator:
    """Interactive configuration system for project initialization."""

    def __init__(self):
        self.config = {}

    def configure_project(self, language: str, project_name: str) -> Dict[str, Any]:
        """Run the full interactive configuration process."""
        console.print("\n[bold blue]🎯 Project Configuration[/bold blue]")
        console.print("Let's configure your project with the features you need.\n")

        # Basic project info
        self.config.update(self._get_basic_info(project_name))

        # Repository features
        self.config.update(self._configure_repository_features())

        # Contributing guidelines
        if self.config.get("contributing_enabled", False):
            self.config.update(self._configure_contributing_guidelines())

        # Code quality tools
        self.config.update(self._configure_code_quality_tools(language))

        # CI/CD
        if self.config.get("ci_cd_enabled", False):
            self.config.update(self._configure_ci_cd(language))

        # Documentation
        if self.config.get("documentation_enabled", False):
            self.config.update(self._configure_documentation())

        # Security
        if self.config.get("security_enabled", False):
            self.config.update(self._configure_security())

        # Show final configuration
        self._show_final_configuration()

        return self.config

    def _get_basic_info(self, project_name: str) -> Dict[str, Any]:
        """Get basic project information."""
        console.print(Panel("📋 Basic Project Information", style="blue"))

        description = Prompt.ask(
            "Project description",
            default=f"A {project_name} project with coding standards",
        )

        author = Prompt.ask("Author name", default="")
        email = Prompt.ask("Author email", default="")

        license_choice = Prompt.ask(
            "License",
            choices=["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "None"],
            default="MIT",
        )

        return {
            "description": description,
            "author": author,
            "email": email,
            "license": license_choice if license_choice != "None" else None,
        }

    def _configure_repository_features(self) -> Dict[str, Any]:
        """Configure repository features."""
        console.print(Panel("🔧 Repository Features", style="green"))

        features = {}

        # Git configuration
        features["git_enabled"] = Confirm.ask(
            "Enable Git repository initialization?", default=True
        )

        if features["git_enabled"]:
            features["git_branch_protection"] = Confirm.ask(
                "Enable branch protection rules?", default=True
            )

            features["git_commit_template"] = Confirm.ask(
                "Use conventional commit template?", default=True
            )

        # Contributing guidelines
        features["contributing_enabled"] = Confirm.ask(
            "Include CONTRIBUTING.md guidelines?", default=True
        )

        # Issue templates
        features["issue_templates_enabled"] = Confirm.ask(
            "Include GitHub issue templates?", default=True
        )

        # Pull request templates
        features["pr_templates_enabled"] = Confirm.ask(
            "Include pull request templates?", default=True
        )

        # Code of conduct
        features["code_of_conduct_enabled"] = Confirm.ask(
            "Include CODE_OF_CONDUCT.md?", default=True
        )

        return features

    def _configure_contributing_guidelines(self) -> Dict[str, Any]:
        """Configure contributing guidelines."""
        console.print(Panel("📝 Contributing Guidelines", style="yellow"))

        guidelines = {}

        # Branch strategy
        branch_strategy = Prompt.ask(
            "Branch strategy",
            choices=["git-flow", "github-flow", "trunk-based", "custom"],
            default="github-flow",
        )

        if branch_strategy == "custom":
            guidelines["main_branch"] = Prompt.ask("Main branch name", default="main")
            guidelines["feature_branch_prefix"] = Prompt.ask(
                "Feature branch prefix", default="feature/"
            )
            guidelines["hotfix_branch_prefix"] = Prompt.ask(
                "Hotfix branch prefix", default="hotfix/"
            )
        else:
            guidelines["branch_strategy"] = branch_strategy

        # Commit conventions
        guidelines["conventional_commits"] = Confirm.ask(
            "Use conventional commits?", default=True
        )

        if guidelines["conventional_commits"]:
            guidelines["commit_types"] = Prompt.ask(
                "Commit types (comma-separated)",
                default="feat,fix,docs,style,refactor,test,chore,ci,perf,revert",
            )

        # Pull request process
        guidelines["pr_required"] = Confirm.ask(
            "Require pull requests for all changes?", default=True
        )

        if guidelines["pr_required"]:
            guidelines["review_required"] = Confirm.ask(
                "Require code review approval?", default=True
            )

            guidelines["reviewers_count"] = IntPrompt.ask(
                "Minimum number of reviewers", default=1
            )

        # Issue reporting
        guidelines["issue_template_enabled"] = Confirm.ask(
            "Use structured issue templates?", default=True
        )

        # License/CLA
        guidelines["cla_required"] = Confirm.ask(
            "Require Contributor License Agreement?", default=False
        )

        if guidelines["cla_required"]:
            guidelines["cla_type"] = Prompt.ask(
                "CLA type",
                choices=["individual", "corporate", "both"],
                default="individual",
            )

        return {"contributing": guidelines}

    def _configure_code_quality_tools(self, language: str) -> Dict[str, Any]:
        """Configure code quality tools."""
        console.print(Panel("🔍 Code Quality Tools", style="cyan"))

        tools = {}

        # Language-specific tools
        if language == "python":
            tools.update(self._configure_python_tools())
        elif language == "typescript":
            tools.update(self._configure_typescript_tools())
        elif language == "go":
            tools.update(self._configure_go_tools())

        # Pre-commit hooks
        tools["pre_commit_enabled"] = Confirm.ask(
            "Enable pre-commit hooks?", default=True
        )

        # Testing
        tools["testing_enabled"] = Confirm.ask("Include testing setup?", default=True)

        if tools["testing_enabled"]:
            tools["coverage_enabled"] = Confirm.ask(
                "Enable code coverage reporting?", default=True
            )

            tools["coverage_threshold"] = IntPrompt.ask(
                "Minimum coverage threshold (%)", default=80
            )

        return {"code_quality": tools}

    def _configure_python_tools(self) -> Dict[str, Any]:
        """Configure Python-specific tools."""
        tools = {}

        # Formatter
        formatter = Prompt.ask(
            "Code formatter",
            choices=["black", "autopep8", "yapf", "none"],
            default="black",
        )
        tools["formatter"] = formatter if formatter != "none" else None

        # Linter
        linter = Prompt.ask(
            "Code linter",
            choices=["flake8", "pylint", "pycodestyle", "none"],
            default="flake8",
        )
        tools["linter"] = linter if linter != "none" else None

        # Type checker
        type_checker = Prompt.ask(
            "Type checker", choices=["mypy", "pyre", "pyright", "none"], default="mypy"
        )
        tools["type_checker"] = type_checker if type_checker != "none" else None

        # Import sorter
        import_sorter = Prompt.ask(
            "Import sorter",
            choices=["isort", "reorder-python-imports", "none"],
            default="isort",
        )
        tools["import_sorter"] = import_sorter if import_sorter != "none" else None

        return tools

    def _configure_typescript_tools(self) -> Dict[str, Any]:
        """Configure TypeScript-specific tools."""
        tools = {}

        # Formatter
        formatter = Prompt.ask(
            "Code formatter", choices=["prettier", "eslint", "none"], default="prettier"
        )
        tools["formatter"] = formatter if formatter != "none" else None

        # Linter
        linter = Prompt.ask(
            "Code linter", choices=["eslint", "tslint", "none"], default="eslint"
        )
        tools["linter"] = linter if linter != "none" else None

        # Bundler
        bundler = Prompt.ask(
            "Bundler",
            choices=["webpack", "vite", "rollup", "esbuild", "none"],
            default="vite",
        )
        tools["bundler"] = bundler if bundler != "none" else None

        return tools

    def _configure_go_tools(self) -> Dict[str, Any]:
        """Configure Go-specific tools."""
        tools = {}

        # Formatter
        tools["formatter"] = "gofmt"  # Standard Go formatter

        # Linter
        linter = Prompt.ask(
            "Code linter",
            choices=["golangci-lint", "golint", "none"],
            default="golangci-lint",
        )
        tools["linter"] = linter if linter != "none" else None

        return tools

    def _configure_ci_cd(self, language: str) -> Dict[str, Any]:
        """Configure CI/CD pipeline."""
        console.print(Panel("🚀 CI/CD Pipeline", style="magenta"))

        ci_cd = {}

        # Platform
        platform = Prompt.ask(
            "CI/CD platform",
            choices=["github-actions", "gitlab-ci", "jenkins", "circleci", "none"],
            default="github-actions",
        )
        ci_cd["platform"] = platform if platform != "none" else None

        if ci_cd["platform"]:
            # Triggers
            ci_cd["triggers"] = []
            if Confirm.ask("Trigger on push to main branch?", default=True):
                ci_cd["triggers"].append("push")
            if Confirm.ask("Trigger on pull requests?", default=True):
                ci_cd["triggers"].append("pull_request")
            if Confirm.ask("Trigger on tags?", default=True):
                ci_cd["triggers"].append("tags")

            # Jobs
            ci_cd["jobs"] = []
            if Confirm.ask("Run tests?", default=True):
                ci_cd["jobs"].append("test")
            if Confirm.ask("Run linting?", default=True):
                ci_cd["jobs"].append("lint")
            if Confirm.ask("Run security scans?", default=True):
                ci_cd["jobs"].append("security")
            if Confirm.ask("Build and deploy?", default=False):
                ci_cd["jobs"].append("deploy")

        return {"ci_cd": ci_cd}

    def _configure_documentation(self) -> Dict[str, Any]:
        """Configure documentation."""
        console.print(Panel("📚 Documentation", style="blue"))

        docs = {}

        # Documentation generator
        generator = Prompt.ask(
            "Documentation generator",
            choices=["sphinx", "mkdocs", "docusaurus", "vuepress", "none"],
            default="mkdocs",
        )
        docs["generator"] = generator if generator != "none" else None

        # API documentation
        docs["api_docs"] = Confirm.ask("Generate API documentation?", default=True)

        # README
        docs["readme_enabled"] = Confirm.ask(
            "Include comprehensive README?", default=True
        )

        # Changelog
        docs["changelog_enabled"] = Confirm.ask("Include CHANGELOG.md?", default=True)

        return {"documentation": docs}

    def _configure_security(self) -> Dict[str, Any]:
        """Configure security features."""
        console.print(Panel("🔒 Security", style="red"))

        security = {}

        # Dependencies scanning
        security["dependency_scanning"] = Confirm.ask(
            "Enable dependency vulnerability scanning?", default=True
        )

        # Code scanning
        security["code_scanning"] = Confirm.ask(
            "Enable code security scanning?", default=True
        )

        # Secrets detection
        security["secrets_detection"] = Confirm.ask(
            "Enable secrets detection in commits?", default=True
        )

        # SBOM generation
        security["sbom_enabled"] = Confirm.ask(
            "Generate Software Bill of Materials?", default=False
        )

        return {"security": security}

    def _show_final_configuration(self):
        """Show the final configuration summary."""
        console.print("\n[bold green]✅ Configuration Complete![/bold green]")
        console.print("\n[bold]Summary of your configuration:[/bold]")

        # Basic info
        if self.config.get("description"):
            console.print(f"📋 Description: {self.config['description']}")
        if self.config.get("author"):
            console.print(f"👤 Author: {self.config['author']}")
        if self.config.get("license"):
            console.print(f"📄 License: {self.config['license']}")

        # Features
        features = []
        if self.config.get("contributing_enabled"):
            features.append("Contributing Guidelines")
        if self.config.get("ci_cd_enabled"):
            features.append("CI/CD Pipeline")
        if self.config.get("documentation_enabled"):
            features.append("Documentation")
        if self.config.get("security_enabled"):
            features.append("Security Features")

        if features:
            console.print(f"🔧 Features: {', '.join(features)}")

        console.print(
            "\n[dim]You can modify these settings later by editing the project configuration files.[/dim]"
        )
