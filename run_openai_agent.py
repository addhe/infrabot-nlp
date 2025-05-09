#!/usr/bin/env python3
import os
import sys
import openai
import subprocess
from datetime import datetime
from typing import Dict, Any, List

def get_current_time(city: str = "") -> Dict[str, Any]:
    """Get the current time, optionally for a specific city."""
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "success": True,
        "result": f"Current time: {time_str}"
    }

def execute_command(command: str) -> Dict[str, Any]:
    """Execute a shell command and return the result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "result": result.stdout
            }
        else:
            return {
                "success": False,
                "error_message": result.stderr
            }
    except Exception as e:
        return {
            "success": False,
            "error_message": str(e)
        }

def main():
    """Main function to run the OpenAI CLI Agent."""
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)
    
    # Set up OpenAI client
    openai.api_key = api_key
    
    # Get model ID from environment or use default
    model_id = os.getenv("OPENAI_MODEL_ID", "gpt-4-turbo-preview")
    
    # Available tools
    tools = {
        "get_current_time": get_current_time,
        "execute_command": execute_command
    }
    
    # Print welcome message
    print(f"""
    Welcome to OpenAI CLI Agent
    Using model: {model_id}
    
    Available commands:
    - Get current time: Ask about the current time
    - Execute commands: Run shell commands (e.g., "run ls -la" or "execute pwd")
    
    Type 'exit()' to quit
    """)
    
    # Conversation history
    conversation = [
        {"role": "system", "content": "You are a helpful assistant that can use tools to help answer questions. You can get the current time or execute shell commands."}
    ]
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input("\n> ")
            
            # Check for exit command
            if user_input.lower() == "exit()":
                print("Shutting down gracefully...")
                sys.exit(0)
            
            # Add user message to conversation
            conversation.append({"role": "user", "content": user_input})
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=model_id,
                messages=conversation,
                temperature=0.7,
                stream=True
            )
            
            # Stream the response
            print()
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            print()
            
            # Add assistant response to conversation
            conversation.append({"role": "assistant", "content": full_response})
            
            # Check if the response contains tool instructions
            if "use the get_current_time tool" in full_response.lower():
                result = get_current_time()
                if result["success"]:
                    print("\nResult:")
                    print("=" * 50)
                    print(result["result"])
                    print("=" * 50)
                else:
                    print("\nError:", result["error_message"])
                    
            elif "use the execute_command tool" in full_response.lower() or "run the command" in full_response.lower():
                # Try to extract the command
                command = None
                if "`" in full_response:
                    # Extract command from backticks
                    parts = full_response.split("`")
                    if len(parts) >= 3:
                        command = parts[1]
                
                if command:
                    print(f"\nExecuting command: {command}")
                    result = execute_command(command)
                    if result["success"]:
                        print("\nResult:")
                        print("=" * 50)
                        print(result["result"])
                        print("=" * 50)
                    else:
                        print("\nError:", result["error_message"])
                else:
                    print("\nCould not determine which command to execute.")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
