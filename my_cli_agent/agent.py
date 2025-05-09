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
    """A conversational agent that can use tools to help answer questions."""
    
    def __init__(self):
        self.history: List[ChatHistory] = []
        self.conversation: List[Dict[str, str]] = [
            {"role": "system", "content": "You are a helpful assistant that can use tools to help answer questions."}
        ]
        
        # Initialize tools dictionary
        self.tools = {
            "get_current_time": get_current_time,
            "execute_command": execute_command
        }
        
        # Add GCP tools if available
        if HAS_GCP_TOOLS:
            self.tools["list_gcp_projects"] = list_gcp_projects
            self.tools["create_gcp_project"] = create_gcp_project
            self.tools["delete_gcp_project"] = delete_gcp_project
        
        # Determine which AI provider to use
        self.provider = self._setup_provider()
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def _setup_provider(self) -> LLMProvider:
        """Set up the appropriate LLM provider based on available API keys."""
        # Check available providers
        providers = []
        
        if HAS_GEMINI and os.getenv("GOOGLE_API_KEY"):
            providers.append(("gemini", GeminiProvider()))
            
        if HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
            providers.append(("openai", OpenAIProvider()))
            
        if HAS_ANTHROPIC and os.getenv("ANTHROPIC_API_KEY"):
            providers.append(("anthropic", AnthropicProvider()))
        
        if not providers:
            # Check which providers are available but missing API keys
            missing_keys = []
            if HAS_GEMINI and not os.getenv("GOOGLE_API_KEY"):
                missing_keys.append("GOOGLE_API_KEY")
            if HAS_OPENAI and not os.getenv("OPENAI_API_KEY"):
                missing_keys.append("OPENAI_API_KEY")
            if HAS_ANTHROPIC and not os.getenv("ANTHROPIC_API_KEY"):
                missing_keys.append("ANTHROPIC_API_KEY")
                
            if missing_keys:
                raise ValueError(f"Missing API key(s): {', '.join(missing_keys)}")
            else:
                raise ValueError("No AI providers available. Please install at least one of: google-generativeai, openai, or anthropic")
        
        # Use the first available provider
        provider_name, provider = providers[0]
        self.provider_name = provider_name
        
        # Set up the provider
        provider.setup()
        
        return provider

    def cleanup(self):
        """Clean up resources before exit."""
        try:
            # Force cleanup of gRPC channels
            for channel in grpc._channel._channel_pool:
                try:
                    channel.close()
                except:
                    pass
            grpc._channel._channel_pool.clear()
        except:
            pass

    def add_to_history(self, role: str, content: str):
        """Add a message to the chat history."""
        self.history.append(ChatHistory(
            role=role,
            content=content,
            timestamp=time.time()
        ))
        
        # Also add to conversation for the LLM
        self.conversation.append({
            "role": role,
            "content": content
        })

    def process_with_tools(self, prompt: str):
        """Process user input and execute appropriate tools based on the content."""
        try:
            # Add user message to history
            self.add_to_history("user", prompt)
            
            # First, check if this is a direct tool request
            tool_result = self._check_direct_tool_request(prompt)
            if tool_result:
                return
            
            # Create a tool selection prompt
            tool_selection_prompt = self._create_tool_selection_prompt(prompt)
            
            # Get a response from the LLM about which tool to use
            tool_response = self.provider.generate_response(tool_selection_prompt, self.conversation)
            
            # Parse the tool response
            if "TOOL:" in tool_response:
                self._handle_tool_response(tool_response)
            else:
                # No tool needed, just have a conversation
                response = self.provider.stream_response(prompt, self.conversation)
                self.add_to_history("assistant", response)
                
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            self.add_to_history("assistant", error_msg)
    
    def _check_direct_tool_request(self, prompt: str) -> bool:
        """Check if the prompt is a direct request to use a specific tool."""
        prompt_lower = prompt.lower()
        
        # Check for time requests
        if any(phrase in prompt_lower for phrase in ["what time", "current time", "time now", "time in"]):
            city = None
            for known_city in ["new york", "paris", "jakarta", "tokyo", "london", "sydney"]:
                if known_city in prompt_lower:
                    city = known_city
                    break
            
            result = get_current_time(city or "")
            self._display_tool_result(result)
            return True
            
        # Check for command execution requests
        if any(phrase in prompt_lower for phrase in ["run command", "execute command", "run the command"]):
            # Try to extract the command
            command = None
            if "`" in prompt:
                # Extract command from backticks
                parts = prompt.split("`")
                if len(parts) >= 3:
                    command = parts[1]
            elif ":" in prompt:
                # Extract command after colon
                command = prompt.split(":", 1)[1].strip()
            
            if command:
                result = execute_command(command)
                self._display_tool_result(result)
                return True
        
        # Check for GCP project deletion requests
        if HAS_GCP_TOOLS and any(phrase in prompt_lower for phrase in [
            "delete gcp", "hapus gcp", "remove gcp", "delete project", "hapus project", 
            "remove project", "delete the project", "hapus proyek", "tolong hapus", "tolong delete"]):
            
            # Try to extract the project ID
            project_id = None
            
            # Look for quoted project ID
            import re
            quoted_match = re.search(r'["\']([\w\-]+)["\']', prompt)
            if quoted_match:
                project_id = quoted_match.group(1)
            else:
                # Look for common project ID patterns
                id_match = re.search(r'\b([\w\-]+(?:-dev|-stg|-prd|-prod))\b', prompt)
                if id_match:
                    project_id = id_match.group(1)
                else:
                    # Look for any word that might be a project ID
                    words = prompt.split()
                    for word in words:
                        if re.match(r'^[\w\-]+$', word) and len(word) > 3 and word not in [
                            "delete", "hapus", "remove", "project", "proyek", "gcp", "the", "tolong"]:
                            project_id = word
                            break
            
            if project_id:
                # Execute the tool
                result = delete_gcp_project(project_id)
                self._display_tool_result(result)
                return True
        
        # Check for GCP project listing requests
        if HAS_GCP_TOOLS and any(phrase in prompt_lower for phrase in [
            "list gcp", "show gcp", "gcp project", "projects", "project list", 
            "tampilkan project", "ada berapa", "berapa banyak", "semua project", 
            "all project", "project apa saja"]):
            
            # Determine environment
            env = "all"  # Default to all projects
            
            # Check for specific environment requests
            if any(env_word in prompt_lower for env_word in ["dev", "development"]):
                env = "dev"
            elif any(env_word in prompt_lower for env_word in ["stg", "staging"]):
                env = "stg"
            elif any(env_word in prompt_lower for env_word in ["prod", "production"]):
                env = "prod"
            elif any(env_word in prompt_lower for env_word in ["other", "misc", "miscellaneous", "non-env"]):
                env = "other"
            elif any(word in prompt_lower for word in ["all", "semua", "every", "any", "all projects", "semua project"]):
                env = "all"
            
            # Execute the tool
            result = list_gcp_projects(env)
            self._display_tool_result(result)
            return True
        
        return False
    
    def _create_tool_selection_prompt(self, prompt: str) -> str:
        """Create a prompt to help the LLM select the appropriate tool."""
        tool_instructions = [
            f"Based on this user request: \"{prompt}\"",
            "If this is a request to view file contents, use execute_command with 'cat' and proper path quoting.",
            "If this is a request to run a command, use execute_command.",
            "If this is a request about time, use get_current_time."
        ]
            
        # Add GCP projects instruction if available
        if HAS_GCP_TOOLS:
            tool_instructions.append("If this is a request about GCP projects, use list_gcp_projects with the environment name (dev/stg/prod).")
            tool_instructions.append("If this is a request to create a GCP project, use create_gcp_project with the project ID and optional project name.")
            tool_instructions.append("If this is a request to delete a GCP project, use delete_gcp_project with the project ID.")
        
        tool_instructions.extend([
            "If none of the above tools are needed, respond with 'NO_TOOL_NEEDED' and I will handle the request directly.",
            "Respond in the following format:",
            "TOOL: <tool_name>",
            "ARGS: <tool_arguments>"
        ])
        
        return "\n".join(tool_instructions)
    
    def _handle_tool_response(self, tool_response: str):
        """Handle a tool response from the LLM."""
        try:
            lines = tool_response.split("\n")
            tool_line = next((line for line in lines if line.startswith("TOOL:")), None)
            args_line = next((line for line in lines if line.startswith("ARGS:")), None)
            
            if not tool_line or not args_line:
                print("\nError: Invalid tool response format.")
                return
            
            tool_name = tool_line.replace("TOOL:", "").strip()
            tool_arg = args_line.replace("ARGS:", "").strip()

            # Clean up the argument
            if ":" in tool_arg:
                tool_arg = tool_arg.split(":")[-1].strip()
            
            # Clean up arguments for list_gcp_projects
            if tool_name == "list_gcp_projects":
                # Extract just the environment name (dev, stg, prod)
                # First remove parameter prefix if present
                if "=" in tool_arg:
                    tool_arg = tool_arg.split("=")[-1].strip()
                
                # Use regex to extract just the environment name
                import re
                
                # Check if user wants all projects
                if any(word in tool_arg.lower() for word in ["all", "semua", "every", "any"]):
                    tool_arg = "all"
                else:
                    env_match = re.search(r'(dev|development|stg|staging|prod|production)', tool_arg.lower())
                    if env_match:
                        tool_arg = env_match.group(1)
                    else:
                        # Default to all if no environment specified
                        tool_arg = "all"
                    
            # Clean up arguments for create_gcp_project
            elif tool_name == "create_gcp_project":
                # Parse project_id, project_name, and organization_id from the argument
                import re
                
                # Initialize variables
                project_id = ""
                project_name = ""
                organization_id = ""
                
                # Extract project_id
                project_id_match = re.search(r'project_id\s*=\s*["\'](.*?)["\']', tool_arg)
                if project_id_match:
                    project_id = project_id_match.group(1)
                else:
                    # Try to get the first quoted string or word
                    project_id_match = re.search(r'["\'](.*?)["\']', tool_arg)
                    if project_id_match:
                        project_id = project_id_match.group(1)
                    else:
                        # Just use the first word
                        project_id = tool_arg.split()[0] if tool_arg.split() else ""
                
                # Extract project_name if present
                project_name_match = re.search(r'project_name\s*=\s*["\'](.*?)["\']', tool_arg)
                if project_name_match:
                    project_name = project_name_match.group(1)
                
                # Extract organization_id if present
                org_id_match = re.search(r'organization_id\s*=\s*["\'](.*?)["\']', tool_arg)
                if org_id_match:
                    organization_id = org_id_match.group(1)
                
                # Clean up the extracted values
                project_id = project_id.strip('"\'}{')
                project_name = project_name.strip('"\'}{')
                organization_id = organization_id.strip('"\'}{')
                
                # Construct a clean argument string
                tool_arg = f"{project_id},{project_name},{organization_id}"
                
            # For cat commands, ensure path is properly quoted
            if tool_name == "execute_command" and "cat" in tool_arg:
                if '"' not in tool_arg and "'" not in tool_arg:
                    file_path = tool_arg.split(" ")[-1]
                    tool_arg = f'cat "{file_path}"'

            if tool_name in self.tools:
                # Execute tool
                result = self.tools[tool_name](tool_arg)
                self._display_tool_result(result)
            else:
                print(f"\nError: Tool '{tool_name}' is not available.")
        except Exception as e:
            print(f"\nError parsing tool response: {e}")
    
    def _display_tool_result(self, result):
        """Display the result of a tool execution."""
        if result.success:
            print("\nResult:")
            print("=" * 50)
            print(result.result)
            print("=" * 50)
        else:
            print("\nError:", result.error_message)

def main():
    """Main function to run the CLI interface."""
    try:
        agent = Agent()
        
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
            "anthropic": "Anthropic Claude"
        }.get(agent.provider_name, agent.provider_name.title())
        
        welcoming_text = f"""
        Welcome to Multi-LLM CLI Agent
        Using provider: {provider_name}
        Using model: {agent.provider.model_id}
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
                agent.process_with_tools(user_input)
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
