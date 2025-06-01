"""GCP Project management tools for ADK agents."""

from typing import Dict, Any, Optional
from ..base.tool_context import ToolContext
from ..base.exceptions import GCPToolsError
from ..base.client import get_gcp_client
import logging

logger = logging.getLogger(__name__)


async def create_gcp_project(
    project_id: str,
    name: str,
    tool_context: ToolContext,
    organization_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new GCP project with state management.
    
    This tool creates a Google Cloud Platform project and stores the operation
    in the session state for future reference.
    
    Args:
        project_id: Unique identifier for the project (lowercase, alphanumeric, hyphens)
        name: Display name for the project
        tool_context: ADK tool context for state access
        organization_id: Optional organization ID to create project under
        
    Returns:
        Dict containing operation status and project details
    """
    logger.info(f"Creating GCP project: {project_id}")
    
    try:
        # Access user preferences from session metadata
        preferred_region = tool_context.get_metadata("default_region", "us-central1")
        auto_enable_apis = tool_context.get_metadata("auto_enable_apis", True)
        
        # Get GCP client
        client = get_gcp_client('resourcemanager')
        
        # Create project configuration
        project_config = {
            "projectId": project_id,
            "name": name,
        }
        
        if organization_id:
            project_config["parent"] = {
                "type": "organization",
                "id": organization_id
            }
        
        # Call GCP API (mock implementation for now)
        # In real implementation, use Google Cloud Resource Manager API
        project_result = {
            "projectId": project_id,
            "name": name,
            "projectNumber": "123456789",
            "lifecycleState": "ACTIVE",
            "createTime": "2025-06-01T12:00:00Z"
        }
        
        # Update session metadata with successful operation
        tool_context.set_metadata("last_created_project", project_id)
        tool_context.set_metadata("last_project_operation", {
            "operation": "create",
            "project_id": project_id,
            "timestamp": "2025-06-01T12:00:00Z",
            "status": "success"
        })
        
        # Store project in user's project list
        user_projects = tool_context.get_metadata("user_projects", [])
        if project_id not in user_projects:
            user_projects.append(project_id)
            tool_context.set_metadata("user_projects", user_projects)
        
        logger.info(f"Successfully created project: {project_id}")
        
        return {
            "status": "success",
            "message": f"Project '{name}' ({project_id}) created successfully",
            "data": {
                "project": project_result,
                "preferred_region": preferred_region,
                "auto_enable_apis": auto_enable_apis
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create project {project_id}: {str(e)}")
        
        # Update metadata with failed operation
        tool_context.set_metadata("last_project_operation", {
            "operation": "create",
            "project_id": project_id,
            "timestamp": "2025-06-01T12:00:00Z",
            "status": "error",
            "error": str(e)
        })
        
        return {
            "status": "error",
            "message": f"Failed to create project: {str(e)}",
            "data": {
                "project_id": project_id,
                "error_details": str(e)
            }
        }


async def list_gcp_projects(
    tool_context: ToolContext,
    filter_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    List GCP projects accessible to the user.
    
    Args:
        tool_context: ADK tool context for state access
        filter_query: Optional filter for projects (e.g., "name:my-project*")
        
    Returns:
        Dict containing list of projects and metadata
    """
    logger.info("Listing GCP projects")
    
    try:
        # Get user's project history from metadata
        user_projects = tool_context.get_metadata("user_projects", [])
        last_operation = tool_context.get_metadata("last_project_operation", {})
        
        # Mock project list (in real implementation, use Resource Manager API)
        projects = [
            {
                "projectId": "my-test-project-1",
                "name": "Test Project 1",
                "projectNumber": "123456789",
                "lifecycleState": "ACTIVE"
            },
            {
                "projectId": "my-prod-project",
                "name": "Production Project",
                "projectNumber": "987654321",
                "lifecycleState": "ACTIVE"
            }
        ]
        
        # Add user-created projects from metadata
        for project_id in user_projects:
            if not any(p["projectId"] == project_id for p in projects):
                projects.append({
                    "projectId": project_id,
                    "name": f"User Created: {project_id}",
                    "projectNumber": "000000000",
                    "lifecycleState": "ACTIVE",
                    "source": "user_created"
                })
        
        # Apply filter if provided
        if filter_query:
            # Simple name filtering (real implementation would parse full filter syntax)
            if filter_query.startswith("name:"):
                name_filter = filter_query[5:].replace("*", "")
                projects = [p for p in projects if name_filter.lower() in p["name"].lower()]
        
        # Update metadata
        tool_context.set_metadata("last_project_list_count", len(projects))
        tool_context.set_metadata("last_project_operation", {
            "operation": "list",
            "timestamp": "2025-06-01T12:00:00Z",
            "status": "success",
            "count": len(projects)
        })
        
        return {
            "status": "success",
            "message": f"Found {len(projects)} projects",
            "data": {
                "projects": projects,
                "total_count": len(projects),
                "user_created_count": len(user_projects),
                "last_operation": last_operation
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        
        return {
            "status": "error",
            "message": f"Failed to list projects: {str(e)}",
            "data": {"error_details": str(e)}
        }


async def delete_gcp_project(
    project_id: str,
    tool_context: ToolContext,
    force: bool = False
) -> Dict[str, Any]:
    """
    Delete a GCP project (mark for deletion).
    
    Args:
        project_id: ID of the project to delete
        tool_context: ADK tool context for state access
        force: Whether to force deletion without confirmation
        
    Returns:
        Dict containing operation status
    """
    logger.info(f"Deleting GCP project: {project_id}")
    
    try:
        # Check if project is in user's managed projects
        user_projects = tool_context.get_metadata("user_projects", [])
        
        # Safety check - prevent deletion of production projects
        if "prod" in project_id.lower() or "production" in project_id.lower():
            return {
                "status": "error",
                "message": "Cannot delete production projects for safety reasons",
                "data": {"project_id": project_id, "reason": "production_safety_check"}
            }
        
        # Mock deletion (in real implementation, use Resource Manager API)
        deletion_result = {
            "projectId": project_id,
            "lifecycleState": "DELETE_REQUESTED",
            "deleteTime": "2025-06-01T12:00:00Z"
        }
        
        # Update session metadata
        if project_id in user_projects:
            user_projects.remove(project_id)
            tool_context.set_metadata("user_projects", user_projects)
        
        tool_context.set_metadata("last_deleted_project", project_id)
        tool_context.set_metadata("last_project_operation", {
            "operation": "delete",
            "project_id": project_id,
            "timestamp": "2025-06-01T12:00:00Z",
            "status": "success"
        })
        
        logger.info(f"Successfully marked project for deletion: {project_id}")
        
        return {
            "status": "success",
            "message": f"Project '{project_id}' marked for deletion (30-day grace period)",
            "data": {
                "project": deletion_result,
                "grace_period_days": 30,
                "permanent_deletion_date": "2025-07-01T12:00:00Z"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {str(e)}")
        
        tool_context.set_metadata("last_project_operation", {
            "operation": "delete",
            "project_id": project_id,
            "timestamp": "2025-06-01T12:00:00Z",
            "status": "error",
            "error": str(e)
        })
        
        return {
            "status": "error",
            "message": f"Failed to delete project: {str(e)}",
            "data": {
                "project_id": project_id,
                "error_details": str(e)
            }
        }
