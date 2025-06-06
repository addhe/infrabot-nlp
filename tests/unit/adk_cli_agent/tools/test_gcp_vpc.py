"""Unit tests for ADK CLI Agent's GCP VPC tools functionality."""
import pytest
import json
from unittest.mock import patch, MagicMock
from adk_cli_agent.tools import gcp_vpc

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
    """Mock the get_gcp_credentials function."""
    with patch("adk_cli_agent.tools.gcp_vpc.get_gcp_credentials") as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_compute_networks_client():
    """Mock GCP Compute Networks Client."""
    with patch("adk_cli_agent.tools.gcp_vpc.compute_v1.NetworksClient", create=True) as mock_client:
        # Create a proper client instance that can be used
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock the insert operation
        mock_operation = MagicMock()
        mock_result = MagicMock()
        mock_result.id = "1234567890"
        mock_operation.result.return_value = mock_result
        mock_client_instance.insert.return_value = mock_operation
        
        # Mock the list operation
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
        
        # Mock the get operation
        mock_client_instance.get.return_value = mock_network1
        
        # Mock the delete operation
        mock_delete_operation = MagicMock()
        mock_delete_result = MagicMock()
        mock_delete_operation.result.return_value = mock_delete_result
        mock_client_instance.delete.return_value = mock_delete_operation
        
        yield mock_client

@pytest.fixture
def mock_compute_subnetworks_client():
    """Mock GCP Compute Subnetworks Client."""
    with patch("adk_cli_agent.tools.gcp_vpc.compute_v1.SubnetworksClient", create=True) as mock_client:
        # Create a proper client instance that can be used
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock the insert operation
        mock_operation = MagicMock()
        mock_result = MagicMock()
        mock_result.id = "subnet-1234567890"
        mock_operation.result.return_value = mock_result
        mock_client_instance.insert.return_value = mock_operation
        
        # Mock the aggregated_list operation
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
        
        yield mock_client

@pytest.fixture
def mock_compute_firewalls_client():
    """Mock GCP Compute Firewalls Client."""
    with patch("adk_cli_agent.tools.gcp_vpc.compute_v1.FirewallsClient", create=True) as mock_client:
        # Create a proper client instance that can be used
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock the list operation
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
        
        yield mock_client

