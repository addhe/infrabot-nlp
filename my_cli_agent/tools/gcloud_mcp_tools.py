import os
import logging
import requests
from my_cli_agent.models import ToolResult
from typing import Dict, Any, List

def _call_gcloud_mcp(tool_name: str, params: Dict[str, Any]) -> ToolResult:
    """Helper function to send a command to the gcloud MCP server.

    Behavior:
    1) Try calling the base URL (no "/mcp" suffix) with payload using the "input" key.
    2) If that fails (HTTP error like 404/405) or the response body is empty, fallback to calling
       the "/mcp" endpoint with payload using the legacy "params" key.
    """
    server_url = os.getenv("GCLOUD_MCP_SERVER_URL")
    if not server_url:
        return ToolResult(
            success=False,
            error_message="GCLOUD_MCP_SERVER_URL environment variable is not set. gcloud tools are disabled."
        )

    # Ensure base URL ends with '/'
    base_url = server_url if server_url.endswith('/') else server_url + '/'
    primary_url = base_url  # root path
    fallback_url = base_url + 'mcp'  # legacy path

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain;q=0.8,*/*;q=0.5",
    }

    primary_payload = {
        "tool": tool_name,
        "input": params,
    }

    # Try primary (root + input)
    try:
        response = requests.post(primary_url, json=primary_payload, headers=headers, timeout=120)
        if 200 <= response.status_code < 300 and response.text:
            return ToolResult(success=True, result=response.text)
        # If 2xx but empty body, treat as failure to allow fallback
        if 200 <= response.status_code < 300 and not response.text:
            logging.warning("gcloud MCP primary call returned 2xx but empty body; attempting fallback to /mcp ...")
        else:
            # Non-2xx -> will try fallback
            logging.warning(f"gcloud MCP primary call returned status {response.status_code}; attempting fallback to /mcp ...")
    except requests.exceptions.Timeout:
        # On timeout, try fallback
        logging.warning("gcloud MCP primary call timed out; attempting fallback to /mcp ...")
    except requests.exceptions.RequestException as e:
        logging.warning(f"gcloud MCP primary call failed: {e}; attempting fallback to /mcp ...")
    except Exception as e:
        logging.warning(f"Unexpected error during gcloud MCP primary call: {e}; attempting fallback to /mcp ...", exc_info=True)

    # Fallback (root + 'mcp' + params)
    fallback_payload = {
        "tool": tool_name,
        "params": params,
    }
    try:
        response = requests.post(fallback_url, json=fallback_payload, headers=headers, timeout=120)
        response.raise_for_status()
        # Accept empty body as a valid success in fallback mode to avoid hard failures
        if not response.text:
            logging.info("gcloud MCP fallback call returned 2xx with empty body; treating as success with empty result.")
            return ToolResult(success=True, result="")
        return ToolResult(success=True, result=response.text)
    except requests.exceptions.Timeout:
        return ToolResult(success=False, error_message="The request to the gcloud MCP server timed out (120 seconds) [fallback mode].")
    except requests.exceptions.RequestException as e:
        return ToolResult(success=False, error_message=f"Failed to connect to the gcloud MCP server (fallback mode): {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred calling gcloud MCP (fallback mode): {e}", exc_info=True)
        return ToolResult(success=False, error_message=f"An unexpected error occurred (fallback mode): {e}")

def run_gcloud_command(command: List[str]) -> ToolResult:
    """
    Executes a gcloud command via the gcloud-mcp server.
    The command should be provided as a list of strings.
    Example: ['compute', 'instances', 'list']
    """
    if not isinstance(command, list):
        return ToolResult(success=False, error_message="Invalid input: command must be a list of strings.")
    # The MCP server expects the parameter to be named 'args' within either 'input' or 'params'.
    return _call_gcloud_mcp("run_gcloud_command", {"args": command})

def create_small_ubuntu_vm(
    name: str | None = None,
    project: str | None = None,
    zone: str = "us-central1-a",
    labels: Dict[str, str] | None = None,
    boot_disk_size_gb: int = 10,
    gcp_project_id: str | None = None,
    **kwargs: Any,
) -> ToolResult:
    """
    Convenience tool: create a minimal Ubuntu VM using default network/subnet.

    - machine: e2-micro
    - image: ubuntu-2204-lts (ubuntu-os-cloud)
    - boot disk: pd-standard, 10GB (configurable)
    - network/subnet: default

    Returns ToolResult with raw MCP response text on success.
    """
    # Allow alias 'gcp_project_id' (from some callers) and ignore extra kwargs
    # Also accept alias for name (e.g., vm_name, instance_name)
    if not name:
        name = kwargs.get("vm_name") or kwargs.get("instance_name") or kwargs.get("resource_name")

    if not project and gcp_project_id:
        project = gcp_project_id
    # Map additional project aliases from kwargs
    if not project:
        project = (
            kwargs.get("project_id")
            or kwargs.get("gcp_project")
            or kwargs.get("google_project")
            or kwargs.get("projectName")
            or kwargs.get("project")
        )

    if not name or not project:
        return ToolResult(success=False, error_message="Both 'name' and 'project' are required.")

    label_str = None
    if labels:
        # join as key=value pairs separated by comma
        label_str = ",".join([f"{k}={v}" for k, v in labels.items()])
    else:
        label_str = "owner=infrabot,env=dev"

    args: List[str] = [
        "compute", "instances", "create", name,
        f"--project={project}",
        f"--zone={zone}",
        "--machine-type=e2-micro",
        "--image-family=ubuntu-2204-lts",
        "--image-project=ubuntu-os-cloud",
        f"--boot-disk-size={boot_disk_size_gb}GB",
        "--boot-disk-type=pd-standard",
        "--network=default",
        "--subnet=default",
        f"--labels={label_str}",
        "--quiet",
    ]

    return _call_gcloud_mcp("run_gcloud_command", {"args": args})

def create_compute_instance(
    name: str | None = None,
    project: str | None = None,
    zone: str | None = None,
    machine_type: str | None = None,
    image_family: str | None = None,
    image_project: str | None = None,
    image: str | None = None,
    boot_disk_size_gb: int = 10,
    boot_disk_type: str = "pd-standard",
    network: str = "default",
    subnet: str = "default",
    labels: Dict[str, str] | None = None,
    additional_args: List[str] | None = None,
    gcp_project_id: str | None = None,
    **kwargs: Any,
) -> ToolResult:
    """
    Generic tool to create a Compute Engine VM using gcloud via MCP.

    Provide either:
      - image (full selfLink or image name in a project), or
      - image_family + image_project

    Example combinations:
      image_family="ubuntu-2204-lts", image_project="ubuntu-os-cloud"
      image="projects/rhel-cloud/global/images/family/rhel-9"
      image="windows-cloud/windows-server-2022-dc-v20240910"
    """
    # Accept alias and ignore extra kwargs for robustness
    # Map common alternative argument names coming from LLM/tooling
    if not name:
        name = (
            kwargs.get("vm_name")
            or kwargs.get("instance_name")
            or kwargs.get("resource_name")
        )

    if not project and gcp_project_id:
        project = gcp_project_id
    if not project:
        project = (
            kwargs.get("project_id")
            or kwargs.get("gcp_project")
            or kwargs.get("google_project")
            or kwargs.get("projectName")
            or kwargs.get("project")
        )

    if not zone:
        zone = kwargs.get("gcp_zone")
        if not zone:
            # If only region given, pick '-a' by default
            region = kwargs.get("gcp_region") or kwargs.get("region")
            zone = f"{region}-a" if region else "us-central1-a"

    if not machine_type:
        machine_type = (
            kwargs.get("machine")
            or kwargs.get("machineType")
            or kwargs.get("instance_type")
            or kwargs.get("flavor")
            or "e2-micro"
        )

    if not all([name, project, zone, machine_type]):
        return ToolResult(success=False, error_message="'name', 'project', 'zone', and 'machine_type' are required.")

    img_flags: List[str] = []
    if image:
        img_flags.extend([f"--image={image}"])
    elif image_family and image_project:
        img_flags.extend([f"--image-family={image_family}", f"--image-project={image_project}"])
    else:
        # Default to Ubuntu LTS if not specified
        image_family = "ubuntu-2204-lts"
        image_project = "ubuntu-os-cloud"
        img_flags.extend([f"--image-family={image_family}", f"--image-project={image_project}"])

    label_str = None
    if labels:
        label_str = ",".join([f"{k}={v}" for k, v in labels.items()])
    else:
        label_str = "owner=infrabot,env=dev"

    args: List[str] = [
        "compute", "instances", "create", name,
        f"--project={project}",
        f"--zone={zone}",
        f"--machine-type={machine_type}",
        *img_flags,
        f"--boot-disk-size={boot_disk_size_gb}GB",
        f"--boot-disk-type={boot_disk_type}",
        f"--network={network}",
        f"--subnet={subnet}",
        f"--labels={label_str}",
        "--quiet",
    ]

    if additional_args:
        args.extend(additional_args)

    return _call_gcloud_mcp("run_gcloud_command", {"args": args})
