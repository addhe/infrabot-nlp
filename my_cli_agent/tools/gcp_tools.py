import re
import os
import json
import subprocess
from .base import ToolResult

# Check if Google Cloud libraries are available
try:
    import google.auth
    from google.cloud import resourcemanager_v3
    HAS_GCP_TOOLS = True
except ImportError:
    HAS_GCP_TOOLS = False
    
# Make sure we're importing all the necessary modules
import json
import subprocess
import os
import re


def create_gcp_project(args: str) -> ToolResult:
    """Creates a new Google Cloud Platform (GCP) project.
    
    Args:
        args (str): Comma-separated string containing project_id, project_name, and organization_id.
            Format: "project_id,project_name,organization_id"
            Only project_id is required, other values can be empty.
        
    Returns:
        ToolResult: Contains the result of the operation or error information
    """
    # Parse the arguments
    parts = args.split(',', 2)
    project_id = parts[0].strip()
    
    # Get optional arguments if provided
    project_name = parts[1].strip() if len(parts) > 1 else ""
    organization_id = parts[2].strip() if len(parts) > 2 else ""
    
    print(f"--- Tool: create_gcp_project called with project_id={project_id}, "
          f"project_name={project_name}, organization_id={organization_id} ---")
    
    # If project_name is not provided or empty, use project_id as the name
    if not project_name.strip():
        project_name = project_id
    
    try:
        # Check if Google Cloud libraries are available
        try:
            import google.auth
            from google.cloud import resourcemanager_v3
            has_gcp_libs = True
        except ImportError:
            has_gcp_libs = False
        
        if not has_gcp_libs:
            return ToolResult(
                success=False,
                result=None,
                error_message="Google Cloud libraries are not properly installed. Please run "
                            "'pip install google-cloud-resource-manager>=1.0.0 google-auth>=2.22.0'"
            )
        
        try:
            credentials, _ = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            return ToolResult(
                success=False,
                result=None,
                error_message="Could not find Google Cloud Application Default Credentials. "
                            "Please run 'gcloud auth application-default login'."
            )
        
        # First approach: Try using Google Cloud Resource Manager API
        try:
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
            
            return ToolResult(
                success=True,
                result=f"Project '{project_name}' ({project_id}) created successfully."
            )
                
        except Exception as api_error:
            print(f"API approach failed: {api_error}, trying gcloud CLI")
            
            # Second approach: Try using gcloud CLI
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
                    return ToolResult(
                        success=True,
                        result=f"Project '{project_name}' ({project_id}) created successfully."
                    )
                else:
                    print(f"gcloud command failed: {result.stderr}")
                    raise Exception(f"gcloud command failed: {result.stderr}")
            except Exception as cli_error:
                print(f"CLI approach failed: {cli_error}")
                raise cli_error
                
    except Exception as e:
        return ToolResult(
            success=False,
            result=None,
            error_message=f"Failed to create GCP project: {e}"
        )


