"""Unit tests for base provider functionality."""
import pytest
from typing import Optional, Union, Dict
from my_cli_agent.providers.base import BaseProvider

class TestProvider(BaseProvider):
    """Test implementation of BaseProvider."""
    async def send_message(self, message: str, conversation_id: Optional[str] = None) -> Union[str, Dict[str, str]]:
        return f"Test response to: {message}"

class TestBaseProvider:
    @pytest.fixture
    def provider(self):
        return TestProvider()

    def test_should_create_provider_instance(self):
        """Test provider instance creation."""
        provider = TestProvider()
        assert isinstance(provider, BaseProvider)

    @pytest.mark.asyncio
    async def test_should_send_message(self, provider):
        """Test basic message sending."""
        message = "Hello"
        response = await provider.send_message(message)
        assert response == "Test response to: Hello"

    @pytest.mark.asyncio
    async def test_should_handle_conversation_id(self, provider):
        """Test message sending with conversation ID."""
        message = "Hello"
        conv_id = "test-conv-1"
        response = await provider.send_message(message, conversation_id=conv_id)
        assert response == "Test response to: Hello"

    @pytest.mark.asyncio
    async def test_should_raise_not_implemented(self):
        """Test TypeError when trying to instantiate abstract base class."""
        with pytest.raises(TypeError) as exc_info:
            BaseProvider()
        assert "Can't instantiate abstract class" in str(exc_info.value)
        assert "send_message" in str(exc_info.value)
