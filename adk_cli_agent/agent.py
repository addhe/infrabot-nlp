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
# Import GCP tools and the flag indicating their availability
from .tools.gcp_tools_new import list_gcp_projects, create_gcp_project, delete_gcp_project, HAS_GCP_TOOLS_FLAG

def cleanup():
    """Clean up resources before exit."""
    try:
        # Force cleanup of gRPC channels
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
        pass # Ignore other potential errors during cleanup

# Register cleanup on exit
atexit.register(cleanup)

# Get model ID from environment variable with fallback to a standard Gemini model
# Use a model ID that is generally available and supports function calling
model_id = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-flash-latest")


# Create list of tools
# Basic tools are always included
tools = [get_current_time, execute_command]

# Add GCP tools only if the necessary libraries are available (checked in gcp_tools.py)
if HAS_GCP_TOOLS_FLAG:
    tools.append(list_gcp_projects)
    tools.append(create_gcp_project)
    tools.append(delete_gcp_project)
else:
    print("GCP tools (list_gcp_projects, create_gcp_project, delete_gcp_project) are NOT available due to missing dependencies (google-cloud-resource-manager or google-auth).")

# Create the agent - this is the main entry point for ADK
root_agent = Agent(
    name="gemini_cli_agent",
    model=model_id,
    description="A CLI agent that can help with time, execute commands, and manage GCP projects",
    instruction="""You are a helpful CLI agent that can answer questions and execute commands.
    You can provide the current time in various cities and execute shell commands.
    
    If GCP tools are available, you can:
    1. List GCP projects (specify 'all' for all projects, or filter by 'dev', 'stg', 'prod')
    2. Create new GCP projects (requires project ID and display name)
    3. Delete GCP projects (with confirmation and safety checks)
    
    For creating GCP projects:
    - Project ID must be globally unique and match the pattern: [a-z][a-z0-9-]* (starts with letter, only lowercase letters, numbers, and hyphens)
    - Project name is recommended but optional. If not provided, the project ID will be used as the name

    Always be helpful, concise, and accurate in your responses.
    If a tool required for a request is not available (e.g. GCP tools), inform the user.
    """,
    tools=tools
)