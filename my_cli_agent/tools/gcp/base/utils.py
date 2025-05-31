"""Utility functions for GCP tools."""

import re
import os
from typing import Optional, Dict, Any, List
from .exceptions import GCPValidationError, GCPConfigurationError


def validate_project_id(project_id: str) -> str:
    """
    Validate GCP project ID format.
    
    Args:
        project_id: The project ID to validate
        
    Returns:
        The validated project ID
        
    Raises:
        GCPValidationError: If project ID format is invalid
    """
    if not project_id:
        raise GCPValidationError("Project ID cannot be empty")
    
    if len(project_id) < 6 or len(project_id) > 30:
        raise GCPValidationError("Project ID must be between 6 and 30 characters")
    
    # GCP project ID rules: lowercase letters, digits, and hyphens
    # Must start with lowercase letter, cannot end with hyphen
    pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
    if not re.match(pattern, project_id):
        raise GCPValidationError(
            "Project ID must start with lowercase letter, contain only "
            "lowercase letters, digits, and hyphens, and cannot end with hyphen"
        )
    
    return project_id


def validate_vpc_name(vpc_name: str) -> str:
    """
    Validate VPC network name format.
    
    Args:
        vpc_name: The VPC name to validate
        
    Returns:
        The validated VPC name
        
    Raises:
        GCPValidationError: If VPC name format is invalid
    """
    if not vpc_name:
        raise GCPValidationError("VPC name cannot be empty")
    
    if len(vpc_name) > 63:
        raise GCPValidationError("VPC name cannot exceed 63 characters")
    
    # VPC name rules: lowercase letters, digits, and hyphens
    # Must start with lowercase letter or digit
    pattern = r'^[a-z0-9][a-z0-9-]*[a-z0-9]$'
    if not re.match(pattern, vpc_name) and len(vpc_name) > 1:
        raise GCPValidationError(
            "VPC name must start with lowercase letter or digit, "
            "contain only lowercase letters, digits, and hyphens"
        )
    
    return vpc_name


def validate_subnet_name(subnet_name: str) -> str:
    """
    Validate subnet name format.
    
    Args:
        subnet_name: The subnet name to validate
        
    Returns:
        The validated subnet name
        
    Raises:
        GCPValidationError: If subnet name format is invalid
    """
    return validate_vpc_name(subnet_name)  # Same rules as VPC


def validate_cidr_range(cidr: str) -> str:
    """
    Validate CIDR range format.
    
    Args:
        cidr: The CIDR range to validate (e.g., "10.0.0.0/24")
        
    Returns:
        The validated CIDR range
        
    Raises:
        GCPValidationError: If CIDR format is invalid
    """
    if not cidr:
        raise GCPValidationError("CIDR range cannot be empty")
    
    # Basic CIDR format validation
    pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if not re.match(pattern, cidr):
        raise GCPValidationError(
            "CIDR range must be in format 'x.x.x.x/y' (e.g., '10.0.0.0/24')"
        )
    
    # Validate IP octets and prefix length
    ip_part, prefix = cidr.split('/')
    octets = ip_part.split('.')
    
    for octet in octets:
        if not (0 <= int(octet) <= 255):
            raise GCPValidationError(f"Invalid IP octet: {octet}")
    
    prefix_len = int(prefix)
    if not (0 <= prefix_len <= 32):
        raise GCPValidationError(f"Invalid prefix length: {prefix_len}")
    
    return cidr


def validate_region(region: str) -> str:
    """
    Validate GCP region format.
    
    Args:
        region: The region to validate
        
    Returns:
        The validated region
        
    Raises:
        GCPValidationError: If region format is invalid
    """
    if not region:
        raise GCPValidationError("Region cannot be empty")
    
    # Basic region format validation (e.g., us-central1, europe-west1)
    pattern = r'^[a-z]+-[a-z0-9]+\d+$'
    if not re.match(pattern, region):
        raise GCPValidationError(
            "Region must be in format 'area-location#' (e.g., 'us-central1')"
        )
    
    return region


def validate_zone(zone: str) -> str:
    """
    Validate GCP zone format.
    
    Args:
        zone: The zone to validate
        
    Returns:
        The validated zone
        
    Raises:
        GCPValidationError: If zone format is invalid
    """
    if not zone:
        raise GCPValidationError("Zone cannot be empty")
    
    # Basic zone format validation (e.g., us-central1-a)
    pattern = r'^[a-z]+-[a-z0-9]+\d+-[a-z]$'
    if not re.match(pattern, zone):
        raise GCPValidationError(
            "Zone must be in format 'region-letter' (e.g., 'us-central1-a')"
        )
    
    return zone


def get_default_project_id() -> Optional[str]:
    """
    Get the default GCP project ID from environment or gcloud config.
    
    Returns:
        The default project ID or None if not found
    """
    # Try environment variable first
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if project_id:
        return project_id
    
    project_id = os.environ.get('GCP_PROJECT')
    if project_id:
        return project_id
    
    # Try gcloud config (this would require subprocess call)
    # For now, return None - can be enhanced later
    return None


