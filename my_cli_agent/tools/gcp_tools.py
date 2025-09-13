"""GCP tools for project management, refactored for backend use."""
import logging
from my_cli_agent.models import ToolResult

# Check if required GCP libraries are available
try:
    import google.auth
    from google.cloud import resourcemanager_v3
    HAS_GCP_TOOLS = True
except ImportError:
    HAS_GCP_TOOLS = False
    logging.warning("GCP libraries not found. GCP tools will be disabled.")

def list_gcp_projects(env: str = 'all') -> ToolResult:
    """
    Lists GCP projects using the Resource Manager API.

    Args:
        env: The environment to filter by (e.g., 'dev', 'stg', 'prod', 'all').
             Filtering is based on project ID naming conventions.

    Returns:
        A ToolResult object with the list of projects or an error.
    """
    if not HAS_GCP_TOOLS:
        return ToolResult(success=False, error_message="GCP client libraries are not installed.")

    try:
        credentials, project = google.auth.default()
        client = resourcemanager_v3.ProjectsClient(credentials=credentials)
        
        request = resourcemanager_v3.SearchProjectsRequest()
        all_projects = client.search_projects(request=request)

        filtered_projects = []
        env_lower = env.lower()

        for project in all_projects:
            project_str = f"{project.display_name} ({project.project_id})"
            
            if env_lower == 'all' or f'-{env_lower}-' in project.project_id or \
               project.project_id.startswith(f'{env_lower}-') or \
               project.project_id.endswith(f'-{env_lower}'):
                filtered_projects.append(project_str)

        if not filtered_projects:
            return ToolResult(success=True, result=f"No projects found matching the environment: '{env}'.")

        result_str = f"Found {len(filtered_projects)} projects in the '{env}' environment:\n- "
        result_str += "\n- ".join(filtered_projects)
        return ToolResult(success=True, result=result_str)

    except google.auth.exceptions.DefaultCredentialsError:
        return ToolResult(
            success=False,
            error_message="GCP authentication failed. Please configure application-default credentials."
        )
    except Exception as e:
        logging.error(f"Failed to list GCP projects: {e}", exc_info=True)
        return ToolResult(success=False, error_message=f"An unexpected error occurred while listing projects: {e}")


def create_gcp_project(project_id: str) -> ToolResult:
    """
    Creates a new GCP project. Note: This is a placeholder.
    In a real-world scenario, this would involve API calls to create the project.
    For safety, this function currently only simulates the action.
    """
    if not project_id or not all(c.isalnum() or c == '-' for c in project_id):
        return ToolResult(
            success=False,
            error_message=f"Invalid project ID: '{project_id}'. Project ID must be 6-30 characters and contain only letters, numbers, or hyphens."
        )
    
    # This is a simulation. In a real implementation, you would use
    # the Resource Manager API to create the project.
    logging.info(f"Simulating creation of GCP project: {project_id}")
    
    return ToolResult(
        success=True,
        result=f"Successfully simulated the creation of project '{project_id}'. In a real environment, this would be a live project."
    )

# Note: A delete function is intentionally omitted for safety in this backend context.
# Exposing delete operations via a chatbot requires robust authorization and confirmation mechanisms.