@pytest.fixture
def mock_confirmation(monkeypatch):
    """Mock confirmation to always return True."""
    with patch("adk_cli_agent.tools.gcp_vpc.confirm_action", return_value=True):
        yield

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for CLI commands."""
    with patch("subprocess.run") as mock:
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(TEST_VPC_NETWORKS)
        mock_result.returncode = 0
        
        # Configure mock to return different results for different commands
        def side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            if isinstance(cmd, list) and any("describe" in str(c) for c in cmd):
                network_result = MagicMock()
                network_result.stdout = json.dumps(TEST_VPC_NETWORKS[0])
                network_result.returncode = 0
                return network_result
            return mock_result
            
        mock.side_effect = side_effect
        yield mock

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
        mock_confirmation
    ):
        """Test creating a VPC network using the API successfully."""
        result = gcp_vpc.create_vpc_network(
            project_id="test-project", 
            network_name="test-vpc", 
            subnet_mode="auto", 
            routing_mode="global"
        )
        
        # Check if the proper API calls were made
        mock_compute_networks_client.return_value.insert.assert_called_once()
        
        # Check the result
        assert result["status"] == "success"
        assert "network" in result
        assert result["network"]["name"] == "test-vpc"
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    def test_create_vpc_network_cli_success(self, mock_subprocess, mock_confirmation):
        """Test creating a VPC network using the CLI successfully."""
        result = gcp_vpc.create_vpc_network(
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
        
        result = gcp_vpc.create_vpc_network(
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
        result = gcp_vpc.create_vpc_network(
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
    def test_create_subnet_api_success(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, mock_confirmation):
        """Test creating a subnet using the API successfully."""
        result = gcp_vpc.create_subnet(
            project_id="test-project", 
            network_name="test-vpc",
            subnet_name="test-subnet",
            region="us-central1",
            cidr_range="10.0.0.0/24",
            enable_private_google_access=True
        )
        
        # Check if the proper API calls were made
        mock_compute_subnetworks_client.return_value.insert.assert_called_once()
        
        # Check the result
        assert result["status"] == "success"
        assert "subnet" in result
        assert result["subnet"]["name"] == "test-subnet"
        assert result["subnet"]["region"] == "us-central1"
        assert result["subnet"]["cidr_range"] == "10.0.0.0/24"
        assert result["subnet"]["private_google_access"] is True
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    def test_create_subnet_cli_success(self, mock_subprocess, mock_confirmation):
        """Test creating a subnet using the CLI successfully."""
        result = gcp_vpc.create_subnet(
            project_id="test-project", 
            network_name="test-vpc",
            subnet_name="test-subnet",
            region="us-central1",
            cidr_range="10.0.0.0/24",
            enable_private_google_access=True
        )
        
        # Check if the CLI command was called
        mock_subprocess.assert_called_once()
        
        # Check the result
        assert result["status"] == "success"
        assert "details" in result


class TestListVpcNetworks:
    """Tests for list_vpc_networks function."""
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    def test_list_vpc_networks_api_success(self, mock_get_gcp_credentials, mock_compute_networks_client, mock_compute_subnetworks_client):
        """Test listing VPC networks using the API successfully."""
        result = gcp_vpc.list_vpc_networks(project_id="test-project")
        
        # Check if the proper API calls were made
        mock_compute_networks_client.return_value.list.assert_called_once()
        
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
        result = gcp_vpc.list_vpc_networks(project_id="test-project")
        
        # Check if the CLI command was called (multiple times is okay for this implementation)
        assert mock_subprocess.call_count >= 1
        
        # Check the result
        assert result["status"] == "success"
        assert "networks" in result
        assert len(result["networks"]) == 2

def test_list_vpc_networks_handles_str_type(monkeypatch):
    class DummyNetworksClient:
        def list(self, project):
            return ["not-a-dict-or-object"]
    class DummySubnetworksClient:
        def aggregated_list(self, request):
            return []
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.get_gcp_credentials", lambda: None)
    monkeypatch.setattr(
        "adk_cli_agent.tools.gcp_vpc.compute_v1.NetworksClient", lambda credentials=None: DummyNetworksClient()
    )
    monkeypatch.setattr(
        "adk_cli_agent.tools.gcp_vpc.compute_v1.SubnetworksClient", lambda credentials=None: DummySubnetworksClient()
    )
    from adk_cli_agent.tools.gcp_vpc import list_vpc_networks
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
    monkeypatch.setattr(
        "adk_cli_agent.tools.gcp_vpc.compute_v1.NetworksClient", lambda credentials=None: DummyNetworksClient()
    )
    monkeypatch.setattr(
        "adk_cli_agent.tools.gcp_vpc.compute_v1.SubnetworksClient", lambda credentials=None: DummySubnetworksClient()
    )
    from adk_cli_agent.tools.gcp_vpc import list_vpc_networks
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
    monkeypatch.setattr(
        "adk_cli_agent.tools.gcp_vpc.compute_v1.NetworksClient", lambda credentials=None: DummyNetworksClient()
    )
    monkeypatch.setattr(
        "adk_cli_agent.tools.gcp_vpc.compute_v1.SubnetworksClient", lambda credentials=None: DummySubnetworksClient()
    )
    monkeypatch.setattr(
        "adk_cli_agent.tools.gcp_vpc.compute_v1.FirewallsClient", lambda credentials=None: DummyFirewallsClient()
    )
    from adk_cli_agent.tools.gcp_vpc import get_vpc_details
    result = get_vpc_details("dummy-project", "test")
    assert result["status"] == "success"
    assert isinstance(result["network"], dict)

def test_list_vpc_networks_cli_fallback(monkeypatch):
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout='[{"name": "default", "id": "123"}]', returncode=0)
        with patch("json.loads", wraps=json.loads) as mock_json:
            result = gcp_vpc.list_vpc_networks("dummy-project")
            assert result["status"] == "success"
            assert "networks" in result

def test_list_vpc_networks_error(monkeypatch):
    monkeypatch.setattr("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    with patch("subprocess.run", side_effect=Exception("CLI error")):
        result = gcp_vpc.list_vpc_networks("dummy-project")
        assert result["status"] == "error"
