

## **组件需求规格说明书：`interfaces模块` - 核心数据契约**

**文档版本**: 1.0
**目的**: 本文档定义了“Synapse”平台中，所有跨模块通信的核心数据结构的Schema。所有服务和模块都**必须**依赖此文件来定义其API的输入和输出，以保证整个系统的类型安全和数据一致性。

### **1. 技术需求 (Technical Requirements)**

*   **TR-1 (技术选型)**: 必须使用 **`Pydantic` v2** 作为定义数据模型的唯一技术。
*   **TR-2 (严格性)**: 所有模型默认应配置为`extra='forbid'`，禁止传入未在模型中定义的额外字段，以保证契约的严格性。
*   **TR-3 (命名规范)**:
    *   模型名称必须使用大驼峰命名法（`PascalCase`）。
    *   字段名称必须使用蛇形命名法（`snake_case`）。
*   **TR-4 (文档化)**: 所有模型和关键字段都**必须**包含清晰的`description`，以便自动生成API文档。
*   **TR-5 (可扩展性)**: 设计应考虑到未来的扩展性，优先使用`Union`和嵌套模型来表达可变性，而不是创建大量相似的模型。
*   **TR-6 (依赖性)**: 此文件应为**纯粹的定义文件**，**严禁**包含任何业务逻辑、函数实现或对其他模块的`import`（除了Python标准类型和Pydantic本身）。

---

### **2. 业务需求：模型定义 (Business Requirements: Model Definitions)**

#### **2.1. 工作流蓝图 (`PlanBlueprint`)**
*   **用途**: 用于由`Planner`或人类用户，声明式地创建或扩展工作流。
*   **BR-PB-01 (`PlanBlueprint`)**:
    *   `workflow_id: Optional[UUID]`
    *   `new_tasks: List[TaskDefinition]`
    *   `new_edges: List[EdgeDefinition]`
    *   `update_tasks: List[TaskUpdate]`
*   **BR-PB-02 (`TaskDefinition`)**:
    *   `task_id: str` (蓝图内的临时ID)
    *   `parent_task_id: Optional[str]`
    *   `input_data: Dict[str, Any]` (取代单一`goal`)
    *   `assignee_id: str` (格式: `Group:id` or `Agent:id`)
    *   `context_overrides: Optional[ContextOverrides]`
    *   `directives: Optional[TaskDirectives]`
*   **BR-PB-03 (`EdgeDefinition`)**:
    *   `source_task_id: str`
    *   `target_task_id: str`
    *   `condition: Optional[Condition]`
    *   `data_flow: Optional[DataFlow]`

#### **2.2. Agent交互 (`AgentResult`)**
*   **用途**: 作为所有`Agent`执行后返回的**唯一**标准化输出。
*   **BR-AR-01 (`AgentResult`)**:
    *   `status: Literal['SUCCESS', 'FAILURE']`
    *   `output: AgentIntent`
    *   `failure_details: Optional[FailureDetails]`
    *   `metadata: Optional[Dict[str, Any]]`
*   **BR-AR-02 (`AgentIntent`)**:
    *   `thought: str`
    *   `intent: Union[FinalAnswer, ToolCallRequest, PlanBlueprint]`
*   **BR-AR-03 (`FinalAnswer`)**:
    *   `content: Any` (可以是字符串、JSON对象等)
*   **BR-AR-04 (`ToolCallRequest`)**:
    *   `tool_id: str`
    *   `arguments: Dict[str, Any]`
*   **BR-AR-05 (`FailureDetails`)**:
    *   `type: Literal['LLM_REFUSAL', 'TOOL_EXECUTION_FAILED', ...]`
    *   `message: str`

#### **2.3. 上下文构建 (`ContextBuildConfig`)**
*   **用途**: 用于`Agent`向`ContextService`声明其需要的上下文类型。
*   **BR-CB-01 (`ContextBuildConfig`)**:
    *   `task_id: UUID` (必需，指明为哪个任务构建上下文)
    *   `include_metadata: bool`
    *   `include_tool_list: bool`
    *   `conversation_history_config: Optional[Dict]` (e.g., `{"last_n": 5}`)
    *   `task_list_config: Optional[Dict]` (e.g., `{"status_in": ["COMPLETED"]}`)
    *   `artifact_config: Optional[Dict]` (e.g., `{"asset_id": "...", "mode": "SUMMARY"}`)
    *   `experience_config: Optional[Dict]` (e.g., `{"query": "...", "top_k": 3}`)

#### **2.4. 任务指令 (`TaskDirectives` & `Condition`)**
*   **用途**: 存储在`tasks.directives`字段中，指导`图引擎`的执行行为。
*   **BR-TD-01 (`TaskDirectives`)**:
    *   `loop_directive: Optional[LoopDirective]`
    *   `on_failure: Optional[Dict]` (e.g., `{"type": "GOTO", "target_task_id": "..."}`)
    *   `timeout_seconds: Optional[int]`
    *   `human_interaction: Optional[Dict]`
