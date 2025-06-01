"""
Monitoring Tools for GCP ADK Infrastructure Management.

Provides comprehensive monitoring tools for Cloud Monitoring, Cloud Logging,
alerting, and observability management.
"""

import json
import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta, timezone

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


class MonitoringTools:
    """Tools for GCP monitoring and observability operations."""
    
    def __init__(self):
        """Initialize monitoring tools."""
        self.context = ToolContext()
    
    # Cloud Monitoring - Metrics Management
    def list_metrics(self, project_id: str, filter_expr: Optional[str] = None) -> Dict[str, Any]:
        """
        List available metrics in Cloud Monitoring.
        
        Args:
            project_id: GCP project ID
            filter_expr: Optional filter expression for metrics
            
        Returns:
            List of available metrics
        """
        try:
            cmd = [
                "gcloud", "monitoring", "metrics", "list",
                "--project", project_id,
                "--format=json"
            ]
            
            if filter_expr:
                cmd.extend(["--filter", filter_expr])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metrics = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "metrics": metrics,
                "count": len(metrics)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list metrics: {e.stderr}"
            }
    
    def create_custom_metric(
        self,
        project_id: str,
        metric_type: str,
        display_name: str,
        description: str,
        metric_kind: str = "GAUGE",
        value_type: str = "DOUBLE"
    ) -> Dict[str, Any]:
        """
        Create a custom metric descriptor.
        
        Args:
            project_id: GCP project ID
            metric_type: Metric type (e.g., 'custom.googleapis.com/my_metric')
            display_name: Human-readable name
            description: Metric description
            metric_kind: GAUGE, DELTA, or CUMULATIVE
            value_type: BOOL, INT64, DOUBLE, STRING, DISTRIBUTION
            
        Returns:
            Metric creation result
        """
        try:
            descriptor = {
                "type": metric_type,
                "displayName": display_name,
                "description": description,
                "metricKind": metric_kind,
                "valueType": value_type
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(descriptor, f)
                descriptor_file = f.name
            
            cmd = [
                "gcloud", "monitoring", "metrics", "descriptors", "create",
                descriptor_file,
                "--project", project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            os.unlink(descriptor_file)
            
            return {
                "success": True,
                "metric_type": metric_type,
                "message": f"Custom metric '{display_name}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create custom metric: {e.stderr}"
            }
    
    # Alert Policies
    def list_alert_policies(self, project_id: str) -> Dict[str, Any]:
        """
        List alert policies.
        
        Args:
            project_id: GCP project ID
            
        Returns:
            List of alert policies
        """
        try:
            cmd = [
                "gcloud", "alpha", "monitoring", "policies", "list",
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            policies = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "alert_policies": policies,
                "count": len(policies)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list alert policies: {e.stderr}"
            }
    
    def create_alert_policy(
        self,
        project_id: str,
        display_name: str,
        condition_display_name: str,
        metric_filter: str,
        threshold_value: float,
        comparison: str = "COMPARISON_GT",
        duration: str = "300s"
    ) -> Dict[str, Any]:
        """
        Create an alert policy.
        
        Args:
            project_id: GCP project ID
            display_name: Alert policy display name
            condition_display_name: Condition display name
            metric_filter: Metric filter expression
            threshold_value: Threshold value for alerting
            comparison: Comparison operator
            duration: Duration for condition evaluation
            
        Returns:
            Alert policy creation result
        """
        try:
            policy = {
                "displayName": display_name,
                "conditions": [{
                    "displayName": condition_display_name,
                    "conditionThreshold": {
                        "filter": metric_filter,
                        "comparison": comparison,
                        "thresholdValue": threshold_value,
                        "duration": duration,
                        "aggregations": [{
                            "alignmentPeriod": "60s",
                            "perSeriesAligner": "ALIGN_MEAN"
                        }]
                    }
                }],
                "enabled": True,
                "combiner": "OR"
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(policy, f)
                policy_file = f.name
            
            cmd = [
                "gcloud", "alpha", "monitoring", "policies", "create",
                "--policy-from-file", policy_file,
                "--project", project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            os.unlink(policy_file)
            
            return {
                "success": True,
                "message": f"Alert policy '{display_name}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create alert policy: {e.stderr}"
            }
    
    # Cloud Logging
    def list_logs(self, project_id: str, filter_expr: Optional[str] = None) -> Dict[str, Any]:
        """
        List available logs.
        
        Args:
            project_id: GCP project ID
            filter_expr: Optional filter expression
            
        Returns:
            List of available logs
        """
        try:
            cmd = [
                "gcloud", "logging", "logs", "list",
                "--project", project_id,
                "--format=json"
            ]
            
            if filter_expr:
                cmd.extend(["--filter", filter_expr])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logs = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "logs": logs,
                "count": len(logs)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list logs: {e.stderr}"
            }
    
    def read_log_entries(
        self,
        project_id: str,
        filter_expr: Optional[str] = None,
        limit: int = 100,
        order_by: str = "timestamp desc"
    ) -> Dict[str, Any]:
        """
        Read log entries.
        
        Args:
            project_id: GCP project ID
            filter_expr: Log filter expression
            limit: Maximum number of entries to return
            order_by: Sort order for entries
            
        Returns:
            Log entries
        """
        try:
            cmd = [
                "gcloud", "logging", "read",
                "--project", project_id,
                "--limit", str(limit),
                "--format=json"
            ]
            
            if filter_expr:
                cmd.append(filter_expr)
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            entries = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "log_entries": entries,
                "count": len(entries)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to read log entries: {e.stderr}"
            }
    
    def create_log_sink(
        self,
        project_id: str,
        sink_name: str,
        destination: str,
        log_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a log sink.
        
        Args:
            project_id: GCP project ID
            sink_name: Name for the sink
            destination: Destination for logs (Cloud Storage, BigQuery, etc.)
            log_filter: Optional filter for logs to include
            
        Returns:
            Sink creation result
        """
        try:
            cmd = [
                "gcloud", "logging", "sinks", "create", sink_name, destination,
                "--project", project_id
            ]
            
            if log_filter:
                cmd.extend(["--log-filter", log_filter])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "sink_name": sink_name,
                "destination": destination,
                "message": f"Log sink '{sink_name}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create log sink: {e.stderr}"
            }
    
    # Placeholder methods for advanced features
    def create_dashboard(self, **kwargs) -> Dict[str, Any]:
        """Create monitoring dashboard (placeholder)."""
        return {"success": False, "error": "Dashboard creation requires Cloud Monitoring API integration"}
    
    def create_uptime_check(self, **kwargs) -> Dict[str, Any]:
        """Create uptime check (placeholder)."""
        return {"success": False, "error": "Uptime check creation not yet implemented"}
    
    def list_error_groups(self, **kwargs) -> Dict[str, Any]:
        """List error groups (placeholder)."""
        return {"success": False, "error": "Error group listing not yet implemented"}
    
    def create_slo(self, **kwargs) -> Dict[str, Any]:
        """Create Service Level Objective (placeholder)."""
        return {"success": False, "error": "SLO creation not yet implemented"}
