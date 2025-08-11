"""CLI commands package for Sympulse Coding Standards."""

from .project import project_group
from .standards import standards_group
from .tools import tools_group
from .admin import admin_group

__all__ = [
    "project_group",
    "standards_group",
    "tools_group",
    "admin_group",
]
