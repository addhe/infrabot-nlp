#!/usr/bin/env python3
"""
Complete GCP ADK Agent Demo

This script demonstrates the complete GCP Agent Development Kit (ADK) architecture
with all specialized agents working together for infrastructure management.

Run this script to see the multi-agent delegation system in action.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    # Import all our specialized agents
    from adk_cli_agent.tools.gcp.agents.root_agent import RootAgent
    from adk_cli_agent.tools.gcp.agents.project_agent import ProjectAgent
    from adk_cli_agent.tools.gcp.agents.compute_agent import ComputeAgent
    from adk_cli_agent.tools.gcp.agents.networking_agent import NetworkingAgent
    from adk_cli_agent.tools.gcp.agents.storage_agent import StorageAgent
    from adk_cli_agent.tools.gcp.agents.iam_agent import IAMAgent
    from adk_cli_agent.tools.gcp.agents.monitoring_agent import MonitoringAgent
    
    # Import base services
    from adk_cli_agent.tools.gcp.base.session_service import SessionService
    from adk_cli_agent.tools.gcp.base.runner import ADKRunner
    
    HAS_ALL_COMPONENTS = True
    logger.info("✅ All ADK components imported successfully")
    
except ImportError as e:
    HAS_ALL_COMPONENTS = False
    logger.error(f"❌ Import error: {e}")
    print(f"Import error: {e}")


def demonstrate_agent_capabilities():
    """Demonstrate the capabilities of each specialized agent."""
    
    if not HAS_ALL_COMPONENTS:
        print("❌ Cannot run demo due to import errors")
        return
    
    print("🚀 GCP ADK Agent Architecture Demo")
    print("=" * 50)
    
    # Initialize session service
    session_service = SessionService()
    session_id = session_service.create_session()
    print(f"📋 Created session: {session_id}")
    
    # Initialize all specialized agents
    agents = {
        'root': RootAgent(session_service=session_service),
        'project': ProjectAgent(session_service=session_service),
        'compute': ComputeAgent(session_service=session_service),
        'networking': NetworkingAgent(session_service=session_service),
        'storage': StorageAgent(session_service=session_service),
        'iam': IAMAgent(session_service=session_service),
        'monitoring': MonitoringAgent(session_service=session_service)
    }
    
    print(f"🤖 Initialized {len(agents)} specialized agents")
    
    # Test scenarios to demonstrate delegation
    test_scenarios = [
        {
            "request": "Create a new GCP project for my web application",
            "expected_agent": "project"
        },
        {
            "request": "Launch a Compute Engine instance for my API server",
            "expected_agent": "compute"
        },
        {
            "request": "Set up a VPC network with firewall rules for security",
            "expected_agent": "networking"
        },
        {
            "request": "Create a Cloud Storage bucket for data archival",
            "expected_agent": "storage"
        },
        {
            "request": "Create service accounts and set up IAM policies",
            "expected_agent": "iam"
        },
        {
            "request": "Set up monitoring alerts for my production environment",
            "expected_agent": "monitoring"
        },
        {
            "request": "Deploy a complete web application with database, storage, and monitoring",
            "expected_agent": "root"  # Complex request requiring multiple agents
        }
    ]
    
    print("\n🎯 Testing Agent Delegation:")
    print("-" * 30)
    
    for i, scenario in enumerate(test_scenarios, 1):
        request = scenario["request"]
        expected = scenario["expected_agent"]
        
        print(f"\n{i}. Request: \"{request}\"")
        
        # Test each agent's ability to handle the request
        best_agent = None
        best_confidence = 0
        
        for agent_name, agent in agents.items():
            if hasattr(agent, 'can_handle_request'):
                assessment = agent.can_handle_request(request)
                confidence = assessment.get('confidence', 0)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_agent = agent_name
        
        if best_agent:
            status = "✅" if best_agent == expected else "⚠️"
            print(f"   {status} Best agent: {best_agent} (confidence: {best_confidence:.2f})")
            
            # Show delegation details for the best agent
            if hasattr(agents[best_agent], 'delegate_request'):
                delegation = agents[best_agent].delegate_request(request, {})
                enhanced_context = delegation.get('enhanced_context', {})
                
                print(f"   📊 Operation type: {enhanced_context.get('operation_type', 'N/A')}")
                print(f"   🔒 Risk level: {enhanced_context.get('risk_assessment', {}).get('level', 'N/A')}")
                
                # Show safety check
                if hasattr(agents[best_agent], 'perform_safety_check'):
                    safety = agents[best_agent].perform_safety_check(request, enhanced_context)
                    safety_status = "✅ Safe" if safety.get('safe', False) else "⚠️ Requires review"
                    print(f"   🛡️ Safety check: {safety_status}")
        else:
            print("   ❌ No agent could handle this request")
    
    print("\n📈 Session Summary:")
    print("-" * 20)
    session_data = session_service.get_session(session_id)
    print(f"Session ID: {session_data.get('session_id', 'N/A')}")
    print(f"Created: {session_data.get('created_at', 'N/A')}")
    print(f"Operations logged: {len(session_data.get('operations', []))}")
    
    print("\n🏗️ ADK Architecture Components:")
    print("-" * 35)
    print("✅ Base Agent Framework (inheritance and patterns)")
    print("✅ Specialized Agents (domain expertise)")
    print("✅ Session Management (state and audit trail)")
    print("✅ Safety Framework (risk assessment and guardrails)")
    print("✅ Multi-Agent Delegation (intelligent routing)")
    print("✅ Tool Context (shared configuration and logging)")
    
    print("\n🔧 Available Tool Categories:")
    print("-" * 30)
    print("✅ Project Management Tools")
    print("✅ Compute Instance Tools")
    print("✅ Networking Configuration Tools")
    print("✅ Storage Management Tools")
    print("✅ IAM and Security Tools")
    print("✅ Monitoring and Observability Tools")
    
    print("\n🎉 GCP ADK Implementation Complete!")
    print("The architecture follows Google ADK Agent Teams patterns with:")
    print("- Specialized domain agents")
    print("- Intelligent request delegation")
    print("- Comprehensive safety guardrails")
    print("- Session state management")
    print("- Multi-agent collaboration")


def test_specific_agent(agent_type: str, request: str):
    """Test a specific agent with a request."""
    
    if not HAS_ALL_COMPONENTS:
        print("❌ Cannot test agent due to import errors")
        return
    
    session_service = SessionService()
    session_id = session_service.create_session()
    
    agents_map = {
        'project': ProjectAgent,
        'compute': ComputeAgent,
        'networking': NetworkingAgent,
        'storage': StorageAgent,
        'iam': IAMAgent,
        'monitoring': MonitoringAgent,
        'root': RootAgent
    }
    
    if agent_type not in agents_map:
        print(f"❌ Unknown agent type: {agent_type}")
        print(f"Available types: {list(agents_map.keys())}")
        return
    
    agent = agents_map[agent_type](session_service=session_service)
    
    print(f"🤖 Testing {agent_type} agent")
    print(f"📝 Request: {request}")
    print("-" * 40)
    
    # Test capability assessment
    if hasattr(agent, 'can_handle_request'):
        assessment = agent.can_handle_request(request)
        print(f"✨ Can handle: {assessment.get('can_handle', False)}")
        print(f"📊 Confidence: {assessment.get('confidence', 0):.2f}")
        print(f"💭 Reasoning: {assessment.get('reasoning', 'N/A')}")
    
    # Test delegation
    if hasattr(agent, 'delegate_request'):
        delegation = agent.delegate_request(request, {})
        enhanced_context = delegation.get('enhanced_context', {})
        print(f"🎯 Should handle: {delegation.get('should_handle', False)}")
        print(f"⚙️ Operation type: {enhanced_context.get('operation_type', 'N/A')}")
    
    # Test safety check
    if hasattr(agent, 'perform_safety_check'):
        safety = agent.perform_safety_check(request, enhanced_context if 'enhanced_context' in locals() else {})
        print(f"🛡️ Safety status: {'✅ Safe' if safety.get('safe', False) else '⚠️ Review needed'}")
        if safety.get('warnings'):
            print(f"⚠️ Warnings: {len(safety.get('warnings', []))}")
        if safety.get('safety_issues'):
            print(f"❌ Issues: {len(safety.get('safety_issues', []))}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test specific agent
        if len(sys.argv) >= 4:
            agent_type = sys.argv[2]
            request = " ".join(sys.argv[3:])
            test_specific_agent(agent_type, request)
        else:
            print("Usage: python adk_demo.py test <agent_type> <request>")
            print("Example: python adk_demo.py test compute 'create a VM instance'")
    else:
        # Run full demonstration
        demonstrate_agent_capabilities()
