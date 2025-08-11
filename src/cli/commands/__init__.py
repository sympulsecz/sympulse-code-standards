"""CLI commands package for Sympulse Coding Standards."""

from .init import app as init_app
from .validate import app as validate_app
from .update import app as update_app
from .audit import app as audit_app
from .list_standards import app as list_standards_app
from .show_standard import app as show_standard_app

__all__ = [
    "init",
    "validate",
    "update",
    "audit",
    "list_standards",
    "show_standard",
]
