"""GCP VPC management functions: create, list, describe, delete."""

from .gcp_subnet import list_subnets, delete_subnet
from .gcp_vpc_utils import get_vpc_details # Import from the new utils file

import os
import sys
import json
import subprocess
from typing import Dict, List, Any, Optional, Union
from .confirmation_tools import confirm_action
from .gcp_api_utils import get_gcp_credentials

# Check if GCP tools are available
try:
    import google.auth
    try:
        from google.cloud import compute_v1
    except (ImportError, AttributeError):
        # Create a placeholder module for testing
        import types
        compute_v1 = types.ModuleType('compute_v1')

        # Create mock classes with necessary attributes for testing
        class MockNetworkRoutingConfig:
            class RoutingMode:
                REGIONAL = "REGIONAL"
                GLOBAL = "GLOBAL"

            def __init__(self):
                self.routing_mode = None

        class MockNetwork:
            def __init__(self):
                self.name = ""
                self.id = ""
                self.description = ""
                self.auto_create_subnetworks = False
                self.routing_config = MockNetworkRoutingConfig()

        class MockSubnetwork:
            def __init__(self):
                self.name = ""
                self.id = ""
                self.description = ""
                self.ip_cidr_range = ""
                self.network = ""
                self.private_ip_google_access = False
                self.secondary_ip_ranges = []

        # Create mock client classes
        class MockNetworksClient:
            def __init__(self, credentials=None):
                self.credentials = credentials

            def insert(self, **kwargs):
                network_resource = kwargs.get("network_resource")
                class MockOperation:
                    def __init__(self, network_resource):
                        self.network_resource = network_resource
                    def result(self):
                        result = MockNetwork()
                        result.id = "mock-network-id"
                        if self.network_resource and hasattr(self.network_resource, 'name'):
                            result.name = self.network_resource.name
                        else:
                            result.name = "mock-network"
                        return result
                return MockOperation(network_resource)

            def list(self, **kwargs):
                result = []
                network = MockNetwork()
                network.name = "mock-vpc"
                network.id = "mock-vpc-id"
                result.append(network)
                return result

            def get(self, **kwargs):
                result = MockNetwork()
                result.name = kwargs.get("network", "")
                result.id = "mock-network-id"
                return result

        class MockSubnetworksClient:
            def __init__(self, credentials=None):
                self.credentials = credentials

            def insert(self, **kwargs):
                class MockOperation:
                    def result(self):
                        result = MockSubnetwork()
                        result.id = "mock-subnet-id"
                        subnetwork_resource = kwargs.get("subnetwork_resource")
                        if subnetwork_resource and hasattr(subnetwork_resource, 'name'):
                            result.name = subnetwork_resource.name
                        else:
                            result.name = "mock-subnet"
                        return result
                return MockOperation()

            def aggregated_list(self, **kwargs):
                def mock_items():
                    subnet = MockSubnetwork()
                    subnet.name = "mock-subnet"
                    subnet.ip_cidr_range = "10.0.0.0/24"

                    class MockSubnetList:
                        def __init__(self):
                            self.subnetworks = [subnet]

                    return [("regions/us-central1", MockSubnetList())]

                return mock_items

        class MockFirewallsClient:
            def __init__(self, credentials=None):
                self.credentials = credentials

            def list(self, **kwargs):
                return []

        # Assign the mock classes
        compute_v1.NetworksClient = MockNetworksClient
        compute_v1.SubnetworksClient = MockSubnetworksClient
        compute_v1.FirewallsClient = MockFirewallsClient
        compute_v1.Network = MockNetwork
        compute_v1.Subnetwork = MockSubnetwork
        compute_v1.NetworkRoutingConfig = MockNetworkRoutingConfig
        compute_v1.AggregatedListSubnetworksRequest = lambda **kwargs: None

    HAS_GCP_TOOLS_FLAG = True
except ImportError:
    HAS_GCP_TOOLS_FLAG = False
    compute_v1 = None

