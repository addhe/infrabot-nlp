"""ADK CLI Agent implementation.

This module implements a CLI agent using Google's Agent Development Kit (ADK).
It provides tools for getting current time, executing commands, and listing/creating GCP projects.
"""
import os
import atexit
from google.adk.agents import Agent

# Import tools from their respective modules
from .tools.time_tools import get_current_time
from .tools.command_tools import execute_command
from .tools.gcp_tools import list_gcp_projects, create_gcp_project, HAS_GCP_TOOLS

def cleanup():
    """Clean up resources before exit."""
    try:
        # Force cleanup of gRPC channels
        import grpc
        for channel in grpc._channel._channel_pool:
            try:
                channel.close()
            except:
                pass
        grpc._channel._channel_pool.clear()
    except:
        pass

# Register cleanup on exit
atexit.register(cleanup)

# Get model ID from environment variable with fallback to a standard Gemini model
# Use the stable version model ID that is officially supported by ADK
model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash-lite")

# Check if GCP tools are available
try:
    import google.auth
    from google.cloud import resourcemanager_v3
    HAS_GCP_TOOLS = True
except ImportError:
    HAS_GCP_TOOLS = False

# Create list of tools
tools = [get_current_time, execute_command]
if HAS_GCP_TOOLS:
    tools.append(list_gcp_projects)
    tools.append(create_gcp_project)

# Create the agent - this is the main entry point for ADK
root_agent = Agent(
    name="gemini_cli_agent",
    model=model_id,
    description="A CLI agent that can help with time, execute commands, list and create GCP projects",
    instruction="""You are a helpful CLI agent that can answer questions and execute commands.
    You can provide the current time in various cities, execute shell commands, list GCP projects,
    and create new GCP projects when requested.
    
    For creating GCP projects, you need a project ID (which must be globally unique) and optionally
    a display name and organization ID. If no display name is provided, the project ID will be used as the name.
    The organization ID is optional and specifies which Google Cloud organization the project should be created under.
    
    Always be helpful, concise, and accurate in your responses.
    """,
    tools=tools
)
