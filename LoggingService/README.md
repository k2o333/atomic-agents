# Logging & Tracing Service

## 1. 模块介绍

日志与追踪服务 (`LoggingService`) 是 Synapse 平台的基础设施模块，负责提供统一的结构化日志记录和分布式追踪能力。它确保系统内所有操作都能生成格式一致、内容结构化的日志，并通过 `trace_id` 和 `span_id` 实现跨模块、跨服务的调用链追踪。

## 2. 模块功能

*   **结构化日志**: 输出 JSON 格式的日志，方便日志收集和分析系统解析。
*   **分布式追踪上下文管理**: 生成和管理 `trace_id` (用于标识整个请求/工作流) 和 `span_id` (用于标识单个操作)。
*   **上下文自动传播**: 在 Python 的异步任务和函数调用中自动传播追踪上下文。
*   **日志自动注入**: 所有通过本服务获取的 Logger 记录的日志都会自动包含当前的 `trace_id` 和 `span_id`。

## 3. 模块入口文件

本模块的入口文件是 `sdk.py`。所有对外提供的功能都通过此文件暴露。

## 4. 如何调用模块接口

### 4.1. 安装模块

确保模块已安装。如果以可编辑模式安装了整个项目，通常可以直接导入。

### 4.2. 导入 SDK

在需要使用日志和追踪功能的 Python 文件中，导入 SDK：

```python
from LoggingService.sdk import get_logger, TracerContextManager
```

### 4.3. 获取 Logger

使用 `get_logger(name)` 函数获取一个已配置好的结构化 Logger 实例。

*   **参数**:
    *   `name` (str): Logger 的名称，通常使用 `__name__` 或模块名。
*   **返回值**: 一个 `logging.Logger` 实例。

```python
# 获取一个 logger
logger = get_logger(__name__)
```

### 4.4. 记录日志

使用获取的 `logger` 实例记录日志。日志会自动以 JSON 格式输出，并包含 `trace_id` 和 `span_id`（如果当前存在追踪上下文）。

*   **方法**: `logger.info()`, `logger.warning()`, `logger.error()` 等标准 `logging.Logger` 方法。
*   **参数**:
    *   `msg` (str): 日志消息。
    *   `extra` (dict, optional): 一个字典，可以包含任何你想添加到 JSON 日志中的额外字段。

```python
# 记录普通日志
logger.info("Processing user request")

# 记录带额外信息的日志
logger.info("User logged in", extra={"user_id": 12345, "ip_address": "192.168.1.100"})
```

### 4.5. 管理追踪上下文

使用 `TracerContextManager` 来创建和管理追踪 (`trace`) 和跨度 (`span`)。

#### 4.5.1. 开始一个新追踪 (Start Trace)

当开始处理一个全新的、顶层的请求或工作流时，使用 `TracerContextManager.start_trace(name)`。

*   **参数**:
    *   `name` (str): 追踪的名称，用于标识这个工作流。
*   **返回值**: 一个上下文管理器 (Context Manager)。

```python
# 在处理新请求的入口点
with TracerContextManager.start_trace("process_user_registration"):
    # ... 在这个 with 块内的所有操作都属于同一个 trace ...
    logger.info("Starting user registration process")
    # 调用其他函数或服务
```

#### 4.5.2. 开始一个新跨度 (Start Span)

在追踪内部，当执行一个具体的子操作（如调用数据库、调用外部API、执行一个函数）时，使用 `TracerContextManager.start_span(name)`。

*   **参数**:
    *   `name` (str): 跨度的名称，用于标识这个操作。
*   **返回值**: 一个上下文管理器 (Context Manager)。

```python
# 在执行某个具体操作时
with TracerContextManager.start_span("validate_user_data"):
    logger.info("Validating input data")
    # ... 执行数据验证逻辑 ...
    
# 在调用另一个服务时
with TracerContextManager.start_span("call_database_save"):
    logger.info("Saving user to database")
    # ... 调用数据库保存逻辑 ...
```

### 4.6. 完整调用示例

```python
# main.py 或某个服务的入口文件
from LoggingService.sdk import get_logger, TracerContextManager

# 1. 获取 logger
logger = get_logger("my_service")

def handle_user_request(user_data):
    # 2. 开始一个新的追踪
    with TracerContextManager.start_trace("handle_user_request"):
        logger.info("Received user request", extra={"request_data": user_data})
        
        # 3. 在追踪内开始一个子操作的跨度
        with TracerContextManager.start_span("validate_input"):
            logger.info("Starting input validation")
            # ... 执行验证 ...
            logger.info("Input validation completed")
            
        # 4. 开始另一个子操作的跨度
        with TracerContextManager.start_span("process_data"):
            logger.info("Starting data processing")
            # ... 执行处理 ...
            logger.info("Data processing completed")
            
        logger.info("Request handled successfully")

# 模拟调用
if __name__ == "__main__":
    handle_user_request({"username": "testuser", "email": "test@example.com"})
```