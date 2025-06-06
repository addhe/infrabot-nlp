"""ADK CLI Agent implementation.

This module implements a CLI agent using Google's Agent Development Kit (ADK).
It provides tools for getting current time, executing commands, and listing/creating GCP projects,
as well as VPC management functions.
"""

import os
import atexit
import json

from google.adk.agents import Agent

# Import tools from their respective modules
from .tools.time_tools import get_current_time
from .tools.command_tools import execute_command
# Import GCP tools and the flag indicating their availability
from .tools.gcp_tools import (
    list_gcp_projects, 
    create_gcp_project, 
    delete_gcp_project,
    create_vpc_network,
    create_subnet,
    list_vpc_networks,
    get_vpc_details,
    delete_vpc_network,
    list_subnets,
    enable_private_google_access,
    disable_private_google_access
)

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
model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash-lite")


# Create list of tools
# Basic tools are always included
tools = [get_current_time, execute_command]

# Add GCP tools only if the necessary libraries are available (checked in gcp_tools.py)
try:
    from .tools.gcp_tools import HAS_GCP_TOOLS_FLAG
except ImportError:
    HAS_GCP_TOOLS_FLAG = False

if HAS_GCP_TOOLS_FLAG:
    # Project management tools
    tools.append(list_gcp_projects)
    tools.append(create_gcp_project)
    tools.append(delete_gcp_project)
    
    # VPC management tools
    tools.append(create_vpc_network)
    tools.append(create_subnet)
    tools.append(list_vpc_networks)
    tools.append(get_vpc_details)
    tools.append(delete_vpc_network)
    # Subnet management tools
    tools.append(list_subnets)
    tools.append(enable_private_google_access)
    tools.append(disable_private_google_access)
else:
    print("GCP tools (project and VPC management) are NOT available due to missing dependencies (google-cloud-resource-manager, google-cloud-compute, or google-auth).")

# Create the agent - this is the main entry point for ADK
root_agent = Agent(
    name="gemini_cli_agent",
    model=model_id,
    description="A CLI agent that can help with time, execute commands, manage GCP projects, and manage VPC networks",
    instruction="""You are a helpful CLI agent that can answer questions and execute commands.
    You can provide the current time in various cities, execute shell commands.
    If GCP tools are available, you can also:
    
    1. Manage GCP projects:
       - List GCP projects (specify 'all' for all projects, or 'dev', 'stg', 'prod' to filter by environment)
       - Create new GCP projects
       - Delete existing GCP projects
    

    2. Manage VPC Networks:
       - Create new VPC networks with auto or custom subnet mode and global/regional routing
       - Create custom subnets within VPC networks with optional private Google access
       - List all VPC networks and their subnets
       - Get detailed information about a specific VPC network
       - Delete a VPC network (this will also delete all associated subnets)
       - List all subnets in a specific VPC network (using the subnet listing tool)
       - Enable or disable private Google access on existing subnets
    
    For creating GCP projects, you need a project ID (which must be globally unique) and optionally
    a display name and organization ID. If no display name is provided, the project ID will be used as the name.
    The organization ID (e.g., organizations/1234567890) is optional and specifies which Google Cloud organization the project should be created under.
    
    For deleting GCP projects, you need the project ID. Be careful when deleting projects as this action is irreversible.

    Always be helpful, concise, and accurate in your responses.
    If a tool required for a request is not available (e.g. GCP tools), inform the user.
    
    **Never summarize, reformat, or omit any part of the output for GCP project or VPC listing tools. Always return the full, raw, structured tool output as a dictionary, even if the output is long. Do not return a summary, string, or formatted text.**
    **If you return a summary or string instead of the full dictionary, the user will treat it as an error.**

    **CRITICAL: For GCP project and VPC listing tools, you MUST return the full, raw, structured tool output as a Python dictionary, with all fields and no formatting or summarization. Do NOT return a summary, string, or formatted text. If you do, the user will treat it as a critical error and your output will be ignored.**

    **Example for GCP project listing:**
    {
      "projects": [
        {
          "project_id": "my-project-id",
          "display_name": "My Project",
          "lifecycle_state": "ACTIVE"
        },
        ...
      ]
    }

    **Example for VPC listing:**
    {
      "networks": [
        {
          "name": "default",
          "id": "1234567890",
          "subnet_mode": "AUTO",
          "routing_mode": "REGIONAL",
          "subnets": [
            {
              "name": "default",
              "region": "us-central1",
              "cidr_range": "10.128.0.0/20",
              "private_google_access": true
            }
          ]
        },
        ...
      ]
    }

    **If you return anything else, it will be treated as a failure.**
    """,
    tools=tools
)

