from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProvider(ABC):
    """Base class for AI providers."""
    
    @abstractmethod
    def setup(self):
        """Setup the provider with necessary credentials."""
        pass
        
    @abstractmethod
    def chat(self, prompt: str, **kwargs) -> str:
        """Send a chat message and get response."""
        pass
        
    @abstractmethod
    def cleanup(self):
        """Cleanup resources."""
        pass