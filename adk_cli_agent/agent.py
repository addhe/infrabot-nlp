"""Simple CLI Agent implementation.

This module implements a CLI agent using our custom tools.
It provides tools for getting current time, executing commands, and listing/creating GCP projects.
"""

import os
import atexit

# Import tools from their respective modules
from .tools.time_tools import get_current_time
from .tools.command_tools import execute_command
# Import GCP tools and the flag indicating their availability
from .tools.gcp_tools import list_gcp_projects, create_gcp_project, HAS_GCP_TOOLS_FLAG

class SimpleAgent:
    """A simple CLI agent that uses function-based tools."""
    
    def __init__(self):
        """Initialize the agent with available tools."""
        self.tools = {
            'get_current_time': get_current_time,
            'execute_command': execute_command,
        }
        
        # Add GCP tools if available
        if HAS_GCP_TOOLS_FLAG:
            self.tools.update({
                'list_gcp_projects': list_gcp_projects,
                'create_gcp_project': create_gcp_project,
            })
        
        self.available_tools = list(self.tools.keys())
        
    def get_available_tools(self):
        """Return list of available tools."""
        return self.available_tools
    
    def execute_tool(self, tool_name, *args, **kwargs):
        """Execute a tool by name with given arguments."""
        if tool_name not in self.tools:
            return {'status': 'error', 'message': f'Tool {tool_name} not available'}
        
        try:
            result = self.tools[tool_name](*args, **kwargs)
            return {'status': 'success', 'result': result}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def help(self):
        """Return help information about available tools."""
        help_text = "Available tools:\n"
        help_text += f"- get_current_time(city=None): Get current time, optionally for a specific city\n"
        help_text += f"- execute_command(command): Execute a shell command\n"
        
        if HAS_GCP_TOOLS_FLAG:
            help_text += f"- list_gcp_projects(env='all'): List GCP projects\n"
            help_text += f"- create_gcp_project(project_id, project_name): Create a new GCP project\n"
        else:
            help_text += f"- GCP tools not available (missing dependencies)\n"
            
        return help_text

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

# Create the main agent instance
agent = SimpleAgent()

# For backward compatibility, also create a root_agent alias
root_agent = agent

# Print initialization message
if HAS_GCP_TOOLS_FLAG:
    print(f"✅ Simple CLI Agent initialized with {len(agent.available_tools)} tools (including GCP tools)")
else:
    print(f"✅ Simple CLI Agent initialized with {len(agent.available_tools)} tools (GCP tools unavailable)")