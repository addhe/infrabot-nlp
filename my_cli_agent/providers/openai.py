import os
from typing import Dict, Any, List, Optional
from openai import OpenAI, AsyncOpenAI
from .base import BaseProvider

class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.client: Optional[AsyncOpenAI] = None
        self.conversation_history: List[Dict[str, str]] = []
        
    async def setup(self):
        """Initialize the OpenAI provider with API key and client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def send_message(self, message: str, conversation_id: Optional[str] = None, **kwargs) -> str:
        """
        Send a message to the OpenAI model and return the response.
        
        Args:
            message: The message to send to the model
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            The model's response as a string
        """
        if not self.client:
            await self.setup()
            
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048)
            )
            
            # Get the assistant's response
            assistant_message = response.choices[0].message.content
            
            # Add assistant's response to conversation history
            if assistant_message:
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message or ""
            
        except Exception as e:
            # Remove the last user message if there was an error
            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()
            raise
        
    async def cleanup(self):
        """Clean up any resources used by the provider."""
        self.conversation_history = []
        self.client = None