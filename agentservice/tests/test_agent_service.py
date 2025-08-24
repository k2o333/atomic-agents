"""
Test script for AgentService class
"""

import sys
import os
import unittest
from typing import Dict, Any
from unittest.mock import Mock, patch

# Add the project root to the path so we can import the agents module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agentservice.agent_service import AgentService, AgentFactory
from interfaces import AgentResult


class TestAgentService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.agent_service = AgentService()
        self.agent_registry = {
            "agents": [
                {
                    "id": "test_agent",
                    "name": "Test Agent",
                    "version": "1.0",
                    "role": "WORKER",
                    "implementation_path": "agentservice.generic_agents.HelloWorldAgent.HelloWorldAgent"
                },
                {
                    "id": "planner_agent",
                    "name": "Test Planner Agent",
                    "version": "1.0",
                    "role": "PLANNER",
                    "implementation_path": "agentservice.generic_agents.HelloWorldAgent.HelloWorldAgent"
                }
            ]
        }
        self.task_data = {"task_id": "123", "input_data": {"query": "test"}}
    
    def test_initialization(self):
        """Test AgentService initialization"""
        self.assertIsNotNone(self.agent_service.context_builder)
        self.assertIsNotNone(self.agent_service.agent_factory)
        self.assertIsNotNone(self.agent_service.logger)
    
    @patch('agentservice.agent_service.AgentFactory.create_agent')
    def test_execute_agent_success(self, mock_create_agent):
        """Test successful agent execution"""
        # Mock the agent instance and its run method
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "status": "SUCCESS",
            "output": {
                "thought": "Test thought",
                "intent": {
                    "content": "Test content"
                }
            }
        }
        mock_create_agent.return_value = mock_agent
        
        # Execute the agent
        result = self.agent_service.execute_agent("test_agent", self.task_data, self.agent_registry)
        
        # Verify the result
        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.output.thought, "Test thought")
        mock_create_agent.assert_called_once()
    
    def test_execute_agent_not_found(self):
        """Test agent execution with non-existent agent"""
        result = self.agent_service.execute_agent("non_existent_agent", self.task_data, self.agent_registry)
        
        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.status, "FAILURE")
        self.assertIn("not found", result.failure_details.message)
    
    @patch('agentservice.agent_service.AgentFactory.create_agent')
    def test_execute_agent_exception(self, mock_create_agent):
        """Test agent execution with exception"""
        # Make the create_agent method raise an exception
        mock_create_agent.side_effect = Exception("Test exception")
        
        # Execute the agent
        result = self.agent_service.execute_agent("test_agent", self.task_data, self.agent_registry)
        
        # Verify the result
        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.status, "FAILURE")
        self.assertIn("Test exception", result.failure_details.message)
    
    def test_get_agent_config_found(self):
        """Test getting agent configuration when agent exists"""
        agent_config = self.agent_service._get_agent_config("test_agent", self.agent_registry)
        
        self.assertIsNotNone(agent_config)
        self.assertEqual(agent_config["id"], "test_agent")
        self.assertEqual(agent_config["name"], "Test Agent")
    
    def test_get_agent_config_not_found(self):
        """Test getting agent configuration when agent doesn't exist"""
        agent_config = self.agent_service._get_agent_config("non_existent_agent", self.agent_registry)
        
        self.assertIsNone(agent_config)


class TestAgentFactory(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.agent_factory = AgentFactory()
        self.agent_config = {
            "implementation_path": "agentservice.generic_agents.HelloWorldAgent.HelloWorldAgent"
        }
        self.task_data = {"task_id": "123", "input_data": {"query": "test"}}
    
    def test_initialization(self):
        """Test AgentFactory initialization"""
        self.assertIsNotNone(self.agent_factory.logger)
    
    def test_create_agent_success(self):
        """Test successful agent creation"""
        agent_instance = self.agent_factory.create_agent(self.agent_config, self.task_data)
        
        # Verify that we got an instance of the correct class
        self.assertIsNotNone(agent_instance)
        # Note: We can't easily check the exact type because it's dynamically loaded
    
    def test_create_agent_missing_implementation_path(self):
        """Test agent creation with missing implementation path"""
        agent_config = {}
        
        with self.assertRaises(ValueError) as context:
            self.agent_factory.create_agent(agent_config, self.task_data)
        
        self.assertIn("implementation_path", str(context.exception))
    
    def test_create_agent_invalid_implementation_path(self):
        """Test agent creation with invalid implementation path"""
        agent_config = {
            "implementation_path": "non.existent.module.Class"
        }
        
        with self.assertRaises(ValueError) as context:
            self.agent_factory.create_agent(agent_config, self.task_data)
        
        self.assertIn("Failed to load agent", str(context.exception))


if __name__ == '__main__':
    unittest.main()