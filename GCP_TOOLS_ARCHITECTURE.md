# GCP Tools Architecture with Agent Teams

## Overview

Dokumen ini menjelaskan arsitektur berbasis Agent Teams untuk Google Cloud Platform (GCP) tools dalam proyek infrabot-nlp. Arsitektur ini dirancang untuk:
- Meningkatkan skalabilitas dan maintainability
- Memisahkan tanggung jawab berdasarkan domain GCP
- Memanfaatkan kekuatan Google ADK untuk orkestrasi agent
- Menyediakan antarmuka yang konsisten untuk pengguna

## Current State vs. Target State

### Current State
- File `gcp_tools.py` tunggal yang monolitik
- Operasi terbatas pada manajemen proyek
- Pemisahan tanggung jawab yang kurang jelas

### Target State
- Arsitektur berbasis Agent Teams
- Setiap layanan GCP memiliki agent khusus
- Delegasi tugas yang cerdas antar agent
- Manajemen state dan session yang terpusat
- Standarisasi error handling dan logging

## Architecture Principles

### 1. Agent-Based Specialization
- Setiap agent fokus pada domain spesifik GCP
- Agent root bertindak sebagai orchestrator
- Delegasi otomatis berdasarkan keahlian agent

### 2. Standardized Operations
Setiap agent mengimplementasikan operasi standar:
- **Create**: Membuat resource baru
- **Read**: Melihat daftar dan detail resource
- **Update**: Memodifikasi resource yang ada
- **Delete**: Menghapus resource

### 3. Layered Architecture with Agent Teams
```
┌─────────────────────────────────────┐
│         Root Agent                 │  # Entry point, delegasi ke agent spesialis
├─────────────────────────────────────┤
│       Specialized Agents           │  # Agent spesialis per domain GCP
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Project     │ │ Compute     │   │
│  │ Agent       │ │ Agent       │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Storage     │ │ Network     │   │
│  │ Agent       │ │ Agent       │   │
│  └─────────────┘ └─────────────┘   │
├─────────────────────────────────────┤
│       GCP Client Layer             │  # Interaksi dengan GCP APIs
├─────────────────────────────────────┤
│       Shared Utilities             │  # Utilitas dan helpers bersama
└─────────────────────────────────────┘
```

## Agent-Based Directory Structure

```
adk_cli_agent/
├── __init__.py
├── agent.py                      # Root agent dan inisialisasi
└── tools/
    ├── __init__.py
    ├── gcp/                      # GCP Agent Teams
    │   ├── __init__.py           # Ekspor agent dan tools GCP
    │   ├── base/
    │   │   ├── __init__.py
    │   │   ├── client.py         # Manajemen koneksi GCP
    │   │   ├── exceptions.py     # Exception khusus GCP
    │   │   └── types.py          # Tipe data umum
    │   │
    │   ├── agents/           # Agent spesialis
    │   │   ├── __init__.py
    │   │   ├── project_agent.py   # Manajemen proyek
    │   │   ├── compute_agent.py   # GCE, GKE
    │   │   ├── storage_agent.py   # Cloud Storage, Cloud SQL
    │   │   ├── network_agent.py   # VPC, Firewall, DNS
    │   │   ├── security_agent.py  # IAM, Secret Manager
    │   │   └── pubsub_agent.py    # Pub/Sub
    │   │
    │   └── tools/            # Tools untuk agent
    │       ├── __init__.py
    │       ├── project_tools.py
    │       ├── compute_tools.py
    │       ├── storage_tools.py
    │       ├── network_tools.py
    │       └── security_tools.py
    │
    └── shared/                 # Utilitas bersama
        ├── __init__.py
        ├── auth.py              # Autentikasi dan otorisasi
        ├── decorators.py        # Decorator umum
        └── utils.py             # Fungsi utilitas

tests/
├── unit/
│   └── adk_cli_agent/
│       └── tools/
│           └── gcp/
│               └── test_agents/  # Test untuk setiap agent
└── integration/
    └── gcp/                # Test integrasi dengan GCP
```

