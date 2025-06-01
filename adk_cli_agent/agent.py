"""ADK CLI Agent implementation with proper ADK patterns.

This module implements a CLI agent using Google's Agent Development Kit (ADK) with:
- SessionService for state management
- ToolContext for state-aware tools
- Safety guardrails with callbacks
- Multi-model support with LiteLLM
- Proper agent configuration patterns
"""

import os
import sys
import atexit
import logging
from typing import Any, Dict, List, Optional, Type, Union, cast, TYPE_CHECKING

# Import ADK components
try:
    from google.adk.agents import Agent
    from google.adk.core import ToolContext, SessionService, Runner
    from google.adk.tools import tool
    HAS_ADK = True
except ImportError:
    # Fallback for development/testing without full ADK
    HAS_ADK = False
    Agent = object  # type: ignore
    ToolContext = object  # type: ignore
    SessionService = object  # type: ignore
    Runner = object  # type: ignore
    tool = lambda func: func  # type: ignore

# Import LiteLLM for multi-model support
try:
    import litellm
    HAS_LITELLM = True
except ImportError:
    HAS_LITELLM = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ADKAgent")

# Import tools from their respective modules
try:
    from .tools.time_tools import get_current_time
    from .tools.command_tools import execute_command
    from .tools.gcp_tools import list_gcp_projects, create_gcp_project, HAS_GCP_TOOLS_FLAG
    TOOLS_IMPORTED = True
except ImportError as e:
    logger.warning(f"Failed to import some tools: {e}")
    TOOLS_IMPORTED = False
    HAS_GCP_TOOLS_FLAG = False

# Safety and security configurations
DANGEROUS_COMMANDS = [
    'rm -rf', 'sudo rm', 'format', 'fdisk', 'dd if=', 'mkfs',
    '> /dev/', 'chmod 777', 'chown -R', '://', 'curl', 'wget'
]

GCP_SENSITIVE_OPERATIONS = [
    'delete', 'remove', 'destroy', 'terminate', 'stop'
]

# Session service for state management
class ADKSessionService:
    """Session service for managing agent state and memory."""
    
    def __init__(self):
        self.sessions = {}
        self.current_session_id = None
        
    def create_session(self, session_id: str = None) -> str:
        """Create a new session."""
        if session_id is None:
            import uuid
            session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'created_at': os.getenv('TIMESTAMP', 'unknown'),
            'state': {},
            'history': [],
            'context': {}
        }
        self.current_session_id = session_id
        return session_id
        
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get session state."""
        return self.sessions.get(session_id, {}).get('state', {})
        
    def update_session_state(self, session_id: str, key: str, value: Any):
        """Update session state."""
        if session_id in self.sessions:
            self.sessions[session_id]['state'][key] = value
            
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context."""
        return self.sessions.get(session_id, {}).get('context', {})

# Initialize session service
session_service = ADKSessionService()

# Safety callbacks
def before_model_callback(inputs: Dict[str, Any], context: ToolContext) -> Dict[str, Any]:
    """Safety callback before model execution."""
    logger.info("Running safety check before model execution")
    
    # Check for potentially harmful requests
    user_input = str(inputs.get('prompt', '')).lower()
    
    for dangerous_pattern in DANGEROUS_COMMANDS:
        if dangerous_pattern in user_input:
            logger.warning(f"Potentially dangerous command detected: {dangerous_pattern}")
            inputs['safety_warning'] = f"Detected potentially dangerous pattern: {dangerous_pattern}"
            
    return inputs

def before_tool_callback(tool_name: str, inputs: Dict[str, Any], context: ToolContext) -> Dict[str, Any]:
    """Safety callback before tool execution."""
    logger.info(f"Running safety check before tool execution: {tool_name}")
    
    # Check for dangerous commands
    if tool_name == 'execute_command':
        command = str(inputs.get('command', '')).lower()
        for dangerous_cmd in DANGEROUS_COMMANDS:
            if dangerous_cmd in command:
                logger.error(f"Blocked dangerous command: {command}")
                raise ValueError(f"Command blocked for safety: contains '{dangerous_cmd}'")
                
    # Check for sensitive GCP operations
    if tool_name in ['create_gcp_project', 'delete_gcp_project']:
        for sensitive_op in GCP_SENSITIVE_OPERATIONS:
            if sensitive_op in str(inputs.values()).lower():
                logger.warning(f"Sensitive GCP operation detected: {sensitive_op}")
                
    return inputs
