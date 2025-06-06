"""Additional tests to improve coverage for gcp_subnet_update.py."""

import pytest
import subprocess
from unittest.mock import patch, MagicMock

from adk_cli_agent.tools.gcp_subnet_update import enable_private_google_access, disable_private_google_access

# Define our own fixtures to avoid relative imports
@pytest.fixture
def mock_get_gcp_credentials():
    """Mock the get_gcp_credentials function."""
    with patch("adk_cli_agent.tools.gcp_subnet_update.get_gcp_credentials") as mock_credentials:
        mock_credentials.return_value = MagicMock()
        yield mock_credentials

@pytest.fixture
def mock_compute_subnetworks_client():
    """Mock GCP Compute Subnetworks Client."""
    with patch("adk_cli_agent.tools.gcp_subnet_update.compute_v1.SubnetworksClient", create=True) as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock subnet get operation
        mock_subnet = MagicMock()
        mock_subnet.private_ip_google_access = False
        mock_client_instance.get.return_value = mock_subnet
        
        # Mock patch operation
        mock_operation = MagicMock()
        mock_result = MagicMock()
        mock_operation.result.return_value = mock_result
        mock_client_instance.patch.return_value = mock_operation
        
        yield mock_client

@pytest.fixture
def mock_confirmation():
    """Mock confirmation to always return True."""
    with patch("adk_cli_agent.tools.gcp_subnet_update.confirm_action", return_value=True) as mock_confirm:
        yield mock_confirm

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for CLI commands."""
    with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Subnet updated successfully"
        yield mock_run


class TestEnablePrivateGoogleAccessErrors:
    """Additional tests for error scenarios in enable_private_google_access."""
    
    @patch("adk_cli_agent.tools.gcp_subnet_update.HAS_GCP_TOOLS_FLAG", True)
    def test_api_exception_fallback_to_cli(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, 
                                          mock_confirmation, mock_subprocess):
        """Test API exception falling back to CLI approach."""
        # Force the API call to raise an exception
        mock_client_instance = mock_compute_subnetworks_client.return_value
        mock_client_instance.get.side_effect = Exception("API Error")
        
        result = enable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Verify the CLI was called as a fallback
        mock_subprocess.assert_called_once()
        assert result["status"] == "success"
    
    def test_permission_denied_error(self, mock_confirmation):
        """Test handling of permission denied error."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Create a CalledProcessError with permission denied message
            error = subprocess.CalledProcessError(1, "cmd")
            error.stderr = "Permission denied: insufficient permissions"
            mock_run.side_effect = error
            
            result = enable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "permissions" in result["message"].lower()
    
    def test_not_found_error(self, mock_confirmation):
        """Test handling of resource not found error."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Create a CalledProcessError with not found message
            error = subprocess.CalledProcessError(1, "cmd")
            error.stderr = "Resource not found: subnetwork test-subnet"
            mock_run.side_effect = error
            
            result = enable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "not found" in result["message"].lower()
    
    def test_network_error(self, mock_confirmation):
        """Test handling of network/API errors."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Create a CalledProcessError with timeout message
            error = subprocess.CalledProcessError(1, "cmd")
            error.stderr = "Timeout when accessing the API"
            mock_run.side_effect = error
            
            result = enable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "Network or API error" in result["message"]
    
    def test_generic_error(self, mock_confirmation):
        """Test handling of generic errors."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Create a CalledProcessError with generic message
            error = subprocess.CalledProcessError(1, "cmd")
            error.stderr = "Unknown error occurred"
            mock_run.side_effect = error
            
            result = enable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "Error enabling private Google access" in result["message"]
    
    def test_general_exception(self, mock_confirmation):
        """Test handling of general exceptions."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Make subprocess.run raise a general exception
            mock_run.side_effect = Exception("Unexpected error")
            
            result = enable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "Error enabling private Google access" in result["message"]


class TestDisablePrivateGoogleAccessErrors:
    """Additional tests for error scenarios in disable_private_google_access."""
    
    @patch("adk_cli_agent.tools.gcp_subnet_update.HAS_GCP_TOOLS_FLAG", True)
    def test_api_exception_fallback_to_cli(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, 
                                          mock_confirmation, mock_subprocess):
        """Test API exception falling back to CLI approach."""
        # Force the API call to raise an exception
        mock_client_instance = mock_compute_subnetworks_client.return_value
        mock_client_instance.get.side_effect = Exception("API Error")
        
        result = disable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Verify the CLI was called as a fallback
        mock_subprocess.assert_called_once()
        assert result["status"] == "success"
    
    def test_permission_denied_error(self, mock_confirmation):
        """Test handling of permission denied error."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Create a CalledProcessError with permission denied message
            error = subprocess.CalledProcessError(1, "cmd")
            error.stderr = "Permission denied: insufficient permissions"
            mock_run.side_effect = error
            
            result = disable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "permissions" in result["message"].lower()
    
    def test_not_found_error(self, mock_confirmation):
        """Test handling of resource not found error."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Create a CalledProcessError with not found message
            error = subprocess.CalledProcessError(1, "cmd")
            error.stderr = "Resource not found: subnetwork test-subnet"
            mock_run.side_effect = error
            
            result = disable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "not found" in result["message"].lower()
    
    def test_network_error(self, mock_confirmation):
        """Test handling of network/API errors."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Create a CalledProcessError with timeout message
            error = subprocess.CalledProcessError(1, "cmd")
            error.stderr = "Timeout when accessing the API"
            mock_run.side_effect = error
            
            result = disable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "Network or API error" in result["message"]
    
    def test_generic_error(self, mock_confirmation):
        """Test handling of generic errors."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Create a CalledProcessError with generic message
            error = subprocess.CalledProcessError(1, "cmd")
            error.stderr = "Unknown error occurred"
            mock_run.side_effect = error
            
            result = disable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "Error disabling private Google access" in result["message"]
    
    def test_general_exception(self, mock_confirmation):
        """Test handling of general exceptions."""
        with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
            # Make subprocess.run raise a general exception
            mock_run.side_effect = Exception("Unexpected error")
            
            result = disable_private_google_access(
                project_id="test-project", 
                subnet_name="test-subnet",
                region="us-central1"
            )
            
            # Check error handling
            assert result["status"] == "error"
            assert "Error disabling private Google access" in result["message"]


@patch("adk_cli_agent.tools.gcp_subnet_update.HAS_GCP_TOOLS_FLAG", False)
def test_gcp_tools_import_handling(mock_confirmation, mock_subprocess):
    """Test the handling when GCP tools are not available."""
    result = enable_private_google_access(
        project_id="test-project", 
        subnet_name="test-subnet",
        region="us-central1"
    )
    
    # Verify the function falls back to CLI
    mock_subprocess.assert_called_once()
    assert result["status"] == "success"