## Implementation Strategy with Agent Teams

### Phase 1: Core Agent Infrastructure (Sprint 1)
1. **Setup Agent Base**
   - Implementasi base agent dengan ADK
   - Buat root agent untuk orkestrasi
   - Implementasi project_agent dengan tools dasar

2. **Authentication & Error Handling**
   - Sistem autentikasi terpusat
   - Standarisasi error handling
   - Logging dan monitoring dasar

### Phase 2: Core Services Agents (Sprint 2)
1. **Compute Agent**
   - Manajemen GCE instances
   - Operasi dasar GKE cluster

2. **Storage Agent**
   - Manajemen Cloud Storage
   - Operasi Cloud SQL

### Phase 3: Advanced Agents (Sprint 3)
1. **Network Agent**
   - Manajemen VPC, subnet, firewall
   - Konfigurasi DNS dan load balancing

2. **Security Agent**
   - Manajemen IAM
   - Operasi Secret Manager
   - Enkripsi dengan KMS

### Phase 4: Integration & Optimization (Sprint 4)
1. **Agent Collaboration**
   - Delegasi tugas antar agent
   - Shared state management
   - Optimasi performa

2. **Advanced Features**
   - Auto-scaling
   - Cost optimization
   - Security compliance checks

## Agent and Tool Standards

### Agent Definition
```python
# agents/base_agent.py
from adk import Agent

class BaseGCPAgent(Agent):
    """Base class for all GCP agents"""
    
    def __init__(self, name: str, description: str):
        super().__init__(
            name=name,
            description=description,
            tools=self._register_tools()
        )
    
    def _register_tools(self):
        """Register tools for this agent"""
        tools = []
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, '_is_tool'):
                tools.append(method)
        return tools

# agents/project_agent.py
class ProjectAgent(BaseGCPAgent):
    """Agent khusus untuk manajemen proyek GCP"""
    
    def __init__(self):
        super().__init__(
            name="gcp-project-agent",
            description="Manages GCP projects (create, list, update, delete)"
        )
    
    @tool
    async def create_project(self, project_id: str, name: str, **kwargs):
        """Create a new GCP project"""
        # Implementation here
        pass
```

### Tool Definition
```python
# tools/project_tools.py
from functools import wraps
from typing import Dict, Any, Optional

from ..base.exceptions import GCPToolsError

def handle_gcp_errors(func):
    """Decorator untuk menangani error GCP"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except GCPToolsError as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, 'code', 'UNKNOWN_ERROR')
            }
    return wrapper

@handle_gcp_errors
async def create_gcp_project(
    project_id: str,
    name: str,
    organization_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Buat proyek GCP baru
    
    Args:
        project_id: ID unik untuk proyek
        name: Nama tampilan proyek
        organization_id: ID organisasi (opsional)
        
    Returns:
        Dict berisi status dan detail proyek
    """
    # Implementation here
    pass
```

### Response Format
```python
# base/types.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class GCPResource:
    """Base class for all GCP resources"""
    resource_type: str
    resource_id: str
    name: str
    status: str
    region: Optional[str] = None
    zone: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolResult:
    """Standard response format for all tools"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data or {},
            "errors": self.errors or []
        }
```

### Error Handling
```python
# base/exceptions.py
class GCPToolsError(Exception):
    """Base exception untuk semua error GCP tools"""
    code = "GCP_ERROR"
    
    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class GCPAuthenticationError(GCPToolsError):
    """Error autentikasi/otorisasi"""
    code = "AUTHENTICATION_ERROR"

class GCPResourceNotFoundError(GCPToolsError):
    """Resource tidak ditemukan"""
    code = "RESOURCE_NOT_FOUND"

class GCPQuotaExceededError(GCPToolsError):
    """Kuota terlampaui"""
    code = "QUOTA_EXCEEDED"

class GCPValidationError(GCPToolsError):
    """Validasi input gagal"""
    code = "VALIDATION_ERROR"
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
