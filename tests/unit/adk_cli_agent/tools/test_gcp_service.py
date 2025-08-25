import pytest
import types

# Import the mocked libraries and exceptions directly. These are available thanks
# to the session-wide mocking in conftest.py.
from google.cloud import serviceusage_v1
from google.api_core import exceptions

# Import the functions and classes to be tested
from adk_cli_agent.tools.gcp_service import (
    is_service_enabled,
    enable_service,
    enable_gcp_service_tool,
    list_gcp_services_tool,
    COMMON_SERVICES
)
from adk_cli_agent.utils.tool_result import ToolResult

# --- Constants ---
TEST_PROJECT_ID = 'test-project'
TEST_SERVICE_SHORT = 'compute'
TEST_SERVICE = 'compute.googleapis.com'
SERVICE_NAME_FULL = f'projects/{TEST_PROJECT_ID}/services/{TEST_SERVICE}'

# --- Mock Service Object Factory ---
def create_mock_service(state, name=None, title=None):
    """A helper to create mock service objects for tests."""
    service = types.SimpleNamespace()
    service.state = state
    service.name = name or SERVICE_NAME_FULL
    # Create a nested namespace for the 'config' attribute
    service.config = types.SimpleNamespace(title=title or 'Mock Service Title')
    return service

# --- Test Cases ---

class TestGcpService:
    def test_is_service_enabled_true(self):
        mock_client = serviceusage_v1.ServiceUsageClient.return_value
        mock_client.get_service.return_value = create_mock_service(
            state=serviceusage_v1.types.Service.State.ENABLED
        )

        is_enabled, service_info = is_service_enabled(TEST_PROJECT_ID, TEST_SERVICE)

        assert is_enabled is True
        assert service_info['state'] == 'ENABLED'
        mock_client.get_service.assert_called_once_with(name=SERVICE_NAME_FULL)

    def test_is_service_enabled_false_due_to_state(self):
        mock_client = serviceusage_v1.ServiceUsageClient.return_value
        mock_client.get_service.return_value = create_mock_service(
            state=serviceusage_v1.types.Service.State.DISABLED
        )

        is_enabled, service_info = is_service_enabled(TEST_PROJECT_ID, TEST_SERVICE)

        assert is_enabled is False
        assert service_info['state'] == 'DISABLED'
        mock_client.get_service.assert_called_once_with(name=SERVICE_NAME_FULL)

    def test_is_service_enabled_false_due_to_notfound(self):
        mock_client = serviceusage_v1.ServiceUsageClient.return_value
        mock_client.get_service.side_effect = exceptions.NotFound("Service not found")

        is_enabled, service_info = is_service_enabled(TEST_PROJECT_ID, TEST_SERVICE)

        assert is_enabled is False
        assert service_info is None
        mock_client.get_service.assert_called_once_with(name=SERVICE_NAME_FULL)

    def test_enable_service_success(self):
        mock_client = serviceusage_v1.ServiceUsageClient.return_value
        # The operation.result() should return the final service object
        mock_client.enable_service.return_value.result.return_value = create_mock_service(
            state=serviceusage_v1.types.Service.State.ENABLED
        )

        success, message = enable_service(TEST_PROJECT_ID, TEST_SERVICE)

        assert success is True
        assert "Successfully enabled" in message
        mock_client.enable_service.assert_called_once()

    def test_enable_service_timeout(self):
        mock_client = serviceusage_v1.ServiceUsageClient.return_value
        mock_client.enable_service.return_value.result.side_effect = exceptions.RetryError("Timeout")

        success, message = enable_service(TEST_PROJECT_ID, TEST_SERVICE, timeout=0.1)

        assert success is False
        assert "Timeout enabling service" in message

    def test_enable_gcp_service_tool_success_when_not_enabled(self):
        mock_client = serviceusage_v1.ServiceUsageClient.return_value
        # Simulate the polling behavior
        mock_client.get_service.side_effect = [
            create_mock_service(state=serviceusage_v1.types.Service.State.DISABLED), # Check before enabling
            create_mock_service(state=serviceusage_v1.types.Service.State.ENABLED),  # Check after enabling
        ]

        result = enable_gcp_service_tool(TEST_PROJECT_ID, TEST_SERVICE_SHORT)

        assert result.success is True
        assert "Successfully enabled" in result.message
        assert mock_client.enable_service.called
        assert mock_client.get_service.call_count == 2

    def test_enable_gcp_service_tool_already_enabled(self):
        mock_client = serviceusage_v1.ServiceUsageClient.return_value
        mock_client.get_service.return_value = create_mock_service(
            state=serviceusage_v1.types.Service.State.ENABLED
        )

        result = enable_gcp_service_tool(TEST_PROJECT_ID, TEST_SERVICE_SHORT)

        assert result.success is True
        assert "already enabled" in result.message
        mock_client.get_service.assert_called_once()

    def test_list_gcp_services_tool_success(self):
        mock_client = serviceusage_v1.ServiceUsageClient.return_value
        mock_client.list_services.return_value = [
            create_mock_service(state=serviceusage_v1.types.Service.State.ENABLED, title="Compute Engine API"),
            create_mock_service(state=serviceusage_v1.types.Service.State.ENABLED, title="Cloud Storage API")
        ]

        result = list_gcp_services_tool(TEST_PROJECT_ID)

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]['title'] == "Compute Engine API"

    def test_common_services_constant(self):
        assert 'compute' in COMMON_SERVICES
        assert COMMON_SERVICES['compute'] == 'compute.googleapis.com'
