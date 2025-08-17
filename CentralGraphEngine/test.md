# Central Graph Engine Test Plan (M1)

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