

## **Agent脚本开发 产品与开发文档 (SDK Guide)**

**文档版本**: 1.0
**模块负责人**: SDK与框架团队

### **1. 产品概述 (Product Overview)**

#### **1.1. Agent的职责与哲学**
在Synapse平台中，`Agent`是**任务的核心执行者**和**智能决策单元**。每一个Agent脚本都应被视为一个**无状态的、可复用的、职责单一**的专家。

本SDK（以`BaseAgent`为核心）旨在赋能开发者，使其能够轻松地创建功能强大、且严格遵循平台架构约束的Agent。

#### **1.2. 核心开发原则**
*   **继承优于从零实现**: 所有Agent都**必须**继承自`BaseAgent`。
*   **意图驱动通信**: Agent与系统的唯一交互方式，是返回一个符合`AgentResult`规范的**声明式意图**。
*   **无副作用**: Agent脚本**严禁**直接执行I/O操作、API调用（LLM除外，且必须通过意图）或修改外部状态。所有行动都必须通过请求调用`Tool`来完成。
*   **配置与代码分离**: 静态配置（`base_prompt`等）应在`capabilities.json`中定义，动态逻辑则在Python脚本中实现。

---

### **2. `BaseAgent` SDK 详解**

`BaseAgent` (`system/agents/base_agent.py`) 是所有Agent开发的基石。它提供了以下属性和方法：

#### **2.1. 核心属性 (Available in `self`)**
*   `self.agent_config: Dict`: 当前Agent在`capabilities.json`中的完整JSON配置对象。
*   `self.task_data: Dict`: 当前正在执行的任务的完整数据库记录，包含`task_id`, `input_data`, `context`等。
*   `self.group_config: Optional[Dict]`: 如果Agent是Planner，这里会包含其所属Group的JSON配置。
*   `self.logger: logging.Logger`: 一个已经配置好的、会自动注入`trace_id`和`span_id`的结构化日志记录器。

#### **2.2. 核心执行流程方法 (`.run()`) - (子类不应重写)**
这是由`图引擎`调用的入口。`BaseAgent`中的`run()`方法实现了一个标准的**模板方法模式**，其逻辑如下：
```python
def run(self) -> Dict:
    self.logger.info("Agent execution started.")
    try:
        # 判断是首次运行，还是处理LLM/Tool的返回
        if self.is_first_run():
            # 首次运行，构建提示词并请求LLM
            final_prompt = self._build_final_prompt()
            result = self.request_llm_call(final_prompt)
        else:
            # 处理重入，将LLM或Tool的返回结果分发
            result = self._handle_reentry()
        
        self.logger.info("Agent execution finished successfully.")
        return result

    except Exception as e:
        self.logger.error("Agent execution failed.", exc_info=True)
        return self.create_failure_response(type="AGENT_EXECUTION_ERROR", message=str(e))
```

#### **2.3. 需要子类实现的抽象方法 (Abstract Methods for Override)**
*   **`_generate_dynamic_prompt(self) -> str`**:
    *   **职责**: **【开发者核心实现】** 生成此Agent独特的、与当前任务相关的**动态提示词部分**。
    *   **返回值**: 一个字符串。
*   **`_handle_llm_response(self, llm_response: Dict) -> Dict`**:
    *   **职责**: **【开发者核心实现】** 在`request_llm_call`返回结果后被调用。负责解析LLM的输出，并决定下一步的**最终意图**（是`FinalAnswer`，还是`ToolCallRequest`，还是`PlanBlueprint`）。
    *   **返回值**: 一个完整的`AgentResult`字典。

#### **2.4. 辅助/SDK方法 (Helper Methods for Use)**
*   `self._build_final_prompt() -> str`: 自动处理`base_prompt`和动态部分的融合。
*   `self.is_first_run() -> bool`: 判断是否是首次执行。
*   `self.get_last_llm_response() -> Optional[Dict]`: 获取上一步LLM调用的结果。
*   `self.get_last_tool_result() -> Optional[Dict]`: 获取上一步工具调用的结果。
*   `self.request_llm_call(prompt: str, ...) -> Dict`: 构建一个请求调用`System.LLM.invoke`的`AgentResult`。
*   `self.request_tool_call(thought: str, tool_id: str, arguments: Dict) -> Dict`: 构建一个`ToolCallRequest`意图。
*   `self.create_final_answer(thought: str, content: Any) -> Dict`: 构建一个`FinalAnswer`意图。
*   `self.create_plan_intent(thought: str, plan_blueprint: PlanBlueprint) -> Dict`: (Planner专用) 构建一个`PlanBlueprint`意图。
*   `self.create_failure_response(...) -> Dict`: 构建一个标准的失败`AgentResult`。

