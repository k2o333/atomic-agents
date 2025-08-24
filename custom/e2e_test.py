"""
End-to-End Test for WeatherAgent and search_weather tool
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, '/root/projects/atom_agents')

from custom.WeatherAgent import WeatherAgent
from custom.search_weather import search_weather


def test_complete_flow():
    """Test the complete flow: Agent -> Tool -> Result -> Final Answer"""
    print("Testing complete flow...")
    
    # Step 1: Create a task for the WeatherAgent
    task_data = {
        'goal': '北京今天天气怎么样？',
        'context': {}
    }
    
    agent_config = {
        'id': 'WeatherAgent',
        'role': 'WORKER',
        'description': '一个可以搜索天气信息的自定义Agent。',
        'implementation_path': 'custom.WeatherAgent.WeatherAgent'
    }
    
    # Step 2: Initialize the agent (first run)
    agent = WeatherAgent(agent_config, task_data)
    result = agent.run()
    
    print(f"First run result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # Step 3: Simulate LLM response requesting tool call
    # This would normally come from the LLMService
    mock_llm_response = {
        "content": '{"action": "search_weather", "city": "北京"}'
    }
    
    # Update task context with mock LLM response
    task_data['context']['last_llm_response'] = mock_llm_response
    
    # Step 4: Re-initialize agent with updated context (second run)
    agent = WeatherAgent(agent_config, task_data)
    result = agent.run()
    
    print(f"Tool call request result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # Step 5: Simulate tool execution
    tool_result = search_weather("北京")
    
    # Step 6: Update task context with tool result
    task_data['context']['last_tool_result'] = {
        "status": "SUCCESS",
        "output": tool_result
    }
    
    # Step 7: Re-initialize agent with tool result (third run)
    agent = WeatherAgent(agent_config, task_data)
    result = agent.run()
    
    print(f"Final answer result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # Step 8: Verify final answer
    if result.get('status') == 'SUCCESS':
        intent = result.get('output', {}).get('intent', {})
        if 'content' in intent:
            print("✓ Complete flow test passed")
            print(f"Final answer: {intent['content']}")
            return True
    
    print("✗ Complete flow test failed")
    return False


def main():
    """Run the end-to-end test"""
    print("Running end-to-end test for WeatherAgent...\n")
    
    success = test_complete_flow()
    
    print("\n" + "="*50)
    if success:
        print("✓ End-to-end test passed!")
        return 0
    else:
        print("✗ End-to-end test failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())