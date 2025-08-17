#!/usr/bin/env python3
"""
Test runner for Central Graph Engine (M1)
This script runs tests with proper mocking to avoid database connections.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestCentralGraphEngine(unittest.TestCase):
    """Test suite for Central Graph Engine functionality"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        pass

    @patch('PersistenceService.service.PersistenceService')
    @patch('AgentService.service.AgentService')
    @patch('toolservices.service.ToolService')
    def test_process_pending_task_with_final_answer(self, mock_tool_service_class, mock_agent_service_class, mock_persistence_service_class):
        """
        Test Case 1: Process Pending Task with FinalAnswer
        Verify that the engine can process a pending task assigned to an Agent 
        and correctly handle a FinalAnswer response.
        """
        # Create mock instances
        mock_persistence_service = Mock()
        mock_agent_service = Mock()
        mock_tool_service = Mock()
        
        # Configure the mock classes to return our mock instances
        mock_persistence_service_class.return_value = mock_persistence_service
        mock_agent_service_class.return_value = mock_agent_service
        mock_tool_service_class.return_value = mock_tool_service
        
        # Import here to avoid database connection issues
        from interfaces import TaskDefinition, AgentResult, AgentIntent, FinalAnswer
        
        # Create a test task
        task = TaskDefinition(
            task_id="test-task-1",
            assignee_id="Agent:TestAgent",
            input_data={"message": "Hello Engine"}
        )
        
        # Import the function after patching to avoid database connection issues
        from CentralGraphEngine.engine import process_task
        
        # Mock agent service to return a successful FinalAnswer
        final_answer = FinalAnswer(content="Hello World from Test Agent!")
        agent_intent = AgentIntent(thought="Processing complete.", intent=final_answer)
        agent_result = AgentResult(status="SUCCESS", output=agent_intent)
        
        # Configure the mock to return our result
        mock_agent_service.execute_agent.return_value = agent_result
        
        # Process the task
        process_task(task)
        
        # Verify the agent was called with the correct task
        mock_agent_service.execute_agent.assert_called_once_with(task)
        
        # Verify the task status was updated to COMPLETED
        mock_persistence_service.update_task_status.assert_called_once_with(
            task_id="test-task-1",
            status="COMPLETED",
            result={"content": "Hello World from Test Agent!"}
        )

    @patch('PersistenceService.service.PersistenceService')
    @patch('AgentService.service.AgentService')
    @patch('toolservices.service.ToolService')
    def test_process_task_with_agent_failure(self, mock_tool_service_class, mock_agent_service_class, mock_persistence_service_class):
        """
        Test Case 2: Process Task with Agent Failure
        Verify that the engine correctly handles a task when the Agent returns a failure.
        """
        # Create mock instances
        mock_persistence_service = Mock()
        mock_agent_service = Mock()
        mock_tool_service = Mock()
        
        # Configure the mock classes to return our mock instances
        mock_persistence_service_class.return_value = mock_persistence_service
        mock_agent_service_class.return_value = mock_agent_service
        mock_tool_service_class.return_value = mock_tool_service
        
        # Import here to avoid database connection issues
        from interfaces import TaskDefinition, AgentResult, AgentIntent
        
        # Create a test task
        task = TaskDefinition(
            task_id="test-task-2",
            assignee_id="Agent:TestAgent",
            input_data={"should_fail": True}
        )
        
        # Import the function after patching to avoid database connection issues
        from CentralGraphEngine.engine import process_task
        
        # Mock agent service to return a failure
        agent_result = AgentResult(
            status="FAILURE",
            output=AgentIntent(thought="Something went wrong.", intent=None),
            failure_details=None
        )
        
        # Configure the mock to return our failure result
        mock_agent_service.execute_agent.return_value = agent_result
        
        # Process the task
        process_task(task)
        
        # Verify the agent was called with the correct task
        mock_agent_service.execute_agent.assert_called_once_with(task)
        
        # Verify the task status was updated to FAILED
        mock_persistence_service.update_task_status.assert_called_once_with(
            task_id="test-task-2",
            status="FAILED",
            result={
                "failure_details": None,
                "thought": "Something went wrong."
            }
        )

    @patch('PersistenceService.service.PersistenceService')
    @patch('AgentService.service.AgentService')
    @patch('toolservices.service.ToolService')
    @patch('CentralGraphEngine.engine.time.sleep')
    def test_main_loop_with_no_pending_tasks(self, mock_sleep, mock_tool_service_class, mock_agent_service_class, mock_persistence_service_class):
        """
        Test Case 3: Main Loop with No Pending Tasks
        Verify that the main loop correctly handles the case when there are no pending tasks.
        """
        # Create mock instances
        mock_persistence_service = Mock()
        mock_agent_service = Mock()
        mock_tool_service = Mock()
        
        # Configure the mock classes to return our mock instances
        mock_persistence_service_class.return_value = mock_persistence_service
        mock_agent_service_class.return_value = mock_agent_service
        mock_tool_service_class.return_value = mock_tool_service
        
        # Mock persistence service to return an empty list
        mock_persistence_service.list_pending_tasks.return_value = []
        
        # Import the function after patching to avoid database connection issues
        from CentralGraphEngine.engine import main_loop
        
        # Run the main loop for one iteration and then break
        mock_sleep.side_effect = KeyboardInterrupt
        try:
            main_loop(polling_interval=1)
        except KeyboardInterrupt:
            pass  # Expected for test termination
        
        # Verify that list_pending_tasks was called
        mock_persistence_service.list_pending_tasks.assert_called_once()

    @patch('PersistenceService.service.PersistenceService')
    @patch('AgentService.service.AgentService')
    @patch('toolservices.service.ToolService')
    @patch('CentralGraphEngine.engine.time.sleep')
    @patch('CentralGraphEngine.engine.process_task')
    def test_main_loop_with_multiple_pending_tasks(self, mock_process_task, mock_sleep, mock_tool_service_class, mock_agent_service_class, mock_persistence_service_class):
        """
        Test Case 4: Main Loop with Multiple Pending Tasks
        Verify that the main loop correctly processes multiple pending tasks in sequence.
        """
        # Create mock instances
        mock_persistence_service = Mock()
        mock_agent_service = Mock()
        mock_tool_service = Mock()
        
        # Configure the mock classes to return our mock instances
        mock_persistence_service_class.return_value = mock_persistence_service
        mock_agent_service_class.return_value = mock_agent_service
        mock_tool_service_class.return_value = mock_tool_service
        
        # Import here to avoid database connection issues
        from interfaces import TaskDefinition
        
        # Create test tasks
        task1 = TaskDefinition(
            task_id="test-task-1",
            assignee_id="Agent:TestAgent1",
            input_data={"message": "Hello 1"}
        )
        
        task2 = TaskDefinition(
            task_id="test-task-2",
            assignee_id="Agent:TestAgent2",
            input_data={"message": "Hello 2"}
        )
        
        task3 = TaskDefinition(
            task_id="test-task-3",
            assignee_id="Agent:TestAgent3",
            input_data={"message": "Hello 3"}
        )
        
        # Mock persistence service to return the tasks
        mock_persistence_service.list_pending_tasks.return_value = [task1, task2, task3]
        
        # Import the function after patching to avoid database connection issues
        from CentralGraphEngine.engine import main_loop
        
        # Run the main loop for one iteration and then break
        mock_sleep.side_effect = KeyboardInterrupt
        try:
            main_loop(polling_interval=1)
        except KeyboardInterrupt:
            pass  # Expected for test termination
        
        # Verify that list_pending_tasks was called
        mock_persistence_service.list_pending_tasks.assert_called_once()
        
        # Verify that process_task was called for each task
        self.assertEqual(mock_process_task.call_count, 3)
        mock_process_task.assert_any_call(task1)
        mock_process_task.assert_any_call(task2)
        mock_process_task.assert_any_call(task3)

    @patch('PersistenceService.service.PersistenceService')
    @patch('AgentService.service.AgentService')
    @patch('toolservices.service.ToolService')
    @patch('CentralGraphEngine.engine.time.sleep')
    def test_error_handling_in_main_loop(self, mock_sleep, mock_tool_service_class, mock_agent_service_class, mock_persistence_service_class):
        """
        Test Case 5: Error Handling in Main Loop
        Verify that the main loop gracefully handles unexpected errors and continues running.
        """
        # Create mock instances
        mock_persistence_service = Mock()
        mock_agent_service = Mock()
        mock_tool_service = Mock()
        
        # Configure the mock classes to return our mock instances
        mock_persistence_service_class.return_value = mock_persistence_service
        mock_agent_service_class.return_value = mock_agent_service
        mock_tool_service_class.return_value = mock_tool_service
        
        # Mock persistence service to throw an exception
        mock_persistence_service.list_pending_tasks.side_effect = Exception("Database connection failed")
        
        # Import the function after patching to avoid database connection issues
        from CentralGraphEngine.engine import main_loop
        
        # Run the main loop for one iteration and then break
        mock_sleep.side_effect = [None, KeyboardInterrupt]
        try:
            main_loop(polling_interval=1)
        except KeyboardInterrupt:
            pass  # Expected for test termination
        
        # Verify that the engine continued running (slept) after the error
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_any_call(1)  # The polling interval

    def test_evaluate_condition_placeholder(self):
        """
        Test the evaluate_condition function (placeholder for M1)
        """
        # For M1, this should always return True
        from CentralGraphEngine.engine import evaluate_condition
        result = evaluate_condition({"some": "condition"}, {"some": "result"})
        self.assertTrue(result)

    @patch('PersistenceService.service.PersistenceService')
    @patch('AgentService.service.AgentService')
    @patch('toolservices.service.ToolService')
    def test_process_directives_placeholder(self, mock_tool_service_class, mock_agent_service_class, mock_persistence_service_class):
        """
        Test the process_directives function (placeholder for M1)
        """
        # Create mock instances
        mock_persistence_service = Mock()
        mock_agent_service = Mock()
        mock_tool_service = Mock()
        
        # Configure the mock classes to return our mock instances
        mock_persistence_service_class.return_value = mock_persistence_service
        mock_agent_service_class.return_value = mock_agent_service
        mock_tool_service_class.return_value = mock_tool_service
        
        # Import here to avoid database connection issues
        from interfaces import TaskDefinition, TaskDirectives, LoopDirective
        
        # Create test directives
        loop_directive = LoopDirective(
            type="PARALLEL_ITERATION",
            iteration_input_key="items",
            input_source_task_id="source_task_1",
            task_template=TaskDefinition(
                task_id="loop_inner_task",
                input_data={"item": "{item}"},
                assignee_id="Agent:Worker"
            )
        )
        
        directives = TaskDirectives(
            loop_directive=loop_directive,
            timeout_seconds=300
        )
        
        # Import the function after patching to avoid database connection issues
        from CentralGraphEngine.engine import process_directives
        
        # Process the directives
        result = process_directives(directives, "test-task-id")
        
        # Should return True
        self.assertTrue(result)

    @patch('PersistenceService.service.PersistenceService')
    @patch('AgentService.service.AgentService')
    @patch('toolservices.service.ToolService')
    def test_handle_completed_task(self, mock_tool_service_class, mock_agent_service_class, mock_persistence_service_class):
        """
        Test handle_completed_task function
        """
        # Create mock instances
        mock_persistence_service = Mock()
        mock_agent_service = Mock()
        mock_tool_service = Mock()
        
        # Configure the mock classes to return our mock instances
        mock_persistence_service_class.return_value = mock_persistence_service
        mock_agent_service_class.return_value = mock_agent_service
        mock_tool_service_class.return_value = mock_tool_service
        
        # Import here to avoid database connection issues
        from interfaces import TaskDefinition
        
        # Create a test task
        task = TaskDefinition(
            task_id="completed-task-1",
            assignee_id="Agent:TestAgent",
            input_data={"message": "Hello Engine"}
        )
        
        # Mock persistence service to return some edges
        mock_edge = Mock()
        mock_edge.source_task_id = "completed-task-1"
        mock_edge.target_task_id = "next-task-1"
        mock_persistence_service.get_outgoing_edges.return_value = [mock_edge]
        
        # Import the function after patching to avoid database connection issues
        from CentralGraphEngine.engine import handle_completed_task
        
        # Handle the completed task
        handle_completed_task(task)
        
        # Verify get_outgoing_edges was called
        mock_persistence_service.get_outgoing_edges.assert_called_once_with("completed-task-1")
    
    @patch('PersistenceService.service.PersistenceService')
    @patch('AgentService.service.AgentService')
    @patch('toolservices.service.ToolService')
    def test_process_pending_task_with_tool_call_request(self, mock_tool_service_class, mock_agent_service_class, mock_persistence_service_class):
        """
        Test Case 6: Process Pending Task with ToolCallRequest (M2 Enhancement)
        Verify that the engine can process a pending task assigned to an Agent 
        and correctly handle a ToolCallRequest response.
        """
        # Create mock instances
        mock_persistence_service = Mock()
        mock_agent_service = Mock()
        mock_tool_service = Mock()
        
        # Configure the mock classes to return our mock instances
        mock_persistence_service_class.return_value = mock_persistence_service
        mock_agent_service_class.return_value = mock_agent_service
        mock_tool_service_class.return_value = mock_tool_service
        
        # Import here to avoid database connection issues
        from interfaces import TaskDefinition, AgentResult, AgentIntent, ToolCallRequest, ToolResult
        
        # Create a test task
        task = TaskDefinition(
            task_id="test-task-6",
            assignee_id="Agent:TestAgent",
            input_data={"message": "Call a tool"}
        )
        
        # Import the function after patching to avoid database connection issues
        from CentralGraphEngine.engine import process_task
        
        # Mock agent service to return a ToolCallRequest
        tool_call_request = ToolCallRequest(
            tool_id="test_tool",
            arguments={"param1": "value1", "param2": "value2"}
        )
        agent_intent = AgentIntent(thought="Need to call a tool.", intent=tool_call_request)
        agent_result = AgentResult(status="SUCCESS", output=agent_intent)
        
        # Configure the mock to return our result
        mock_agent_service.execute_agent.return_value = agent_result
        
        # Mock tool service to return a successful result
        tool_result = ToolResult(
            status="SUCCESS",
            output={"result": "Tool executed successfully"}
        )
        mock_tool_service.run_tool.return_value = tool_result
        
        # Process the task
        process_task(task)
        
        # Verify the agent was called with the correct task
        mock_agent_service.execute_agent.assert_called_once_with(task)
        
        # Verify the tool service was called with the tool call request
        mock_tool_service.run_tool.assert_called_once_with(tool_call_request)
        
        # Verify the task context was updated with the tool result (but not marked as COMPLETED)
        mock_persistence_service.update_task_context.assert_called_once_with(
            task_id="test-task-6",
            context={"last_tool_result": tool_result}
        )
        
        # Verify that update_task_status was NOT called (task should remain PENDING)
        mock_persistence_service.update_task_status.assert_not_called()

if __name__ == '__main__':
    unittest.main()