---

### **3. 开发任务分解 (Development Tasks)**

#### **3.1. M1: 框架与通用Agent开发**
*   **任务1: 实现`BaseAgent`基类**
    *   **开发者**: 框架团队。
    *   **需求**: 实现`BaseAgent`的所有核心属性和方法，包括`run()`的模板逻辑、提示词融合、重入判断和所有SDK辅助方法。将`_generate_dynamic_prompt`和`_handle_llm_response`定义为抽象方法。
*   **任务2: 实现`GenericWorkerAgent`**
    *   **开发者**: 框架团队。
    *   **需求**:
        *   创建一个`GenericWorkerAgent(BaseAgent)`类。
        *   实现`_generate_dynamic_prompt`，其逻辑是简单地渲染来自`Group`或`Agent`配置中的`prompt_template`。
        *   实现`_handle_llm_response`，其逻辑是根据配置的`output_mode`来处理LLM的返回。如果`mode`是`DIRECTIVE_TEXT_TO_INTENT`，它会请求调用相应的`Formatter`工具；如果是`SIMPLE_TEXT_TO_INTENT`，它会直接将结果包装成`FinalAnswer`。
*   **任务3: 实现`GenericPlannerAgent`**
    *   **开发者**: 框架团队。
    *   **需求**:
        *   创建一个`GenericPlannerAgent(BaseAgent)`类。
        *   其`_generate_dynamic_prompt`会使用`group_config`中的`planner_prompt_template`。
        *   其`_handle_llm_response`的默认实现，是尝试将LLM的输出解析和验证为一个`PlanBlueprint`。

#### **3.2. M2: 业务Agent开发**
*   **任务4: 开发自定义`Worker Agent` (e.g., `TerraformAgent`)**
    *   **开发者**: 业务团队。
    *   **需求**:
        1.  在`custom_agents/`目录下，创建一个`terraform_agent.py`文件。
        2.  定义`class TerraformAgent(BaseAgent)`。
        3.  在`capabilities.json`中为其注册，并配置好`implementation_path`, `base_prompt`等。
        4.  实现`_generate_dynamic_prompt`方法，用于构建与Terraform相关的动态提示。
        5.  实现`_handle_llm_response`方法，用于处理LLM返回的Terraform代码，并**返回一个调用`NativeTools.terraform.validate`工具的`ToolCallRequest`意图**。
        6.  在`run`方法中，增加对`get_last_tool_result`的处理逻辑：当收到`validate`工具的结果后，再决定是返回`FinalAnswer`还是启动返工。
*   **任务5: 开发自定义`Planner` (e.g., `DevOpsPlanner`)**
    *   **开发者**: 业务团队。
    *   **需求**:
        1.  在`custom_planners/`目录下，创建一个`devops_planner.py`文件。
        2.  定义`class DevOpsPlanner(BaseAgent)`。
        3.  在`capabilities.json`中为一个`Group`配置`planner_implementation_path`指向此类。
        4.  实现`run`方法，其中可能包含直接调用外部系统SDK（如Jira, Gitlab）的**确定性逻辑**，并结合`request_llm_call`来进行最终的规划，最后返回一个`PlanBlueprint`。

---

### **4. 验收标准**
*   **M1**: `GenericWorkerAgent`和`GenericPlannerAgent`能够被`图引擎`成功加载和运行。
*   **M2**: 业务开发者能够通过继承`BaseAgent`，轻松地实现具有复杂内部逻辑（多步思考、工具调用、返工）的自定义Agent。
*   **通用**: 所有Agent的执行，都必须能在`日志与追踪服务`中看到清晰的、包含`trace_id`和`span_id`的日志流。

这份详尽的PRD，为您的Agent开发团队提供了从框架（`BaseAgent`）到实现（`Generic`/`Custom` Agent）的完整路线图和开发规范，确保了所有被创造出的“智能体”，都能在您设计的这个宇宙中，和谐、高效、可靠地运行。