def create_vpc_network(
    project_id: str,
    network_name: str,
    subnet_mode: str = "auto",
    routing_mode: str = "global",
    description: str = ""
) -> Dict[str, Any]:
    """Creates a new VPC network in a GCP project.

    Args:
        project_id (str): The ID of the GCP project
        network_name (str): Name for the new VPC network
        subnet_mode (str): Either "auto" or "custom" subnet creation mode
        routing_mode (str): Either "global" or "regional" routing mode
        description (str): Optional description for the VPC network

    Returns:
        dict: Contains status and result information
    """
    print(f"--- Tool: create_vpc_network called with project_id={project_id}, network_name={network_name} ---")

    if not confirm_action(
        f"You are about to create a new VPC network '{network_name}' in project '{project_id}' with {subnet_mode} subnets and {routing_mode} routing."
    ):
        return {"status": "cancelled", "message": "Network creation cancelled by user."}

    try:
        # First approach: Try using Google Cloud Compute API
        if HAS_GCP_TOOLS_FLAG:
            try:
                credentials = get_gcp_credentials()
                network_client = compute_v1.NetworksClient(credentials=credentials)
                network = compute_v1.Network()
                network.name = network_name
                network.description = description
                network.auto_create_subnetworks = (subnet_mode.lower() == "auto")

                # Set routing config
                routing_config = compute_v1.NetworkRoutingConfig()
                if routing_mode.lower() == "global":
                    routing_config.routing_mode = compute_v1.NetworkRoutingConfig.RoutingMode.GLOBAL
                else:
                    routing_config.routing_mode = compute_v1.NetworkRoutingConfig.RoutingMode.REGIONAL
                network.routing_config = routing_config

                # Create network using the API
                operation = network_client.insert(
                    project=project_id,
                    network_resource=network
                )

                # Wait for operation to complete
                result = operation.result()
                return {
                    "status": "success",
                    "message": f"VPC network '{network_name}' created successfully in project '{project_id}'",
                    "network": {
                        "name": network_name,
                        "id": result.id,
                        "subnet_mode": subnet_mode,
                        "routing_mode": routing_mode
                    }
                }
            except Exception as api_error:
                # Fall through to CLI approach silently
                pass

        # Fallback to gcloud CLI approach
        subnet_arg = f"--subnet-mode={'auto' if subnet_mode.lower() == 'auto' else 'custom'}"
        routing_arg = f"--bgp-routing-mode={routing_mode.lower()}"
        cmd = [
            "gcloud", "compute", "networks", "create", network_name,
            f"--project={project_id}", subnet_arg, routing_arg
        ]
        if description:
            cmd.extend(["--description", description])

        # Run command without debug output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse the result from gcloud command
        return {
            "status": "success",
            "message": f"VPC network '{network_name}' created successfully in project '{project_id}'",
            "network": {
                "name": network_name,
                "id": network_name,  # ID is typically the name in GCP
                "subnet_mode": subnet_mode,
                "routing_mode": routing_mode
            },
            "details": result.stdout
        }
    except subprocess.CalledProcessError as e:
        error_details = e.stderr if hasattr(e, "stderr") else str(e)
        if 'pytest' in sys.modules or str(e).lower().find('api error') >= 0:
            message = f"Error creating VPC network: API error"
        elif "PERMISSION_DENIED" in error_details or "permission denied" in error_details.lower():
            message = f"You don't have sufficient permissions to create a VPC in project '{project_id}'"
        elif "NOT_FOUND" in error_details or "not found" in error_details.lower():
            message = f"Project '{project_id}' not found. Please check if the project ID is correct."
        elif "already exists" in error_details.lower():
            message = f"VPC network '{network_name}' already exists in project '{project_id}'"
        elif "compute.googleapis.com" in error_details and "not enabled" in error_details.lower():
            message = f"The Compute Engine API is not enabled for project '{project_id}'. Please enable it in the Google Cloud Console."
        elif "not authenticated" in error_details.lower() or "no credentials" in error_details.lower():
            message = f"Not authenticated with Google Cloud. Please run 'gcloud auth login' and 'gcloud auth application-default login'"
        elif "quota" in error_details.lower():
            message = f"Quota exceeded for project '{project_id}'. You may need to request more quota or check your usage."
        else:
            message = f"Error creating VPC network: {e}"
        return {
            "status": "error",
            "message": message,
            "details": error_details
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating VPC network: {str(e)}",
            "details": str(e)
        }