*   **BR-TD-02 (`LoopDirective`)**:
    *   `type: Literal['PARALLEL_ITERATION', 'SERIAL_ITERATION']`
    *   `iteration_input_key: str`
    *   `input_source_task_id: str`
    *   `task_template: TaskDefinition`
    *   `max_iterations: Optional[int]`
*   **BR-TD-03 (`Condition`)**:
    *   `evaluator: Literal['CEL']`
    *   `expression: str`

#### **2.5. 人工干预 (`InterventionRequest`)**
*   **用途**: 定义外部用户干预工作流的API请求体。
*   **BR-IR-01 (`InterventionRequest`)**:
    *   `intervention_type: Literal['ROLLBACK_AND_MODIFY', 'PAUSE', 'RESUME']`
    *   `target_task_id: UUID`
    *   `rollback_to_version: Optional[int]`
    *   `new_input_data: Optional[Dict[str, Any]]`
    *   `new_assignee_id: Optional[str]`
    *   `comment: str`

---

### **`interfaces.py` 完整示例代码**

```python
# interfaces.py
from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from uuid import UUID

# --- FORWARD DECLARATIONS ---
# Pydantic v2 supports string forward references for self-referencing models
TaskDefinition = "TaskDefinition"

# --- 2.4. TASK DIRECTIVES ---
class Condition(BaseModel):
    evaluator: Literal['CEL']
    expression: str

class LoopDirective(BaseModel):
    type: Literal['PARALLEL_ITERATION', 'SERIAL_ITERATION']
    iteration_input_key: str
    input_source_task_id: str
    task_template: TaskDefinition
    max_iterations: Optional[int] = None

class TaskDirectives(BaseModel):
    loop_directive: Optional[LoopDirective] = None
    on_failure: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[int] = None
    human_interaction: Optional[Dict[str, Any]] = None

# --- 2.1. PLAN BLUEPRINT ---
class DataFlow(BaseModel):
    mappings: Dict[str, str]

class ContextOverrides(BaseModel):
    priority: Literal['NORMAL', 'HIGHEST'] = 'NORMAL'
    include_assets: Optional[List[Dict[str, Any]]] = None
    include_task_results: Optional[List[str]] = None
    ad_hoc_text: Optional[str] = None
    override_context_config: Optional[Dict[str, Any]] = None

class TaskDefinition(BaseModel):
    task_id: str
    parent_task_id: Optional[str] = None
    input_data: Dict[str, Any]
    assignee_id: str
    context_overrides: Optional[ContextOverrides] = None
    directives: Optional[TaskDirectives] = None

class EdgeDefinition(BaseModel):
    source_task_id: str
    target_task_id: str
    condition: Optional[Condition] = None
    data_flow: Optional[DataFlow] = None

class TaskUpdate(BaseModel):
    task_id: UUID
    new_input_data: Optional[Dict[str, Any]] = None
    new_status: Optional[str] = None

class PlanBlueprint(BaseModel):
    workflow_id: Optional[UUID] = None
    new_tasks: List[TaskDefinition] = []
    new_edges: List[EdgeDefinition] = []
    update_tasks: List[TaskUpdate] = []

# --- 2.2. AGENT RESULT ---
class FinalAnswer(BaseModel):
    content: Any

class ToolCallRequest(BaseModel):
    tool_id: str
    arguments: Dict[str, Any]

class AgentIntent(BaseModel):
    thought: str
    intent: Union[FinalAnswer, ToolCallRequest, PlanBlueprint]

class FailureDetails(BaseModel):
    type: Literal['LLM_REFUSAL', 'TOOL_EXECUTION_FAILED', 'VALIDATION_ERROR', 'RESOURCE_UNAVAILABLE']
    message: str

class AgentResult(BaseModel):
    status: Literal['SUCCESS', 'FAILURE']
    output: AgentIntent
    failure_details: Optional[FailureDetails] = None
    metadata: Optional[Dict[str, Any]] = None

# --- 2.3. CONTEXT BUILD CONFIG ---
class ContextBuildConfig(BaseModel):
    task_id: UUID
    include_metadata: bool = True
    include_tool_list: bool = True
    conversation_history_config: Optional[Dict[str, Any]] = None
    task_list_config: Optional[Dict[str, Any]] = None
    artifact_config: Optional[Dict[str, Any]] = None
    experience_config: Optional[Dict[str, Any]] = None

# --- 2.5. HUMAN INTERVENTION ---
class InterventionRequest(BaseModel):
    intervention_type: Literal['ROLLBACK_AND_MODIFY', 'PAUSE', 'RESUME']
    target_task_id: UUID
    rollback_to_version: Optional[int] = None
    new_input_data: Optional[Dict[str, Any]] = None
    new_assignee_id: Optional[str] = None
    comment: str

# Pydantic v2 needs this for self-referencing models
TaskDefinition.model_rebuild()
LoopDirective.model_rebuild()
```

这份详尽的`interfaces.py`需求文档，为您的整个分布式系统建立了一套坚实、可靠、类型安全的“**通用语言**”，是实现所有模块高效、无歧义协作的绝对前提。