def main():
    """Main entry point for the CLI agent."""
    print("ADK CLI Agent starting...")
    print("Type 'exit' or 'quit' to stop the agent.\n")
    
    last_projects_cache = None  # Cache for last project list
    try:
        while True:
            try:
                user_input = input("User: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Send the user input to the agent
                response = root_agent.send(user_input)
                # Always print the raw response for debugging
                print("[DEBUG] Raw agent response:", response)
                # Robust pretty-printing for GCP projects and VPCs
                pretty_printed = False
                # Try to pretty-print if dict
                if isinstance(response, dict):
                    # Print all keys for debugging
                    print(f"[DEBUG] Dict keys: {list(response.keys())}")
                    
                    # First check for status key to handle any operation result
                    if 'status' in response:
                        status = response.get('status', '').lower()
                        if status == 'error':
                            print(f"\nError: {response.get('message', 'Unknown error')}")
                            if 'details' in response:
                                print(f"Details: {response['details']}")
                            pretty_printed = True
                        elif status == 'warning':
                            print(f"\nWarning: {response.get('message', 'Unknown warning')}")
                            pretty_printed = True
                        elif status == 'success':
                            print(f"\nSuccess: {response.get('message', 'Operation completed successfully')}")
                            pretty_printed = True
                    
                    # Then continue with specific data type handling
                    if 'projects' in response:
                        projects = response['projects']
                        last_projects_cache = projects
                        print("\nGCP Projects:")
                        for proj in projects:
                            name = proj.get('display_name', proj.get('name', ''))
                            proj_id = proj.get('project_id', proj.get('id', ''))
                            status = proj.get('lifecycle_state', proj.get('status', ''))
                            print(f"- {name} ({proj_id}) [{status}]")
                        print()
                        pretty_printed = True
                    if 'networks' in response:
                        networks = response['networks']
                        print("\nVPC Networks:")
                        for net in networks:
                            print(f"- {net.get('name', '')} (ID: {net.get('id', '')}) [subnet_mode: {net.get('subnet_mode', '')}, routing_mode: {net.get('routing_mode', '')}]")
                            # Do not print subnets here; instruct user to use the subnet tool for details
                            # Optionally, show subnet count if available
                            subnet_count = len(net.get('subnets', [])) if 'subnets' in net and isinstance(net['subnets'], list) else 'unknown'
                            print(f"    [Use 'list_subnets' or ask for subnet details to see subnets. Subnet count: {subnet_count}]")
                        print()
                        pretty_printed = True
                    # Debug print for VPC details
                    if 'network' in response:
                        print("[DEBUG] VPC network details:")
                        print(json.dumps(response['network'], indent=2))
                        pretty_printed = True
                    
                    # Specific handling for subnet creation results
                    if 'subnet' in response and response.get('status') != 'error':
                        # Only print subnet details if we haven't already handled the response through status
                        if not pretty_printed:
                            print(f"\nSubnet operation result:")
                            subnet = response['subnet']
                            print(f"- Name: {subnet.get('name', '')}")
                            print(f"- Region: {subnet.get('region', '')}")
                            print(f"- CIDR Range: {subnet.get('cidr_range', '')}")
                            print(f"- Private Google Access: {subnet.get('private_google_access', False)}")
                            print()
                            pretty_printed = True
                    if response.get('status') == 'error':
                        print(f"Error: {response.get('message', 'Unknown error')}")
                        if 'details' in response:
                            print(f"Details: {response['details']}")
                # If dict but not pretty-printed, warn and show raw dict
                if isinstance(response, dict) and not pretty_printed:
                    print("[LLM Compliance Warning] LLM did not return expected structured output (missing 'projects' or 'networks'). Raw response:")
                    print(response)
                # If string, try to parse as JSON, else warn
                elif isinstance(response, str):
                    try:
                        parsed = json.loads(response)
                        if isinstance(parsed, dict) and ('projects' in parsed or 'networks' in parsed):
                            print("[LLM Compliance Warning] Output was a JSON string, not a dict. Pretty-printing anyway.")
                            response = parsed
                            # Recurse to pretty-print
                            if 'projects' in response:
                                projects = response['projects']
                                last_projects_cache = projects
                                print("\nGCP Projects:")
                                for proj in projects:
                                    name = proj.get('display_name', proj.get('name', ''))
                                    proj_id = proj.get('project_id', proj.get('id', ''))
                                    status = proj.get('lifecycle_state', proj.get('status', ''))
                                    print(f"- {name} ({proj_id}) [{status}]" )
                                print()
                                pretty_printed = True
                            if 'networks' in response:
                                networks = response['networks']
                                print("\nVPC Networks:")
                                for net in networks:
                                    print(f"- {net.get('name', '')} (ID: {net.get('id', '')}) [subnet_mode: {net.get('subnet_mode', '')}, routing_mode: {net.get('routing_mode', '')}]")
                                    if net.get('subnets'):
                                        for subnet in net['subnets']:
                                            print(f"    - Subnet: {subnet.get('name', '')} | Region: {subnet.get('region', '')} | CIDR: {subnet.get('cidr_range', '')} | Private Google Access: {subnet.get('private_google_access', False)}")
                                print()
                                pretty_printed = True
                        else:
                            print("[LLM Compliance Warning] Output is a string, not a dict, and does not match expected schema. Raw output:")
                            print(response)
                    except Exception:
                        print("[LLM Compliance Warning] Output is not structured (string returned instead of dict). This is an LLM error. Raw output:")
                        print(response)
                else:
                    print(f"[Debug] Unexpected agent response type: {type(response)}. Raw response:")
                    print(response)

                # Project name to ID mapping for follow-up requests
                if last_projects_cache and 'project' in user_input.lower() and 'id' not in user_input.lower():
                    # Try to help user by showing name->ID mapping
                    print("[INFO] You can refer to projects by these names and IDs:")
                    for proj in last_projects_cache:
                        name = proj.get('display_name', proj.get('name', ''))
                        proj_id = proj.get('project_id', proj.get('id', ''))
                        print(f"- {name}: {proj_id}")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")
                
    except Exception as e:
        print(f"Failed to start agent: {e}")

if __name__ == "__main__":
    main()