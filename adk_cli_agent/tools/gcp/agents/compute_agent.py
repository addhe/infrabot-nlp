"""Specialized GCP Compute Agent for VM and compute resource management."""

from typing import Dict, List, Optional, Callable, Any
import logging
from ..base.base_agent import SpecializedGCPAgent
from ..tools.compute_tools import create_vm_instance, list_vm_instances, stop_vm_instance

logger = logging.getLogger(__name__)


class ComputeAgent(SpecializedGCPAgent):
    """Specialized agent for GCP compute operations and VM management."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        **kwargs
    ):
        """Initialize the GCP Compute Agent.
        
        Args:
            model: Model to use (supports LiteLLM format)
            **kwargs: Additional arguments for base class
        """
        
        # Specialized instruction for compute management
        instruction = """
You are the GCP Compute Engine Specialist with deep expertise in virtual machines and compute resources.

**Core Expertise:**
- **VM Instance Management**: Create, configure, start, stop, and delete VM instances
- **Machine Type Selection**: Recommend optimal machine types based on workload requirements
- **Zone and Region Planning**: Guide users on geographic placement and availability zones
- **Image and Disk Management**: Handle OS images, custom images, and persistent disk configuration
- **Network Configuration**: Set up VM networking, firewall rules, and load balancing
- **Performance Optimization**: Monitor and optimize compute resource utilization

**Best Practices You Follow:**
1. **Cost Optimization**: Recommend appropriate machine types and preemptible instances
2. **Security Hardening**: Apply security best practices for VM configuration
3. **High Availability**: Design for fault tolerance and disaster recovery
4. **Monitoring Setup**: Configure logging and monitoring for compute resources
5. **Capacity Planning**: Plan for scaling and resource growth

**Machine Type Expertise:**
- **General Purpose**: E2, N1, N2, N2D for balanced workloads
- **Compute Optimized**: C2, C2D for CPU-intensive applications
- **Memory Optimized**: M1, M2 for memory-intensive workloads
- **Custom Machine Types**: Tailored configurations for specific needs

**Safety Protocols:**
- Confirm instance operations that affect running workloads
- Validate zone availability and resource quotas
- Check for dependent services before stopping instances
- Warn about data loss risks with ephemeral storage
- Verify backup strategies for persistent data

**Session Awareness:**
- Remember user's preferred zones and machine types
- Track instance creation patterns and naming conventions
- Store workload-specific configurations for reuse
- Maintain history of compute operations and optimizations

