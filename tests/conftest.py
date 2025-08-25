"""Pytest configuration file for defining shared fixtures."""

import sys
import pytest
import types
from unittest.mock import MagicMock


class MockState:
    """A mock object to represent an Enum member with a .name attribute."""

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        # Make comparison work by value, not by identity
        return isinstance(other, self.__class__) and self.name == other.name


class MockServiceStateEnum:
    """A mock class to represent the Service.State enum."""

    ENABLED = MockState("ENABLED")
    DISABLED = MockState("DISABLED")


def create_mock_package(name):
    """Creates a fake module that looks like a package to the import system."""
    mod = types.ModuleType(name)
    mod.__path__ = [f'/mock/{name.replace(".", "/")}'] # The path is critical
    return mod

def pytest_configure(config):
    """
    Mocks the entire Google Cloud package using a full fake package structure.
    This runs before test collection and uses the `__path__` attribute to ensure
    the import system treats our mocks as real packages, resolving the errors.
    """
    # Create the entire fake package structure
    google = create_mock_package('google')
    google.cloud = create_mock_package('google.cloud')
    google.auth = create_mock_package('google.auth')
    google.api_core = create_mock_package('google.api_core')
    google.api_core.exceptions = create_mock_package('google.api_core.exceptions')
    google.cloud.serviceusage_v1 = create_mock_package('google.cloud.serviceusage_v1')
    google.cloud.serviceusage_v1.types = create_mock_package('google.cloud.serviceusage_v1.types')
    google.cloud.resourcemanager_v3 = create_mock_package('google.cloud.resourcemanager_v3')
    google.cloud.compute_v1 = create_mock_package('google.cloud.compute_v1')
    google.adk = create_mock_package('google.adk')
    google.adk.agents = create_mock_package('google.adk.agents')

    # --- Configure the mock modules with MagicMock attributes ---

    google.auth.default = MagicMock(return_value=(MagicMock(), 'test-project-from-auth'))
    google.adk.agents.Agent = MagicMock()
    google.api_core.operation = create_mock_package('google.api_core.operation')
    # Provide a concrete Operation type so tests can use it in spec=
    class _Operation:
        def result(self, *args, **kwargs):
            return None
    google.api_core.operation.Operation = _Operation

    google.cloud.serviceusage_v1.ServiceUsageClient = MagicMock()
    google.cloud.resourcemanager_v3.ProjectsClient = MagicMock()
    google.cloud.compute_v1.InstancesClient = MagicMock()
    google.cloud.compute_v1.NetworksClient = MagicMock()
    google.cloud.compute_v1.SubnetworksClient = MagicMock()
    google.cloud.compute_v1.FirewallsClient = MagicMock()

    exceptions = google.api_core.exceptions
    exceptions.NotFound = type('NotFound', (Exception,), {})
    exceptions.RetryError = type('RetryError', (Exception,), {})
    exceptions.GoogleAPICallError = type('GoogleAPICallError', (Exception,), {})
    exceptions.PermissionDenied = type('PermissionDenied', (Exception,), {})
    exceptions.AlreadyExists = type('AlreadyExists', (Exception,), {})
    exceptions.FailedPrecondition = type('FailedPrecondition', (Exception,), {})

    google.cloud.serviceusage_v1.types.Service = MagicMock()
    google.cloud.serviceusage_v1.types.Service.State = MockServiceStateEnum

    # --- Update sys.modules with the entire mock package structure ---
    modules_to_patch = {
        'google': google,
        'google.cloud': google.cloud,
        'google.auth': google.auth,
        'google.api_core': google.api_core,
        'google.api_core.exceptions': google.api_core.exceptions,
        'google.cloud.serviceusage_v1': google.cloud.serviceusage_v1,
        'google.cloud.serviceusage_v1.types': google.cloud.serviceusage_v1.types,
        'google.cloud.resourcemanager_v3': google.cloud.resourcemanager_v3,
        'google.cloud.compute_v1': google.cloud.compute_v1,
        'google.adk': google.adk,
        'google.adk.agents': google.adk.agents,
    }
    sys.modules.update(modules_to_patch)


@pytest.fixture(autouse=True)
def reset_gcp_mocks():
    """Resets the state of the globally mocked GCP clients before each test."""
    from google.cloud import serviceusage_v1, resourcemanager_v3, compute_v1

    clients = [
        serviceusage_v1.ServiceUsageClient,
        resourcemanager_v3.ProjectsClient,
        compute_v1.InstancesClient,
        compute_v1.NetworksClient,
        compute_v1.SubnetworksClient,
        compute_v1.FirewallsClient,
    ]
    for client in clients:
        client.reset_mock()
        client.return_value.reset_mock()


@pytest.fixture(autouse=True)
def mock_sleep(mocker):
    """Patch time.sleep to speed up tests with polling loops."""
    mocker.patch('time.sleep', return_value=None)
