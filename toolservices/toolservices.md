
## **原生工具服务 (Native Tools Service) 产品与开发文档**

**文档版本**: 1.0
**模块负责人**: [待定]

### **1. 产品概述 (Product Overview)**

#### **1.1. 职责 (Responsibility)**
原生工具服务 (以下简称`ToolService`) 是Synapse平台执行所有**非LLM的、与外部世界交互的具体动作**的**唯一、安全的**执行环境。它负责动态加载、沙箱化执行并监控`Tool`脚本，确保Agent的“行动意图”能够被可靠地转化为现实世界中的操作。

#### **1.2. 核心价值 (Core Value Proposition)**
*   **安全 (Security)**: 通过**安全沙箱**机制，将不可信的`Tool`代码（尤其是执行代码的`Tool`）与系统核心隔离开来，防止恶意操作和资源滥用。
*   **解耦 (Decoupling)**: 将工具的**执行逻辑**与`图引擎`的**调度逻辑**完全分离。
*   **可扩展性 (Extensibility)**: 提供一个简单的“插件式”框架，让开发者可以轻松地创建和注册新的`Tool`，来无限扩展平台的能力。
*   **可靠性 (Reliability)**: 对`Tool`的执行进行统一的输入校验、错误捕获和超时控制。

### **2. 开发计划 (Development Plan)**

我们将分三个阶段来构建一个企业级的、安全可靠的`ToolService`。

#### **2.1. 阶段一：核心执行与动态加载 (Milestone 1 - MVP)**
**目标**: 实现一个能动态加载并直接执行受信任`Tool`脚本的核心执行器。

*   **FR-TLS-01: 动态加载与执行**
    *   **FR-TLS-01a**: `ToolService`必须提供一个核心方法`run_tool(tool_call_request: ToolCallRequest) -> ToolResult`。
    *   **FR-TLS-01b**: 该方法必须能根据`tool_call_request.tool_id`，从`能力注册表`中查找对应的`implementation_path`。
    *   **FR-TLS-01c**: 必须使用`importlib`，**动态地**加载并获取`Tool`脚本中的`run`函数。
*   **FR-TLS-02: 输入参数校验**
    *   在调用`Tool`的`run`函数**之前**，`ToolService`必须根据`capabilities.json`中为该`Tool`定义的`parameters_schema`，对`tool_call_request.arguments`进行严格的**JSON Schema校验**。
    *   如果校验失败，必须立即返回一个包含详细校验错误的`FAILURE`结果，**不执行**`Tool`代码。
*   **FR-TLS-03: 统一的结果与错误封装**
    *   `run_tool`方法**必须**捕获`Tool`脚本执行过程中抛出的任何异常。
    *   如果`Tool`成功执行并返回，其返回值必须被包装在一个标准的成功`ToolResult`中，例如`{"status": "SUCCESS", "output": tool_return_value}`。
    *   如果`Tool`执行时发生异常，该异常必须被捕获，并包装在一个标准的失败`ToolResult`中，例如`{"status": "FAILURE", "error_type": "TOOL_EXECUTION_ERROR", "error_message": str(e)}`。
*   **FR-TLS-04: 追踪与日志**
    *   每一次`run_tool`的执行，都**必须**在一个独立的、名为`tool_execution:{tool_id}`的**追踪`Span`**中进行。

#### **2.2. 阶段二：安全与资源控制 (Milestone 2 - Security Hardening)**
**目标**: 引入安全沙箱和超时控制，使服务能够安全地执行潜在的危险代码。

*   **FR-TLS-05: 安全沙箱 (核心)**
    *   **FR-TLS-05a**: 对于在`capabilities.json`中被标记为`"requires_sandbox": true`的`Tool`（特别是执行代码、文件系统操作的），`ToolService`**必须**在一个**隔离的环境**中执行它们。
    *   **FR-TLS-05b**: 首选的沙箱技术是**Docker容器**。`ToolService`会为每一次调用，启动一个临时的、网络访问受限的、文件系统被映射的Docker容器来执行`Tool`代码。
    *   **FR-TLS-05c**: 需要实现一个Docker容器的池化管理机制，以减少重复创建容器的开销。
