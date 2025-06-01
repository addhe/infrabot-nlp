"""Tests for GCP Compute Tools."""

import pytest
from unittest.mock import patch, MagicMock
from google.api_core.exceptions import GoogleAPICallError
from google.cloud.compute_v1 import Instance, AttachedDisk, NetworkInterface, AccessConfig

from adk_cli_agent.tools.gcp.tools.compute_tools import (
    list_instances,
    create_instance,
    delete_instance,
    start_instance,
    stop_instance,
    get_instance_details
)
from adk_cli_agent.tools.gcp.base.types import ToolResult

# Mock data for testing
TEST_PROJECT = "test-project"
TEST_ZONE = "us-central1-a"
TEST_INSTANCE_NAME = "test-instance"

# Fixtures

@pytest.fixture
def mock_instance():
    """Create a mock Instance object."""
    instance = Instance()
    instance.name = TEST_INSTANCE_NAME
    instance.id = "1234567890"
    instance.status = "RUNNING"
    instance.machine_type = f"zones/{TEST_ZONE}/machineTypes/e2-micro"
    instance.creation_timestamp = "2023-01-01T00:00:00.000Z"
    
    # Add network interface
    network_iface = NetworkInterface()
    network_iface.name = "nic0"
    network_iface.network = f"projects/{TEST_PROJECT}/global/networks/default"
    network_iface.network_i_p = "10.0.0.2"
    
    access_config = AccessConfig()
    access_config.name = "External NAT"
    access_config.nat_i_p = "34.123.45.67"
    access_config.type_ = "ONE_TO_ONE_NAT"
    network_iface.access_configs = [access_config]
    
    instance.network_interfaces = [network_iface]
    
    # Add disk
    disk = AttachedDisk()
    disk.boot = True
    disk.device_name = "boot-disk"
    disk.auto_delete = True
    disk.type_ = "PERSISTENT"
    disk.mode = "READ_WRITE"
    disk.interface = "SCSI"
    disk.kind = "compute#attachedDisk"
    
    instance.disks = [disk]
    
    return instance

# Tests

@patch('adk_cli_agent.tools.gcp.tools.compute_tools.compute_v1.InstancesClient')
def test_list_instances_success(mock_client_class, mock_instance):
    """Test successful listing of instances."""
    # Setup mock
    mock_client = MagicMock()
    mock_client.list.return_value = [mock_instance]
    mock_client_class.return_value = mock_client
    
    # Call the function
    result = list_instances(TEST_PROJECT, TEST_ZONE)
    
    # Assertions
    assert result.success is True
    assert len(result.data['instances']) == 1
    assert result.data['instances'][0]['name'] == TEST_INSTANCE_NAME
    mock_client.list.assert_called_once_with(project=TEST_PROJECT, zone=TEST_ZONE, filter=None)

@patch('adk_cli_agent.tools.gcp.tools.compute_tools.compute_v1.InstancesClient')
def test_list_instances_error(mock_client_class):
    """Test error handling when listing instances."""
    # Setup mock to raise exception
    mock_client = MagicMock()
    mock_client.list.side_effect = GoogleAPICallError("API error")
    mock_client_class.return_value = mock_client
    
    # Call the function
    result = list_instances(TEST_PROJECT, TEST_ZONE)
    
    # Assertions
    assert result.success is False
    assert "API error" in result.message
    assert result.error_code == "LIST_INSTANCES_FAILED"

@patch('adk_cli_agent.tools.gcp.tools.compute_tools.compute_v1.InstancesClient')
def test_create_instance_success(mock_client_class):
    """Test successful instance creation."""
    # Setup mock
    mock_client = MagicMock()
    operation = MagicMock()
    operation.name = "operation-123"
    operation.target_link = f"projects/{TEST_PROJECT}/zones/{TEST_ZONE}/operations/operation-123"
    operation.status = "RUNNING"
    mock_client.insert.return_value = operation
    mock_client_class.return_value = mock_client
    
    # Call the function
    result = create_instance(
        project_id=TEST_PROJECT,
        zone=TEST_ZONE,
        instance_name=TEST_INSTANCE_NAME,
        machine_type="e2-micro",
        disk_size_gb=20
    )
    
    # Assertions
    assert result.success is True
    assert "started" in result.message
    assert result.data["operation_id"] == "operation-123"
    mock_client.insert.assert_called_once()

@patch('adk_cli_agent.tools.gcp.tools.compute_tools.compute_v1.InstancesClient')
def test_get_instance_details_success(mock_client_class, mock_instance):
    """Test successful retrieval of instance details."""
    # Setup mock
    mock_client = MagicMock()
    mock_client.get.return_value = mock_instance
    mock_client_class.return_value = mock_client
    
    # Call the function
    result = get_instance_details(TEST_PROJECT, TEST_ZONE, TEST_INSTANCE_NAME)
    
    # Assertions
    assert result.success is True
    assert result.data['instance']['name'] == TEST_INSTANCE_NAME
    assert result.data['instance']['status'] == "RUNNING"
    mock_client.get.assert_called_once_with(
        project=TEST_PROJECT,
        zone=TEST_ZONE,
        instance=TEST_INSTANCE_NAME
    )

@patch('adk_cli_agent.tools.gcp.tools.compute_tools.compute_v1.InstancesClient')
def test_stop_instance_success(mock_client_class):
    """Test successful instance stop."""
    # Setup mock
    mock_client = MagicMock()
    operation = MagicMock()
    operation.name = "operation-stop-123"
    operation.target_link = f"projects/{TEST_PROJECT}/zones/{TEST_ZONE}/operations/operation-stop-123"
    operation.status = "RUNNING"
    mock_client.stop.return_value = operation
    mock_client_class.return_value = mock_client
    
    # Call the function
    result = stop_instance(TEST_PROJECT, TEST_ZONE, TEST_INSTANCE_NAME)
    
    # Assertions
    assert result.success is True
    assert "initiated" in result.message
    assert result.data["operation_type"] == "stop_instance"
    mock_client.stop.assert_called_once_with(
        project=TEST_PROJECT,
        zone=TEST_ZONE,
        instance=TEST_INSTANCE_NAME
    )

@patch('adk_cli_agent.tools.gcp.tools.compute_tools.compute_v1.InstancesClient')
def test_delete_instance_success(mock_client_class):
    """Test successful instance deletion."""
    # Setup mock
    mock_client = MagicMock()
    operation = MagicMock()
    operation.name = "operation-delete-123"
    operation.target_link = f"projects/{TEST_PROJECT}/zones/{TEST_ZONE}/operations/operation-delete-123"
    operation.status = "RUNNING"
    mock_client.delete.return_value = operation
    mock_client_class.return_value = mock_client
    
    # Call the function
    result = delete_instance(TEST_PROJECT, TEST_ZONE, TEST_INSTANCE_NAME)
    
    # Assertions
    assert result.success is True
    assert "started" in result.message
    assert result.data["operation_type"] == "delete_instance"
    mock_client.delete.assert_called_once_with(
        project=TEST_PROJECT,
        zone=TEST_ZONE,
        instance=TEST_INSTANCE_NAME
    )
