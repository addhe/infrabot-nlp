"""Specialized GCP Project Agent for project management operations."""

from typing import Dict, List, Optional, Callable, Any
import logging
from ..base.base_agent import SpecializedGCPAgent
from ..tools.project_tools import create_gcp_project, list_gcp_projects, delete_gcp_project

logger = logging.getLogger(__name__)


class ProjectAgent(SpecializedGCPAgent):
    """Specialized agent for GCP project management operations."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        **kwargs
    ):
        """Initialize the GCP Project Agent.
        
        Args:
            model: Model to use (supports LiteLLM format)
            **kwargs: Additional arguments for base class
        """
        
        # Specialized instruction for project management
        instruction = """
You are the GCP Project Management Specialist with deep expertise in Google Cloud project lifecycle management.

**Core Expertise:**
- **Project Creation**: Create new GCP projects with proper naming, organization structure, and initial configuration
- **Project Management**: List, filter, and organize existing projects across environments
- **Project Deletion**: Safely remove projects with proper safety checks and confirmation
- **Organization Management**: Handle organizational hierarchies and project placement
- **Resource Planning**: Advise on project structure, naming conventions, and resource organization

**Best Practices You Follow:**
1. **Naming Conventions**: Enforce consistent project naming (environment prefixes, team identifiers)
2. **Environment Separation**: Maintain clear boundaries between dev, staging, and production
3. **Security Compliance**: Ensure proper IAM setup and access controls
4. **Cost Management**: Advise on billing accounts and budget setup
5. **Resource Organization**: Structure projects for optimal management and governance

**Safety Protocols:**
- Always confirm project deletions, especially for production environments
- Validate project names against organizational standards
- Check for existing resources before allowing deletion
- Warn about billing and IAM implications
- Verify organization placement and permissions

**Session Awareness:**
- Remember user's preferred regions and naming patterns
- Track previously created projects in this session
- Store user's organizational context and team preferences
- Maintain history of project operations for audit purposes

Always check the session state for user preferences and previously created projects before making recommendations.
"""
        
        # Register project-specific tools
        tools = [
            create_gcp_project,
            list_gcp_projects,
            delete_gcp_project,
        ]
        
        super().__init__(
            name="gcp_project_agent",
            specialization="project",
            model=model,
            description="Specialized GCP agent for project lifecycle management",
            instruction=instruction.strip(),
            tools=tools,
            **kwargs
        )
    
    def get_delegation_logic(self) -> Dict[str, Any]:
        """Return delegation logic specific to project management.
        
        Returns:
            Project-specific delegation rules
        """
        base_logic = super().get_delegation_logic()
        
        # Extend with project-specific logic
        base_logic.update({
            "specialized_operations": {
                "project_creation": {
                    "operations": ["create_gcp_project"],
                    "prerequisites": ["project_name", "organization_context"],
                    "safety_checks": ["naming_validation", "duplicate_check"]
                },
                "project_listing": {
                    "operations": ["list_gcp_projects"],
                    "filters": ["environment", "team", "status", "organization"],
                    "output_formats": ["table", "json", "summary"]
                },
                "project_deletion": {
                    "operations": ["delete_gcp_project"],
                    "safety_checks": ["confirmation_required", "resource_check", "backup_reminder"],
                    "escalation_triggers": ["production_projects", "active_resources"]
                }
            },
            "expertise_areas": [
                "project_lifecycle",
                "organization_management", 
                "resource_planning",
                "naming_conventions",
                "environment_separation"
            ]
        })
        
        return base_logic