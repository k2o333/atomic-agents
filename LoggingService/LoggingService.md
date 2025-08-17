# Logging & Tracing Service 产品与开发文档

## 1. 产品概述 (Product Overview)

### 1.1 职责 (Responsibility)
日志与追踪服务 (Logging & Tracing Service) 是 Synapse 平台提供**统一结构化日志**和**分布式追踪**能力的核心基础设施。它确保系统内所有模块的日志输出格式一致、内容结构化、并能通过 `trace_id` 和 `span_id` 进行关联和追溯。

### 1.2 核心需求 (Core Requirements)
根据《系统模块说明.md》(FR-LOG-xx)，本服务需满足以下核心需求：
*   **FR-LOG-01**: 提供一个配置化的、输出结构化JSON日志的统一接口。
*   **FR-LOG-02 (追踪体系)**: 实现一个基于`trace_id`（端到端流程）和`span_id`（单次操作）的二级追踪体系。
*   **FR-LOG-03 (上下文传播)**: 使用`ContextVar`等机制实现追踪上下文在异步任务中的自动传播。
*   **FR-LOG-04 (日志注入)**: 所有日志记录**必须**自动包含当前的`trace_id`和`span_id`。

## 2. 开发计划 (Development Plan)

遵循《建议开发顺序.md》中的 M1 阶段目标，我们将分阶段实现 Logging & Tracing Service。

### 2.1 阶段一：核心骨架 (Milestone 1 - MVP)
目标：实现最基本的功能，支持“Hello World”工作流。

#### 2.1.1 核心功能开发 (Core Functionality)
*   **JSON日志输出**:
    *   选型并集成 `python-json-logger` 库，实现将日志格式化为结构化的JSON。
    *   定义基础日志字段，确保包含时间戳、日志级别、消息、模块名等。
*   **基础追踪上下文 (`trace_id`, `span_id`)**:
    *   实现一个简单的追踪上下文管理器 (`TracerContextManager`)，用于生成和管理 `trace_id` 和 `span_id`。
    *   在服务启动、处理新请求或工作流时，创建新的 `trace_id`。
    *   在服务内部调用其他模块或执行子任务时，生成新的 `span_id` 并与父 `span_id` 关联。
*   **上下文传播 (`ContextVar`)**:
    *   使用 Python 的 `contextvars.ContextVar` 来存储当前的 `trace_id` 和 `span_id`。
    *   确保在异步函数 (`async/await`) 和线程池中，上下文能够正确传播。
*   **日志自动注入**:
    *   开发一个自定义的日志记录器 (`StructuredLogger`) 或日志过滤器 (`LogRecord` filter)。
    *   该记录器/过滤器在每次记录日志时，自动从 `ContextVar` 中获取当前的 `trace_id` 和 `span_id`，并将其作为字段注入到最终的JSON日志中。
*   **追踪上下文的序列化与反序列化 (Serialization & Deserialization)**:
    *   **SDK必须提供两个核心的辅助函数：`inject_trace_context() -> Dict` 和 `extract_trace_context(context_dict: Dict)`。**
    *   `inject_trace_context` 负责从当前的 `ContextVar` 中读取 `trace_id` 和 `span_id`，并将其打包成一个字典（遵循W3C Trace Context标准格式，如 `{'traceparent': '...'}`），以便可以被放入消息队列的payload或HTTP请求的header中。
    *   `extract_trace_context` 负责从接收到的字典中解析出 `trace_id` 和 `span_id`，并将其设置到当前进程的 `ContextVar` 中，从而实现追踪链路的跨服务延续。
*   **集成OpenTelemetry (可选)**:
    *   虽然M1阶段可以手动实现基础追踪，但应设计好与 OpenTelemetry (`opentelemetry-python`) 的集成点，为后续增强做准备。

