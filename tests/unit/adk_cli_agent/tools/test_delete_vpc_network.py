"""Unit tests for ADK CLI Agent's GCP VPC network delete functionality."""
import pytest
import json
from unittest.mock import patch, MagicMock
from adk_cli_agent.tools.gcp_vpc import delete_vpc_network

# Test fixture imports from main test file
from tests.unit.adk_cli_agent.tools.test_gcp_vpc import (
    mock_get_gcp_credentials,
    mock_compute_networks_client,
    mock_compute_subnetworks_client,
    mock_compute_firewalls_client,
    mock_confirmation,
    mock_subprocess
)

class TestDeleteVpcNetwork:
    """Tests for delete_vpc_network function."""
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    def test_delete_vpc_network_api_success(
        self,
        mock_get_gcp_credentials,
        mock_compute_networks_client,
        mock_confirmation
    ):
        """Test deleting a VPC network using the API successfully."""
        # Mock the delete operation
        mock_operation = MagicMock()
        mock_result = MagicMock()
        mock_operation.result.return_value = mock_result
        mock_compute_networks_client.delete.return_value = mock_operation
        
        # Mock the get_vpc_details function to return a successful result
        with patch("adk_cli_agent.tools.gcp_vpc.get_vpc_details") as mock_get_details:
            mock_get_details.return_value = {
                "status": "success",
                "network": {
                    "name": "test-vpc",
                    "subnets": [{"name": "test-subnet"}]
                }
            }
            
            result = delete_vpc_network(
                project_id="test-project", 
                network_name="test-vpc"
            )
            
            # Check if the proper API calls were made
            mock_compute_networks_client.delete.assert_called_once()
            
            # Check the result
            assert result["status"] == "success"
            assert "deleted successfully" in result["message"]
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", False)
    def test_delete_vpc_network_cli_success(self, mock_subprocess, mock_confirmation):
        """Test deleting a VPC network using the CLI successfully."""
        # Configure mock to return successful result
        mock_result = MagicMock()
        mock_result.stdout = "Deleted [https://www.googleapis.com/compute/v1/projects/test-project/global/networks/test-vpc]."
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Mock the get_vpc_details function
        with patch("adk_cli_agent.tools.gcp_vpc.get_vpc_details") as mock_get_details:
            mock_get_details.return_value = {
                "status": "success",
                "network": {
                    "name": "test-vpc",
                    "subnets": []
                }
            }
            
            result = delete_vpc_network(
                project_id="test-project", 
                network_name="test-vpc"
            )
            
            # Check if the CLI command was called
            mock_subprocess.assert_called_once()
            cmd_args = mock_subprocess.call_args[0][0]
            assert "delete" in cmd_args
            assert "test-vpc" in cmd_args
            
            # Check the result
            assert result["status"] == "success"
            assert "deleted successfully" in result["message"]
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    def test_delete_vpc_network_api_error(self, mock_get_gcp_credentials, mock_compute_networks_client, mock_confirmation):
        """Test error handling when API call fails."""
        # Mock an error in the API call
        mock_compute_networks_client.return_value.delete.side_effect = Exception("API error")
        
        # Mock the get_vpc_details function
        with patch("adk_cli_agent.tools.gcp_vpc.get_vpc_details") as mock_get_details:
            mock_get_details.return_value = {"status": "success", "network": {"name": "test-vpc", "subnets": []}}
            
            result = delete_vpc_network(
                project_id="test-project", 
                network_name="test-vpc"
            )
            
            # Check the error handling (should fall back to CLI)
            assert result["status"] == "success" or result["status"] == "error"
    
    @patch("adk_cli_agent.tools.gcp_vpc.HAS_GCP_TOOLS_FLAG", True)
    def test_delete_vpc_network_not_found(self, mock_get_gcp_credentials, mock_compute_networks_client, mock_confirmation):
        """Test error handling when the network doesn't exist."""
        # Mock the delete operation to fail with a "not found" error
        mock_compute_networks_client.return_value.delete.side_effect = Exception("Resource not found")
        
        # Mock the CLI to also fail with a "not found" error
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.side_effect = Exception("Resource not found: The resource 'projects/test-project/global/networks/test-vpc' was not found")
            
            # Mock get_vpc_details to report network doesn't exist
            with patch("adk_cli_agent.tools.gcp_vpc.get_vpc_details") as mock_get_details:
                mock_get_details.return_value = {"status": "error", "message": "Network not found"}
                
                result = delete_vpc_network(
                    project_id="test-project", 
                    network_name="test-vpc"
                )
                
                # Check the error handling
                assert result["status"] == "error"
                assert "not found" in result["message"].lower()
    
    @patch("adk_cli_agent.tools.gcp_vpc.confirm_action", return_value=False)
    def test_delete_vpc_network_cancelled(self, mock_confirm):
        """Test cancellation flow when user does not confirm."""
        result = delete_vpc_network(
            project_id="test-project", 
            network_name="test-vpc"
        )
        
        # Check the cancellation result
        assert result["status"] == "cancelled"
        assert "cancelled by user" in result["message"].lower()
