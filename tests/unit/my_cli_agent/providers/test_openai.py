"""Unit tests for OpenAI provider."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from my_cli_agent.providers.openai import OpenAIProvider

class MockAsyncChatCompletion:
    def __init__(self, content):
        self.choices = [MagicMock()]
        self.choices[0].message.content = content

class MockAsyncClient:
    def __init__(self, content="Test response"):
        self.chat = MagicMock()
        self.chat.completions = MagicMock()
        self.chat.completions.create = AsyncMock(return_value=MockAsyncChatCompletion(content))

class TestOpenAIProvider:
    @pytest.fixture
    def mock_async_openai(self):
        with patch('my_cli_agent.providers.openai.AsyncOpenAI') as mock:
            mock.return_value = MockAsyncClient()
            yield mock

    @pytest.fixture
    def provider(self, mock_async_openai):
        provider = OpenAIProvider()
        provider.client = MockAsyncClient()  # Inject mock client
        return provider

    @pytest.mark.asyncio
    async def test_should_initialize_provider(self, provider):
        """Test provider initialization."""
        assert provider is not None
        assert hasattr(provider, 'model')
        assert provider.model == 'gpt-3.5-turbo'  # Default model

    @pytest.mark.asyncio
    async def test_should_send_message(self, provider):
        """Test sending a message to OpenAI."""
        message = "Test message"
        response = await provider.send_message(message)
        assert response == "Test response"
        
        # Verify the chat completion was called with the right arguments
        provider.client.chat.completions.create.assert_awaited_once()
        call_args = provider.client.chat.completions.create.await_args[1]
        assert call_args['messages'][0]['content'] == message
        assert call_args['model'] == 'gpt-3.5-turbo'

    @pytest.mark.asyncio
    async def test_should_handle_api_error(self, provider):
        """Test handling API errors."""
        # Set up the mock to raise an exception
        provider.client.chat.completions.create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            await provider.send_message("Test message")
        assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_should_maintain_conversation_history(self, provider):
        """Test conversation history management."""
        conv_id = "test-conv"
        
        # First message
        await provider.send_message("Message 1", conversation_id=conv_id)
        # Second message should include the first one in history
        await provider.send_message("Message 2", conversation_id=conv_id)
        
        # Get the arguments from the second call
        call_args = provider.client.chat.completions.create.await_args[1]
        messages = call_args['messages']
        
        # Should have 4 messages in history: [user1, assistant1, user2, assistant2]
        assert len(messages) == 4
        # Verify the structure of the conversation
        assert messages[0]['role'] == 'user' and messages[0]['content'] == "Message 1"
        assert messages[1]['role'] == 'assistant' and messages[1]['content'] == "Test response"
        assert messages[2]['role'] == 'user' and messages[2]['content'] == "Message 2"
        assert messages[3]['role'] == 'assistant' and messages[3]['content'] == "Test response"
