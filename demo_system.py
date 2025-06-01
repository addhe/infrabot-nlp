#!/usr/bin/env python3
"""
Demo lengkap ADK GCP system tanpa perlu API key nyata.
Menunjukkan delegation system dan mock responses.
"""

import asyncio
import sys
from typing import Dict, Any

# Import ADK components
from adk_cli_agent.tools.gcp.agents import RootGCPAgent
from adk_cli_agent.tools.gcp.base import ToolContext
from adk_cli_agent.tools.gcp.tools import (
    create_gcp_project, 
    list_gcp_projects,
    ComputeTools
)

class MockDemo:
    """Demo class dengan mock responses untuk testing tanpa API key."""
    
    def __init__(self):
        self.context = ToolContext()
        self.agent = RootGCPAgent()
        
    async def demo_imports(self):
        """Demo testing imports dan instantiation."""
        print("🧪 Demo 1: System Components")
        print("=" * 50)
        
        print(f"✅ ToolContext created: {self.context.session_id}")
        print(f"✅ RootGCPAgent created: {self.agent.name}")
        print(f"📋 Agent description: {self.agent.description}")
        
        # Show agent status
        status = self.agent.get_agent_status()
        print(f"🔍 Total agents: {status['total_agents']}")
        print(f"📊 Sub-agents: {list(status['sub_agents'].keys())}")
        
    async def demo_delegation_logic(self):
        """Demo delegation system tanpa API calls."""
        print("\n🎯 Demo 2: Agent Delegation Logic")
        print("=" * 50)
        
        # Test delegation logic
        test_queries = [
            "List all GCP projects",
            "Create a VM instance in us-central1-a", 
            "Show storage buckets",
            "Set up a complex multi-service architecture"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            
            # Test routing logic (tidak perlu API key)
            routing = await self.agent.route_request(query, self.context)
            print(f"   🎯 Route to: {routing['route_to']}")
            print(f"   🏷️  Operation: {routing['operation_type']}")
            print(f"   💭 Reasoning: {routing['reasoning']}")
    
    async def demo_tool_functions(self):
        """Demo tool functions dengan mock responses."""
        print("\n🔧 Demo 3: Tool Functions (Mock Mode)")
        print("=" * 50)
        
        # Demo project tools
        print("\n📁 Project Tools:")
        
        # Mock create project
        try:
            project_result = await create_gcp_project(
                project_id="demo-project-123",
                name="Demo Project",
                tool_context=self.context
            )
            print(f"   ✅ Create project: {project_result['status']}")
            print(f"   📋 Message: {project_result['message']}")
        except Exception as e:
            print(f"   ⚠️  Mock response: {str(e)}")
        
        # Mock list projects
        try:
            list_result = await list_gcp_projects(
                tool_context=self.context
            )
            print(f"   ✅ List projects: {list_result['status']}")
            print(f"   📊 Found: {len(list_result.get('data', {}).get('projects', []))} projects")
        except Exception as e:
            print(f"   ⚠️  Mock response: {str(e)}")
        
        # Demo compute tools
        print("\n💻 Compute Tools:")
        
        try:
            from adk_cli_agent.tools.gcp.tools.compute_tools import create_vm_instance
            
            vm_result = await create_vm_instance(
                name="demo-vm",
                project_id="demo-project",
                zone="us-central1-a",
                tool_context=self.context
            )
            print(f"   ✅ Create VM: {vm_result['status']}")
            print(f"   📋 Message: {vm_result['message']}")
        except Exception as e:
            print(f"   ⚠️  Mock response: {str(e)}")
    
    async def demo_context_management(self):
        """Demo context dan state management."""
        print("\n📊 Demo 4: Context & State Management")
        print("=" * 50)
        
        # Show context state
        print(f"🆔 Session ID: {self.context.session_id}")
        print(f"⏰ Created: {self.context.created_at}")
        print(f"🔧 GCP Config: {self.context.gcp_config}")
        
        # Update context
        self.context.set_metadata("demo_mode", True)
        self.context.set_metadata("test_user", "developer")
        
        # Update GCP config
        self.context.gcp_config["project_id"] = "demo-project"
        self.context.gcp_config["region"] = "us-central1"
        
        print(f"✅ Updated metadata: {self.context.metadata}")
        print(f"✅ Updated GCP config: {self.context.gcp_config}")
        
        # Show state
        print(f"📝 State keys: {list(self.context.state.keys())}")
    
    async def demo_error_handling(self):
        """Demo error handling system."""
        print("\n⚠️  Demo 5: Error Handling")
        print("=" * 50)
        
        # Test dengan input yang invalid
        test_cases = [
            {"name": "", "project": "test"},  # Empty name
            {"name": "test", "project": ""},  # Empty project
            {"name": "test-vm", "project": "invalid-project-id-that-is-too-long"},  # Invalid project
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n🧪 Test Case {i}: {case}")
            
            try:
                from adk_cli_agent.tools.gcp.tools.compute_tools import create_vm_instance
                
                result = await create_vm_instance(
                    name=case["name"],
                    project_id=case["project"],
                    zone="us-central1-a",
                    tool_context=self.context
                )
                
                if result["status"] == "error":
                    print(f"   ✅ Error handled: {result['message']}")
                else:
                    print(f"   ⚠️  Unexpected success: {result}")
                    
            except Exception as e:
                print(f"   ✅ Exception caught: {str(e)}")

async def main():
    """Main demo function."""
    print("🚀 ADK GCP System Demo")
    print("🔧 Mode: Local Testing (No API required)")
    print("=" * 60)
    
    demo = MockDemo()
    
    # Run all demos
    demos = [
        demo.demo_imports,
        demo.demo_delegation_logic,
        demo.demo_tool_functions,
        demo.demo_context_management,
        demo.demo_error_handling
    ]
    
    for demo_func in demos:
        try:
            await demo_func()
            input("\n⏯️  Press Enter to continue...")
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user.")
            break
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            input("\n⏯️  Press Enter to continue...")
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\n📚 Next Steps:")
    print("1. Set GOOGLE_API_KEY untuk real LLM responses")
    print("2. Setup GCP credentials untuk real operations")
    print("3. Try interactive mode: python interactive_demo.py")
    print("4. Read RUNNING_GUIDE.md untuk panduan lengkap")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
