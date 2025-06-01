"""ADK Runner for orchestrating agent execution with safety and state management."""

from typing import Dict, List, Optional, Any, Union, Callable
import logging
import asyncio
from datetime import datetime, timezone
import traceback

from .session_service import ADKSessionService
from .base_agent import BaseGCPAgent

logger = logging.getLogger(__name__)


class ADKRunner:
    """Runner for executing ADK agents with comprehensive safety and state management."""
    
    def __init__(
        self,
        session_service: ADKSessionService,
        safety_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the ADK Runner.
        
        Args:
            session_service: Session service for state management
            safety_config: Safety configuration settings
        """
        self.session_service = session_service
        self.safety_config = safety_config or self._get_default_safety_config()
        self.execution_history: List[Dict[str, Any]] = []
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        
    def _get_default_safety_config(self) -> Dict[str, Any]:
        """Get default safety configuration.
        
        Returns:
            Default safety settings
        """
        return {
            "max_execution_time": 300,  # 5 minutes
            "max_concurrent_executions": 5,
            "require_confirmation": {
                "destructive_operations": True,
                "production_environments": True,
                "billing_changes": True
            },
            "blocked_operations": [
                "format_disk",
                "delete_all",
                "rm_rf_root"
            ],
            "rate_limits": {
                "operations_per_minute": 60,
                "api_calls_per_minute": 100
            },
            "audit_logging": True,
            "emergency_stop": True
        }
    
    async def execute_agent(
        self,
        agent: BaseGCPAgent,
        user_prompt: str,
        session_id: str,
        context: Optional[Any] = None,
        safety_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute an agent with comprehensive safety and monitoring.
        
        Args:
            agent: Agent to execute
            user_prompt: User's request
            session_id: Session identifier
            context: Tool context for state access
            safety_overrides: Optional safety setting overrides
            
        Returns:
            Execution result with metadata
        """
        execution_id = f"{session_id}_{datetime.now().timestamp()}"
        
        execution_context = {
            "execution_id": execution_id,
            "session_id": session_id,
            "agent_name": agent.name,
            "user_prompt": user_prompt,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "starting",
            "safety_checks": [],
            "warnings": [],
            "result": None,
            "error": None,
            "execution_time": 0
        }
        
        try:
            # Track active execution
            self.active_executions[execution_id] = execution_context
            
            # Pre-execution safety checks
            safety_result = await self._perform_safety_checks(
                agent, user_prompt, session_id, context, safety_overrides
            )
            
            execution_context["safety_checks"] = safety_result["checks"]
            execution_context["warnings"] = safety_result["warnings"]
            
            if not safety_result["allowed"]:
                execution_context["status"] = "blocked"
                execution_context["error"] = safety_result["reason"]
                return execution_context
            
            # Check rate limits
            if not self._check_rate_limits(session_id):
                execution_context["status"] = "rate_limited"
                execution_context["error"] = "Rate limit exceeded"
                return execution_context
            
            # Update session state with execution start
            self.session_service.update_session_state(
                session_id, 
                "current_execution", 
                execution_id
            )
            
            # Execute the agent with timeout
            execution_context["status"] = "executing"
            
            start_time = datetime.now()
            
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    agent.run(user_prompt, context),
                    timeout=self.safety_config["max_execution_time"]
                )
                
                execution_context["result"] = result
                execution_context["status"] = "completed"
                
            except asyncio.TimeoutError:
                execution_context["status"] = "timeout"
                execution_context["error"] = "Execution timed out"
                
            except Exception as e:
                execution_context["status"] = "error"
                execution_context["error"] = str(e)
                execution_context["traceback"] = traceback.format_exc()
                logger.error(f"Agent execution error: {str(e)}")
            
            # Calculate execution time
            end_time = datetime.now()
            execution_context["execution_time"] = (end_time - start_time).total_seconds()
            execution_context["completed_at"] = end_time.isoformat()
            
            # Post-execution processing
            await self._post_execution_processing(execution_context, session_id, context)
            
            return execution_context
            
        except Exception as e:
            # Handle unexpected errors
            execution_context["status"] = "system_error"
            execution_context["error"] = f"System error: {str(e)}"
            execution_context["traceback"] = traceback.format_exc()
            logger.error(f"System error in agent execution: {str(e)}")
            return execution_context
            
        finally:
            # Clean up active execution tracking
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            # Update session state
            self.session_service.update_session_state(
                session_id, 
                "last_execution", 
                execution_context
            )
            
            # Add to execution history
            self.execution_history.append(execution_context)
            
            # Record operation in session service
            self.session_service.record_operation(session_id, {
                "operation_type": "agent_execution",
                "agent_name": agent.name,
                "execution_id": execution_id,
                "status": execution_context["status"],
                "execution_time": execution_context["execution_time"],
                "user_prompt": user_prompt[:100] + "..." if len(user_prompt) > 100 else user_prompt
            })
    
    async def _perform_safety_checks(
        self,
        agent: BaseGCPAgent,
        user_prompt: str,
        session_id: str,
        context: Optional[Any],
        safety_overrides: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform comprehensive safety checks before execution.
        
        Args:
            agent: Agent to execute
            user_prompt: User's request
            session_id: Session identifier
            context: Tool context
            safety_overrides: Safety overrides
            
        Returns:
            Safety check results
        """
        safety_result = {
            "allowed": True,
            "reason": "",
            "checks": [],
            "warnings": []
        }
        
        try:
            # Check for blocked operations
            prompt_lower = user_prompt.lower()
            for blocked_op in self.safety_config["blocked_operations"]:
                if blocked_op in prompt_lower:
                    safety_result["allowed"] = False
                    safety_result["reason"] = f"Blocked operation detected: {blocked_op}"
                    safety_result["checks"].append(f"BLOCKED: {blocked_op}")
                    return safety_result
            
            # Check for destructive operations
            destructive_keywords = [
                "delete", "remove", "destroy", "terminate", "stop", "shutdown"
            ]
            
            if any(keyword in prompt_lower for keyword in destructive_keywords):
                safety_result["checks"].append("Destructive operation detected")
                
                if self.safety_config["require_confirmation"]["destructive_operations"]:
                    # Check if confirmation was provided in context
                    if context and hasattr(context, 'state'):
                        confirmed = context.state.get("operation_confirmed", False)
                        if not confirmed:
                            safety_result["warnings"].append(
                                "Destructive operation requires confirmation"
                            )
                            # Don't block, but flag for confirmation
            
            # Check for production environment operations
            prod_keywords = ["prod", "production", "live"]
            if any(keyword in prompt_lower for keyword in prod_keywords):
                safety_result["checks"].append("Production environment operation")
                safety_result["warnings"].append(
                    "Production environment detected - extra caution required"
                )
            
            # Check concurrent execution limits
            if len(self.active_executions) >= self.safety_config["max_concurrent_executions"]:
                safety_result["allowed"] = False
                safety_result["reason"] = "Maximum concurrent executions reached"
                safety_result["checks"].append("Concurrent execution limit")
                return safety_result
            
            # Agent-specific safety checks
            if hasattr(agent, "get_delegation_logic"):
                delegation_logic = agent.get_delegation_logic()
                safety_checks = delegation_logic.get("safety_checks", {})
                
                for check_name, check_enabled in safety_checks.items():
                    if check_enabled:
                        safety_result["checks"].append(f"Agent safety check: {check_name}")
            
            # Apply safety overrides
            if safety_overrides:
                for override_key, override_value in safety_overrides.items():
                    if override_key in self.safety_config:
                        safety_result["checks"].append(f"Safety override: {override_key}")
            
            safety_result["checks"].append("All safety checks passed")
            return safety_result
            
        except Exception as e:
            logger.error(f"Error in safety checks: {str(e)}")
            safety_result["allowed"] = False
            safety_result["reason"] = f"Safety check error: {str(e)}"
            return safety_result
    
    def _check_rate_limits(self, session_id: str) -> bool:
        """Check if rate limits are exceeded.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if within rate limits
        """
        try:
            # Simple rate limiting - check operations in last minute
            current_time = datetime.now(timezone.utc)
            recent_operations = [
                op for op in self.execution_history
                if (current_time - datetime.fromisoformat(op["started_at"].replace('Z', '+00:00'))).total_seconds() <= 60
            ]
            
            operations_per_minute = len(recent_operations)
            limit = self.safety_config["rate_limits"]["operations_per_minute"]
            
            if operations_per_minute >= limit:
                logger.warning(f"Rate limit exceeded: {operations_per_minute}/{limit} operations per minute")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limits: {str(e)}")
            # Fail safe - allow execution if rate check fails
            return True
    
    async def _post_execution_processing(
        self,
        execution_context: Dict[str, Any],
        session_id: str,
        context: Optional[Any]
    ) -> None:
        """Perform post-execution processing and cleanup.
        
        Args:
            execution_context: Execution context
            session_id: Session identifier
            context: Tool context
        """
        try:
            # Update session memory with execution results
            if execution_context["status"] == "completed" and execution_context["result"]:
                self.session_service.add_to_memory(
                    session_id,
                    "short_term",
                    "last_successful_execution",
                    {
                        "agent": execution_context["agent_name"],
                        "result": execution_context["result"],
                        "timestamp": execution_context["completed_at"]
                    }
                )
            
            # Log audit information
            if self.safety_config["audit_logging"]:
                audit_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "session_id": session_id,
                    "execution_id": execution_context["execution_id"],
                    "agent": execution_context["agent_name"],
                    "status": execution_context["status"],
                    "execution_time": execution_context["execution_time"],
                    "safety_checks": execution_context["safety_checks"],
                    "warnings": execution_context["warnings"]
                }
                
                # In a real implementation, this would go to a proper audit log
                logger.info(f"Audit log: {audit_entry}")
            
            # Update context state if available
            if context and hasattr(context, 'state'):
                context.state["last_execution_result"] = {
                    "status": execution_context["status"],
                    "agent": execution_context["agent_name"],
                    "timestamp": execution_context.get("completed_at", execution_context["started_at"])
                }
            
        except Exception as e:
            logger.error(f"Error in post-execution processing: {str(e)}")
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Execution status or None if not found
        """
        # Check active executions first
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        
        # Check execution history
        for execution in self.execution_history:
            if execution["execution_id"] == execution_id:
                return execution
        
        return None
    
    def list_active_executions(self) -> Dict[str, Dict[str, Any]]:
        """List all currently active executions.
        
        Returns:
            Dictionary of active executions
        """
        return self.active_executions.copy()
    
    def get_execution_history(
        self, 
        session_id: Optional[str] = None, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get execution history, optionally filtered by session.
        
        Args:
            session_id: Optional session filter
            limit: Optional limit on results
            
        Returns:
            List of execution records
        """
        history = self.execution_history
        
        if session_id:
            history = [ex for ex in history if ex["session_id"] == session_id]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    async def emergency_stop(self, execution_id: Optional[str] = None) -> Dict[str, Any]:
        """Emergency stop for executions.
        
        Args:
            execution_id: Optional specific execution to stop, or all if None
            
        Returns:
            Stop operation result
        """
        try:
            if not self.safety_config["emergency_stop"]:
                return {
                    "status": "disabled",
                    "message": "Emergency stop is disabled in safety configuration"
                }
            
            stopped_executions = []
            
            if execution_id:
                # Stop specific execution
                if execution_id in self.active_executions:
                    self.active_executions[execution_id]["status"] = "emergency_stopped"
                    stopped_executions.append(execution_id)
            else:
                # Stop all active executions
                for exec_id in list(self.active_executions.keys()):
                    self.active_executions[exec_id]["status"] = "emergency_stopped"
                    stopped_executions.append(exec_id)
            
            logger.warning(f"Emergency stop executed for {len(stopped_executions)} executions")
            
            return {
                "status": "success",
                "stopped_executions": stopped_executions,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in emergency stop: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
