"""GCP Subnet update functions: update subnet properties like private Google access."""

import json
import sys
import subprocess
from typing import Dict, Any, Optional

from .confirmation_tools import confirm_action
from .gcp_api_utils import get_gcp_credentials

# Check if GCP tools are available
try:
    from google.cloud import compute_v1
    HAS_GCP_TOOLS_FLAG = True
except ImportError:
    HAS_GCP_TOOLS_FLAG = False


def enable_private_google_access(
    project_id: str,
    subnet_name: str,
    region: str
) -> Dict[str, Any]:
    """Enables private Google access for an existing subnet.

    Args:
        project_id (str): The ID of the GCP project
        subnet_name (str): Name of the subnet to update
        region (str): GCP region for the subnet

    Returns:
        dict: Contains status and result information
    """
    print(f"--- Tool: enable_private_google_access called with project_id={project_id}, subnet_name={subnet_name}, region={region} ---")

    if not confirm_action(
        f"You are about to enable private Google access for subnet '{subnet_name}' in region '{region}'."
    ):
        return {"status": "cancelled", "message": "Subnet update cancelled by user."}

    try:
        # First approach: Try using Google Cloud Compute API
        if HAS_GCP_TOOLS_FLAG:
            try:
                credentials = get_gcp_credentials()
                subnet_client = compute_v1.SubnetworksClient(credentials=credentials)

                # Get the current subnet configuration
                subnet = subnet_client.get(
                    project=project_id,
                    region=region,
                    subnetwork=subnet_name
                )

                # Check if private access is already enabled
                if subnet.private_ip_google_access:
                    return {
                        "status": "success",
                        "message": f"Private Google access is already enabled for subnet '{subnet_name}' in region '{region}'.",
                        "subnet": {
                            "name": subnet_name,
                            "region": region,
                            "private_google_access": True
                        }
                    }

                # Create the patch request with private Google access enabled
                subnet_update = compute_v1.Subnetwork()
                subnet_update.private_ip_google_access = True
                
                # Set the fingerprint to avoid 400 error
                subnet_update.fingerprint = subnet.fingerprint
                
                # Use patch operation to update only the private_ip_google_access field
                update_operation = subnet_client.patch(
                    project=project_id,
                    region=region,
                    subnetwork=subnet_name,
                    subnetwork_resource=subnet_update
                )

                # Wait for operation to complete
                result = update_operation.result()
                
                return {
                    "status": "success",
                    "message": f"Successfully enabled private Google access for subnet '{subnet_name}' in region '{region}'.",
                    "subnet": {
                        "name": subnet_name,
                        "region": region,
                        "private_google_access": True
                    }
                }
            except Exception as api_error:
                # Log the API error for debugging purposes
                print(f"[DEBUG] API error: {str(api_error)}")
                # Fall through to CLI approach

        # Fallback to gcloud CLI approach
        cmd = [
            "gcloud", "compute", "networks", "subnets", "update", subnet_name,
            f"--project={project_id}",
            f"--region={region}",
            "--enable-private-ip-google-access"
        ]
        
        try:

            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return {
                "status": "success",
                "message": f"Successfully enabled private Google access for subnet '{subnet_name}' in region '{region}'.",
                "subnet": {
                    "name": subnet_name,
                    "region": region,
                    "private_google_access": True
                },
                "details": result.stdout
            }
        except subprocess.CalledProcessError as cli_e:
            # If both API and CLI approach fail, return an error
            error_details = cli_e.stderr if hasattr(cli_e, "stderr") else str(cli_e)
            return {
                "status": "error",
                "message": f"Failed to enable private Google access: {error_details}",
                "details": error_details
            }
    except subprocess.CalledProcessError as e:
        error_details = e.stderr if hasattr(e, "stderr") else str(e)
        error_lower = error_details.lower() if error_details else ""
        # Handle known error cases
        if "permission denied" in error_lower or "permission_denied" in error_lower:
            message = f"You don't have sufficient permissions to update subnet '{subnet_name}' in project '{project_id}'"
        elif "not found" in error_lower:
            message = f"Subnet '{subnet_name}' not found in region '{region}' of project '{project_id}'. Please check if the subnet name and region are correct."
        elif "unavailable" in error_lower or "timeout" in error_lower or "connection" in error_lower:
            message = f"Network or API error occurred. This may be a transient issue. Please try again later."
        else:
            message = f"Error enabling private Google access for subnet: {e}"
        return {
            "status": "error",
            "message": message,
            "details": error_details
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error enabling private Google access for subnet: {str(e)}",
            "details": str(e)
        }


