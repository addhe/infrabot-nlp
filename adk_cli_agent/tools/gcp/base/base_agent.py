"""Base agent class for GCP infrastructure management with ADK patterns."""

from typing import Dict, List, Optional, Callable, Any
from abc import ABC, abstractmethod
import logging

# Import ADK components
try:
    from google.adk.agents import Agent
    from google.adk.tools.tool_context import ToolContext
    HAS_ADK = True
except ImportError:
    # Fallback for development/testing without full ADK
    HAS_ADK = False
    Agent = object  # type: ignore
    ToolContext = object  # type: ignore


logger = logging.getLogger(__name__)


class BaseGCPAgent(ABC):
    """Base class for GCP agents following ADK patterns."""
    
    def __init__(
        self,
        name: str,
        model: str = "gpt-4o-mini",
        description: str = "",
        instruction: str = "",
        tools: Optional[List[Callable]] = None,
        before_model_callback: Optional[Callable] = None,
        before_tool_callback: Optional[Callable] = None,
    ):
        """Initialize the base GCP agent.
        
        Args:
            name: Agent name for identification
            model: Model to use (supports LiteLLM format)
            description: Brief description of agent capabilities
            instruction: System instruction for the agent
            tools: List of tool functions to register
            before_model_callback: Safety callback before model calls
            before_tool_callback: Safety callback before tool calls
        """
        self.name = name
        self.model = model
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        self.before_model_callback = before_model_callback
        self.before_tool_callback = before_tool_callback
        
        # Create the ADK agent if available
        if HAS_ADK:
            self.agent = Agent(
                name=self.name,
                model=self.model,
                description=self.description,
                instruction=self.instruction,
                tools=self.tools,
            )
            
            # Register callbacks if provided
            if self.before_model_callback:
                self.agent.before_model_callback = self.before_model_callback
            if self.before_tool_callback:
                self.agent.before_tool_callback = self.before_tool_callback
        else:
            # Simple fallback for development without ADK
            self.agent = None
    
    @abstractmethod
    def get_delegation_logic(self) -> Dict[str, Any]:
        """Return delegation logic for multi-agent scenarios.
        
        Returns:
            Dictionary containing delegation rules and target agents
        """
        pass
    
    def add_tool(self, tool_func: Callable) -> None:
        """Add a tool to the agent.
        
        Args:
            tool_func: Tool function to add
        """
        self.tools.append(tool_func)
        # Re-register tools with the agent if ADK is available
        if HAS_ADK and self.agent:
            self.agent = Agent(
                name=self.name,
                model=self.model,
                description=self.description,
                instruction=self.instruction,
                tools=self.tools,
            )
    
    def add_safety_callback(
        self, 
        callback_type: str, 
        callback_func: Callable
    ) -> None:
        """Add safety callbacks to the agent.
        
        Args:
            callback_type: 'before_model' or 'before_tool'
            callback_func: Callback function
        """
        if callback_type == "before_model":
            self.before_model_callback = callback_func
            self.agent.before_model_callback = callback_func
        elif callback_type == "before_tool":
            self.before_tool_callback = callback_func
            self.agent.before_tool_callback = callback_func
        else:
            raise ValueError(f"Unknown callback type: {callback_type}")
    
    async def run(
        self, 
        user_prompt: str, 
        context: Optional[Any] = None
    ) -> Any:
        """Run the agent with a user prompt.
        
        Args:
            user_prompt: User's request
            context: Tool context for state access
            
        Returns:
            Agent response
        """
        try:
            logger.info(f"Running {self.name} agent with prompt: {user_prompt}")
            
            # Run the agent
            result = await self.agent.run(user_prompt, deps=context)
            
            logger.info(f"{self.name} agent completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name} agent: {str(e)}")
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information.
        
        Returns:
            Dictionary with agent details
        """
        return {
            "name": self.name,
            "model": self.model,
            "description": self.description,
            "instruction": self.instruction,
            "tool_count": len(self.tools),
            "has_model_callback": self.before_model_callback is not None,
            "has_tool_callback": self.before_tool_callback is not None,
        }


class SpecializedGCPAgent(BaseGCPAgent):
    """Base class for specialized GCP agents (compute, networking, etc.)."""
    
    def __init__(
        self,
        name: str,
        specialization: str,
        model: str = "gpt-4o-mini",
        description: str = "",
        instruction: str = "",
        tools: Optional[List[Callable]] = None,
        **kwargs
    ):
        """Initialize specialized GCP agent.
        
        Args:
            name: Agent name
            specialization: Area of specialization (compute, networking, etc.)
            model: Model to use
            description: Agent description
            instruction: System instruction
            tools: Tool functions
            **kwargs: Additional arguments for base class
        """
        self.specialization = specialization
        
        # Enhance instruction with specialization context
        enhanced_instruction = f"""
{instruction}

You are a specialized GCP {specialization} agent. You have deep expertise in Google Cloud {specialization} services and best practices.

Key responsibilities:
- Provide expert guidance on GCP {specialization} services
- Execute {specialization}-related operations safely and efficiently
- Follow GCP best practices and security guidelines
- Maintain state awareness through session context
- Escalate complex multi-service requests to the root agent

Always check the current session state before making recommendations or executing operations.
"""
        
        super().__init__(
            name=name,
            model=model,
            description=description,
            instruction=enhanced_instruction.strip(),
            tools=tools,
            **kwargs
        )
    
    def get_delegation_logic(self) -> Dict[str, Any]:
        """Return delegation logic for specialized agents.
        
        Returns:
            Delegation rules specific to this specialization
        """
        return {
            "can_handle": [self.specialization],
            "escalate_to_root": [
                "multi_service_operations",
                "cross_specialization_requests",
                "complex_architecture_decisions"
            ],
            "specialization": self.specialization
        }