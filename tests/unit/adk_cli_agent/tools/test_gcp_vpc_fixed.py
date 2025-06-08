"""Unit tests for ADK CLI Agent's GCP VPC tools functionality."""
import pytest
import json
from unittest.mock import patch, MagicMock, ANY
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

# Import the functions we\'re testing
from adk_cli_agent.tools.gcp_vpc import (
    create_vpc_network,
    create_subnet,
    list_vpc_networks,
    # get_vpc_details, # Removed: Now imported from gcp_vpc_utils
    HAS_GCP_TOOLS_FLAG,
    compute_v1
)
from adk_cli_agent.tools.gcp_vpc_utils import get_vpc_details # Added: Import from utils

# Test data
TEST_VPC_NETWORKS = [
    {
        "name": "test-vpc-1",
        "id": "1234567890",
        "subnet_mode": "auto",
        "routing_mode": "GLOBAL",
        "subnets": [
            {
                "name": "test-subnet-1",
                "region": "us-central1",
                "cidr_range": "10.0.0.0/24",
                "private_google_access": True
            }
        ]
    },
    {
        "name": "test-vpc-2",
        "id": "0987654321",
        "subnet_mode": "custom",
        "routing_mode": "REGIONAL",
        "subnets": []
    }
]

@pytest.fixture
def mock_get_gcp_credentials():
    """Mock the get_gcp_credentials function in both relevant modules."""
    shared_mock_credentials = MagicMock()
    with patch("adk_cli_agent.tools.gcp_vpc.get_gcp_credentials", return_value=shared_mock_credentials), \
         patch("adk_cli_agent.tools.gcp_vpc_utils.get_gcp_credentials", return_value=shared_mock_credentials):
        yield shared_mock_credentials

@pytest.fixture
def mock_compute_networks_client():
    """Mock GCP Compute Networks Client in both relevant modules."""
    mock_client_instance = MagicMock()
    
    # Configure common behavior for mock_client_instance (insert, list, get methods)
    mock_operation = MagicMock()
    mock_result_op = MagicMock() # Renamed to avoid conflict with subprocess mock's 'result'
    mock_result_op.id = "1234567890"
    mock_operation.result.return_value = mock_result_op
    mock_client_instance.insert.return_value = mock_operation
    
    mock_network1 = MagicMock()
    mock_network1.name = "test-vpc-1"
    mock_network1.id = "1234567890"
    mock_network1.auto_create_subnetworks = True
    mock_network1.routing_config = MagicMock()
    mock_network1.routing_config.routing_mode = MagicMock()
    mock_network1.routing_config.routing_mode.name = "GLOBAL"
    
    mock_network2 = MagicMock()
    mock_network2.name = "test-vpc-2"
    mock_network2.id = "0987654321"
    mock_network2.auto_create_subnetworks = False
    mock_network2.routing_config = MagicMock()
    mock_network2.routing_config.routing_mode = MagicMock()
    mock_network2.routing_config.routing_mode.name = "REGIONAL"
    
    mock_client_instance.list.return_value = [mock_network1, mock_network2]
    mock_client_instance.get.return_value = mock_network1 # Default mock for get

    with patch("adk_cli_agent.tools.gcp_vpc.compute_v1.NetworksClient", create=True, return_value=mock_client_instance), \
         patch("adk_cli_agent.tools.gcp_vpc_utils.compute_v1.NetworksClient", create=True, return_value=mock_client_instance):
        yield mock_client_instance

