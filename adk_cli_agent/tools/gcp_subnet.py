"""GCP Subnet management functions: list subnets for a VPC network."""

import json
import subprocess
from typing import Dict, Any
from .confirmation_tools import confirm_action
from .gcp_api_utils import get_gcp_credentials
from .gcp_vpc import get_vpc_details

# Check if GCP tools are available
try:
    from google.cloud import compute_v1
    HAS_GCP_TOOLS_FLAG = True
except ImportError:
    HAS_GCP_TOOLS_FLAG = False

def list_subnets(project_id: str, network_name: str) -> Dict[str, Any]:
    """
    Lists all subnets for a given VPC network in a GCP project.

    Args:
        project_id (str): The ID of the GCP project
        network_name (str): The name of the VPC network (not a subnet name)

    Returns:
        dict: Contains status and list of subnets
    """
    # Basic validation to prevent common mistakes
    if "subnet" in network_name.lower() and not network_name.lower().endswith("-vpc"):
        print(f"[WARNING] The name '{network_name}' contains 'subnet' which suggests it might be a subnet name, not a network/VPC name")
        return {
            "status": "error",
            "message": f"The name '{network_name}' appears to be a subnet name, not a VPC network name. Please provide a VPC network name.",
            "details": "VPC network names typically end with '-vpc' and don't contain 'subnet'"
        }
        
    vpc_details = get_vpc_details(project_id, network_name)
    if vpc_details.get("status") != "success":
        return {
            "status": "error",
            "message": f"Failed to get VPC details: {vpc_details.get('message', 'Unknown error')}",
            "details": vpc_details.get("details")
        }
    network = vpc_details.get("network", {})
    subnets = network.get("subnets", [])
    return {
        "status": "success",
        "message": f"Found {len(subnets)} subnets in VPC '{network_name}' (project '{project_id}')",
        "subnets": subnets
    }

def delete_subnet(
    project_id: str,
    subnet_name: str,
    region: str
) -> Dict[str, Any]:
    """Deletes a subnet from a GCP project.
    
    Args:
        project_id (str): The ID of the GCP project
        subnet_name (str): Name of the subnet to delete
        region (str): GCP region for the subnet
        
    Returns:
        dict: Contains status and result information
    """
    print(f"--- Tool: delete_subnet called with project_id={project_id}, subnet_name={subnet_name}, region={region} ---")
    
    # Get confirmation before proceeding with deletion
    if not confirm_action(
        f"Are you sure you want to delete subnet '{subnet_name}' in region '{region}'? This action cannot be undone."
    ):
        return {
            "status": "cancelled",
            "message": f"Delete operation for subnet '{subnet_name}' was cancelled by user."
        }
    
    try:
        # First approach: Try using Google Cloud Compute API
        if HAS_GCP_TOOLS_FLAG:
            try:
                credentials = get_gcp_credentials()
                subnet_client = compute_v1.SubnetworksClient(credentials=credentials)
                
                # Try to get the subnet first to make sure it exists
                try:
                    subnet = subnet_client.get(
                        project=project_id,
                        region=region,
                        subnetwork=subnet_name
                    )
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Subnet '{subnet_name}' does not exist in region '{region}' or cannot be accessed: {str(e)}",
                        "details": str(e)
                    }
                
                # Delete the subnet
                operation = subnet_client.delete(
                    project=project_id,
                    region=region,
                    subnetwork=subnet_name
                )
                
                # Wait for the operation to complete
                result = operation.result()
                
                # If we got this far, the operation was successful
                return {
                    "status": "success",
                    "message": f"Subnet '{subnet_name}' was successfully deleted from region '{region}'.",
                    "operation": "api",
                    "subnet": {
                        "name": subnet_name,
                        "region": region
                    }
                }
            except Exception as api_e:
                # Fall through to CLI approach silently
                pass
        
        # Fallback to gcloud CLI
        cmd = [
            "gcloud", "compute", "networks", "subnets", "delete", subnet_name,
            f"--project={project_id}", f"--region={region}", "--quiet"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "status": "success",
            "message": f"Subnet '{subnet_name}' was successfully deleted from region '{region}'.",
            "operation": "cli",
            "subnet": {
                "name": subnet_name,
                "region": region
            },
            "details": result.stdout
        }
    except subprocess.CalledProcessError as e:
        error_details = e.stderr if hasattr(e, "stderr") else str(e)
        error_lower = error_details.lower() if error_details else ""
        
        # Handle known error cases
        if "not found" in error_lower or "was not found" in error_lower:
            message = f"Subnet '{subnet_name}' not found in region '{region}'. It may have been already deleted."
        elif "permission denied" in error_lower or "permissions" in error_lower or "permission_denied" in error_lower:
            message = f"You don't have sufficient permissions to delete subnet '{subnet_name}' in project '{project_id}'."
        elif "in use" in error_lower:
            message = f"Subnet '{subnet_name}' is currently in use. Please ensure there are no resources using this subnet before deleting it."
        elif "vpc network" in error_lower and "not found" in error_lower:
            message = f"The VPC network containing subnet '{subnet_name}' was not found in project '{project_id}'."
        else:
            message = f"Failed to delete subnet '{subnet_name}': {error_details}"
            
        return {
            "status": "error",
            "message": message,
            "details": error_details
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting subnet '{subnet_name}': {str(e)}",
            "details": str(e)
        }
