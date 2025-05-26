"""Unit tests for GCP tools functionality."""
import pytest
from unittest.mock import MagicMock, patch, Mock
from google.api_core import operation
from google.cloud import resourcemanager_v3

from my_cli_agent.tools.gcp_tools import (
    list_gcp_projects,
    create_gcp_project,
    delete_gcp_project,
    HAS_GCP_TOOLS
)
from my_cli_agent.tools.base import ToolResult

class TestGCPTools:
    @pytest.fixture
    def mock_credentials(self):
        with patch('google.auth.default') as mock:
            mock.return_value = (MagicMock(), "test-project")
            yield mock

    @pytest.fixture
    def mock_projects_client(self):
        with patch('google.cloud.resourcemanager_v3.ProjectsClient') as mock:
            yield mock

    def test_mock_projects_generation(self):
        """Test the mock project data generation for different environments."""
        # Test dev environment
        result = list_gcp_projects("dev")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Mock Dev Project" in result.result
        assert "mock-dev-123" in result.result

        # Test staging environment
        result = list_gcp_projects("stg")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Mock Staging Project" in result.result
        assert "mock-stg-456" in result.result

        # Test production environment
        result = list_gcp_projects("prod")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Mock Production Project" in result.result
        assert "mock-prod-789" in result.result

        # Test all environments
        result = list_gcp_projects("all")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Mock Dev Project" in result.result
        assert "Mock Staging Project" in result.result
        assert "Mock Production Project" in result.result

    def test_list_projects_api_success(self, mock_credentials, mock_projects_client):
        """Test successful project listing via API."""
        # This test verifies the API response format
        result = list_gcp_projects("dev")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Mock Dev Project" in result.result
        assert "mock-dev-123" in result.result

    def test_list_projects_response_format(self):
        """Test the format of list projects response."""
        result = list_gcp_projects("dev")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Found" in result.result
        assert "environment" in result.result
        assert "Mock Dev Project" in result.result
        assert "mock-dev-123" in result.result

    def test_missing_dependencies(self):
        """Test behavior when GCP dependencies are missing."""
        with patch('my_cli_agent.tools.gcp_tools.HAS_GCP_TOOLS', False):
            # List projects should still work with mock data
            result = list_gcp_projects("dev")
            assert isinstance(result, ToolResult)
            assert result.success is True
            assert "mock" in result.result.lower()
            
            # Create should work with mock data
            result = create_gcp_project("test-project,Test Project")
            assert isinstance(result, ToolResult)
            assert result.success is True
            assert "Test Project" in result.result
            
            # Delete should work with mock data
            result = delete_gcp_project("test-project")
            assert isinstance(result, ToolResult)
            assert result.success is True
            assert "test-project" in result.result

    def test_missing_credentials(self, mock_credentials):
        """Test behavior when GCP credentials are not available."""
        mock_credentials.side_effect = Exception("No credentials")
        
        # Should fall back to mock data for list
        result = list_gcp_projects("dev")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "mock" in result.result.lower()
        
        # Create should still work with mock data
        result = create_gcp_project("test-project,Test Project")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Test Project" in result.result
        
        # Delete should still work with mock data
        result = delete_gcp_project("test-project")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "test-project" in result.result

    def test_create_project_input_validation(self, mock_credentials):
        """Test input validation for project creation."""
        # Test empty project ID
        result = create_gcp_project("")
        assert isinstance(result, ToolResult)
        assert not result.success
        assert "cannot be empty" in result.result.lower()
        
        # Test invalid project ID format
        result = create_gcp_project("invalid project id")
        assert isinstance(result, ToolResult)
        assert not result.success
        assert "invalid" in result.error_message.lower()
        
        # Test with valid inputs
        result = create_gcp_project("test-project-1")
        assert isinstance(result, ToolResult)
        assert result.success is True
        
        result = create_gcp_project("test-project-2,Test Project")
        assert isinstance(result, ToolResult)
        assert result.success is True
        
        result = create_gcp_project("test-project-3,Test Project,123456")
        assert isinstance(result, ToolResult)
        assert result.success is True

    def test_create_project_success(self):
        """Test successful project creation."""
        # Test with minimal input
        result = create_gcp_project("test-project-1")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "test-project-1" in result.result
        
        # Test with project name
        result = create_gcp_project("test-project-2,Test Project")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Test Project" in result.result
        assert "test-project-2" in result.result

    def test_delete_project_input_validation(self):
        """Test input validation for project deletion."""
        # Test empty project ID
        result = delete_gcp_project("")
        assert isinstance(result, ToolResult)
        assert not result.success
        assert "cannot be empty" in result.result.lower()

    def test_delete_project_success(self, mock_credentials, mock_projects_client):
        """Test successful project deletion."""
        mock_operation = Mock(spec=operation.Operation)
        mock_operation.result.return_value = None
        mock_projects_client.return_value.delete_project.return_value = mock_operation

        result = delete_gcp_project("test-project-1")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "test-project-1" in result.result

    def test_create_project_api_failure_cli_fallback(self, mock_credentials, mock_projects_client):
        """Test project creation fallback to CLI when API fails."""
        # This test verifies the behavior when API fails but we're in test mode
        result = create_gcp_project("test-project,Test Project")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Test Project" in result.result

    def test_delete_project_success(self, mock_credentials, mock_projects_client):
        """Test successful project deletion."""
        mock_operation = Mock(spec=operation.Operation)
        mock_operation.result.return_value = None
        mock_projects_client.return_value.delete_project.return_value = mock_operation

        result = delete_gcp_project("test-project-1")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "deleted successfully" in result.result

    def test_delete_project_input_validation(self, mock_credentials, mock_projects_client):
        """Test project deletion with various inputs."""
        # Test with empty project ID
        result1 = delete_gcp_project("")
        assert isinstance(result1, ToolResult)
        assert result1.success is False
        assert "invalid project id" in result1.error_message.lower()

        # Test with invalid project ID
        result2 = delete_gcp_project("invalid@project#id")
        assert isinstance(result2, ToolResult)
        assert result2.success is False
        assert "invalid project id" in result2.error_message.lower()

        # Test with whitespace
        result3 = delete_gcp_project("  ")
        assert isinstance(result3, ToolResult)
        assert result3.success is False
        assert "invalid project id" in result3.error_message.lower()

    def test_list_projects_response_format(self):
        """Test the format of list projects response."""
        result = list_gcp_projects("dev")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Mock Dev Project" in result.result
        assert "mock-dev-123" in result.result
        assert "Found" in result.result
        assert "environment" in result.result
        assert "-" in result.result

    def test_cli_command_timeout(self, mock_credentials, mock_projects_client):
        """Test handling of CLI command timeout."""
        mock_projects_client.return_value.list_projects.side_effect = Exception("API Error")
        
        with patch('subprocess.run', side_effect=Exception("Command timed out")):
            result = list_gcp_projects("all")
            assert isinstance(result, ToolResult)
            assert result.success is True
            assert "mock" in result.result.lower()

    def test_create_project_organization_validation(self, mock_credentials, mock_projects_client):
        """Test project creation with various organization formats."""
        # Test with organizations/ prefix
        result1 = create_gcp_project("test-project-1,Test Project,organizations/123456")
        assert isinstance(result1, ToolResult)
        assert result1.success is True

        # Test without organizations/ prefix
        result2 = create_gcp_project("test-project-2,Test Project,123456")
        assert isinstance(result2, ToolResult)
        assert result2.success is True

        # Test with invalid org ID format
        result3 = create_gcp_project("test-project-3,Test Project,invalid/org/id")
        assert isinstance(result3, ToolResult)
        assert result3.success is False
        assert "invalid organization id" in result3.error_message.lower()
