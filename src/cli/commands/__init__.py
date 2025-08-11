"""CLI commands package for Sympulse Coding Standards."""

from .project import project_group
from .standards import standards_group
from .tools import tools_group

__all__ = [
    "project_group",
    "standards_group",
    "tools_group",
]
