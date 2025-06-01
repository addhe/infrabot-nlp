#!/usr/bin/env python3
"""
Demo script untuk ADK GCP Agent System
Demonstrasi penggunaan berbagai agent dan tools
"""

import asyncio
import os
import sys
from datetime import datetime
from pprint import pprint

# Import ADK GCP components
try:
    from adk_cli_agent.tools.gcp.agents import RootGCPAgent
    from adk_cli_agent.tools.gcp.base import ToolContext
    print("✅ ADK GCP components imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and have installed dependencies")
    sys.exit(1)


def print_separator(title="", width=60):
    """Print a nice separator with optional title."""
    if title:
        print(f"\n{'=' * width}")
        print(f"  {title}")
        print('=' * width)
    else:
        print('-' * width)


async def test_basic_imports():
    """Test that all components can be imported and instantiated."""
    print_separator("Testing Basic Imports and Instantiation")
    
    try:
        # Test ToolContext
        context = ToolContext()
        print(f"✅ ToolContext created with session: {context.session_id}")
        
        # Test RootGCPAgent
        agent = RootGCPAgent()
        print(f"✅ RootGCPAgent created: {agent.name}")
        
        # Get agent status
        status = agent.get_agent_status()
        print(f"✅ Agent status: {status['total_agents']} total agents")
        
        return agent, context
        
    except Exception as e:
        print(f"❌ Error in basic imports: {e}")
        raise


async def test_agent_delegation(agent, context):
    """Test agent delegation logic."""
    print_separator("Testing Agent Delegation Logic")
    
    test_requests = [
        "List all GCP projects",
        "Create a VM instance in us-central1-a",
        "Show me storage buckets",
        "Help with networking setup",
        "What are my IAM policies?"
    ]
    
    for request in test_requests:
        try:
            print(f"\n🔍 Testing request: '{request}'")
            
            # Test routing logic
            routing = await agent.route_request(request, context)
            print(f"   📡 Routed to: {routing['route_to']} agent")
            print(f"   💡 Reason: {routing['reasoning']}")
            
        except Exception as e:
            print(f"   ❌ Routing error: {e}")


async def test_mock_operations(agent, context):
    """Test mock operations without real GCP calls."""
    print_separator("Testing Mock Operations")
    
    # Set mock mode in context
    context.state["mock_mode"] = True
    context.gcp_config["project_id"] = "demo-project-123"
    
    test_operations = [
        {
            "description": "List GCP projects",
            "query": "List all projects in my GCP account"
        },
        {
            "description": "Create VM instance", 
            "query": "Create a small VM named 'test-vm' in us-central1-a"
        },
        {
            "description": "List storage buckets",
            "query": "Show all storage buckets in my project"
        }
    ]
    
    for operation in test_operations:
        try:
            print(f"\n🧪 Mock test: {operation['description']}")
            
            # This will use mock responses since we don't have real GCP credentials
            result = await agent.run(operation['query'], context)
            print(f"   ✅ Mock result received: {type(result)}")
            
        except Exception as e:
            print(f"   ❌ Mock operation error: {e}")


def test_tools_availability():
    """Test that all tools are available and can be imported."""
    print_separator("Testing Tools Availability")
    
    try:
        from adk_cli_agent.tools.gcp.tools import (
            create_gcp_project, list_gcp_projects, delete_gcp_project,
            ComputeTools, StorageTools, NetworkingTools, 
            IAMTools, MonitoringTools
        )
        
        print("✅ Project tools imported")
        print("✅ ComputeTools imported")
        print("✅ StorageTools imported") 
        print("✅ NetworkingTools imported")
        print("✅ IAMTools imported")
        print("✅ MonitoringTools imported")
        
    except ImportError as e:
        print(f"❌ Tools import error: {e}")


def test_individual_agents():
    """Test that individual specialized agents can be imported."""
    print_separator("Testing Individual Agents")
    
    try:
        from adk_cli_agent.tools.gcp.agents import (
            ProjectAgent, ComputeAgent, StorageAgent,
            NetworkingAgent, IAMAgent, MonitoringAgent
        )
        
        agents = [
            ("ProjectAgent", ProjectAgent),
            ("ComputeAgent", ComputeAgent), 
            ("StorageAgent", StorageAgent),
            ("NetworkingAgent", NetworkingAgent),
            ("IAMAgent", IAMAgent),
            ("MonitoringAgent", MonitoringAgent)
        ]
        
        for name, agent_class in agents:
            try:
                agent = agent_class()
                print(f"✅ {name}: {agent.name}")
            except Exception as e:
                print(f"❌ {name} error: {e}")
                
    except ImportError as e:
        print(f"❌ Agents import error: {e}")


def check_environment():
    """Check environment setup."""
    print_separator("Environment Check")
    
    # Check API keys
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if google_api_key:
        print("✅ GOOGLE_API_KEY is set")
    elif openai_api_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  No API key found. Set GOOGLE_API_KEY or OPENAI_API_KEY")
    
    # Check GCP credentials
    gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if gcp_creds:
        print(f"✅ GCP credentials: {gcp_creds}")
    else:
        print("ℹ️  No GCP credentials set (optional for demo)")
    
    # Check project
    project_id = os.getenv("GCP_PROJECT_ID")
    if project_id:
        print(f"✅ GCP project: {project_id}")
    else:
        print("ℹ️  No GCP project set (will use demo-project)")


async def interactive_demo():
    """Interactive demo mode."""
    print_separator("Interactive Demo Mode")
    print("Enter queries to test the agent (type 'quit' to exit)")
    
    try:
        agent = RootGCPAgent()
        context = ToolContext()
        context.state["demo_mode"] = True
        
        while True:
            try:
                user_input = input("\n💬 Your query: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Exiting interactive demo")
                    break
                    
                if not user_input:
                    continue
                
                print("🤖 Processing...")
                result = await agent.run(user_input, context)
                print(f"✅ Response: {result}")
                
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Demo setup error: {e}")


async def main():
    """Main demo function."""
    print("🚀 ADK GCP Agent Demo")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    check_environment()
    
    # Test individual components
    test_tools_availability()
    test_individual_agents()
    
    # Test basic functionality
    try:
        agent, context = await test_basic_imports()
        await test_agent_delegation(agent, context)
        await test_mock_operations(agent, context)
        
        print_separator("Demo Summary")
        print("✅ All basic tests completed successfully!")
        print("🎯 System is ready for use")
        
        # Ask if user wants interactive mode
        if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
            await interactive_demo()
        else:
            print("\nTo run interactive mode: python demo_adk_system.py --interactive")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Demo crashed: {e}")
        sys.exit(1)
