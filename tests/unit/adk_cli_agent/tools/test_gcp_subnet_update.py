"""Tests for gcp_subnet_update.py."""

import pytest
from unittest.mock import patch, MagicMock

from adk_cli_agent.tools.gcp_subnet_update import enable_private_google_access, disable_private_google_access

@pytest.fixture
def mock_get_gcp_credentials():
    """Mock the get_gcp_credentials function."""
    with patch("adk_cli_agent.tools.gcp_subnet_update.get_gcp_credentials") as mock_credentials:
        mock_credentials.return_value = MagicMock()
        yield mock_credentials

@pytest.fixture
def mock_compute_v1_subnetwork():
    """Mock the compute_v1.Subnetwork class."""
    mock_subnetwork_class = MagicMock()
    with patch("adk_cli_agent.tools.gcp_subnet_update.compute_v1.Subnetwork", return_value=mock_subnetwork_class):
        yield mock_subnetwork_class

@pytest.fixture
def mock_compute_subnetworks_client(mock_compute_v1_subnetwork):
    """Mock GCP Compute Subnetworks Client."""
    with patch("adk_cli_agent.tools.gcp_subnet_update.compute_v1.SubnetworksClient", create=True) as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock subnet get operation
        mock_subnet = MagicMock()
        mock_subnet.private_ip_google_access = False
        mock_subnet.fingerprint = "test-fingerprint"
        mock_client_instance.get.return_value = mock_subnet
        
        # Mock patch operation
        mock_operation = MagicMock()
        mock_result = MagicMock()
        mock_operation.result.return_value = mock_result
        mock_client_instance.patch.return_value = mock_operation
        
        yield mock_client

@pytest.fixture
def mock_confirmation(monkeypatch):
    """Mock confirmation to always return True."""
    with patch("adk_cli_agent.tools.gcp_subnet_update.confirm_action", return_value=True) as mock_confirm:
        yield mock_confirm

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for CLI commands."""
    with patch("adk_cli_agent.tools.gcp_subnet_update.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Subnet updated successfully"
        yield mock_run

class TestEnablePrivateGoogleAccess:
    """Tests for enable_private_google_access function."""
    
    @patch("adk_cli_agent.tools.gcp_subnet_update.HAS_GCP_TOOLS_FLAG", True)
    def test_api_success(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, mock_compute_v1_subnetwork, mock_confirmation):
        """Test enabling private Google access using the API successfully."""
        result = enable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check if the API was called correctly
        mock_client_instance = mock_compute_subnetworks_client.return_value
        mock_client_instance.get.assert_called_once()
        mock_client_instance.patch.assert_called_once()
        
        # Verify subnetwork_resource parameter in patch call
        patch_call_kwargs = mock_client_instance.patch.call_args.kwargs
        assert "subnetwork_resource" in patch_call_kwargs
        subnet_update = patch_call_kwargs["subnetwork_resource"]
        assert subnet_update.private_ip_google_access is True
        assert subnet_update.fingerprint == "test-fingerprint"
        
        # Check the result
        assert result["status"] == "success"
        assert "subnet" in result
        assert result["subnet"]["name"] == "test-subnet"
        assert result["subnet"]["region"] == "us-central1"
        assert result["subnet"]["private_google_access"] is True
    
    @patch("adk_cli_agent.tools.gcp_subnet_update.HAS_GCP_TOOLS_FLAG", True)
    def test_already_enabled(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, mock_compute_v1_subnetwork, mock_confirmation):
        """Test when private Google access is already enabled."""
        # Set the mock subnet's private_ip_google_access to True
        mock_client_instance = mock_compute_subnetworks_client.return_value
        mock_client_instance.get.return_value.private_ip_google_access = True
        
        result = enable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check that patch was not called
        mock_client_instance.get.assert_called_once()
        mock_client_instance.patch.assert_not_called()
        
        # Check the result
        assert result["status"] == "success"
        assert "already enabled" in result["message"].lower()
    
    @patch("adk_cli_agent.tools.gcp_subnet_update.HAS_GCP_TOOLS_FLAG", False)
    def test_cli_success(self, mock_subprocess, mock_confirmation):
        """Test enabling private Google access using CLI successfully."""
        result = enable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check if CLI was called
        mock_subprocess.assert_called_once()
        
        # Check the result
        assert result["status"] == "success"
        assert "subnet" in result
        assert result["subnet"]["private_google_access"] is True

    @patch("adk_cli_agent.tools.gcp_subnet_update.confirm_action", return_value=False)
    def test_user_cancellation(self, mock_confirm):
        """Test cancellation flow when user does not confirm."""
        result = enable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check the cancellation result
        assert result["status"] == "cancelled"
        assert "cancelled by user" in result["message"].lower()


class TestDisablePrivateGoogleAccess:
    """Tests for disable_private_google_access function."""
    
    @patch("adk_cli_agent.tools.gcp_subnet_update.HAS_GCP_TOOLS_FLAG", True)
    def test_api_success(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, mock_compute_v1_subnetwork, mock_confirmation):
        """Test disabling private Google access using the API successfully."""
        # Set the mock subnet's private_ip_google_access to True
        mock_client_instance = mock_compute_subnetworks_client.return_value
        mock_client_instance.get.return_value.private_ip_google_access = True
        
        result = disable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check if the API was called correctly
        mock_client_instance.get.assert_called_once()
        mock_client_instance.patch.assert_called_once()
        
        # Verify subnetwork_resource parameter in patch call
        patch_call_kwargs = mock_client_instance.patch.call_args.kwargs
        assert "subnetwork_resource" in patch_call_kwargs
        subnet_update = patch_call_kwargs["subnetwork_resource"]
        assert subnet_update.private_ip_google_access is False
        assert subnet_update.fingerprint == "test-fingerprint"
        
        # Check the result
        assert result["status"] == "success"
        assert "subnet" in result
        assert result["subnet"]["private_google_access"] is False
    
    @patch("adk_cli_agent.tools.gcp_subnet_update.HAS_GCP_TOOLS_FLAG", True)
    def test_already_disabled(self, mock_get_gcp_credentials, mock_compute_subnetworks_client, mock_compute_v1_subnetwork, mock_confirmation):
        """Test when private Google access is already disabled."""
        # Subnet's private_ip_google_access is already False by default in the fixture
        
        result = disable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check that patch was not called
        mock_client_instance = mock_compute_subnetworks_client.return_value
        mock_client_instance.get.assert_called_once()
        mock_client_instance.patch.assert_not_called()
        
        # Check the result
        assert result["status"] == "success"
        assert "already disabled" in result["message"].lower()
    
    @patch("adk_cli_agent.tools.gcp_subnet_update.HAS_GCP_TOOLS_FLAG", False)
    def test_cli_success(self, mock_subprocess, mock_confirmation):
        """Test disabling private Google access using CLI successfully."""
        result = disable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check if CLI was called
        mock_subprocess.assert_called_once()
        
        # Check the result
        assert result["status"] == "success"
        assert "subnet" in result
        assert result["subnet"]["private_google_access"] is False

    @patch("adk_cli_agent.tools.gcp_subnet_update.confirm_action", return_value=False)
    def test_user_cancellation(self, mock_confirm):
        """Test cancellation flow when user does not confirm."""
        result = disable_private_google_access(
            project_id="test-project", 
            subnet_name="test-subnet",
            region="us-central1"
        )
        
        # Check the cancellation result
        assert result["status"] == "cancelled"
        assert "cancelled by user" in result["message"].lower()
