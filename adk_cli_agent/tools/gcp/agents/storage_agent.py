"""
Storage Agent for GCP ADK Infrastructure Management.

This agent specializes in GCP storage operations including Cloud Storage buckets,
Cloud SQL databases, Firestore, and storage security management.
"""

from typing import Dict, Any, List, Optional
from ..base.base_agent import SpecializedGCPAgent
from ..tools.storage_tools import StorageTools


class StorageAgent(SpecializedGCPAgent):
    """
    Specialized agent for GCP storage infrastructure management.
    
    Handles Cloud Storage buckets, Cloud SQL instances, Firestore databases,
    backup strategies, and storage security policies.
    """
    
    def __init__(self, session_service, model: str = "gemini-1.5-pro"):
        """Initialize the Storage Agent with comprehensive storage capabilities."""
        super().__init__(
            name="storage_agent",
            model=model,
            session_service=session_service,
            description="GCP storage infrastructure specialist handling Cloud Storage, Cloud SQL, Firestore, and storage security management.",
            instruction=self._get_storage_instructions(),
            tools=self._register_storage_tools()
        )
    
    def _get_storage_instructions(self) -> str:
        """Get comprehensive storage-specific instructions."""
        return """
You are a GCP Storage Infrastructure Specialist with deep expertise in cloud storage solutions, database management, and data security.

## CORE STORAGE RESPONSIBILITIES:

### Cloud Storage Management:
- Design and implement Cloud Storage bucket architectures
- Configure storage classes and lifecycle policies for cost optimization
- Manage object versioning, retention policies, and deletion protection
- Implement cross-region replication and backup strategies

### Database Services:
- Deploy and manage Cloud SQL instances (MySQL, PostgreSQL, SQL Server)
- Configure high availability, read replicas, and automated backups
- Optimize database performance and resource allocation
- Implement database security and access controls

### NoSQL and Document Storage:
- Design and manage Firestore databases and collections
- Configure security rules and access patterns
- Optimize query performance and data modeling
- Implement data import/export and backup strategies

### Storage Security and Compliance:
- Configure IAM roles and bucket policies for secure access
- Implement encryption at rest and in transit
- Set up audit logging and access monitoring
- Ensure compliance with data protection regulations

## STORAGE BEST PRACTICES:

### Cost Optimization:
- Choose appropriate storage classes based on access patterns
- Implement lifecycle policies for automatic data tiering
- Monitor and optimize storage usage and costs
- Use regional vs multi-regional storage strategically

### Data Protection:
- Implement comprehensive backup and recovery strategies
- Configure point-in-time recovery for databases
- Use versioning and retention policies for critical data
- Test backup restoration procedures regularly

### Performance Optimization:
- Design storage layouts for optimal access patterns
- Configure database connection pooling and query optimization
- Implement caching strategies where appropriate
- Monitor performance metrics and tune accordingly

### Security and Access Control:
- Apply principle of least privilege for storage access
- Use service accounts and IAM roles for applications
- Configure private access and VPC endpoint connections
- Implement data classification and handling policies

## SAFETY AND COMPLIANCE:

### Data Protection:
- Validate backup configurations before making changes
- Test restoration procedures in non-production environments
- Implement data retention and deletion policies
- Ensure compliance with data residency requirements

### Change Management:
- Review storage configuration changes for impact
- Implement gradual rollout for critical storage updates
- Maintain documentation of storage architectures
- Coordinate with application teams for database changes

### Disaster Recovery:
- Design multi-region backup and recovery strategies
- Test disaster recovery procedures regularly
- Implement automated failover where appropriate
- Document recovery time and point objectives

## ESCALATION TRIGGERS:
- Production database configuration changes
- Storage bucket policy modifications affecting application access
- Large-scale data migration or deletion operations
- Security configuration changes for sensitive data
- Backup or recovery procedure failures

Always prioritize data integrity, security, and availability when making storage infrastructure changes. Coordinate with data and security teams for changes affecting sensitive or regulated data.
"""
    
    def _register_storage_tools(self) -> List[Any]:
        """Register storage-specific tools."""
        storage_tools = StorageTools()
        
        return [
            # Cloud Storage Management
            storage_tools.create_storage_bucket,
            storage_tools.list_storage_buckets,
            storage_tools.delete_storage_bucket,
            storage_tools.set_bucket_policy,
            storage_tools.configure_bucket_lifecycle,
            storage_tools.upload_object,
            storage_tools.download_object,
            storage_tools.list_objects,
            storage_tools.delete_object,
            
            # Cloud SQL Management
            storage_tools.create_sql_instance,
            storage_tools.list_sql_instances,
            storage_tools.delete_sql_instance,
            storage_tools.create_sql_database,
            storage_tools.list_sql_databases,
            storage_tools.create_sql_user,
            storage_tools.backup_sql_instance,
            storage_tools.restore_sql_instance,
            
            # Firestore Management
            storage_tools.create_firestore_database,
            storage_tools.list_firestore_collections,
            storage_tools.query_firestore_data,
            storage_tools.backup_firestore_database,
            storage_tools.restore_firestore_database,
            
            # Storage Security
            storage_tools.configure_bucket_iam,
            storage_tools.set_encryption_config,
            storage_tools.configure_access_logging,
            storage_tools.scan_storage_security,
            
            # Storage Monitoring
            storage_tools.get_storage_metrics,
            storage_tools.analyze_storage_costs,
            storage_tools.check_storage_compliance,
        ]
    
    def delegate_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle storage-specific requests with specialized logic.
        
        Args:
            request: The storage request to process
            context: Additional context including session state
            
        Returns:
            Response with storage analysis and recommendations
        """
        # Analyze request for storage patterns
        storage_keywords = {
            'cloud_storage': ['bucket', 'cloud storage', 'gcs', 'object storage'],
            'cloud_sql': ['cloud sql', 'database', 'mysql', 'postgresql', 'sql server'],
            'firestore': ['firestore', 'nosql', 'document', 'collection'],
            'backup': ['backup', 'restore', 'recovery', 'snapshot'],
            'security': ['iam', 'encryption', 'access', 'policy', 'security'],
            'lifecycle': ['lifecycle', 'retention', 'archival', 'deletion'],
            'replication': ['replication', 'sync', 'cross-region', 'mirror']
        }
        
        # Determine storage focus
        request_lower = request.lower()
        detected_components = []
        
        for component, keywords in storage_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                detected_components.append(component)
        
        # Add storage-specific context
        enhanced_context = {
            **context,
            'storage_components': detected_components,
            'requires_backup_validation': any(keyword in request_lower for keyword in ['delete', 'remove', 'drop', 'truncate']),
            'affects_production_data': any(keyword in request_lower for keyword in ['production', 'prod', 'live', 'customer']),
            'storage_scope': 'multi_region' if any(keyword in request_lower for keyword in ['region', 'global', 'replicate']) else 'single_region'
        }
        
        # Check for high-risk operations
        high_risk_operations = [
            'delete bucket', 'drop database', 'delete instance',
            'remove backup', 'change encryption', 'modify iam',
            'delete collection', 'truncate data'
        ]
        
        if any(operation in request_lower for operation in high_risk_operations):
            enhanced_context['requires_confirmation'] = True
            enhanced_context['risk_level'] = 'high'
        
        return {
            'agent': self.name,
            'specialization': 'storage',
            'context': enhanced_context,
            'recommendations': self._get_storage_recommendations(detected_components, context),
            'safety_checks': self._get_storage_safety_checks(request_lower, enhanced_context)
        }
    
    def _get_storage_recommendations(self, components: List[str], context: Dict[str, Any]) -> List[str]:
        """Generate storage-specific recommendations."""
        recommendations = []
        
        if 'cloud_storage' in components:
            recommendations.extend([
                "Choose appropriate storage class based on access patterns",
                "Configure lifecycle policies for cost optimization",
                "Enable versioning for important data protection",
                "Consider regional vs multi-regional based on requirements"
            ])
        
        if 'cloud_sql' in components:
            recommendations.extend([
                "Configure automated backups with appropriate retention",
                "Consider read replicas for read-heavy workloads",
                "Enable high availability for production databases",
                "Monitor database performance and optimize queries"
            ])
        
        if 'firestore' in components:
            recommendations.extend([
                "Design document structure for optimal query patterns",
                "Configure security rules for data access control",
                "Consider composite indexes for complex queries",
                "Plan for data export and backup strategies"
            ])
        
        if 'security' in components:
            recommendations.extend([
                "Apply principle of least privilege for storage access",
                "Enable encryption at rest and in transit",
                "Configure audit logging for storage access",
                "Review and update IAM policies regularly"
            ])
        
        # Add environment-specific recommendations
        if context.get('environment') == 'production':
            recommendations.extend([
                "Test backup and recovery procedures regularly",
                "Implement monitoring and alerting for storage systems",
                "Document disaster recovery procedures",
                "Coordinate with application teams for database changes"
            ])
        
        return recommendations
    
    def _get_storage_safety_checks(self, request: str, context: Dict[str, Any]) -> List[str]:
        """Generate storage-specific safety checks."""
        safety_checks = []
        
        # Backup safety checks
        if 'backup' in request or 'restore' in request:
            safety_checks.extend([
                "Verify backup integrity before restoration",
                "Check backup retention policies and compliance",
                "Validate restoration target and scope"
            ])
        
        # Database safety checks
        if 'database' in request or 'sql' in request:
            safety_checks.extend([
                "Verify database connections and dependencies",
                "Check for ongoing transactions or maintenance",
                "Validate database configuration changes"
            ])
        
        # Storage bucket safety checks
        if 'bucket' in request or 'storage' in request:
            safety_checks.extend([
                "Check for objects and dependencies in bucket",
                "Verify bucket policies and access permissions",
                "Validate lifecycle and retention configurations"
            ])
        
        # Production data checks
        if context.get('affects_production_data'):
            safety_checks.extend([
                "Create backup before making changes",
                "Schedule changes during maintenance window",
                "Notify stakeholders of potential data impact"
            ])
        
        # High-risk operation checks
        if context.get('risk_level') == 'high':
            safety_checks.extend([
                "Obtain approval from data administrator",
                "Test operation in non-production environment",
                "Prepare rollback procedures for changes"
            ])
        
        # Deletion safety checks
        if context.get('requires_backup_validation'):
            safety_checks.extend([
                "Confirm recent backup exists and is valid",
                "Verify data is not needed for compliance",
                "Check for references from other systems"
            ])
        
        return safety_checks