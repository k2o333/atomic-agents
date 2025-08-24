#!/usr/bin/env python3
"""
Integration test for Central Graph Engine Ultimate Version
"""

import sys
import os
import uuid
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, '/root/projects/atom_agents')

from CentralGraphEngine.engine import (
    handle_completed_task, 
    process_task, 
    apply_data_flow,
    main_loop
)
from interfaces import (
    TaskDefinition, 
    EdgeDefinition, 
    AgentResult, 
    FinalAnswer, 
    ToolCallRequest, 
    PlanBlueprint,
    Condition,
    DataFlow
)

class MockPersistenceService:
    def __init__(self):
        self.calls = []
        
    def get_task_and_lock(self, task_id):
        self.calls.append(f"get_task_and_lock({task_id})")
        # Return a mock task
        return TaskDefinition(
            task_id=str(task_id),
            assignee_id="Agent:TestAgent",
            input_data={"test": "data"},
            status="PENDING"
        )
        
    def get_outgoing_edges(self, task_id):
        self.calls.append(f"get_outgoing_edges({task_id})")
        # Return mock edges
        if str(task_id) == "completed-task-1":
            return [
                EdgeDefinition(
                    source_task_id="completed-task-1",
                    target_task_id="downstream-task-1",
                    condition=Condition(evaluator="CEL", expression="result.score > 80"),
                    data_flow=DataFlow(mappings={"input_score": "score"})
                )
            ]
        return []
        
    def update_task_status_and_result(self, task_id, status, result=None):
        self.calls.append(f"update_task_status_and_result({task_id}, {status}, {result})")
        return True
        
    def update_task_context(self, task_id, context):
        self.calls.append(f"update_task_context({task_id}, {context})")
        return True
        
    def create_workflow_from_blueprint(self, blueprint):
        self.calls.append(f"create_workflow_from_blueprint(blueprint)")
        return True

class MockAgentService:
    def execute_agent(self, task):
        self.last_task = task
        # Return a mock agent result
        return AgentResult(
            status="SUCCESS",
            output={"thought": "Test thought", "intent": FinalAnswer(content="Test final answer")}
        )

class MockToolService:
    def run_tool(self, tool_call):
        self.last_tool_call = tool_call
        return {"status": "SUCCESS", "output": "Test tool result"}

def test_handle_completed_task():
    """Test handle_completed_task function with edge conditions."""
    print("Testing handle_completed_task...")
    
    # Create a mock persistence service
    mock_persistence = MockPersistenceService()
    
    # Patch the global persistence_service
    with patch('CentralGraphEngine.engine.persistence_service', mock_persistence):
        # Create a completed task
        task = TaskDefinition(
            task_id="completed-task-1",
            assignee_id="Agent:TestAgent",
            input_data={},
            status="COMPLETED"
        )
        
        # Call handle_completed_task
        handle_completed_task(task)
        
        # Verify the calls were made
        expected_calls = [
            "get_outgoing_edges(completed-task-1)"
        ]
        
        for call in expected_calls:
            assert call in mock_persistence.calls, f"Expected call {call} not found in {mock_persistence.calls}"
        
        print("handle_completed_task test passed!")

def test_process_task_with_planblueprint():
    """Test process_task function with PlanBlueprint intent."""
    print("Testing process_task with PlanBlueprint...")
    
    # Create a mock persistence service
    mock_persistence = MockPersistenceService()
    
    # Create a mock agent service that returns a PlanBlueprint
    mock_agent = MockAgentService()
    mock_agent.execute_agent = Mock(return_value=AgentResult(
        status="SUCCESS",
        output={"thought": "Creating plan", "intent": PlanBlueprint(
            new_tasks=[],
            new_edges=[],
            update_tasks=[]
        )}
    ))
    
    # Patch the global services
    with patch('CentralGraphEngine.engine.persistence_service', mock_persistence), \
         patch('CentralGraphEngine.engine.agent_service', mock_agent):
        
        # Create a pending task
        task = TaskDefinition(
            task_id="plan-task-1",
            assignee_id="Agent:PlannerAgent",
            input_data={"goal": "Test plan"},
            status="PENDING"
        )
        
        # Call process_task
        process_task(task)
        
        # Verify the calls were made
        expected_calls = [
            "create_workflow_from_blueprint(blueprint)",
            "update_task_status_and_result(plan-task-1, COMPLETED, {'message': 'Plan executed successfully'})"
        ]
        
        for call in expected_calls:
            assert call in mock_persistence.calls, f"Expected call {call} not found in {mock_persistence.calls}"
        
        print("process_task with PlanBlueprint test passed!")

def test_apply_data_flow():
    """Test apply_data_flow function."""
    print("Testing apply_data_flow...")
    
    # Test with valid data flow
    data_flow = DataFlow(mappings={
        "target_field": "source_field",
        "another_field": "another_source"
    })
    
    source_result = {
        "source_field": "test_value",
        "another_source": 42,
        "extra_field": "extra_value"
    }
    
    result = apply_data_flow(data_flow, source_result)
    
    expected = {
        "target_field": "test_value",
        "another_field": 42
    }
    
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test with empty data flow
    empty_result = apply_data_flow(None, source_result)
    assert empty_result == {}, f"Expected empty dict, got {empty_result}"
    
    print("apply_data_flow test passed!")

def run_all_tests():
    """Run all integration tests."""
    print("Running Central Graph Engine Integration Tests...")
    print("=" * 50)
    
    try:
        test_apply_data_flow()
        test_handle_completed_task()
        test_process_task_with_planblueprint()
        
        print("=" * 50)
        print("All integration tests passed!")
        return True
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)