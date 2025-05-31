"""GCP tools for project management."""
import os
import subprocess
import json
import sys
from typing import Optional, List, Dict, Any
import google.auth
from google.cloud import resourcemanager_v3
from google.cloud import resourcemanager as resource_manager
from my_cli_agent.tools.base import ToolResult
from my_cli_agent.tools.gcp.management.projects import ProjectManager, get_project_manager
from my_cli_agent.tools.gcp.base.exceptions import GCPToolsError, GCPValidationError
from my_cli_agent.tools.gcp.base.intent import IntentDetector
from my_cli_agent.tools.gcp.base.auth import get_project_parent, validate_credentials

# Check if required GCP libraries are available
try:
    import google.cloud.resourcemanager
    HAS_GCP_TOOLS = True
except ImportError:
    HAS_GCP_TOOLS = False

def execute_command(command: str) -> ToolResult:
    """
    Execute a GCP-related command.
    
    Args:
        command (str): The command to execute
        
    Returns:
        ToolResult: Contains the command result or error information
    """
    print(f"Executing command with intent detection: {command}")
    command = command.lower().strip()
    
    try:
        project_manager = get_project_manager()
        
        # Detect command intent
        intent, confidence, params = IntentDetector.detect_intent(command)
        print(f"Detected intent: {intent}, confidence: {confidence}, params: {params}")
        
        if not intent:
            return ToolResult(
                success=False,
                result=("Unknown GCP command. Available commands:\n"
                       "- List projects: 'list gcp projects [dev/stg/prod/all]'\n"
                       "- Create project: 'create gcp project <project-id> [project name]'\n"
                       "- Delete project: 'delete gcp project <project-id>'")
            )
            
        if confidence < 0.6:
            suggestions = []
            if "crate" in command:
                suggestions.append('"create project"')
            if "delte" in command:
                suggestions.append('"delete project"')
            if suggestions:
                return ToolResult(
                    success=False,
                    result=f"Did you mean {' or '.join(suggestions)}? Please use the correct format."
                )
        
        try:
            # Execute based on detected intent
            if intent == "list_projects":
                return list_gcp_projects(params.get("environment", "all"), project_manager)
                
            elif intent == "create_project":
                if "project_id" not in params:
                    return ToolResult(
                        success=False,
                        result="Project ID not specified. Please use: create gcp project <project-id> [project name]"
                    )
                    
                # Validate project ID basic format
                project_id = params["project_id"]
                if not project_id.islower() or not project_id[0].isalpha():
                    return ToolResult(
                        success=False,
                        result=("Invalid project ID format. Project ID must start with a lowercase letter "
                               "and contain only lowercase letters, numbers, and hyphens.")
                    )
                print(f"Creating project with ID: {project_id}, name: {params.get('project_name')}")
                    
                return create_gcp_project(
                    project_id,
                    name=params.get("project_name"),
                    project_manager=project_manager
                )
                
            elif intent == "delete_project":
                if "project_id" not in params:
                    return ToolResult(
                        success=False,
                        result="Project ID not specified. Please use: delete gcp project <project-id>"
                    )
                    
                return delete_gcp_project(params["project_id"], project_manager)
            
        except Exception as op_error:
            print(f"Operation error: {str(op_error)}")
            raise
        
    except GCPToolsError as e:
        print(f"GCP Tools error: {str(e)}")
        return ToolResult(
            success=False,
            result=f"GCP operation failed: {str(e)}",
            error_message=str(e)
        )
    except Exception as e:
        print(f"Unexpected error in execute_command: {str(e)}")
        import traceback
        traceback.print_exc()
        return ToolResult(
            success=False,
            result=f"Unexpected error: {str(e)}",
            error_message=str(e)
        )

def list_gcp_projects(env: str = 'all', project_manager: Optional[ProjectManager] = None) -> ToolResult:
    """List GCP projects using the ProjectManager.

    Args:
        env (str, optional): Environment to filter by. Defaults to 'all'.
        project_manager (ProjectManager, optional): Project manager instance.

    Returns:
        ToolResult: Operation result
    """
    manager = project_manager or get_project_manager()
    try:
        projects = manager.list_projects(env)
        if not projects:
            return ToolResult(
                success=True,
                result=f"No projects found for environment: {env}",
                error_message=None
            )
        
        formatted_projects = [f"{p.display_name} ({p.project_id})" for p in projects]
        return ToolResult(
            success=True,
            result=f"Found {len(projects)} projects in the {env} environment:\n- " + "\n- ".join(formatted_projects),
            error_message=None
        )
    except GCPToolsError as e:
        return ToolResult(
            success=False,
            result=f"Failed to list projects: {str(e)}",
            error_message=str(e)
        )

def create_gcp_project(project_id: str, name: Optional[str] = None, project_manager: Optional[ProjectManager] = None) -> ToolResult:
    """Create a new GCP project using the ProjectManager.

    Args:
        project_id (str): The project ID to create
        name (str, optional): Display name for the project. Defaults to project_id.
        project_manager (ProjectManager, optional): Project manager instance.

    Returns:
        ToolResult: Operation result
    """
    try:
        # Additional validation
        if not project_id:
            raise GCPValidationError("Project ID cannot be empty")
            
        if not project_id[0].isalpha() or not project_id[0].islower():
            raise GCPValidationError("Project ID must start with a lowercase letter")
            
        if not all(c.islower() or c.isdigit() or c == '-' for c in project_id):
            raise GCPValidationError(
                "Project ID can only contain lowercase letters, numbers, and hyphens"
            )
            
        # Validate credentials and get organization
        if not validate_credentials():
            raise GCPToolsError(
                "Current credentials do not have access to any organization. "
                "Please use a service account with proper organization access "
                "or set GCP_ORGANIZATION_ID manually."
            )
            
        # Get organization ID for the project
        parent = get_project_parent()
        if not parent:
            raise GCPToolsError(
                "Could not determine organization for project creation. "
                "Please set GCP_ORGANIZATION_ID environment variable "
                "or use a service account with organization access."
            )
            
        manager = project_manager or get_project_manager()
        project = manager.create_project(
            project_id,
            name=name or project_id,
            organization_id=parent
        )
        
        return ToolResult(
            success=True,
            result=f"Project '{project.display_name}' ({project.project_id}) created successfully.",
            error_message=None
        )
        
    except GCPToolsError as e:
        return ToolResult(
            success=False,
            result=f"Failed to create project: {str(e)}",
            error_message=str(e)
        )
    except Exception as e:
        return ToolResult(
            success=False,
            result=f"Unexpected error during project creation: {str(e)}",
            error_message=str(e)
        )

def delete_gcp_project(project_id: str, project_manager: Optional[ProjectManager] = None) -> ToolResult:
    """Delete a GCP project using the ProjectManager.

    Args:
        project_id (str): The project ID to delete
        project_manager (ProjectManager, optional): Project manager instance.

    Returns:
        ToolResult: Operation result
    """
    manager = project_manager or get_project_manager()
    try:
        manager.delete_project(project_id)
        return ToolResult(
            success=True,
            result=f"Project '{project_id}' deleted successfully.",
            error_message=None
        )
    except GCPToolsError as e:
        return ToolResult(
            success=False,
            result=f"Failed to delete project: {str(e)}",
            error_message=str(e)
        )
