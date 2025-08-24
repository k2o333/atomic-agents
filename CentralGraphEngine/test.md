# Central Graph Engine Test Plan (Ultimate Version)

## Test Case 1: Process Pending Task with FinalAnswer

### Description
Verify that the engine can process a pending task assigned to an Agent and correctly handle a FinalAnswer response.

### Input
A TaskDefinition with:
- task_id: "test-task-1"
- assignee_id: "Agent:TestAgent"
- input_data: {"message": "Hello Engine"}
- status: "PENDING"

### Expected Output
- The task status is updated to "COMPLETED"
- The task result contains the FinalAnswer content
- Appropriate log messages are generated

### Actual Output
[To be filled during testing]

### Result
[To be filled during testing]

### Notes
This test requires a mock AgentService that returns a predefined FinalAnswer.

## Test Case 2: Process Task with Agent Failure

### Description
Verify that the engine correctly handles a task when the Agent returns a failure.

### Input
A TaskDefinition with:
- task_id: "test-task-2"
- assignee_id: "Agent:TestAgent"
- input_data: {"should_fail": true}
- status: "PENDING"

### Expected Output
- The task status is updated to "FAILED"
- The task result contains the failure details
- Appropriate error log messages are generated

### Actual Output
[To be filled during testing]

### Result
[To be filled during testing]

### Notes
This test requires a mock AgentService that returns a failure response.

## Test Case 3: Main Loop with No Pending Tasks

### Description
Verify that the main loop correctly handles the case when there are no pending tasks.

### Input
An empty list of pending tasks from the PersistenceService

### Expected Output
- The engine sleeps for the polling interval
- An appropriate log message is generated indicating no tasks found

### Actual Output
[To be filled during testing]

### Result
[To be filled during testing]

### Notes
This test verifies the polling behavior when there's no work to do.

## Test Case 4: Main Loop with Multiple Pending Tasks

### Description
Verify that the main loop correctly processes multiple pending tasks in sequence.

### Input
A list of 3 TaskDefinitions with different task_ids, all with status "PENDING"

### Expected Output
- All 3 tasks are processed in sequence
- Each task's status is updated appropriately
- Log messages are generated for each task

### Actual Output
[To be filled during testing]

### Result
[To be filled during testing]

### Notes
This test verifies the engine's ability to handle a batch of tasks.

## Test Case 5: Error Handling in Main Loop

### Description
Verify that the main loop gracefully handles unexpected errors and continues running.

### Input
A PersistenceService that throws an exception when listing pending tasks

### Expected Output
- The exception is caught and logged
- The engine continues running after a delay
- No crash occurs

### Actual Output
[To be filled during testing]

### Result
[To be filled during testing]

### Notes
This test ensures the robustness of the main loop.

## Test Case 6: Process Pending Task with ToolCallRequest (M2 Enhancement)

### Description
Verify that the engine can process a pending task assigned to an Agent and correctly handle a ToolCallRequest response.

### Input
A TaskDefinition with:
- task_id: "test-task-6"
- assignee_id: "Agent:TestAgent"
- input_data: {"message": "Call a tool"}
- status: "PENDING"

### Expected Output
- The engine calls ToolService.run_tool() with the ToolCallRequest
- The task context is updated with the tool result
- The task status remains "PENDING" (not marked as COMPLETED)
- Appropriate log messages are generated
- The task is re-queued for agent re-entry (handled by database NOTIFY)

### Actual Output
[To be filled during testing]

### Result
[To be filled during testing]

### Notes
This test requires a mock ToolService that returns a predefined ToolResult.

## Test Case 7: Process Pending Task with PlanBlueprint (M3 Enhancement)

### Description
Verify that the engine can process a pending task assigned to an Agent and correctly handle a PlanBlueprint response.

### Input
A TaskDefinition with:
- task_id: "test-task-7"
- assignee_id: "Agent:PlannerAgent"
- input_data: {"goal": "Create a plan"}
- status: "PENDING"

### Expected Output
- The engine calls PersistenceService.create_workflow_from_blueprint() with the PlanBlueprint
- The original task status is updated to "COMPLETED"
- Appropriate log messages are generated

### Actual Output
[To be filled during testing]

### Result
[To be filled during testing]

### Notes
This test requires a mock AgentService that returns a predefined PlanBlueprint.

## Test Case 8: Handle Completed Task with Edge Conditions

### Description
Verify that the engine correctly handles a completed task by evaluating downstream edges.

### Input
A TaskDefinition with:
- task_id: "test-task-8"
- status: "COMPLETED"
- result: {"score": 90, "status": "success"}

### Expected Output
- The engine retrieves outgoing edges from PersistenceService
- Each edge condition is evaluated using ConditionEvaluator
- Downstream tasks are activated based on condition results
- Appropriate log messages are generated

### Actual Output
[To be filled during testing]

### Result
[To be filled during testing]

### Notes
This test requires a mock PersistenceService that returns predefined edges.

## Test Case 9: Condition Evaluation with Various Expressions

### Description
Verify that the ConditionEvaluator correctly evaluates various CEL-like expressions.

### Input
Various Condition objects with different expressions and context data

### Expected Output
- Simple boolean expressions evaluate correctly
- Context-based expressions evaluate correctly
- Numeric comparisons evaluate correctly
- Invalid expressions are handled gracefully

### Actual Output
- Simple boolean expressions evaluate correctly: PASS
- Context-based expressions evaluate correctly: PASS
- Numeric comparisons evaluate correctly: PASS
- Invalid expressions are handled gracefully: PASS

### Result
PASS

### Notes
This test is implemented in test_condition_evaluator.py and test_simple.py

## Test Case 10: Data Flow Mapping

### Description
Verify that data flow mappings correctly transform source task results to target task input.

### Input
A DataFlow with various mappings, source task result data

### Expected Output
- Source result data is correctly mapped to target input data
- Missing mappings result in empty target data
- Invalid mappings are handled gracefully

### Actual Output
- Source result data is correctly mapped to target input data: PASS
- Missing mappings result in empty target data: PASS
- Invalid mappings are handled gracefully: PASS (function handles None input)

### Result
PASS

### Notes
This test verifies the apply_data_flow function in engine.py. Tested in test_simple.py

## Test Case 11: Redis BRPOP Integration

### Description
Verify that the engine can connect to Redis and consume tasks via BRPOP.

### Input
Redis server with tasks in queue

### Expected Output
- Tasks are consumed from Redis queue using BRPOP
- Tasks are processed correctly
- Appropriate log messages are generated

### Actual Output
[To be filled during testing]

### Result
[To be filled during testing]

### Notes
This test requires a running Redis server and Notify Handler.