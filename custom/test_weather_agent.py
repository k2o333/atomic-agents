"""
Test script for WeatherAgent and search_weather tool
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/root/projects/atom_agents')

from custom.search_weather import search_weather
from custom.WeatherAgent import WeatherAgent


def test_search_weather():
    """Test the search_weather tool"""
    print("Testing search_weather tool...")
    
    # Test with a city name
    result = search_weather("Beijing")
    print(f"Result: {result}")
    
    # Check if the result is successful
    if result.get('status') == 'success':
        print("✓ search_weather tool test passed")
        return True
    else:
        print("✗ search_weather tool test failed")
        return False


def test_weather_agent():
    """Test the WeatherAgent class"""
    print("\nTesting WeatherAgent class...")
    
    # Create a mock task data
    task_data = {
        'goal': '北京今天天气怎么样？',
        'context': {}
    }
    
    # Create a mock agent config
    agent_config = {
        'id': 'WeatherAgent',
        'role': 'WORKER',
        'description': '一个可以搜索天气信息的自定义Agent。',
        'implementation_path': 'custom.WeatherAgent.WeatherAgent'
    }
    
    # Create the agent
    agent = WeatherAgent(agent_config, task_data)
    
    # Test _generate_dynamic_prompt
    prompt = agent._generate_dynamic_prompt()
    print(f"Generated prompt: {prompt[:100]}...")  # Show first 100 chars
    
    # Test is_first_run
    is_first = agent.is_first_run()
    print(f"Is first run: {is_first}")
    
    if is_first:
        print("✓ WeatherAgent initialization test passed")
        return True
    else:
        print("✗ WeatherAgent initialization test failed")
        return False


def main():
    """Run all tests"""
    print("Running WeatherAgent and search_weather tests...\n")
    
    # Test the search_weather tool
    tool_test_passed = test_search_weather()
    
    # Test the WeatherAgent class
    agent_test_passed = test_weather_agent()
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary:")
    print(f"search_weather tool: {'PASSED' if tool_test_passed else 'FAILED'}")
    print(f"WeatherAgent class: {'PASSED' if agent_test_passed else 'FAILED'}")
    
    if tool_test_passed and agent_test_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())