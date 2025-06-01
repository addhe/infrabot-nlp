"""Root agent for GCP infrastructure management with delegation capabilities."""

from typing import Dict, List, Optional, Callable, Any
import logging
from ..base.base_agent import BaseGCPAgent, SpecializedGCPAgent
from ..tools.project_tools import create_gcp_project, list_gcp_projects, delete_gcp_project
from ..tools.compute_tools import create_vm_instance, list_vm_instances, stop_vm_instance

logger = logging.getLogger(__name__)


class RootGCPAgent(BaseGCPAgent):
    """Root agent that coordinates GCP infrastructure operations and delegates to specialized agents."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        **kwargs
    ):
        """Initialize the root GCP agent.
        
        Args:
            model: Model to use (supports LiteLLM format)
            **kwargs: Additional arguments for base class
        """
        
        # Comprehensive instruction for the root agent
        instruction = """
You are the Root GCP Infrastructure Agent with comprehensive knowledge of Google Cloud Platform.

**Primary Responsibilities:**
1. **Multi-Service Coordination**: Handle complex requests spanning multiple GCP services
2. **Agent Delegation**: Route specialized requests to appropriate sub-agents
3. **Architecture Guidance**: Provide high-level infrastructure design recommendations
4. **Safety Oversight**: Ensure all operations follow GCP best practices and security guidelines

**Service Areas You Manage:**
- **Projects**: Creation, management, and organization of GCP projects
- **Compute**: VM instances, machine types, zones, and compute resources
- **Networking**: VPCs, firewalls, load balancers, and connectivity
- **Storage**: Cloud Storage, persistent disks, and data management
- **Security**: IAM, service accounts, and access control

**Delegation Strategy:**
- Route project-specific requests to Project Agent
- Route compute operations to Compute Agent  
- Route networking tasks to Network Agent
- Handle cross-service architecture decisions yourself
- Escalate to human operators for production-critical changes

**Safety Guidelines:**
- Always check session state for user preferences and project context
- Confirm destructive operations (delete, stop, terminate)
- Validate resource configurations against GCP best practices
- Warn about security implications and cost considerations
- Use appropriate machine types and regions based on user preferences

**Session State Management:**
- Track user's default regions, projects, and preferences
- Remember previous operations and their outcomes
- Maintain operation history for audit and rollback purposes
- Store learned user patterns for better recommendations

