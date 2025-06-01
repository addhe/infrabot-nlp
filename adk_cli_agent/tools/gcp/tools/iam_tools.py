"""
IAM Tools for GCP ADK Infrastructure Management.

Provides comprehensive IAM tools for service accounts, IAM policies, roles,
and security management.
"""

import json
import subprocess
from typing import Dict, Any, List, Optional, Union

try:
    from ...base.tool_context import ToolContext
except ImportError:
    # Fallback for development/testing
    class ToolContext:
        def __init__(self):
            pass
        def get_project_id(self):
            return None
        def log_operation(self, operation, details):
            pass


class IAMTools:
    """Tools for GCP IAM operations."""
    
    def __init__(self):
        """Initialize IAM tools."""
        self.context = ToolContext()
    
    # Service Account Management
    def create_service_account(
        self,
        project_id: str,
        account_id: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a service account.
        
        Args:
            project_id: GCP project ID
            account_id: Service account ID (email prefix)
            display_name: Human-readable name for the service account
            description: Description of the service account purpose
            
        Returns:
            Service account creation result
        """
        try:
            cmd = [
                "gcloud", "iam", "service-accounts", "create", account_id,
                "--project", project_id
            ]
            
            if display_name:
                cmd.extend(["--display-name", display_name])
            
            if description:
                cmd.extend(["--description", description])
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "service_account": json.loads(result.stdout) if result.stdout else {},
                "message": f"Service account '{account_id}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create service account: {e.stderr}",
                "command": " ".join(cmd)
            }
    
    def list_service_accounts(self, project_id: str) -> Dict[str, Any]:
        """
        List service accounts in a project.
        
        Args:
            project_id: GCP project ID
            
        Returns:
            List of service accounts
        """
        try:
            cmd = [
                "gcloud", "iam", "service-accounts", "list",
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            accounts = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "service_accounts": accounts,
                "count": len(accounts)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list service accounts: {e.stderr}"
            }
    
    def delete_service_account(self, project_id: str, service_account_email: str) -> Dict[str, Any]:
        """
        Delete a service account.
        
        Args:
            project_id: GCP project ID
            service_account_email: Email of the service account to delete
            
        Returns:
            Deletion result
        """
        try:
            cmd = [
                "gcloud", "iam", "service-accounts", "delete", service_account_email,
                "--project", project_id,
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Service account '{service_account_email}' deleted successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to delete service account: {e.stderr}"
            }
    
    def create_service_account_key(
        self,
        project_id: str,
        service_account_email: str,
        key_file_path: str,
        key_file_type: str = "json"
    ) -> Dict[str, Any]:
        """
        Create a service account key.
        
        Args:
            project_id: GCP project ID
            service_account_email: Email of the service account
            key_file_path: Path to save the key file
            key_file_type: Type of key file (json or p12)
            
        Returns:
            Key creation result
        """
        try:
            cmd = [
                "gcloud", "iam", "service-accounts", "keys", "create", key_file_path,
                "--iam-account", service_account_email,
                "--project", project_id,
                "--key-file-type", key_file_type
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "key_file": key_file_path,
                "message": f"Service account key created for '{service_account_email}'"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create service account key: {e.stderr}"
            }
    
    def list_service_account_keys(self, project_id: str, service_account_email: str) -> Dict[str, Any]:
        """
        List keys for a service account.
        
        Args:
            project_id: GCP project ID
            service_account_email: Email of the service account
            
        Returns:
            List of service account keys
        """
        try:
            cmd = [
                "gcloud", "iam", "service-accounts", "keys", "list",
                "--iam-account", service_account_email,
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            keys = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "keys": keys,
                "count": len(keys)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list service account keys: {e.stderr}"
            }
    
    def delete_service_account_key(
        self,
        project_id: str,
        service_account_email: str,
        key_id: str
    ) -> Dict[str, Any]:
        """
        Delete a service account key.
        
        Args:
            project_id: GCP project ID
            service_account_email: Email of the service account
            key_id: ID of the key to delete
            
        Returns:
            Key deletion result
        """
        try:
            cmd = [
                "gcloud", "iam", "service-accounts", "keys", "delete", key_id,
                "--iam-account", service_account_email,
                "--project", project_id,
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Service account key '{key_id}' deleted successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to delete service account key: {e.stderr}"
            }
    
    # IAM Policy Management
    def get_iam_policy(self, resource: str, resource_type: str = "project") -> Dict[str, Any]:
        """
        Get IAM policy for a resource.
        
        Args:
            resource: Resource identifier (project ID, etc.)
            resource_type: Type of resource (project, organization, etc.)
            
        Returns:
            IAM policy
        """
        try:
            if resource_type == "project":
                cmd = [
                    "gcloud", "projects", "get-iam-policy", resource,
                    "--format=json"
                ]
            else:
                return {
                    "success": False,
                    "error": f"Resource type '{resource_type}' not yet supported"
                }
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            policy = json.loads(result.stdout) if result.stdout else {}
            
            return {
                "success": True,
                "policy": policy
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to get IAM policy: {e.stderr}"
            }
    
    def set_iam_policy(self, resource: str, policy_file: str, resource_type: str = "project") -> Dict[str, Any]:
        """
        Set IAM policy for a resource.
        
        Args:
            resource: Resource identifier
            policy_file: Path to policy file
            resource_type: Type of resource
            
        Returns:
            Policy update result
        """
        try:
            if resource_type == "project":
                cmd = [
                    "gcloud", "projects", "set-iam-policy", resource, policy_file
                ]
            else:
                return {
                    "success": False,
                    "error": f"Resource type '{resource_type}' not yet supported"
                }
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"IAM policy set for {resource_type} '{resource}'"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to set IAM policy: {e.stderr}"
            }
    
    def add_iam_binding(
        self,
        resource: str,
        member: str,
        role: str,
        resource_type: str = "project"
    ) -> Dict[str, Any]:
        """
        Add an IAM binding.
        
        Args:
            resource: Resource identifier
            member: Member to grant access (user:email, serviceAccount:email, etc.)
            role: Role to grant
            resource_type: Type of resource
            
        Returns:
            Binding addition result
        """
        try:
            if resource_type == "project":
                cmd = [
                    "gcloud", "projects", "add-iam-policy-binding", resource,
                    "--member", member,
                    "--role", role
                ]
            else:
                return {
                    "success": False,
                    "error": f"Resource type '{resource_type}' not yet supported"
                }
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"IAM binding added: {member} -> {role} on {resource}"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to add IAM binding: {e.stderr}"
            }
    
    def remove_iam_binding(
        self,
        resource: str,
        member: str,
        role: str,
        resource_type: str = "project"
    ) -> Dict[str, Any]:
        """
        Remove an IAM binding.
        
        Args:
            resource: Resource identifier
            member: Member to remove access from
            role: Role to remove
            resource_type: Type of resource
            
        Returns:
            Binding removal result
        """
        try:
            if resource_type == "project":
                cmd = [
                    "gcloud", "projects", "remove-iam-policy-binding", resource,
                    "--member", member,
                    "--role", role
                ]
            else:
                return {
                    "success": False,
                    "error": f"Resource type '{resource_type}' not yet supported"
                }
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"IAM binding removed: {member} -/-> {role} on {resource}"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to remove IAM binding: {e.stderr}"
            }
    
    def test_iam_permissions(
        self,
        resource: str,
        permissions: List[str],
        resource_type: str = "project"
    ) -> Dict[str, Any]:
        """
        Test IAM permissions for a resource.
        
        Args:
            resource: Resource identifier
            permissions: List of permissions to test
            resource_type: Type of resource
            
        Returns:
            Permission test result
        """
        try:
            if resource_type == "project":
                cmd = [
                    "gcloud", "projects", "test-iam-permissions", resource,
                    "--permissions", ",".join(permissions),
                    "--format=json"
                ]
            else:
                return {
                    "success": False,
                    "error": f"Resource type '{resource_type}' not yet supported"
                }
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            permissions_result = json.loads(result.stdout) if result.stdout else {}
            
            return {
                "success": True,
                "permissions": permissions_result
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to test IAM permissions: {e.stderr}"
            }
    
    # Role Management
    def create_custom_role(
        self,
        project_id: str,
        role_id: str,
        title: str,
        description: str,
        permissions: List[str],
        stage: str = "GA"
    ) -> Dict[str, Any]:
        """
        Create a custom IAM role.
        
        Args:
            project_id: GCP project ID
            role_id: ID for the custom role
            title: Human-readable title for the role
            description: Description of the role
            permissions: List of permissions for the role
            stage: Role stage (ALPHA, BETA, GA, DEPRECATED)
            
        Returns:
            Role creation result
        """
        try:
            cmd = [
                "gcloud", "iam", "roles", "create", role_id,
                "--project", project_id,
                "--title", title,
                "--description", description,
                "--permissions", ",".join(permissions),
                "--stage", stage,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "role": json.loads(result.stdout) if result.stdout else {},
                "message": f"Custom role '{role_id}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create custom role: {e.stderr}"
            }
    
    def list_roles(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List IAM roles.
        
        Args:
            project_id: Optional project ID to list custom roles
            
        Returns:
            List of roles
        """
        try:
            cmd = ["gcloud", "iam", "roles", "list"]
            
            if project_id:
                cmd.extend(["--project", project_id])
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            roles = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "roles": roles,
                "count": len(roles)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list roles: {e.stderr}"
            }
    
    def update_custom_role(
        self,
        project_id: str,
        role_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update a custom IAM role.
        
        Args:
            project_id: GCP project ID
            role_id: ID of the role to update
            **kwargs: Fields to update (title, description, permissions, stage)
            
        Returns:
            Role update result
        """
        try:
            cmd = [
                "gcloud", "iam", "roles", "update", role_id,
                "--project", project_id
            ]
            
            for key, value in kwargs.items():
                if key == "permissions" and value:
                    cmd.extend(["--permissions", ",".join(value)])
                elif key in ["title", "description", "stage"] and value:
                    cmd.extend([f"--{key}", value])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Custom role '{role_id}' updated successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to update custom role: {e.stderr}"
            }
    
    def delete_custom_role(self, project_id: str, role_id: str) -> Dict[str, Any]:
        """
        Delete a custom IAM role.
        
        Args:
            project_id: GCP project ID
            role_id: ID of the role to delete
            
        Returns:
            Role deletion result
        """
        try:
            cmd = [
                "gcloud", "iam", "roles", "delete", role_id,
                "--project", project_id,
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Custom role '{role_id}' deleted successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to delete custom role: {e.stderr}"
            }
    
    def describe_role(self, role_name: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Describe an IAM role.
        
        Args:
            role_name: Name of the role to describe
            project_id: Optional project ID for custom roles
            
        Returns:
            Role description
        """
        try:
            cmd = ["gcloud", "iam", "roles", "describe", role_name]
            
            if project_id:
                cmd.extend(["--project", project_id])
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            role = json.loads(result.stdout) if result.stdout else {}
            
            return {
                "success": True,
                "role": role
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to describe role: {e.stderr}"
            }
    
    # Placeholder methods for organization policies and advanced features
    def set_organization_policy(self, **kwargs) -> Dict[str, Any]:
        """Set organization policy (placeholder)."""
        return {"success": False, "error": "Organization policy management not yet implemented"}
    
    def get_organization_policy(self, **kwargs) -> Dict[str, Any]:
        """Get organization policy (placeholder)."""
        return {"success": False, "error": "Organization policy retrieval not yet implemented"}
    
    def list_organization_policies(self, **kwargs) -> Dict[str, Any]:
        """List organization policies (placeholder)."""
        return {"success": False, "error": "Organization policy listing not yet implemented"}
    
    def clear_organization_policy(self, **kwargs) -> Dict[str, Any]:
        """Clear organization policy (placeholder)."""
        return {"success": False, "error": "Organization policy clearing not yet implemented"}
    
    def analyze_iam_security(self, **kwargs) -> Dict[str, Any]:
        """Analyze IAM security (placeholder)."""
        return {"success": False, "error": "IAM security analysis not yet implemented"}
    
    def audit_service_account_usage(self, **kwargs) -> Dict[str, Any]:
        """Audit service account usage (placeholder)."""
        return {"success": False, "error": "Service account usage audit not yet implemented"}
    
    def check_compliance_status(self, **kwargs) -> Dict[str, Any]:
        """Check compliance status (placeholder)."""
        return {"success": False, "error": "Compliance status check not yet implemented"}
    
    def generate_access_report(self, **kwargs) -> Dict[str, Any]:
        """Generate access report (placeholder)."""
        return {"success": False, "error": "Access report generation not yet implemented"}
    
    def create_conditional_binding(self, **kwargs) -> Dict[str, Any]:
        """Create conditional binding (placeholder)."""
        return {"success": False, "error": "Conditional binding creation not yet implemented"}
    
    def validate_iam_condition(self, **kwargs) -> Dict[str, Any]:
        """Validate IAM condition (placeholder)."""
        return {"success": False, "error": "IAM condition validation not yet implemented"}
    
    def list_conditional_bindings(self, **kwargs) -> Dict[str, Any]:
        """List conditional bindings (placeholder)."""
        return {"success": False, "error": "Conditional binding listing not yet implemented"}
    
    def monitor_iam_changes(self, **kwargs) -> Dict[str, Any]:
        """Monitor IAM changes (placeholder)."""
        return {"success": False, "error": "IAM change monitoring not yet implemented"}
    
    def detect_privilege_escalation(self, **kwargs) -> Dict[str, Any]:
        """Detect privilege escalation (placeholder)."""
        return {"success": False, "error": "Privilege escalation detection not yet implemented"}
    
    def analyze_access_patterns(self, **kwargs) -> Dict[str, Any]:
        """Analyze access patterns (placeholder)."""
        return {"success": False, "error": "Access pattern analysis not yet implemented"}