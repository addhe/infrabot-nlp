from abc import ABC, abstractmethod
from typing import Optional, Union, Dict

class BaseProvider(ABC):
    """Base class for AI model providers."""

    @abstractmethod
    async def send_message(self, message: str, conversation_id: Optional[str] = None) -> Union[str, Dict[str, str]]:
        """
        Send a message to the AI model and get its response.

        Args:
            message: The message to send to the model
            conversation_id: Optional ID to maintain conversation context

        Returns:
            The model's response as a string or dictionary with response details
        """
        raise NotImplementedError("Subclasses must implement send_message method")