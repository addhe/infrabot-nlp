#!/usr/bin/env python3
"""
Interactive demo untuk ADK GCP system.
Allows real-time interaction dengan agent system.
"""

import asyncio
import readline
import sys
import os
from datetime import datetime

from adk_cli_agent.tools.gcp.agents import RootGCPAgent
from adk_cli_agent.tools.gcp.base import ToolContext

class InteractiveDemo:
    """Interactive CLI untuk ADK GCP system."""
    
    def __init__(self):
        self.context = ToolContext()
        self.agent = None
        self.has_api_key = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY"))
        
    async def initialize(self):
        """Initialize the agent."""
        try:
            self.agent = RootGCPAgent()
            return True
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            return False
    
    def print_welcome(self):
        """Print welcome message."""
        print("🤖 ADK GCP Interactive Demo")
        print("=" * 50)
        print(f"📅 Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🆔 ID: {self.context.session_id}")
        
        if self.has_api_key:
            print("✅ API Key: Detected (real responses available)")
        else:
            print("⚠️  API Key: Not set (mock responses only)")
            print("   Set GOOGLE_API_KEY or OPENAI_API_KEY for real LLM")
        
        print(f"🎯 Agent: {self.agent.name if self.agent else 'Not initialized'}")
        print("=" * 50)
        
    def print_help(self):
        """Print help information."""
        print("\n📚 Available Commands:")
        print("╭─ Basic Commands ─────────────────────────────╮")
        print("│ help, h          - Show this help           │")
        print("│ status, st       - Show system status       │")
        print("│ context, ctx     - Show session context     │")
        print("│ clear, cls       - Clear screen             │")
        print("│ quit, exit, q    - Exit demo                │")
        print("╰──────────────────────────────────────────────╯")
        
        print("\n╭─ GCP Commands (Examples) ────────────────────╮")
        print("│ list projects                                │")
        print("│ list compute instances in my-project        │")
        print("│ create project demo-project                 │")
        print("│ create vm test-vm in us-central1-a          │")
        print("│ show storage buckets                         │")
        print("│ help with IAM policies                       │")
        print("╰──────────────────────────────────────────────╯")
        
        print("\n╭─ Agent Commands ──────────────────────────────╮")
        print("│ route: <query>   - Test routing logic       │")
        print("│ delegate: <task> - Test delegation          │")
        print("│ mock: <command>  - Force mock response       │")
        print("╰──────────────────────────────────────────────╯")
    
    async def handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands. Returns True if handled."""
        cmd = user_input.lower().strip()
        
        if cmd in ['help', 'h']:
            self.print_help()
            return True
            
        elif cmd in ['status', 'st']:
            await self.show_status()
            return True
            
        elif cmd in ['context', 'ctx']:
            self.show_context()
            return True
            
        elif cmd in ['clear', 'cls']:
            os.system('clear' if os.name == 'posix' else 'cls')
            self.print_welcome()
            return True
            
        elif cmd.startswith('route:'):
            query = cmd[6:].strip()
            await self.test_routing(query)
            return True
            
        elif cmd.startswith('delegate:'):
            task = cmd[9:].strip()
            await self.test_delegation(task)
            return True
            
        elif cmd.startswith('mock:'):
            mock_cmd = cmd[5:].strip()
            await self.mock_response(mock_cmd)
            return True
            
        return False
    
    async def show_status(self):
        """Show system status."""
        print("\n📊 System Status:")
        print("─" * 30)
        
        if self.agent:
            status = self.agent.get_agent_status()
            print(f"🤖 Root Agent: {self.agent.name}")
            print(f"📝 Description: {self.agent.description}")
            print(f"👥 Total Agents: {status['total_agents']}")
            print(f"🔧 Sub-agents: {', '.join(status['sub_agents'].keys())}")
            
            # Check delegation logic
            delegation = self.agent.get_delegation_logic()
            print(f"🎯 Delegation Rules: {len(delegation['delegation_rules'])}")
            
        else:
            print("❌ Agent not initialized")
            
        print(f"🔑 API Key: {'✅ Set' if self.has_api_key else '❌ Not set'}")
        print(f"🆔 Session: {self.context.session_id}")
    
    def show_context(self):
        """Show session context."""
        print("\n📋 Session Context:")
        print("─" * 30)
        print(f"🆔 Session ID: {self.context.session_id}")
        print(f"⏰ Created: {self.context.created_at}")
        print(f"🏷️  Metadata: {dict(self.context.metadata)}")
        print(f"☁️  GCP Config: {dict(self.context.gcp_config)}")
        print(f"📊 State Keys: {list(self.context.state.keys())}")
    
    async def test_routing(self, query: str):
        """Test routing logic for a query."""
        if not query:
            print("❌ Please provide a query after 'route:'")
            return
            
        print(f"\n🎯 Testing routing for: '{query}'")
        print("─" * 40)
        
        try:
            routing = await self.agent.route_request(query, self.context)
            print(f"🎯 Target: {routing['route_to']}")
            print(f"🏷️  Type: {routing['operation_type']}")
            print(f"💭 Reasoning: {routing['reasoning']}")
            
            if 'target_agent' in routing:
                agent = routing['target_agent']
                if hasattr(agent, 'name'):
                    print(f"🤖 Agent: {agent.name}")
                    
        except Exception as e:
            print(f"❌ Routing error: {e}")
    
    async def test_delegation(self, task: str):
        """Test delegation for a task."""
        if not task:
            print("❌ Please provide a task after 'delegate:'")
            return
            
        print(f"\n🔄 Testing delegation for: '{task}'")
        print("─" * 40)
        
        try:
            # Test delegation logic tanpa executing
            routing = await self.agent.route_request(task, self.context)
            print(f"📋 Would delegate to: {routing['route_to']}")
            print(f"💭 Reasoning: {routing['reasoning']}")
            
            # Simulate execution
            print("🔄 Simulating execution...")
            if self.has_api_key:
                result = await self.agent.execute_delegated_request(task, self.context)
                print(f"✅ Result: {result}")
            else:
                print("⚠️  Mock: Would execute with real agent")
                
        except Exception as e:
            print(f"❌ Delegation error: {e}")
    
    async def mock_response(self, command: str):
        """Generate mock response for a command."""
        print(f"\n🎭 Mock response for: '{command}'")
        print("─" * 30)
        
        mock_responses = {
            "list projects": "Found 3 projects: my-project, test-project, staging-project",
            "create vm": "VM 'test-vm' would be created in us-central1-a",
            "list buckets": "Found 2 storage buckets: data-bucket, logs-bucket",
            "show iam": "IAM policies for project would be displayed",
        }
        
        # Find matching response
        response = None
        for key, value in mock_responses.items():
            if key in command.lower():
                response = value
                break
        
        if response:
            print(f"🎭 {response}")
        else:
            print(f"🎭 Mock response: Command '{command}' would be processed by appropriate agent")
    
    async def process_user_input(self, user_input: str):
        """Process user input."""
        # Handle special commands
        if await self.handle_special_commands(user_input):
            return
        
        # Process as regular query
        print(f"\n🤖 Processing: '{user_input}'")
        
        try:
            if self.has_api_key:
                print("🔄 Sending to agent...")
                result = await self.agent.execute_delegated_request(user_input, self.context)
                print(f"✅ Agent response: {result}")
            else:
                print("🎭 Mock mode (no API key):")
                # Show routing decision
                routing = await self.agent.route_request(user_input, self.context)
                print(f"   🎯 Would route to: {routing['route_to']}")
                print(f"   💭 Reasoning: {routing['reasoning']}")
                print("   ⚠️  Set API key for real responses")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def run(self):
        """Run the interactive demo."""
        # Initialize
        if not await self.initialize():
            return
        
        # Welcome
        self.print_welcome()
        self.print_help()
        
        print("\n💬 Ready for input! Type 'help' for commands.")
        
        # Main loop
        try:
            while True:
                try:
                    # Get user input
                    user_input = input("\n🗣️  You: ").strip()
                    
                    # Check for exit
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    
                    # Skip empty input
                    if not user_input:
                        continue
                    
                    # Process input
                    await self.process_user_input(user_input)
                    
                except KeyboardInterrupt:
                    print("\n\n⚠️  Use 'quit' to exit cleanly.")
                    continue
                    
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")

async def main():
    """Main function."""
    demo = InteractiveDemo()
    await demo.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
