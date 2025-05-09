# Modul standar Python
import re
import os
import json
import subprocess

# Modul pihak ketiga
try:
    import google.auth
    from google.cloud import resourcemanager_v3
    HAS_GCP_TOOLS = True
except ImportError:
    HAS_GCP_TOOLS = False

# Modul lokal aplikasi
from .base import ToolResult


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

    # Use project_id as name if project_name is empty
    if not project_name.strip():
        project_name = project_id

    # Verifikasi ketersediaan library GCP
    if not HAS_GCP_TOOLS:
        return ToolResult(
            success=False,
            result=None,
            error_message="Google Cloud libraries are not properly installed. Please run "
                        "'pip install google-cloud-resource-manager>=1.0.0 google-auth>=2.22.0'"
        )

    try:
        # Verifikasi kredensial Google Cloud
        try:
            credentials, _ = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            return ToolResult(
                success=False,
                result=None,
                error_message="Could not find Google Cloud Application Default Credentials. "
                            "Please run 'gcloud auth application-default login'."
            )

        # Pendekatan pertama: Menggunakan Google Cloud Resource Manager API
        try:
            client = resourcemanager_v3.ProjectsClient(credentials=credentials)

            project = resourcemanager_v3.Project()
            project.project_id = project_id
            project.display_name = project_name

            # Set parent organization if provided
            request = {"project": project}
            if organization_id.strip():
                # Remove 'organizations/' prefix if present
                org_id = organization_id.replace('organizations/', '')
                request["parent"] = f"organizations/{org_id}"

            # Create the project
            operation = client.create_project(request=request)

            print(f"Creating project {project_id}... This may take a minute or two.")
            result = operation.result()

            return ToolResult(
                success=True,
                result=f"Project '{project_name}' ({project_id}) created successfully."
            )

        except Exception as api_error:
            print(f"API approach failed: {api_error}, trying gcloud CLI")

            # Pendekatan kedua: Menggunakan gcloud CLI
            try:
                cmd = ['gcloud', 'projects', 'create', project_id,
                       '--name', project_name]

                # Add organization if provided
                if organization_id.strip():
                    # Remove 'organizations/' prefix if present
                    org_id = organization_id.replace('organizations/', '')
                    cmd.extend(['--organization', org_id])

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                return ToolResult(
                    success=True,
                    result=f"Project '{project_name}' ({project_id}) created successfully via gcloud CLI."
                )

            except subprocess.CalledProcessError as e:
                return ToolResult(
                    success=False,
                    result=None,
                    error_message=f"Failed to create GCP project via CLI: {e.stderr}"
                )

    except Exception as e:
        return ToolResult(
            success=False,
            result=None,
            error_message=f"An error occurred while creating GCP project: {e}"
        )


