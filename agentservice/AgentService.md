# Agent Service Development Documentation

## Module Overview

The Agent Service is a core component of the Synapse platform responsible for instantiating and executing Agent scripts. It acts as the execution environment for all Agent logic, dynamically loading and running Agent implementations based on capability definitions.

This document provides a comprehensive guide to developing and extending the Agent Service.

## 1. Purpose and Responsibilities

The Agent Service serves as the "execution environment" for all Agents in the Synapse platform. Its primary responsibilities include:

1. **Dynamic Agent Loading**: Loading Agent implementations based on `implementation_path` defined in `capabilities.json`
2. **Agent Execution**: Running Agent scripts according to their type (Generic or Custom)
3. **Result Standardization**: Ensuring all Agent outputs conform to the `AgentResult` specification
4. **Integration with Other Services**: Coordinating with Context Service, LLM Gateway Service, and Tool Service as needed
5. **Tracing and Logging**: Providing distributed tracing capabilities for Agent executions

## 2. Architecture

The Agent Service follows a modular architecture that enables dynamic loading and execution of various Agent types:

1. **Agent Factory**: Responsible for creating Agent instances based on capability definitions
2. **Agent Executor**: Handles the actual execution of Agent scripts
3. **Base Agent Class**: Provides common functionality and interfaces for all Agent types
4. **Generic Agent Implementations**: Pre-built Agent templates for common use cases
5. **Result Validator**: Ensures all outputs conform to the `AgentResult` specification

**Important Boundary**: `AgentService` **only responsible for executing a single Agent's `.run()` method and returning its intent**. It **does not concern itself** with any workflow logic, such as: where the Agent should go next after execution (determined by the `Engine`'s `Edge`), or how the Agent was invoked (could be a linear task or part of a parallel loop). This strict separation of responsibilities ensures that `AgentService` is a pure, reusable "**Agent Execution Runtime**".

## 3. M1 Implementation Details

### 3.1. Core Requirements

In the M1 phase, the Agent Service must implement a simplified version that can execute a "Hello World" Agent:

1. **Agent Script Executor**:
   - Must be able to dynamically load and run Agent scripts based on `implementation_path`
   - Must handle the simplest case: a script that returns a hard-coded `AgentResult`

2. **Generic Worker Agent Support**:
   - Must support the `GenericWorkerAgent.py` script template
   - Must be able to execute an Agent based on JSON configuration

3. **Result Validation**:
   - Must ensure all outputs strictly follow the `AgentResult` v1.1 specification
   - Must handle both SUCCESS and FAILURE statuses

### 3.2. Interface with Central Graph Engine

The Agent Service interacts with the Central Graph Engine through a well-defined interface:

1. **Input**: Receives a task with:
   - `agent_id` to identify which Agent to execute
   - `task_data` containing the input data for the Agent

2. **Process**:
   - Looks up the Agent configuration in the capability registry
   - Loads and instantiates the appropriate Agent class
   - Executes the Agent's `run()` method
   - Validates the result

3. **Output**: Returns an `AgentResult` object that conforms to the specification in `interfaces.py`

### 3.3. Hello World Agent Implementation

For M1, the Agent Service must support a simple "Hello World" Agent:

```python
# HelloWorldAgent.py
from interfaces import AgentResult, FinalAnswer, AgentIntent

class HelloWorldAgent:
    def run(self, task_data):
        """
        Simple implementation that returns a hard-coded result.
        """
        intent = FinalAnswer(content="Hello World!")
        output = AgentIntent(thought="This is a simple Hello World agent.", intent=intent)
        return AgentResult(status="SUCCESS", output=output)
```

## 4. M2 Implementation Details

### 4.0. The BaseAgent SDK

The core of the M2 phase is delivering a fully-featured `BaseAgent` base class. This class is the **Software Development Kit (SDK)** for all custom Agent developers. It encapsulates all the complexity of interacting with the system (such as handling re-entry, requesting LLM/Tool calls, and creating standard intent formats), allowing Agent developers to focus purely on business logic.

### 4.1. Enhanced Agent Support

