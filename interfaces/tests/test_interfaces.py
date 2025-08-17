# /root/projects/atom_agents/interfaces/tests/test_interfaces.py

import unittest
from uuid import UUID
from interfaces import (
    PlanBlueprint, TaskDefinition, EdgeDefinition,
    AgentResult, AgentIntent, FinalAnswer, ToolCallRequest,
    ContextBuildConfig,
    TaskDirectives, LoopDirective, Condition,
    InterventionRequest
)

class TestInterfaces(unittest.TestCase):

    def test_plan_blueprint_creation(self):
        """Test creation of a basic PlanBlueprint."""
        task_def = TaskDefinition(
            task_id="task_1",
            input_data={"goal": "Test goal"},
            assignee_id="Agent:TestAgent"
        )
        
        edge_def = EdgeDefinition(
            source_task_id="task_1",
            target_task_id="task_2"
        )
        
        blueprint = PlanBlueprint(
            new_tasks=[task_def],
            new_edges=[edge_def]
        )
        
        self.assertEqual(len(blueprint.new_tasks), 1)
        self.assertEqual(blueprint.new_tasks[0].task_id, "task_1")
        self.assertEqual(len(blueprint.new_edges), 1)

    def test_agent_result_final_answer(self):
        """Test AgentResult with FinalAnswer intent."""
        final_answer = FinalAnswer(content="This is the final answer.")
        agent_intent = AgentIntent(thought="Processing complete.", intent=final_answer)
        result = AgentResult(status="SUCCESS", output=agent_intent)
        
        self.assertEqual(result.status, "SUCCESS")
        self.assertIsInstance(result.output.intent, FinalAnswer)
        self.assertEqual(result.output.intent.content, "This is the final answer.")

    def test_agent_result_tool_call(self):
        """Test AgentResult with ToolCallRequest intent."""
        tool_call = ToolCallRequest(tool_id="NativeTools.web.search", arguments={"query": "test"})
        agent_intent = AgentIntent(thought="Need to search.", intent=tool_call)
        result = AgentResult(status="SUCCESS", output=agent_intent)
        
        self.assertEqual(result.status, "SUCCESS")
        self.assertIsInstance(result.output.intent, ToolCallRequest)
        self.assertEqual(result.output.intent.tool_id, "NativeTools.web.search")

    def test_context_build_config(self):
        """Test ContextBuildConfig model."""
        config = ContextBuildConfig(
            task_id=UUID('12345678-1234-5678-1234-567812345678'),
            include_metadata=True,
            experience_config={"top_k": 5}
        )
        
        self.assertEqual(config.task_id, UUID('12345678-1234-5678-1234-567812345678'))
        self.assertTrue(config.include_metadata)
        self.assertEqual(config.experience_config, {"top_k": 5})

    def test_task_directives(self):
        """Test TaskDirectives and nested LoopDirective."""
        # Create a simple task template for the loop
        inner_task_template = TaskDefinition(
            task_id="loop_inner_task",
            input_data={"item": "{item}"},
            assignee_id="Agent:Worker"
        )
        
        loop_directive = LoopDirective(
            type="PARALLEL_ITERATION",
            iteration_input_key="items",
            input_source_task_id="source_task_1",
            task_template=inner_task_template,
            max_iterations=10
        )
        
        task_directives = TaskDirectives(
            loop_directive=loop_directive,
            timeout_seconds=300
        )
        
        self.assertEqual(task_directives.loop_directive.type, "PARALLEL_ITERATION")
        self.assertEqual(task_directives.timeout_seconds, 300)
        self.assertEqual(task_directives.loop_directive.max_iterations, 10)

    def test_intervention_request(self):
        """Test InterventionRequest model."""
        intervention = InterventionRequest(
            intervention_type="ROLLBACK_AND_MODIFY",
            target_task_id=UUID('12345678-1234-5678-1234-567812345678'),
            new_input_data={"corrected_goal": "New goal"},
            comment="Fixing an error."
        )
        
        self.assertEqual(intervention.intervention_type, "ROLLBACK_AND_MODIFY")
        self.assertEqual(intervention.new_input_data, {"corrected_goal": "New goal"})

if __name__ == '__main__':
    unittest.main()