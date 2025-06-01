#!/usr/bin/env python3
"""
Quick test script untuk verify ADK GCP system
"""

import sys
import os

def test_imports():
    """Test basic imports."""
    print("🧪 Testing imports...")
    
    try:
        # Test individual imports
        from adk_cli_agent.tools.gcp.agents import RootGCPAgent
        print("  ✅ RootGCPAgent")
        
        from adk_cli_agent.tools.gcp.base import ToolContext
        print("  ✅ ToolContext")
        
        from adk_cli_agent.tools.gcp.tools import create_gcp_project
        print("  ✅ Project tools")
        
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_instantiation():
    """Test that classes can be instantiated."""
    print("\n🏗️  Testing instantiation...")
    
    try:
        from adk_cli_agent.tools.gcp.agents import RootGCPAgent
        from adk_cli_agent.tools.gcp.base import ToolContext
        
        # Create instances
        context = ToolContext()
        print(f"  ✅ ToolContext: {context.session_id}")
        
        agent = RootGCPAgent()
        print(f"  ✅ RootGCPAgent: {agent.name}")
        
        return True
    except Exception as e:
        print(f"  ❌ Instantiation error: {e}")
        return False

def test_environment():
    """Test environment setup."""
    print("\n🌍 Testing environment...")
    
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        print("  ✅ API key found")
    else:
        print("  ⚠️  No API key (set GOOGLE_API_KEY or OPENAI_API_KEY)")
    
    # Check if ADK is available
    try:
        import subprocess
        result = subprocess.run(["adk", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ ADK command available")
        else:
            print("  ❌ ADK command not working")
    except FileNotFoundError:
        print("  ❌ ADK command not found")
    
    return True

def main():
    """Run all tests."""
    print("🚀 Quick ADK System Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_instantiation, 
        test_environment
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    if all(results):
        print("🎉 All tests passed! System is ready.")
        return 0
    else:
        print("❌ Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