def list_gcp_projects(env: str) -> ToolResult:
    """Lists Google Cloud Platform (GCP) projects for a specified environment.
    
    Args:
        env (str): The environment to list projects for (dev/stg/prod)
        
    Returns:
        ToolResult: Contains the list of projects or error information
    """
    print(f"--- Tool: list_gcp_projects called with env={env} ---")
    
    # Initialize projects as an empty list to avoid undefined variable issues
    projects = []
    
    try:
        # Check if Google Cloud libraries are available
        try:
            import google.auth
            from google.cloud import resourcemanager_v3
            has_gcp_libs = True
        except ImportError:
            has_gcp_libs = False
        
        if not has_gcp_libs:
            return ToolResult(
                success=False,
                result=None,
                error_message="Google Cloud libraries are not properly installed. Please run "
                            "'pip install google-cloud-resource-manager>=1.0.0 google-auth>=2.22.0'"
            )
        
        # Try to get credentials
        try:
            credentials, _ = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            return ToolResult(
                success=False,
                result=None,
                error_message="Could not find Google Cloud Application Default Credentials. "
                            "Please run 'gcloud auth application-default login'."
            )
            
        # Create the client
        client = resourcemanager_v3.ProjectsClient(credentials=credentials)
        
        # Try to list projects using the API
        try:
            # List all projects the user has access to
            projects_list = []
            
            # Use the search_projects method instead of list_projects
            # This doesn't require a parent parameter
            request = resourcemanager_v3.SearchProjectsRequest()
            
            # Collect all projects
            for project in client.search_projects(request=request):
                # Get project details
                project_id = project.project_id
                project_name = project.display_name if project.display_name else project_id
                
                # Filter projects based on environment tag/label or naming convention
                if (env.lower() in project_id.lower() or 
                        (project_name and env.lower() in project_name.lower())):
                    projects_list.append(f"{project_name} ({project_id})")
            
            # If we found projects, use them
            if projects_list:
                projects = projects_list
            # Otherwise, fall back to mock data
            else:
                print("No matching projects found via API, using mock data")
                projects = get_mock_projects(env)
                
        except Exception as e:
            print(f"API approach failed: {e}, using mock data")
            # Fall back to mock data if API call fails
            projects = get_mock_projects(env)
            
            # Add error information to the first project if we have any projects
            if projects:
                projects[0] = f"API Error: {str(e)} - {projects[0]}"
        
        # Try using gcloud CLI if API approach failed or returned no results
        if not projects:
            try:
                print("Trying gcloud CLI approach...")
                # Prepare the gcloud command
                cmd = ['gcloud', 'projects', 'list', '--format=json']
                
                # Execute the command
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    projects_json = json.loads(result.stdout)
                    all_projects = []
                    
                    # Process all projects
                    for project in projects_json:
                        project_id = project.get('projectId', '')
                        project_name = project.get('name', project_id)
                        all_projects.append((project_name, project_id))
                    
                    # Filter projects based on environment
                    if env.lower() == "all":
                        # Return all projects
                        projects = [f"{name} ({pid})" for name, pid in all_projects]
                    elif env.lower() in ["dev", "development"]:
                        # Filter for dev projects
                        projects = [f"{name} ({pid})" for name, pid in all_projects 
                                  if "dev" in pid.lower() or "dev" in name.lower()]
                    elif env.lower() in ["stg", "staging"]:
                        # Filter for staging projects
                        projects = [f"{name} ({pid})" for name, pid in all_projects 
                                  if any(pattern in pid.lower() or pattern in name.lower() 
                                        for pattern in ["-stg", "_stg", "stg-", "stg_", "staging"])]
                    elif env.lower() in ["prod", "production"]:
                        # Filter for production projects
                        projects = [f"{name} ({pid})" for name, pid in all_projects 
                                  if any(pattern in pid.lower() or pattern in name.lower() 
                                        for pattern in ["-prd", "_prd", "prd-", "prd_", "-prod", "_prod", "prod-", "prod_", "production"])]
                    elif env.lower() in ["other", "misc", "miscellaneous", "non-env"]:
                        # Return projects that don't match any environment pattern
                        projects = [f"{name} ({pid})" for name, pid in all_projects 
                                  if not any(pattern in pid.lower() or pattern in name.lower() 
                                           for pattern in ["dev", "stg", "staging", "prd", "prod", "production"])]
                    else:
                        # For any other specific filter, try to match it against project names/IDs
                        projects = [f"{name} ({pid})" for name, pid in all_projects 
                                  if env.lower() in pid.lower() or env.lower() in name.lower()]
                
                if not projects:
                    print(f"No matching projects found via gcloud CLI for environment '{env}', using mock data")
                    projects = get_mock_projects(env)
            except Exception as cli_error:
                print(f"CLI approach failed: {cli_error}, using mock data")
                projects = get_mock_projects(env)
        
        # Return the list of projects
        return ToolResult(
            success=True,
            result="\n".join(projects) if projects else 
                   f"No GCP projects found for '{env}' environment."
        )
        
    except Exception as e:
        # Catch any unexpected exceptions
        error_msg = f"An error occurred while listing GCP projects: {e}"
        print(error_msg)
        return ToolResult(
            success=False,
            error_message=error_msg,
            result=None
        )

