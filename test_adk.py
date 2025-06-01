#!/usr/bin/env python3
"""Test script for ADK agent setup."""

import sys
import os
import importlib
from typing import Dict, Any

print("=== Python Environment ===")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

# Check if we can import the agent module
try:
    print("\n=== Importing ADK Agent ===")
    from adk_cli_agent.agent import SimpleAgent
    print("✅ Successfully imported SimpleAgent from adk_cli_agent.agent")
    
    # Try to create an agent instance
    print("\n=== Testing Agent Creation ===")
    agent = SimpleAgent()
    print("✅ Successfully created agent instance")
    
    # Test getting available tools
    print("\n=== Testing Available Tools ===")
    tools = agent.get_available_tools()
    print(f"Available tools: {tools}")
    
    if not tools:
        print("⚠️  No tools found. This might indicate an issue with tool imports.")
    
    # Test a simple tool (get_current_time should always be available)
    print("\n=== Testing get_current_time Tool ===")
    result = agent.execute_tool('get_current_time')
    print(f"Tool result: {result}")
    
    if not isinstance(result, dict) or 'success' not in result:
        print("⚠️  Unexpected tool result format")
    elif not result.get('success'):
        print(f"⚠️  Tool execution failed: {result.get('message', 'Unknown error')}")
    else:
        print("✅ Tool executed successfully")
    
    # Test GCP tools if available
    if 'list_gcp_projects' in tools:
        print("\n=== Testing GCP Tools ===")
        # This will only work if GCP credentials are properly configured
        result = agent.execute_tool('list_gcp_projects')
        print(f"GCP Projects: {result}")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}", file=sys.stderr)
    print("\n=== DEBUG ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Try to find where the module is being imported from
    try:
        import adk_cli_agent
        print(f"\nModule found at: {adk_cli_agent.__file__}")
    except ImportError:
        print("\nCould not import adk_cli_agent")
    
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed!")