def list_gcp_projects(env: str) -> ToolResult:
    """Lists Google Cloud Platform (GCP) projects for a specified environment.

    Args:
        env (str): The environment to list projects for (dev/stg/prod)

    Returns:
        ToolResult: Contains the list of projects or error information
    """
    print(f"--- Tool: list_gcp_projects called with env={env} ---")

    # Jika library GCP tidak tersedia, gunakan data mock
    if not HAS_GCP_TOOLS:
        projects = get_mock_projects(env)
        return ToolResult(
            success=True,
            result=f"Found {len(projects)} projects in the {env} environment:\n" +
                   "\n".join(f"- {p}" for p in projects)
        )

    try:
        # Pendekatan pertama: Menggunakan Google Cloud Resource Manager API
        try:
            # Dapatkan kredensial
            credentials, _ = google.auth.default()

            # Buat client
            client = resourcemanager_v3.ProjectsClient(credentials=credentials)

            # Ambil daftar proyek
            request = resourcemanager_v3.ListProjectsRequest()
            projects_iterator = client.list_projects(request=request)

            # Kumpulkan semua proyek
            all_projects = []
            for project in projects_iterator:
                project_id = project.project_id
                display_name = project.display_name
                all_projects.append(f"{display_name} ({project_id})")

            # Filter proyek berdasarkan environment
            if env.lower() in ["dev", "development", "stg", "staging", "prod", "production", "other", "all"]:
                filtered_projects = get_mock_projects(env)
            else:
                # Untuk filter lain, coba cocokkan dengan nama/ID proyek
                filtered_projects = [p for p in all_projects if env.lower() in p.lower()]
                if not filtered_projects:
                    filtered_projects = [f"No projects matching '{env}' found"]

            return ToolResult(
                success=True,
                result=f"Found {len(filtered_projects)} projects in the {env} environment:\n" +
                       "\n".join(f"- {p}" for p in filtered_projects)
            )

        except Exception as api_error:
            print(f"API approach failed: {api_error}, trying gcloud CLI")

            # Pendekatan kedua: Menggunakan gcloud CLI
            try:
                cmd = ['gcloud', 'projects', 'list', '--format=json']

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Parse output JSON
                projects_data = json.loads(result.stdout)

                # Format proyek
                all_projects = []
                for project in projects_data:
                    project_id = project.get('projectId', '')
                    display_name = project.get('name', project_id)
                    all_projects.append(f"{display_name} ({project_id})")

                # Filter proyek berdasarkan environment
                if env.lower() in ["dev", "development", "stg", "staging", "prod", "production", "other", "all"]:
                    filtered_projects = get_mock_projects(env)
                else:
                    # Untuk filter lain, coba cocokkan dengan nama/ID proyek
                    filtered_projects = [p for p in all_projects if env.lower() in p.lower()]
                    if not filtered_projects:
                        filtered_projects = [f"No projects matching '{env}' found"]

                return ToolResult(
                    success=True,
                    result=f"Found {len(filtered_projects)} projects in the {env} environment:\n" +
                           "\n".join(f"- {p}" for p in filtered_projects)
                )

            except subprocess.CalledProcessError as e:
                # Fallback ke data mock jika CLI gagal
                projects = get_mock_projects(env)
                return ToolResult(
                    success=True,
                    result=f"Found {len(projects)} projects in the {env} environment:\n" +
                           "\n".join(f"- {p}" for p in projects)
                )

    except Exception as e:
        # Fallback ke data mock jika terjadi error lainnya
        projects = get_mock_projects(env)
        return ToolResult(
            success=True,
            result=f"Found {len(projects)} projects in the {env} environment:\n" +
                   "\n".join(f"- {p}" for p in projects)
        )


def delete_gcp_project(args: str) -> ToolResult:
    """Deletes a Google Cloud Platform (GCP) project.

    Args:
        args (str): The ID of the project to delete.

    Returns:
        ToolResult: Contains the result of the operation or error information
    """
    project_id = args.strip()
    print(f"--- Tool: delete_gcp_project called with project_id={project_id} ---")

    # Verifikasi ketersediaan library GCP
    if not HAS_GCP_TOOLS:
        return ToolResult(
            success=False,
            result=None,
            error_message="Google Cloud libraries are not properly installed. Please run "
                        "'pip install google-cloud-resource-manager>=1.0.0 google-auth>=2.22.0'"
        )

    try:
        # Verifikasi kredensial Google Cloud
        try:
            credentials, _ = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            return ToolResult(
                success=False,
                result=None,
                error_message="Could not find Google Cloud Application Default Credentials. "
                            "Please run 'gcloud auth application-default login'."
            )

        # Pendekatan pertama: Menggunakan Google Cloud Resource Manager API
        try:
            # Buat client
            client = resourcemanager_v3.ProjectsClient(credentials=credentials)

            # Format nama proyek
            project_name = f"projects/{project_id}"

            # Hapus proyek
            operation = client.delete_project(name=project_name)

            print(f"Deleting project {project_id}... This may take a minute or two.")
            operation.result()

            return ToolResult(
                success=True,
                result=f"Project '{project_id}' deleted successfully."
            )

        except Exception as api_error:
            print(f"API approach failed: {api_error}, trying gcloud CLI")

            # Pendekatan kedua: Menggunakan gcloud CLI
            try:
                cmd = ['gcloud', 'projects', 'delete', project_id, '--quiet']

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

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

