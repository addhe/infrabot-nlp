"""Example usage of GCP Root Agent with specialized agents.

This script demonstrates how to initialize the GCP Root Agent with specialized agents
and perform operations across different GCP services.
"""

import asyncio
import logging
from pprint import pprint

from adk_cli_agent.tools.gcp.agents import (
    GCPRootAgent,
    ProjectAgent,
    ComputeAgent,
    StorageAgent,
    NetworkingAgent,
    IAMAgent
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function to demonstrate root agent usage."""
    try:
        # Initialize specialized agents
        project_agent = ProjectAgent()
        compute_agent = ComputeAgent()
        storage_agent = StorageAgent()
        networking_agent = NetworkingAgent()
        iam_agent = IAMAgent()

        # Create root agent with all specialized agents
        root_agent = GCPRootAgent(agents=[
            project_agent,
            compute_agent,
            storage_agent,
            networking_agent,
            iam_agent
        ])

        # Example 1: List all available agents
        print("\n=== Available Agents ===")
        agents = root_agent.get_available_agents()
        for agent in agents:
            print(f"- {agent['name']}: {agent['description']}")

        # Example 2: List projects using the project agent
        print("\n=== Listing GCP Projects ===")
        projects_result = await root_agent.route_request(
            agent_name="gcp-project-agent",
            tool_name="list_projects",
            env="all"
        )
        pprint(projects_result)

        # Example 3: List compute instances
        print("\n=== Listing Compute Instances ===")
        # Replace with your project ID and zone
        project_id = "your-project-id"
        zone = "us-central1-a"
        
        instances_result = await root_agent.route_request(
            agent_name="gcp-compute-agent",
            tool_name="list_instances",
            project_id=project_id,
            zone=zone
        )
        pprint(instances_result)

        # Example 4: List storage buckets
        print("\n=== Listing Storage Buckets ===")
        buckets_result = await root_agent.route_request(
            agent_name="gcp-storage-agent",
            tool_name="list_buckets",
            project_id=project_id
        )
        pprint(buckets_result)

        # Example 5: List IAM policies
        print("\n=== Getting IAM Policy ===")
        iam_policy_result = await root_agent.route_request(
            agent_name="gcp-iam-agent",
            tool_name="get_iam_policy",
            project_id=project_id
        )
        pprint(iam_policy_result)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
