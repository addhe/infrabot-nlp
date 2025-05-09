from abc import ABC, abstractmethod
import os
import google.generativeai as genai
import openai
from anthropic import Anthropic

class BaseModel(ABC):
    @abstractmethod
    def setup(self):
        pass
    
    @abstractmethod
    def chat(self, prompt: str) -> str:
        pass

class GeminiModel(BaseModel):
    def __init__(self):
        self.model = None
        self.chat_session = None
        self.model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash-thinking-exp-01-21")
        self.generation_config = {
            "temperature": 0.9,
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
    
    def setup(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model_id,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        self.chat_session = self.model.start_chat()
    
    def chat(self, prompt: str) -> str:
        response = self.chat_session.send_message(content=prompt)
        return response.text

class OpenAIModel(BaseModel):
    def __init__(self):
        self.model = None
        self.model_id = os.getenv("OPENAI_MODEL_ID", "gpt-4-turbo-preview")
    
    def setup(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")
        openai.api_key = api_key
        
    def chat(self, prompt: str) -> str:
        response = openai.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=2048
        )
        return response.choices[0].message.content

class ClaudeModel(BaseModel):
    def __init__(self):
        self.client = None
        self.model_id = os.getenv("CLAUDE_MODEL_ID", "claude-3-opus-20240229")
    
    def setup(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY environment variable.")
        self.client = Anthropic(api_key=api_key)
        
    def chat(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model_id,
            max_tokens=2048,
            temperature=0.9,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text