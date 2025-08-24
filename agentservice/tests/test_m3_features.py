#!/usr/bin/env python3
"""
Test script for M3 features of the AgentService
"""

import sys
import os
import json
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentservice.agent_service import AgentService


class TestM3Features(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.agent_service = AgentService()
        
        # Load the capabilities registry
        capabilities_path = os.path.join(os.path.dirname(__file__), '..', 'generic_agents', 'capabilities.json')
        with open(capabilities_path, 'r') as f:
            self.agent_registry = json.load(f)
    
    def test_context_building_integration(self):
        """Test that context building is integrated correctly"""
        # This test would require a more complex setup with mocked services
        # For now, we'll just verify that the service initializes correctly
        self.assertIsNotNone(self.agent_service.context_builder)
    
    def test_planner_agent_support(self):
        """Test that Planner agents are supported"""
        task_data = {
            "task_id": "task_1",
            "input_data": {
                "request": "Create a plan to develop a new feature"
            },
            "group_config": {
                "planner_prompt_template": "Create a plan for: {user_request}",
                "team_list": ["Dev Team", "QA Team"]
            }
        }
        
        result = self.agent_service.execute_agent("generic_planner_agent", task_data, self.agent_registry)
        
        # Verify that we get a result
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "SUCCESS")
    
    def test_prompt_fusion_strategy(self):
        """Test that prompt fusion strategy is implemented"""
        # This test would require checking the internal behavior of the agent
        # For now, we'll just verify that the context-aware agent can be executed
        task_data = {
            "task_id": "task_2", 
            "input_data": {"query": "What is the weather today?"},
            "context": {}
        }
        
        result = self.agent_service.execute_agent("context_aware_worker", task_data, self.agent_registry)
        
        # Verify that we get a result
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "SUCCESS")


if __name__ == "__main__":
    unittest.main()