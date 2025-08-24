#!/usr/bin/env python3
"""
Example usage of the AgentService with M3 features
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentservice.agent_service import AgentService


def main():
    """Test the AgentService with M3 features"""
    print("Testing AgentService with M3 features...")
    
    # Create an instance of the AgentService
    agent_service = AgentService()
    
    # Load the capabilities registry
    capabilities_path = os.path.join(os.path.dirname(__file__), 'generic_agents', 'capabilities.json')
    with open(capabilities_path, 'r') as f:
        agent_registry = json.load(f)
    
    # Test 1: Execute a regular worker agent
    print("\n1. Testing regular worker agent (HelloWorldAgent)...")
    task_data = {"task_id": "task_1", "input_data": {}}
    result = agent_service.execute_agent("hello_world_agent", task_data, agent_registry)
    
    print(f"Status: {result.status}")
    print(f"Thought: {result.output.thought}")
    if hasattr(result.output.intent, 'content'):
        print(f"Content: {result.output.intent.content}")
    elif hasattr(result.output.intent, 'tool_id'):
        print(f"Tool Call: {result.output.intent.tool_id}")
    
    # Test 2: Execute a context-aware worker agent
    print("\n2. Testing context-aware worker agent...")
    task_data_with_context = {
        "task_id": "task_2", 
        "input_data": {"query": "What is the weather today?"},
        "context": {
            "user_id": "user_123",
            "session_id": "session_456"
        }
    }
    result = agent_service.execute_agent("context_aware_worker", task_data_with_context, agent_registry)
    
    print(f"Status: {result.status}")
    print(f"Thought: {result.output.thought}")
    if hasattr(result.output.intent, 'content'):
        print(f"Content: {result.output.intent.content}")
    elif hasattr(result.output.intent, 'tool_id'):
        print(f"Tool Call: {result.output.intent.tool_id}")
    
    # Test 3: Execute a Planner agent
    print("\n3. Testing Planner agent...")
    task_data_planner = {
        "task_id": "task_3",
        "input_data": {
            "request": "Create a plan to develop a new feature for our web application"
        },
        "group_config": {
            "planner_prompt_template": "As a planner, create a detailed plan for: {user_request}. Available teams: Research Team, Development Team, QA Team, Deployment Team",
            "team_list": ["Development Team", "QA Team", "Deployment Team"]
        }
    }
    result = agent_service.execute_agent("generic_planner_agent", task_data_planner, agent_registry)
    
    print(f"Status: {result.status}")
    print(f"Thought: {result.output.thought}")
    if hasattr(result.output.intent, 'content'):
        print(f"Content: {result.output.intent.content}")
    elif hasattr(result.output.intent, 'tool_id'):
        print(f"Tool Call: {result.output.intent.tool_id}")
    elif hasattr(result.output.intent, 'new_tasks'):
        print(f"Plan generated with {len(result.output.intent.new_tasks)} tasks")
    
    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    main()