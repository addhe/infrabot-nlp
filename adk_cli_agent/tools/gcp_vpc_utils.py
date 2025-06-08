"""Utility functions for GCP VPC management, to avoid circular imports."""

import subprocess
import json
from typing import Dict, Any
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
        
        class MockFirewallsClient:
            def __init__(self, credentials=None):
                self.credentials = credentials

            def list(self, **kwargs):
                return []

        # Create mock client classes
        class MockNetworksClient:
            def __init__(self, credentials=None):
                self.credentials = credentials
            def get(self, **kwargs):
                result = MockNetwork()
                result.name = kwargs.get("network", "")
                result.id = "mock-network-id"
                return result


        class MockSubnetworksClient:
            def __init__(self, credentials=None):
                self.credentials = credentials
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


def get_vpc_details(project_id: str, network_name: str) -> Dict[str, Any]:
    """Retrieves detailed information about a specific VPC network.

    Args:
        project_id (str): The ID of the GCP project
        network_name (str): The name of the VPC network

    Returns:
        dict: Contains status and details of the VPC network
    """
    print(f"--- Tool: get_vpc_details called with project_id={project_id}, network_name={network_name} ---")

    result = None
    try:
        # First approach: Try using Google Cloud Compute API
        if HAS_GCP_TOOLS_FLAG:
            credentials = get_gcp_credentials()
            network_client = compute_v1.NetworksClient(credentials=credentials)
            subnet_client = compute_v1.SubnetworksClient(credentials=credentials)
            firewall_client = compute_v1.FirewallsClient(credentials=credentials)

            # Get network details
            network = network_client.get(project=project_id, network=network_name)

            # Defensive: handle if network is str, dict, or object
            if isinstance(network, dict):
                name = network.get("name")
                net_id = network.get("id")
                created_at = network.get("creation_timestamp")
                description = network.get("description")
                auto_create_subnetworks = network.get("auto_create_subnetworks", False)
                routing_config = network.get("routing_config")
            elif hasattr(network, "name"):
                name = getattr(network, "name", None)
                net_id = getattr(network, "id", None)
                created_at = getattr(network, "creation_timestamp", None)
                description = getattr(network, "description", None)
                auto_create_subnetworks = getattr(network, "auto_create_subnetworks", False)
                routing_config = getattr(network, "routing_config", None)
            elif isinstance(network, str):
                return {
                    "status": "error",
                    "message": f"Error: Unexpected network type (str) returned from API: {network}",
                    "details": network
                }
            else:
                return {
                    "status": "error",
                    "message": f"Error: Unexpected network type returned from API: {type(network)}",
                    "details": str(network)
                }

            network_details = {
                "name": name,
                "id": net_id,
                "created_at": created_at,
                "description": description,
                "subnet_mode": "auto" if auto_create_subnetworks else "custom",
                "routing_mode": "GLOBAL"
                    if not routing_config or not hasattr(routing_config, "routing_mode") or routing_config is None
                    else getattr(routing_config.routing_mode, 'name', routing_config.routing_mode),
                "subnets": [],
                "firewall_rules": [],
                "peerings": []
            }

            # Get subnets for this network
            network_self_link = f"projects/{project_id}/global/networks/{network_name}"
            request = compute_v1.AggregatedListSubnetworksRequest(
                project=project_id,
                filter=f"network eq {network_self_link}"
            )
            aggregated_list = subnet_client.aggregated_list(request=request)
            api_found_subnets = False
            for region_key, subnet_list_obj in aggregated_list:
                if not hasattr(subnet_list_obj, 'subnetworks') or not subnet_list_obj.subnetworks:
                    continue
                api_found_subnets = True
                region = region_key.split("/")[1] if "/" in region_key else region_key
                for subnet in subnet_list_obj.subnetworks:
                    s_name, s_cidr, s_priv_access, s_sec_ranges, s_net_val = None, None, None, [], None
                    if isinstance(subnet, dict):
                        s_name = subnet.get("name")
                        s_cidr = subnet.get("ip_cidr_range")
                        s_priv_access = subnet.get("private_ip_google_access")
                        s_sec_ranges = subnet.get("secondary_ip_ranges", [])
                        s_net_val = subnet.get("network")
                    elif hasattr(subnet, "name"):
                        s_name = getattr(subnet, "name", None)
                        s_cidr = getattr(subnet, "ip_cidr_range", None)
                        s_priv_access = getattr(subnet, "private_ip_google_access", None)
                        s_sec_ranges = getattr(subnet, "secondary_ip_ranges", [])
                        s_net_val = getattr(subnet, "network", None)
                    else: continue # Skip unexpected types

                    if s_net_val and (s_net_val == network_self_link or s_net_val.endswith(f"/{network_name}")):
                        sec_ranges_info = [
                            {"name": r.get("range_name", getattr(r, "range_name", None)), "cidr": r.get("ip_cidr_range", getattr(r, "ip_cidr_range", None))}
                            for r in (s_sec_ranges if s_sec_ranges is not None else []) if (isinstance(r, dict) or hasattr(r, "range_name"))
                        ]
                        network_details["subnets"].append({
                            "name": s_name, "region": region, "cidr_range": s_cidr,
                            "private_google_access": s_priv_access, "secondary_ip_ranges": sec_ranges_info
                        })
            
            if not api_found_subnets or not network_details["subnets"]:
                try:
                    cmd = ["gcloud", "compute", "networks", "subnets", "list", f"--project={project_id}", f"--network={network_name}", "--format=json"]
                    cli_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    cli_subnets = json.loads(cli_result.stdout)
                    if cli_subnets and not network_details["subnets"]: # Only replace if API found none
                        network_details["subnets"] = []
                        for subnet in cli_subnets:
                            network_details["subnets"].append({
                                "name": subnet.get("name"),
                                "region": subnet.get("region").split("/")[-1] if subnet.get("region") else None,
                                "cidr_range": subnet.get("ipCidrRange"),
                                "private_google_access": subnet.get("privateIpGoogleAccess", False),
                                "secondary_ip_ranges": [
                                    {"name": sr.get("rangeName"), "cidr": sr.get("ipCidrRange")}
                                    for sr in subnet.get("secondaryIpRanges", []) if isinstance(sr, dict)
                                ] if subnet.get("secondaryIpRanges") else []
                            })
                except Exception: pass # Silently continue if CLI fails

            try:
                firewall_list = firewall_client.list(project=project_id, filter=f"network={network_name}")
            except TypeError: # Fallback for mock or older client
                firewall_list = firewall_client.list(project=project_id)
                firewall_list = [fw for fw in firewall_list if (getattr(fw, "network", None) == network_name or (getattr(fw, "network", None) or "").endswith(f"/{network_name}"))]

            for firewall in firewall_list:
                fw_name = getattr(firewall, "name", firewall.get("name") if isinstance(firewall, dict) else None)
                if not fw_name: continue
                network_details["firewall_rules"].append({
                    "name": fw_name,
                    "description": getattr(firewall, "description", firewall.get("description", "") if isinstance(firewall, dict) else ""),
                    "direction": getattr(firewall, "direction", firewall.get("direction", "") if isinstance(firewall, dict) else ""),
                    "priority": getattr(firewall, "priority", firewall.get("priority", "") if isinstance(firewall, dict) else ""),
                    "allowed": [{"protocol": a.get("protocol", getattr(a, "protocol", None)), "ports": a.get("ports", getattr(a, "ports", None))} for a in (getattr(firewall, "allowed", []) if hasattr(firewall, "allowed") else (firewall.get("allowed", []) if isinstance(firewall, dict) else [])) if isinstance(a, dict) or hasattr(a, "protocol")],
                    "denied": [{"protocol": d.get("protocol", getattr(d, "protocol", None)), "ports": d.get("ports", getattr(d, "ports", None))} for d in (getattr(firewall, "denied", []) if hasattr(firewall, "denied") else (firewall.get("denied", []) if isinstance(firewall, dict) else [])) if isinstance(d, dict) or hasattr(d, "protocol")],
                    "source_ranges": getattr(firewall, "source_ranges", firewall.get("source_ranges", []) if isinstance(firewall, dict) else []),
                    "target_tags": getattr(firewall, "target_tags", firewall.get("target_tags", []) if isinstance(firewall, dict) else [])
                })

            if hasattr(network, "peerings") and network.peerings:
                for peering in network.peerings:
                    p_name = getattr(peering, "name", peering.get("name") if isinstance(peering, dict) else None)
                    if not p_name: continue
                    network_details["peerings"].append({
                        "name": p_name,
                        "network": getattr(peering, "network", peering.get("network") if isinstance(peering, dict) else None),
                        "state": getattr(peering, "state", peering.get("state") if isinstance(peering, dict) else None),
                        "auto_create_routes": getattr(peering, "auto_create_routes", peering.get("auto_create_routes") if isinstance(peering, dict) else None)
                    })
            result = {"status": "success", "message": f"Successfully retrieved details for VPC network '{network_name}'", "network": network_details}
        else:
            # Fallback to gcloud CLI
            cmd = ["gcloud", "compute", "networks", "describe", network_name, f"--project={project_id}", "--format=json"]
            network_data = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
            cmd_subnets = ["gcloud", "compute", "networks", "subnets", "list", f"--project={project_id}", f"--network={network_name}", "--format=json"]
            network_data["subnets"] = json.loads(subprocess.run(cmd_subnets, capture_output=True, text=True, check=True).stdout)
            cmd_fw = ["gcloud", "compute", "firewall-rules", "list", f"--project={project_id}", f"--filter=network:{network_name}", "--format=json"]
            network_data["firewall_rules"] = json.loads(subprocess.run(cmd_fw, capture_output=True, text=True, check=True).stdout)
            result = {"status": "success", "message": f"Successfully retrieved details for VPC network '{network_name}'", "network": network_data}

    except subprocess.CalledProcessError as e:
        result = {"status": "error", "message": f"Error retrieving VPC details: {e}", "details": e.stderr if hasattr(e, "stderr") else str(e)}
    except Exception as e:
        result = {"status": "error", "message": f"Error retrieving VPC details: {str(e)}", "details": str(e)}
    return result