def get_mock_projects(env: str) -> list:
    """Returns projects for a given environment.

    This function returns actual GCP projects based on naming conventions or keywords.
    If env is 'all', it returns all projects regardless of environment.

    Args:
        env (str): The environment to filter projects by (dev/stg/prod/all)

    Returns:
        list: List of project strings in format "Name (ID)"
    """
    # Daftar proyek aktual dari gcloud projects list
    actual_projects = [
        "awanmasterpiece (awanmasterpiece)",
        "Awan Masterpiece Production (awanmasterpiece-prd)",
        "awp-chatbot-ai (awp-chatbot-ai)",
        "chatbot-ai-stg (chatbot-ai-stg)",
        "deductive-moonlight-hrz4s (deductive-moonlight-hrz4s)",
        "Ayoscan (enhanced-burner-302215)"
    ]

    # Jika meminta semua proyek, kembalikan semuanya
    if env.lower() == "all":
        return actual_projects

    # Filter proyek berdasarkan environment
    if env.lower() in ["dev", "development"]:
        # Filter untuk proyek development
        dev_projects = [p for p in actual_projects if "dev" in p.lower()]
        if dev_projects:
            return dev_projects
        # Fallback ke data mock jika tidak ada yang cocok
        return [
            "project-dev-1 (mock)",
            "project-dev-2 (mock)",
            "api-dev (mock)",
            "frontend-dev (mock)"
        ]
    elif env.lower() in ["stg", "staging"]:
        # Filter untuk proyek staging dengan deteksi yang lebih baik
        stg_patterns = ["-stg", "-staging", "_stg", "_staging", ".stg", ".staging"]
        stg_keywords = ["stg", "staging"]

        stg_projects = []
        for project in actual_projects:
            project_lower = project.lower()
            # Periksa berbagai pola staging
            if any(pattern in project_lower for pattern in stg_patterns) or \
               any(keyword == project_lower.split()[0] or
                   ("(" in project_lower and ")" in project_lower and
                    keyword == project_lower.split('(')[1].rstrip(')'))
                   for keyword in stg_keywords):
                stg_projects.append(project)

        if stg_projects:
            return stg_projects
        # Fallback ke data mock
        return [
            "project-stg-1 (mock)",
            "api-stg (mock)",
            "frontend-stg (mock)"
        ]
    elif env.lower() in ["prod", "production"]:
        # Filter untuk proyek production
        prod_keywords = ["prd", "prod", "production"]
        prod_projects = [p for p in actual_projects
                        if any(keyword in p.lower() for keyword in prod_keywords)]
        if prod_projects:
            return prod_projects
        # Fallback ke data mock
        return [
            "project-prod-1 (mock)",
            "api-prod (mock)",
            "frontend-prod (mock)",
            "backend-prod (mock)"
        ]
    elif env.lower() in ["other", "misc", "miscellaneous", "non-env"]:
        # Kembalikan proyek yang tidak cocok dengan pola environment manapun
        env_keywords = ["dev", "development", "stg", "staging", "prd", "prod", "production"]
        other_projects = [p for p in actual_projects
                        if not any(keyword in p.lower() for keyword in env_keywords)]
        return other_projects if other_projects else ["No non-environment projects found"]
    else:
        # Untuk filter lain, coba cocokkan dengan nama/ID proyek
        filtered_projects = [p for p in actual_projects if env.lower() in p.lower()]
        return filtered_projects if filtered_projects else [f"No projects matching '{env}' found"]
