import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.tools.gcp_tools import list_gcp_projects, create_gcp_project, HAS_GCP_TOOLS
from my_cli_agent.models import ToolResult

# A mock project object that simulates the structure of the real GCP project object
class MockGcpProject:
    def __init__(self, project_id, display_name):
        self.project_id = project_id
        self.display_name = display_name

@unittest.skipIf(not HAS_GCP_TOOLS, "GCP libraries not installed, skipping GCP tool tests")
class TestGcpTools(unittest.TestCase):

    @patch('my_cli_agent.tools.gcp_tools.google.auth.default')
    @patch('my_cli_agent.tools.gcp_tools.resourcemanager_v3.ProjectsClient')
    def test_list_gcp_projects_success(self, mock_projects_client, mock_auth):
        """Test listing GCP projects successfully."""
        # Mock the authentication and the client
        mock_auth.return_value = (None, None)
        mock_client_instance = mock_projects_client.return_value
        
        # Setup mock projects to be returned by the API call
        mock_projects = [
            MockGcpProject("proj-dev-123", "Project Dev"),
            MockGcpProject("proj-stg-456", "Project Staging"),
            MockGcpProject("proj-prod-789", "Project Prod"),
        ]
        mock_client_instance.search_projects.return_value = mock_projects

        # Test filtering for 'dev'
        result_dev = list_gcp_projects(env="dev")
        self.assertTrue(result_dev.success)
        self.assertIn("Found 1 projects", result_dev.result)

    @patch('google.cloud.compute_v1.InstancesClient')
    def test_list_gce_instances_success(self, mock_client):
        """Test successfully listing GCE instances."""
        # Arrange
        mock_client_instance = mock_client.return_value

        # Create mock instances
        mock_instance_1 = MagicMock()
        mock_instance_1.name = "instance-1"
        mock_instance_1.status = "RUNNING"

        mock_instance_2 = MagicMock()
        mock_instance_2.name = "instance-2"
        mock_instance_2.status = "TERMINATED"

        mock_client_instance.list.return_value = [mock_instance_1, mock_instance_2]

        # Act
        from my_cli_agent.tools.gcp_tools import list_gce_instances
        result = list_gce_instances(project_id="test-project", zone="us-central1-a")

        # Assert
        self.assertTrue(result.success)
        self.assertIn("Name: instance-1, Status: RUNNING", result.result)
        self.assertIn("Name: instance-2, Status: TERMINATED", result.result)
        mock_client_instance.list.assert_called_once_with(project="test-project", zone="us-central1-a")

    @patch('my_cli_agent.tools.gcp_tools.google.auth.default')
    def test_list_gcp_projects_auth_failure(self, mock_auth):
        """Test handling of GCP authentication failure."""
        import google.auth.exceptions
        mock_auth.side_effect = google.auth.exceptions.DefaultCredentialsError("Auth failed")
        
        result = list_gcp_projects()
        self.assertFalse(result.success)
        self.assertIn("GCP authentication failed", result.error_message)

    def test_create_gcp_project_success_simulation(self):
        """Test the successful simulation of creating a project."""
        project_id = "my-simulated-project"
        result = create_gcp_project(project_id)
        self.assertTrue(result.success)
        self.assertIn(f"Successfully simulated the creation of project '{project_id}'", result.result)

    def test_create_gcp_project_invalid_id(self):
        """Test create_gcp_project with an invalid project ID."""
        result = create_gcp_project("Invalid ID With Spaces")
        self.assertFalse(result.success)
        self.assertIn("Invalid project ID", result.error_message)

    def test_create_gcp_project_empty_id(self):
        """Test create_gcp_project with an empty project ID."""
        result = create_gcp_project("")
        self.assertFalse(result.success)
        self.assertIn("Invalid project ID", result.error_message)

if __name__ == '__main__':
    unittest.main()