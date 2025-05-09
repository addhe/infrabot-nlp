import os
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
        self.chat = None
        
    def setup(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable.")
        genai.configure(api_key=api_key)
        
    def chat(self, prompt: str, **kwargs) -> str:
        model = genai.GenerativeModel(
            model_name=self.model_id,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        chat = model.start_chat()
        response = chat.send_message(content=prompt)
        return response.text
        
    def cleanup(self):
        pass  # No specific cleanup needed for Gemini