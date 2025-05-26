"""Unit tests for ADK agent implementation."""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from adk_cli_agent.agent import root_agent
from adk_cli_agent.tools import gcp_tools, time_tools, command_tools

@pytest.fixture
def mock_adk_agent():
    with patch('google.adk.agents.Agent') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance

def test_agent_initialization(mock_adk_agent):
    """Test ADK agent initialization with basic tools."""
    tools = [time_tools.get_current_time, command_tools.execute_command]
    assert root_agent is not None
    assert len(root_agent.tools) >= 2  # Should have at least the basic tools

def test_agent_gcp_tools_availability():
    """Test GCP tools availability based on dependencies."""
    if gcp_tools.HAS_GCP_TOOLS_FLAG:
        assert len(root_agent.tools) >= 4  # Should include GCP tools
    else:
        assert len(root_agent.tools) >= 2  # Should only have basic tools

@pytest.mark.asyncio
async def test_agent_has_required_attributes(mock_adk_agent):
    """Test that the agent has the required attributes and methods."""
    # Check that the agent has the expected attributes
    assert hasattr(root_agent, 'name')
    assert hasattr(root_agent, 'description')
    assert hasattr(root_agent, 'tools')
    assert isinstance(root_agent.name, str)
    assert isinstance(root_agent.description, str)
    assert isinstance(root_agent.tools, list)
    
    # Check that the agent has the expected methods
    assert hasattr(root_agent, 'run_async')
    assert callable(getattr(root_agent, 'run_async', None))
