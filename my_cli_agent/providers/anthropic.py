import os
from anthropic import Anthropic
from .base import BaseProvider

class AnthropicProvider(BaseProvider):
    def __init__(self):
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.client = None
        
    def setup(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY environment variable.")
        self.client = Anthropic(api_key=api_key)
        
    def chat(self, prompt: str, **kwargs) -> str:
        if not self.client:
            self.setup()
            
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
        
    def cleanup(self):
        pass  # No specific cleanup needed for Anthropic