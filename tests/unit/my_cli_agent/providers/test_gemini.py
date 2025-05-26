"""Unit tests for Gemini provider."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import google.generativeai as genai
from my_cli_agent.providers.gemini import GeminiProvider

class MockChatSession:
    def __init__(self, response_text="Test response"):
        self.send_message_async = AsyncMock()
        self.send_message_async.return_value.text = response_text
        self.history = []

class TestGeminiProvider:
    @pytest.fixture
    def mock_genai(self):
        with patch('my_cli_agent.providers.gemini.genai') as mock:
            mock.configure = MagicMock()
            mock.GenerativeModel.return_value.start_chat.return_value = MockChatSession()
            yield mock

    @pytest.fixture
    def provider(self, mock_genai):
        provider = GeminiProvider()
        # Skip the actual setup in tests
        provider._is_setup = True
        return provider

    @pytest.mark.asyncio
    async def test_should_initialize_provider(self, provider):
        """Test provider initialization."""
        assert provider is not None
        assert hasattr(provider, 'model_id')
        assert provider.model_id == "gemini-2.0-flash-thinking-exp-01-21"  # Default model ID
        assert hasattr(provider, 'generation_config')
        assert hasattr(provider, 'safety_settings')

    @pytest.mark.asyncio
    async def test_should_send_message(self, provider, mock_genai):
        """Test sending a message to Gemini."""
        message = "Test message"
        response = await provider.send_message(message)
        assert response == "Test response"
        
        # Verify the chat session was used correctly
        mock_genai.GenerativeModel.return_value.start_chat.assert_called_once()
        provider.chat_session.send_message_async.assert_awaited_once_with(content=message)

    @pytest.mark.asyncio
    async def test_should_handle_api_error(self, provider, mock_genai):
        """Test handling API errors."""
        # Setup the mock to raise an exception
        mock_session = MockChatSession()
        mock_session.send_message_async.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value.start_chat.return_value = mock_session
        
        with pytest.raises(Exception) as exc_info:
            await provider.send_message("Test message")
        assert "API Error" in str(exc_info.value)
        
    @pytest.mark.asyncio
    async def test_should_maintain_conversation(self, provider, mock_genai):
        """Test that conversation history is maintained."""
        # First message
        response1 = await provider.send_message("First message")
        assert response1 == "Test response"
        
        # Second message should use the same chat session
        response2 = await provider.send_message("Second message")
        assert response2 == "Test response"
        
        # Verify only one chat session was created
        mock_genai.GenerativeModel.return_value.start_chat.assert_called_once()
        assert provider.chat_session.send_message_async.await_count == 2