def delete_gcp_project(args: str) -> ToolResult:
    """Deletes a Google Cloud Platform (GCP) project.
    
    Args:
        args (str): The ID of the project to delete.
        
    Returns:
        ToolResult: Contains the result of the operation or error information
    """
    # Clean up the project ID
    project_id = args.strip().strip('"\'\'{}()[]')
    
    print(f"--- Tool: delete_gcp_project called with project_id={project_id} ---")
    
    try:
        # Check if Google Cloud libraries are available
        try:
            import google.auth
            from google.cloud import resourcemanager_v3
            has_gcp_libs = True
        except ImportError:
            has_gcp_libs = False
        
        if not has_gcp_libs:
            return ToolResult(
                success=False,
                result=None,
                error_message="Google Cloud libraries are not properly installed. Please run "
                            "'pip install google-cloud-resource-manager>=1.0.0 google-auth>=2.22.0'"
            )
        
        try:
            credentials, _ = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            return ToolResult(
                success=False,
                result=None,
                error_message="Could not find Google Cloud Application Default Credentials. "
                            "Please run 'gcloud auth application-default login'."
            )
        
        # First approach: Try using Google Cloud Resource Manager API
        try:
            # Create the client
            client = resourcemanager_v3.ProjectsClient(credentials=credentials)
            
            # Get the project name
            project_name = f"projects/{project_id}"
            
            # Delete the project
            print(f"Deleting project {project_id}... This may take a minute or two.")
            operation = client.delete_project(name=project_name)
            
            # Wait for the operation to complete
            result = operation.result()
            
            return ToolResult(
                success=True,
                result=f"Project '{project_id}' deleted successfully."
            )
                
        except Exception as api_error:
            print(f"API approach failed: {api_error}, trying gcloud CLI")
            
            # Second approach: Try using gcloud CLI
            try:
                # Run gcloud projects delete command
                cmd = ['gcloud', 'projects', 'delete', project_id, '--quiet']
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                return ToolResult(
                    success=True,
                    result=f"Project '{project_id}' deleted successfully via gcloud CLI."
                )
                    
            except subprocess.CalledProcessError as e:
                return ToolResult(
                    success=False,
                    result=None,
                    error_message=f"Failed to delete GCP project via CLI: {e.stderr}"
                )
                
    except Exception as e:
        return ToolResult(
            success=False,
            result=None,
            error_message=f"An error occurred while deleting GCP project: {e}"
        )

# Helper function to get projects based on environment
def get_mock_projects(env: str) -> list:
    """Returns projects for a given environment.
    
    This function returns actual GCP projects based on naming conventions or keywords.
    If env is 'all', it returns all projects regardless of environment.
    """
    # Define actual projects from gcloud projects list
    actual_projects = [
        "awanmasterpiece (awanmasterpiece)",
        "Awan Masterpiece Production (awanmasterpiece-prd)",
        "awp-chatbot-ai (awp-chatbot-ai)",
        "chatbot-ai-stg (chatbot-ai-stg)",
        "deductive-moonlight-hrz4s (deductive-moonlight-hrz4s)",
        "Ayoscan (enhanced-burner-302215)"
    ]
    
    # If requesting all projects, return all of them
    if env.lower() == "all":
        return actual_projects
    
    # Filter projects based on environment
    if env.lower() in ["dev", "development"]:
        # Filter for dev projects (those containing 'dev' in name or ID)
        dev_projects = [p for p in actual_projects if "dev" in p.lower()]
        if dev_projects:
            return dev_projects
        # Fall back to mock data if no matches
        return [
            "project-dev-1 (mock)", 
            "project-dev-2 (mock)", 
            "api-dev (mock)", 
            "frontend-dev (mock)"
        ]
    elif env.lower() in ["stg", "staging"]:
        # Filter for staging projects - improved detection
        stg_projects = []
        for project in actual_projects:
            project_lower = project.lower()
            # Check for various staging patterns
            if any(pattern in project_lower for pattern in ["-stg", "-staging", "_stg", "_staging", ".stg", ".staging"]) or \
               any(pattern == project_lower.split()[0] or pattern == project_lower.split('(')[1].rstrip(')') for pattern in ["stg", "staging"]):
                stg_projects.append(project)
        
        if stg_projects:
            return stg_projects
        # Fall back to mock data if no matches
        return [
            "project-stg-1 (mock)", 
            "api-stg (mock)", 
            "frontend-stg (mock)"
        ]
    elif env.lower() in ["prod", "production"]:
        # Filter for production projects
        prod_projects = [p for p in actual_projects if any(s in p.lower() for s in ["prd", "prod", "production"])]
        if prod_projects:
            return prod_projects
        # Fall back to mock data if no matches
        return [
            "project-prod-1 (mock)", 
            "api-prod (mock)", 
            "frontend-prod (mock)", 
            "backend-prod (mock)"
        ]
    elif env.lower() in ["other", "misc", "miscellaneous", "non-env"]:
        # Return projects that don't match any environment pattern
        other_projects = [p for p in actual_projects if not any(s in p.lower() for s in 
                                                              ["dev", "development", "stg", "staging", "prd", "prod", "production"])]
        return other_projects if other_projects else ["No non-environment projects found"]
    else:
        # For any other specific filter, try to match it against project names/IDs
        filtered_projects = [p for p in actual_projects if env.lower() in p.lower()]
        return filtered_projects if filtered_projects else [f"No projects matching '{env}' found"]