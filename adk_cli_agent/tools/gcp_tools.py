"""Google Cloud Platform (GCP) tools for ADK CLI Agent."""

# This module is now a thin wrapper that imports GCP project management functions from gcp_project.py
from .gcp_project import list_gcp_projects, create_gcp_project, delete_gcp_project
