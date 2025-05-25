"""Google Cloud Platform (GCP) tools for ADK CLI Agent."""

import os
import json
import subprocess

# Check if GCP tools are available
try:
    import google.auth
    from google.cloud import resourcemanager_v3
    HAS_GCP_TOOLS_FLAG = True # Renamed to avoid conflict
except ImportError:
    HAS_GCP_TOOLS_FLAG = False

def list_gcp_projects(env: str) -> dict:
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
    
    env_lower = env.lower()

    try:
        # First approach: Try using Google Cloud Resource Manager API
        try:
            # These imports are inside try-block as per original file structure
            import google.auth 
            from google.cloud import resourcemanager_v3
            
            if not HAS_GCP_TOOLS_FLAG:
                raise ImportError("Google Cloud libraries not found, skipping API approach.")

            credentials, _ = google.auth.default() # Can raise DefaultCredentialsError
            client = resourcemanager_v3.ProjectsClient(credentials=credentials)
            
            request = resourcemanager_v3.SearchProjectsRequest() # Searches projects accessible to the user
            projects_list = []
            
            for project in client.search_projects(request=request):
                project_id = project.project_id
                project_name = project.display_name if project.display_name else project_id
                
                if env_lower == "all":
                    projects_list.append(f"{project_name} ({project_id})")
                elif (env_lower in project_id.lower() or \
                      (project_name and env_lower in project_name.lower())):
                    projects_list.append(f"{project_name} ({project_id})")
            
            if projects_list:
                return {
                    "status": "success",
                    "report": "\\n".join(projects_list)
                }
            else:
                print(f"No projects matching '{env}' found via API, trying gcloud CLI.")
                raise Exception(f"No projects matching '{env}' found via API") 
                
        except (ImportError, google.auth.exceptions.DefaultCredentialsError) as cred_api_error:
            print(f"Google Cloud API setup failed: {cred_api_error}, trying gcloud CLI.")
            # Fall through to CLI
        except Exception as api_error: # Other API related errors
            print(f"API approach failed: {api_error}, trying gcloud CLI.")
            # Fall through to CLI
            
        # Second approach: Try using gcloud CLI
        # This block is reached if the API approach fails or is skipped
        try:
            import subprocess 
            import json 
            import os
            
            try:
                subprocess.run(['gcloud', '--version'], capture_output=True, text=True, check=True, timeout=5)
            except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as gcloud_check_error:
                print(f"gcloud CLI not found or not working: {gcloud_check_error}, using mock data.")
                raise Exception("gcloud CLI not available or timed out") 

            result = subprocess.run(
                ['gcloud', 'projects', 'list', '--format=json'],
                capture_output=True,
                text=True,
                check=True, 
                env=os.environ.copy(),
                timeout=30 
            )
            
            if result.stdout:
                projects_data = json.loads(result.stdout)
                filtered_projects = []
                for project in projects_data:
                    project_id = project.get('projectId', '')
                    project_name = project.get('name', project_id) 
                    
                    if env_lower == "all":
                        filtered_projects.append(f"{project_name} ({project_id})")
                    elif (env_lower in project_id.lower() or \
                          (project_name and env_lower in project_name.lower())):
                        filtered_projects.append(f"{project_name} ({project_id})")
                
                if filtered_projects:
                    return {
                        "status": "success",
                        "report": "\\n".join(filtered_projects)
                    }
                else:
                    print(f"No projects matching '{env}' found via gcloud CLI, using mock data.")
                    raise Exception(f"No projects matching '{env}' found via gcloud CLI")
            else: 
                print("gcloud command returned empty output, using mock data.")
                raise Exception("gcloud command returned empty output")

        except Exception as cli_error: 
            print(f"CLI approach failed: {cli_error}, using mock data.")
            pass 
            
        # Fall back to mock data if both API and CLI approaches fail or are skipped
        projects_mock = []
        if env_lower == "all":
            projects_mock = [
                "project-mock-all-1 (mock-id-all-1)",
                "project-mock-all-2 (mock-id-all-2)",
                "another-dev-project-mock (mock-dev-3)",
                "some-staging-project-mock (mock-stg-4)",
                "critical-prod-app-mock (mock-prod-5)"
            ]
        elif env_lower == "dev" or env_lower == "development":
            projects_mock = [
                "project-dev-1 (mock)", 
                "project-dev-2 (mock)", 
                "api-dev (mock)", 
                "frontend-dev (mock)"
            ]
        elif env_lower == "stg" or env_lower == "staging":
            projects_mock = [
                "project-stg-1 (mock)", 
                "api-stg (mock)", 
                "frontend-stg (mock)"
            ]
        elif env_lower == "prod" or env_lower == "production":
            projects_mock = [
                "project-prod-1 (mock)", 
                "api-prod (mock)", 
                "frontend-prod (mock)", 
                "backend-prod (mock)"
            ]
        
        report_detail_prefix = "API and CLI approaches failed"
        if not HAS_GCP_TOOLS_FLAG:
            report_detail_prefix = "Google Cloud libraries not installed. API/CLI attempts skipped"
        
        report_detail = f"{report_detail_prefix} for env='{env}'."

        if not projects_mock:
            report_msg = f"Using mock data: {report_detail} No mock projects to list for this environment."
        else:
            report_msg = f"Using mock data: {report_detail}\\n" + "\\n".join(projects_mock)
            
        return {
            "status": "success", 
            "report": report_msg
        }
                
    except Exception as e: 
        return {
            "status": "error",
            "error_message": f"An unexpected error occurred in list_gcp_projects: {e}"
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
    
    effective_project_name = project_name.strip() if project_name.strip() else project_id
    
    try:
        # First approach: Try using Google Cloud Resource Manager API
        try:
            import google.auth
            from google.cloud import resourcemanager_v3
            
            if not HAS_GCP_TOOLS_FLAG:
                raise ImportError("Google Cloud libraries not found, skipping API approach.")

            credentials, _ = google.auth.default()
            client = resourcemanager_v3.ProjectsClient(credentials=credentials)
            
            project = resourcemanager_v3.Project()
            project.project_id = project_id
            project.display_name = effective_project_name
            
            request_payload = {"project": project}
            if organization_id.strip():
                formatted_org_id = organization_id.strip()
                if not formatted_org_id.startswith('organizations/'):
                    formatted_org_id = f'organizations/{formatted_org_id}'
                request_payload["parent"] = formatted_org_id
            
            operation = client.create_project(request=request_payload)
            
            print(f"Creating project {project_id} via API... This may take a minute or two.")
            operation.result(timeout=120) # Wait for the operation to complete
            
            return {
                "status": "success",
                "report": f"Project '{effective_project_name}' ({project_id}) created successfully via API."
            }
                
        except (ImportError, google.auth.exceptions.DefaultCredentialsError) as cred_api_error:
            print(f"Google Cloud API setup failed for create_project: {cred_api_error}, trying gcloud CLI.")
        except Exception as api_error:
            print(f"API approach for create_project failed: {api_error}, trying gcloud CLI.")
            
        # Second approach: Try using gcloud CLI
        import subprocess
        import os
            
        try:
            subprocess.run(['gcloud', '--version'], capture_output=True, text=True, check=True, timeout=5)
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as gcloud_check_error:
            print(f"gcloud CLI not found or not working for create_project: {gcloud_check_error}")
            raise Exception(f"gcloud CLI not available or timed out: {gcloud_check_error}") # Fail if CLI not working

        cmd = ['gcloud', 'projects', 'create', project_id, 
                f'--name={effective_project_name}', '--format=json']
        
        if organization_id.strip():
            org_id_only = organization_id.strip().replace('organizations/', '')
            cmd.append(f'--organization={org_id_only}')
        
        print(f"Creating project {project_id} via gcloud CLI... This may take a minute or two.")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True, # Will raise error if gcloud command fails
            env=os.environ.copy(),
            timeout=180 # Longer timeout for project creation
        )
        
        # If check=True, non-zero return code raises an exception
        return {
            "status": "success",
            "report": f"Project '{effective_project_name}' ({project_id}) created successfully via gcloud CLI."
        }
                
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create GCP project '{project_id}': {e}"
        }