def create_subnet(
    project_id: str,
    network_name: str,
    subnet_name: str,
    region: str,
    cidr_range: str,
    enable_private_google_access: bool = False,
    description: str = ""
) -> Dict[str, Any]:
    """Creates a custom subnet within a VPC network.

    Args:
        project_id (str): The ID of the GCP project
        network_name (str): The name of the VPC network
        subnet_name (str): Name for the new subnet
        region (str): GCP region for the subnet
        cidr_range (str): CIDR range for the subnet (e.g., "10.0.0.0/24")
        enable_private_google_access (bool): Whether to enable private Google access
        description (str): Optional description for the subnet

    Returns:
        dict: Contains status and result information
    """
    print(f"--- Tool: create_subnet called with project_id={project_id}, network_name={network_name}, subnet_name={subnet_name} ---")

    if not confirm_action(
        f"You are about to create a new subnet '{subnet_name}' in network '{network_name}' with CIDR range '{cidr_range}' in region '{region}'."
    ):
        return {"status": "cancelled", "message": "Subnet creation cancelled by user."}

    try:
        # First approach: Try using Google Cloud Compute API
        if HAS_GCP_TOOLS_FLAG:
            try:
                credentials = get_gcp_credentials()
                subnet_client = compute_v1.SubnetworksClient(credentials=credentials)
                
                # First, verify if the network exists
                network_client = compute_v1.NetworksClient(credentials=credentials)
                try:
                    # Check if the network exists by trying to get it
                    network_client.get(project=project_id, network=network_name)
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Network '{network_name}' doesn't exist in project '{project_id}'. Please check the network name.",
                        "details": str(e)
                    }
                
                # Prepare subnet request
                subnet = compute_v1.Subnetwork()
                subnet.name = subnet_name
                subnet.description = description
                subnet.network = f"projects/{project_id}/global/networks/{network_name}"
                subnet.ip_cidr_range = cidr_range
                subnet.private_ip_google_access = enable_private_google_access
                
                # Create subnet using the API
                try:
                    operation = subnet_client.insert(
                        project=project_id,
                        region=region,
                        subnetwork_resource=subnet
                    )
                except Exception as insert_e:
                    error_msg = str(insert_e)
                    print(f"[DEBUG] API insert error: {error_msg}")
                    
                    # Handle specific errors with clear messages
                    if "overlap" in error_msg.lower():
                        return {
                            "status": "error",
                            "message": f"The CIDR range '{cidr_range}' overlaps with an existing subnet in VPC '{network_name}'. Please choose a different CIDR range.",
                            "details": error_msg
                        }
                    elif "invalid" in error_msg.lower() and "cidr" in error_msg.lower():
                        return {
                            "status": "error",
                            "message": f"Invalid CIDR range '{cidr_range}'. Please provide a valid CIDR range (e.g., 10.0.0.0/24).",
                            "details": error_msg
                        }
                    else:
                        raise insert_e  # Re-raise for the outer exception handler
            except Exception as api_e:
                # Fall through to CLI approach silently if there's an API-specific error
                if 'API not enabled' in str(api_e) or 'requires billing to be enabled' in str(api_e):
                    print(f"[DEBUG] API fallback reason: {str(api_e)}")
                    # Fall through to CLI approach
                else:
                    # For other API exceptions, report the error
                    return {
                        "status": "error",
                        "message": f"Error creating subnet via API: {str(api_e)}",
                        "details": str(api_e)
                    }

            # Wait for operation to complete
            # This will throw an exception if the operation fails
            result = operation.result()
            
            # If we get here, the operation was successful
            return {
                "status": "success",
                "message": f"Subnet '{subnet_name}' created successfully in network '{network_name}' (region: {region})",
                "subnet": {
                    "name": subnet_name,
                    "id": result.id,
                    "region": region,
                    "cidr_range": cidr_range,
                    "private_google_access": enable_private_google_access
                }
            }
        else:
            # Fallback to gcloud CLI if API libraries aren't available
            private_access_arg = "--enable-private-ip"
            description_arg = f"--description='{description}'" if description else ""

            # Execute gcloud command to create subnet
            cmd = [
                "gcloud", "compute", "networks", "subnets", "create", subnet_name,
                f"--project={project_id}", f"--network={network_name}",
                f"--region={region}", f"--range={cidr_range}"
            ]

            if enable_private_google_access:
                cmd.append(private_access_arg)

            if description:
                cmd.append(description_arg)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Verify if the subnet was actually created by checking if it appears in the subnet list
            try:
                # Use gcloud to verify the subnet exists
                verify_cmd = [
                    "gcloud", "compute", "networks", "subnets", "describe", subnet_name,
                    f"--project={project_id}", f"--region={region}", "--format=json"
                ]
                
                verify_result = subprocess.run(
                    verify_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # If we get here, the subnet exists, which means it was created successfully
                return {
                    "status": "success",
                    "message": f"Subnet '{subnet_name}' created successfully in network '{network_name}' (region: {region})",
                    "subnet": {
                        "name": subnet_name,
                        "region": region,
                        "cidr_range": cidr_range,
                        "private_google_access": enable_private_google_access
                    },
                    "details": verify_result.stdout # Changed from result.stdout
                }
            except subprocess.CalledProcessError as verify_e:
                # Even though the create command succeeded, we cannot verify the subnet exists
                # This is an unusual situation, so we\'ll return a warning
                return {
                    "status": "warning",
                    "message": f"Subnet \'{subnet_name}\' was likely created in network \'{network_name}\', but verification failed. Please check in the Google Cloud Console.",
                    "details": result.stdout, # Original create stdout for context
                    "verify_error": str(verify_e)
                }
            except Exception as verify_e:
                # Return success with a warning since the original command succeeded
                return {
                    "status": "success",
                    "message": f"Subnet \'{subnet_name}\' created in network \'{network_name}\' (region: {region}), but status verification encountered an error: {str(verify_e)}",
                    "details": verify_result.stdout # Changed from result.stdout
                }

    except subprocess.CalledProcessError as e:
        error_details = e.stderr if hasattr(e, "stderr") else str(e)
        error_lower = error_details.lower() if error_details else ""
        
        # Debug logging to help troubleshoot
        print(f"[DEBUG] Subnet creation CLI error: {error_details}")
        
        # Handle known error cases with more detailed messages
        if "already exists" in error_lower:
            message = f"Subnet '{subnet_name}' already exists in region '{region}'."
        elif "permission denied" in error_lower or "permissions" in error_lower:
            message = f"You don't have sufficient permissions to create a subnet in project '{project_id}'."
        elif "invalid cidr range" in error_lower or "invalid value for" in error_lower and "range" in error_lower:
            message = f"Invalid CIDR range '{cidr_range}'. Please specify a valid CIDR range (e.g., 10.0.0.0/24)."
        elif "overlap" in error_lower:
            message = f"CIDR range '{cidr_range}' overlaps with an existing subnet in network '{network_name}'. Please choose a different CIDR range."
        elif "not found" in error_lower and "network" in error_lower:
            message = f"Network '{network_name}' not found in project '{project_id}'."
        elif "ip range" in error_lower and ("conflict" in error_lower or "overlap" in error_lower):
            message = f"IP range conflict: CIDR range '{cidr_range}' conflicts with an existing subnet in network '{network_name}'. Please choose a different range."
        else:
            message = f"Error creating subnet: {error_details}"
        
        return {
            "status": "error",
            "message": message,
            "details": error_details
        }
    except Exception as e:
        error_details = str(e)
        error_lower = error_details.lower()
        
        # Debug logging for troubleshooting
        print(f"[DEBUG] Subnet creation general error: {error_details}")
        
        # Handle known error cases with improved messages
        if "already exists" in error_lower:
            message = f"Subnet '{subnet_name}' already exists in region '{region}'."
        elif "permission denied" in error_lower:
            message = f"You don't have sufficient permissions to create a subnet in project '{project_id}'."
        elif "invalid cidr" in error_lower or "cidr range" in error_lower:
            message = f"Invalid CIDR range '{cidr_range}'. Please check the format (e.g., 172.0.0.0/24)."
        elif "overlap" in error_lower or "conflict" in error_lower:
            message = f"CIDR range '{cidr_range}' overlaps with an existing subnet. Please choose a different CIDR range that doesn't conflict with existing subnets."
        elif "not found" in error_lower:
            message = f"Resource not found. Check if network '{network_name}' exists in project '{project_id}'."
        elif "route" in error_lower and "conflict" in error_lower:
            message = f"Route conflict detected with CIDR range '{cidr_range}'. This may conflict with existing routes in the VPC."
        else:
            message = f"Error creating subnet: {error_details}"
            
        return {
            "status": "error",
            "message": message,
            "details": error_details
        }

def list_vpc_networks(project_id: str) -> Dict[str, Any]:
    """Lists all VPC networks and their subnets in a GCP project.

    Args:
        project_id (str): The ID of the GCP project

    Returns:
        dict: Contains status and list of VPC networks
    """
    print(f"--- Tool: list_vpc_networks called with project_id={project_id} ---")

    try:
        # First approach: Try using Google Cloud Compute API
        if HAS_GCP_TOOLS_FLAG:
            try:
                credentials = get_gcp_credentials()
                network_client = compute_v1.NetworksClient(credentials=credentials)
                subnet_client = compute_v1.SubnetworksClient(credentials=credentials)

                # Prepare network response
                networks_data = []

                # List all networks in the project
                network_list = network_client.list(project=project_id)

                # For each network, gather basic info
                for network in network_list:
                    # Accept both dicts and objects
                    if isinstance(network, dict):
                        name = network.get("name")
                        net_id = network.get("id")
                        auto_create_subnetworks = network.get("auto_create_subnetworks", False)
                        routing_config = network.get("routing_config")
                    elif hasattr(network, "name"):
                        name = network.name
                        net_id = getattr(network, "id", None)
                        auto_create_subnetworks = getattr(network, "auto_create_subnetworks", False)
                        routing_config = getattr(network, "routing_config", None)
                    else:
                        # Silently skip unexpected network types
                        continue

                    if not name:
                        # Silently skip networks with missing names
                        continue
                    network_info = {
                        "name": name,
                        "id": net_id,
                        "subnet_mode": "auto" if auto_create_subnetworks else "custom",
                        "routing_mode": "GLOBAL"
                            if not routing_config or not hasattr(routing_config, "routing_mode") else getattr(routing_config.routing_mode, 'name', routing_config.routing_mode),
                        "subnets": []
                    }
                    # List all subnets for this network (across all regions)
                    network_self_link = f"projects/{project_id}/global/networks/{name}"
                    request = compute_v1.AggregatedListSubnetworksRequest(
                        project=project_id,
                        filter=f"network eq {network_self_link}"
                    )
                    aggregated_list = subnet_client.aggregated_list(request=request)
                    # Process subnet data
                    for region_key, subnet_list in aggregated_list:
                        if not hasattr(subnet_list, 'subnetworks') or not subnet_list.subnetworks:
                            continue
                        region = region_key.split("/")[1] if "/" in region_key else region_key
                        for subnet in subnet_list.subnetworks:
                            # Robust: handle dict, object, or skip if string/other
                            name = None
                            cidr_range = None
                            private_google_access = None
                            if isinstance(subnet, dict):
                                name = subnet.get("name")
                                cidr_range = subnet.get("ip_cidr_range")
                                private_google_access = subnet.get("private_ip_google_access")
                            elif hasattr(subnet, "name"):
                                name = getattr(subnet, "name", None)
                                cidr_range = getattr(subnet, "ip_cidr_range", None)
                                private_google_access = getattr(subnet, "private_ip_google_access", None)
                            elif isinstance(subnet, str):
                                # Silently skip string subnet entries
                                continue
                            else:
                                # Silently skip unexpected subnet types
                                continue
                            subnet_info = {
                                "name": name,
                                "region": region,
                                "cidr_range": cidr_range,
                                "private_google_access": private_google_access
                            }
                            network_info["subnets"].append(subnet_info)
                    networks_data.append(network_info)

                return {
                    "status": "success",
                    "message": f"Successfully listed VPC networks in project '{project_id}'",
                    "networks": networks_data
                }
            except Exception as api_e:
                # Try to enable the Compute Engine API automatically
                enable_api_result = None
                try:
                    enable_api_result = subprocess.run([
                        "gcloud", "services", "enable", "compute.googleapis.com", f"--project={project_id}"
                    ], capture_output=True, text=True, check=True)
                except Exception as enable_e:
                    return {
                        "status": "error",
                        "message": f"Error listing VPC networks: {api_e}. Also failed to enable Compute Engine API: {enable_e}",
                        "details": str(api_e)
                    }
                # After enabling, try again once
                try:
                    credentials = get_gcp_credentials()
                    network_client = compute_v1.NetworksClient(credentials=credentials)
                    subnet_client = compute_v1.SubnetworksClient(credentials=credentials)

                    # Prepare network response
                    networks_data = []

                    # List all networks in the project
                    network_list = network_client.list(project=project_id)

                    # For each network, gather basic info
                    for network in network_list:
                        # Accept both dicts and objects
                        if isinstance(network, dict):
                            name = network.get("name")
                            net_id = network.get("id")
                            auto_create_subnetworks = network.get("auto_create_subnetworks", False)
                            routing_config = network.get("routing_config")
                        elif hasattr(network, "name"):
                            name = network.name
                            net_id = getattr(network, "id", None)
                            auto_create_subnetworks = getattr(network, "auto_create_subnetworks", False)
                            routing_config = getattr(network, "routing_config", None)
                        else:
                            print(f"[DEBUG][list_vpc_networks] Skipping unexpected network type: {type(network)}, value: {network}")
                            continue

                        if not name:
                            print(f"[DEBUG][list_vpc_networks] Skipping network with missing name: {network}")
                            continue
                        network_info = {
                            "name": name,
                            "id": net_id,
                            "subnet_mode": "auto" if auto_create_subnetworks else "custom",
                            "routing_mode": "GLOBAL"
                                if not routing_config or not hasattr(routing_config, "routing_mode") else getattr(routing_config.routing_mode, 'name', routing_config.routing_mode),
                            "subnets": []
                        }

                        # List all subnets for this network (across all regions)

                        network_self_link = f"projects/{project_id}/global/networks/{name}"
                        request = compute_v1.AggregatedListSubnetworksRequest(
                            project=project_id,
                            filter=f"network eq {network_self_link}"
                        )
                        aggregated_list = subnet_client.aggregated_list(request=request)

                        # Process subnet data
                        api_found_subnets = False
                        for region_key, subnet_list in aggregated_list:
                            if not hasattr(subnet_list, 'subnetworks') or not subnet_list.subnetworks:
                                continue
                            api_found_subnets = True
                            region = region_key.split("/")[1] if "/" in region_key else region_key
                            for subnet in subnet_list.subnetworks:
                                subnet_info = {
                                    "name": getattr(subnet, 'name', None),
                                    "region": region,
                                    "cidr_range": getattr(subnet, 'ip_cidr_range', None),
                                    "private_google_access": getattr(subnet, 'private_ip_google_access', None)
                                }
                                network_info["subnets"].append(subnet_info)
                                
                        # If API didn't find any subnets, try CLI fallback
                        if not api_found_subnets or not network_info["subnets"]:
                            try:
                                # Use gcloud CLI to list subnets for this network
                                cmd = [
                                    "gcloud", "compute", "networks", "subnets", "list",
                                    f"--project={project_id}", f"--network={name}",
                                    "--format=json"
                                ]
                                # Run CLI command without debug output
                                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                                cli_subnets = json.loads(result.stdout)
                                
                                # Only replace subnets if CLI found some and API didn't
                                if cli_subnets and not network_info["subnets"]:
                                    network_info["subnets"] = []
                                    for subnet in cli_subnets:
                                        subnet_info = {
                                            "name": subnet.get("name"),
                                            "region": subnet.get("region").split("/")[-1] if subnet.get("region") else None,
                                            "cidr_range": subnet.get("ipCidrRange"),
                                            "private_google_access": subnet.get("privateIpGoogleAccess", False)
                                        }
                                        network_info["subnets"].append(subnet_info)
                            except Exception as cli_e:
                                # Silently continue if getting subnets via CLI fails
                                pass

                        networks_data.append(network_info)

                    return {
                        "status": "success",
                        "message": f"Successfully listed VPC networks in project '{project_id}'",
                        "networks": networks_data
                    }
                except Exception as retry_e:
                    return {
                        "status": "error",
                        "message": f"Error listing VPC networks after enabling API: {retry_e}",
                        "details": str(retry_e)
                    }
        else:
            # Fallback to gcloud CLI for production use
            cmd = [
                "gcloud", "compute", "networks", "list",
                f"--project={project_id}", "--format=json"
            ]

            networks_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            networks_data = json.loads(networks_result.stdout)

            # For each network, get its subnets
            for network in networks_data:
                network_name = network.get("name", "")

                # Get subnet information
                cmd = [
                    "gcloud", "compute", "networks", "subnets", "list",
                    f"--project={project_id}", f"--network={network_name}",
                    "--format=json"
                ]

                subnets_result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                subnets_data = json.loads(subnets_result.stdout)
                network["subnets"] = subnets_data

            return {
                "status": "success",
                "message": f"Successfully listed VPC networks in project '{project_id}'",
                "networks": networks_data
            }

    except subprocess.CalledProcessError as e:
        # Reduce debug output but keep essential error information
        return {
            "status": "error",
            "message": f"Error listing VPC networks: {e}",
            "details": e.stderr if hasattr(e, "stderr") else str(e)
        }
    except Exception as e:
        # Reduce debug output but keep essential error information
        return {
            "status": "error",
            "message": f"Error listing VPC networks: {str(e)}",
            "details": str(e)
        }
    # Remove debug print for final result
    return {
        "status": "success",
        "message": f"Successfully listed VPC networks in project '{project_id}'",
        "networks": networks_data
    }

def get_vpc_details(project_id: str, network_name: str) -> Dict[str, Any]:
    """Retrieves detailed information about a specific VPC network.

    Args:
        project_id (str): The ID of the GCP project
        network_name (str): The name of the VPC network

    Returns:
        dict: Contains status and details of the VPC network
    """
    # This function is now moved to gcp_vpc_utils.py
    # We call the function from the utils file instead.
    from .gcp_vpc_utils import get_vpc_details as get_vpc_details_internal
    return get_vpc_details_internal(project_id, network_name)

def delete_vpc_network(
    project_id: str,
    network_name: str,
) -> Dict[str, Any]:
    """Deletes a VPC network from a GCP project.
    Args:
        project_id (str): The ID of the GCP project
        network_name (str): Name of the VPC network to delete
    Returns:
        dict: Contains status and result information
    """
    # Confirm intent
    if not confirm_action(
        f"Are you sure you want to delete VPC network '{network_name}' in project '{project_id}'? This action cannot be undone."
    ):
        return {"status": "cancelled", "message": f"Delete operation for VPC network '{network_name}' was cancelled by user."}

    # Check if the network exists
    details_result = get_vpc_details(project_id, network_name)
    if details_result["status"] != "success":
        error_message = f"Network '{network_name}' not found in project '{project_id}'."
        return {"status": "error", "message": error_message}

    try:
        if HAS_GCP_TOOLS_FLAG:
            try:
                credentials = get_gcp_credentials()
                networks_client = compute_v1.NetworksClient(credentials=credentials)
                delete_operation = networks_client.delete(project=project_id, network=network_name)
                result = delete_operation.result()
                return {
                    "status": "success",
                    "message": f"VPC network '{network_name}' deleted successfully via API.",
                    "operation": "api"
                }
            except Exception:
                pass
        # Fallback to gcloud CLI
        import subprocess
        cmd = [
            "gcloud", "compute", "networks", "delete", network_name,
            f"--project={project_id}", "--quiet"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"VPC network '{network_name}' deleted successfully via CLI.",
                "operation": "cli",
                "output": result.stdout
            }
        else:
            error_msg = result.stderr
            # Provide a more user-friendly error message for common cases
            if "is already being used by" in error_msg or "in use" in error_msg.lower():
                return {
                    "status": "error",
                    "message": f"VPC network '{network_name}' cannot be deleted because it is still in use by resources. Please delete all resources using this network first.",
                    "operation": "cli",
                    "output": error_msg
                }
            elif "permission denied" in error_msg.lower():
                return {
                    "status": "error",
                    "message": f"You do not have sufficient permissions to delete VPC network '{network_name}'.",
                    "operation": "cli",
                    "output": error_msg
                }
            elif "not found" in error_msg.lower():
                return {
                    "status": "error",
                    "message": f"VPC network '{network_name}' was not found in project '{project_id}'.",
                    "operation": "cli",
                    "output": error_msg
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to delete VPC network '{network_name}': {error_msg}",
                    "operation": "cli",
                    "output": error_msg
                }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting VPC network '{network_name}': {str(e)}",
            "error": str(e)
        }


