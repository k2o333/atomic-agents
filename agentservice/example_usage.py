#!/usr/bin/env python3
"""
Example usage of the HelloWorldAgent
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentservice.generic_agents.HelloWorldAgent import HelloWorldAgent

def main():
    """Test the HelloWorldAgent"""
    print("Testing HelloWorldAgent...")
    
    # Create an instance of the agent
    agent = HelloWorldAgent()
    
    # Run the agent with empty task data
    result = agent.run({})
    
    # Print the result
    print(f"Status: {result.status}")
    print(f"Thought: {result.output.thought}")
    print(f"Content: {result.output.intent.content}")
    
    # Verify the result
    assert result.status == "SUCCESS"
    assert result.output.intent.content == "Hello World!"
    print("\n✅ Test passed! HelloWorldAgent is working correctly.")

if __name__ == "__main__":
    main()