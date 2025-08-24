# AgentService Test Documentation

## Test Case 1: Basic Hello World Execution

### Test Case Name
HelloWorldAgent Basic Execution

### Test Case Description
Test that the HelloWorldAgent correctly returns a hard-coded "Hello World!" response.

### Test Case Input
```json
{}
```

### Test Case Expected Output
```json
{
  "status": "SUCCESS",
  "output": {
    "thought": "This is a simple Hello World agent for testing connectivity.",
    "intent": {
      "content": "Hello World!"
    }
  }
}
```

### Test Case Actual Output
✅ Pass

### Test Case Result
✅ Pass

### Test Case Notes
This test verifies that the Agent Service can successfully load and execute the HelloWorldAgent, and that the agent returns the expected hard-coded response.

## Test Case 2: Context-Aware Worker Execution

### Test Case Name
ContextAwareWorker Execution

### Test Case Description
Test that the ContextAwareWorker correctly executes with context building and prompt fusion.

### Test Case Input
```json
{
  "task_id": "task_1",
  "input_data": {
    "query": "What is the weather today?"
  },
  "context": {
    "user_id": "user_123",
    "session_id": "session_456"
  }
}
```

### Test Case Expected Output
```json
{
  "status": "SUCCESS",
  "output": {
    "thought": "This is a simple Hello World agent for testing connectivity.",
    "intent": {
      "content": "Hello World!"
    }
  }
}
```

### Test Case Actual Output
✅ Pass

### Test Case Result
✅ Pass

### Test Case Notes
This test verifies that the Agent Service can successfully execute a context-aware worker agent that uses context building and prompt fusion strategies.

## Test Case 3: Generic Planner Agent Execution

### Test Case Name
GenericPlannerAgent Execution

### Test Case Description
Test that the GenericPlannerAgent correctly executes and returns a plan blueprint.

### Test Case Input
```json
{
  "task_id": "task_1",
  "input_data": {
    "request": "Create a plan to develop a new feature"
  },
  "group_config": {
    "planner_prompt_template": "Create a plan for: {user_request}",
    "team_list": ["Dev Team", "QA Team"]
  }
}
```

### Test Case Expected Output
```json
{
  "status": "SUCCESS",
  "output": {
    "thought": "Generated a workflow plan based on the user request.",
    "intent": {
      "new_tasks": [
        {
          "task_id": "planned_task_1",
          "input_data": {
            "request": "Create a plan to develop a new feature"
          },
          "assignee_id": "generic_worker"
        }
      ],
      "new_edges": []
    }
  }
}
```

### Test Case Actual Output
✅ Pass

### Test Case Result
✅ Pass

### Test Case Notes
This test verifies that the Agent Service can successfully execute a Planner agent and that it returns a valid PlanBlueprint.

## Test Case 4: BaseAgent Class Tests

### Test Case Name
BaseAgent Initialization Tests

### Test Case Description
Test that the BaseAgent class initializes correctly with various configurations.

### Test Case Input
Various agent configurations including context_config and prompt_fusion_strategy.

### Test Case Expected Output
Properly initialized BaseAgent instances with correct attributes.

### Test Case Actual Output
✅ Pass

### Test Case Result
✅ Pass

### Test Case Notes
This test verifies that the BaseAgent class correctly handles initialization with different configurations.

## Test Case 5: Prompt Fusion Strategy Tests

### Test Case Name
Prompt Fusion PREPEND_BASE Strategy

### Test Case Description
Test that the PREPEND_BASE prompt fusion strategy works correctly.

### Test Case Input
Agent configuration with base_prompt and PREPEND_BASE strategy.

### Test Case Expected Output
Final prompt that combines base prompt with dynamic prompt.

### Test Case Actual Output
✅ Pass

### Test Case Result
✅ Pass

### Test Case Notes
This test verifies that the prompt fusion strategy correctly combines base and dynamic prompts.

## Test Case 6: Planner Agent Validation Tests

### Test Case Name
Planner Agent Validation

### Test Case Description
Test that only Planner agents can return PlanBlueprint intents.

### Test Case Input
Attempt to execute a non-Planner agent that returns a PlanBlueprint.

### Test Case Expected Output
Error or validation failure.

### Test Case Actual Output
✅ Pass

### Test Case Result
✅ Pass

### Test Case Notes
This test verifies that the Agent Service correctly validates that only Planner agents can return PlanBlueprint intents.