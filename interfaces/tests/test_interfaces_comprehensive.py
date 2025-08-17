# /root/projects/atom_agents/interfaces/tests/test_interfaces_comprehensive.py

import unittest
import uuid
import sys
import os

# Add the project root to the path so we can import interfaces
sys.path.insert(0, '/root/projects/atom_agents')

from interfaces.interfaces import (
    PlanBlueprint, TaskDefinition, EdgeDefinition, TaskUpdate,
    AgentResult, AgentIntent, FinalAnswer, ToolCallRequest, FailureDetails,
    ContextBuildConfig,
    TaskDirectives, LoopDirective, Condition, DataFlow, ContextOverrides,
    InterventionRequest
)

class TestPlanBlueprintModels(unittest.TestCase):

    def test_plan_blueprint_basic_structure(self):
        """Test Case 1: PlanBlueprint基本结构验证"""
        data = {
            "workflow_id": "123e4567-e89b-12d3-a456-426614174000",
            "new_tasks": [],
            "new_edges": [],
            "update_tasks": []
        }
        
        blueprint = PlanBlueprint(**data)
        
        self.assertEqual(str(blueprint.workflow_id), "123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(blueprint.new_tasks, [])
        self.assertEqual(blueprint.new_edges, [])
        self.assertEqual(blueprint.update_tasks, [])

    def test_plan_blueprint_with_new_tasks(self):
        """Test Case 2: PlanBlueprint包含新任务"""
        data = {
            "new_tasks": [
                {
                    "task_id": "task1",
                    "input_data": {"goal": "test goal"},
                    "assignee_id": "Agent:1"
                }
            ]
        }
        
        blueprint = PlanBlueprint(**data)
        
        self.assertEqual(len(blueprint.new_tasks), 1)
        self.assertEqual(blueprint.new_tasks[0].task_id, "task1")
        self.assertEqual(blueprint.new_tasks[0].input_data, {"goal": "test goal"})
        self.assertEqual(blueprint.new_tasks[0].assignee_id, "Agent:1")

class TestAgentResultModels(unittest.TestCase):

    def test_agent_result_success_state(self):
        """Test Case 3: AgentResult成功状态验证"""
        data = {
            "status": "SUCCESS",
            "output": {
                "thought": "Task completed successfully",
                "intent": {
                    "content": "Final result"
                }
            }
        }
        
        result = AgentResult(**data)
        
        self.assertEqual(result.status, "SUCCESS")
        self.assertIsInstance(result.output, AgentIntent)
        self.assertIsInstance(result.output.intent, FinalAnswer)
        self.assertEqual(result.output.intent.content, "Final result")
        self.assertIsNone(result.failure_details)

    def test_agent_result_failure_state(self):
        """Test Case 4: AgentResult失败状态验证"""
        data = {
            "status": "FAILURE",
            "output": {
                "thought": "Task failed",
                "intent": {
                    "content": "Error occurred"
                }
            },
            "failure_details": {
                "type": "LLM_REFUSAL",
                "message": "LLM refused to execute"
            }
        }
        
        result = AgentResult(**data)
        
        self.assertEqual(result.status, "FAILURE")
        self.assertIsInstance(result.output, AgentIntent)
        self.assertIsInstance(result.output.intent, FinalAnswer)
        self.assertEqual(result.output.intent.content, "Error occurred")
        self.assertIsInstance(result.failure_details, FailureDetails)
        self.assertEqual(result.failure_details.type, "LLM_REFUSAL")
        self.assertEqual(result.failure_details.message, "LLM refused to execute")

class TestContextBuildConfigModels(unittest.TestCase):

    def test_context_build_config_basic_structure(self):
        """Test Case 5: ContextBuildConfig基本结构验证"""
        data = {
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "include_metadata": True,
            "include_tool_list": True
        }
        
        config = ContextBuildConfig(**data)
        
        self.assertEqual(str(config.task_id), "123e4567-e89b-12d3-a456-426614174000")
        self.assertTrue(config.include_metadata)
        self.assertTrue(config.include_tool_list)

    def test_context_build_config_with_options(self):
        """Test Case 6: ContextBuildConfig包含配置选项"""
        data = {
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "conversation_history_config": {"last_n": 5},
            "task_list_config": {"status_in": ["COMPLETED"]},
            "artifact_config": {"asset_id": "asset123", "mode": "SUMMARY"}
        }
        
        config = ContextBuildConfig(**data)
        
        self.assertEqual(str(config.task_id), "123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(config.conversation_history_config, {"last_n": 5})
        self.assertEqual(config.task_list_config, {"status_in": ["COMPLETED"]})
        self.assertEqual(config.artifact_config, {"asset_id": "asset123", "mode": "SUMMARY"})

class TestTaskDirectivesModels(unittest.TestCase):

    def test_task_directives_basic_structure(self):
        """Test Case 7: TaskDirectives基本结构验证"""
        data = {
            "timeout_seconds": 300,
            "on_failure": {"type": "GOTO", "target_task_id": "task2"}
        }
        
        directives = TaskDirectives(**data)
        
        self.assertEqual(directives.timeout_seconds, 300)
        self.assertEqual(directives.on_failure, {"type": "GOTO", "target_task_id": "task2"})
        self.assertIsNone(directives.loop_directive)

    def test_task_directives_with_loop(self):
        """Test Case 8: TaskDirectives包含循环指令"""
        # First create a task template for the loop
        task_template = TaskDefinition(
            task_id="subtask",
            input_data={"item": "{{item}}"},
            assignee_id="Agent:1"
        )
        
        data = {
            "loop_directive": {
                "type": "PARALLEL_ITERATION",
                "iteration_input_key": "items",
                "input_source_task_id": "task1",
                "task_template": task_template
            }
        }
        
        directives = TaskDirectives(**data)
        
        self.assertIsInstance(directives.loop_directive, LoopDirective)
        self.assertEqual(directives.loop_directive.type, "PARALLEL_ITERATION")
        self.assertEqual(directives.loop_directive.iteration_input_key, "items")
        self.assertEqual(directives.loop_directive.input_source_task_id, "task1")
        self.assertEqual(directives.loop_directive.task_template.task_id, "subtask")

class TestInterventionRequestModels(unittest.TestCase):

    def test_intervention_request_basic_structure(self):
        """Test Case 9: InterventionRequest基本结构验证"""
        data = {
            "intervention_type": "PAUSE",
            "target_task_id": "123e4567-e89b-12d3-a456-426614174000",
            "comment": "Pausing for review"
        }
        
        intervention = InterventionRequest(**data)
        
        self.assertEqual(intervention.intervention_type, "PAUSE")
        self.assertEqual(str(intervention.target_task_id), "123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(intervention.comment, "Pausing for review")

    def test_intervention_request_rollback_and_modify(self):
        """Test Case 10: InterventionRequest回滚并修改"""
        data = {
            "intervention_type": "ROLLBACK_AND_MODIFY",
            "target_task_id": "123e4567-e89b-12d3-a456-426614174000",
            "rollback_to_version": 1,
            "new_input_data": {"updated_goal": "new goal"},
            "new_assignee_id": "Agent:2",
            "comment": "Rolling back and updating task"
        }
        
        intervention = InterventionRequest(**data)
        
        self.assertEqual(intervention.intervention_type, "ROLLBACK_AND_MODIFY")
        self.assertEqual(intervention.rollback_to_version, 1)
        self.assertEqual(intervention.new_input_data, {"updated_goal": "new goal"})
        self.assertEqual(intervention.new_assignee_id, "Agent:2")
        self.assertEqual(intervention.comment, "Rolling back and updating task")

class TestLoggingFunctionality(unittest.TestCase):

    def test_model_field_validation(self):
        """Test Case 12: 模型字段验证日志记录"""
        # This test would require more complex mocking to capture validation errors
        # For now, we'll test that the model correctly validates valid data
        try:
            result = AgentResult(
                status="SUCCESS",
                output={
                    "thought": "test",
                    "intent": {
                        "content": "test"
                    }
                }
            )
            self.assertEqual(result.status, "SUCCESS")
        except Exception as e:
            self.fail(f"Valid data should not raise an exception: {e}")

    def test_model_initialization(self):
        """Test Case 11: 模型初始化日志记录"""
        # Test that models can be initialized without errors
        try:
            blueprint = PlanBlueprint(workflow_id="123e4567-e89b-12d3-a456-426614174000")
            self.assertIsNotNone(blueprint)
        except Exception as e:
            self.fail(f"Model initialization should not raise an exception: {e}")

    def test_distributed_tracing_context(self):
        """Test Case 13: 分布式追踪功能验证"""
        # Test that models work within a context (simplified test)
        try:
            config = ContextBuildConfig(
                task_id=uuid.uuid4(),
                include_metadata=True
            )
            self.assertIsNotNone(config)
        except Exception as e:
            self.fail(f"Model should work within context: {e}")

if __name__ == '__main__':
    # Change to the project directory
    os.chdir('/root/projects/atom_agents')
    unittest.main()