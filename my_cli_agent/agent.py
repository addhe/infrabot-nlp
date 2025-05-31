import datetime
import os
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import atexit
import grpc
import sys
import json

# Import AI providers conditionally
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Import tools
from .tools.time_tools import get_current_time
from .tools.command_tools import execute_command
from .tools.gcp_tools import list_gcp_projects, create_gcp_project, delete_gcp_project, HAS_GCP_TOOLS

# Import model providers
from .providers.openai import OpenAIProvider
from .providers.gemini import GeminiProvider
from .providers.anthropic import AnthropicProvider

# --- Type Definitions ---
@dataclass
class ChatHistory:
    """Represents a chat message in the conversation history."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float

@dataclass
class ToolResult:
    """Represents the result of a tool execution."""
    success: bool
    result: Any = None
    error_message: Optional[str] = None

class LLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        
    def setup(self):
        """Set up the provider with credentials."""
        raise NotImplementedError("Subclasses must implement setup()")
        
    def generate_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Generate a response to the given prompt."""
        raise NotImplementedError("Subclasses must implement generate_response()")
        
    def stream_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Stream a response to the given prompt and return the full response."""
        raise NotImplementedError("Subclasses must implement stream_response()")

class GeminiProvider(LLMProvider):
    """Provider for Google's Gemini models."""
    
    def __init__(self, model_id: str = None):
        super().__init__(model_id or os.getenv("GEMINI_MODEL_ID", "learnlm-2.0-flash-experimental"))
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
        
    def setup(self):
        """Set up Gemini with API key."""
        if not HAS_GEMINI:
            raise ValueError("Gemini SDK not installed. Please install with 'pip install google-generativeai'")
            
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable.")
        genai.configure(api_key=api_key)
        
    def generate_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Generate a response using Gemini."""
        model = genai.GenerativeModel(
            model_name=self.model_id,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        # Convert conversation to Gemini format
        gemini_messages = []
        for msg in conversation:
            if msg["role"] in ["user", "assistant"]:
                gemini_messages.append({"role": msg["role"], "parts": [msg["content"]]})
        
        chat = model.start_chat(history=gemini_messages)
        response = chat.send_message(prompt)
        return response.text
        
    def stream_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Stream a response using Gemini."""
        model = genai.GenerativeModel(
            model_name=self.model_id,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        # Convert conversation to Gemini format
        gemini_messages = []
        for msg in conversation:
            if msg["role"] in ["user", "assistant"]:
                gemini_messages.append({"role": msg["role"], "parts": [msg["content"]]})
        
        chat = model.start_chat(history=gemini_messages)
        response_stream = chat.send_message(prompt, stream=True)
        
        full_response = ""
        print()
        for chunk in response_stream:
            if hasattr(chunk, 'text') and chunk.text:
                print(chunk.text, end="", flush=True)
                full_response += chunk.text
        print()
        
        return full_response

class OpenAIProvider(LLMProvider):
    """Provider for OpenAI's models."""
    
    def __init__(self, model_id: str = None):
        super().__init__(model_id or os.getenv("OPENAI_MODEL_ID", "gpt-4-turbo-preview"))
        
    def setup(self):
        """Set up OpenAI with API key."""
        if not HAS_OPENAI:
            raise ValueError("OpenAI SDK not installed. Please install with 'pip install openai'")
            
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")
        openai.api_key = api_key
        
    def generate_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Generate a response using OpenAI."""
        # Create a copy of the conversation and add the new prompt
        messages = conversation.copy()
        messages.append({"role": "user", "content": prompt})
        
        response = openai.chat.completions.create(
            model=self.model_id,
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    def stream_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Stream a response using OpenAI."""
        # Create a copy of the conversation and add the new prompt
        messages = conversation.copy()
        messages.append({"role": "user", "content": prompt})
        
        response = openai.chat.completions.create(
            model=self.model_id,
            messages=messages,
            temperature=0.7,
            stream=True
        )
        
        full_response = ""
        print()
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        print()
        
        return full_response

class AnthropicProvider(LLMProvider):
    """Provider for Anthropic's Claude models."""
    
    def __init__(self, model_id: str = None):
        super().__init__(model_id or os.getenv("CLAUDE_MODEL_ID", "claude-3-opus-20240229"))
        
    def setup(self):
        """Set up Anthropic with API key."""
        if not HAS_ANTHROPIC:
            raise ValueError("Anthropic SDK not installed. Please install with 'pip install anthropic'")
            
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY environment variable.")
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def generate_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Generate a response using Anthropic Claude."""
        # Extract system message if present
        system_message = "You are a helpful assistant."
        for msg in conversation:
            if msg["role"] == "system":
                system_message = msg["content"]
                break
        
        # Convert conversation to Anthropic format
        anthropic_messages = []
        for msg in conversation:
            if msg["role"] in ["user", "assistant"]:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add the new prompt
        anthropic_messages.append({"role": "user", "content": prompt})
        
        response = self.client.messages.create(
            model=self.model_id,
            system=system_message,
            messages=anthropic_messages,
            max_tokens=2000
        )
        
        return response.content[0].text
        
    def stream_response(self, prompt: str, conversation: List[Dict[str, str]]) -> str:
        """Stream a response using Anthropic Claude."""
        # Extract system message if present
        system_message = "You are a helpful assistant."
        for msg in conversation:
            if msg["role"] == "system":
                system_message = msg["content"]
                break
        
        # Convert conversation to Anthropic format
        anthropic_messages = []
        for msg in conversation:
            if msg["role"] in ["user", "assistant"]:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add the new prompt
        anthropic_messages.append({"role": "user", "content": prompt})
        
        response = self.client.messages.create(
            model=self.model_id,
            system=system_message,
            messages=anthropic_messages,
            max_tokens=2000,
            stream=True
        )
        
        full_response = ""
        print()
        for chunk in response:
            if chunk.delta.text:
                content = chunk.delta.text
                print(content, end="", flush=True)
                full_response += content
        print()
        
        return full_response

class Agent:
    """Main agent class for handling commands and interactions with AI models."""
    
    def __init__(self, model_provider):
        """Initialize agent with a model provider."""
        self.model_provider = model_provider
        self.tool_modules = {}
        self._load_tools()
        
    @property
    def has_gcp_tools(self) -> bool:
        """Check if GCP tools are available."""
        try:
            from my_cli_agent.tools.gcp_tools import HAS_GCP_TOOLS
            return HAS_GCP_TOOLS
        except ImportError:
            return False
    
    def _load_tools(self):
        """Load available tool modules."""
        from my_cli_agent.tools import command_tools, time_tools, gcp_tools
        self.tool_modules = {
            'command': command_tools,
            'time': time_tools,
            'gcp': gcp_tools
        }
    
    def execute_command(self, command: str) -> ToolResult:
        """
        Execute a shell command using the command tools.
        
        Args:
            command: The shell command to execute
            
        Returns:
            ToolResult containing the command output or error
        """
        from my_cli_agent.tools.command_tools import execute_command
        return execute_command(command)
    
    def get_time(self, city: str) -> ToolResult:
        """
        Get the current time for a specific city.
        
        Args:
            city: The city to get the time for
            
        Returns:
            ToolResult containing the current time or error
        """
        from my_cli_agent.tools.time_tools import get_current_time
        return get_current_time(city)
    
    def list_gcp_projects(self, environment: str = None) -> ToolResult:
        """
        List GCP projects for the specified environment.
        
        Args:
            environment: Optional environment filter (e.g., 'dev', 'prod')
            
        Returns:
            ToolResult containing the list of projects or error
        """
        from my_cli_agent.tools.gcp_tools import list_gcp_projects
        return list_gcp_projects(environment)
        
    def create_gcp_project(self, project_id: str, name: str = None) -> ToolResult:
        """
        Create a new GCP project.
        
        Args:
            project_id: The project ID to create (can be in format 'id,name,org')
            name: The display name for the project (defaults to project_id)
            
        Returns:
            ToolResult containing the result of the operation or error information
        """
        from my_cli_agent.tools.gcp_tools import create_gcp_project
        return create_gcp_project(project_id, name)
        
    def cleanup(self):
        """Clean up any resources before exiting."""
        pass
    
    def process_command(self, command: str) -> str:
        """
        Process a user command through the AI model and execute any required tools.
        
        Args:
            command: The user's command or query
            
        Returns:
            The final response to show to the user
        """
        try:
            # First check for direct GCP commands in multiple languages
            if self.has_gcp_tools:
                command_lower = command.lower()
                
                # Match for GCP commands in different languages (English and Indonesian)
                gcp_project_keywords = ["list projects", "show projects", "get projects", "gcp projects", 
                                       "projects", "project", "gcp", "semua project", "semua gcp",
                                       "list semua", "lihat semua", "tampilkan semua", "berapa projects", 
                                       "projects yang saya", "milik", "miliki"]
                
                if any(keyword in command_lower for keyword in gcp_project_keywords):
                    print(f"Executing GCP tool command: {command}")
                    from my_cli_agent.tools.gcp_tools import execute_command as gcp_execute
                    tool_result = gcp_execute(command)
                    if tool_result.success:
                        return f"{tool_result.result}"
                    else:
                        error_msg = tool_result.error_message or "Unknown error occurred"
                        return f"Tool execution failed: {error_msg}"
            
            # Get AI model's response if no direct command match
            response = self.model_provider.generate_response(command, [{"role": "user", "content": command}])
            
            # Check if we need to execute any tools based on response
            for tool_name, tool_module in self.tool_modules.items():
                if tool_name in response.lower():
                    # Execute relevant tool function
                    try:
                        tool_result = tool_module.execute_command(command)
                        if tool_result.success:
                            return f"{tool_result.result}"
                        else:
                            error_msg = tool_result.error_message or "Unknown error occurred"
                            return f"Tool execution failed: {error_msg}"
                    except Exception as tool_error:
                        return f"Error executing {tool_name} command: {str(tool_error)}"
            
            return response
            
        except Exception as e:
            raise Exception(f"Error processing command: {str(e)}")

def main():
    """Main function to run the CLI interface."""
    print("Starting agent...")
    try:
        # Determine which provider to use based on available APIs and environment variables
        provider = None
        
        # Try OpenAI first if available and configured
        if HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
            provider = OpenAIProvider()
        # Try Gemini next if available and configured
        elif HAS_GEMINI and os.getenv("GOOGLE_API_KEY"):
            provider = GeminiProvider()
        # Try Anthropic last if available and configured
        elif HAS_ANTHROPIC and os.getenv("ANTHROPIC_API_KEY"):
            provider = AnthropicProvider()
            
        if provider is None:
            # Fall back to mock provider if no API keys are configured
            from .providers.mock import MockProvider
            provider = MockProvider()
            print("WARNING: No API keys configured. Using mock provider with limited functionality.")
            
        agent = Agent(provider)
        
        # Create welcome message based on available tools
        available_commands = [
            "- Get current time: Ask about time in supported cities (New York, Paris, Jakarta, Tokyo, London, Sydney)",
            "- Execute commands: Run shell commands (e.g., \"run ls -la\" or \"execute pwd\")"
        ]
        
        # Add GCP projects command if available
        if HAS_GCP_TOOLS:
            available_commands.insert(0, "- List GCP projects: Ask about projects in any environment (dev/stg/prod)")
            available_commands.insert(1, "- Create GCP project: Ask to create a new GCP project with a specific ID and name")
        
        # Get provider name for display
        provider_name = {
            "gemini": "Google Gemini",
            "openai": "OpenAI",
            "anthropic": "Anthropic Claude",
            "mock": "Mock Provider (Demo Mode)"
        }.get(agent.model_provider.__class__.__name__.replace('Provider', '').lower(), 
              agent.model_provider.__class__.__name__)
        
        welcoming_text = f"""
        Welcome to Multi-LLM CLI Agent
        Using provider: {provider_name}
        Using model: {agent.model_provider.model_id}
        Available commands:
        {chr(10).join(available_commands)}
        
        Type 'exit()' to quit
        """
        print(welcoming_text)
        
        while True:
            try:
                user_input = input("\n> ")
                if user_input.lower() == "exit()":
                    print("Shutting down gracefully...")
                    agent.cleanup()
                    sys.exit(0)
                response = agent.process_command(user_input)
                print(f"\n{response}")
            except KeyboardInterrupt:
                print("\nExiting...")
                agent.cleanup()
                sys.exit(0)
            except Exception as e:
                print(f"An error occurred: {e}")
                agent.cleanup()
                sys.exit(1)
    except Exception as e:
        print(f"Error initializing agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
