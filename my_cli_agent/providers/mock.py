"""Mock provider for testing without API keys."""

from typing import List, Dict


class MockProvider:
    """A mock provider for testing when no API keys are available."""
    
    def __init__(self):
        """Initialize the mock provider."""
        self.model_id = "mock-model"
    
    def generate_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Generate a mock response for testing."""
        return f"This is a mock response to: {prompt}\n\nReal functionality requires configuring API keys for OpenAI, Gemini, or Anthropic."
    
    def stream_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Stream a mock response for testing."""
        response = self.generate_response(prompt, conversation)
        print(response)
        return response