#### 2.1.2 集成与使用
*   **提供SDK**:
    *   开发一个简单的SDK，暴露给其他模块使用。SDK应包含：
        *   `get_logger(name)`: 获取一个配置好的结构化日志记录器。
        *   `start_trace(name)`: 开始一个新的追踪（生成 `trace_id`）。
        *   `start_span(name)`: 在当前追踪下开始一个新的跨度（生成 `span_id`）。
        *   `inject_trace_context()`: 将当前追踪上下文序列化为字典。
        *   `extract_trace_context(context_dict)`: 从字典中提取追踪上下文并设置到当前上下文。
*   **核心模块集成**:
    *   在 `中央图引擎`、`Agent服务`、`数据库服务` 等核心模块中集成此SDK。
    *   在关键操作（如任务处理、数据库查询、Agent调用）前后，使用 `start_span` 包裹，并使用获取的 logger 记录带有 `trace_id` 和 `span_id` 的日志。
    *   当需要跨进程/服务调用时（例如，将任务ID放入Redis队列供`图引擎`消费），使用 `inject_trace_context` 将上下文信息附带在消息中。接收方在处理消息时，首先调用 `extract_trace_context` 来恢复上下文。

### 2.2 阶段二：功能增强 (Milestone 2 - Enhanced Features)
目标：引入更强大的追踪能力和分析工具。

#### 2.2.1 迁移到OpenTelemetry
*   **全面采用OpenTelemetry**:
    *   弃用手动实现的追踪上下文管理器。
    *   使用 `opentelemetry-python` SDK 来管理 `TracerProvider`, `Tracer`, `Span`。
    *   使用 OpenTelemetry 的 API 来创建 `Span` 并记录事件。
    *   `inject_trace_context` 和 `extract_trace_context` 的实现将委托给 OpenTelemetry 的 Propagator。
*   **Exporter集成**:
    *   集成 OpenTelemetry Exporter (如 OTLP, Jaeger, Zipkin)，将追踪数据发送到后端分析平台。
*   **自动Instrumentation**:
    *   探索并集成 OpenTelemetry 提供的库级自动Instrumentation（如对数据库驱动、HTTP客户端的自动追踪）。

### 2.3 阶段三：生产就绪 (Milestone 3 - Production Ready)
目标：提高性能、可靠性并支持高级分析。

#### 2.3.1 性能与可靠性
*   **异步日志处理**: 考虑使用异步日志处理器，避免日志I/O阻塞主业务逻辑。
*   **采样**: 配置合适的采样策略，避免在高负载下产生过多的日志和追踪数据。
*   **错误处理**: 确保日志和追踪服务本身具有健壮的错误处理机制，避免因服务内部错误影响主流程。

#### 2.3.2 高级分析
*   **度量 (Metrics)**: 集成 OpenTelemetry Metrics，收集和导出关键业务和技术指标。
*   **日志聚合**: 配置日志聚合工具（如 ELK Stack, Fluentd）来收集和分析 JSON 日志。

## 3. 技术选型 (Technology Stack)

*   **编程语言**: Python 3.11+
*   **日志库**: `python-json-logger`
*   **追踪库**: `opentelemetry-python` (从M2开始全面使用)
*   **上下文传播**: `contextvars` (Python标准库)
*   **(可选) 日志聚合**: ELK Stack, Fluentd
*   **(可选) 追踪后端**: Jaeger, Zipkin, Tempo

## 4. 模块结构 (Module Structure)

```
LoggingService/
├── __init__.py
├── config.py             # 日志和追踪配置
├── logger.py             # 结构化日志记录器封装
├── tracer.py             # 追踪上下文管理 (M1简化版ContextVar封装/M2+OpenTelemetry)
├── context.py            # ContextVar 管理 (可选，如果逻辑复杂可拆分)
├── sdk.py                # 对外提供的SDK接口
├── filters.py            # 日志过滤器 (用于自动注入trace_id/span_id)
├── formatters.py         # 自定义日志格式化器 (如果需要)
├── tests/                # 单元测试
│   ├── __init__.py
│   ├── test_logger.py
│   └── ...
└── README.md             # 模块说明文档
```

