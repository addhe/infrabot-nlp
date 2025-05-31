"""
Comprehensive test suite for GCP Subnet Management.

This module tests the SubnetManager class functionality including:
- Subnet CRUD operations
- Regional subnet management  
- Secondary IP ranges support
- Private Google access configuration
- CIDR validation and resource naming
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google.cloud import compute
from google.api_core import exceptions as gcp_exceptions

from ..base.client import GCPClientManager
from ..base.exceptions import (
    GCPToolsError as GCPResourceError, 
    GCPValidationError,
    GCPOperationError
)
from ..base.types import GCPSubnet, GCPResourceStatus
from .subnet import SubnetManager


class TestSubnetManager:
    """Test suite for SubnetManager class."""
    
    @pytest.fixture
    def mock_client_manager(self):
        """Create a mock GCP client manager."""
        manager = Mock(spec=GCPClientManager)
        manager.project_id = "test-project"
        manager.get_compute_client.return_value = Mock(spec=compute.SubnetworksClient)
        return manager
        
    @pytest.fixture
    def subnet_manager(self, mock_client_manager):
        """Create a SubnetManager instance with mocked client."""
        return SubnetManager(mock_client_manager)
        
    @pytest.fixture
    def sample_subnet_data(self):
        """Sample subnet data for testing."""
        return {
            'name': 'test-subnet',
            'vpc_name': 'test-vpc',
            'region': 'us-central1',
            'ip_cidr_range': '10.0.1.0/24',
            'description': 'Test subnet for unit tests',
            'private_ip_google_access': True,
            'secondary_ip_ranges': [
                {
                    'rangeName': 'pods',
                    'ipCidrRange': '10.1.0.0/16'
                },
                {
                    'rangeName': 'services', 
                    'ipCidrRange': '10.2.0.0/16'
                }
            ]
        }

    def test_list_subnets_success(self, subnet_manager, mock_client_manager):
        """Test successful subnet listing."""
        # Mock subnet data
        mock_subnet1 = Mock()
        mock_subnet1.name = "subnet-1"
        mock_subnet1.network = "projects/test-project/global/networks/vpc-1"
        mock_subnet1.region = "projects/test-project/regions/us-central1"
        mock_subnet1.ip_cidr_range = "10.0.1.0/24"
        mock_subnet1.description = "Test subnet 1"
        mock_subnet1.private_ip_google_access = True
        mock_subnet1.secondary_ip_ranges = []
        
        mock_subnet2 = Mock()
        mock_subnet2.name = "subnet-2"
        mock_subnet2.network = "projects/test-project/global/networks/vpc-2"
        mock_subnet2.region = "projects/test-project/regions/us-west1"
        mock_subnet2.ip_cidr_range = "10.0.2.0/24"
        mock_subnet2.description = "Test subnet 2"
        mock_subnet2.private_ip_google_access = False
        mock_subnet2.secondary_ip_ranges = []
        
        # Mock client response
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.list.return_value = [mock_subnet1, mock_subnet2]
        
        # Test list subnets
        subnets = subnet_manager.list_subnets(region="us-central1")
        
        assert len(subnets) == 2
        assert all(isinstance(subnet, GCPSubnet) for subnet in subnets)
        assert subnets[0].name == "subnet-1"
        assert subnets[0].vpc_name == "vpc-1"
        assert subnets[0].region == "us-central1"
        assert subnets[0].ip_cidr_range == "10.0.1.0/24"
        assert subnets[0].private_ip_google_access is True
        
        # Verify client was called correctly
        mock_client.list.assert_called_once_with(
            project="test-project",
            region="us-central1"
        )

    def test_list_subnets_empty_result(self, subnet_manager, mock_client_manager):
        """Test subnet listing with no results."""
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.list.return_value = []
        
        subnets = subnet_manager.list_subnets(region="us-central1")
        
        assert subnets == []
        mock_client.list.assert_called_once()

    def test_list_subnets_client_error(self, subnet_manager, mock_client_manager):
        """Test subnet listing with client error."""
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.list.side_effect = gcp_exceptions.GoogleAPICallError("API Error")
        
        with pytest.raises(GCPResourceError, match="Failed to list subnets"):
            subnet_manager.list_subnets(region="us-central1")

    def test_get_subnet_success(self, subnet_manager, mock_client_manager):
        """Test successful subnet retrieval."""
        # Mock subnet data
        mock_subnet = Mock()
        mock_subnet.name = "test-subnet"
        mock_subnet.network = "projects/test-project/global/networks/test-vpc"
        mock_subnet.region = "projects/test-project/regions/us-central1"
        mock_subnet.ip_cidr_range = "10.0.1.0/24"
        mock_subnet.description = "Test subnet"
        mock_subnet.private_ip_google_access = True
        mock_subnet.secondary_ip_ranges = [
            Mock(range_name='pods', ip_cidr_range='10.1.0.0/16'),
            Mock(range_name='services', ip_cidr_range='10.2.0.0/16')
        ]
        
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.get.return_value = mock_subnet
        
        subnet = subnet_manager.get_subnet("test-subnet", region="us-central1")
        
        assert isinstance(subnet, GCPSubnet)
        assert subnet.name == "test-subnet"
        assert subnet.vpc_name == "test-vpc"
        assert subnet.region == "us-central1"
        assert subnet.ip_cidr_range == "10.0.1.0/24"
        assert subnet.private_ip_google_access is True
        assert len(subnet.secondary_ip_ranges) == 2
        assert subnet.secondary_ip_ranges[0]['rangeName'] == 'pods'
        
        mock_client.get.assert_called_once_with(
            project="test-project",
            region="us-central1",
            subnetwork="test-subnet"
        )

    def test_get_subnet_not_found(self, subnet_manager, mock_client_manager):
        """Test subnet retrieval when subnet doesn't exist."""
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.get.side_effect = gcp_exceptions.NotFound("Subnet not found")
        
        subnet = subnet_manager.get_subnet("nonexistent-subnet", region="us-central1")
        
        assert subnet is None

    def test_create_subnet_success(self, subnet_manager, mock_client_manager, sample_subnet_data):
        """Test successful subnet creation."""
        # Mock operation response
        mock_operation = Mock()
        mock_operation.name = "operation-12345"
        
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.insert.return_value = mock_operation
        
        # Mock operation wait
        with patch.object(subnet_manager, '_wait_for_operation') as mock_wait:
            mock_wait.return_value = True
            
            result = subnet_manager.create_subnet(**sample_subnet_data)
            
        assert result is True
        
        # Verify client was called with correct parameters
        mock_client.insert.assert_called_once()
        call_args = mock_client.insert.call_args
        assert call_args[1]['project'] == "test-project"
        assert call_args[1]['region'] == "us-central1"
        
        # Verify subnet resource structure
        subnet_resource = call_args[1]['subnetwork_resource']
        assert subnet_resource.name == "test-subnet"
        assert subnet_resource.network.endswith("/networks/test-vpc")
        assert subnet_resource.ip_cidr_range == "10.0.1.0/24"
        assert subnet_resource.private_ip_google_access is True
        assert len(subnet_resource.secondary_ip_ranges) == 2

    def test_create_subnet_invalid_cidr(self, subnet_manager, sample_subnet_data):
        """Test subnet creation with invalid CIDR range."""
        sample_subnet_data['ip_cidr_range'] = "invalid-cidr"
        
        with pytest.raises(GCPValidationError, match="Invalid CIDR range"):
            subnet_manager.create_subnet(**sample_subnet_data)

    def test_create_subnet_operation_timeout(self, subnet_manager, mock_client_manager, sample_subnet_data):
        """Test subnet creation with operation timeout."""
        mock_operation = Mock()
        mock_operation.name = "operation-12345"
        
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.insert.return_value = mock_operation
        
        # Mock operation wait timeout
        with patch.object(subnet_manager, '_wait_for_operation') as mock_wait:
            mock_wait.return_value = False
            
            with pytest.raises(GCPOperationError, match="Subnet creation operation timed out"):
                subnet_manager.create_subnet(**sample_subnet_data)

    def test_create_subnet_api_error(self, subnet_manager, mock_client_manager, sample_subnet_data):
        """Test subnet creation with API error."""
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.insert.side_effect = gcp_exceptions.GoogleAPICallError("API Error")
        
        with pytest.raises(GCPResourceError, match="Failed to create subnet"):
            subnet_manager.create_subnet(**sample_subnet_data)

    def test_update_subnet_success(self, subnet_manager, mock_client_manager):
        """Test successful subnet update."""
        update_data = {
            'description': 'Updated subnet description',
            'private_ip_google_access': False
        }
        
        mock_operation = Mock()
        mock_operation.name = "operation-12345"
        
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.patch.return_value = mock_operation
        
        with patch.object(subnet_manager, '_wait_for_operation') as mock_wait:
            mock_wait.return_value = True
            
            result = subnet_manager.update_subnet(
                "test-subnet", 
                region="us-central1",
                **update_data
            )
            
        assert result is True
        
        mock_client.patch.assert_called_once()
        call_args = mock_client.patch.call_args
        assert call_args[1]['project'] == "test-project"
        assert call_args[1]['region'] == "us-central1"
        assert call_args[1]['subnetwork'] == "test-subnet"

    def test_delete_subnet_success(self, subnet_manager, mock_client_manager):
        """Test successful subnet deletion."""
        mock_operation = Mock()
        mock_operation.name = "operation-12345"
        
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.delete.return_value = mock_operation
        
        with patch.object(subnet_manager, '_wait_for_operation') as mock_wait:
            mock_wait.return_value = True
            
            result = subnet_manager.delete_subnet("test-subnet", region="us-central1")
            
        assert result is True
        
        mock_client.delete.assert_called_once_with(
            project="test-project",
            region="us-central1",
            subnetwork="test-subnet"
        )

    def test_delete_subnet_not_found(self, subnet_manager, mock_client_manager):
        """Test subnet deletion when subnet doesn't exist."""
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.delete.side_effect = gcp_exceptions.NotFound("Subnet not found")
        
        result = subnet_manager.delete_subnet("nonexistent-subnet", region="us-central1")
        
        assert result is True  # Consider deletion of non-existent resource as success

    def test_secondary_ip_ranges_processing(self, subnet_manager, mock_client_manager, sample_subnet_data):
        """Test processing of secondary IP ranges in subnet creation."""
        mock_operation = Mock()
        mock_client = mock_client_manager.get_compute_client.return_value
        mock_client.insert.return_value = mock_operation
        
        with patch.object(subnet_manager, '_wait_for_operation') as mock_wait:
            mock_wait.return_value = True
            
            subnet_manager.create_subnet(**sample_subnet_data)
            
        # Verify secondary IP ranges were processed correctly
        call_args = mock_client.insert.call_args
        subnet_resource = call_args[1]['subnetwork_resource']
        secondary_ranges = subnet_resource.secondary_ip_ranges
        
        assert len(secondary_ranges) == 2
        assert secondary_ranges[0].range_name == 'pods'
        assert secondary_ranges[0].ip_cidr_range == '10.1.0.0/16'
        assert secondary_ranges[1].range_name == 'services'
        assert secondary_ranges[1].ip_cidr_range == '10.2.0.0/16'

    def test_subnet_name_validation(self, subnet_manager, sample_subnet_data):
        """Test subnet name validation."""
        # Test invalid characters
        sample_subnet_data['name'] = 'test_subnet_with_underscores'
        
        with pytest.raises(GCPValidationError, match="Invalid subnet name"):
            subnet_manager.create_subnet(**sample_subnet_data)
            
        # Test name too long
        sample_subnet_data['name'] = 'a' * 64  # Exceeds 63 character limit
        
        with pytest.raises(GCPValidationError, match="Invalid subnet name"):
            subnet_manager.create_subnet(**sample_subnet_data)

    def test_region_extraction_from_url(self, subnet_manager):
        """Test region extraction from GCP resource URL."""
        # Test various URL formats
        region_url = "projects/test-project/regions/us-central1"
        assert subnet_manager._extract_region_from_url(region_url) == "us-central1"
        
        # Test full URL
        full_url = "https://www.googleapis.com/compute/v1/projects/test-project/regions/us-west1"
        assert subnet_manager._extract_region_from_url(full_url) == "us-west1"
        
        # Test already extracted region
        simple_region = "europe-west1"
        assert subnet_manager._extract_region_from_url(simple_region) == "europe-west1"

    def test_vpc_name_extraction_from_url(self, subnet_manager):
        """Test VPC name extraction from network URL."""
        # Test standard network URL
        network_url = "projects/test-project/global/networks/my-vpc"
        assert subnet_manager._extract_vpc_name_from_url(network_url) == "my-vpc"
        
        # Test full URL
        full_url = "https://www.googleapis.com/compute/v1/projects/test-project/global/networks/production-vpc"
        assert subnet_manager._extract_vpc_name_from_url(full_url) == "production-vpc"

    def test_wait_for_operation_success(self, subnet_manager, mock_client_manager):
        """Test successful operation waiting."""
        mock_operation = Mock()
        mock_operation.name = "operation-12345"
        
        # Mock regional operations client
        mock_ops_client = Mock()
        mock_client_manager.get_compute_client.return_value = mock_ops_client
        
        # Mock operation status progression
        op_in_progress = Mock()
        op_in_progress.status = "RUNNING"
        
        op_done = Mock()
        op_done.status = "DONE"
        op_done.error = None
        
        mock_ops_client.get.side_effect = [op_in_progress, op_done]
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = subnet_manager._wait_for_operation(mock_operation, region="us-central1")
            
        assert result is True

    def test_wait_for_operation_with_error(self, subnet_manager, mock_client_manager):
        """Test operation waiting with operation error."""
        mock_operation = Mock()
        mock_operation.name = "operation-12345"
        
        mock_ops_client = Mock()
        mock_client_manager.get_compute_client.return_value = mock_ops_client
        
        # Mock operation with error
        op_with_error = Mock()
        op_with_error.status = "DONE"
        op_with_error.error = Mock()
        op_with_error.error.errors = [{'message': 'Operation failed'}]
        
        mock_ops_client.get.return_value = op_with_error
        
        with pytest.raises(GCPOperationError, match="Operation failed"):
            subnet_manager._wait_for_operation(mock_operation, region="us-central1")

    def test_comprehensive_subnet_workflow(self, subnet_manager, mock_client_manager, sample_subnet_data):
        """Test complete subnet lifecycle: create, get, update, delete."""
        mock_client = mock_client_manager.get_compute_client.return_value
        
        # Test creation
        mock_operation = Mock()
        mock_operation.name = "create-operation"
        mock_client.insert.return_value = mock_operation
        
        with patch.object(subnet_manager, '_wait_for_operation', return_value=True):
            create_result = subnet_manager.create_subnet(**sample_subnet_data)
        assert create_result is True
        
        # Test retrieval
        mock_subnet = Mock()
        mock_subnet.name = sample_subnet_data['name']
        mock_subnet.network = f"projects/test-project/global/networks/{sample_subnet_data['vpc_name']}"
        mock_subnet.region = f"projects/test-project/regions/{sample_subnet_data['region']}"
        mock_subnet.ip_cidr_range = sample_subnet_data['ip_cidr_range']
        mock_subnet.description = sample_subnet_data['description']
        mock_subnet.private_ip_google_access = sample_subnet_data['private_ip_google_access']
        mock_subnet.secondary_ip_ranges = []
        
        mock_client.get.return_value = mock_subnet
        retrieved_subnet = subnet_manager.get_subnet(sample_subnet_data['name'], region=sample_subnet_data['region'])
        assert retrieved_subnet is not None
        assert retrieved_subnet.name == sample_subnet_data['name']
        
        # Test update
        mock_update_operation = Mock()
        mock_update_operation.name = "update-operation"
        mock_client.patch.return_value = mock_update_operation
        
        with patch.object(subnet_manager, '_wait_for_operation', return_value=True):
            update_result = subnet_manager.update_subnet(
                sample_subnet_data['name'], 
                region=sample_subnet_data['region'],
                description="Updated description"
            )
        assert update_result is True
        
        # Test deletion
        mock_delete_operation = Mock()
        mock_delete_operation.name = "delete-operation"
        mock_client.delete.return_value = mock_delete_operation
        
        with patch.object(subnet_manager, '_wait_for_operation', return_value=True):
            delete_result = subnet_manager.delete_subnet(sample_subnet_data['name'], region=sample_subnet_data['region'])
        assert delete_result is True