*   **FR-TLS-06: 超时控制**
    *   `ToolService`必须支持在`capabilities.json`的`Tool`定义中，配置一个可选的`timeout_seconds`参数。
    *   在执行`Tool`时，`ToolService`必须强制执行这个超时限制。如果超时，必须安全地终止`Tool`的执行（例如，停止Docker容器），并返回一个`FAILURE`结果，`error_type`为`"TOOL_TIMEOUT_ERROR"`。

#### **2.3. 阶段三：高级特性 (Milestone 3 - Advanced Features)**
**目标**: 提升服务的可维护性和智能。

*   **FR-TLS-07: Tool返回`PlanBlueprint`**
    *   `ToolService`在接收到`Tool`的返回结果后，需要检查其中是否包含一个可选的`post_execution_plan`字段。
    *   如果存在，`ToolService`**不执行**这个计划，而是将其原封不动地包含在`ToolResult`中，交由上游的`中央图引擎`来决定如何处理。
*   **FR-TLS-08: 依赖管理**
    *   为需要特殊Python库（如`pandas`, `tensorflow`）的`Tool`，提供一个**依赖声明机制**。
    *   在执行`Tool`时，`ToolService`（或其Docker沙箱）能确保这些依赖已经被安装。

### **3. 数据库与配置依赖**

*   `ToolService`**不直接**与`PostgreSQL`交互。
*   它严重依赖于由`能力初始化服务`在启动时加载并提供的**能力注册表**，以获取`Tool`的`implementation_path`和`parameters_schema`等元数据。

### **4. 模块结构 (Module Structure)**

```
ToolService/
├── __init__.py
├── main.py                 # API服务器入口 (如果作为独立微服务)
├── service.py              # 核心服务接口 (run_tool)
├── core/
│   ├── executor.py         # 核心执行逻辑
│   ├── loader.py           # 动态代码加载器
│   ├── validator.py        # 输入参数校验器
│   └── sandbox/            # 【M2】安全沙箱实现
│       ├── __init__.py
│       ├── base_sandbox.py
│       └── docker_sandbox.py
├── tests/
│   ├── __init__.py
│   └── test_executor.py
└── README.md
```

### **5. API 接口示例 (Internal API)**

`ToolService`主要被`中央图引擎`在内部调用。

```python
# service.py
from interfaces import ToolCallRequest, ToolResult

class ToolService:
    def run_tool(self, tool_call_request: ToolCallRequest) -> ToolResult:
        """
        根据ToolCallRequest，动态加载、校验并沙箱化执行一个Tool。
        
        这是一个同步或异步的方法，它会等待Tool执行完成。
        """
        # 1. 从能力注册表获取Tool的定义
        # 2. 调用validator.py对arguments进行校验
        # 3. 根据Tool定义，选择执行器（直接执行或沙箱执行）
        # 4. 调用executor.py执行
        # 5. 捕获结果或异常，封装成ToolResult并返回
        pass
```

### **6. 测试策略 (Testing Strategy)**

*   **单元测试**: 对`loader`, `validator`进行严格的单元测试。
*   **集成测试**:
    *   编写多个模拟的`Tool`脚本（成功的、失败的、超时的、返回`post_execution_plan`的）。
    *   编写测试用例，通过`run_tool`方法调用这些模拟`Tool`，并验证`ToolService`返回的`ToolResult`是否完全符合预期。
    *   **【M2】** 必须编写专门的测试用例，来验证沙箱的隔离性是否生效（例如，一个`Tool`试图访问沙箱外的文件，应该被阻止并报错）。

这份详尽的PRD，为您构建一个**安全、可靠、可扩展**的`原生工具服务`提供了清晰的路线图。它确保了您平台的所有“行动”都在一个受控、可观测的环境中进行，这是企业级智能体系统不可或缺的安全基石。