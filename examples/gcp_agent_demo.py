#!/usr/bin/env python3
"""
GCP Agent Demo Script

This script demonstrates the usage of various GCP agents to manage GCP resources.
It shows how to initialize agents, perform operations, and handle responses.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to allow imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from adk_cli_agent.tools.gcp.agents import (
    GCPRootAgent,
    ProjectAgent,
    ComputeAgent,
    StorageAgent,
    NetworkingAgent,
    IAMAgent
)

# Configuration
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
REGION = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
ZONE = os.getenv('GOOGLE_CLOUD_ZONE', 'us-central1-a')
BUCKET_NAME = f"demo-bucket-{PROJECT_ID}"
NETWORK_NAME = "demo-network"
SUBNET_NAME = "demo-subnet"
INSTANCE_NAME = "demo-instance"
SERVICE_ACCOUNT_NAME = "demo-service-account"

class GCPSetupDemo:
    """Demonstrates GCP resource management using the GCP agents."""
    
    def __init__(self):
        """Initialize the demo with GCP agents."""
        self.project_agent = ProjectAgent()
        self.compute_agent = ComputeAgent()
        self.storage_agent = StorageAgent()
        self.networking_agent = NetworkingAgent()
        self.iam_agent = IAMAgent()
        
        # Initialize root agent with all specialized agents
        self.root_agent = GCPRootAgent(agents=[
            self.project_agent,
            self.compute_agent,
            self.storage_agent,
            self.networking_agent,
            self.iam_agent
        ])
        
        # Store created resources for cleanup
        self.created_resources: Dict[str, List[Dict[str, Any]]] = {
            'buckets': [],
            'instances': [],
            'networks': [],
            'subnets': [],
            'service_accounts': []
        }
    
    async def run_demo(self):
        """Run the complete demo workflow."""
        try:
            # 1. Verify project access
            await self.verify_project_access()
            
            # 2. List available agents and tools
            await self.list_agents_and_tools()
            
            # 3. Storage operations
            await self.demo_storage_operations()
            
            # 4. Networking operations
            await self.demo_networking_operations()
            
            # 5. IAM operations
            await self.demo_iam_operations()
            
            # 6. Compute operations
            await self.demo_compute_operations()
            
            logger.info("Demo completed successfully!")
            
        except Exception as e:
            logger.error(f"Demo failed: {str(e)}", exc_info=True)
            raise
        finally:
            # 7. Cleanup resources
            await self.cleanup_resources()
    
    async def verify_project_access(self):
        """Verify access to the GCP project."""
        logger.info(f"Verifying access to project: {PROJECT_ID}")
        
        # Get project details
        result = await self.project_agent.get_project(project_id=PROJECT_ID)
        
        if not result.success:
            raise RuntimeError(f"Failed to access project: {result.error}")
        
        project = result.data
        logger.info(f"Project details: {json.dumps(project, indent=2, default=str)}")
    
    async def list_agents_and_tools(self):
        """List all available agents and their tools."""
        logger.info("Listing available agents and tools...")
        
        agents = self.root_agent.get_available_agents()
        
        logger.info("\n=== Available Agents ===")
        for agent in agents:
            logger.info(f"\nAgent: {agent['name']}")
            logger.info(f"Description: {agent['description']}")
            logger.info("Tools:")
            for tool in agent['tools']:
                logger.info(f"  - {tool['name']}: {tool['description']}")
    
    async def demo_storage_operations(self):
        """Demonstrate storage operations."""
        logger.info("\n=== Starting Storage Operations ===")
        
        # Create a bucket
        logger.info(f"Creating bucket: {BUCKET_NAME}")
        create_result = await self.storage_agent.create_bucket(
            project_id=PROJECT_ID,
            bucket_name=BUCKET_NAME,
            location=REGION,
            storage_class="STANDARD"
        )
        
        if not create_result.success:
            logger.warning(f"Failed to create bucket: {create_result.error}")
            return
            
        self.created_resources['buckets'].append({'name': BUCKET_NAME})
        logger.info(f"Bucket created: {BUCKET_NAME}")
        
        # List buckets
        logger.info("Listing buckets...")
        list_result = await self.storage_agent.list_buckets(project_id=PROJECT_ID)
        
        if list_result.success:
            buckets = list_result.data.get('buckets', [])
            logger.info(f"Found {len(buckets)} buckets:")
            for bucket in buckets:
                logger.info(f"- {bucket['name']} ({bucket['storage_class']})")
    
    async def demo_networking_operations(self):
        """Demonstrate networking operations."""
        logger.info("\n=== Starting Networking Operations ===")
        
        # Create a VPC network
        logger.info(f"Creating VPC network: {NETWORK_NAME}")
        network_result = await self.networking_agent.create_network(
            project_id=PROJECT_ID,
            network_name=NETWORK_NAME,
            auto_create_subnetworks=False,
            description="Demo network"
        )
        
        if not network_result.success:
            logger.warning(f"Failed to create network: {network_result.error}")
            return
            
        self.created_resources['networks'].append({'name': NETWORK_NAME})
        
        # Create a subnet
        logger.info(f"Creating subnet: {SUBNET_NAME}")
        subnet_result = await self.networking_agent.create_subnet(
            project_id=PROJECT_ID,
            region=REGION,
            network_name=NETWORK_NAME,
            subnet_name=SUBNET_NAME,
            ip_cidr_range="10.0.0.0/24",
            description="Demo subnet"
        )
        
        if not subnet_result.success:
            logger.warning(f"Failed to create subnet: {subnet_result.error}")
            return
            
        self.created_resources['subnets'].append({
            'name': SUBNET_NAME,
            'region': REGION
        })
        
        # List networks
        logger.info("Listing networks...")
        list_result = await self.networking_agent.list_networks(
            project_id=PROJECT_ID
        )
        
        if list_result.success:
            networks = list_result.data.get('networks', [])
            logger.info(f"Found {len(networks)} networks:")
            for network in networks:
                logger.info(f"- {network['name']} ({network.get('description', 'No description')})")
    
    async def demo_iam_operations(self):
        """Demonstrate IAM operations."""
        logger.info("\n=== Starting IAM Operations ===")
        
        # Create a service account
        logger.info(f"Creating service account: {SERVICE_ACCOUNT_NAME}")
        sa_result = await self.iam_agent.create_service_account(
            project_id=PROJECT_ID,
            account_id=SERVICE_ACCOUNT_NAME,
            display_name="Demo Service Account",
            description="Service account for demo purposes"
        )
        
        if not sa_result.success:
            logger.warning(f"Failed to create service account: {sa_result.error}")
            return
            
        sa_email = sa_result.data.get('email')
        self.created_resources['service_accounts'].append({
            'email': sa_email,
            'account_id': SERVICE_ACCOUNT_NAME
        })
        
        logger.info(f"Service account created: {sa_email}")
        
        # List service accounts
        logger.info("Listing service accounts...")
        list_result = await self.iam_agent.list_service_accounts(
            project_id=PROJECT_ID
        )
        
        if list_result.success:
            accounts = list_result.data.get('accounts', [])
            logger.info(f"Found {len(accounts)} service accounts:")
            for account in accounts[:5]:  # Show first 5 accounts
                logger.info(f"- {account['display_name']} ({account['email']})")
            if len(accounts) > 5:
                logger.info(f"... and {len(accounts) - 5} more")
    
    async def demo_compute_operations(self):
        """Demonstrate compute operations."""
        logger.info("\n=== Starting Compute Operations ===")
        
        # List available machine types
        logger.info("Listing available machine types...")
        machine_types_result = await self.compute_agent.list_machine_types(
            project_id=PROJECT_ID,
            zone=ZONE
        )
        
        if not machine_types_result.success:
            logger.warning(f"Failed to list machine types: {machine_types_result.error}")
            return
            
        machine_types = machine_types_result.data.get('machine_types', [])
        if machine_types:
            # Get the first available machine type
            machine_type = f"zones/{ZONE}/machineTypes/{machine_types[0]['name']}"
            logger.info(f"Using machine type: {machine_type}")
            
            # List available images
            logger.info("Listing available images...")
            images_result = await self.compute_agent.list_images(
                project_id="debian-cloud",
                max_results=5
            )
            
            if not images_result.success:
                logger.warning(f"Failed to list images: {images_result.error}")
                return
                
            images = images_result.data.get('images', [])
            if images:
                # Use the first Debian 10 image
                image_uri = images[0]['self_link']
                logger.info(f"Using image: {image_uri}")
                
                # Create an instance (just show the command, don't actually create)
                logger.info("\nTo create an instance, you would use:")
                logger.info(f"""
                await compute_agent.create_instance(
                    project_id='{PROJECT_ID}',
                    zone='{ZONE}',
                    instance_name='{INSTANCE_NAME}',
                    machine_type='{machine_type}',
                    source_image=image_uri,
                    network_name='{NETWORK_NAME}',
                    subnetwork_name='{SUBNET_NAME}',
                    external_ip=True
                )
                """)
            else:
                logger.warning("No images found")
    
    async def cleanup_resources(self):
        """Clean up created resources."""
        logger.info("\n=== Cleaning Up Resources ===")
        
        # Delete service accounts
        for sa in self.created_resources['service_accounts']:
            logger.info(f"Deleting service account: {sa['email']}")
            await self.iam_agent.delete_service_account(
                project_id=PROJECT_ID,
                account_id=sa['email']
            )
        
        # Delete instances
        for instance in self.created_resources['instances']:
            logger.info(f"Deleting instance: {instance['name']}")
            await self.compute_agent.delete_instance(
                project_id=PROJECT_ID,
                zone=instance.get('zone', ZONE),
                instance_name=instance['name']
            )
        
        # Delete subnets
        for subnet in self.created_resources['subnets']:
            logger.info(f"Deleting subnet: {subnet['name']}")
            await self.networking_agent.delete_subnet(
                project_id=PROJECT_ID,
                region=subnet['region'],
                subnet_name=subnet['name']
            )
        
        # Delete networks
        for network in self.created_resources['networks']:
            logger.info(f"Deleting network: {network['name']}")
            await self.networking_agent.delete_network(
                project_id=PROJECT_ID,
                network_name=network['name']
            )
        
        # Delete buckets
        for bucket in self.created_resources['buckets']:
            logger.info(f"Deleting bucket: {bucket['name']}")
            # First, delete all objects in the bucket
            list_objects = await self.storage_agent.list_objects(
                bucket_name=bucket['name']
            )
            
            if list_objects.success:
                for obj in list_objects.data.get('objects', []):
                    logger.info(f"  Deleting object: {obj['name']}")
                    await self.storage_agent.delete_object(
                        bucket_name=bucket['name'],
                        object_name=obj['name']
                    )
            
            # Then delete the bucket
            await self.storage_agent.delete_bucket(
                bucket_name=bucket['name']
            )

async def main():
    """Run the demo."""
    if not PROJECT_ID:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable must be set")
        return
    
    demo = GCPSetupDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
