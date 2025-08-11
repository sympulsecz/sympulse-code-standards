"""Sympulse Coding Standards - Portable coding standards for Sympulse team."""

__version__ = "0.2.0"
__author__ = "Petr Čala"
__email__ = "petr.cala@sympulse.cz"

from .core import StandardsManager, ValidationResult
from .validators import PythonValidator, TypeScriptValidator, ValidationIssue
from .generators import ProjectGenerator

__all__ = [
    "StandardsManager",
    "ValidationResult",
    "ProjectGenerator",
    "PythonValidator",
    "TypeScriptValidator",
    "ValidationIssue",
    "__version__",
]
