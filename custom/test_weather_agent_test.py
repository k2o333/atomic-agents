"""
Test script for WeatherAgent - compatible with the project's test framework
"""

import sys
import os
import unittest
import json

# Add the project root to the Python path
sys.path.insert(0, '/root/projects/atom_agents')

from custom.WeatherAgent import WeatherAgent
from custom.search_weather import search_weather


class TestWeatherAgent(unittest.TestCase):
    """Test cases for WeatherAgent and search_weather tool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.task_data = {
            'goal': '北京今天天气怎么样？',
            'context': {}
        }
        
        self.agent_config = {
            'id': 'WeatherAgent',
            'role': 'WORKER',
            'description': '一个可以搜索天气信息的自定义Agent。',
            'implementation_path': 'custom.WeatherAgent.WeatherAgent'
        }
    
    def test_search_weather_tool(self):
        """Test the search_weather tool"""
        result = search_weather("Beijing")
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('data', result)
        self.assertEqual(result['data']['city'], 'Beijing')
        self.assertIn('temperature', result['data'])
        self.assertIn('description', result['data'])
    
    def test_weather_agent_initialization(self):
        """Test WeatherAgent initialization"""
        agent = WeatherAgent(self.agent_config, self.task_data)
        
        self.assertIsInstance(agent, WeatherAgent)
        self.assertTrue(agent.is_first_run())
    
    def test_weather_agent_prompt_generation(self):
        """Test WeatherAgent prompt generation"""
        agent = WeatherAgent(self.agent_config, self.task_data)
        prompt = agent._generate_dynamic_prompt()
        
        self.assertIsInstance(prompt, str)
        self.assertIn('weather assistant', prompt)
        self.assertIn('北京今天天气怎么样？', prompt)
    
    def test_complete_flow_simulation(self):
        """Test the complete flow simulation"""
        # First run - should request LLM call
        agent = WeatherAgent(self.agent_config, self.task_data)
        result = agent.run()
        
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['output']['intent']['tool_id'], 'System.LLM.invoke')
        
        # Simulate LLM response requesting tool call
        mock_llm_response = {
            "content": '{"action": "search_weather", "city": "北京"}'
        }
        
        # Second run - should request tool call
        task_data_with_llm = {
            'goal': '北京今天天气怎么样？',
            'context': {
                'last_llm_response': mock_llm_response
            }
        }
        
        agent = WeatherAgent(self.agent_config, task_data_with_llm)
        result = agent.run()
        
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['output']['intent']['tool_id'], 'custom.search_weather')
        self.assertEqual(result['output']['intent']['arguments']['city'], '北京')
        
        # Simulate tool execution and third run
        tool_result = search_weather("北京")
        task_data_with_tool = {
            'goal': '北京今天天气怎么样？',
            'context': {
                'last_tool_result': {
                    "status": "SUCCESS",
                    "output": tool_result
                }
            }
        }
        
        agent = WeatherAgent(self.agent_config, task_data_with_tool)
        result = agent.run()
        
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertIn('content', result['output']['intent'])
        self.assertIn('weather', result['output']['intent']['content'])
        self.assertIn('北京', result['output']['intent']['content'])


if __name__ == '__main__':
    unittest.main()