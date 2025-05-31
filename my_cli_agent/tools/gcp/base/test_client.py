"""
Unit tests for GCP base client management functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google.auth.credentials import Credentials
from google.cloud import resourcemanager, compute

from my_cli_agent.tools.gcp.base.client import (
    GCPClientManager,
    get_client_manager,
    set_default_project
)
from my_cli_agent.tools.gcp.base.exceptions import (
    GCPAuthenticationError,
    GCPClientError
)
from my_cli_agent.tools.gcp.base.types import GCPProject


class TestGCPClientManager:
    """Test cases for GCPClientManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.project_id = "test-project-123"
        self.mock_credentials = Mock(spec=Credentials)
    
    def test_init_with_credentials(self):
        """Test initialization with provided credentials."""
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        
        assert manager.project_id == self.project_id
        assert manager.credentials == self.mock_credentials
        assert manager._clients == {}
    
    @patch('my_cli_agent.tools.gcp.base.client.default')
    def test_init_without_credentials(self, mock_default):
        """Test initialization with default credentials."""
        mock_default.return_value = (self.mock_credentials, self.project_id)
        
        manager = GCPClientManager()
        
        assert manager.project_id == self.project_id
        assert manager.credentials == self.mock_credentials
        mock_default.assert_called_once()
    
    @patch('my_cli_agent.tools.gcp.base.client.default')
    def test_init_authentication_error(self, mock_default):
        """Test initialization with authentication failure."""
        mock_default.side_effect = Exception("Auth failed")
        
        with pytest.raises(GCPAuthenticationError, match="Failed to authenticate with GCP"):
            GCPClientManager()
    
    @patch('my_cli_agent.tools.gcp.base.client.resourcemanager_v1.ProjectsClient')
    def test_get_resource_manager_client(self, mock_client_class):
        """Test getting Resource Manager client."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        
        client = manager.get_resource_manager_client()
        
        assert client == mock_client
        assert manager._clients['resource_manager'] == mock_client
        mock_client_class.assert_called_once_with(credentials=self.mock_credentials)
        
        # Test caching
        client2 = manager.get_resource_manager_client()
        assert client2 == mock_client
        assert mock_client_class.call_count == 1
    
    @patch('my_cli_agent.tools.gcp.base.client.resourcemanager_v1.ProjectsClient')
    def test_get_resource_manager_client_error(self, mock_client_class):
        """Test Resource Manager client creation error."""
        mock_client_class.side_effect = Exception("Client creation failed")
        
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        
        with pytest.raises(GCPClientError, match="Failed to create Resource Manager client"):
            manager.get_resource_manager_client()
    
    @patch('my_cli_agent.tools.gcp.base.client.compute_v1.InstancesClient')
    def test_get_compute_client(self, mock_client_class):
        """Test getting Compute Engine client."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        
        client = manager.get_compute_client()
        
        assert client == mock_client
        assert manager._clients['compute'] == mock_client
        mock_client_class.assert_called_once_with(credentials=self.mock_credentials)
    
    @patch('my_cli_agent.tools.gcp.base.client.compute_v1.NetworksClient')
    def test_get_vpc_client(self, mock_client_class):
        """Test getting VPC Networks client."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        
        client = manager.get_vpc_client()
        
        assert client == mock_client
        assert manager._clients['vpc'] == mock_client
        mock_client_class.assert_called_once_with(credentials=self.mock_credentials)
    
    @patch('my_cli_agent.tools.gcp.base.client.compute_v1.SubnetworksClient')
    def test_get_subnet_client(self, mock_client_class):
        """Test getting Subnet client."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        
        client = manager.get_subnet_client()
        
        assert client == mock_client
        assert manager._clients['subnet'] == mock_client
        mock_client_class.assert_called_once_with(credentials=self.mock_credentials)
    
    def test_validate_project_access_no_project(self):
        """Test project validation without project ID."""
        manager = GCPClientManager(credentials=self.mock_credentials)
        
        with pytest.raises(GCPAuthenticationError, match="No project ID specified"):
            manager.validate_project_access()
    
    @patch('my_cli_agent.tools.gcp.base.client.resourcemanager_v1.ProjectsClient')
    def test_validate_project_access_success(self, mock_client_class):
        """Test successful project validation."""
        mock_client = Mock()
        mock_project = Mock()
        mock_project.project_id = self.project_id
        mock_project.display_name = "Test Project"
        mock_project.state.name = "ACTIVE"
        mock_project.labels = {"env": "test"}
        
        mock_client.get_project.return_value = mock_project
        mock_client_class.return_value = mock_client
        
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        
        result = manager.validate_project_access()
        
        assert isinstance(result, GCPProject)
        assert result.project_id == self.project_id
        assert result.name == "Test Project"
        assert result.lifecycle_state == "ACTIVE"
        assert result.labels == {"env": "test"}
        
        mock_client.get_project.assert_called_once_with(name=f"projects/{self.project_id}")
    
    @patch('my_cli_agent.tools.gcp.base.client.resourcemanager_v1.ProjectsClient')
    def test_validate_project_access_error(self, mock_client_class):
        """Test project validation error."""
        mock_client = Mock()
        mock_client.get_project.side_effect = Exception("Access denied")
        mock_client_class.return_value = mock_client
        
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        
        with pytest.raises(GCPAuthenticationError, match="Failed to access project"):
            manager.validate_project_access()
    
    def test_close(self):
        """Test closing all clients."""
        mock_client1 = Mock()
        mock_client2 = Mock()
        
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        manager._clients = {
            'client1': mock_client1,
            'client2': mock_client2
        }
        
        manager.close()
        
        mock_client1.close.assert_called_once()
        mock_client2.close.assert_called_once()
        assert manager._clients == {}
    
    def test_close_with_error(self):
        """Test closing clients with error handling."""
        mock_client1 = Mock()
        mock_client1.close.side_effect = Exception("Close failed")
        mock_client2 = Mock()
        
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        manager._clients = {
            'client1': mock_client1,
            'client2': mock_client2
        }
        
        # Should not raise exception
        manager.close()
        
        mock_client1.close.assert_called_once()
        mock_client2.close.assert_called_once()
        assert manager._clients == {}
    
    def test_context_manager(self):
        """Test context manager functionality."""
        manager = GCPClientManager(
            project_id=self.project_id,
            credentials=self.mock_credentials
        )
        
        with patch.object(manager, 'close') as mock_close:
            with manager:
                pass
            mock_close.assert_called_once()


