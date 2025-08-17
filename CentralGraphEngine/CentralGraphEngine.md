# Central Graph Engine Development Documentation

## Module Overview

The Central Graph Engine is the core orchestrator of the Synapse platform. It consumes tasks from a queue, executes them by coordinating with other services, and manages the flow of a workflow based on the directives and intents returned.

This document provides a comprehensive guide to developing and extending the Central Graph Engine.

## **2. 架构 (Architecture)**

引擎遵循一个模块化的、**事件驱动的**架构，其核心职责是响应来自任务队列的事件。

1.  **事件消费者 (`Event Consumer`)**: 引擎的入口点。它**不轮询**数据库，而是**阻塞式地**从Redis任务队列中获取任务ID。
2.  **任务处理器 (`Task Processor`)**: 系统的核心状态机。在接收到一个任务ID后，它负责加载任务状态，并根据任务的类型和指令，协调其他服务来执行它。
3.  **服务集成 (`Service Integrations`)**: 通过`interfaces.py`中定义的契约，与`PersistenceService`, `AgentService`, `ToolService`等进行交互。
4.  **指令处理器 (`Directive Processor`)**: (M2+) 负责解析和执行任务中的`directives`，如循环和并行模式。
5.  **意图处理器 (`Intent Processor`)**: 负责解析Agent返回的`AgentIntent`，并决定下一步的微观操作（调用工具、结束任务等）。
6.  **条件评估器 (`Condition Evaluator`)**: (M2+) 负责调用CEL Evaluator来评估`Edge`的条件，以决定工作流的宏观走向。

## **3. M1实现细节 (M1 Implementation Details)**

### **3.1. 事件驱动机制 (Event-Driven Mechanism)**

在M1阶段，引擎**必须**实现事件驱动的核心。**轮询机制不被采用。**

*   **任务队列**: 引擎将使用**Redis的`BRPOP`命令**，阻塞式地、高效地从一个预定义的任务列表（如`'task_execution_queue'`）中等待并获取新的任务ID。
*   **上游连接**: 引擎本身**不直接**监听PostgreSQL。它依赖于独立的`Notify Handler`模块，该模块负责`LISTEN`数据库的`NOTIFY`事件，并将任务ID推入Redis队列。
*   **入口循环**: 引擎的`main_loop`不再是`while True: sleep(1)`，而是一个`while True: task_id = redis.brpop('task_queue')`的阻塞循环。

### **3.2. 任务处理流程 (Task Processing Flow)**

1.  **从Redis队列获取一个`task_id`**。
2.  **启动追踪**: 为这个`task_id`的处理过程，启动一个新的`Span`，并恢复从消息中传递过来的`trace_id`。
3.  **获取任务并加锁**:
    *   调用`PersistenceService`的`get_task_and_lock(task_id)`方法。该方法内部使用`SELECT ... FOR UPDATE SKIP LOCKED`来原子性地获取任务数据并锁定该行，防止其他引擎实例重复处理。
    *   如果未能获取到锁（意味着任务已被其他实例处理），则直接放弃并返回等待下一个任务。
4.  **处理任务状态**:
    *   **如果任务状态为 `COMPLETED`**: 调用`handle_completed_task(task)`，该方法将负责查找和评估下游的`Edge`（M2功能）。
    *   **如果任务状态为 `PENDING`**:
        a.  检查`assignee_id`是否为`Agent`。
        b.  调用`AgentService`执行该Agent。
        c.  处理Agent返回的`AgentResult`:
            *   如果意图是`FinalAnswer`且状态`SUCCESS`：调用`PersistenceService`更新任务状态为`COMPLETED`并存入结果。
            *   如果意图是`ToolCallRequest`且状态`SUCCESS`：
                - 调用`ToolService.run_tool()`执行工具
                - 获取工具执行结果
                - 调用`PersistenceService.update_task_context()`更新任务的`context`字段（result列），将工具结果存入其中
                - **重要**: 不将任务标记为`COMPLETED`，保持`PENDING`状态
                - 数据库的`UPDATE`操作会自动触发`NOTIFY`，这将导致**同一个`task_id`**被再次放入任务队列，从而启动Agent的"重入"执行
            *   如果状态是`FAILURE`：更新任务状态为`FAILED`。
            *   **注意**: `UPDATE`操作会自动触发PostgreSQL的`NOTIFY`，从而自然地启动下游任务的处理流程。

## Future Development (M2, M3)

### Enhanced Task Processing

- Implement handling of `PlanBlueprint` intents
- Add support for task directives (loop, timeout, etc.)
- Implement condition evaluation for task edges
- Add complex workflow orchestration capabilities

### Error Handling and Retries

- Implement retry mechanisms for transient failures
- Add circuit breaker patterns for external service calls
- Enhance error reporting and monitoring

## Testing

The test plan is defined in `test.md` and includes test cases for:
- Processing tasks with FinalAnswer
- Handling agent failures
- Main loop behavior with no tasks
- Processing multiple tasks
- Error handling in the main loop
- Processing tasks with ToolCallRequest (M2 enhancement)

Run tests using the defined test cases and verify all scenarios.

## Dependencies

- Python 3.11+
- `interfaces` module
- `LoggingService` module
- `PersistenceService` module (mocked in M1)
- `AgentService` module (mocked in M1)
- `ToolService` module (mocked in M1)

## **7. 运行引擎**

要完整地运行M1的事件驱动系统，需要启动**两个**核心进程：

1.  **通知处理器 (Notify Handler)**:
    ```bash
    python notify_handler.py
    ```
2.  **中央图引擎 (Central Graph Engine)**:
    ```bash
    # 可以启动多个实例以测试负载均衡
    python engine.py
    ```

引擎启动后，将连接到Redis并阻塞等待任务，而`Notify Handler`则连接到PostgreSQL等待数据库事件。