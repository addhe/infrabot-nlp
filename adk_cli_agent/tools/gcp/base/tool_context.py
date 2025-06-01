"""
Tool Context for GCP ADK Implementation

This module provides the ToolContext class that maintains state and configuration
for tool execution across the ADK agent framework.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolContext:
    """
    Context object that provides shared state and configuration for tools.
    
    This class maintains:
    - Session state and metadata
    - GCP project and configuration information
    - Execution context and logging
    - Safety and compliance settings
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize tool context with optional session ID."""
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.created_at = datetime.now()
        self.metadata: Dict[str, Any] = {}
        self.gcp_config: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}  # Add state attribute
        self.safety_config: Dict[str, Any] = {
            'require_confirmation': True,
            'max_risk_level': 'medium',
            'production_protection': True
        }
        self._load_gcp_config()
    
    def _load_gcp_config(self):
        """Load GCP configuration from environment."""
        self.gcp_config = {
            'project_id': os.getenv('GOOGLE_CLOUD_PROJECT'),
            'region': os.getenv('GOOGLE_CLOUD_REGION', 'us-central1'),
            'zone': os.getenv('GOOGLE_CLOUD_ZONE', 'us-central1-a'),
            'credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        }
    
    def get_project_id(self) -> Optional[str]:
        """Get the current GCP project ID."""
        return self.gcp_config.get('project_id')
    
    def get_region(self) -> str:
        """Get the current GCP region."""
        return self.gcp_config.get('region', 'us-central1')
    
    def get_zone(self) -> str:
        """Get the current GCP zone."""
        return self.gcp_config.get('zone', 'us-central1-a')
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata for the context."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the context."""
        return self.metadata.get(key, default)
    
    def is_production_environment(self) -> bool:
        """Check if we're in a production environment."""
        project_id = self.get_project_id()
        if not project_id:
            return False
        
        # Common production project naming patterns
        prod_indicators = ['prod', 'production', 'live', 'prd']
        return any(indicator in project_id.lower() for indicator in prod_indicators)
    
    def get_safety_level(self) -> str:
        """Get the current safety level setting."""
        return self.safety_config.get('max_risk_level', 'medium')
    
    def requires_confirmation(self) -> bool:
        """Check if operations require confirmation."""
        return self.safety_config.get('require_confirmation', True)
    
    def log_operation(self, operation: str, details: Dict[str, Any]):
        """Log an operation for audit trail."""
        log_entry = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'details': details,
            'project_id': self.get_project_id()
        }
        logger.info(f"Operation logged: {log_entry}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary representation."""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
            'gcp_config': self.gcp_config,
            'safety_config': self.safety_config
        }
    
    def __repr__(self) -> str:
        return f"ToolContext(session_id='{self.session_id}', project_id='{self.get_project_id()}')"
