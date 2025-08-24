# Agent Service Development Documentation

## **模块概述**

Agent服务 (Agent Service) 是Synapse平台负责实例化和执行Agent脚本的核心组件。它作为所有Agent逻辑的执行环境，根据能力定义（`capabilities.json`），动态地加载和运行Agent的实现。

## **1. 目的与职责**

Agent服务是Synapse平台中所有Agent的“**执行运行时 (Execution Runtime)**”。其主要职责包括：

1.  **动态Agent加载**: 根据`capabilities.json`中定义的`implementation_path`加载Agent实现。
2.  **上下文构建**: 在执行Agent前，调用内部的`ContextBuilder`，为Agent准备好所有必需的上下文和提示词。
3.  **Agent执行**: 根据Agent的类型（通用或自定义）运行Agent脚本。
4.  **结果标准化**: 确保所有Agent的输出都严格遵循`AgentResult`规范。
5.  **追踪与日志**: 为每一次Agent执行提供分布式的追踪和结构化日志。

## **2. 架构**

Agent服务遵循一个模块化的架构，以支持各种Agent类型的动态加载和执行：

1.  **Agent工厂 (Agent Factory)**: 负责根据能力定义创建Agent实例。
2.  **上下文构建器 (Context Builder)**: **【核心组件】** 负责实现完整的上下文构建生命周期。它解析Agent的`context_config`，按需从`PersistenceService`等底层服务拉取数据，执行提示词融合，并注入全局约束。
3.  **Agent执行器 (Agent Executor)**: 负责执行Agent的`.run()`方法，使用由`ContextBuilder`提供的上下文。
4.  **BaseAgent基类 (SDK核心)**: 为所有Agent类型提供通用的功能和接口。
5.  **通用Agent实现**: 预置的、由配置驱动的Agent模板（如`GenericWorkerAgent`）。
6.  **结果校验器 (Result Validator)**: 确保所有输出都符合`AgentResult`规范。

**重要边界**: `AgentService`**只负责执行单个Agent的`.run()`方法并返回其意图**。它**不关心**任何工作流逻辑，例如Agent执行完后下一步该去哪里（由`图引擎`的`Edge`决定），或Agent是如何被调用的（可能是线性任务或并行循环的一部分）。这种严格的职责分离，确保了`AgentService`是一个纯粹的、可复用的“**Agent执行运行时**”。
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

## **4. M2实现细节**

#### **4.0. BaseAgent SDK**
M2阶段的核心，是交付一个功能完备的`BaseAgent`基类。这个类是所有自定义Agent开发者的**软件开发工具包（SDK）**。它封装了所有与系统交互的复杂性（如处理重入、请求LLM/Tool、创建标准意图格式），让Agent开发者可以专注于业务逻辑本身。

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

## **5. M3实现细节**

### **5.1. Planner支持**

1.  **规划生成**:
    *   必须支持返回`PlanBlueprint`意图的Agent。
    *   必须校验只有`role: PLANNER`的Agent才能返回`PlanBlueprint`意图。

2.  **上下文集成**:
    *   在执行任何Agent（无论是Planner还是Worker）**之前**，`AgentService`会首先检查其在`capabilities.json`中定义的`context_config`。然后，它会调用内部的`ContextBuilder`来预构建上下文。**这个上下文将作为`task_data`的一部分，在Agent实例化时被传递。** Agent脚本本身不需要直接调用上下文服务。

### **5.2. 高级特性**

1.  **提示词融合**:
    *   必须实现`capabilities.json`中定义的`prompt_fusion_strategy`生命周期。
    *   必须支持不同的融合策略（`PREPEND_BASE`等）。

2.  **错误处理**:
    *   必须能正确处理和报告Agent执行失败。
    *   必须能将执行过程中捕获的异常，转换为符合`AgentResult`规范的、包含`failure_details`的`FAILURE`状态对象。

## **6. 依赖**

*   Python 3.11+
*   `interfaces` 模块
*   `LoggingService` 模块
*   `CapabilityInitializer` 模块 (用于访问能力注册表)
*   **`PersistenceService` 和其他底层服务** (由内部的`ContextBuilder`调用)
*   `LLMService` (间接通过返回`System.LLM.invoke`意图来交互)

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