# State-aware tool wrappers using ToolContext
@tool
def get_current_time_with_context(context: ToolContext, city: str = "") -> dict:
    """Get current time with session context.
    
    Args:
        context: Tool context for session state management
        city: City name for timezone (optional)
        
    Returns:
        Dict containing current time information
    """
    # Update session state with tool usage
    session_id = getattr(context, 'session_id', None)
    if session_id:
        session_service.update_session_state(session_id, 'last_time_query', city)
        
    result = get_current_time(city)
    
    # Store result in context for potential future use
    if hasattr(context, 'set_value'):
        context.set_value('last_time_result', result)
        
    return result

@tool  
def execute_command_with_context(context: ToolContext, command: str) -> dict:
    """Execute command with session context and safety checks.
    
    Args:
        context: Tool context for session state management
        command: Shell command to execute
        
    Returns:
        Dict containing command execution result
    """
    # Check session state for command history
    session_id = getattr(context, 'session_id', None)
    if session_id:
        session_state = session_service.get_session_state(session_id)
        command_history = session_state.get('command_history', [])
        command_history.append(command)
        session_service.update_session_state(session_id, 'command_history', command_history[-10:])  # Keep last 10
        
    result = execute_command(command)
    
    # Store result in context
    if hasattr(context, 'set_value'):
        context.set_value('last_command_result', result)
        
    return result

@tool
def list_gcp_projects_with_context(context: ToolContext, env: str = "all") -> dict:
    """List GCP projects with session context.
    
    Args:
        context: Tool context for session state management 
        env: Environment filter (dev, stg, prod, all)
        
    Returns:
        Dict containing GCP projects list
    """
    # Update session state
    session_id = getattr(context, 'session_id', None)
    if session_id:
        session_service.update_session_state(session_id, 'last_gcp_env', env)
        
    result = list_gcp_projects(env)
    
    # Store result in context
    if hasattr(context, 'set_value'):
        context.set_value('last_gcp_projects', result)
        
    return result

@tool
def create_gcp_project_with_context(
    context: ToolContext, 
    project_id: str, 
    project_name: str = "", 
    organization_id: str = ""
) -> dict:
    """Create GCP project with session context and tracking.
    
    Args:
        context: Tool context for session state management
        project_id: Unique project identifier
        project_name: Display name for project
        organization_id: Organization ID (optional)
        
    Returns:
        Dict containing creation result
    """
    # Track project creation in session
    session_id = getattr(context, 'session_id', None)
    if session_id:
        session_state = session_service.get_session_state(session_id)
        created_projects = session_state.get('created_projects', [])
        created_projects.append({
            'project_id': project_id,
            'project_name': project_name,
            'timestamp': os.getenv('TIMESTAMP', 'unknown')
        })
        session_service.update_session_state(session_id, 'created_projects', created_projects)
        
    result = create_gcp_project(project_id, project_name, organization_id)
    
    # Store result in context
    if hasattr(context, 'set_value'):
        context.set_value('last_project_creation', result)
        
    return result
# Model configuration with LiteLLM support
def get_model_config():
    """Get model configuration with multi-model support."""
    model_id = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-flash-latest")
    
    if HAS_LITELLM:
        # Support multiple models through LiteLLM
        supported_models = {
            "gemini": f"gemini/{model_id}",
            "gpt-4": "gpt-4-turbo-preview", 
            "gpt-3.5": "gpt-3.5-turbo",
            "claude": "claude-3-opus-20240229"
        }
        
        # Check available API keys and select best model
        if os.getenv("OPENAI_API_KEY") and os.getenv("USE_OPENAI", "false").lower() == "true":
            return supported_models["gpt-4"]
        elif os.getenv("ANTHROPIC_API_KEY") and os.getenv("USE_CLAUDE", "false").lower() == "true":
            return supported_models["claude"]
        else:
            return supported_models["gemini"]
    else:
        return model_id

