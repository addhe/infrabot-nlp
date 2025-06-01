"""
GCP Specialized Agents for ADK Implementation.

This module provides specialized agents for different aspects of GCP
infrastructure management including compute, storage, networking,
IAM/security, and monitoring/observability.
"""

from .root_agent import RootGCPAgent
from .project_agent import ProjectAgent
from .compute_agent import ComputeAgent
from .networking_agent import NetworkingAgent
from .storage_agent import StorageAgent
from .iam_agent import IAMAgent
from .monitoring_agent import MonitoringAgent

# Aliases for backward compatibility
RootAgent = RootGCPAgent

__all__ = [
    'RootGCPAgent',
    'RootAgent',
    'ProjectAgent',
    'ComputeAgent',
    'NetworkingAgent',
    'StorageAgent',
    'IAMAgent',
    'MonitoringAgent'
]