"""
Unit tests for GCP VPC management functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google.cloud import compute

from my_cli_agent.tools.gcp.networking.vpc import (
    VPCManager,
    get_vpc_manager
)
from my_cli_agent.tools.gcp.base import (
    GCPVPC,
    GCPClientManager,
    GCPToolsError,
    GCPResourceNotFoundError,
    GCPValidationError
)

# Create alias for backward compatibility  
GCPError = GCPToolsError
GCPResourceError = GCPResourceNotFoundError


class TestVPCManager:
    """Test cases for VPCManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client_manager = Mock(spec=GCPClientManager)
        self.mock_client_manager.project_id = "test-project-123"
        self.vpc_manager = VPCManager(self.mock_client_manager)
    
    def test_list_vpcs_success(self):
        """Test successful VPC listing."""
        # Setup mock client
        mock_vpc_client = Mock()
        self.mock_client_manager.get_vpc_client.return_value = mock_vpc_client
        
        # Create mock networks
        mock_network1 = Mock()
        mock_network1.name = "test-vpc-1"
        mock_network1.description = "Test VPC 1"
        mock_network1.auto_create_subnetworks = False
        mock_network1.routing_config = {"routing_mode": "REGIONAL"}
        mock_network1.self_link = "https://compute.googleapis.com/projects/test-project/networks/test-vpc-1"
        mock_network1.creation_timestamp = "2024-01-01T00:00:00.000-08:00"
        
        mock_network2 = Mock()
        mock_network2.name = "test-vpc-2"
        mock_network2.description = "Test VPC 2"
        mock_network2.auto_create_subnetworks = True
        mock_network2.routing_config = {"routing_mode": "GLOBAL"}
        mock_network2.self_link = "https://compute.googleapis.com/projects/test-project/networks/test-vpc-2"
        mock_network2.creation_timestamp = "2024-01-02T00:00:00.000-08:00"
        
        mock_vpc_client.list.return_value = [mock_network1, mock_network2]
        
        # Test VPC listing
        result = self.vpc_manager.list_vpcs()
        
        assert len(result) == 2
        assert all(isinstance(vpc, GCPVPC) for vpc in result)
        assert result[0].name == "test-vpc-1"
        assert result[0].auto_create_subnetworks is False
        assert result[1].name == "test-vpc-2"
        assert result[1].auto_create_subnetworks is True
        
        mock_vpc_client.list.assert_called_once()
    
    def test_list_vpcs_no_project_id(self):
        """Test VPC listing without project ID."""
        self.mock_client_manager.project_id = None
        
        with pytest.raises(GCPValidationError, match="Project ID is required"):
            self.vpc_manager.list_vpcs()
    
    def test_list_vpcs_with_project_id(self):
        """Test VPC listing with explicit project ID."""
        mock_vpc_client = Mock()
        self.mock_client_manager.get_vpc_client.return_value = mock_vpc_client
        mock_vpc_client.list.return_value = []
        
        result = self.vpc_manager.list_vpcs("another-project-456")
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_list_vpcs_error(self):
        """Test VPC listing error handling."""
        self.mock_client_manager.get_vpc_client.side_effect = Exception("Client error")
        
        with pytest.raises(GCPError, match="Failed to list VPCs"):
            self.vpc_manager.list_vpcs()
    
    def test_get_vpc_success(self):
        """Test successful VPC retrieval."""
        # Setup mock client
        mock_vpc_client = Mock()
        self.mock_client_manager.get_vpc_client.return_value = mock_vpc_client
        
        # Create mock network
        mock_network = Mock()
        mock_network.name = "test-vpc"
        mock_network.description = "Test VPC"
        mock_network.auto_create_subnetworks = False
        mock_network.routing_config = {"routing_mode": "REGIONAL"}
        mock_network.self_link = "https://compute.googleapis.com/projects/test-project/networks/test-vpc"
        mock_network.creation_timestamp = "2024-01-01T00:00:00.000-08:00"
        
        mock_vpc_client.get.return_value = mock_network
        
        # Test VPC retrieval
        result = self.vpc_manager.get_vpc("test-vpc")
        
        assert isinstance(result, GCPVPC)
        assert result.name == "test-vpc"
        assert result.description == "Test VPC"
        assert result.auto_create_subnetworks is False
        assert result.routing_mode == "REGIONAL"
        
        mock_vpc_client.get.assert_called_once()
    
    def test_get_vpc_invalid_name(self):
        """Test VPC retrieval with invalid name."""
        with pytest.raises(GCPValidationError):
            self.vpc_manager.get_vpc("invalid_vpc_name!")
    
    def test_get_vpc_not_found(self):
        """Test VPC retrieval when VPC not found."""
        self.mock_client_manager.get_vpc_client.side_effect = Exception("Not found")
        
        with pytest.raises(GCPResourceError, match="Failed to get VPC"):
            self.vpc_manager.get_vpc("test-vpc")
    
    def test_create_vpc_success(self):
        """Test successful VPC creation."""
        # Setup mock client
        mock_vpc_client = Mock()
        self.mock_client_manager.get_vpc_client.return_value = mock_vpc_client
        
        # Mock operation
        mock_operation = Mock()
        mock_operation.name = "operation-123"
        mock_vpc_client.insert.return_value = mock_operation
        
        # Mock the get_vpc method for return value
        mock_vpc = GCPVPC(
            project_id="test-project-123",
            name="test-vpc",
            description="Test VPC",
            auto_create_subnetworks=False,
            routing_mode="REGIONAL",
            self_link="https://compute.googleapis.com/projects/test-project/networks/test-vpc",
            creation_timestamp="2024-01-01T00:00:00.000-08:00"
        )
        
        with patch.object(self.vpc_manager, 'get_vpc', return_value=mock_vpc):
            with patch.object(self.vpc_manager, '_wait_for_operation'):
                # Test VPC creation
                result = self.vpc_manager.create_vpc(
                    "test-vpc",
                    description="Test VPC",
                    auto_create_subnetworks=False,
                    routing_mode="REGIONAL"
                )
        
        assert isinstance(result, GCPVPC)
        assert result.name == "test-vpc"
        assert result.description == "Test VPC"
        
        mock_vpc_client.insert.assert_called_once()
    
    def test_create_vpc_invalid_name(self):
        """Test VPC creation with invalid name."""
        with pytest.raises(GCPValidationError):
            self.vpc_manager.create_vpc("invalid_vpc_name!")
    
    def test_create_vpc_error(self):
        """Test VPC creation error handling."""
        self.mock_client_manager.get_vpc_client.side_effect = Exception("Creation failed")
        
        with pytest.raises(GCPResourceError, match="Failed to create VPC"):
            self.vpc_manager.create_vpc("test-vpc")
    
    def test_update_vpc_success(self):
        """Test successful VPC update."""
        # Setup mock client
        mock_vpc_client = Mock()
        self.mock_client_manager.get_vpc_client.return_value = mock_vpc_client
        
        # Mock current VPC
        current_vpc = GCPVPC(
            project_id="test-project-123",
            name="test-vpc",
            description="Old description",
            auto_create_subnetworks=False,
            routing_mode="REGIONAL",
            self_link="https://compute.googleapis.com/projects/test-project/networks/test-vpc",
            creation_timestamp="2024-01-01T00:00:00.000-08:00"
        )
        
        # Mock updated VPC
        updated_vpc = GCPVPC(
            project_id="test-project-123",
            name="test-vpc",
            description="New description",
            auto_create_subnetworks=False,
            routing_mode="GLOBAL",
            self_link="https://compute.googleapis.com/projects/test-project/networks/test-vpc",
            creation_timestamp="2024-01-01T00:00:00.000-08:00"
        )
        
        # Mock operation
        mock_operation = Mock()
        mock_operation.name = "operation-123"
        mock_vpc_client.patch.return_value = mock_operation
        
        with patch.object(self.vpc_manager, 'get_vpc', side_effect=[current_vpc, updated_vpc]):
            with patch.object(self.vpc_manager, '_wait_for_operation'):
                # Test VPC update
                result = self.vpc_manager.update_vpc(
                    "test-vpc",
                    description="New description",
                    routing_mode="GLOBAL"
                )
        
        assert isinstance(result, GCPVPC)
        assert result.description == "New description"
        assert result.routing_mode == "GLOBAL"
        
        mock_vpc_client.patch.assert_called_once()
    
    def test_delete_vpc_success(self):
        """Test successful VPC deletion."""
        # Setup mock client
        mock_vpc_client = Mock()
        self.mock_client_manager.get_vpc_client.return_value = mock_vpc_client
        
        # Mock operation
        mock_operation = Mock()
        mock_operation.name = "operation-123"
        mock_vpc_client.delete.return_value = mock_operation
        
        with patch.object(self.vpc_manager, '_wait_for_operation'):
            # Test VPC deletion
            result = self.vpc_manager.delete_vpc("test-vpc")
        
        assert result is True
        mock_vpc_client.delete.assert_called_once()
    
    def test_delete_vpc_invalid_name(self):
        """Test VPC deletion with invalid name."""
        with pytest.raises(GCPValidationError):
            self.vpc_manager.delete_vpc("invalid_vpc_name!")
    
    def test_delete_vpc_error(self):
        """Test VPC deletion error handling."""
        self.mock_client_manager.get_vpc_client.side_effect = Exception("Deletion failed")
        
        with pytest.raises(GCPResourceError, match="Failed to delete VPC"):
            self.vpc_manager.delete_vpc("test-vpc")
    
    @patch('my_cli_agent.tools.gcp.networking.vpc.compute.GlobalOperationsClient')
    def test_wait_for_operation_success(self, mock_operations_client_class):
        """Test successful operation waiting."""
        mock_operations_client = Mock()
        mock_operations_client_class.return_value = mock_operations_client
        
        mock_operation = Mock()
        mock_operation.name = "operation-123"
        
        mock_result = Mock()
        mock_result.error = None
        mock_operations_client.wait.return_value = mock_result
        
        # Should not raise exception
        self.vpc_manager._wait_for_operation(mock_operation, "test-project")
        
        mock_operations_client.wait.assert_called_once_with(
            project="test-project",
            operation="operation-123",
            timeout=300
        )
    
    @patch('my_cli_agent.tools.gcp.networking.vpc.compute.GlobalOperationsClient')
    def test_wait_for_operation_error(self, mock_operations_client_class):
        """Test operation waiting with error."""
        mock_operations_client = Mock()
        mock_operations_client_class.return_value = mock_operations_client
        
        mock_operation = Mock()
        mock_operation.name = "operation-123"
        
        mock_error = Mock()
        mock_error.errors = [Mock(code="ERROR_CODE", message="Error message")]
        
        mock_result = Mock()
        mock_result.error = mock_error
        mock_operations_client.wait.return_value = mock_result
        
        with pytest.raises(GCPResourceError, match="Operation failed"):
            self.vpc_manager._wait_for_operation(mock_operation, "test-project")
    
    @patch('my_cli_agent.tools.gcp.networking.vpc.compute.GlobalOperationsClient')
    def test_wait_for_operation_exception(self, mock_operations_client_class):
        """Test operation waiting with exception."""
        mock_operations_client_class.side_effect = Exception("Client error")
        
        mock_operation = Mock()
        mock_operation.name = "operation-123"
        
        with pytest.raises(GCPResourceError, match="Failed to wait for operation"):
            self.vpc_manager._wait_for_operation(mock_operation, "test-project")


class TestGlobalVPCManager:
    """Test cases for global VPC manager functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Reset global state
        import my_cli_agent.tools.gcp.networking.vpc as vpc_module
        vpc_module._vpc_manager = None
    
    def test_get_vpc_manager_new(self):
        """Test getting new VPC manager."""
        mock_client_manager = Mock()
        
        with patch('my_cli_agent.tools.gcp.networking.vpc.VPCManager') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            result = get_vpc_manager(mock_client_manager)
            
            assert result == mock_instance
            mock_class.assert_called_once_with(mock_client_manager)
    
    def test_get_vpc_manager_cached(self):
        """Test getting cached VPC manager."""
        with patch('my_cli_agent.tools.gcp.networking.vpc.VPCManager') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            # First call creates new instance
            result1 = get_vpc_manager()
            # Second call returns cached instance
            result2 = get_vpc_manager()
            
            assert result1 == mock_instance
            assert result2 == mock_instance
            assert mock_class.call_count == 1
