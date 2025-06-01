#!/usr/bin/env python3
"""
GCP Monitoring Demo

This script demonstrates the usage of the GCP MonitoringAgent to monitor GCP resources.
It shows how to query metrics, create custom metrics, and monitor resource health.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to allow imports
sys.path.append(str(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from adk_cli_agent.tools.gcp.agents import MonitoringAgent
from adk_cli_agent.tools.gcp.tools.base.types import ToolResult

# Configuration
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
REGION = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
ZONE = os.getenv('GOOGLE_CLOUD_ZONE', 'us-central1-a')
INSTANCE_NAME = os.getenv('GCE_INSTANCE_NAME', 'demo-instance')

class MonitoringDemo:
    """Demonstrates GCP Monitoring capabilities."""
    
    def __init__(self):
        """Initialize the demo with a MonitoringAgent."""
        self.agent = MonitoringAgent(project_id=PROJECT_ID)
        self.created_metrics: List[Dict[str, Any]] = []
    
    async def run_demo(self):
        """Run the complete demo workflow."""
        try:
            # 1. List available metric descriptors
            await self.list_metric_descriptors()
            
            # 2. Query CPU utilization for an instance
            await self.query_cpu_utilization()
            
            # 3. Query memory usage for an instance
            await self.query_memory_usage()
            
            # 4. Query network traffic for an instance
            await self.query_network_traffic()
            
            # 5. Create a custom metric
            await self.create_custom_metric()
            
            # 6. Write data to the custom metric
            await self.write_custom_metric_data()
            
            # 7. Query the custom metric
            await self.query_custom_metric()
            
            logger.info("Demo completed successfully!")
            
        except Exception as e:
            logger.error(f"Demo failed: {str(e)}", exc_info=True)
            raise
        finally:
            # 8. Clean up created resources
            await self.cleanup_resources()
    
    async def list_metric_descriptors(self):
        """List available metric descriptors."""
        logger.info("\n=== Listing Metric Descriptors ===")
        
        # List the first 10 metric descriptors
        result = await self.agent.list_metric_descriptors(
            filter_str='metric.type = starts_with("compute.googleapis.com/")',
            page_size=10
        )
        
        if not result.success:
            logger.error(f"Failed to list metric descriptors: {result.error}")
            return
        
        descriptors = result.data.get('descriptors', [])
        logger.info(f"Found {len(descriptors)} metric descriptors:")
        
        for i, desc in enumerate(descriptors, 1):
            logger.info(f"{i}. {desc['type']} ({desc['metric_kind']}, {desc['value_type']})")
            logger.info(f"   {desc['description']}")
    
    async def query_cpu_utilization(self):
        """Query CPU utilization for a Compute Engine instance."""
        logger.info("\n=== Querying CPU Utilization ===")
        
        # Get CPU utilization for the last 15 minutes
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=15)
        
        result = await self.agent.get_cpu_utilization(
            instance_id=INSTANCE_NAME,
            zone=ZONE,
            start_time=start_time,
            end_time=end_time,
            aggregation={
                'alignment_period': {'seconds': 300},  # 5 minutes
                'per_series_aligner': monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
                'cross_series_reducer': monitoring_v3.Aggregation.Reducer.REDUCE_MEAN,
            }
        )
        
        if not result.success:
            logger.error(f"Failed to query CPU utilization: {result.error}")
            return
        
        time_series = result.data.get('time_series', [])
        if not time_series:
            logger.warning("No CPU utilization data found for the specified instance.")
            return
        
        logger.info(f"CPU Utilization for {INSTANCE_NAME}:")
        for ts in time_series:
            points = ts.get('points', [])
            if not points:
                continue
                
            # Print the most recent data point
            latest = points[-1]
            timestamp = latest['time']
            value = latest['value']
            
            logger.info(f"  {timestamp}: {value*100:.2f}%")
    
    async def query_memory_usage(self):
        """Query memory usage for a Compute Engine instance."""
        logger.info("\n=== Querying Memory Usage ===")
        
        # Get memory usage for the last 15 minutes
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=15)
        
        result = await self.agent.get_memory_usage(
            instance_id=INSTANCE_NAME,
            zone=ZONE,
            start_time=start_time,
            end_time=end_time,
            aggregation={
                'alignment_period': {'seconds': 300},  # 5 minutes
                'per_series_aligner': monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
            }
        )
        
        if not result.success:
            logger.error(f"Failed to query memory usage: {result.error}")
            return
        
        time_series = result.data.get('time_series', [])
        if not time_series:
            logger.warning("No memory usage data found for the specified instance.")
            return
        
        logger.info(f"Memory Usage for {INSTANCE_NAME}:")
        for ts in time_series:
            points = ts.get('points', [])
            if not points:
                continue
                
            # Print the most recent data point
            latest = points[-1]
            timestamp = latest['time']
            value = latest['value']  # In bytes
            
            # Convert to MB for readability
            value_mb = value / (1024 * 1024)
            logger.info(f"  {timestamp}: {value_mb:.2f} MB")
    
    async def query_network_traffic(self):
        """Query network traffic for a Compute Engine instance."""
        logger.info("\n=== Querying Network Traffic ===")
        
        # Get network traffic for the last 15 minutes
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=15)
        
        for direction in ['received', 'sent']:
            result = await self.agent.get_network_traffic(
                instance_id=INSTANCE_NAME,
                zone=ZONE,
                direction=direction,
                start_time=start_time,
                end_time=end_time,
                aggregation={
                    'alignment_period': {'seconds': 300},  # 5 minutes
                    'per_series_aligner': monitoring_v3.Aggregation.Aligner.ALIGN_RATE,
                }
            )
            
            if not result.success:
                logger.error(f"Failed to query {direction} traffic: {result.error}")
                continue
            
            time_series = result.data.get('time_series', [])
            if not time_series:
                logger.warning(f"No {direction} traffic data found for the specified instance.")
                continue
            
            logger.info(f"Network {direction.capitalize()} for {INSTANCE_NAME}:")
            for ts in time_series:
                points = ts.get('points', [])
                if not points:
                    continue
                    
                # Print the most recent data point
                latest = points[-1]
                timestamp = latest['time']
                value = latest['value']  # In bytes/second
                
                # Convert to KB/s for readability
                value_kbps = value / 1024
                logger.info(f"  {timestamp}: {value_kbps:.2f} KB/s")
    
    async def create_custom_metric(self):
        """Create a custom metric."""
        logger.info("\n=== Creating Custom Metric ===")
        
        metric_type = f"custom.googleapis.com/demo/custom_metric_{int(datetime.now().timestamp())}"
        
        result = await self.agent.create_metric_descriptor(
            metric_type=metric_type,
            metric_kind="GAUGE",
            value_type="DOUBLE",
            description="A custom demo metric",
            display_name="Demo Custom Metric",
            labels={
                "environment": "demo",
                "purpose": "monitoring_demo"
            }
        )
        
        if not result.success:
            logger.error(f"Failed to create custom metric: {result.error}")
            return
        
        self.created_metrics.append({
            'type': metric_type,
            'descriptor': result.data.get('descriptor', {})
        })
        
        logger.info(f"Created custom metric: {metric_type}")
    
    async def write_custom_metric_data(self):
        """Write data to the custom metric."""
        if not self.created_metrics:
            logger.warning("No custom metrics to write data to. Run create_custom_metric() first.")
            return
        
        logger.info("\n=== Writing Data to Custom Metric ===")
        
        metric_type = self.created_metrics[0]['type']
        
        # Write a few data points
        now = datetime.now(timezone.utc)
        for i in range(5):
            # Generate a sample value
            value = 10.0 + (i * 2.5)
            
            # Write the data point
            result = await self.agent.write_metric(
                metric_type=metric_type,
                value=value,
                resource_type="global",
                resource_labels={"project_id": PROJECT_ID},
                metric_labels={"demo_label": f"value_{i}"},
                timestamp=now - timedelta(minutes=4-i)  # Backdate the points
            )
            
            if result.success:
                logger.info(f"Wrote data point: {value} at {result.data.get('timestamp')}")
            else:
                logger.error(f"Failed to write data point: {result.error}")
    
    async def query_custom_metric(self):
        """Query the custom metric data."""
        if not self.created_metrics:
            logger.warning("No custom metrics to query. Run create_custom_metric() first.")
            return
        
        logger.info("\n=== Querying Custom Metric ===")
        
        metric_type = self.created_metrics[0]['type']
        
        # Query the last 10 minutes of data
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=10)
        
        result = await self.agent.query_metrics(
            metric_type=metric_type,
            resource_type="global",
            start_time=start_time,
            end_time=end_time
        )
        
        if not result.success:
            logger.error(f"Failed to query custom metric: {result.error}")
            return
        
        time_series = result.data.get('time_series', [])
        if not time_series:
            logger.warning("No data found for the custom metric.")
            return
        
        logger.info(f"Data for custom metric {metric_type}:")
        for ts in time_series:
            labels = ts.get('metric', {})
            points = ts.get('points', [])
            
            logger.info(f"  Labels: {json.dumps(labels, indent=4)}")
            for point in points:
                logger.info(f"    {point['time']}: {point['value']}")
    
    async def cleanup_resources(self):
        """Clean up created resources."""
        logger.info("\n=== Cleaning Up Resources ===")
        
        # Note: In a real application, you would want to clean up any created metrics.
        # However, Cloud Monitoring doesn't provide an API to delete metric descriptors.
        # They will be automatically cleaned up after a period of inactivity.
        
        if self.created_metrics:
            logger.info("The following custom metrics were created (they will be automatically cleaned up):")
            for metric in self.created_metrics:
                logger.info(f"  - {metric['type']}")
        else:
            logger.info("No resources to clean up.")

async def main():
    """Run the monitoring demo."""
    if not PROJECT_ID:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable must be set")
        return
    
    demo = MonitoringDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
