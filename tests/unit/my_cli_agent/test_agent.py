"""Unit tests for the Direct API Agent implementation."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from my_cli_agent.agent import Agent
from my_cli_agent.tools.base import ToolResult

@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.send_message.return_value = "Test response"
    return provider

class TestDirectAPIAgent:
    @pytest.fixture
    def agent(self, mock_provider):
        return Agent(model_provider=mock_provider)

    def test_should_initialize_with_provider(self, mock_provider):
        """Test agent initialization with a model provider."""
        agent = Agent(model_provider=mock_provider)
        assert agent.model_provider == mock_provider

    def test_should_execute_command(self, agent):
        """Test executing a command through the agent."""
        command = "ls -la"
        result = agent.execute_command(command)
        assert isinstance(result, ToolResult)

    def test_should_get_time(self, agent):
        """Test getting time through the agent."""
        city = "London"
        result = agent.get_time(city)
        assert isinstance(result, ToolResult)

    def test_should_handle_gcp_tools(self, agent):
        """Test GCP tools functionality when available."""
        result = agent.list_gcp_projects("dev")
        assert isinstance(result, ToolResult)

        if agent.has_gcp_tools:
            # Test with just project_id (name will default to project_id)
            result = agent.create_gcp_project("test-project-1")
            assert isinstance(result, ToolResult)
            
            # Test with project_id and name
            result = agent.create_gcp_project("test-project-2", "Test Project")
            assert isinstance(result, ToolResult)

@pytest.mark.asyncio
class TestAsyncMethods:
    @pytest.fixture
    def agent(self, mock_provider):
        return Agent(model_provider=mock_provider)
        
    async def test_should_send_message(self, agent):
        """Test async message sending."""
        message = "Hello, how are you?"
        response = await agent.model_provider.send_message(message)
        assert response == "Test response"
