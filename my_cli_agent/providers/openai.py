import os
from openai import OpenAI
from .base import BaseProvider

class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.client = None
        
    def setup(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=api_key)
        
    def chat(self, prompt: str, **kwargs) -> str:
        if not self.client:
            self.setup()
            
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=2048
        )
        return response.choices[0].message.content
        
    def cleanup(self):
        pass  # No specific cleanup needed for OpenAI