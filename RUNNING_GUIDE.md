# Panduan Menjalankan dan Test ADK CLI

## Ringkasan Sistem

ADK CLI Agent untuk GCP adalah sistem berbasis agent yang dirancang untuk mengelola infrastruktur Google Cloud Platform dengan delegation yang cerdas antar agent spesialis.

## 📋 Prerequisites

### 1. Dependencies
```bash
# Install ADK dan dependencies utama
pip install google-adk
pip install -r requirements.txt

# Atau install dalam development mode
pip install -e .
```

### 2. Environment Variables

#### API Keys (Wajib)
```bash
# Google API Key untuk LLM
export GOOGLE_API_KEY="your-google-api-key-here"

# Atau menggunakan OpenAI (alternatif)
export OPENAI_API_KEY="your-openai-api-key-here"
```

#### GCP Credentials (Opsional - untuk operasi GCP nyata)
```bash
# Setup GCP credentials
gcloud auth application-default login

# Atau set service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

# Set default project
export GCP_PROJECT_ID="your-gcp-project-id"
```

#### Debug Mode (Opsional)
```bash
export ADK_DEBUG=1  # Enable detailed logging
```

## 🚀 Cara Menjalankan

### Quick Start (Recommended)
```bash
# 1. Setup otomatis
./setup_adk.sh

# 2. Quick test
python3 quick_test.py

# 3. Run demo lengkap
python3 demo_system.py

# 4. Interactive mode
python3 interactive_demo.py
```

### Method 1: Demo Scripts
```bash
# Demo lengkap tanpa perlu API key
python3 demo_system.py

# Interactive CLI mode
python3 interactive_demo.py

# Quick system test
python3 quick_test.py
```

### Method 2: Manual Python
```bash
# Jalankan dalam mode interaktif
python -c "
import asyncio
from adk_cli_agent.tools.gcp.agents import RootGCPAgent

async def main():
    agent = RootGCPAgent()
    result = await agent.run('List all GCP projects')
    print(result)

asyncio.run(main())
"
```

## 🧪 Testing System

### 1. Unit Tests
```bash
# Jalankan semua unit tests
pytest tests/unit/ -v

# Test spesifik ADK agent
pytest tests/unit/adk_cli_agent/ -v

# Test tools GCP
pytest tests/unit/adk_cli_agent/tools/test_gcp_tools.py -v
```

### 2. Integration Tests
```bash
# Test integrasi (memerlukan GCP credentials)
pytest tests/integration/ -v

# Test compute tools
pytest tests/gcp/compute/ -v
```

### 3. Manual Testing

#### Test Import System
```bash
python -c "
print('Testing imports...')

# Test all agents import
from adk_cli_agent.tools.gcp.agents import (
    RootGCPAgent, ProjectAgent, ComputeAgent, 
    StorageAgent, NetworkingAgent, IAMAgent
)
print('✅ All agents imported successfully')

# Test tools import
from adk_cli_agent.tools.gcp.tools import (
    create_gcp_project, list_gcp_projects,
    ComputeTools, StorageTools, NetworkingTools
)
print('✅ All tools imported successfully')

# Test base components
from adk_cli_agent.tools.gcp.base import (
    ToolContext, GCPToolsError, GCPClient
)
print('✅ Base components imported successfully')
"
```

#### Test Agent Creation
```bash
python -c "
from adk_cli_agent.tools.gcp.agents import RootGCPAgent

# Create root agent
root_agent = RootGCPAgent()
print(f'✅ Root agent created: {root_agent.name}')
print(f'📋 Description: {root_agent.description}')

# Get agent status
status = root_agent.get_agent_status()
print(f'🔍 Total agents: {status[\"total_agents\"]}')
"
```

## 🎯 Contoh Penggunaan

### 1. Simple Demo
```bash
# Buat file demo sederhana
cat > simple_demo.py << 'EOF'
import asyncio
import os
from adk_cli_agent.tools.gcp.agents import RootGCPAgent
from adk_cli_agent.tools.gcp.base import ToolContext

async def demo():
    # Buat context
    context = ToolContext()
    
    # Buat root agent
    agent = RootGCPAgent()
    
    # Demo queries
    queries = [
        "List all available GCP projects",
        "Show me information about compute instances",
        "What networking tools are available?",
        "Help me understand GCP IAM"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        try:
            result = await agent.run(query, context)
            print(f"✅ Result: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(demo())
EOF

# Jalankan demo
python simple_demo.py
```

