"""Unit tests for GCP VPC management functionality."""
import pytest
from unittest.mock import MagicMock, patch, Mock, ANY
from google.api_core import operation
from google.cloud import compute_v1
from google.cloud.compute_v1.types.compute import Network, NetworkRoutingConfig, Operation

from my_cli_agent.tools.gcp.networking.vpc import VPCManager, get_vpc_manager
from my_cli_agent.tools.gcp.base import GCPVPC, GCPClientManager, GCPToolsError, GCPValidationError
from my_cli_agent.tools.gcp.base.types import GCPResourceStatus

# Mock untuk menghindari masalah dengan protobuf message
class MockOperation(Operation):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = "DONE"
        self.name = "test-operation"
        self.description = "Test operation"
        self.operation_type = "insert"
        self.target_link = "projects/test-project/global/networks/test-vpc"

class TestGCPVPCManager:
    @pytest.fixture
    def mock_client_manager(self):
        """Mock GCP client manager."""
        manager = MagicMock(spec=GCPClientManager)
        manager.project_id = "test-project"
        
        # Mock the get_vpc_client method
        mock_vpc_client = MagicMock()
        manager.get_vpc_client.return_value = mock_vpc_client
        
        return manager, mock_vpc_client

    @pytest.fixture
    def vpc_manager(self, mock_client_manager):
        """Create a VPC manager with a mock client manager."""
        client_manager, _ = mock_client_manager
        manager = VPCManager(client_manager)
        
        # Mock the _wait_for_operation method
        manager._wait_for_operation = MagicMock()
        return manager

    def test_list_vpcs_success(self, vpc_manager, mock_client_manager):
        """Test successful listing of VPCs."""
        client_manager, mock_vpc_client = mock_client_manager
        
        # Create mock network objects with the correct attributes
        mock_network1 = Network()
        mock_network1.name = "test-vpc-1"
        mock_network1.self_link = "projects/test-project/global/networks/test-vpc-1"
        mock_network1.auto_create_subnetworks = True
        mock_network1.creation_timestamp = "2023-01-01T00:00:00Z"
        
        # Add routing config using the correct message type
        routing_config = NetworkRoutingConfig()
        routing_config.routing_mode = NetworkRoutingConfig.RoutingMode.REGIONAL
        mock_network1.routing_config = routing_config
        
        mock_network2 = Network()
        mock_network2.name = "test-vpc-2"
        mock_network2.self_link = "projects/test-project/global/networks/test-vpc-2"
        mock_network2.auto_create_subnetworks = False
        mock_network2.creation_timestamp = "2023-01-02T00:00:00Z"
        
        # Add routing config using the correct message type
        routing_config2 = NetworkRoutingConfig()
        routing_config2.routing_mode = NetworkRoutingConfig.RoutingMode.GLOBAL
        mock_network2.routing_config = routing_config2
        
        # Mock the list method to return our mock networks
        mock_vpc_client.list.return_value = [mock_network1, mock_network2]
        
        # Call the method
        vpcs = vpc_manager.list_vpcs("test-project")
        
        # Verify the results
        assert len(vpcs) == 2
        assert isinstance(vpcs[0], GCPVPC)
        assert vpcs[0].name == "test-vpc-1"
        assert vpcs[1].name == "test-vpc-2"
        assert vpcs[0].auto_create_subnetworks is True
        assert vpcs[1].auto_create_subnetworks is False
        assert vpcs[0].routing_mode == "REGIONAL"
        assert vpcs[1].routing_mode == "GLOBAL"
        assert vpcs[0].status == GCPResourceStatus.READY
        assert vpcs[1].status == GCPResourceStatus.READY
        
        # Verify the client was called correctly
        client_manager.get_vpc_client.assert_called_once()
        mock_vpc_client.list.assert_called_once()

    def test_get_vpc_success(self, vpc_manager, mock_client_manager):
        """Test successful retrieval of a VPC."""
        client_manager, mock_vpc_client = mock_client_manager
        
        # Create a mock network object with the correct attributes
        mock_network = Network()
        mock_network.name = "test-vpc"
        mock_network.self_link = "projects/test-project/global/networks/test-vpc"
        mock_network.auto_create_subnetworks = True
        mock_network.creation_timestamp = "2023-01-01T00:00:00Z"
        
        # Add routing config using the correct message type
        routing_config = NetworkRoutingConfig()
        routing_config.routing_mode = NetworkRoutingConfig.RoutingMode.REGIONAL
        mock_network.routing_config = routing_config
        
        # Configure the mock to return our network
        mock_vpc_client.get.return_value = mock_network
        
        # Call the method
        vpc = vpc_manager.get_vpc("test-vpc", "test-project")
        
        # Verify the results
        assert isinstance(vpc, GCPVPC)
        assert vpc.name == "test-vpc"
        assert vpc.auto_create_subnetworks is True
        assert vpc.project_id == "test-project"
        assert vpc.routing_mode == "REGIONAL"
        assert vpc.status == GCPResourceStatus.READY
        
        # Verify the client was called correctly
        client_manager.get_vpc_client.assert_called_once()
        
        # Verify the get request was made with correct parameters
        mock_vpc_client.get.assert_called_once()
        args, kwargs = mock_vpc_client.get.call_args
        assert 'project' in kwargs or 'request' in kwargs
        
        # Handle both request object and direct parameters
        if 'request' in kwargs:
            request = kwargs['request']
            assert request.project == 'test-project'
            assert request.network == 'test-vpc'
        else:
            assert kwargs.get('project') == 'test-project'
            assert kwargs.get('network') == 'test-vpc'

    def test_create_vpc_success(self, vpc_manager, mock_client_manager):
        """Test successful creation of a VPC."""
        client_manager, mock_vpc_client = mock_client_manager
        
        # Create a mock operation
        mock_operation = MockOperation()
        
        # Mock the insert method to return our mock operation
        mock_vpc_client.insert.return_value = mock_operation
        
        # Mock the get method to return a mock network
        mock_network = Network()
        mock_network.name = "test-vpc"
        mock_network.self_link = "projects/test-project/global/networks/test-vpc"
        mock_network.auto_create_subnetworks = True
        mock_network.creation_timestamp = "2023-01-01T00:00:00Z"
        
        # Mock the get method to return our mock network
        mock_vpc_client.get.return_value = mock_network
        
        # Call the method
        vpc = vpc_manager.create_vpc(
            vpc_name="test-vpc",
            project_id="test-project",
            auto_create_subnetworks=True,
            routing_mode="REGIONAL"
        )
        
        # Verify the results
        assert isinstance(vpc, GCPVPC)
        assert vpc.name == "test-vpc"
        
        # Verify the client was called correctly
        client_manager.get_vpc_client.assert_called_once()
        
        # Verify insert was called with correct parameters
        mock_vpc_client.insert.assert_called_once()
        args, kwargs = mock_vpc_client.insert.call_args
        
        # Handle both request object and direct parameters
        if 'request' in kwargs:
            request = kwargs['request']
            assert request.project == 'test-project'
            network_resource = request.network_resource
        else:
            assert 'project' in kwargs
            assert 'network_resource' in kwargs
            assert kwargs['project'] == 'test-project'
            network_resource = kwargs['network_resource']
        
        # Verify the network resource
        assert network_resource.name == 'test-vpc'
        assert network_resource.auto_create_subnetworks is True
        assert hasattr(network_resource, 'routing_config')
        
        # Verify routing config
        routing_config = network_resource.routing_config
        assert routing_config.routing_mode == NetworkRoutingConfig.RoutingMode.REGIONAL
        
        # Verify we waited for the operation
        vpc_manager._wait_for_operation.assert_called_once_with(mock_operation, "test-project")

    def test_delete_vpc_success(self, vpc_manager, mock_client_manager):
        """Test successful deletion of a VPC."""
        client_manager, mock_vpc_client = mock_client_manager
        
        # Create a mock operation
        mock_operation = MockOperation()
        
        # Mock the delete method to return our mock operation
        mock_vpc_client.delete.return_value = mock_operation
        
        # Call the method
        vpc_manager.delete_vpc(
            vpc_name="test-vpc",
            project_id="test-project"
        )
        
        # Verify the client was called correctly
        client_manager.get_vpc_client.assert_called_once()
        
        # Verify delete was called with correct parameters
        mock_vpc_client.delete.assert_called_once()
        args, kwargs = mock_vpc_client.delete.call_args
        
        # Handle both request object and direct parameters
        if 'request' in kwargs:
            request = kwargs['request']
            assert request.project == 'test-project'
            assert request.network == 'test-vpc'
        else:
            assert 'project' in kwargs
            assert 'network' in kwargs
            assert kwargs['project'] == 'test-project'
            assert kwargs['network'] == 'test-vpc'
        
        # Verify we waited for the operation
        vpc_manager._wait_for_operation.assert_called_once_with(mock_operation, "test-project")

    def test_get_vpc_manager_with_provided_client(self, mock_client_manager):
        """Test getting the VPC manager with provided client manager."""
        client_manager, _ = mock_client_manager
        
        # Test with provided client manager
        with patch('my_cli_agent.tools.gcp.networking.vpc.get_client_manager') as mock_get_client:
            # Call with provided client manager
            manager = get_vpc_manager(client_manager)
            
            # Verify the manager was created with the provided client
            assert isinstance(manager, VPCManager)
            assert manager.client_manager == client_manager
            
            # Should not call get_client_manager when client is provided
            mock_get_client.assert_not_called()
    
    def test_get_vpc_manager_with_default_client(self):
        """Test getting the VPC manager with default client manager."""
        # Create a mock client manager
        mock_client = MagicMock(spec=GCPClientManager)
        mock_client.project_id = "test-project"
        
        # Create a new VPCManager instance with our mock client
        with patch('my_cli_agent.tools.gcp.networking.vpc.get_client_manager') as mock_get_client:
            mock_get_client.return_value = mock_client
            
            # Call without providing a client manager
            manager = get_vpc_manager()
            
            # Verify the manager was created with a client manager
            assert isinstance(manager, VPCManager)
            
            # Verify get_client_manager was called once
            mock_get_client.assert_called_once()
            
            # Reset the mock to test the singleton behavior
            mock_get_client.reset_mock()
            
            # Call again - should return the same instance without calling get_client_manager
            manager2 = get_vpc_manager()
            assert manager is manager2  # Should be the same instance
            mock_get_client.assert_not_called()  # Should not call get_client_manager again

    def test_vpc_validation_errors(self, vpc_manager, mock_client_manager):
        """Test validation errors for VPC operations."""
        client_manager, mock_vpc_client = mock_client_manager
        
        # Test empty project ID
        with pytest.raises(GCPValidationError, match="Project ID cannot be empty"):
            vpc_manager.list_vpcs("")
            
        # Test invalid project ID format (with spaces)
        with pytest.raises(GCPValidationError, match="Project ID must start with lowercase letter"):
            vpc_manager.list_vpcs("invalid project id")
        
        # Test invalid project ID (too short)
        with pytest.raises(GCPValidationError, match="Project ID must be between 6 and 30 characters"):
            vpc_manager.list_vpcs("abc")
            
        # Test invalid project ID (starts with number)
        with pytest.raises(GCPValidationError, match="Project ID must start with lowercase letter"):
            vpc_manager.list_vpcs("1invalid-project")
            
        # Test invalid project ID (ends with hyphen)
        with pytest.raises(GCPValidationError, match="cannot end with hyphen"):
            vpc_manager.list_vpcs("invalid-project-")
            
        # Test invalid VPC name (empty)
        with pytest.raises(ValueError, match="VPC name cannot be empty"):
            vpc_manager.get_vpc("", "test-project")
            
        # Test invalid VPC name (too long)
        long_name = "a" * 64  # Exceeds 63 character limit
        with pytest.raises(ValueError, match="VPC name must be between"):
            vpc_manager.get_vpc(long_name, "test-project")
            
        # Test invalid routing mode
        with pytest.raises(ValueError, match="Invalid routing mode"):
            vpc_manager.create_vpc(
                vpc_name="test-vpc",
                project_id="test-project",
                auto_create_subnetworks=True,
                routing_mode="INVALID_MODE"
            )
        
        # Verify no unnecessary client calls were made
        client_manager.get_vpc_client.assert_not_called()
        mock_vpc_client.list.assert_not_called()
        mock_vpc_client.get.assert_not_called()
        mock_vpc_client.insert.assert_not_called()
        mock_vpc_client.delete.assert_not_called()