## 5. API 接口示例 (API Interface Examples)

```python
# sdk.py

import logging
from contextlib import contextmanager
from typing import Generator, Dict, Optional
# 假设我们有一个内部的tracer模块来管理trace/span
# from . import tracer

def get_logger(name: str) -> logging.Logger:
    """
    获取一个已配置为输出结构化JSON日志的Logger实例。
    该Logger会自动在每条日志中注入当前的 trace_id 和 span_id。
    """
    # 内部实现会配置 logger 使用 JsonFormatter 和 自动注入 trace_id/span_id 的 filter
    pass

# 最佳实践：使用`extra`参数传递结构化的业务上下文
# logger = get_logger(__name__)
# logger.info(
#     "Task processing started.", 
#     extra={
#         "task_id": "uuid-123",
#         "agent_id": "Coder_v1",
#         "input_data_size": 512
#     }
# )

@contextmanager
def start_trace(name: str) -> Generator[None, None, None]:
    """
    开始一个新的分布式追踪。
    此操作会生成一个新的 trace_id，并将其设置为当前上下文。
    """
    # trace_id = tracer.generate_trace_id()
    # token = tracer.set_trace_id(trace_id)
    try:
        yield
    finally:
        # tracer.reset_trace_id(token)
        pass

@contextmanager
def start_span(name: str) -> Generator[None, None, None]:
    """
    在当前追踪下开始一个新的跨度 (Span)。
    此操作会生成一个新的 span_id，并将其设置为当前上下文。
    它还会将此 span_id 与父 span_id 关联（如果存在）。
    """
    # span_id = tracer.generate_span_id()
    # parent_span_id = tracer.get_current_span_id()
    # token = tracer.set_span_id(span_id)
    try:
        # 可以在这里记录 span 开始的日志
        # logger = get_logger(__name__)
        # logger.info("Span started", extra={"event": "span_start", "span_name": name})
        yield
    finally:
        # tracer.reset_span_id(token)
        # 记录 span 结束的日志
        # logger.info("Span ended", extra={"event": "span_end", "span_name": name})
        pass

def inject_trace_context() -> Dict[str, str]:
    """
    将当前的追踪上下文 (trace_id, span_id) 序列化为一个字典。
    该字典可以被放入HTTP Header或消息队列的Payload中，以便在服务间传递。
    返回:
        Dict[str, str]: 包含追踪上下文信息的字典，例如遵循W3C Trace Context标准。
    """
    # context_data = tracer.get_current_context()
    # return format_context_for_propagation(context_data) # 例如 {'traceparent': '...'}
    pass

def extract_trace_context(context_dict: Dict[str, str]) -> None:
    """
    从一个字典中提取追踪上下文 (trace_id, span_id) 并设置到当前的ContextVar中。
    通常在服务接收到请求或消息时调用此函数。
    参数:
        context_dict (Dict[str, str]): 包含追踪上下文信息的字典。
    """
    # context_data = parse_context_from_propagation(context_dict) # 例如从 {'traceparent': '...'} 解析
    # tracer.set_context(context_data)
    pass
```

## 6. 测试策略 (Testing Strategy)

*   **单元测试**: 使用 `unittest` 或 `pytest` 对 `logger`, `tracer`, `context`, `sdk` 等模块的核心功能进行测试。
*   **集成测试**: 编写测试用例，验证在不同模块调用、异步任务中，`trace_id` 和 `span_id` 能否正确传播，并且日志能够正确注入这些ID。同时测试 `inject_trace_context` 和 `extract_trace_context` 的正确性。

## 7. 部署与依赖 (Deployment & Dependencies)

*   本服务作为 Python 包，通过 `pip` 安装依赖。
*   核心依赖: `python-json-logger`, `opentelemetry-api`, `opentelemetry-sdk` (M2+), `interfaces` 模块。
*   需要配置日志级别、追踪采样率、Exporter端点等。