"""Unit tests for GCP Client."""

import json
import pytest
from unittest.mock import patch, MagicMock, mock_open

import google
from google.auth.exceptions import DefaultCredentialsError

from adk_cli_agent.tools.gcp.base.client import GCPClient
from adk_cli_agent.tools.gcp.base.exceptions import GCPAuthenticationError, GCPOperationError


class TestGCPClient:
    """Test cases for GCPClient class."""

    @patch('adk_cli_agent.tools.gcp.base.client.google.auth.default')
    def test_init_with_google_auth(self, mock_auth_default):
        """Test client initialization using Google Auth."""
        # Setup
        mock_credentials = MagicMock()
        mock_auth_default.return_value = (mock_credentials, "test-project")
        
        # Execute
        client = GCPClient()
        
        # Assert
        assert client.credentials == mock_credentials
        assert client.project_id == "test-project"
        assert client._authenticated is True
        mock_auth_default.assert_called_once()
    
    @patch('adk_cli_agent.tools.gcp.base.client.google.auth.default')
    def test_init_with_explicit_project(self, mock_auth_default):
        """Test client initialization with explicit project ID."""
        # Setup
        mock_credentials = MagicMock()
        mock_auth_default.return_value = (mock_credentials, "default-project")
        
        # Execute
        client = GCPClient(project_id="explicit-project")
        
        # Assert
        assert client.credentials == mock_credentials
        assert client.project_id == "explicit-project"  # Should keep explicit project
        assert client._authenticated is True
    
    @patch('adk_cli_agent.tools.gcp.base.client.google.auth.default')
    @patch('adk_cli_agent.tools.gcp.base.client.subprocess.run')
    def test_fallback_to_cli_auth(self, mock_subprocess, mock_auth_default):
        """Test fallback to CLI auth when Google Auth fails."""
        # Setup
        mock_auth_default.side_effect = DefaultCredentialsError()
        
        mock_result = MagicMock()
        mock_result.stdout = json.dumps([{"account": "test@example.com"}])
        mock_subprocess.return_value = mock_result
        
        # Execute
        client = GCPClient()
        
        # Assert
        assert client._authenticated is True
        mock_auth_default.assert_called_once()
        mock_subprocess.assert_called_once()
    
    @patch('adk_cli_agent.tools.gcp.base.client.google.auth.default')
    @patch('adk_cli_agent.tools.gcp.base.client.subprocess.run')
    def test_auth_failure(self, mock_subprocess, mock_auth_default):
        """Test authentication failure handling."""
        # Setup
        mock_auth_default.side_effect = DefaultCredentialsError()
        
        mock_subprocess.side_effect = Exception("CLI auth failed")
        
        # Execute and Assert
        with pytest.raises(GCPAuthenticationError):
            client = GCPClient()
    
    @patch('adk_cli_agent.tools.gcp.base.client.google.auth.default')
    @patch('adk_cli_agent.tools.gcp.base.client.subprocess.run')
    def test_execute_cli_command_success(self, mock_subprocess, mock_auth_default):
        """Test successful CLI command execution."""
        # Setup
        mock_auth_default.return_value = (MagicMock(), "test-project")
        
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"key": "value"})
        mock_subprocess.return_value = mock_result
        
        client = GCPClient()
        
        # Execute
        result = client.execute_cli_command(["compute", "instances", "list"])
        
        # Assert
        assert result == {"key": "value"}
        mock_subprocess.assert_called_once()
        args, kwargs = mock_subprocess.call_args
        assert args[0] == ["gcloud", "compute", "instances", "list", "--format=json", "--project", "test-project"]
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["check"] is True
    
    @patch('adk_cli_agent.tools.gcp.base.client.google.auth.default')
    @patch('adk_cli_agent.tools.gcp.base.client.subprocess.run')
    def test_execute_cli_command_without_json(self, mock_subprocess, mock_auth_default):
        """Test CLI command execution without JSON output."""
        # Setup
        mock_auth_default.return_value = (MagicMock(), "test-project")
        
        mock_result = MagicMock()
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        client = GCPClient()
        
        # Execute
        result = client.execute_cli_command(["compute", "ssh"], json_output=False)
        
        # Assert
        assert result == {"stdout": "Command output", "stderr": ""}
        args, kwargs = mock_subprocess.call_args
        assert args[0] == ["gcloud", "compute", "ssh", "--project", "test-project"]
        
    @patch('adk_cli_agent.tools.gcp.base.client.google.auth.default')
    @patch('adk_cli_agent.tools.gcp.base.client.subprocess.run')
    def test_execute_cli_command_error(self, mock_subprocess, mock_auth_default):
        """Test CLI command execution error handling."""
        # Setup
        mock_auth_default.return_value = (MagicMock(), "test-project")
        
        import subprocess
        mock_error = subprocess.CalledProcessError(1, "cmd")
        mock_error.stderr = "Command failed"
        mock_subprocess.side_effect = mock_error
        
        client = GCPClient()
        
        # Execute and Assert
        with pytest.raises(GCPOperationError) as exc:
            client.execute_cli_command(["invalid", "command"])
        
        assert "Command execution failed: Command failed" in str(exc.value)

    @patch('adk_cli_agent.tools.gcp.base.client.google.auth.default')
    @patch('adk_cli_agent.tools.gcp.base.client.subprocess.run')
    def test_execute_cli_command_json_parse_error(self, mock_subprocess, mock_auth_default):
        """Test CLI command with JSON parse error."""
        # Setup
        mock_auth_default.return_value = (MagicMock(), "test-project")
        
        mock_result = MagicMock()
        mock_result.stdout = "Invalid JSON"
        mock_subprocess.return_value = mock_result
        
        client = GCPClient()
        
        # Execute and Assert
        with pytest.raises(GCPOperationError) as exc:
            client.execute_cli_command(["compute", "instances", "list"])
        
        assert "Failed to parse command output as JSON" in str(exc.value)
