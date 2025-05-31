"""
Unit tests for GCP project management functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google.cloud import resourcemanager_v3

from my_cli_agent.tools.gcp.management.projects import (
    ProjectManager,
    get_project_manager,
    get_mock_projects
)
from my_cli_agent.tools.gcp.base.types import GCPProject
from my_cli_agent.tools.gcp.base.client import GCPClientManager
from my_cli_agent.tools.gcp.base.exceptions import (
    GCPToolsError,
    GCPResourceNotFoundError,
    GCPValidationError
)

# Create alias for backward compatibility  
GCPError = GCPToolsError
GCPResourceError = GCPToolsError


class TestProjectManager:
    """Test cases for ProjectManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client_manager = MagicMock(spec=GCPClientManager)
        self.project_manager = ProjectManager(client_manager=self.mock_client_manager)
    
    @patch('my_cli_agent.tools.gcp.management.projects.google.auth.default')
    @patch('my_cli_agent.tools.gcp.management.projects.resourcemanager_v3.ProjectsClient')
    def test_list_projects_success(self, mock_client_class, mock_auth):
        """Test successful project listing."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "default-project")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create mock projects
        mock_project1 = Mock()
        mock_project1.project_id = "test-dev-123"
        mock_project1.display_name = "Test Dev Project"
        mock_project1.state.name = "ACTIVE"
        mock_project1.labels = {"env": "dev"}
        
        mock_project2 = Mock()
        mock_project2.project_id = "test-prod-456"
        mock_project2.display_name = "Test Prod Project"
        mock_project2.state.name = "ACTIVE"
        mock_project2.labels = {"env": "prod"}
        
        mock_client.search_projects.return_value = [mock_project1, mock_project2]
        
        # Test listing all projects
        result = self.project_manager.list_projects("all")
        
        assert len(result) == 2
        assert all(isinstance(p, GCPProject) for p in result)
        assert result[0].project_id == "test-dev-123"
        assert result[1].project_id == "test-prod-456"
        
        mock_auth.assert_called_once()
        mock_client.search_projects.assert_called_once()
    
    @patch('my_cli_agent.tools.gcp.management.projects.google.auth.default')
    @patch('my_cli_agent.tools.gcp.management.projects.resourcemanager_v3.ProjectsClient')
    def test_list_projects_with_environment_filter(self, mock_client_class, mock_auth):
        """Test project listing with environment filtering."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "default-project")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create mock projects
        mock_project1 = Mock()
        mock_project1.project_id = "test-dev-123"
        mock_project1.display_name = "Test Dev Project"
        mock_project1.state.name = "ACTIVE"
        mock_project1.labels = {}
        
        mock_project2 = Mock()
        mock_project2.project_id = "test-prod-456"
        mock_project2.display_name = "Test Prod Project"
        mock_project2.state.name = "ACTIVE"
        mock_project2.labels = {}
        
        mock_client.search_projects.return_value = [mock_project1, mock_project2]
        
        # Test filtering by dev environment
        result = self.project_manager.list_projects("dev")
        
        assert len(result) == 1
        assert result[0].project_id == "test-dev-123"
    
    @patch('my_cli_agent.tools.gcp.management.projects.google.auth.default')
    def test_list_projects_error(self, mock_auth):
        """Test project listing error handling."""
        mock_auth.side_effect = Exception("Auth failed")
        
        with pytest.raises(GCPError, match="Failed to list projects"):
            self.project_manager.list_projects()
    
    def test_get_project_success(self):
        """Test successful project retrieval."""
        mock_project = GCPProject(
            id="test-project-123",
            project_id="test-project-123",
            name="Test Project",
            status="ACTIVE",
            resource_type="project",
            labels={}
        )
        
        self.mock_client_manager.validate_project_access.return_value = mock_project
        
        result = self.project_manager.get_project("test-project-123")
        
        assert result == mock_project
        self.mock_client_manager.validate_project_access.assert_called_once_with("test-project-123")
    
    def test_get_project_invalid_id(self):
        """Test project retrieval with invalid ID."""
        with pytest.raises(GCPValidationError):
            self.project_manager.get_project("invalid_project_id!")
    
    def test_get_project_not_found(self):
        """Test project retrieval when project not found."""
        self.mock_client_manager.validate_project_access.side_effect = Exception("Not found")
        
        with pytest.raises(GCPResourceError, match="Failed to get project"):
            self.project_manager.get_project("test-project-123")
    
    @patch('my_cli_agent.tools.gcp.management.projects.google.auth.default')
    @patch('my_cli_agent.tools.gcp.management.projects.resourcemanager_v3.ProjectsClient')
    def test_create_project_success(self, mock_client_class, mock_auth):
        """Test successful project creation."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "default-project")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock operation and result
        mock_operation = Mock()
        mock_result = Mock()
        mock_result.project_id = "new-project-123"
        mock_result.display_name = "New Project"
        mock_result.state.name = "ACTIVE"
        mock_result.labels = {"env": "test"}
        
        mock_operation.result.return_value = mock_result
        mock_client.create_project.return_value = mock_operation
        
        # Test project creation
        result = self.project_manager.create_project(
            "new-project-123",
            name="New Project",
            labels={"env": "test"}
        )
        
        assert isinstance(result, GCPProject)
        assert result.project_id == "new-project-123"
        assert result.name == "New Project"
        assert result.labels == {"env": "test"}
        
        mock_client.create_project.assert_called_once()
        mock_operation.result.assert_called_once()
    
    def test_create_project_invalid_id(self):
        """Test project creation with invalid ID."""
        with pytest.raises(GCPValidationError):
            self.project_manager.create_project("invalid_project_id!")
    
    @patch('my_cli_agent.tools.gcp.management.projects.google.auth.default')
    def test_create_project_error(self, mock_auth):
        """Test project creation error handling."""
        mock_auth.side_effect = Exception("Creation failed")
        
        with pytest.raises(GCPResourceError, match="Failed to create project"):
            self.project_manager.create_project("new-project-123")
    
    @patch('my_cli_agent.tools.gcp.management.projects.google.auth.default')
    @patch('my_cli_agent.tools.gcp.management.projects.resourcemanager_v3.ProjectsClient')
    def test_update_project_success(self, mock_client_class, mock_auth):
        """Test successful project update."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "default-project")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock current project
        mock_current_project = Mock()
        mock_current_project.project_id = "test-project-123"
        mock_current_project.display_name = "Old Name"
        mock_current_project.labels = {}
        
        # Mock updated project
        mock_updated_project = Mock()
        mock_updated_project.project_id = "test-project-123"
        mock_updated_project.display_name = "New Name"
        mock_updated_project.state.name = "ACTIVE"
        mock_updated_project.labels = {"env": "updated"}
        
        mock_client.get_project.return_value = mock_current_project
        mock_client.update_project.return_value = mock_updated_project
        
        # Test project update
        result = self.project_manager.update_project(
            "test-project-123",
            name="New Name",
            labels={"env": "updated"}
        )
        
        assert isinstance(result, GCPProject)
        assert result.project_id == "test-project-123"
        assert result.name == "New Name"
        assert result.labels == {"env": "updated"}
        
        mock_client.get_project.assert_called_once()
        mock_client.update_project.assert_called_once()
    
    @patch('my_cli_agent.tools.gcp.management.projects.google.auth.default')
    @patch('my_cli_agent.tools.gcp.management.projects.resourcemanager_v3.ProjectsClient')
    def test_delete_project_success(self, mock_client_class, mock_auth):
        """Test successful project deletion."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "default-project")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_operation = Mock()
        mock_operation.result.return_value = None
        mock_client.delete_project.return_value = mock_operation
        
        # Test project deletion
        result = self.project_manager.delete_project("test-project-123")
        
        assert result is True
        mock_client.delete_project.assert_called_once_with(name="projects/test-project-123")
        mock_operation.result.assert_called_once()
    
    def test_matches_environment_all(self):
        """Test environment matching for 'all'."""
        project = GCPProject(
            id="any-project-123",
            project_id="any-project-123",
            name="Any Project",
            status="ACTIVE",
            resource_type="project",
            labels={}
        )
        
        assert self.project_manager._matches_environment(project, "all") is True
    
    def test_matches_environment_dev(self):
        """Test environment matching for dev."""
        project_dev = GCPProject(
            id="test-dev-123",
            project_id="test-dev-123",
            name="Dev Project",
            status="ACTIVE",
            resource_type="project",
            labels={}
        )
        
        project_prod = GCPProject(
            id="test-prod-456",
            project_id="test-prod-456",
            name="Prod Project",
            status="ACTIVE",
            resource_type="project",
            labels={}
        )
        
        assert self.project_manager._matches_environment(project_dev, "dev") is True
        assert self.project_manager._matches_environment(project_prod, "dev") is False


class TestMockProjects:
    """Test cases for mock project functionality."""
    
    def test_get_mock_projects_all(self):
        """Test getting all mock projects."""
        result = get_mock_projects("all")
        
        assert len(result) == 8
        assert "Mock Dev Project (mock-dev-123)" in result
        assert "Mock Staging Project (mock-stg-456)" in result
        assert "Mock Production Project (mock-prod-789)" in result
    
    def test_get_mock_projects_dev(self):
        """Test getting dev mock projects."""
        result = get_mock_projects("dev")
        
        assert len(result) == 2
        assert all("-dev-" in project or "development" in project.lower() for project in result)
    
    def test_get_mock_projects_stg(self):
        """Test getting staging mock projects."""
        result = get_mock_projects("stg")
        
        assert len(result) == 2
        assert all("-stg-" in project or "-staging" in project.lower() for project in result)
    
    def test_get_mock_projects_prod(self):
        """Test getting production mock projects."""
        result = get_mock_projects("prod")
        
        assert len(result) == 2
        assert all("-prod-" in project or "-production" in project.lower() for project in result)
    
    def test_get_mock_projects_invalid(self):
        """Test getting projects with invalid environment."""
        result = get_mock_projects("invalid")
        
        assert len(result) == 1
        assert "No projects matching environment: invalid" in result[0]
    
    def test_get_mock_projects_no_match(self):
        """Test getting projects with no matches."""
        result = get_mock_projects("nonexistent")
        
        assert len(result) == 1
        assert "No projects found matching environment: nonexistent" in result[0]


class TestGlobalProjectManager:
    """Test cases for global project manager functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Reset global state
        import my_cli_agent.tools.gcp.management.projects as projects_module
        projects_module._project_manager = None
    
    def test_get_project_manager_new(self):
        """Test getting new project manager."""
        mock_client_manager = Mock()
        
        with patch('my_cli_agent.tools.gcp.management.projects.ProjectManager') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            result = get_project_manager(mock_client_manager)
            
            assert result == mock_instance
            mock_class.assert_called_once_with(mock_client_manager)
    
    def test_get_project_manager_cached(self):
        """Test getting cached project manager."""
        with patch('my_cli_agent.tools.gcp.management.projects.ProjectManager') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            # First call creates new instance
            result1 = get_project_manager()
            # Second call returns cached instance
            result2 = get_project_manager()
            
            assert result1 == mock_instance
            assert result2 == mock_instance
            assert mock_class.call_count == 1
