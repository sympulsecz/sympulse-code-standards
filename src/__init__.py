"""Sympulse Coding Standards - Portable coding standards for Sympulse team."""

__version__ = "0.0.1"
__author__ = "Petr Čala"
__email__ = "petr.cala@sympulse.cz"

from .core import StandardsManager, ValidationResult
from .validators import PythonValidator, TypeScriptValidator, ValidationIssue
from .generators import ProjectGenerator
from .cli import app as cli_app

__all__ = [
    "StandardsManager",
    "ValidationResult",
    "ProjectGenerator",
    "PythonValidator",
    "TypeScriptValidator",
    "ValidationIssue",
    "cli_app",
    "__version__",
]
