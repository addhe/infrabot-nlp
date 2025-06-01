"""ADK Session Service for state management and agent coordination."""

from typing import Dict, List, Optional, Any, Union
import logging
import json
import uuid
from datetime import datetime, timezone
import asyncio

logger = logging.getLogger(__name__)


class ADKSessionService:
    """Session service for managing agent state, memory, and multi-agent coordination."""
    
    def __init__(self):
        """Initialize the session service."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.active_agents: Dict[str, Any] = {}
        self.operation_history: Dict[str, List[Dict[str, Any]]] = {}
        
    def create_session(
        self, 
        user_id: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new session with optional initial context.
        
        Args:
            user_id: Optional user identifier
            initial_context: Initial session context
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "state": initial_context or {},
            "context": {
                "conversation_history": [],
                "tool_usage_history": [],
                "agent_interactions": [],
                "user_preferences": {}
            },
            "memory": {
                "short_term": {},  # Current session memory
                "long_term": {},   # Persistent user preferences
                "working": {}      # Temporary working memory
            }
        }
        
        # Initialize operation history for this session
        self.operation_history[session_id] = []
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        return self.sessions.get(session_id)
    
    def update_session_state(
        self, 
        session_id: str, 
        key: str, 
        value: Any
    ) -> bool:
        """Update session state.
        
        Args:
            session_id: Session identifier
            key: State key to update
            value: New value
            
        Returns:
            True if updated successfully
        """
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        self.sessions[session_id]["state"][key] = value
        self.sessions[session_id]["last_activity"] = datetime.now(timezone.utc).isoformat()
        
        logger.debug(f"Updated session {session_id} state: {key}")
        return True
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get session state.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session state dictionary
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return {}
        
        return session.get("state", {})
    
    def add_to_memory(
        self, 
        session_id: str, 
        memory_type: str, 
        key: str, 
        value: Any
    ) -> bool:
        """Add data to session memory.
        
        Args:
            session_id: Session identifier
            memory_type: Type of memory (short_term, long_term, working)
            key: Memory key
            value: Value to store
            
        Returns:
            True if added successfully
        """
        if session_id not in self.sessions:
            return False
        
        if memory_type not in self.sessions[session_id]["memory"]:
            logger.warning(f"Invalid memory type: {memory_type}")
            return False
        
        self.sessions[session_id]["memory"][memory_type][key] = value
        self.sessions[session_id]["last_activity"] = datetime.now(timezone.utc).isoformat()
        
        logger.debug(f"Added to {memory_type} memory in session {session_id}: {key}")
        return True
    
    def get_from_memory(
        self, 
        session_id: str, 
        memory_type: str, 
        key: str, 
        default: Any = None
    ) -> Any:
        """Get data from session memory.
        
        Args:
            session_id: Session identifier
            memory_type: Type of memory
            key: Memory key
            default: Default value if not found
            
        Returns:
            Stored value or default
        """
        session = self.sessions.get(session_id)
        if not session:
            return default
        
        memory = session.get("memory", {}).get(memory_type, {})
        return memory.get(key, default)
    
    def record_operation(
        self, 
        session_id: str, 
        operation: Dict[str, Any]
    ) -> bool:
        """Record an operation in session history.
        
        Args:
            session_id: Session identifier
            operation: Operation details
            
        Returns:
            True if recorded successfully
        """
        if session_id not in self.operation_history:
            self.operation_history[session_id] = []
        
        # Add timestamp if not present
        if "timestamp" not in operation:
            operation["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        self.operation_history[session_id].append(operation)
        
        # Also add to session context
        if session_id in self.sessions:
            self.sessions[session_id]["context"]["tool_usage_history"].append(operation)
            self.sessions[session_id]["last_activity"] = datetime.now(timezone.utc).isoformat()
        
        logger.debug(f"Recorded operation in session {session_id}: {operation.get('operation_type', 'unknown')}")
        return True
    
    def get_operation_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get operation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Optional limit on number of operations to return
            
        Returns:
            List of operations
        """
        history = self.operation_history.get(session_id, [])
        
        if limit:
            return history[-limit:]
        return history
    
    def register_agent(self, agent_name: str, agent_instance: Any) -> bool:
        """Register an agent with the session service.
        
        Args:
            agent_name: Name of the agent
            agent_instance: Agent instance
            
        Returns:
            True if registered successfully
        """
        self.active_agents[agent_name] = {
            "instance": agent_instance,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "type": getattr(agent_instance, "specialization", "generic"),
            "status": "active"
        }
        
        logger.info(f"Registered agent: {agent_name}")
        return True
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """Get a registered agent by name.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent instance or None
        """
        agent_info = self.active_agents.get(agent_name)
        if agent_info:
            return agent_info["instance"]
        return None
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all registered agents.
        
        Returns:
            Dictionary of agent information
        """
        return {
            name: {
                "type": info["type"],
                "status": info["status"],
                "registered_at": info["registered_at"]
            }
            for name, info in self.active_agents.items()
        }
    
    async def coordinate_agents(
        self, 
        session_id: str, 
        request: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Coordinate multiple agents for complex requests.
        
        Args:
            session_id: Session identifier
            request: User request
            context: Additional context
            
        Returns:
            Coordination result
        """
        try:
            coordination_result = {
                "session_id": session_id,
                "request": request,
                "agents_involved": [],
                "coordination_plan": {},
                "execution_result": {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Get the root agent for delegation
            root_agent = self.get_agent("gcp-root-agent")
            if not root_agent:
                logger.error("Root agent not found for coordination")
                return {
                    "error": "Root agent not available",
                    "status": "failed"
                }
            
            # Use root agent's delegation logic
            if hasattr(root_agent, "route_request"):
                routing_decision = await root_agent.route_request(request, context)
                coordination_result["coordination_plan"] = routing_decision
                
                # Execute through the root agent's delegation
                if hasattr(root_agent, "execute_delegated_request"):
                    result = await root_agent.execute_delegated_request(request, context)
                    coordination_result["execution_result"] = result
                    coordination_result["status"] = "success"
                else:
                    # Fallback to direct execution
                    result = await root_agent.run(request, context)
                    coordination_result["execution_result"] = result
                    coordination_result["status"] = "success"
            
            # Record the coordination operation
            self.record_operation(session_id, {
                "operation_type": "agent_coordination",
                "request": request,
                "agents_involved": coordination_result["agents_involved"],
                "status": coordination_result.get("status", "unknown")
            })
            
            return coordination_result
            
        except Exception as e:
            logger.error(f"Error in agent coordination: {str(e)}")
            return {
                "session_id": session_id,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up a session and its associated data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if cleaned up successfully
        """
        try:
            # Remove session data
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            # Remove operation history
            if session_id in self.operation_history:
                del self.operation_history[session_id]
            
            logger.info(f"Cleaned up session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {str(e)}")
            return False
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of session activity.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        operations = self.operation_history.get(session_id, [])
        
        return {
            "session_id": session_id,
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "total_operations": len(operations),
            "operation_types": list(set(op.get("operation_type", "unknown") for op in operations)),
            "state_keys": list(session["state"].keys()),
            "memory_usage": {
                "short_term": len(session["memory"]["short_term"]),
                "long_term": len(session["memory"]["long_term"]),
                "working": len(session["memory"]["working"])
            },
            "user_preferences": session["context"]["user_preferences"]
        }
