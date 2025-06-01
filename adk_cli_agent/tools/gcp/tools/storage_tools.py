"""
Storage Tools for GCP ADK Infrastructure Management.

Provides comprehensive storage tools for Cloud Storage, Cloud SQL, Firestore,
and storage security management.
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


class StorageTools:
    """Tools for GCP storage operations."""
    
    def __init__(self):
        """Initialize storage tools."""
        self.context = ToolContext()
    
    # Cloud Storage Management
    def create_storage_bucket(
        self,
        project_id: str,
        bucket_name: str,
        location: str = "US",
        storage_class: str = "STANDARD",
        uniform_bucket_level_access: bool = True
    ) -> Dict[str, Any]:
        """
        Create a Cloud Storage bucket.
        
        Args:
            project_id: GCP project ID
            bucket_name: Name for the storage bucket
            location: Bucket location (region or multi-region)
            storage_class: Storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE)
            uniform_bucket_level_access: Enable uniform bucket-level access
            
        Returns:
            Bucket creation result
        """
        try:
            cmd = [
                "gcloud", "storage", "buckets", "create", f"gs://{bucket_name}",
                "--project", project_id,
                "--location", location,
                "--default-storage-class", storage_class
            ]
            
            if uniform_bucket_level_access:
                cmd.append("--uniform-bucket-level-access")
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "bucket": {"name": bucket_name, "location": location, "storage_class": storage_class},
                "message": f"Storage bucket '{bucket_name}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create storage bucket: {e.stderr}",
                "command": " ".join(cmd)
            }
    
    def list_storage_buckets(self, project_id: str) -> Dict[str, Any]:
        """
        List Cloud Storage buckets in a project.
        
        Args:
            project_id: GCP project ID
            
        Returns:
            List of storage buckets
        """
        try:
            cmd = [
                "gcloud", "storage", "buckets", "list",
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            buckets = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "buckets": buckets,
                "count": len(buckets)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list storage buckets: {e.stderr}"
            }
    
    def delete_storage_bucket(self, project_id: str, bucket_name: str) -> Dict[str, Any]:
        """
        Delete a Cloud Storage bucket.
        
        Args:
            project_id: GCP project ID
            bucket_name: Name of the bucket to delete
            
        Returns:
            Deletion result
        """
        try:
            cmd = [
                "gcloud", "storage", "rm", f"gs://{bucket_name}",
                "--recursive",
                "--project", project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Storage bucket '{bucket_name}' deleted successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to delete storage bucket: {e.stderr}"
            }
    
    def set_bucket_policy(self, bucket_name: str, policy_file: str) -> Dict[str, Any]:
        """
        Set IAM policy for a storage bucket.
        
        Args:
            bucket_name: Name of the storage bucket
            policy_file: Path to IAM policy file
            
        Returns:
            Policy update result
        """
        try:
            cmd = [
                "gcloud", "storage", "buckets", "set-iam-policy",
                f"gs://{bucket_name}", policy_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"IAM policy set for bucket '{bucket_name}'"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to set bucket policy: {e.stderr}"
            }
    
    def configure_bucket_lifecycle(self, bucket_name: str, lifecycle_config: str) -> Dict[str, Any]:
        """
        Configure lifecycle policy for a storage bucket.
        
        Args:
            bucket_name: Name of the storage bucket
            lifecycle_config: Path to lifecycle configuration file
            
        Returns:
            Lifecycle configuration result
        """
        try:
            cmd = [
                "gcloud", "storage", "buckets", "update",
                f"gs://{bucket_name}",
                "--lifecycle-file", lifecycle_config
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Lifecycle policy configured for bucket '{bucket_name}'"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to configure lifecycle policy: {e.stderr}"
            }
    
    def upload_object(self, source_path: str, bucket_name: str, object_name: str) -> Dict[str, Any]:
        """
        Upload an object to Cloud Storage.
        
        Args:
            source_path: Local path to source file
            bucket_name: Target storage bucket
            object_name: Name for the object in storage
            
        Returns:
            Upload result
        """
        try:
            cmd = [
                "gcloud", "storage", "cp", source_path,
                f"gs://{bucket_name}/{object_name}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Object uploaded to gs://{bucket_name}/{object_name}"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to upload object: {e.stderr}"
            }
    
    def download_object(self, bucket_name: str, object_name: str, destination_path: str) -> Dict[str, Any]:
        """
        Download an object from Cloud Storage.
        
        Args:
            bucket_name: Source storage bucket
            object_name: Name of the object in storage
            destination_path: Local path to save the file
            
        Returns:
            Download result
        """
        try:
            cmd = [
                "gcloud", "storage", "cp",
                f"gs://{bucket_name}/{object_name}",
                destination_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Object downloaded from gs://{bucket_name}/{object_name}"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to download object: {e.stderr}"
            }
    
    def list_objects(self, bucket_name: str, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        List objects in a Cloud Storage bucket.
        
        Args:
            bucket_name: Storage bucket name
            prefix: Optional prefix filter
            
        Returns:
            List of objects
        """
        try:
            bucket_path = f"gs://{bucket_name}"
            if prefix:
                bucket_path += f"/{prefix}"
            
            cmd = [
                "gcloud", "storage", "ls", bucket_path,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            objects = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "objects": objects,
                "count": len(objects)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list objects: {e.stderr}"
            }
    
    def delete_object(self, bucket_name: str, object_name: str) -> Dict[str, Any]:
        """
        Delete an object from Cloud Storage.
        
        Args:
            bucket_name: Storage bucket name
            object_name: Name of the object to delete
            
        Returns:
            Deletion result
        """
        try:
            cmd = [
                "gcloud", "storage", "rm",
                f"gs://{bucket_name}/{object_name}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Object gs://{bucket_name}/{object_name} deleted successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to delete object: {e.stderr}"
            }
    
    # Cloud SQL Management
    def create_sql_instance(
        self,
        project_id: str,
        instance_name: str,
        database_version: str,
        tier: str = "db-n1-standard-1",
        region: str = "us-central1",
        root_password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Cloud SQL instance.
        
        Args:
            project_id: GCP project ID
            instance_name: Name for the SQL instance
            database_version: Database version (e.g., MYSQL_8_0, POSTGRES_13)
            tier: Machine type for the instance
            region: GCP region for the instance
            root_password: Root password for the instance
            
        Returns:
            Instance creation result
        """
        try:
            cmd = [
                "gcloud", "sql", "instances", "create", instance_name,
                "--project", project_id,
                "--database-version", database_version,
                "--tier", tier,
                "--region", region
            ]
            
            if root_password:
                cmd.extend(["--root-password", root_password])
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "instance": json.loads(result.stdout) if result.stdout else {},
                "message": f"Cloud SQL instance '{instance_name}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create SQL instance: {e.stderr}"
            }
    
    def list_sql_instances(self, project_id: str) -> Dict[str, Any]:
        """
        List Cloud SQL instances in a project.
        
        Args:
            project_id: GCP project ID
            
        Returns:
            List of SQL instances
        """
        try:
            cmd = [
                "gcloud", "sql", "instances", "list",
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            instances = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "instances": instances,
                "count": len(instances)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list SQL instances: {e.stderr}"
            }
    
    def delete_sql_instance(self, project_id: str, instance_name: str) -> Dict[str, Any]:
        """
        Delete a Cloud SQL instance.
        
        Args:
            project_id: GCP project ID
            instance_name: Name of the instance to delete
            
        Returns:
            Deletion result
        """
        try:
            cmd = [
                "gcloud", "sql", "instances", "delete", instance_name,
                "--project", project_id,
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Cloud SQL instance '{instance_name}' deleted successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to delete SQL instance: {e.stderr}"
            }
    
    def create_sql_database(self, project_id: str, instance_name: str, database_name: str) -> Dict[str, Any]:
        """
        Create a database in a Cloud SQL instance.
        
        Args:
            project_id: GCP project ID
            instance_name: SQL instance name
            database_name: Name for the database
            
        Returns:
            Database creation result
        """
        try:
            cmd = [
                "gcloud", "sql", "databases", "create", database_name,
                "--instance", instance_name,
                "--project", project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Database '{database_name}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create database: {e.stderr}"
            }
    
    def list_sql_databases(self, project_id: str, instance_name: str) -> Dict[str, Any]:
        """
        List databases in a Cloud SQL instance.
        
        Args:
            project_id: GCP project ID
            instance_name: SQL instance name
            
        Returns:
            List of databases
        """
        try:
            cmd = [
                "gcloud", "sql", "databases", "list",
                "--instance", instance_name,
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            databases = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "databases": databases,
                "count": len(databases)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list databases: {e.stderr}"
            }
    
    def create_sql_user(
        self,
        project_id: str,
        instance_name: str,
        username: str,
        password: str,
        host: str = "%"
    ) -> Dict[str, Any]:
        """
        Create a user in a Cloud SQL instance.
        
        Args:
            project_id: GCP project ID
            instance_name: SQL instance name
            username: Username for the new user
            password: Password for the new user
            host: Host pattern for the user
            
        Returns:
            User creation result
        """
        try:
            cmd = [
                "gcloud", "sql", "users", "create", username,
                "--instance", instance_name,
                "--password", password,
                "--host", host,
                "--project", project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"SQL user '{username}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create SQL user: {e.stderr}"
            }
    
    def backup_sql_instance(self, project_id: str, instance_name: str) -> Dict[str, Any]:
        """
        Create a backup of a Cloud SQL instance.
        
        Args:
            project_id: GCP project ID
            instance_name: SQL instance name
            
        Returns:
            Backup creation result
        """
        try:
            cmd = [
                "gcloud", "sql", "backups", "create",
                "--instance", instance_name,
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "backup": json.loads(result.stdout) if result.stdout else {},
                "message": f"Backup created for SQL instance '{instance_name}'"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create backup: {e.stderr}"
            }
    
    def restore_sql_instance(
        self,
        project_id: str,
        instance_name: str,
        backup_id: str
    ) -> Dict[str, Any]:
        """
        Restore a Cloud SQL instance from backup.
        
        Args:
            project_id: GCP project ID
            instance_name: SQL instance name
            backup_id: ID of the backup to restore from
            
        Returns:
            Restore result
        """
        try:
            cmd = [
                "gcloud", "sql", "backups", "restore", backup_id,
                "--restore-instance", instance_name,
                "--project", project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"SQL instance '{instance_name}' restored from backup '{backup_id}'"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to restore from backup: {e.stderr}"
            }
    
    # Placeholder methods for Firestore and additional storage features
    def create_firestore_database(self, **kwargs) -> Dict[str, Any]:
        """Create Firestore database (placeholder)."""
        return {"success": False, "error": "Firestore database creation not yet implemented"}
    
    def list_firestore_collections(self, **kwargs) -> Dict[str, Any]:
        """List Firestore collections (placeholder)."""
        return {"success": False, "error": "Firestore collection listing not yet implemented"}
    
    def query_firestore_data(self, **kwargs) -> Dict[str, Any]:
        """Query Firestore data (placeholder)."""
        return {"success": False, "error": "Firestore data querying not yet implemented"}
    
    def backup_firestore_database(self, **kwargs) -> Dict[str, Any]:
        """Backup Firestore database (placeholder)."""
        return {"success": False, "error": "Firestore backup not yet implemented"}
    
    def restore_firestore_database(self, **kwargs) -> Dict[str, Any]:
        """Restore Firestore database (placeholder)."""
        return {"success": False, "error": "Firestore restore not yet implemented"}
    
    def configure_bucket_iam(self, **kwargs) -> Dict[str, Any]:
        """Configure bucket IAM (placeholder)."""
        return {"success": False, "error": "Bucket IAM configuration not yet implemented"}
    
    def set_encryption_config(self, **kwargs) -> Dict[str, Any]:
        """Set encryption configuration (placeholder)."""
        return {"success": False, "error": "Encryption configuration not yet implemented"}
    
    def configure_access_logging(self, **kwargs) -> Dict[str, Any]:
        """Configure access logging (placeholder)."""
        return {"success": False, "error": "Access logging configuration not yet implemented"}
    
    def scan_storage_security(self, **kwargs) -> Dict[str, Any]:
        """Scan storage security (placeholder)."""
        return {"success": False, "error": "Storage security scanning not yet implemented"}
    
    def get_storage_metrics(self, **kwargs) -> Dict[str, Any]:
        """Get storage metrics (placeholder)."""
        return {"success": False, "error": "Storage metrics not yet implemented"}
    
    def analyze_storage_costs(self, **kwargs) -> Dict[str, Any]:
        """Analyze storage costs (placeholder)."""
        return {"success": False, "error": "Storage cost analysis not yet implemented"}
    
    def check_storage_compliance(self, **kwargs) -> Dict[str, Any]:
        """Check storage compliance (placeholder)."""
        return {"success": False, "error": "Storage compliance check not yet implemented"}