def format_resource_name(resource_type: str, name: str, project_id: str, 
                        region: Optional[str] = None, zone: Optional[str] = None) -> str:
    """
    Format a full GCP resource name.
    
    Args:
        resource_type: Type of resource (projects, networks, subnetworks, etc.)
        name: Resource name
        project_id: GCP project ID
        region: Region (optional)
        zone: Zone (optional)
        
    Returns:
        Formatted resource name
    """
    if resource_type == "projects":
        return f"projects/{project_id}"
    
    base = f"projects/{project_id}"
    
    if zone:
        base += f"/zones/{zone}"
    elif region:
        base += f"/regions/{region}"
    else:
        base += "/global"
    
    return f"{base}/{resource_type}/{name}"


def parse_labels(labels_str: str) -> Dict[str, str]:
    """
    Parse labels from string format to dictionary.
    
    Args:
        labels_str: Labels in format "key1=value1,key2=value2"
        
    Returns:
        Dictionary of labels
        
    Raises:
        GCPValidationError: If label format is invalid
    """
    if not labels_str:
        return {}
    
    labels = {}
    for label_pair in labels_str.split(','):
        label_pair = label_pair.strip()
        if '=' not in label_pair:
            raise GCPValidationError(f"Invalid label format: {label_pair}")
        
        key, value = label_pair.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        if not key:
            raise GCPValidationError("Label key cannot be empty")
        
        labels[key] = value
    
    return labels


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to remove sensitive information.
    
    Args:
        error: The exception to sanitize
        
    Returns:
        Sanitized error message
    """
    message = str(error)
    
    # Remove potential sensitive information
    # This can be expanded based on specific needs
    sensitive_patterns = [
        r'Bearer [a-zA-Z0-9._-]+',  # Bearer tokens
        r'key=[a-zA-Z0-9._-]+',     # API keys
    ]
    
    for pattern in sensitive_patterns:
        message = re.sub(pattern, '[REDACTED]', message)
    
    return message


def normalize_resource_name(name: str) -> str:
    """
    Normalize a resource name to conform to GCP naming standards.
    
    Args:
        name: Input name to normalize
        
    Returns:
        Normalized name following GCP conventions
        
    Raises:
        GCPValidationError: If name cannot be normalized
    """
    if not name or not isinstance(name, str):
        from .exceptions import GCPValidationError
        raise GCPValidationError("Resource name must be a non-empty string")
    
    # Convert to lowercase and replace invalid characters
    normalized = name.lower()
    
    # Replace underscores and spaces with hyphens
    normalized = normalized.replace('_', '-').replace(' ', '-')
    
    # Remove any characters that aren't alphanumeric or hyphens
    import re
    normalized = re.sub(r'[^a-z0-9-]', '', normalized)
    
    # Remove consecutive hyphens
    normalized = re.sub(r'-+', '-', normalized)
    
    # Remove leading/trailing hyphens
    normalized = normalized.strip('-')
    
    # Ensure it starts with a letter
    if normalized and not normalized[0].isalpha():
        normalized = f"gcp-{normalized}"
    
    # Validate length (GCP resources typically have 1-63 character limits)
    if len(normalized) > 63:
        normalized = normalized[:63].rstrip('-')
    
    if not normalized:
        from .exceptions import GCPValidationError
        raise GCPValidationError(f"Cannot normalize resource name '{name}' - results in empty string")
    
    return normalized


def parse_resource_url(resource_url: str) -> Dict[str, str]:
    """
    Parse a GCP resource URL to extract components.
    
    Args:
        resource_url: The GCP resource URL to parse
        
    Returns:
        Dictionary containing parsed components
    """
    components = {}
    
    # Handle different URL formats
    if '/projects/' in resource_url:
        parts = resource_url.split('/')
        try:
            project_idx = parts.index('projects') + 1
            components['project'] = parts[project_idx]
            
            if 'regions' in parts:
                region_idx = parts.index('regions') + 1
                components['region'] = parts[region_idx]
                
            if 'zones' in parts:
                zone_idx = parts.index('zones') + 1
                components['zone'] = parts[zone_idx]
                
            if 'networks' in parts:
                network_idx = parts.index('networks') + 1
                components['network'] = parts[network_idx]
                
            if 'subnetworks' in parts:
                subnet_idx = parts.index('subnetworks') + 1
                components['subnetwork'] = parts[subnet_idx]
                
        except (ValueError, IndexError):
            pass  # Best effort parsing
            
    return components


def format_resource_labels(labels: Dict[str, str]) -> List[str]:
    """
    Format resource labels for display or API calls.
    
    Args:
        labels: Dictionary of label key-value pairs
        
    Returns:
        List of formatted label strings
    """
    return [f"{key}={value}" for key, value in labels.items()]
