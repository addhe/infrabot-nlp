"""GCP Subnet management functions: list subnets for a VPC network."""

from typing import Dict, Any
from .gcp_vpc import get_vpc_details

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