# Create the ADK agent with proper configuration
def create_adk_agent():
    """Create properly configured ADK agent."""
    
    # Collect available tools
    tools = []
    
    # Always include basic tools with context support
    tools.extend([
        get_current_time_with_context,
        execute_command_with_context
    ])
    
    # Add GCP tools if available
    if HAS_GCP_TOOLS_FLAG:
        tools.extend([
            list_gcp_projects_with_context,
            create_gcp_project_with_context
        ])
    
    if HAS_ADK:
        # Use proper ADK agent configuration
        agent = Agent(
            name="infrabot-nlp-cli-agent",
            model=get_model_config(),
            description="Advanced CLI agent for infrastructure management with GCP tools",
            instruction="""You are an expert infrastructure management agent with the following capabilities:

1. **Time Management**: Provide current time for any supported city/timezone
2. **Command Execution**: Execute shell commands safely with built-in security checks  
3. **GCP Operations**: Manage Google Cloud Platform resources including projects

**Safety Guidelines**:
- Always validate commands before execution
- Warn users about potentially dangerous operations
- For GCP operations, confirm destructive actions
- Maintain session state for better user experience

**Interaction Style**:
- Be helpful and professional
- Provide clear explanations for complex operations
- Ask for confirmation on sensitive operations
- Show progress for long-running tasks

**Session Management**:
- Track user's command history and preferences
- Remember previous GCP environments and projects
- Provide contextual suggestions based on session state

When users request infrastructure operations, guide them through the process step by step and ensure they understand the implications of their actions.""",
            tools=tools,
            before_model_callback=before_model_callback,
            before_tool_callback=before_tool_callback,
            session_service=session_service,
            output_key="infrabot_response"  # For automatic state persistence
        )
    else:
        # Fallback agent for development/testing
        agent = SimpleADKAgent(tools=tools)
        
    return agent

