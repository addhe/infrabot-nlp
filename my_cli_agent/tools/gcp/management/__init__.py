"""
GCP Management Module

This module provides tools for managing GCP organizational resources
like projects, billing, and IAM.
"""

from .projects import (
    ProjectManager,
    get_project_manager,
    get_mock_projects
)

__all__ = [
    'ProjectManager',
    'get_project_manager',
    'get_mock_projects'
]
