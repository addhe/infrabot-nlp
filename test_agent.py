#!/usr/bin/env python3
"""Test script for SimpleAgent."""

import asyncio
import logging
from adk_cli_agent.agent import SimpleAgent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_agent():
    """Test the SimpleAgent functionality."""
    print("Creating agent instance...")
    agent = SimpleAgent()
    
    print("\nAgent tools:")
    for tool in agent.get_available_tools():
        print(f"- {tool}")
    
    print("\nTesting get_current_time tool:")
    time_result = await agent.execute_tool('get_current_time')
    print(f"Result: {time_result}")
    
    if 'list_gcp_projects' in agent.get_available_tools():
        print("\nTesting list_gcp_projects tool:")
        projects_result = await agent.execute_tool('list_gcp_projects', env='all')
        print(f"Result: {projects_result}")
    
    print("\nAgent context:")
    print(agent.context)
    
    print("\nAgent help:")
    print(agent.help())

if __name__ == "__main__":
    print("Starting agent test...")
    asyncio.run(test_agent())
    print("\nTest completed!")