def disable_private_google_access(
    project_id: str,
    subnet_name: str,
    region: str
) -> Dict[str, Any]:
    """Disables private Google access for an existing subnet.

    Args:
        project_id (str): The ID of the GCP project
        subnet_name (str): Name of the subnet to update
        region (str): GCP region for the subnet

    Returns:
        dict: Contains status and result information
    """
    print(f"--- Tool: disable_private_google_access called with project_id={project_id}, subnet_name={subnet_name}, region={region} ---")

    if not confirm_action(
        f"You are about to disable private Google access for subnet '{subnet_name}' in region '{region}'."
    ):
        return {"status": "cancelled", "message": "Subnet update cancelled by user."}

    try:
        # First approach: Try using Google Cloud Compute API
        if HAS_GCP_TOOLS_FLAG:
            try:
                credentials = get_gcp_credentials()
                subnet_client = compute_v1.SubnetworksClient(credentials=credentials)

                # Get the current subnet configuration
                subnet = subnet_client.get(
                    project=project_id,
                    region=region,
                    subnetwork=subnet_name
                )

                # Check if private access is already disabled
                if not subnet.private_ip_google_access:
                    return {
                        "status": "success",
                        "message": f"Private Google access is already disabled for subnet '{subnet_name}' in region '{region}'.",
                        "subnet": {
                            "name": subnet_name,
                            "region": region,
                            "private_google_access": False
                        }
                    }

                # Create the patch request with private Google access disabled
                subnet_update = compute_v1.Subnetwork()
                subnet_update.private_ip_google_access = False
                
                # Set the fingerprint to avoid 400 error
                subnet_update.fingerprint = subnet.fingerprint

                # Use patch operation to update only the private_ip_google_access field
                update_operation = subnet_client.patch(
                    project=project_id,
                    region=region,
                    subnetwork=subnet_name,
                    subnetwork_resource=subnet_update
                )

                # Wait for operation to complete
                result = update_operation.result()

                return {
                    "status": "success",
                    "message": f"Successfully disabled private Google access for subnet '{subnet_name}' in region '{region}'.",
                    "subnet": {
                        "name": subnet_name,
                        "region": region,
                        "private_google_access": False
                    }
                }
            except Exception as api_error:
                # Log the API error for debugging purposes
                print(f"[DEBUG] API error: {str(api_error)}")
                # Fall through to CLI approach

        # Fallback to gcloud CLI approach
        cmd = [
            "gcloud", "compute", "networks", "subnets", "update", subnet_name,
            f"--project={project_id}",
            f"--region={region}",
            "--no-enable-private-ip-google-access"
        ]

        try:
            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return {
                "status": "success",
                "message": f"Successfully disabled private Google access for subnet '{subnet_name}' in region '{region}'.",
                "subnet": {
                    "name": subnet_name,
                    "region": region,
                    "private_google_access": False
                },
                "details": result.stdout
            }
        except subprocess.CalledProcessError as cli_e:
            # If both API and CLI approach fail, return an error
            error_details = cli_e.stderr if hasattr(cli_e, "stderr") else str(cli_e)
            return {
                "status": "error",
                "message": f"Failed to disable private Google access: {error_details}",
                "details": error_details
            }
    except subprocess.CalledProcessError as e:
        error_details = e.stderr if hasattr(e, "stderr") else str(e)
        error_lower = error_details.lower() if error_details else ""
        # Handle known error cases
        if "permission denied" in error_lower or "permission_denied" in error_lower:
            message = f"You don't have sufficient permissions to update subnet '{subnet_name}' in project '{project_id}'"
        elif "not found" in error_lower:
            message = f"Subnet '{subnet_name}' not found in region '{region}' of project '{project_id}'. Please check if the subnet name and region are correct."
        elif "unavailable" in error_lower or "timeout" in error_lower or "connection" in error_lower:
            message = f"Network or API error occurred. This may be a transient issue. Please try again later."
        else:
            message = f"Error disabling private Google access for subnet: {e}"
        return {
            "status": "error",
            "message": message,
            "details": error_details
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error disabling private Google access for subnet: {str(e)}",
            "details": str(e)
        }