@pytest.fixture
def mock_compute_subnetworks_client():
    """Mock GCP Compute Subnetworks Client in both relevant modules."""
    mock_client_instance = MagicMock()

    mock_operation = MagicMock()
    mock_result_op = MagicMock()
    mock_result_op.id = "subnet-1234567890"
    mock_operation.result.return_value = mock_result_op
    mock_client_instance.insert.return_value = mock_operation
    
    mock_subnet = MagicMock()
    mock_subnet.name = "test-subnet-1"
    mock_subnet.ip_cidr_range = "10.0.0.0/24"
    mock_subnet.private_ip_google_access = True
    mock_subnet.secondary_ip_ranges = []
    
    mock_subnet_list = MagicMock()
    mock_subnet_list.subnetworks = [mock_subnet]
    
    mock_items = {
        "regions/us-central1": mock_subnet_list,
        "regions/us-east1": MagicMock(subnetworks=[])
    }
    
    def mock_aggregated_list_side_effect(**kwargs):
        return mock_items.items()
    
    mock_client_instance.aggregated_list.side_effect = mock_aggregated_list_side_effect

    with patch("adk_cli_agent.tools.gcp_vpc.compute_v1.SubnetworksClient", create=True, return_value=mock_client_instance), \
         patch("adk_cli_agent.tools.gcp_vpc_utils.compute_v1.SubnetworksClient", create=True, return_value=mock_client_instance):
        yield mock_client_instance

@pytest.fixture
def mock_compute_firewalls_client():
    """Mock GCP Compute Firewalls Client in both relevant modules."""
    mock_client_instance = MagicMock()
    
    mock_firewall_rule = MagicMock()
    mock_firewall_rule.name = "allow-internal"
    mock_firewall_rule.description = "Allow internal traffic"
    mock_firewall_rule.direction = "INGRESS"
    mock_firewall_rule.priority = 1000
    
    mock_allowed = MagicMock()
    mock_allowed.protocol = "tcp"
    mock_allowed.ports = ["22", "80"]
    mock_firewall_rule.allowed = [mock_allowed]
    mock_firewall_rule.denied = []
    mock_firewall_rule.source_ranges = ["10.0.0.0/8"]
    mock_firewall_rule.target_tags = ["web"]
    
    mock_client_instance.list.return_value = [mock_firewall_rule]

    with patch("adk_cli_agent.tools.gcp_vpc.compute_v1.FirewallsClient", create=True, return_value=mock_client_instance), \
         patch("adk_cli_agent.tools.gcp_vpc_utils.compute_v1.FirewallsClient", create=True, return_value=mock_client_instance):
        yield mock_client_instance

