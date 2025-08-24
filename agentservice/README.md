# Agent Service

## Module Overview

The Agent Service is a core component responsible for instantiating and executing Agent scripts. It acts as the execution environment for all Agent logic, dynamically loading and running Agent implementations based on capability definitions.

## M3 Features Overview

### Context Building Integration
The Agent Service now automatically builds context for agents before execution based on their `context_config` definition in `capabilities.json`. This ensures that agents have all the necessary information and constraints before they run.

### Planner Agent Support
Special handling for Planner agents that return `PlanBlueprint` intents. Only agents with `role: PLANNER` are allowed to return PlanBlueprint intents, ensuring proper validation.

### Prompt Fusion Strategy
Implementation of prompt fusion strategies like `PREPEND_BASE` that allow agents to combine base prompts with dynamic prompts for more effective LLM interactions.

## HelloWorldAgent

A simple agent that returns a hard-coded "Hello World!" response for testing connectivity.

### Usage

The HelloWorldAgent can be executed through the Agent Service by referencing its capability ID `hello_world_agent`.

### Expected Output

When executed, the agent will return:
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

## Generic Planner Agent

A generic planner agent that generates workflow plans based on user requests.

### Usage

The GenericPlannerAgent can be executed through the Agent Service by referencing its capability ID `generic_planner_agent`.

## Context-Aware Worker

A worker agent that demonstrates context building and prompt fusion capabilities.

### Usage

The ContextAwareWorker can be executed through the Agent Service by referencing its capability ID `context_aware_worker`.

## Directory Structure

```
agentservice/
├── agent_service.py          # Main AgentService implementation
├── agent_factory.py          # Agent factory component
├── agent_executor.py         # Agent executor component
├── base_agent.py             # BaseAgent SDK
├── baseagent/                # Base agent components (migrated from /agents)
│   ├── base_agent.py         # BaseAgent class
│   ├── generic_planner_agent.py  # Generic Planner agent implementation
│   ├── tests/                # Tests for baseagent components
│   │   └── base_agent_test.py  # Tests for BaseAgent
│   └── test.md               # Test documentation
├── generic_agents/           # Generic agent implementations
│   ├── HelloWorldAgent.py    # Simple Hello World agent
│   └── capabilities.json     # Capabilities registry
├── tests/                    # Tests for agentservice components
│   ├── test_agent_service.py # Tests for AgentService
│   └── test_m3_features.py   # Tests for M3 features
├── example_usage.py          # Example usage scripts
├── example_usage_m3.py       # M3 features example
├── test.md                   # Test documentation
├── README.md                 # This file
└── AgentService.md           # Detailed documentation
```

## Example Usage

### Running the examples:
```bash
python agentservice/example_usage.py
python agentservice/example_usage_m3.py
```

### Running the tests:
```bash
python -m agentservice.tests.test_agent_service
python -m agentservice.tests.test_m3_features
python -m agentservice.baseagent.tests.base_agent_test
```