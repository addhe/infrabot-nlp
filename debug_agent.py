#!/usr/bin/env python3
import sys

print("Starting debug")
try:
    from my_cli_agent.agent import main
    print("Successfully imported main")
    
    main()
    print("Main executed successfully")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Script completed")
