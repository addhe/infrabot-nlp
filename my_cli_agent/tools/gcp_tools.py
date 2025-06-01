"""GCP tools for project management."""
import os
import subprocess
import json
import sys
import re
from typing import Optional, List, Dict, Any
import google.auth
from google.cloud import resourcemanager_v3
from google.cloud import resourcemanager as resource_manager
from my_cli_agent.tools.base import ToolResult
from my_cli_agent.tools.gcp.management.projects import ProjectManager, get_project_manager
from my_cli_agent.tools.gcp.base.exceptions import GCPToolsError, GCPValidationError
from my_cli_agent.tools.gcp.base.intent import IntentDetector
from my_cli_agent.tools.gcp.base.auth import get_project_parent, validate_credentials

# Define exported symbols
__all__ = ['list_gcp_projects', 'create_gcp_project', 'delete_gcp_project', 'HAS_GCP_TOOLS']

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
                       "- Create project: 'create gcp project <project-id>' or 'create multiple projects <id1>, <id2>'\n"
                       "- Delete project: 'delete gcp project <project-id>' or 'delete projects <id1>, <id2>'")
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
                if "project_ids" in params:
                    return create_gcp_project(
                        project_ids=params["project_ids"],
                        name=params.get("project_name"),
                        project_manager=project_manager
                    )
                elif "project_id" in params:
                    return create_gcp_project(
                        project_id=params["project_id"],
                        name=params.get("project_name"),
                        project_manager=project_manager
                    )
                else:
                    return ToolResult(
                        success=False,
                        result="Project ID not specified. Please use: create gcp project <project-id> [project name]"
                    )
                    
            elif intent == "delete_project":
                if "project_ids" in params:
                    return delete_gcp_project(
                        project_ids=params["project_ids"],
                        environment=params.get("environment"),
                        is_bulk=True,
                        project_manager=project_manager
                    )
                elif "project_id" in params:
                    return delete_gcp_project(
                        project_id=params["project_id"],
                        project_manager=project_manager
                    )
                else:
                    return ToolResult(
                        success=False,
                        result="Project ID not specified. Please use: delete gcp project <project-id>"
                    )
            
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
    """List GCP projects with their status."""
    try:
        projects_data = []
        
        # Try using gcloud CLI for listing projects
        try:
            import subprocess
            result = subprocess.run(
                ['gcloud', 'projects', 'list', '--format=json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                projects = json.loads(result.stdout)
                for project in projects:
                    project_id = project.get('projectId', '')
                    project_name = project.get('name', '')
                    lifecycle_state = project.get('lifecycleState', 'UNKNOWN')
                    
                    # Filter by environment if specified
                    if env.lower() != 'all':
                        if env.lower() not in project_id.lower() and env.lower() not in project_name.lower():
                            continue
                            
                    projects_data.append({
                        'id': project_id,
                        'name': project_name,
                        'state': lifecycle_state
                    })
                    
        except Exception as e:
            print(f"Failed to list projects via gcloud: {e}")
            return ToolResult(
                success=False,
                result="Failed to retrieve project list",
                error_message=str(e)
            )

        if not projects_data:
            return ToolResult(
                success=True,
                result=f"Tidak ada proyek ditemukan di environment {env}",  # No projects found in environment
                error_message=None
            )

        # Count states
        active_count = sum(1 for p in projects_data if p['state'] == 'ACTIVE')
        pending_count = sum(1 for p in projects_data if p['state'] in ['DELETE_REQUESTED', 'DELETE_IN_PROGRESS'])
        
        # Format output
        output = [f"\nDitemukan {len(projects_data)} proyek total ({active_count} aktif, {pending_count} menunggu penghapusan):"]
        
        # Active projects
        active_projects = [p for p in projects_data if p['state'] == 'ACTIVE']
        if active_projects:
            output.append("\nProyek Aktif:") # Active Projects
            for proj in active_projects:
                output.append(f"🟢 {proj['name']} ({proj['id']}) - AKTIF")
                
        # Inactive projects
        inactive_projects = [p for p in projects_data if p['state'] == 'INACTIVE']
        if inactive_projects:
            output.append("\nProyek Tidak Aktif:") # Inactive Projects
            for proj in inactive_projects:
                output.append(f"⚫ {proj['name']} ({proj['id']}) - TIDAK AKTIF")
                
        # Projects being deleted
        deleting_projects = [p for p in projects_data if p['state'] in ['DELETE_REQUESTED', 'DELETE_IN_PROGRESS']]
        if deleting_projects:
            output.append("\nProyek Menunggu Penghapusan:") # Projects Pending Deletion
            for proj in deleting_projects:
                status = "MENUNGGU PENGHAPUSAN - Akan dihapus permanen dalam 30 hari" if proj['state'] == 'DELETE_REQUESTED' else "SEDANG DIHAPUS"
                output.append(f"🔴 {proj['name']} ({proj['id']}) - {status}")
                
        # Unknown state projects
        unknown_projects = [p for p in projects_data if p['state'] not in ['ACTIVE', 'INACTIVE', 'DELETE_REQUESTED', 'DELETE_IN_PROGRESS']]
        if unknown_projects:
            output.append("\nProyek Status Tidak Diketahui:") # Projects with Unknown Status
            for proj in unknown_projects:
                output.append(f"⚪ {proj['name']} ({proj['id']}) - TIDAK DIKETAHUI: {proj['state']}")

        # Add legend
        output.append("\nLegenda Status:")
        output.append("🟢 AKTIF")
        output.append("⚫ TIDAK AKTIF")
        output.append("🔴 MENGHAPUS")
        output.append("⚪ TIDAK DIKETAHUI")

        return ToolResult(
            success=True,
            result="\n".join(output),
            error_message=None
        )

    except Exception as e:
        print(f"Error in list_gcp_projects: {e}")
        return ToolResult(
            success=False,
            result=f"Gagal menampilkan daftar proyek: {str(e)}",  # Failed to list projects
            error_message=str(e)
        )

def create_gcp_project(
    project_id: str = None,
    project_ids: List[str] = None,
    name: str = None,
    project_manager: Optional[ProjectManager] = None
) -> ToolResult:
    """Create one or more GCP projects."""
    try:
        if not validate_credentials(require_org=False):
            raise GCPToolsError(
                "Failed to validate credentials. Please ensure you have valid credentials "
                "configured either through gcloud auth or a service account key."
            )

        # Handle bulk creation
        if project_ids:
            results = []
            success_count = 0
            errors = []
            
            print(f"\nCreating {len(project_ids)} projects:")
            for pid in project_ids:
                print(f"  - {pid}")
            
            for pid in project_ids:
                try:
                    # Validate project ID format
                    if not re.match(r'^[a-z][a-z0-9-]*$', pid):
                        raise ValueError(
                            f"Invalid project ID '{pid}'. Project ID must start with a letter "
                            "and can only contain lowercase letters, numbers, and hyphens"
                        )
                    
                    # Generate display name from project ID if not provided
                    display_name = name or pid.replace('-', ' ').title()
                    print(f"\nCreating project {pid}...")
                    
                    import subprocess
                    result = subprocess.run(
                        ['gcloud', 'projects', 'create', pid, f'--name={display_name}', '--format=json'],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    results.append(f"Successfully created project {display_name} ({pid})")
                    success_count += 1
                    
                except subprocess.CalledProcessError as e:
                    error_msg = e.stderr if e.stderr else str(e)
                    if "ALREADY_EXISTS" in error_msg:
                        error_msg = f"Project ID '{pid}' already exists"
                    elif "INVALID_ARGUMENT" in error_msg:
                        error_msg = f"Invalid project ID '{pid}'"
                    results.append(f"Failed to create {pid}: {error_msg}")
                    errors.append(error_msg)
                except ValueError as e:
                    results.append(f"Failed to create {pid}: {str(e)}")
                    errors.append(str(e))

            # Prepare summary
            summary = "\n".join(results)
            if success_count == len(project_ids):
                status = "All projects created successfully"
            elif success_count > 0:
                status = f"{success_count} out of {len(project_ids)} projects created successfully"
            else:
                status = "Failed to create any projects"

            return ToolResult(
                success=success_count > 0,
                result=f"{status}\n\n{summary}",
                error_message="\n".join(errors) if errors else None
            )

        # Handle single project creation
        elif project_id:
            try:
                # Validate project ID format
                if not re.match(r'^[a-z][a-z0-9-]*$', project_id):
                    raise ValueError(
                        "Project ID must start with a letter and can only contain "
                        "lowercase letters, numbers, and hyphens"
                    )
                
                # Generate display name from project ID if not provided
                display_name = name or project_id.replace('-', ' ').title()
                print(f"\nCreating project {project_id}...")
                
                import subprocess
                result = subprocess.run(
                    ['gcloud', 'projects', 'create', project_id, f'--name={display_name}', '--format=json'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                return ToolResult(
                    success=True,
                    result=f"Successfully created project {display_name} ({project_id})",
                    error_message=None
                )
                
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else str(e)
                if "ALREADY_EXISTS" in error_msg:
                    error_msg = f"Project ID '{project_id}' already exists"
                elif "INVALID_ARGUMENT" in error_msg:
                    error_msg = f"Invalid project ID format"
                return ToolResult(
                    success=False,
                    result=f"Failed to create project: {error_msg}",
                    error_message=error_msg
                )
            except ValueError as e:
                return ToolResult(
                    success=False,
                    result=f"Failed to create project: {str(e)}",
                    error_message=str(e)
                )
        else:
            return ToolResult(
                success=False,
                result="No project ID specified",
                error_message="Project ID is required"
            )

    except Exception as e:
        return ToolResult(
            success=False,
            result=f"Unexpected error during project creation: {str(e)}",
            error_message=str(e)
        )

def delete_gcp_project(
    project_id: str = None,
    project_ids: List[str] = None,
    environment: str = None,
    is_bulk: bool = False,
    project_manager: Optional[ProjectManager] = None
) -> ToolResult:
    """Delete one or more GCP projects."""
    try:
        if not validate_credentials(require_org=False):
            raise GCPToolsError(
                "Failed to validate credentials. Please ensure you have valid credentials "
                "configured either through gcloud auth or a service account key."
            )
        
        # Handle bulk deletion
        if project_ids or is_bulk:
            target_projects = project_ids or [project_id]
            if not target_projects:
                return ToolResult(
                    success=False,
                    result="No projects specified for deletion",
                    error_message="No projects specified"
                )

            # Get user confirmation
            confirm_msg = f"\nWARNING: You are about to delete {len(target_projects)} projects:\n"
            for pid in target_projects:
                confirm_msg += f"  - {pid}\n"
            confirm_msg += "\nAre you sure you want to continue? [y/N]: "
            
            if input(confirm_msg).lower() not in ['y', 'yes']:
                return ToolResult(
                    success=True,
                    result="Bulk deletion cancelled by user",
                    error_message=None
                )

            # Process each project
            results = []
            success_count = 0
            errors = []
            
            for pid in target_projects:
                try:
                    import subprocess
                    result = subprocess.run(
                        ['gcloud', 'projects', 'delete', pid, '--quiet'],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    results.append(f"Successfully deleted project {pid}")
                    success_count += 1
                except subprocess.CalledProcessError as e:
                    error_msg = e.stderr if e.stderr else str(e)
                    if "PROJECT_DELETE_INACTIVE" in error_msg:
                        error_msg = f"Project {pid} is inactive and cannot be deleted"
                    elif "INVALID_ARGUMENT" in error_msg:
                        error_msg = f"Invalid project ID format: {pid}"
                    elif "NOT_FOUND" in error_msg:
                        error_msg = f"Project {pid} not found"
                    results.append(f"Failed to delete {pid}: {error_msg}")
                    errors.append(error_msg)

            # Prepare summary
            summary = "\n".join(results)
            if success_count == len(target_projects):
                status = "All projects deleted successfully"
            elif success_count > 0:
                status = f"{success_count} out of {len(target_projects)} projects deleted successfully"
            else:
                status = "Failed to delete any projects"

            return ToolResult(
                success=success_count > 0,
                result=f"{status}\n\n{summary}",
                error_message="\n".join(errors) if errors else None
            )

        # Handle single project deletion
        else:
            if not project_id:
                return ToolResult(
                    success=False,
                    result="Project ID not specified",
                    error_message="Project ID is required"
                )

            try:
                import subprocess
                result = subprocess.run(
                    ['gcloud', 'projects', 'delete', project_id, '--quiet'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return ToolResult(
                    success=True,
                    result=f"Project {project_id} deleted successfully",
                    error_message=None
                )
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else str(e)
                if "PROJECT_DELETE_INACTIVE" in error_msg:
                    error_msg = f"Project {project_id} is inactive and cannot be deleted"
                elif "INVALID_ARGUMENT" in error_msg:
                    error_msg = f"Invalid project ID format: {project_id}"
                elif "NOT_FOUND" in error_msg:
                    error_msg = f"Project {project_id} not found"
                return ToolResult(
                    success=False,
                    result=f"Failed to delete project: {error_msg}",
                    error_message=error_msg
                )

    except Exception as e:
        return ToolResult(
            success=False,
            result=f"Unexpected error during project deletion: {str(e)}",
            error_message=str(e)
        )

def confirm_bulk_operation(operation, items):
    """Get user confirmation for bulk operations.
    
    Args:
        operation (str): The operation being performed (e.g., "delete")
        items (list): List of items being affected
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    print(f"\nWARNING: You are about to {operation} {len(items)} projects:")
    for item in items:
        print(f"  - {item}")
    response = input("\nAre you sure you want to continue? [y/N]: ")
    return response.lower() in ['y', 'yes']

def _check_project_environment(project_id: str, environment: str) -> bool:
    """Check if a project belongs to the specified environment.
    
    Args:
        project_id (str): The project ID to check
        environment (str): The environment to check against (dev/stg/prod)
        
    Returns:
        bool: True if the project belongs to the specified environment
    """
    env_lower = environment.lower()
    pid_lower = project_id.lower()
    
    if env_lower in ['dev', 'development']:
        return any(term in pid_lower for term in ['dev', 'development'])
    elif env_lower in ['stg', 'staging']:
        return any(term in pid_lower for term in ['stg', 'staging'])
    elif env_lower in ['prod', 'production']:
        return any(term in pid_lower for term in ['prod', 'production'])
    return True  # If no environment specified or unknown environment

def reactivate_gcp_project(project_id: str) -> ToolResult:
    """Reactivate an inactive GCP project.
    
    Args:
        project_id (str): The ID of the project to reactivate
        
    Returns:
        ToolResult: Contains the result of the reactivation attempt
    """
    try:
        import subprocess
        
        # First check if project is actually inactive
        result = subprocess.run(
            ['gcloud', 'projects', 'describe', project_id, '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            project_info = json.loads(result.stdout)
            if project_info.get('lifecycleState') != 'INACTIVE':
                return ToolResult(
                    success=False,
                    result=f"Project {project_id} is not inactive (current state: {project_info.get('lifecycleState')})",
                    error_message="Project is not in INACTIVE state"
                )
        
        # Try to reactivate the project
        result = subprocess.run(
            ['gcloud', 'projects', 'undelete', project_id],
            capture_output=True,
            text=True,
            check=True
        )
        
        return ToolResult(
            success=True,
            result=f"Successfully reactivated project {project_id}",
            error_message=None
        )
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        return ToolResult(
            success=False,
            result=f"Failed to reactivate project {project_id}: {error_msg}",
            error_message=error_msg
        )
    except Exception as e:
        return ToolResult(
            success=False,
            result=f"Unexpected error while reactivating project {project_id}: {str(e)}",
            error_message=str(e)
        )
