"""Google Cloud Platform (GCP) tools for ADK CLI Agent."""

import os
import json
import subprocess
from typing import Optional, Dict, Any

# Check if GCP tools are available
HAS_GCP_TOOLS_FLAG = True  # We'll keep this True since we have CLI fallback
GOOGLE_CLOUD_AVAILABLE = False

try:
    import google.auth
    from google.cloud import resourcemanager_v3
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    pass  # Will fallback to CLI

def list_gcp_projects(env: str) -> Dict[str, Any]:
    """Lists Google Cloud Platform (GCP) projects.
    
    If 'env' is 'all', it lists all accessible projects.
    Otherwise, it attempts to filter projects for a specified environment (dev/stg/prod)
    based on project ID or name.
    
    Args:
        env (str): The environment to list projects for (dev/stg/prod/all).
        
    Returns:
        dict: Contains status and the list of projects as a report, or an error message.
    """
    print(f"--- Tool: list_gcp_projects called with env={env} ---")
    
    if not env:
        env = "all"
    
    env_lower = env.lower()
    projects_list = []

    try:
        # First approach: Try using Google Cloud Resource Manager API if available
        if GOOGLE_CLOUD_AVAILABLE:
            try:
                print("Attempting to get default credentials...")
                credentials, _ = google.auth.default()
                if not credentials:
                    print("No default credentials found.")
                    raise Exception("No default credentials found")
                    
                print("Creating Resource Manager client...")
                client = resourcemanager_v3.ProjectsClient(credentials=credentials)
                
                print("Sending SearchProjectsRequest...")
                request = resourcemanager_v3.SearchProjectsRequest()
                
                print("Fetching projects...")
                for project in client.search_projects(request=request):
                    project_id = project.project_id
                    project_name = project.display_name if project.display_name else project_id
                    state = project.state.name if hasattr(project.state, 'name') else 'UNKNOWN'
                    
                    # Format project entry with state
                    project_entry = f"{project_name} ({project_id}) - {state}"
                    
                    if env_lower == "all":
                        projects_list.append(project_entry)
                    elif (env_lower in project_id.lower() or \
                          (project_name and env_lower in project_name.lower())):
                        projects_list.append(project_entry)
                
                if projects_list:
                    report = f"Found {len(projects_list)} projects:\n" + "\n".join(projects_list)
                    return {
                        "status": "success",
                        "report": report
                    }
                print(f"No projects matching '{env}' found via API, trying gcloud CLI.")
                raise Exception(f"No projects matching '{env}' found via API") 
                    
            except Exception as api_error:
                print(f"API approach failed: {str(api_error)}, trying gcloud CLI.")
                # Fall through to CLI
        
        # Second approach: Use gcloud CLI
        try:
            print("Attempting to list projects using gcloud CLI...")
            result = subprocess.run(
                ["gcloud", "projects", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            projects = json.loads(result.stdout)
            for project in projects:
                project_id = project.get('projectId', '')
                project_name = project.get('name', project_id)
                state = project.get('lifecycleState', 'UNKNOWN')
                
                # Format project entry with state
                project_entry = f"{project_name} ({project_id}) - {state}"
                
                if env_lower == "all":
                    projects_list.append(project_entry)
                elif (env_lower in project_id.lower() or \
                      (project_name and env_lower in project_name.lower())):
                    projects_list.append(project_entry)
            
            if projects_list:
                report = f"Found {len(projects_list)} projects:\n" + "\n".join(projects_list)
                return {
                    "status": "success",
                    "report": report
                }
            else:
                return {
                    "status": "success",
                    "report": f"No projects matching '{env}' found."
                }
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to list projects using gcloud CLI: {e.stderr}"
            print(error_msg)
            return {
                "status": "error",
                "error_message": error_msg
            }
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse gcloud output: {e}"
            print(error_msg)
            return {
                "status": "error",
                "error_message": error_msg
            }
            
    except Exception as e:
        error_msg = f"An unexpected error occurred in list_gcp_projects: {str(e)}"
        print(f"ERROR: {error_msg}")
        return {
            "status": "error",
            "error_message": error_msg
        }

def create_gcp_project(project_id: str, project_name: Optional[str] = None) -> Dict[str, Any]:
    """Creates a new Google Cloud Platform (GCP) project.
    
    Args:
        project_id (str): The desired project ID (must be globally unique).
        project_name (str, optional): A human-readable name for the project.
                                    If not provided, project_id will be used.
    
    Returns:
        dict: Contains status and creation result or error message.
    """
    if not project_name:
        project_name = project_id

    try:
        # First approach: Try using Google Cloud Resource Manager API if available
        if GOOGLE_CLOUD_AVAILABLE:
            try:
                print(f"Attempting to create project {project_id} using API...")
                credentials, _ = google.auth.default()
                if not credentials:
                    raise Exception("No default credentials found")
                    
                client = resourcemanager_v3.ProjectsClient(credentials=credentials)
                
                # Create project request
                project = resourcemanager_v3.Project()
                project.project_id = project_id
                project.display_name = project_name
                
                # Submit the request
                operation = client.create_project(request={"project": project})
                result = operation.result()  # Waits for operation to complete
                
                return {
                    "status": "success",
                    "report": f"Project {project_name} ({project_id}) created successfully via API."
                }
                
            except Exception as api_error:
                print(f"API approach failed: {str(api_error)}, trying gcloud CLI.")
                # Fall through to CLI
        
        # Second approach: Use gcloud CLI
        try:
            print(f"Attempting to create project {project_id} using gcloud CLI...")
            result = subprocess.run(
                ["gcloud", "projects", "create", project_id, f"--name={project_name}"],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "status": "success",
                "report": f"Project {project_name} ({project_id}) created successfully via CLI."
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to create project using gcloud CLI: {e.stderr}"
            print(error_msg)
            return {
                "status": "error",
                "error_message": error_msg
            }
            
    except Exception as e:
        error_msg = f"An unexpected error occurred in create_gcp_project: {str(e)}"
        print(f"ERROR: {error_msg}")
        return {
            "status": "error",
            "error_message": error_msg
        }
