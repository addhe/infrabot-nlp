import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from .base import BaseProvider

class GeminiProvider(BaseProvider):
    def __init__(self):
        self.model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash-thinking-exp-01-21")
        self.generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        self.chat_session = None
        self._is_setup = False
        
    async def setup(self):
        """Initialize the Gemini provider with API key."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable.")
        genai.configure(api_key=api_key)
        self._is_setup = True
        
    async def send_message(self, message: str, conversation_id: Optional[str] = None, **kwargs) -> str:
        """
        Send a message to the Gemini model and return the response.
        
        Args:
            message: The message to send to the model
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            The model's response as a string
        """
        if not self._is_setup:
            await self.setup()
            
        model = genai.GenerativeModel(
            model_name=self.model_id,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        if self.chat_session is None:
            self.chat_session = model.start_chat()
            
        response = await self.chat_session.send_message_async(content=message)
        return response.text
        
    async def cleanup(self):
        """Clean up any resources used by the provider."""
        self.chat_session = None
        self._is_setup = False