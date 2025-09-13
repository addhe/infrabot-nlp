import os
from typing import List, Dict
import google.generativeai as genai

class GeminiProvider:
    """Provider for Google's Gemini models, refactored for backend use."""

    def __init__(self, model_id: str = None):
        self.model_id = model_id or os.getenv("GEMINI_MODEL_ID", "gemini-pro")
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        self._model = None

    def setup(self):
        """Initializes the Gemini model with the API key."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable.")
        genai.configure(api_key=api_key)
        
        self._model = genai.GenerativeModel(
            model_name=self.model_id,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

    def generate_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """
        Generates a non-streamed response from the Gemini model.

        Args:
            prompt: The user's prompt.
            conversation: The history of the conversation (currently unused in this stateless setup).

        Returns:
            The model's response as a string.
        """
        if not self._model:
            raise RuntimeError("Provider has not been set up. Call setup() before generating a response.")
        
        # For stateless tool selection, we don't need a long history.
        # For conversational fallback, a more complex history management would be needed.
        response = self._model.generate_content(prompt)
        return response.text
