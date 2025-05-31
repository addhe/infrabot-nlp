"""Base types and data structures for GCP tools."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class GCPResourceStatus(Enum):
    """Standard GCP resource status values."""
    CREATING = "CREATING"
    READY = "READY"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    STOPPING = "STOPPING"
    DELETING = "DELETING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class GCPRegion(Enum):
    """Common GCP regions."""
    US_CENTRAL1 = "us-central1"
    US_EAST1 = "us-east1"
    US_WEST1 = "us-west1"
    EUROPE_WEST1 = "europe-west1"
    ASIA_SOUTHEAST1 = "asia-southeast1"
    ASIA_NORTHEAST1 = "asia-northeast1"


@dataclass
class GCPResource:
    """Base class for all GCP resources."""
    id: str
    name: str
    status: str
    resource_type: str
    region: Optional[str] = None
    zone: Optional[str] = None
    project_id: Optional[str] = None
    created_time: Optional[str] = None
    updated_time: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'resource_type': self.resource_type,
            'region': self.region,
            'zone': self.zone,
            'project_id': self.project_id,
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'labels': self.labels,
            'metadata': self.metadata
        }


@dataclass
class GCPProject(GCPResource):
    """GCP Project resource."""
    organization_id: Optional[str] = None
    display_name: Optional[str] = None
    
    def __post_init__(self):
        self.resource_type = "project"


@dataclass
class GCPVPC(GCPResource):
    """GCP VPC resource."""
    auto_create_subnetworks: bool = False
    routing_mode: str = "REGIONAL"
    mtu: int = 1460
    
    def __post_init__(self):
        self.resource_type = "vpc"


@dataclass
class GCPSubnet(GCPResource):
    """GCP Subnet resource."""
    vpc_name: str = ""
    ip_cidr_range: str = ""
    gateway_address: Optional[str] = None
    secondary_ip_ranges: list = field(default_factory=list)
    private_ip_google_access: bool = False
    
    def __post_init__(self):
        self.resource_type = "subnet"


@dataclass
class GCPOperation:
    """Represents a GCP operation result."""
    operation: str  # create, read, update, delete
    resource_type: str
    resource: Optional[GCPResource] = None
    success: bool = True
    message: str = ""
    error_code: Optional[str] = None
    duration: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary representation."""
        result = {
            'operation': self.operation,
            'resource_type': self.resource_type,
            'success': self.success,
            'message': self.message
        }
        
        if self.resource:
            result['resource'] = self.resource.to_dict()
        
        if self.error_code:
            result['error_code'] = self.error_code
            
        if self.duration:
            result['duration'] = self.duration
            
        return result
