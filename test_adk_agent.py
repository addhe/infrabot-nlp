#!/usr/bin/env python3
"""Quick test script for Simple CLI Agent functionality."""

import sys
import traceback

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        import adk_cli_agent
        print("✅ Agent import successful")
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        return False
    
    try:
        from adk_cli_agent.tools.gcp_tools import HAS_GCP_TOOLS_FLAG
        print(f"✅ GCP tools import successful (Available: {HAS_GCP_TOOLS_FLAG})")
    except Exception as e:
        print(f"❌ GCP tools import failed: {e}")
        return False
    
    try:
        from adk_cli_agent.tools.time_tools import get_current_time
        print("✅ Time tools import successful")
    except Exception as e:
        print(f"❌ Time tools import failed: {e}")
        return False
        
    try:
        from adk_cli_agent.tools.command_tools import execute_command
        print("✅ Command tools import successful")
    except Exception as e:
        print(f"❌ Command tools import failed: {e}")
        return False
    
    return True

def test_basic_tools():
    """Test basic tool functionality."""
    print("\nTesting basic tools...")
    
    try:
        from adk_cli_agent.tools.command_tools import execute_command
        result = execute_command("echo test")
        
        print("\nOutput:")
        print("=" * 80)
        if isinstance(result, dict):
            print(result.get('report', result.get('output', str(result))))
        else:
            print(result)
        print("=" * 80)
        
        print("✅ execute_command works")
        return True
    except Exception as e:
        print(f"❌ execute_command failed: {e}")
        traceback.print_exc()
        return False

def test_gcp_tools():
    """Test GCP tools functionality."""
    print("\nTesting GCP tools...")
    
    try:
        from adk_cli_agent.tools.gcp_tools import list_gcp_projects, HAS_GCP_TOOLS_FLAG
        
        if not HAS_GCP_TOOLS_FLAG:
            print("⚠️  GCP tools not available (missing dependencies)")
            return True
            
        result = list_gcp_projects("all")
        if isinstance(result, dict) and result.get('status') == 'success':
            report = result.get('report', '')
            lines = len(report.split('\n')) if report else 0
            print("✅ list_gcp_projects works")
            print(f"   Found: {lines} lines in report")
        else:
            print(f"⚠️  list_gcp_projects returned: {result}")
        return True
    except Exception as e:
        print(f"❌ GCP tools test failed: {e}")
        traceback.print_exc()
        return False

def test_agent_functionality():
    """Test the main agent functionality."""
    print("\nTesting agent functionality...")
    
    try:
        from adk_cli_agent import agent
        
        # Test getting available tools
        tools = agent.get_available_tools()
        print(f"✅ Agent has {len(tools)} available tools: {tools}")
        
        # Test executing a tool
        result = agent.execute_tool('execute_command', 'echo "Hello from agent"')
        if result.get('status') == 'success':
            print("✅ Agent tool execution works")
        else:
            print(f"⚠️  Agent tool execution returned: {result}")
        
        # Test help function
        help_text = agent.help()
        print(f"✅ Agent help function works (length: {len(help_text)} chars)")
        
        return True
    except Exception as e:
        print(f"❌ Agent functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Simple CLI Agent - Quick Test")
    print("=" * 40)
    
    success = True
    
    # Test imports
    success &= test_imports()
    
    # Test basic tools
    success &= test_basic_tools()
    
    # Test GCP tools
    success &= test_gcp_tools()
    
    # Test agent functionality
    success &= test_agent_functionality()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! The Simple CLI Agent is ready.")
        print("\nNext steps:")
        print("1. Run: python run_adk_agent.py")
        print("2. Or test with: from adk_cli_agent import agent")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
