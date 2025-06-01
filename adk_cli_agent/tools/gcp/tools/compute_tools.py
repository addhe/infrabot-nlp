"""GCP Compute management tools for ADK agents."""

from typing import Dict, Any, Optional, List
from ..base.tool_context import ToolContext
from ..base.exceptions import GCPToolsError
from ..base.client import get_gcp_client
import logging

logger = logging.getLogger(__name__)


async def create_vm_instance(
    name: str,
    project_id: str,
    zone: str,
    tool_context: ToolContext,
    machine_type: str = "e2-medium",
    image_family: str = "ubuntu-2004-lts",
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new GCP Compute Engine VM instance.
    
    Args:
        name: Name for the VM instance
        project_id: GCP project ID
        zone: GCP zone (e.g., 'us-central1-a')
        tool_context: ADK tool context for state access
        machine_type: Machine type (default: e2-medium)
        image_family: OS image family (default: ubuntu-2004-lts)
        
    Returns:
        Dict containing operation status and instance details
    """
    logger.info(f"Creating VM instance: {name} in {project_id}/{zone}")
    
    try:
        # Get user preferences from state
        preferred_machine_type = tool_context.state.get("preferred_machine_type", machine_type)
        default_zone = tool_context.state.get("default_zone", zone)
        
        # Mock VM creation (in real implementation, use Compute Engine API)
        instance_result = {
            "name": name,
            "zone": zone,
            "machineType": preferred_machine_type,
            "status": "RUNNING",
            "id": "1234567890123456789",
            "selfLink": f"https://www.googleapis.com/compute/v1/projects/{project_id}/zones/{zone}/instances/{name}",
            "creationTimestamp": "2025-06-01T12:00:00Z"
        }
        
        # Update session state
        user_instances = tool_context.state.get("user_instances", [])
        instance_info = {
            "name": name,
            "project_id": project_id,
            "zone": zone,
            "machine_type": preferred_machine_type,
            "created_at": "2025-06-01T12:00:00Z"
        }
        user_instances.append(instance_info)
        tool_context.state["user_instances"] = user_instances
        
        tool_context.state["last_vm_operation"] = {
            "operation": "create",
            "instance_name": name,
            "project_id": project_id,
            "zone": zone,
            "timestamp": "2025-06-01T12:00:00Z",
            "status": "success"
        }
        
        return {
            "status": "success",
            "message": f"VM instance '{name}' created successfully",
            "data": {
                "instance": instance_result,
                "estimated_monthly_cost": "$25.00",
                "ssh_command": f"gcloud compute ssh {name} --zone={zone} --project={project_id}"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create VM instance {name}: {str(e)}")
        
        return {
            "status": "error",
            "message": f"Failed to create VM instance: {str(e)}",
            "data": {
                "instance_name": name,
                "error_details": str(e)
            }
        }


async def list_vm_instances(
    project_id: str,
    tool_context: ToolContext,
    zone: Optional[str] = None
) -> Dict[str, Any]:
    """
    List GCP Compute Engine VM instances.
    
    Args:
        project_id: GCP project ID
        tool_context: ADK tool context for state access
        zone: Specific zone to filter by (optional)
        
    Returns:
        Dict containing list of instances
    """
    logger.info(f"Listing VM instances in project: {project_id}")
    
    try:
        # Get user's instances from state
        user_instances = tool_context.state.get("user_instances", [])
        
        # Mock instance list (filter by project and optionally zone)
        instances = []
        for instance in user_instances:
            if instance["project_id"] == project_id:
                if zone is None or instance["zone"] == zone:
                    instances.append({
                        "name": instance["name"],
                        "zone": instance["zone"],
                        "machineType": instance["machine_type"],
                        "status": "RUNNING",
                        "id": "1234567890123456789",
                        "creationTimestamp": instance["created_at"]
                    })
        
        # Update state
        tool_context.state["last_vm_list_count"] = len(instances)
        tool_context.state["last_vm_operation"] = {
            "operation": "list",
            "project_id": project_id,
            "zone": zone,
            "timestamp": "2025-06-01T12:00:00Z",
            "status": "success",
            "count": len(instances)
        }
        
        return {
            "status": "success",
            "message": f"Found {len(instances)} VM instances",
            "data": {
                "instances": instances,
                "total_count": len(instances),
                "project_id": project_id,
                "zone_filter": zone
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to list VM instances: {str(e)}")
        
        return {
            "status": "error",
            "message": f"Failed to list VM instances: {str(e)}",
            "data": {"error_details": str(e)}
        }


async def stop_vm_instance(
    name: str,
    project_id: str,
    zone: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Stop a GCP Compute Engine VM instance.
    
    Args:
        name: Name of the VM instance
        project_id: GCP project ID
        zone: GCP zone
        tool_context: ADK tool context for state access
        
    Returns:
        Dict containing operation status
    """
    logger.info(f"Stopping VM instance: {name}")
    
    try:
        # Mock stopping instance
        stop_result = {
            "name": name,
            "zone": zone,
            "status": "STOPPING",
            "operationType": "stop",
            "targetId": "1234567890123456789"
        }
        
        # Update session state
        tool_context.state["last_vm_operation"] = {
            "operation": "stop",
            "instance_name": name,
            "project_id": project_id,
            "zone": zone,
            "timestamp": "2025-06-01T12:00:00Z",
            "status": "success"
        }
        
        return {
            "status": "success",
            "message": f"VM instance '{name}' is stopping",
            "data": {
                "operation": stop_result,
                "estimated_stop_time": "30-60 seconds"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to stop VM instance {name}: {str(e)}")
        
        return {
            "status": "error",
            "message": f"Failed to stop VM instance: {str(e)}",
            "data": {
                "instance_name": name,
                "error_details": str(e)
            }
        }


class ComputeTools:
    """GCP Compute Engine tools wrapper class."""
    
    @staticmethod
    async def create_vm_instance(
        name: str,
        project_id: str,
        zone: str,
        tool_context: ToolContext,
        machine_type: str = "e2-medium",
        image_family: str = "ubuntu-2004-lts",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new GCP Compute Engine VM instance."""
        return await create_vm_instance(
            name=name,
            project_id=project_id,
            zone=zone,
            tool_context=tool_context,
            machine_type=machine_type,
            image_family=image_family,
            **kwargs
        )
    
    @staticmethod
    async def list_vm_instances(
        project_id: str,
        tool_context: ToolContext,
        zone: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """List VM instances in a project or zone."""
        return await list_vm_instances(
            project_id=project_id,
            tool_context=tool_context,
            zone=zone,
            **kwargs
        )
    
    @staticmethod
    async def stop_vm_instance(
        name: str,
        project_id: str,
        zone: str,
        tool_context: ToolContext,
        **kwargs
    ) -> Dict[str, Any]:
        """Stop a running VM instance."""
        return await stop_vm_instance(
            name=name,
            project_id=project_id,
            zone=zone,
            tool_context=tool_context,
            **kwargs
        )
