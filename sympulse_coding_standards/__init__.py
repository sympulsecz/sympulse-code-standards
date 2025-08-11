"""Sympulse Coding Standards - Portable coding standards for Sympulse team."""

__version__ = "0.1.0"
__author__ = "Petr Čala"
__email__ = "petr.cala@sympulse.cz"

from .core import StandardsManager
from .validators import ValidationResult
from .generators import ProjectGenerator

__all__ = [
    "StandardsManager",
    "ValidationResult", 
    "ProjectGenerator",
    "__version__",
]
