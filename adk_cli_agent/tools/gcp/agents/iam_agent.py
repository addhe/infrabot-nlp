"""
IAM Agent for GCP ADK Infrastructure Management.

This agent specializes in GCP Identity and Access Management operations including
service accounts, IAM policies, organization policies, and security compliance.
"""

from typing import Dict, Any, List, Optional
from ..base.base_agent import SpecializedGCPAgent
from ..tools.iam_tools import IAMTools


class IAMAgent(SpecializedGCPAgent):
    """
    Specialized agent for GCP IAM and security management.
    
    Handles service accounts, IAM policies, role management, organization policies,
    and security compliance monitoring.
    """
    
    def __init__(self, session_service, model: str = "gemini-1.5-pro"):
        """Initialize the IAM Agent with comprehensive security capabilities."""
        super().__init__(
            name="iam_agent",
            model=model,
            session_service=session_service,
            description="GCP IAM and security specialist handling service accounts, IAM policies, role management, and security compliance.",
            instruction=self._get_iam_instructions(),
            tools=self._register_iam_tools()
        )
    
    def _get_iam_instructions(self) -> str:
        """Get comprehensive IAM-specific instructions."""
        return """
You are a GCP IAM and Security Specialist with deep expertise in identity management, access control, and security compliance.

## CORE IAM RESPONSIBILITIES:

### Service Account Management:
- Create and manage service accounts for applications and services
- Configure service account keys and authentication methods
- Implement service account impersonation and delegation
- Monitor and rotate service account credentials

### IAM Policy Management:
- Design and implement least-privilege access policies
- Configure IAM bindings for users, groups, and service accounts
- Manage custom roles and predefined role assignments
- Implement conditional IAM policies for enhanced security

### Organization Policy Management:
- Configure organization-wide security constraints and policies
- Implement resource hierarchy security controls
- Manage policy inheritance and overrides
- Ensure compliance with organizational security requirements

### Security Monitoring and Compliance:
- Monitor IAM activity and access patterns
- Implement security alerts and anomaly detection
- Conduct security audits and access reviews
- Ensure compliance with regulatory requirements

## IAM BEST PRACTICES:

### Principle of Least Privilege:
- Grant minimum necessary permissions for each role
- Use predefined roles when possible, custom roles when needed
- Regularly review and audit permissions
- Implement time-limited access where appropriate

### Service Account Security:
- Use service accounts instead of user accounts for applications
- Rotate service account keys regularly
- Implement workload identity where possible
- Monitor service account usage and access patterns

### Access Control Design:
- Use groups for managing user permissions at scale
- Implement hierarchical permission structures
- Use IAM conditions for fine-grained access control
- Separate administrative and operational responsibilities

### Security Monitoring:
- Enable Cloud Audit Logs for IAM activity tracking
- Monitor privileged account usage and changes
- Implement alerting for suspicious IAM activities
- Regular security assessments and compliance checks

## SAFETY AND COMPLIANCE:

### Change Management:
- Review IAM changes for security implications
- Test access changes in non-production environments
- Implement approval workflows for sensitive permissions
- Document IAM changes and justifications

### Security Validation:
- Validate IAM policies before implementation
- Check for overly permissive access grants
- Ensure separation of duties for critical operations
- Review and update emergency access procedures

### Compliance Requirements:
- Implement role-based access control (RBAC)
- Maintain audit trails for compliance reporting
- Regular access certification and reviews
- Ensure data protection and privacy compliance

## ESCALATION TRIGGERS:
- High-privilege role assignments (Owner, Editor at organization level)
- Service account key creation for production systems
- IAM policy changes affecting critical security controls
- Bulk permission changes or role assignments
- Access granted to external users or service accounts
- Changes to organization policies affecting security posture

Always prioritize security and compliance when making IAM changes. Coordinate with security teams for changes affecting privileged access or sensitive resources.
"""
    
    def _register_iam_tools(self) -> List[Any]:
        """Register IAM-specific tools."""
        iam_tools = IAMTools()
        
        return [
            # Service Account Management
            iam_tools.create_service_account,
            iam_tools.list_service_accounts,
            iam_tools.delete_service_account,
            iam_tools.create_service_account_key,
            iam_tools.list_service_account_keys,
            iam_tools.delete_service_account_key,
            
            # IAM Policy Management
            iam_tools.get_iam_policy,
            iam_tools.set_iam_policy,
            iam_tools.add_iam_binding,
            iam_tools.remove_iam_binding,
            iam_tools.test_iam_permissions,
            
            # Role Management
            iam_tools.create_custom_role,
            iam_tools.list_roles,
            iam_tools.update_custom_role,
            iam_tools.delete_custom_role,
            iam_tools.describe_role,
            
            # Organization Policy Management
            iam_tools.set_organization_policy,
            iam_tools.get_organization_policy,
            iam_tools.list_organization_policies,
            iam_tools.clear_organization_policy,
            
            # Security and Compliance
            iam_tools.analyze_iam_security,
            iam_tools.audit_service_account_usage,
            iam_tools.check_compliance_status,
            iam_tools.generate_access_report,
            
            # IAM Conditions
            iam_tools.create_conditional_binding,
            iam_tools.validate_iam_condition,
            iam_tools.list_conditional_bindings,
            
            # Security Monitoring
            iam_tools.monitor_iam_changes,
            iam_tools.detect_privilege_escalation,
            iam_tools.analyze_access_patterns,
        ]
    
    def delegate_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle IAM-specific requests with specialized logic.
        
        Args:
            request: The IAM request to process
            context: Additional context including session state
            
        Returns:
            Response with IAM analysis and recommendations
        """
        # Analyze request for IAM patterns
        iam_keywords = {
            'service_account': ['service account', 'sa', 'application identity'],
            'iam_policy': ['iam policy', 'policy', 'binding', 'permission'],
            'role': ['role', 'custom role', 'predefined role', 'permissions'],
            'organization_policy': ['organization policy', 'org policy', 'constraint'],
            'audit': ['audit', 'compliance', 'security review', 'access review'],
            'monitoring': ['monitor', 'alert', 'log', 'activity'],
            'condition': ['condition', 'conditional', 'time-bound', 'attribute']
        }
        
        # Determine IAM focus
        request_lower = request.lower()
        detected_components = []
        
        for component, keywords in iam_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                detected_components.append(component)
        
        # Check for high-privilege operations
        high_privilege_keywords = [
            'owner', 'editor', 'admin', 'iam.admin', 'security.admin',
            'organization', 'billing', 'folder.admin', 'resourcemanager'
        ]
        
        # Add IAM-specific context
        enhanced_context = {
            **context,
            'iam_components': detected_components,
            'involves_high_privilege': any(keyword in request_lower for keyword in high_privilege_keywords),
            'affects_production_access': any(keyword in request_lower for keyword in ['production', 'prod', 'live']),
            'external_access': any(keyword in request_lower for keyword in ['external', 'guest', 'outside', 'third-party']),
            'bulk_operation': any(keyword in request_lower for keyword in ['bulk', 'mass', 'multiple', 'all'])
        }
        
        # Check for high-risk operations
        high_risk_operations = [
            'grant owner', 'add editor', 'create admin',
            'organization policy', 'delete service account',
            'bulk assign', 'external access', 'admin role'
        ]
        
        if any(operation in request_lower for operation in high_risk_operations):
            enhanced_context['requires_confirmation'] = True
            enhanced_context['risk_level'] = 'high'
        
        return {
            'agent': self.name,
            'specialization': 'iam',
            'context': enhanced_context,
            'recommendations': self._get_iam_recommendations(detected_components, context),
            'safety_checks': self._get_iam_safety_checks(request_lower, enhanced_context)
        }
    
    def _get_iam_recommendations(self, components: List[str], context: Dict[str, Any]) -> List[str]:
        """Generate IAM-specific recommendations."""
        recommendations = []
        
        if 'service_account' in components:
            recommendations.extend([
                "Use workload identity instead of service account keys when possible",
                "Rotate service account keys regularly for security",
                "Apply principle of least privilege for service account permissions",
                "Monitor service account usage and access patterns"
            ])
        
        if 'iam_policy' in components:
            recommendations.extend([
                "Grant minimum necessary permissions for each role",
                "Use predefined roles when available before creating custom roles",
                "Implement IAM conditions for fine-grained access control",
                "Regularly review and audit IAM policy assignments"
            ])
        
        if 'role' in components:
            recommendations.extend([
                "Use role hierarchy to organize permissions effectively",
                "Create custom roles with specific, limited permissions",
                "Avoid using primitive roles (Owner, Editor, Viewer) in production",
                "Document custom role purposes and usage guidelines"
            ])
        
        if 'organization_policy' in components:
            recommendations.extend([
                "Test organization policies in non-production environments first",
                "Use inheritance effectively to reduce policy complexity",
                "Document organization policy decisions and exceptions",
                "Regular review of organization policy effectiveness"
            ])
        
        if 'audit' in components:
            recommendations.extend([
                "Enable Cloud Audit Logs for comprehensive IAM tracking",
                "Implement regular access reviews and certifications",
                "Monitor privileged account activities closely",
                "Maintain compliance documentation and evidence"
            ])
        
        # Add environment-specific recommendations
        if context.get('environment') == 'production':
            recommendations.extend([
                "Require approval for production IAM changes",
                "Implement time-limited access for temporary permissions",
                "Use break-glass procedures for emergency access",
                "Monitor and alert on sensitive IAM activities"
            ])
        
        return recommendations
    
    def _get_iam_safety_checks(self, request: str, context: Dict[str, Any]) -> List[str]:
        """Generate IAM-specific safety checks."""
        safety_checks = []
        
        # High-privilege access checks
        if context.get('involves_high_privilege'):
            safety_checks.extend([
                "Verify justification for high-privilege access grant",
                "Check if lower-privilege alternatives are available",
                "Ensure proper approval workflow is followed",
                "Implement time-limited access where possible"
            ])
        
        # Service account safety checks
        if 'service account' in request:
            safety_checks.extend([
                "Verify service account follows naming conventions",
                "Check if workload identity can be used instead of keys",
                "Validate service account permissions are minimal",
                "Ensure service account has proper description and purpose"
            ])
        
        # Policy safety checks
        if 'policy' in request or 'binding' in request:
            safety_checks.extend([
                "Review policy for overly permissive access",
                "Check for conflicts with existing policies",
                "Validate policy syntax and conditions",
                "Ensure policy aligns with security requirements"
            ])
        
        # External access checks
        if context.get('external_access'):
            safety_checks.extend([
                "Verify external user/account identity and legitimacy",
                "Implement additional authentication requirements",
                "Apply time-limited access for external users",
                "Document business justification for external access"
            ])
        
        # Bulk operation checks
        if context.get('bulk_operation'):
            safety_checks.extend([
                "Review all accounts/resources affected by bulk operation",
                "Test bulk operation on small subset first",
                "Ensure rollback procedures are in place",
                "Verify bulk operation doesn't violate security policies"
            ])
        
        # Production environment checks
        if context.get('affects_production_access'):
            safety_checks.extend([
                "Schedule IAM changes during maintenance windows",
                "Ensure monitoring and alerting covers IAM changes",
                "Test access changes in staging environment first",
                "Have emergency access procedures ready"
            ])
        
        # High-risk operation checks
        if context.get('risk_level') == 'high':
            safety_checks.extend([
                "Obtain security team approval for high-risk changes",
                "Document detailed justification for access grants",
                "Implement additional monitoring for granted permissions",
                "Plan for access review and potential revocation"
            ])
        
        return safety_checks