"""Google Cloud Platform (GCP) tools for ADK CLI Agent."""

import os
import json
import subprocess

# Check if GCP tools are available
try:
    import google.auth
    from google.cloud import resourcemanager_v3
    HAS_GCP_TOOLS = True
except ImportError:
    HAS_GCP_TOOLS = False

def list_gcp_projects(env: str) -> dict:
    """Lists Google Cloud Platform (GCP) projects for a specified environment.
    
    Args:
        env (str): The environment to list projects for (dev/stg/prod)
        
    Returns:
        dict: status and result or error message.
    """
    print(f"--- Tool: list_gcp_projects called with env={env} ---")
    
    try:
        # First approach: Try using Google Cloud Resource Manager API
        try:
            import google.auth
            from google.cloud import resourcemanager_v3
            
            # Get credentials
            credentials, _ = google.auth.default()
            
            # Create the client
            client = resourcemanager_v3.ProjectsClient(credentials=credentials)
            
            # Use search_projects instead of list_projects to avoid parent parameter issues
            request = resourcemanager_v3.SearchProjectsRequest()
            projects_list = []
            
            # Collect all projects
            for project in client.search_projects(request=request):
                # Get project details
                project_id = project.project_id
                project_name = project.display_name if project.display_name else project_id
                
                # Filter projects based on environment tag/label or naming convention
                if (env.lower() in project_id.lower() or 
                        (project_name and env.lower() in project_name.lower())):
                    projects_list.append(f"{project_name} ({project_id})")
            
            # If we found projects, return them
            if projects_list:
                return {
                    "status": "success",
                    "report": "\n".join(projects_list)
                }
            else:
                print("No matching projects found via API, trying gcloud CLI")
                # Try gcloud CLI as a fallback
                raise Exception("No matching projects found via API")
                
        except Exception as api_error:
            print(f"API approach failed: {api_error}, trying gcloud CLI")
            
            # Second approach: Try using gcloud CLI
            import subprocess
            import json
            import os
            
            try:
                # Run gcloud projects list command with JSON output format
                result = subprocess.run(
                    ['gcloud', 'projects', 'list', '--format=json'],
                    capture_output=True,
                    text=True,
                    check=True,
                    env=os.environ.copy()
                )
                
                if result.returncode == 0 and result.stdout:
                    # Parse JSON output
                    try:
                        projects_data = json.loads(result.stdout)
                        
                        # Filter projects based on environment
                        filtered_projects = []
                        for project in projects_data:
                            project_id = project.get('projectId', '')
                            project_name = project.get('name', project_id)
                            
                            # Simple filtering based on naming convention
                            if (env.lower() in project_id.lower() or 
                                    env.lower() in project_name.lower()):
                                filtered_projects.append(f"{project_name} ({project_id})")
                        
                        if filtered_projects:
                            return {
                                "status": "success",
                                "report": "\n".join(filtered_projects)
                            }
                        else:
                            # Fall back to mock data
                            raise Exception("No matching projects found via gcloud CLI")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
                        raise e
                else:
                    print(f"gcloud command failed: {result.stderr}")
                    raise Exception(f"gcloud command failed: {result.stderr}")
            except Exception as cli_error:
                print(f"CLI approach failed: {cli_error}, using mock data")
                # Both approaches failed, use mock data
                pass
            
        # Fall back to mock data if both approaches fail
        projects = []
        if env == "dev" or env == "development":
            projects = [
                "project-dev-1 (mock)", 
                "project-dev-2 (mock)", 
                "api-dev (mock)", 
                "frontend-dev (mock)"
            ]
        elif env == "stg" or env == "staging":
            projects = [
                "project-stg-1 (mock)", 
                "api-stg (mock)", 
                "frontend-stg (mock)"
            ]
        elif env == "prod" or env == "production":
            projects = [
                "project-prod-1 (mock)", 
                "api-prod (mock)", 
                "frontend-prod (mock)", 
                "backend-prod (mock)"
            ]
            
        return {
            "status": "success",
            "report": f"Using mock data (API and CLI approaches failed):\n" + "\n".join(projects)
        }
                
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An error occurred while listing GCP projects: {e}"
        }

def create_gcp_project(project_id: str, project_name: str = "", organization_id: str = "") -> dict:
    """Creates a new Google Cloud Platform (GCP) project.
    
    Args:
        project_id (str): The ID for the new project (must be globally unique)
        project_name (str, optional): The display name for the new project. 
            If not provided, project_id will be used as the name.
        organization_id (str, optional): The ID of the organization to create the project under.
            Format should be 'organizations/ORGANIZATION_ID'. If not provided, the project
            will be created without an organization or use the default organization.
        
    Returns:
        dict: status and result or error message.
    """
    print(f"--- Tool: create_gcp_project called with project_id={project_id}, "
          f"project_name={project_name}, organization_id={organization_id} ---")
    
    # If project_name is not provided or empty, use project_id as the name
    if not project_name.strip():
        project_name = project_id
    
    try:
        # First approach: Try using Google Cloud Resource Manager API
        try:
            import google.auth
            from google.cloud import resourcemanager_v3
            
            # Get credentials
            credentials, _ = google.auth.default()
            
            # Create the client
            client = resourcemanager_v3.ProjectsClient(credentials=credentials)
            
            # Create a project resource
            project = resourcemanager_v3.Project()
            project.project_id = project_id
            project.display_name = project_name
            
            # Set parent organization if provided
            request = {"project": project}
            if organization_id.strip():
                # Format should be 'organizations/ORGANIZATION_ID'
                if not organization_id.startswith('organizations/'):
                    organization_id = f'organizations/{organization_id}'
                request["parent"] = organization_id
            
            # Create the project
            operation = client.create_project(request=request)
            
            # Wait for the operation to complete
            print(f"Creating project {project_id}... This may take a minute or two.")
            result = operation.result()
            
            return {
                "status": "success",
                "report": f"Project '{project_name}' ({project_id}) created successfully."
            }
                
        except Exception as api_error:
            print(f"API approach failed: {api_error}, trying gcloud CLI")
            
            # Second approach: Try using gcloud CLI
            import subprocess
            import os
            
            try:
                # Run gcloud projects create command
                cmd = ['gcloud', 'projects', 'create', project_id, 
                       f'--name={project_name}', '--format=json']
                
                # Add organization flag if provided
                if organization_id.strip():
                    # Extract just the ID if full format is provided
                    org_id = organization_id.replace('organizations/', '')
                    cmd.append(f'--organization={org_id}')
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    env=os.environ.copy()
                )
                
                if result.returncode == 0:
                    return {
                        "status": "success",
                        "report": f"Project '{project_name}' ({project_id}) created successfully."
                    }
                else:
                    print(f"gcloud command failed: {result.stderr}")
                    raise Exception(f"gcloud command failed: {result.stderr}")
            except Exception as cli_error:
                print(f"CLI approach failed: {cli_error}")
                raise cli_error
                
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create GCP project: {e}"
        }