Always check session state for user preferences on machine types, zones, and configuration patterns.
"""
        
        # Register compute-specific tools
        tools = [
            create_vm_instance,
            list_vm_instances,
            stop_vm_instance,
        ]
        
        super().__init__(
            name="gcp_compute_agent",
            specialization="compute",
            model=model,
            description="Specialized GCP agent for compute engine and VM management",
            instruction=instruction.strip(),
            tools=tools,
            **kwargs
        )
    
    def get_delegation_logic(self) -> Dict[str, Any]:
        """Return delegation logic specific to compute management.
        
        Returns:
            Compute-specific delegation rules
        """
        base_logic = super().get_delegation_logic()
        
        # Extend with compute-specific logic
        base_logic.update({
            "specialized_operations": {
                "instance_creation": {
                    "operations": ["create_vm_instance"],
                    "prerequisites": ["machine_type", "zone", "image"],
                    "safety_checks": ["quota_validation", "zone_availability", "network_setup"]
                },
                "instance_management": {
                    "operations": ["list_vm_instances", "stop_vm_instance"],
                    "filters": ["zone", "status", "labels", "machine_type"],
                    "safety_checks": ["workload_impact", "data_preservation"]
                },
                "capacity_planning": {
                    "operations": ["recommend_machine_type", "estimate_costs"],
                    "considerations": ["workload_type", "performance_requirements", "budget"]
                }
            },
            "expertise_areas": [
                "vm_lifecycle",
                "machine_type_selection",
                "zone_placement",
                "performance_tuning",
                "cost_optimization",
                "security_hardening"
            ],
            "workload_patterns": {
                "web_servers": {
                    "recommended_types": ["e2-medium", "n1-standard-1"],
                    "considerations": ["load_balancing", "auto_scaling"]
                },
                "databases": {
                    "recommended_types": ["n2-highmem-2", "m1-megamem-96"],
                    "considerations": ["persistent_disks", "backup_strategy"]
                },
                "batch_processing": {
                    "recommended_types": ["c2-standard-4", "preemptible"],
                    "considerations": ["fault_tolerance", "cost_efficiency"]
                }
            }
        })
        
        return base_logic
    
    async def recommend_machine_type(
        self,
        workload_type: str,
        performance_requirements: Dict[str, Any],
        context: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Recommend optimal machine type based on workload characteristics.
        
        Args:
            workload_type: Type of workload (web, database, batch, etc.)
            performance_requirements: CPU, memory, and other requirements
            context: Tool context for state access
            
        Returns:
            Machine type recommendations with reasoning
        """
        try:
            recommendations = {
                "workload_type": workload_type,
                "primary_recommendation": {},
                "alternatives": [],
                "cost_analysis": {},
                "reasoning": []
            }
            
            # Get workload patterns from delegation logic
            delegation_logic = self.get_delegation_logic()
            workload_patterns = delegation_logic.get("workload_patterns", {})
            
            # Check for specific workload pattern
            if workload_type in workload_patterns:
                pattern = workload_patterns[workload_type]
                recommendations["primary_recommendation"] = {
                    "machine_type": pattern["recommended_types"][0],
                    "considerations": pattern["considerations"]
                }
                recommendations["alternatives"] = [
                    {"machine_type": mt, "use_case": f"Alternative for {workload_type}"}
                    for mt in pattern["recommended_types"][1:]
                ]
            else:
                # General recommendations based on requirements
                cpu_cores = performance_requirements.get("cpu_cores", 1)
                memory_gb = performance_requirements.get("memory_gb", 4)
                
                if memory_gb / cpu_cores > 6:
                    # Memory-intensive workload
                    recommendations["primary_recommendation"] = {
                        "machine_type": "n2-highmem-2",
                        "reasoning": "High memory-to-CPU ratio detected"
                    }
                elif cpu_cores > 4:
                    # CPU-intensive workload
                    recommendations["primary_recommendation"] = {
                        "machine_type": "c2-standard-4",
                        "reasoning": "High CPU requirements detected"
                    }
                else:
                    # Balanced workload
                    recommendations["primary_recommendation"] = {
                        "machine_type": "e2-standard-2",
                        "reasoning": "Balanced CPU and memory requirements"
                    }
            
            # Check session state for user preferences
            if context and hasattr(context, 'state'):
                user_preferences = context.state.get("user_preferences", {})
                preferred_series = user_preferences.get("preferred_machine_series")
                
                if preferred_series:
                    recommendations["reasoning"].append(
                        f"Considering user preference for {preferred_series} series"
                    )
                
                # Store recommendation in session for future reference
                context.state["last_machine_type_recommendation"] = recommendations
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating machine type recommendation: {str(e)}")
            return {
                "workload_type": workload_type,
                "error": str(e),
                "fallback_recommendation": {
                    "machine_type": "e2-medium",
                    "reasoning": "Safe default due to recommendation error"
                }
            }
    
    async def validate_compute_operation(
        self,
        operation: str,
        instance_name: str,
        zone: str,
        context: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Validate compute operations before execution.
        
        Args:
            operation: Type of operation (create, stop, delete, etc.)
            instance_name: Target instance name
            zone: Target zone
            context: Tool context for state access
            
        Returns:
            Validation result with safety recommendations
        """
        try:
            validation_result = {
                "operation": operation,
                "instance_name": instance_name,
                "zone": zone,
                "valid": True,
                "warnings": [],
                "recommendations": [],
                "safety_checks": []
            }
            
            # Check session state for operation history
            if context and hasattr(context, 'state'):
                compute_operations = context.state.get("compute_operations_history", [])
                user_preferences = context.state.get("user_preferences", {})
                
                # Validation based on operation type
                if operation == "create":
                    # Check for naming conflicts
                    existing_instances = [op.get("instance_name") for op in compute_operations 
                                        if op.get("operation") == "create"]
                    if instance_name in existing_instances:
                        validation_result["warnings"].append(
                            f"Instance name {instance_name} was used before in this session"
                        )
                    
                    # Validate zone against user preferences
                    preferred_zone = user_preferences.get("default_zone")
                    if preferred_zone and zone != preferred_zone:
                        validation_result["recommendations"].append(
                            f"Consider using preferred zone {preferred_zone}"
                        )
                
                elif operation == "stop":
                    # Safety checks for stopping instances
                    validation_result["safety_checks"].extend([
                        "Verify no critical workloads are running",
                        "Check for unsaved data or active connections",
                        "Confirm stop vs. delete intention",
                        "Consider maintenance window timing"
                    ])
                
                elif operation == "delete":
                    # Enhanced safety for deletion
                    validation_result["safety_checks"].extend([
                        "IRREVERSIBLE: Confirm instance deletion",
                        "Backup any data on local SSDs",
                        "Verify persistent disks are configured correctly",
                        "Check for dependent services or load balancers"
                    ])
                    validation_result["warnings"].append(
                        "Instance deletion is permanent and cannot be undone"
                    )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating compute operation: {str(e)}")
            return {
                "operation": operation,
                "instance_name": instance_name,
                "zone": zone,
                "valid": False,
                "error": str(e),
                "recommendations": ["Manual review required due to validation error"]
            }