class SimpleADKAgent:
    
    # Define model fields
    version: str = "1.0.0"
    
    # Use a valid field name without leading underscore
    initialized: bool = Field(default=False, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        """Initialize the SimpleAgent with required parameters."""
        logger.info("Initializing SimpleAgent...")
        
        # Initialize with required parameters for BaseGCPAgent
        try:
            super().__init__(
                name=kwargs.get("name", "SimpleCLIAgent"),
                description=kwargs.get("description", "A simple CLI agent with basic and GCP tools")
            )
            logger.info("BaseGCPAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BaseGCPAgent: {e}")
            raise
        
        # Initialize agent properties (these are not Pydantic fields)
        self.root_agent = self
        self.agent = self
        self.sub_agents = []
        self.tools = {}
        self.available_tools = []
        
        logger.info(f"Agent initialized with {len(self.available_tools)} tools")

    def _initialize_tools(self):
        """Initialize the agent's tools."""
        if self.initialized:
            logger.debug("Tools already initialized")
            return
            
        logger.info("Initializing tools...")
        
        try:
            # Register basic tools
            self.tools = {
                'get_current_time': get_current_time,
                'execute_command': execute_command,
            }
            logger.info("Basic tools registered")
            
            # Add GCP tools if available
            if HAS_GCP_TOOLS_FLAG:
                self.tools.update({
                    'list_gcp_projects': list_gcp_projects,
                    'create_gcp_project': create_gcp_project,
                })
                logger.info("GCP tools registered")
            else:
                logger.warning("GCP tools not available. Some functionality will be limited.")
                
            self.available_tools = list(self.tools.keys())
            logger.info(f"Available tools: {', '.join(self.available_tools)}")
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing tools: {e}")
            raise

    def model_post_init(self, __context):
        """Initialize the agent after model initialization."""
        logger.info("Running model_post_init...")
        try:
            self._initialize_tools()
            logger.info("model_post_init completed successfully")
        except Exception as e:
            logger.error(f"Error in model_post_init: {e}")
            raise

    def _close(self):
        """Cleanup method called by ADK on exit."""
        # Add any cleanup code here if needed
        pass

    def get_available_tools(self) -> List[str]:
        """Return list of available tools."""
        return self.available_tools
    
    async def execute_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with given arguments."""
        if tool_name not in self.tools:
            return {'success': False, 'message': f'Tool {tool_name} not available'}
        
        try:
            tool = self.tools[tool_name]
            
            # Handle both sync and async tools
            if inspect.iscoroutinefunction(tool):
                result = await tool(*args, **kwargs)
            else:
                # Run sync tools in a thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,  # Use default executor
                    lambda: tool(*args, **kwargs)
                )
                
            if isinstance(result, dict) and 'success' in result:
                return result
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'message': str(e)}
            
    async def process_message(self, message: str, **kwargs) -> str:
        """Process a message and return a response."""
        # This is a simple implementation that just echoes the message
        # In a real implementation, you would use the Gemini API here
        return f"You said: {message}"
        
    async def generate_content(
        self,
        contents: List[Any],
        **kwargs
    ) -> Any:
        """Generate content using the agent's model."""
        # This is a simple implementation that just returns the last message
        # In a real implementation, you would use the Gemini API here
        if not contents:
            return "No content provided"
            
        last_content = contents[-1]
        # Check if we have the actual Content type and if the object is an instance
        if HAS_GENAI_TYPES and RuntimeContent and isinstance(last_content, RuntimeContent):
            parts = last_content.parts
        elif isinstance(last_content, dict):
            parts = last_content.get('parts', [])
        else:
            parts = [str(last_content)]
            
        if not parts:
            return "No content parts found"
            
        return f"Processed: {parts[0].text if hasattr(parts[0], 'text') else str(parts[0])}"
    
    def help(self) -> str:
        """Return help information about available tools."""
        help_text = """
        SimpleCLIAgent Help
        ==================
        
        Available Commands:
        ------------------
        - help: Show this help message
        - exit: Exit the agent
        - get_current_time [city]: Get current time, optionally for a specific city
        - execute_command <command>: Execute a shell command
        """
        
        if HAS_GCP_TOOLS_FLAG:
            help_text += """
        GCP Commands:
        ------------
        - list_gcp_projects [env]: List GCP projects (optional: filter by environment)
        - create_gcp_project <project_id> <project_name>: Create a new GCP project
        """
        else:
            help_text += "\nNote: GCP tools are not available (missing dependencies)\n"
            
        help_text += "\nType any message to chat with the agent."
        return help_text
        
    @property
    def context(self) -> Dict[str, Any]:
        """Return the agent's context. Required by ADK."""
        return {
            'agent_type': 'cli',
            'name': 'SimpleCLIAgent',
            'description': 'A simple CLI agent with basic and GCP tools',
            'version': self.version,
            'tools': self.available_tools,
            'capabilities': {
                'time': True,
                'command': True,
                'gcp': HAS_GCP_TOOLS_FLAG,
                'interactive': True
            },
            'config': {
                'debug': os.getenv('ADK_DEBUG', '0') == '1'
            }
        }
    
    def __str__(self) -> str:
        """Return string representation of the agent."""
        return f"SimpleAgent with {len(self.available_tools)} tools"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the agent."""
        return f"SimpleAgent(tools={self.available_tools})"

def cleanup():
    """Clean up resources before exit."""
    try:
        # Force cleanup of gRPC channels if they exist
        import grpc
        if hasattr(grpc, '_channel') and hasattr(grpc._channel, '_channel_pool'):
            for channel in list(grpc._channel._channel_pool): # Iterate over a copy
                try:
                    channel.close()
                except Exception:
                    pass # Ignore errors during cleanup
            grpc._channel._channel_pool.clear()
    except ImportError:
        pass # grpc might not be installed or available
    except Exception:
        pass # Ignore all cleanup errors

# Register cleanup on exit
atexit.register(cleanup)

# Create the main agent instance that will be exported and used
agent = SimpleAgent()

# Set the name and description as instance attributes for backward compatibility
agent.name = "SimpleCLIAgent"
agent.description = "A simple CLI agent with basic and GCP tools"

# Export root_agent as required by ADK
root_agent = agent

# Print initialization message
if HAS_GCP_TOOLS_FLAG:
    print(f"✅ Simple CLI Agent initialized with {len(agent.available_tools)} tools (including GCP tools)")
else:
    print(f"✅ Simple CLI Agent initialized with {len(agent.available_tools)} tools (GCP tools unavailable)")

# Make sure the agent has the required attributes for ADK
if not hasattr(agent, 'root_agent'):
    agent.root_agent = agent