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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agentservice.baseagent.base_agent import BaseAgent
from interfaces import PlanBlueprint, TaskDefinition, EdgeDefinition


class TestAgent(BaseAgent):
    """Test implementation of BaseAgent for testing purposes"""
    
    def __init__(self, agent_config=None, task_data=None, group_config=None):
        # If no config is provided, use default values
        if agent_config is None:
            agent_config = {}
        if task_data is None:
            task_data = {}
        super().__init__(agent_config, task_data, group_config)
    
    def _generate_dynamic_prompt(self) -> str:
        return "Test prompt"
    
    def _handle_llm_response(self, llm_response: Dict) -> Dict:
        return self.create_final_answer(
            thought="Handled LLM response",
            content=llm_response.get("content", "default")
        )


class TestPlannerAgent(BaseAgent):
    """Test implementation of a Planner agent for testing purposes"""
    
    def __init__(self, agent_config=None, task_data=None, group_config=None):
        # If no config is provided, use default values
        if agent_config is None:
            agent_config = {}
        if task_data is None:
            task_data = {}
        super().__init__(agent_config, task_data, group_config)
    
    def _generate_dynamic_prompt(self) -> str:
        return "Test planner prompt"
    
    def _handle_llm_response(self, llm_response: Dict) -> Dict:
        return self.create_final_answer(
            thought="Handled LLM response",
            content=llm_response.get("content", "default")
        )
    
    def _generate_plan_blueprint(self) -> PlanBlueprint:
        """Generate a test plan blueprint"""
        task = TaskDefinition(
            task_id="test_task_1",
            input_data={"test": "data"},
            assignee_id="test_worker"
        )
        
        edge = EdgeDefinition(
            source_task_id="test_task_1",
            target_task_id="test_task_2"
        )
        
        return PlanBlueprint(
            new_tasks=[task],
            new_edges=[edge]
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
        self.assertEqual(agent.context_config, {})
        self.assertEqual(agent.prompt_fusion_strategy, {})
    
    def test_initialization_with_context_config(self):
        """Test BaseAgent initialization with context config"""
        agent_config_with_context = {
            "name": "test_agent", 
            "version": "1.0",
            "context_config": {"include_metadata": True}
        }
        agent = TestAgent(agent_config_with_context, self.task_data)
        
        self.assertEqual(agent.context_config, {"include_metadata": True})
    
    def test_initialization_with_prompt_fusion_strategy(self):
        """Test BaseAgent initialization with prompt fusion strategy"""
        agent_config_with_fusion = {
            "name": "test_agent", 
            "version": "1.0",
            "prompt_fusion_strategy": {"mode": "PREPEND_BASE"}
        }
        agent = TestAgent(agent_config_with_fusion, self.task_data)
        
        self.assertEqual(agent.prompt_fusion_strategy, {"mode": "PREPEND_BASE"})
    
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
    
    def test_apply_prompt_fusion_prepend_base(self):
        """Test prompt fusion with PREPEND_BASE strategy"""
        agent_config_with_fusion = {
            "name": "test_agent", 
            "version": "1.0",
            "base_prompt": "You are a helpful assistant.",
            "prompt_fusion_strategy": {"mode": "PREPEND_BASE"}
        }
        agent = TestAgent(agent_config_with_fusion, self.task_data)
        
        dynamic_prompt = "What is the weather today?"
        final_prompt = agent._apply_prompt_fusion(dynamic_prompt)
        
        expected_prompt = "You are a helpful assistant.\n\nWhat is the weather today?"
        self.assertEqual(final_prompt, expected_prompt)
    
    def test_apply_prompt_fusion_no_strategy(self):
        """Test prompt fusion with no strategy (default)"""
        agent_config_no_fusion = {
            "name": "test_agent", 
            "version": "1.0"
        }
        agent = TestAgent(agent_config_no_fusion, self.task_data)
        
        dynamic_prompt = "What is the weather today?"
        final_prompt = agent._apply_prompt_fusion(dynamic_prompt)
        
        self.assertEqual(final_prompt, dynamic_prompt)
    
    def test_is_planner_agent_true(self):
        """Test _is_planner_agent returns True for Planner agents"""
        planner_config = {
            "name": "test_planner", 
            "version": "1.0",
            "role": "PLANNER"
        }
        agent = TestAgent(planner_config, self.task_data)
        
        self.assertTrue(agent._is_planner_agent())
    
    def test_is_planner_agent_false(self):
        """Test _is_planner_agent returns False for non-Planner agents"""
        worker_config = {
            "name": "test_worker", 
            "version": "1.0",
            "role": "WORKER"
        }
        agent = TestAgent(worker_config, self.task_data)
        
        self.assertFalse(agent._is_planner_agent())
    
    def test_is_planner_agent_default_false(self):
        """Test _is_planner_agent returns False when no role is specified"""
        agent = TestAgent(self.agent_config, self.task_data)
        
        self.assertFalse(agent._is_planner_agent())


if __name__ == '__main__':
    unittest.main()