"""Unit tests for ADK CLI Agent's GCP VPC subnet delete functionality."""

import pytest
import json
from unittest.mock import patch, MagicMock

from adk_cli_agent.tools.gcp_subnet import delete_subnet

@pytest.fixture
def mock_get_gcp_credentials():
    """Mock the get_gcp_credentials function."""
    with patch("adk_cli_agent.tools.gcp_subnet.get_gcp_credentials") as mock_credentials:
        mock_credentials.return_value = MagicMock()
        yield mock_credentials

@pytest.fixture
def mock_compute_subnetworks_client():
    """Mock GCP Compute Subnetworks Client."""
    with patch("adk_cli_agent.tools.gcp_subnet.compute_v1.SubnetworksClient", create=True) as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Set up a successful get operation
        mock_subnet = MagicMock()
        mock_subnet.name = "test-subnet"
        mock_subnet.region = "us-central1"
        mock_client_instance.get.return_value = mock_subnet
        
        # Set up a successful delete operation
        mock_operation = MagicMock()
        mock_result = MagicMock()
        mock_operation.result.return_value = mock_result
        mock_client_instance.delete.return_value = mock_operation
        
        yield mock_client

@pytest.fixture
def mock_confirmation():
    """Mock confirmation to always return True."""
    with patch("adk_cli_agent.tools.gcp_subnet.confirm_action", return_value=True) as mock_confirm:
        yield mock_confirm

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for CLI commands."""
    with patch("adk_cli_agent.tools.gcp_subnet.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Subnet deleted successfully"
        yield mock_run

class TestDeleteSubnet:
    """Tests for delete_subnet function."""
    
    @patch("adk_cli_agent.tools.gcp_subnet.HAS_GCP_TOOLS_FLAG", True)
    def test_api_success(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, mock_confirmation):
        """Test deleting a subnet using the API successfully."""
        result = delete_subnet(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check if the API was called correctly
        mock_client_instance = mock_compute_subnetworks_client.return_value
        mock_client_instance.get.assert_called_once()
        mock_client_instance.delete.assert_called_once()
        
        # Check the result
        assert result["status"] == "success"
        assert "subnet" in result
        assert result["subnet"]["name"] == "test-subnet"
        assert result["subnet"]["region"] == "us-central1"
        assert result["operation"] == "api"
    
    @patch("adk_cli_agent.tools.gcp_subnet.HAS_GCP_TOOLS_FLAG", True)
    def test_subnet_not_found(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, mock_confirmation):
        """Test when subnet is not found."""
        # Set up the mock to raise an exception on get
        mock_client_instance = mock_compute_subnetworks_client.return_value
        mock_client_instance.get.side_effect = Exception("Subnet not found")
        
        result = delete_subnet(
            project_id="test-project", 
            subnet_name="nonexistent-subnet",
            region="us-central1"
        )
        
        # Check that delete was not called
        mock_client_instance.delete.assert_not_called()
        
        # Check the result
        assert result["status"] == "error"
        assert "not exist" in result["message"].lower() or "not found" in result["message"].lower()
    
    @patch("adk_cli_agent.tools.gcp_subnet.HAS_GCP_TOOLS_FLAG", False)
    def test_cli_success(self, mock_subprocess, mock_confirmation):
        """Test deleting a subnet using CLI successfully."""
        result = delete_subnet(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check if CLI was called
        mock_subprocess.assert_called_once()
        
        # Check the result
        assert result["status"] == "success"
        assert "subnet" in result
        assert result["subnet"]["name"] == "test-subnet"
        assert result["subnet"]["region"] == "us-central1"
        assert result["operation"] == "cli"

    @patch("adk_cli_agent.tools.gcp_subnet.confirm_action", return_value=False)
    def test_user_cancellation(self, mock_confirm):
        """Test cancellation flow when user does not confirm."""
        result = delete_subnet(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check the cancellation result
        assert result["status"] == "cancelled"
        assert "cancelled by user" in result["message"].lower()

class TestDeleteSubnetErrors:
    """Tests for error scenarios in delete_subnet."""
    
    @patch("adk_cli_agent.tools.gcp_subnet.HAS_GCP_TOOLS_FLAG", True)
    def test_api_exception_fallback_to_cli(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, 
                                           mock_confirmation, mock_subprocess):
        """Test API exception falling back to CLI approach."""
        # Set up the mock to successfully get the subnet but fail on delete
        mock_client_instance = mock_compute_subnetworks_client.return_value
        mock_client_instance.delete.side_effect = Exception("API Error")
        
        result = delete_subnet(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Verify the CLI was called as a fallback
        mock_subprocess.assert_called_once()
        assert result["status"] == "success"
    
    @patch("adk_cli_agent.tools.gcp_subnet.HAS_GCP_TOOLS_FLAG", False)
    @patch("adk_cli_agent.tools.gcp_subnet.subprocess.run")
    def test_permission_denied_error(self, mock_run, mock_confirmation):
        """Test handling of permission denied error."""
        # Create a CalledProcessError with permission denied message
        import subprocess
        error = subprocess.CalledProcessError(1, "cmd")
        error.stderr = "Permission denied: insufficient permissions"
        mock_run.side_effect = error
        
        result = delete_subnet(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check error handling
        assert result["status"] == "error"
        assert "permissions" in result["message"].lower()
    
    @patch("adk_cli_agent.tools.gcp_subnet.HAS_GCP_TOOLS_FLAG", False)
    @patch("adk_cli_agent.tools.gcp_subnet.subprocess.run")
    def test_not_found_error(self, mock_run, mock_confirmation):
        """Test handling of resource not found error."""
        # Create a CalledProcessError with not found message
        import subprocess
        error = subprocess.CalledProcessError(1, "cmd")
        error.stderr = "Resource not found: subnetwork test-subnet"
        mock_run.side_effect = error
        
        result = delete_subnet(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check error handling
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()
    
    @patch("adk_cli_agent.tools.gcp_subnet.HAS_GCP_TOOLS_FLAG", False)
    @patch("adk_cli_agent.tools.gcp_subnet.subprocess.run")
    def test_in_use_error(self, mock_run, mock_confirmation):
        """Test handling of subnet in use error."""
        # Create a CalledProcessError with in-use message
        import subprocess
        error = subprocess.CalledProcessError(1, "cmd")
        error.stderr = "Subnet is currently in use by resources"
        mock_run.side_effect = error
        
        result = delete_subnet(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check error handling
        assert result["status"] == "error"
        assert "in use" in result["message"].lower()
    
    @patch("adk_cli_agent.tools.gcp_subnet.HAS_GCP_TOOLS_FLAG", False)
    @patch("adk_cli_agent.tools.gcp_subnet.subprocess.run")
    def test_generic_error(self, mock_run, mock_confirmation):
        """Test handling of generic errors."""
        # Create a CalledProcessError with generic message
        import subprocess
        error = subprocess.CalledProcessError(1, "cmd")
        error.stderr = "Unknown error occurred"
        mock_run.side_effect = error
        
        result = delete_subnet(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check error handling
        assert result["status"] == "error"
        assert "Failed to delete subnet" in result["message"]
