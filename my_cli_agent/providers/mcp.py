import functools
from typing import List, Dict, Any
from my_cli_agent.models import Tool
from my_cli_agent.tools.tool_utils import call_mcp_server_helper

# A list of dictionaries, where each dictionary defines an MCP tool.
# This makes adding new prompt-based MCP tools as simple as adding a new dict to this list.
MCP_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "call_mcp_server",
        "description": (
            "Sends a prompt to the Zen MCP server for advanced processing. "
            "This tool acts as a gateway to the MCP server, allowing it to handle "
            "complex, multi-step tasks like code reviews, debugging, and planning."
        ),
        "env_var": "MCP_SERVER_URL",
    },
    {
        "name": "call_sequential_thinking_mcp",
        "description": (
            "Sends a prompt to the Sequential Thinking MCP server for problems "
            "that require step-by-step reasoning or complex analysis."
        ),
        "env_var": "SEQ_THINKING_MCP_SERVER_URL",
    },
    {
        "name": "call_example_mcp",
        "description": (
            "This is an example MCP tool. It shows how to add new tools "
            "by simply adding a new definition to the provider list. "
            "It does not connect to a real server and should be used for demonstration purposes."
        ),
        "env_var": "EXAMPLE_MCP_SERVER_URL",
    },
    # To add a new MCP tool, just add another dictionary definition above this line.
]

def _create_mcp_tool(definition: Dict[str, Any]) -> Tool:
    """Dynamically creates a tool function from a definition."""

    # Use functools.partial to create a new function with some arguments pre-filled.
    # This new function will only require the 'prompt' argument.
    tool_function = functools.partial(
        call_mcp_server_helper,
        mcp_env_var=definition["env_var"],
        tool_name=definition["name"]
    )

    # The agent uses the function's name and docstring to select the right tool.
    # We must set them dynamically.
    tool_function.__name__ = definition["name"]
    tool_function.__doc__ = definition["description"]

    # The agent expects a list of Tool objects.
    return Tool(
        name=definition["name"],
        description=definition["description"],
        func=tool_function
    )

def get_mcp_tools() -> List[Tool]:
    """
    Generates and returns a list of all MCP tools defined in this provider.

    This function is called by the agent to get all available MCP tools.
    """
    return [_create_mcp_tool(definition) for definition in MCP_TOOL_DEFINITIONS]