### 2. Interactive CLI Mode
```bash
# Buat interactive CLI
cat > interactive_cli.py << 'EOF'
import asyncio
import readline
from adk_cli_agent.tools.gcp.agents import RootGCPAgent
from adk_cli_agent.tools.gcp.base import ToolContext

async def interactive_mode():
    print("🤖 ADK GCP Agent Interactive Mode")
    print("Commands: 'help', 'status', 'quit'")
    print("-" * 50)
    
    context = ToolContext()
    agent = RootGCPAgent()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("""
Available commands:
- List projects: 'list all GCP projects'
- VM instances: 'show compute instances in my-project'
- Agent status: 'status'
- Help: 'help'
- Quit: 'quit'
                """)
                continue
            elif user_input.lower() == 'status':
                status = agent.get_agent_status()
                print(f"📊 Status: {status['total_agents']} agents ready")
                continue
            
            print("🤖 Agent: Processing...")
            result = await agent.run(user_input, context)
            print(f"✅ Agent: {result}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(interactive_mode())
EOF

# Jalankan interactive mode
python interactive_cli.py
```

### 3. Real GCP Operations Demo
```bash
# Demo dengan operasi GCP nyata (memerlukan credentials)
cat > gcp_operations_demo.py << 'EOF'
import asyncio
import os
from adk_cli_agent.tools.gcp.agents import RootGCPAgent
from adk_cli_agent.tools.gcp.base import ToolContext

async def gcp_demo():
    # Check credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GCP credentials not configured. Demo akan menggunakan mock responses.")
    
    context = ToolContext()
    agent = RootGCPAgent()
    
    # Set project context if available
    project_id = os.getenv("GCP_PROJECT_ID", "demo-project")
    context.gcp_config["project_id"] = project_id
    
    scenarios = [
        f"List all projects in my GCP account",
        f"Show compute instances in project {project_id}",
        f"List storage buckets in project {project_id}",
        f"Show IAM policies for project {project_id}",
        f"Create a small VM instance named 'test-vm' in us-central1-a"
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario}")
        try:
            result = await agent.execute_delegated_request(scenario, context)
            print(f"✅ Success: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("Press Enter to continue...")

if __name__ == "__main__":
    asyncio.run(gcp_demo())
EOF

# Jalankan GCP demo
python gcp_operations_demo.py
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Verify Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check if package is installable
pip install -e .

# Verify imports
python -c "import adk_cli_agent; print('✅ Package found')"
```

#### 2. ADK Command Not Found
```bash
# Install ADK
pip install google-adk

# Verify installation
adk --version

# Check PATH
which adk
```

#### 3. API Key Issues
```bash
# Verify API key is set
echo $GOOGLE_API_KEY

# Test API key (replace with your key)
python -c "
import os
import requests
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print('✅ API key is set')
else:
    print('❌ API key not found')
"
```

#### 4. Permission Errors
```bash
# Check GCP authentication
gcloud auth list

# Test default credentials
python -c "
from google.auth import default
try:
    credentials, project = default()
    print(f'✅ GCP credentials found for project: {project}')
except Exception as e:
    print(f'❌ GCP credentials error: {e}')
"
```

## 📊 Monitoring & Logs

### Log Locations
```bash
# ADK logs
tail -f /tmp/agents_log/agent.latest.log

# Python logs
export PYTHONPATH=$PWD
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# Run your code here
"
```

### Debug Mode
```bash
# Enable debug logging
export ADK_DEBUG=1
export PYTHONUNBUFFERED=1

# Run with detailed output
python run_adk_agent.py
```

## 🎯 Next Steps

1. **Explore Examples**: Check `examples/` folder untuk contoh penggunaan lebih lengkap
2. **Read Architecture**: Baca `GCP_TOOLS_ARCHITECTURE.md` untuk memahami design system
3. **Contribute**: Lihat `CONTRIBUTING.md` untuk panduan development
4. **Test Real GCP**: Setup credentials dan test dengan resources GCP nyata

## 🔗 Useful Commands Summary

```bash
# Quick start
export GOOGLE_API_KEY="your-key"
python run_adk_agent.py

# Test everything
pytest tests/ -v

# Interactive mode
python interactive_cli.py

# Check system
python -c "from adk_cli_agent.tools.gcp.agents import RootGCPAgent; print('✅ Ready')"
```

Happy coding! 🚀