@pytest.fixture
def mock_confirmation():  # Removed monkeypatch argument
    """Mock confirmation to always return True."""
    # confirm_action is in gcp_vpc.py and gcp_subnet.py (via confirmation_tools.py)
    # Patching where it\'s directly imported by the modules under test or their direct imports.
    with patch("adk_cli_agent.tools.gcp_vpc.confirm_action", return_value=True) as mock_confirm_vpc, \
         patch("adk_cli_agent.tools.confirmation_tools.confirm_action", return_value=True) as mock_confirm_tools, \
         patch("adk_cli_agent.tools.gcp_subnet.confirm_action", return_value=True, create=True) as mock_confirm_subnet:
        # Yield the one most likely to be used by gcp_vpc.py functions, or a generic mock if shared.
        yield mock_confirm_vpc 

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for CLI commands."""
    with patch("subprocess.run") as mock_run:
        # Mock for 'gcloud compute networks subnets create'
        mock_subnet_create_result = MagicMock()
        mock_subnet_create_result.stdout = "" 
        mock_subnet_create_result.stderr = ""
        mock_subnet_create_result.returncode = 0

        # Mock for 'gcloud compute networks subnets describe'
        mock_subnet_describe_output = {
            "name": "test-subnet", 
            "network": "projects/test-project/global/networks/test-vpc", 
            "ipCidrRange": "10.0.0.0/24", 
            "region": "projects/test-project/regions/us-central1", 
            "privateIpGoogleAccess": True, 
            "secondaryIpRanges": [] 
        }
        mock_subnet_describe_result = MagicMock()
        mock_subnet_describe_result.stdout = json.dumps(mock_subnet_describe_output)
        mock_subnet_describe_result.stderr = ""
        mock_subnet_describe_result.returncode = 0

        # Mock for 'gcloud compute networks list' (for list_vpc_networks test)
        mock_networks_list_result = MagicMock()
        mock_networks_list_result.stdout = json.dumps(TEST_VPC_NETWORKS)
        mock_networks_list_result.stderr = ""
        mock_networks_list_result.returncode = 0
        
        # Mock for 'gcloud compute networks describe' (for get_vpc_details test - network details)
        mock_network_describe_output = TEST_VPC_NETWORKS[0] #  VPC details
        mock_network_describe_cli_result = MagicMock()
        mock_network_describe_cli_result.stdout = json.dumps(mock_network_describe_output)
        mock_network_describe_cli_result.stderr = ""
        mock_network_describe_cli_result.returncode = 0

        # Mock for 'gcloud compute networks subnets list --network' (for get_vpc_details test - subnets list)
        mock_subnets_list_output = [{"name": "subnet-1", "ipCidrRange": "10.1.0.0/24", "region": "us-central1"}]
        mock_subnets_list_cli_result = MagicMock()
        mock_subnets_list_cli_result.stdout = json.dumps(mock_subnets_list_output)
        mock_subnets_list_cli_result.stderr = ""
        mock_subnets_list_cli_result.returncode = 0
        
        # Mock for 'gcloud compute firewall-rules list --filter' (for get_vpc_details test - firewall rules)
        mock_firewalls_list_output = [{"name": "fw-rule-1", "direction": "INGRESS", "priority": 1000}]
        mock_firewalls_list_cli_result = MagicMock()
        mock_firewalls_list_cli_result.stdout = json.dumps(mock_firewalls_list_output)
        mock_firewalls_list_cli_result.stderr = ""
        mock_firewalls_list_cli_result.returncode = 0

        def side_effect_func(cmd_args_list, **kwargs):
            cmd_str = " ".join(cmd_args_list)

            # More specific matches first
            if "compute networks subnets describe" in cmd_str:
                return mock_subnet_describe_result
            elif "compute networks subnets create" in cmd_str:
                return mock_subnet_create_result
            # Order changed: Specific get_vpc_details calls before general list_vpc_networks
            elif "compute networks subnets list" in cmd_str and "--network" in cmd_str: # for get_vpc_details (subnets)
                 return mock_subnets_list_cli_result
            elif "compute firewall-rules list" in cmd_str and "--filter=network:" in cmd_str: # for get_vpc_details (firewalls)
                 return mock_firewalls_list_cli_result
            elif "compute networks describe" in cmd_str: # for get_vpc_details (network details)
                 return mock_network_describe_cli_result
            # General list for list_vpc_networks (less specific)
            elif "compute networks list" in cmd_str: # for list_vpc_networks
                return mock_networks_list_result
            else: 
                default_mock_result = MagicMock()
                default_mock_result.stdout = "{}" 
                default_mock_result.stderr = f"Command not specifically mocked: {cmd_str}"
                default_mock_result.returncode = 0 
                return default_mock_result

        mock_run.side_effect = side_effect_func
        yield mock_run

class TestCreateVpcNetwork:
    """Tests for create_vpc_network function."""
    
    @patch("adk_cli_agent.tools.gcp_vpc.compute_v1.Network", autospec=True)
    @patch("adk_cli_agent.tools.gcp_vpc.compute_v1.NetworkRoutingConfig", autospec=True)
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    def test_create_vpc_network_api_success(
        self,
        mock_network,           # for Network
        mock_routing_config,    # for NetworkRoutingConfig
        mock_get_gcp_credentials,
        mock_compute_networks_client,
        mock_confirmation # mock_confirmation is a fixture
    ):
        """Test creating a VPC network using the API successfully."""
        result = create_vpc_network(
            project_id="test-project", 
            network_name="test-vpc", 
            subnet_mode="auto", 
            routing_mode="global"
        )
        
        # Check if the proper API calls were made
        mock_compute_networks_client.insert.assert_called_once() # Corrected: remove .return_value
        
        # Check the result
        assert result["status"] == "success"
        assert "network" in result
        assert result["network"]["name"] == "test-vpc"
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    def test_create_vpc_network_cli_success(self, mock_subprocess, mock_confirmation):
        """Test creating a VPC network using the CLI successfully."""
        result = create_vpc_network(
            project_id="test-project", 
            network_name="test-vpc", 
            subnet_mode="auto", 
            routing_mode="global"
        )
        
        # Check if the CLI command was called
        mock_subprocess.assert_called_once()
        
        # Check the result
        assert result["status"] == "success"
        assert "details" in result
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    def test_create_vpc_network_api_error(self, mock_get_gcp_credentials, mock_compute_networks_client, mock_confirmation):
        """Test error handling when API call fails."""
        # Mock an error in the API call
        mock_compute_networks_client.return_value.insert.side_effect = Exception("API error")
        
        result = create_vpc_network(
            project_id="test-project", 
            network_name="test-vpc", 
            subnet_mode="auto", 
            routing_mode="global"
        )
        
        # Check the error handling
        assert result["status"] == "error"
        assert "message" in result
        assert "API error" in result["message"]
    
    @patch("adk_cli_agent.tools.gcp_vpc.confirm_action", return_value=False)
    def test_create_vpc_network_cancelled(self, mock_confirm):
        """Test cancellation flow when user does not confirm."""
        result = create_vpc_network(
            project_id="test-project", 
            network_name="test-vpc", 
            subnet_mode="auto", 
            routing_mode="global"
        )
        
        # Check the cancellation result
        assert result["status"] == "cancelled"
        assert "cancelled by user" in result["message"].lower()


class TestCreateSubnet:
    """Tests for create_subnet function."""
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    # mock_compute_networks_client is a fixture providing the client instance
    def test_create_subnet_api_success(self, mock_get_gcp_credentials, mock_compute_networks_client, mock_compute_subnetworks_client, mock_confirmation): # mock_confirmation is a fixture
        """Test creating a subnet using the API successfully."""
        # Ensure the mock_compute_networks_client.get call (to check if network exists) returns a mock object
        mock_compute_networks_client.get.return_value = MagicMock() 

        result = create_subnet(
            project_id="test-project", 
            network_name="test-vpc",
            subnet_name="test-subnet",
            region="us-central1",
            cidr_range="10.0.0.0/24",
            enable_private_google_access=True
        )
        
        mock_compute_subnetworks_client.insert.assert_called_once()
        
        assert result["status"] == "success"
        assert "subnet" in result
        assert result["subnet"]["name"] == "test-subnet"
        assert result["subnet"]["region"] == "us-central1"
        assert result["subnet"]["cidr_range"] == "10.0.0.0/24"
        assert result["subnet"]["private_google_access"] is True

    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    def test_create_subnet_cli_success(self, mock_subprocess, mock_confirmation):
        """Test creating a subnet using the CLI successfully."""
        project_id="test-project"
        network_name="test-vpc"
        subnet_name="test-subnet"
        region="us-central1"
        cidr_range="10.0.0.0/24"
        enable_private_google_access=True

        result = create_subnet(
            project_id=project_id, 
            network_name=network_name,
            subnet_name=subnet_name,
            region=region,
            cidr_range=cidr_range,
            enable_private_google_access=enable_private_google_access
        )
        
        assert mock_subprocess.call_count == 2 
        
        # Call 1: Create subnet
        create_call_args_tuple = mock_subprocess.call_args_list[0]
        create_cmd_list = create_call_args_tuple[0][0] # The command list as a list of strings

        assert "gcloud" in create_cmd_list
        assert "compute" in create_cmd_list
        assert "networks" in create_cmd_list
        assert "subnets" in create_cmd_list
        assert "create" in create_cmd_list
        assert subnet_name in create_cmd_list
        assert f"--network={network_name}" in create_cmd_list
        assert f"--project={project_id}" in create_cmd_list
        assert f"--range={cidr_range}" in create_cmd_list
        assert f"--region={region}" in create_cmd_list
        if enable_private_google_access:
            # Corrected assertion: The actual flag used in gcp_vpc.py is "--enable-private-ip"
            assert "--enable-private-ip" in create_cmd_list
        else:
            assert "--no-enable-private-ip" in create_cmd_list # Or check it's absent

        # Call 2: Describe subnet
        describe_call_args_tuple = mock_subprocess.call_args_list[1]
        describe_cmd_list = describe_call_args_tuple[0][0] # The command list

        assert "gcloud" in describe_cmd_list
        assert "compute" in describe_cmd_list
        assert "networks" in describe_cmd_list
        assert "subnets" in describe_cmd_list
        assert "describe" in describe_cmd_list
        assert subnet_name in describe_cmd_list
        assert f"--project={project_id}" in describe_cmd_list
        assert f"--region={region}" in describe_cmd_list
        assert "--format=json" in describe_cmd_list

        assert result["status"] == "success"
        assert "details" in result
        # Optionally, verify the contents of result["details"] based on mock_subnet_describe_output
        details_dict = json.loads(result["details"]) if isinstance(result["details"], str) else result["details"]
        assert details_dict["name"] == subnet_name
        assert details_dict["ipCidrRange"] == cidr_range
        assert details_dict["privateIpGoogleAccess"] == enable_private_google_access


class TestListVpcNetworks:
    """Tests for list_vpc_networks function."""
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    def test_list_vpc_networks_api_success(self, mock_get_gcp_credentials, mock_compute_networks_client, mock_compute_subnetworks_client):
        """Test listing VPC networks using the API successfully."""
        result = list_vpc_networks(project_id="test-project")
        
        # Check if the proper API calls were made
        mock_compute_networks_client.list.assert_called_once() # Corrected: remove .return_value
        
        # Check the result
        assert result["status"] == "success"
        assert "networks" in result
        assert len(result["networks"]) == 2
        assert result["networks"][0]["name"] == "test-vpc-1"
        assert result["networks"][0]["subnet_mode"] == "auto"
        assert result["networks"][0]["routing_mode"] == "GLOBAL"
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    def test_list_vpc_networks_cli_success(self, mock_subprocess):
        """Test listing VPC networks using the CLI successfully."""
        result = list_vpc_networks(project_id="test-project")
        
        # Check if the CLI command was called (multiple times is okay for this implementation)
        assert mock_subprocess.call_count >= 1
        
        # Check the result
        assert result["status"] == "success"
        assert "networks" in result
        assert len(result["networks"]) == 2


class TestGetVpcDetails:
    """Tests for get_vpc_details function."""
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    def test_get_vpc_details_api_success(self, mock_get_gcp_credentials, mock_compute_networks_client, mock_compute_subnetworks_client, mock_compute_firewalls_client):
        """Test getting VPC details using the API successfully."""
        # Since get_vpc_details is in gcp_vpc_utils.py, HAS_GCP_TOOLS_FLAG for it should be patched there.
        # However, the mock_compute_networks_client fixture already patches the client in both utils and gcp_vpc.
        # The HAS_GCP_TOOLS_FLAG patch here might be misleading if not correctly targeted.
        # For now, let's assume the test setup intends to control behavior via the flag in gcp_vpc.py,
        # but the actual function under test is get_vpc_details from gcp_vpc_utils.py.
        # This might need refinement if get_vpc_details itself checks a flag in its own module.

        with patch("adk_cli_agent.tools.gcp_vpc_utils.HAS_GCP_TOOLS_FLAG", True): # More specific patch
            result = get_vpc_details(
                project_id="test-project", 
                network_name="test-vpc-1"
            )
        
        # Check if the proper API calls were made
        mock_compute_networks_client.get.assert_called_once() # Corrected: remove .return_value
        
        # Check the result
        assert result["status"] == "success"
        assert "network" in result
        assert result["network"]["name"] == "test-vpc-1"
    
    @patch("adk_cli_agent.tools.gcp_vpc_utils.HAS_GCP_TOOLS_FLAG", False) # Corrected patch target
    def test_get_vpc_details_cli_success(self, mock_subprocess):
        """Test getting VPC details using the CLI successfully."""
        project_id = "test-project"
        network_name = "test-vpc-1" # Should match the network name in mock_network_describe_output

        result = get_vpc_details(
            project_id=project_id, 
            network_name=network_name
        )
        
        assert mock_subprocess.call_count == 3

        expected_calls = [
            (['gcloud', 'compute', 'networks', 'describe', network_name, f'--project={project_id}', '--format=json'], 
             {'capture_output': True, 'text': True, 'check': True}),
            (['gcloud', 'compute', 'networks', 'subnets', 'list', f'--project={project_id}', f'--network={network_name}', '--format=json'], # Swapped order of --project and --network
             {'capture_output': True, 'text': True, 'check': True}),
            (['gcloud', 'compute', 'firewall-rules', 'list', f'--project={project_id}', f'--filter=network:{network_name}', '--format=json'], # Swapped order of --project and --filter
             {'capture_output': True, 'text': True, 'check': True})
        ]
        
        # Check each call
        for i, expected_call in enumerate(expected_calls):
            actual_call_args, actual_call_kwargs = mock_subprocess.call_args_list[i]
            assert actual_call_args[0] == expected_call[0] # Compare command list
            assert actual_call_kwargs == expected_call[1] # Compare kwargs
        
        assert result["status"] == "success"
        assert "network" in result
        assert result["network"]["name"] == network_name 
        # Add more assertions based on the combined mocked output if necessary
        assert "subnets" in result["network"]
        assert len(result["network"]["subnets"]) > 0 # Based on mock_subnets_list_output
        assert "firewall_rules" in result["network"]
        assert len(result["network"]["firewall_rules"]) > 0 # Based on mock_firewalls_list_output

def test_list_vpc_networks_handles_str_type(monkeypatch):
    class DummyNetworksClient:
        def list(self, project):
            return ["not-a-dict-or-object"]
    class DummySubnetworksClient:
        def aggregated_list(self, request):
            return []
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.get_gcp_credentials", lambda: None)
    monkeypatch.setattr(compute_v1, "NetworksClient", lambda credentials=None: DummyNetworksClient())
    monkeypatch.setattr(compute_v1, "SubnetworksClient", lambda credentials=None: DummySubnetworksClient())
    result = list_vpc_networks("dummy-project")
    assert result["status"] == "success"
    assert isinstance(result["networks"], list)

def test_list_vpc_networks_enable_api_on_error(monkeypatch):
    class DummyNetworksClient:
        calls = 0  # Use a class variable to persist across instances
        def __init__(self):
            pass
        def list(self, project):
            if DummyNetworksClient.calls == 0:
                DummyNetworksClient.calls += 1
                raise Exception("API not enabled")
            return []
    class DummySubnetworksClient:
        def aggregated_list(self, request):
            return []
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.get_gcp_credentials", lambda: None)
    monkeypatch.setattr(compute_v1, "NetworksClient", lambda credentials=None: DummyNetworksClient())
    monkeypatch.setattr(compute_v1, "SubnetworksClient", lambda credentials=None: DummySubnetworksClient())
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="enabled", returncode=0)
        result = list_vpc_networks("dummy-project")
        assert result["status"] == "success"

def test_get_vpc_details_handles_unexpected_types(monkeypatch):
    class DummyNetwork:
        name = "test"
        id = "id"
        auto_create_subnetworks = True
        routing_config = None
        peerings = ["not-a-dict-or-object"]
        creation_timestamp = "2025-06-03T00:00:00Z"
        description = "desc"
    class DummySubnetList:
        subnetworks = ["not-a-dict-or-object"]
    class DummyNetworksClient:
        def get(self, project, network):
            return DummyNetwork()
    class DummySubnetworksClient:
        def aggregated_list(self, request):
            return [("regions/us-central1", DummySubnetList())]
    class DummyFirewallsClient:
        def list(self, project, filter):
            return ["not-a-dict-or-object"]
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.get_gcp_credentials", lambda: None)
    monkeypatch.setattr(compute_v1, "NetworksClient", lambda credentials=None: DummyNetworksClient())
    monkeypatch.setattr(compute_v1, "SubnetworksClient", lambda credentials=None: DummySubnetworksClient())
    monkeypatch.setattr(compute_v1, "FirewallsClient", lambda credentials=None: DummyFirewallsClient())
    result = get_vpc_details("dummy-project", "test")
    assert result["status"] == "success"
    assert isinstance(result["network"], dict)

def test_list_vpc_networks_cli_fallback(monkeypatch):
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout='[{"name": "default", "id": "123"}]', returncode=0)
        with patch("json.loads", wraps=json.loads) as mock_json:
            result = list_vpc_networks("dummy-project")
            assert result["status"] == "success"
            assert "networks" in result

def test_list_vpc_networks_error(monkeypatch):
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    with patch("subprocess.run", side_effect=Exception("CLI error")):
        result = list_vpc_networks("dummy-project")
        assert result["status"] == "error"