Always start by checking the current session state to understand the user's context and preferences.
"""
        
        # Initialize basic tools that the root agent can handle directly
        tools = [
            create_gcp_project,
            list_gcp_projects,
            delete_gcp_project,
            create_vm_instance,
            list_vm_instances,
            stop_vm_instance,
        ]
        
        super().__init__(
            name="gcp_root_agent",
            model=model,
            description="Root GCP agent for infrastructure management and delegation",
            instruction=instruction.strip(),
            tools=tools,
            **kwargs
        )
        
        # Initialize specialized agents
        self.sub_agents: Dict[str, SpecializedGCPAgent] = {}
        self._initialize_sub_agents()
    
    def _initialize_sub_agents(self) -> None:
        """Initialize specialized sub-agents."""
        try:
            # Import specialized agents
            from .project_agent import ProjectAgent
            from .compute_agent import ComputeAgent
            
            # Create specialized agents with debugging
            logger.info("Creating ProjectAgent...")
            project_agent = ProjectAgent()
            logger.info(f"ProjectAgent created: {type(project_agent)} - {project_agent.__class__.__name__}")
            logger.info(f"ProjectAgent has run method: {hasattr(project_agent, 'run')}")
            self.sub_agents["project"] = project_agent
            
            logger.info("Creating ComputeAgent...")
            compute_agent = ComputeAgent()
            logger.info(f"ComputeAgent created: {type(compute_agent)} - {compute_agent.__class__.__name__}")
            logger.info(f"ComputeAgent has run method: {hasattr(compute_agent, 'run')}")
            self.sub_agents["compute"] = compute_agent
            
            logger.info(f"Initialized {len(self.sub_agents)} specialized agents")
            
            # Debug sub_agents dictionary
            for name, agent in self.sub_agents.items():
                logger.info(f"sub_agents['{name}'] = {type(agent)} with methods: {[m for m in dir(agent) if not m.startswith('_')]}")
            
        except ImportError as e:
            logger.warning(f"Could not initialize some specialized agents: {e}")
        except Exception as e:
            logger.error(f"Error initializing specialized agents: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def get_delegation_logic(self) -> Dict[str, Any]:
        """Return delegation logic for the root agent.
        
        Returns:
            Delegation rules and routing information
        """
        return {
            "agent_type": "root",
            "delegation_rules": {
                "project_operations": {
                    "agent": "project",
                    "keywords": ["project", "create project", "list projects", "delete project"],
                    "operations": ["create_gcp_project", "list_gcp_projects", "delete_gcp_project"]
                },
                "compute_operations": {
                    "agent": "compute", 
                    "keywords": ["vm", "instance", "compute", "machine", "server"],
                    "operations": ["create_vm_instance", "list_vm_instances", "stop_vm_instance"]
                },
                "multi_service": {
                    "agent": "root",
                    "keywords": ["architecture", "design", "setup", "infrastructure"],
                    "operations": ["complex_setup", "architecture_guidance", "cross_service"]
                }
            },
            "escalation_triggers": [
                "production_operations",
                "delete_operations",
                "security_changes",
                "billing_changes"
            ],
            "safety_checks": {
                "confirm_destructive": True,
                "validate_resources": True,
                "check_costs": True,
                "audit_logging": True
            }
        }
    
    async def route_request(
        self, 
        user_prompt: str, 
        context: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Route user request to appropriate agent.
        
        Args:
            user_prompt: User's request
            context: Tool context for state access
            
        Returns:
            Routing decision and target agent
        """
        try:
            # Analyze the request to determine routing
            prompt_lower = user_prompt.lower()
            delegation_logic = self.get_delegation_logic()
            
            # Check for specific operation patterns
            for operation_type, rules in delegation_logic["delegation_rules"].items():
                # Check keywords
                if any(keyword in prompt_lower for keyword in rules["keywords"]):
                    target_agent = rules["agent"]
                    
                    # If routing to self (root), handle directly
                    if target_agent == "root":
                        return {
                            "route_to": "root",
                            "target_agent": self,
                            "operation_type": operation_type,
                            "reasoning": f"Complex {operation_type} requires root agent coordination"
                        }
                    
                    # Route to specialized agent if available
                    if target_agent in self.sub_agents:
                        return {
                            "route_to": target_agent,
                            "target_agent": self.sub_agents[target_agent],
                            "operation_type": operation_type,
                            "reasoning": f"Routing {operation_type} to specialized {target_agent} agent"
                        }
            
            # Default to root agent for unmatched requests
            return {
                "route_to": "root",
                "target_agent": self,
                "operation_type": "general",
                "reasoning": "Unmatched request, handling with root agent"
            }
            
        except Exception as e:
            logger.error(f"Error in request routing: {str(e)}")
            # Fallback to root agent
            return {
                "route_to": "root",
                "target_agent": self,
                "operation_type": "error_fallback",
                "reasoning": f"Error in routing, fallback to root: {str(e)}"
            }
    
    async def execute_delegated_request(
        self,
        user_prompt: str,
        context: Optional[Any] = None
    ) -> Any:
        """Execute a request with proper delegation.
        
        Args:
            user_prompt: User's request
            context: Tool context for state access
            
        Returns:
            Result from the appropriate agent
        """
        try:
            # Route the request
            routing_decision = await self.route_request(user_prompt, context)
            target_agent = routing_decision["target_agent"]
            operation_type = routing_decision["operation_type"]
            
            logger.info(f"Routing request to {routing_decision['route_to']} agent: {routing_decision['reasoning']}")
            
            # Check for escalation triggers
            delegation_logic = self.get_delegation_logic()
            prompt_lower = user_prompt.lower()
            
            for trigger in delegation_logic["escalation_triggers"]:
                if trigger.replace("_", " ") in prompt_lower:
                    logger.warning(f"Escalation trigger detected: {trigger}")
                    # Add safety confirmation for sensitive operations
                    if context and hasattr(context, 'state'):
                        context.state["requires_confirmation"] = True
                        context.state["escalation_reason"] = trigger
            
            # Execute with the target agent
            if target_agent == self:
                # Execute directly with root agent - need to implement proper execution
                # For now, return a placeholder response
                result = f"Root agent handling: {user_prompt}"
            else:
                # Debug the target agent before execution
                logger.info(f"About to execute with target_agent: {type(target_agent)} - {target_agent.__class__.__name__}")
                logger.info(f"target_agent has run method: {hasattr(target_agent, 'run')}")
                logger.info(f"target_agent methods: {[m for m in dir(target_agent) if not m.startswith('_') and callable(getattr(target_agent, m))]}")
                
                # Execute with specialized agent using the correct method
                result = await target_agent.run(user_prompt, context)
            
            # Log successful delegation
            if context and hasattr(context, 'state'):
                context.state["last_delegation"] = {
                    "target_agent": routing_decision["route_to"],
                    "operation_type": operation_type,
                    "timestamp": "2025-06-01T12:00:00Z",
                    "status": "success"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in delegated execution: {str(e)}")
            
            # Update state with error
            if context and hasattr(context, 'state'):
                context.state["last_delegation"] = {
                    "target_agent": "error",
                    "operation_type": "failed",
                    "timestamp": "2025-06-01T12:00:00Z",
                    "status": "error",
                    "error": str(e)
                }
            
            raise
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of root agent and all sub-agents.
        
        Returns:
            Status information for all agents
        """
        status = {
            "root_agent": self.get_info(),
            "sub_agents": {},
            "delegation_logic": self.get_delegation_logic(),
            "total_agents": 1 + len(self.sub_agents)
        }
        
        # Get status from all sub-agents
        for agent_name, agent in self.sub_agents.items():
            try:
                status["sub_agents"][agent_name] = agent.get_info()
            except Exception as e:
                status["sub_agents"][agent_name] = {
                    "error": str(e),
                    "status": "unavailable"
                }
        
        return status