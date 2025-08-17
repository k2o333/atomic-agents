"""
Test script for BaseAgent class
"""

import sys
import os
import unittest
from typing import Dict, Any, Optional
from unittest.mock import Mock

# Add the project root to the path so we can import the agents module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.base_agent import BaseAgent


class TestAgent(BaseAgent):
    """Test implementation of BaseAgent for testing purposes"""
    
    def _generate_dynamic_prompt(self) -> str:
        return "Test prompt"
    
    def _handle_llm_response(self, llm_response: Dict) -> Dict:
        return self.create_final_answer(
            thought="Handled LLM response",
            content=llm_response.get("content", "default")
        )


class TestBaseAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.agent_config = {"name": "test_agent", "version": "1.0"}
        self.task_data = {"task_id": "123", "input_data": {"query": "test"}, "context": {}}
        self.group_config = {"group_name": "test_group"}
    
    def test_initialization(self):
        """Test BaseAgent initialization"""
        agent = TestAgent(self.agent_config, self.task_data, self.group_config)
        
        self.assertEqual(agent.agent_config, self.agent_config)
        self.assertEqual(agent.task_data, self.task_data)
        self.assertEqual(agent.group_config, self.group_config)
        self.assertIsNotNone(agent.logger)
    
    def test_is_first_run_true(self):
        """Test is_first_run returns True when no previous results exist"""
        task_data_no_context = {"task_id": "123", "input_data": {"query": "test"}}
        agent = TestAgent(self.agent_config, task_data_no_context)
        
        self.assertTrue(agent.is_first_run())
    
    def test_is_first_run_false_with_llm_response(self):
        """Test is_first_run returns False when LLM response exists"""
        task_data_with_llm = {
            "task_id": "123", 
            "input_data": {"query": "test"},
            "context": {"last_llm_response": {"content": "response"}}
        }
        agent = TestAgent(self.agent_config, task_data_with_llm)
        
        self.assertFalse(agent.is_first_run())
    
    def test_is_first_run_false_with_tool_result(self):
        """Test is_first_run returns False when tool result exists"""
        task_data_with_tool = {
            "task_id": "123", 
            "input_data": {"query": "test"},
            "context": {"last_tool_result": {"status": "success"}}
        }
        agent = TestAgent(self.agent_config, task_data_with_tool)
        
        self.assertFalse(agent.is_first_run())
    
    def test_get_last_llm_response(self):
        """Test get_last_llm_response retrieves correct response"""
        llm_response = {"content": "test response"}
        task_data_with_response = {
            "task_id": "123",
            "input_data": {"query": "test"},
            "context": {"last_llm_response": llm_response}
        }
        agent = TestAgent(self.agent_config, task_data_with_response)
        
        result = agent.get_last_llm_response()
        self.assertEqual(result, llm_response)
    
    def test_get_last_llm_response_none(self):
        """Test get_last_llm_response returns None when no response exists"""
        agent = TestAgent(self.agent_config, self.task_data)
        
        result = agent.get_last_llm_response()
        self.assertIsNone(result)
    
    def test_get_last_tool_result(self):
        """Test get_last_tool_result retrieves correct result"""
        tool_result = {"status": "success", "data": "result"}
        task_data_with_tool_result = {
            "task_id": "123",
            "input_data": {"query": "test"},
            "context": {"last_tool_result": tool_result}
        }
        agent = TestAgent(self.agent_config, task_data_with_tool_result)
        
        result = agent.get_last_tool_result()
        self.assertEqual(result, tool_result)
    
    def test_get_last_tool_result_none(self):
        """Test get_last_tool_result returns None when no result exists"""
        agent = TestAgent(self.agent_config, self.task_data)
        
        result = agent.get_last_tool_result()
        self.assertIsNone(result)
    
    def test_request_llm_call(self):
        """Test request_llm_call creates correct AgentResult"""
        agent = TestAgent(self.agent_config, self.task_data)
        prompt = "What is the weather today?"
        
        result = agent.request_llm_call(prompt)
        
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["output"]["thought"], "Requesting LLM call to process the task.")
        self.assertEqual(result["output"]["intent"]["tool_id"], "System.LLM.invoke")
        self.assertEqual(result["output"]["intent"]["arguments"]["prompt"], prompt)
    
    def test_request_tool_call(self):
        """Test request_tool_call creates correct AgentResult"""
        agent = TestAgent(self.agent_config, self.task_data)
        tool_id = "Calculator.add"
        arguments = {"a": 1, "b": 2}
        
        result = agent.request_tool_call(tool_id, arguments)
        
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["output"]["thought"], f"Requesting tool call for {tool_id}.")
        self.assertEqual(result["output"]["intent"]["tool_id"], tool_id)
        self.assertEqual(result["output"]["intent"]["arguments"], arguments)
    
    def test_create_final_answer(self):
        """Test create_final_answer creates correct AgentResult"""
        agent = TestAgent(self.agent_config, self.task_data)
        thought = "The calculation is complete."
        content = {"result": 3}
        
        result = agent.create_final_answer(thought, content)
        
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["output"]["thought"], thought)
        self.assertEqual(result["output"]["intent"]["content"], content)
    
    def test_create_failure_response(self):
        """Test create_failure_response creates correct AgentResult"""
        agent = TestAgent(self.agent_config, self.task_data)
        error_type = "VALIDATION_ERROR"  # Use a valid enum value
        message = "This is a test error"
        
        result = agent.create_failure_response(error_type, message)
        
        self.assertEqual(result["status"], "FAILURE")
        self.assertEqual(result["failure_details"]["type"], error_type)
        self.assertEqual(result["failure_details"]["message"], message)
        self.assertIn("Agent execution failed", result["output"]["intent"]["content"])


if __name__ == '__main__':
    unittest.main()