"""Unit tests for GCP tools functionality."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))
import pytest
from unittest.mock import MagicMock, patch, Mock
from google.api_core import operation

from my_cli_agent.tools.gcp_tools import (
    list_gcp_projects,
    create_gcp_project,
    delete_gcp_project,
    execute_command
)
from my_cli_agent.tools.base import ToolResult
from my_cli_agent.tools.gcp.base.exceptions import GCPToolsError, GCPValidationError
from my_cli_agent.tools.gcp.base.types import GCPProject

@pytest.fixture
def mock_project_manager():
    """Mock project manager fixture."""
    with patch('my_cli_agent.tools.gcp.management.projects.get_project_manager') as mock:
        manager = MagicMock()
        mock.return_value = manager
        yield manager

class TestGCPTools:
    """Test suite for GCP tools functionality."""

    def test_mock_projects_generation(self, mock_project_manager):
        """Test the mock project data generation for different environments."""
        # Test dev environment
        mock_dev_projects = [
            GCPProject(project_id="mock-dev-123", display_name="Mock Dev Project"),
            GCPProject(project_id="mock-dev-124", display_name="Mock Development Service")
        ]
        mock_project_manager.list_projects.return_value = mock_dev_projects

        result = list_gcp_projects("dev")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Mock Dev Project" in result.result
        assert "mock-dev-123" in result.result

        # Test staging environment
        mock_stg_projects = [
            GCPProject(project_id="mock-stg-456", display_name="Mock Staging Project"),
            GCPProject(project_id="mock-stg-457", display_name="Mock Staging Service")
        ]
        mock_project_manager.list_projects.return_value = mock_stg_projects
        
        result = list_gcp_projects("stg")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Mock Staging Project" in result.result
        assert "mock-stg-456" in result.result

        # Test production environment
        mock_prod_projects = [
            GCPProject(project_id="mock-prod-789", display_name="Mock Production Project"),
            GCPProject(project_id="mock-prod-790", display_name="Mock Production Service")
        ]
        mock_project_manager.list_projects.return_value = mock_prod_projects
        
        result = list_gcp_projects("prod")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Mock Production Project" in result.result
        assert "mock-prod-789" in result.result

    def test_list_projects_api_success(self, mock_project_manager):
        """Test successful project listing."""
        projects = [
            GCPProject(project_id="dev-project-1", display_name="Dev Project 1"),
            GCPProject(project_id="dev-project-2", display_name="Dev Project 2")
        ]
        mock_project_manager.list_projects.return_value = projects

        result = list_gcp_projects("dev")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Dev Project 1" in result.result
        assert "dev-project-1" in result.result
        assert "Found" in result.result
        assert "environment" in result.result

    def test_list_projects_error_handling(self, mock_project_manager):
        """Test error handling in list_projects."""
        mock_project_manager.list_projects.side_effect = GCPToolsError("API Error")
        
        result = list_gcp_projects("dev")
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Failed to list projects" in result.result
        assert "API Error" in str(result.error_message)

    def test_create_project_success(self, mock_project_manager):
        """Test successful project creation."""
        project = GCPProject(
            project_id="test-project-1", 
            display_name="Test Project 1"
        )
        mock_project_manager.create_project.return_value = project

        result = create_gcp_project("test-project-1", "Test Project 1")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Test Project 1" in result.result
        assert "test-project-1" in result.result
        assert "created successfully" in result.result

    def test_create_project_validation(self, mock_project_manager):
        """Test project creation input validation."""
        mock_project_manager.create_project.side_effect = GCPValidationError("Invalid project ID")

        result = create_gcp_project("invalid@id")
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Failed to create project" in result.result
        assert "Invalid project ID" in str(result.error_message)

    def test_create_project_already_exists(self, mock_project_manager):
        """Test project creation when project already exists."""
        mock_project_manager.create_project.side_effect = GCPToolsError("Project ID already exists")

        result = create_gcp_project("existing-project")
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Failed to create project" in result.result
        assert "already exists" in str(result.error_message)

    def test_delete_project_success(self, mock_project_manager):
        """Test successful project deletion."""
        result = delete_gcp_project("test-project-1")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "deleted successfully" in result.result

    def test_delete_project_error(self, mock_project_manager):
        """Test project deletion error handling."""
        mock_project_manager.delete_project.side_effect = GCPToolsError("Project not found")

        result = delete_gcp_project("nonexistent-project")
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Failed to delete project" in result.result
        assert "Project not found" in str(result.error_message)

    def test_command_execution(self, mock_project_manager):
        """Test command execution."""
        # Setup mock projects for listing
        projects = [
            GCPProject(project_id="dev-project-1", display_name="Dev Project 1"),
            GCPProject(project_id="dev-project-2", display_name="Dev Project 2")
        ]
        mock_project_manager.list_projects.return_value = projects

        # Test list command
        result = execute_command("list gcp projects dev")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "Dev Project 1" in result.result

        # Test create command
        project = GCPProject(project_id="new-project", display_name="New Project")
        mock_project_manager.create_project.return_value = project

        result = execute_command("create gcp project new-project")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "created successfully" in result.result

        # Test delete command
        result = execute_command("delete gcp project test-project")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "deleted successfully" in result.result

        # Test invalid command
        result = execute_command("invalid command")
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Unknown GCP command" in result.result

    def test_command_typo_handling(self, mock_project_manager):
        """Test handling of common command typos."""
        # Test "crate" instead of "create"
        result = execute_command("crate project test-project")
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Unknown GCP command" in result.result
        assert "create gcp project" in result.result.lower()

        # Test missing "gcp" keyword
        result = execute_command("create project test-project")
        assert isinstance(result, ToolResult)
        assert result.success is True  # Should still work even without "gcp" keyword
        assert "created successfully" in result.result

    def test_command_execution_with_spaces(self, mock_project_manager):
        """Test command execution with various space formatting."""
        project = GCPProject(project_id="test-project", display_name="Test Project")
        mock_project_manager.create_project.return_value = project

        # Extra spaces
        result = execute_command("  create    gcp    project    test-project  ")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "created successfully" in result.result

        # With project name containing spaces
        result = execute_command("create gcp project test-project My Test Project")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "created successfully" in result.result

    def test_project_id_validation(self, mock_project_manager):
        """Test project ID validation rules."""
        # Test invalid characters
        mock_project_manager.create_project.side_effect = GCPValidationError(
            "Project ID must start with a lowercase letter and contain only lowercase letters, numbers, and hyphens"
        )
        
        result = create_gcp_project("Invalid@Project")
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Failed to create project" in result.result
        assert "lowercase" in str(result.error_message)

        # Test numeric start
        result = create_gcp_project("123-project")
        assert isinstance(result, ToolResult)
        assert result.success is False

        # Test uppercase letters
        result = create_gcp_project("Test-Project")
        assert isinstance(result, ToolResult)
        assert result.success is False

    def test_intent_detection_bulk_delete_en(self, intent_detector):
        # Test bulk deletion patterns in English
        text = "delete projects proj1 and proj2"
        intent, params = intent_detector.detect_intent(text)
        assert intent == "delete_project"
        assert params['project_ids'] == ['proj1', 'proj2']
        assert params['is_bulk'] is True

        text = "delete all projects in production"
        intent, params = intent_detector.detect_intent(text)
        assert intent == "delete_project"
        assert params['is_bulk'] is True
        assert params['environment'] == 'prod'

    def test_intent_detection_bulk_delete_id(self, intent_detector):
        # Test bulk deletion patterns in Indonesian
        text = "hapus projects proj1, proj2 dan proj3"
        intent, params = intent_detector.detect_intent(text)
        assert intent == "delete_project"
        assert params['project_ids'] == ['proj1', 'proj2', 'proj3']
        assert params['is_bulk'] is True

        text = "hapus semua projects di development"
        intent, params = intent_detector.detect_intent(text)
        assert intent == "delete_project"
        assert params['is_bulk'] is True
        assert params['environment'] == 'dev'

    @patch('builtins.input', return_value='y')
    def test_gcp_tools_bulk_delete(mock_input, gcp_tools):
        projects = ['proj1', 'proj2']
        result = gcp_tools.delete_gcp_project(project_ids=projects, is_bulk=True)
        assert "Successfully deleted" in result
        assert all(pid in result for pid in projects)

    def test_gcp_tools_bulk_delete_with_environment(gcp_tools):
        projects = ['prod-proj1', 'dev-proj2']
        result = gcp_tools.delete_gcp_project(
            project_ids=projects,
            environment='prod',
            is_bulk=True
        )
        assert "Successfully deleted" in result
        assert "Skipped dev-proj2" in result
