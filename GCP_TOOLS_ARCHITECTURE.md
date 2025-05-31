# GCP Tools Architecture Design

## Overview

This document outlines the modular architecture for Google Cloud Platform (GCP) tools in the infrabot-nlp project. The architecture is designed to be scalable, maintainable, and easily extensible for future GCP services.

## Current State vs. Target State

### Current State
- Single monolithic `gcp_tools.py` file
- Limited to project management operations
- Mixed concerns and responsibilities

### Target State
- Modular, service-based architecture
- Comprehensive GCP service coverage
- Clean separation of concerns
- Standardized interfaces and error handling

## Architecture Principles

### 1. Service-Based Modularity
Each GCP service (Compute, Storage, Networking, etc.) has its own dedicated module.

### 2. Standardized Operations
All modules implement consistent CRUD operations:
- **Create**: Create new resources
- **Read**: List and describe resources
- **Update**: Modify existing resources
- **Delete**: Remove resources

### 3. Layered Architecture
```
┌─────────────────────────────────────┐
│         Tool Interface Layer        │  # User-facing tool functions
├─────────────────────────────────────┤
│       Service Management Layer      │  # Business logic and orchestration
├─────────────────────────────────────┤
│         GCP Client Layer            │  # GCP API interactions
├─────────────────────────────────────┤
│         Utilities Layer             │  # Common utilities and helpers
└─────────────────────────────────────┘
```

## Directory Structure

```
my_cli_agent/tools/gcp/
├── __init__.py                    # Main GCP tools interface
├── base/
│   ├── __init__.py
│   ├── client.py                  # Base GCP client management
│   ├── exceptions.py              # Custom GCP exceptions
│   ├── types.py                   # Common type definitions
│   └── utils.py                   # Common utilities
├── compute/
│   ├── __init__.py
│   ├── gce.py                     # Google Compute Engine
│   ├── gke.py                     # Google Kubernetes Engine
│   └── load_balancer.py           # Load balancers
├── networking/
│   ├── __init__.py
│   ├── vpc.py                     # Virtual Private Cloud
│   ├── subnet.py                  # Subnets
│   ├── firewall.py                # Firewall rules
│   └── dns.py                     # Cloud DNS
├── storage/
│   ├── __init__.py
│   ├── cloud_storage.py           # Cloud Storage buckets
│   ├── cloud_sql.py               # Cloud SQL databases
│   └── persistent_disk.py         # Persistent disks
├── data/
│   ├── __init__.py
│   ├── redis.py                   # Redis instances
│   ├── memcache.py                # Memcached instances
│   └── pubsub.py                  # Pub/Sub topics and subscriptions
├── serverless/
│   ├── __init__.py
│   ├── cloud_run.py               # Cloud Run services
│   └── cloud_functions.py         # Cloud Functions
├── security/
│   ├── __init__.py
│   ├── iam.py                     # Identity and Access Management
│   ├── secret_manager.py          # Secret Manager
│   └── kms.py                     # Key Management Service
├── management/
│   ├── __init__.py
│   ├── projects.py                # Project management
│   ├── billing.py                 # Billing management
│   └── monitoring.py              # Monitoring and logging
└── tests/
    ├── __init__.py
    ├── test_compute/
    ├── test_networking/
    ├── test_storage/
    ├── test_data/
    ├── test_serverless/
    ├── test_security/
    └── test_management/
```

## Implementation Strategy

### Phase 1: Core Infrastructure (Current Sprint)
1. **Create base architecture**
   - `base/` module with common utilities
   - `management/projects.py` (migrate existing functionality)
   - `networking/vpc.py` and `networking/subnet.py`

2. **Establish patterns**
   - Standardized error handling
   - Consistent API interfaces
   - Common testing patterns

### Phase 2: Essential Services (Next Sprint)
1. **Compute services**
   - Google Compute Engine management
   - Basic GKE cluster operations

2. **Storage services**
   - Cloud Storage bucket management
   - Cloud SQL instance management

### Phase 3: Advanced Services (Future)
1. **Security and IAM**
2. **Serverless platforms**
3. **Data services**
4. **Monitoring and operations**

## Interface Standards

### Standard Function Signature
```python
def operation_resource(
    resource_id: str,
    project_id: Optional[str] = None,
    **kwargs
) -> ToolResult:
    """
    Perform operation on GCP resource.
    
    Args:
        resource_id: The resource identifier
        project_id: GCP project ID (optional, uses default if not provided)
        **kwargs: Additional resource-specific parameters
        
    Returns:
        ToolResult with success status and resource information
    """
```

### Standard Response Format
```python
@dataclass
class GCPResource:
    id: str
    name: str
    status: str
    region: Optional[str] = None
    zone: Optional[str] = None
    created_time: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

# ToolResult.result should contain:
{
    "operation": "create|read|update|delete",
    "resource_type": "vpc|subnet|instance|etc",
    "resource": GCPResource,
    "message": "Human-readable status message"
}
```

### Error Handling Standards
```python
class GCPToolsError(Exception):
    """Base exception for GCP tools"""
    pass

class GCPAuthenticationError(GCPToolsError):
    """Authentication/authorization errors"""
    pass

class GCPResourceNotFoundError(GCPToolsError):
    """Resource not found errors"""
    pass

class GCPQuotaExceededError(GCPToolsError):
    """Quota/limit exceeded errors"""
    pass
```

## Testing Strategy

### Test Categories
1. **Unit Tests**: Test individual functions with mocked GCP APIs
2. **Integration Tests**: Test with actual GCP APIs (using test projects)
3. **End-to-End Tests**: Full workflow testing

### Test Patterns
```python
class TestGCPService:
    @pytest.fixture
    def mock_gcp_client(self):
        # Standard GCP client mocking
        pass
    
    def test_create_resource_success(self, mock_gcp_client):
        # Test successful resource creation
        pass
        
    def test_create_resource_validation_error(self):
        # Test input validation
        pass
        
    def test_create_resource_api_error(self, mock_gcp_client):
        # Test API error handling
        pass
```

## Migration Plan

### Step 1: Refactor Current Code
1. Move existing `gcp_tools.py` functions to `management/projects.py`
2. Create base utilities and client management
3. Update existing tests to use new structure

### Step 2: Implement VPC and Subnet Tools
1. Create `networking/vpc.py` with VPC management functions
2. Create `networking/subnet.py` with subnet management functions
3. Add comprehensive test coverage

### Step 3: Update Tool Interface
1. Update main `gcp_tools.py` to import from new modules
2. Maintain backward compatibility
3. Add new VPC/subnet functionality to AI tool interface

## Benefits of This Architecture

### 1. Maintainability
- Clear separation of concerns
- Easy to locate and modify specific functionality
- Reduced code duplication

### 2. Scalability
- Easy to add new GCP services
- Modular testing approach
- Independent development of features

### 3. Consistency
- Standardized interfaces across all services
- Consistent error handling and logging
- Uniform testing patterns

### 4. Extensibility
- Plugin-like architecture for new services
- Easy integration with existing codebase
- Clear patterns for future development

## Next Steps

1. **Create base infrastructure** (this sprint)
2. **Migrate existing project management** (this sprint)
3. **Implement VPC and subnet management** (this sprint)
4. **Add comprehensive testing** (this sprint)
5. **Plan Phase 2 services** (next sprint planning)

This architecture provides a solid foundation for comprehensive GCP management while maintaining clean, maintainable code that follows established patterns and best practices.