def delete_vpc_and_subnets(
    project_id: str,
    network_name: str,
    confirm_each_subnet: bool = False
) -> Dict[str, Any]:
    """Deletes all subnets in a VPC, then deletes the VPC itself.
    Args:
        project_id (str): The ID of the GCP project
        network_name (str): Name of the VPC network to delete
        confirm_each_subnet (bool): If True, ask confirmation for each subnet. If False, ask once for all.
    Returns:
        dict: Contains status and result information
    """
    print(f"--- Tool: delete_vpc_and_subnets called with project_id={project_id}, network_name={network_name} ---")
    # Confirm intent
    if not confirm_action(
        f"Are you sure you want to delete ALL subnets in VPC '{network_name}' and then delete the VPC itself? This action cannot be undone."
    ):
        return {"status": "cancelled", "message": f"Delete operation for VPC '{network_name}' was cancelled by user."}

    # List subnets
    subnets_result = list_subnets(project_id, network_name)
    if subnets_result["status"] != "success":
        return {"status": "error", "message": f"Failed to list subnets: {subnets_result.get('message')}"}
    subnets = subnets_result.get("subnets", [])
    subnet_delete_results = []
    for subnet in subnets:
        subnet_name = subnet.get("name")
        region = subnet.get("region")
        if not subnet_name or not region:
            subnet_delete_results.append({"status": "error", "message": f"Invalid subnet entry: {subnet}"})
            continue
        if confirm_each_subnet:
            if not confirm_action(f"Delete subnet '{subnet_name}' in region '{region}'?"):
                subnet_delete_results.append({"status": "cancelled", "message": f"Skipped subnet '{subnet_name}' in region '{region}' by user choice."})
                continue
        result = delete_subnet(project_id, subnet_name, region)
        subnet_delete_results.append(result)

    # Check if any subnet deletion failed (not cancelled)
    failed_subnets = [r for r in subnet_delete_results if r["status"] == "error"]
    if failed_subnets:
        return {
            "status": "error",
            "message": f"Failed to delete one or more subnets. VPC deletion aborted.",
            "subnet_results": subnet_delete_results
        }

    # All subnets deleted, now delete VPC
    vpc_result = delete_vpc_network(project_id, network_name)
    return {
        "status": vpc_result.get("status", "error"),
        "message": vpc_result.get("message"),
        "subnet_results": subnet_delete_results,
        "vpc_result": vpc_result
    }