In M2, the Agent Service must support more complex Agents that interact with LLMs and Tools:

1. **LLM Integration**:
   - Must support Agents that request LLM calls through the `System.LLM.invoke` ToolCallRequest
   - Must handle re-entry logic for Agents that process LLM responses

2. **Tool Integration**:
   - Must support Agents that request Tool calls
   - Must handle re-entry logic for Agents that process Tool responses

3. **Base Agent Class**:
   - Must provide helper methods for common Agent operations:
     - `request_llm_call(prompt)`: Returns a ToolCallRequest intent for LLM invocation
     - `get_last_llm_response()`: Retrieves the last LLM response for processing
     - `get_last_tool_response()`: Retrieves the last Tool response for processing
     - `create_final_answer(thought, content)`: Creates a properly formatted FinalAnswer intent
     - `create_tool_call_request(tool_id, arguments)`: Creates a ToolCallRequest intent

### 4.2. Generic Worker Agent Implementation

The Agent Service must fully support the GenericWorkerAgent template:

1. **Prompt Construction**:
   - Must be able to build prompts from `prompt_template` and `input_data` in the JSON configuration
   - Must support variable substitution in prompt templates

2. **Execution Flow**:
   - On first execution, constructs the prompt and returns a ToolCallRequest for `System.LLM.invoke`
   - On re-entry, processes the LLM response and returns a FinalAnswer

### 4.3. Custom Agent Support

The Agent Service must support custom Agent implementations:

1. **Inheritance Model**:
   - Custom Agents must inherit from the BaseAgent class
   - Must implement the `run()` method that returns an `AgentResult`

2. **Re-entry Handling**:
   - Must support Agents that need to process LLM or Tool responses
   - Must provide mechanisms to determine if this is the first execution or a re-entry

## 5. M3 Implementation Details

### 5.1. Planner Support

In M3, the Agent Service must support Planner Agents:

1. **Plan Generation**:
   - Must support Agents that return `PlanBlueprint` intents
   - Must validate that only Agents with `role: PLANNER` return PlanBlueprint intents

2. **Context Integration**:
   - `AgentService` will first check the `context_config` defined for the Agent in `capabilities.json` before executing any Agent (whether Planner or Worker). Then, it will call the `ContextService` to pre-build the context. **This context will be part of the `task_data` and passed to the Agent during instantiation.** The Agent script itself does not need to directly call the `ContextService`.

### 5.2. Advanced Features

1. **Prompt Fusion**:
   - Must implement the prompt fusion lifecycle as defined in the specification
   - Must support different fusion strategies (PREPEND_BASE, etc.)

2. **Error Handling**:
   - Must properly handle and report Agent execution failures
   - Must convert exceptions into properly formatted `AgentResult` objects with FAILURE status

## 6. Dependencies

- Python 3.11+
- `interfaces` module
- `LoggingService` module
- `CapabilityInitializer` module (for accessing capability registry)
- `ContextService` module (M2+)
- `LLMService` module (indirectly through Tool calls, M2+)

## 7. Testing

The Agent Service should be tested with:

1. **Unit Tests**:
   - Agent loading and instantiation
   - Result validation
   - Generic Worker Agent execution
   - Custom Agent execution

2. **Integration Tests**:
   - End-to-end Agent execution with the Central Graph Engine
   - LLM interaction flows (M2+)
   - Tool interaction flows (M2+)
   - Planner execution flows (M3+)

3. **M1 Acceptance Criteria**:
   - Can successfully load and execute a HelloWorldAgent
   - Correctly returns an AgentResult with FinalAnswer intent
   - Properly integrates with tracing and logging systems

## 8. Future Development

### Enhanced Error Handling
- Implement retry mechanisms for transient failures
- Add circuit breaker patterns for external service calls
- Enhance error reporting and monitoring

### Performance Optimizations
- Implement Agent instance caching
- Add support for concurrent Agent execution
- Optimize prompt construction and validation

### Security Enhancements
- Implement sandboxing for Agent execution
- Add input validation and sanitization
- Implement access control for Agent capabilities