class TestGlobalClientManager:
    """Test cases for global client manager functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Reset global state
        import my_cli_agent.tools.gcp.base.client as client_module
        client_module._global_client_manager = None
    
    def test_get_client_manager_new(self):
        """Test getting new client manager."""
        with patch('my_cli_agent.tools.gcp.base.client.GCPClientManager') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            result = get_client_manager("test-project", force_new=True)
            
            assert result == mock_instance
            mock_class.assert_called_once_with("test-project", None)
    
    def test_get_client_manager_cached(self):
        """Test getting cached client manager."""
        with patch('my_cli_agent.tools.gcp.base.client.GCPClientManager') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            # First call creates new instance
            result1 = get_client_manager("test-project")
            # Second call returns cached instance
            result2 = get_client_manager()
            
            assert result1 == mock_instance
            assert result2 == mock_instance
            assert mock_class.call_count == 1
    
    def test_set_default_project(self):
        """Test setting default project."""
        mock_manager = Mock()
        
        import my_cli_agent.tools.gcp.base.client as client_module
        client_module._global_client_manager = mock_manager
        
        set_default_project("new-project-id")
        
        assert mock_manager.project_id == "new-project-id"
    
    def test_set_default_project_no_manager(self):
        """Test setting default project with no global manager."""
        # Should not raise exception
        set_default_project("new-project-id")
