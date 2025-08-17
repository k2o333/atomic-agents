# ToolService Module

## 简介

ToolService是Synapse平台执行所有**非LLM的、与外部世界交互的具体动作**的**唯一、安全的**执行环境。它负责动态加载、执行并监控`Tool`脚本，确保Agent的"行动意图"能够被可靠地转化为现实世界中的操作。

## 主要功能

1. **动态加载**: 根据`tool_id`从能力注册表中查找对应的实现路径，并动态加载Tool函数
2. **参数校验**: 在执行Tool之前，根据定义的JSON Schema对传入参数进行严格校验
3. **安全执行**: 执行Tool函数并捕获所有异常，确保系统稳定性
4. **标准化结果**: 将Tool执行结果封装成标准化的`ToolResult`格式返回

## 安装/部署

### 依赖项

- Python 3.11+
- `interfaces` 模块
- `LoggingService` 模块
- `jsonschema` 库

### 环境要求

- 可访问的 `capabilities.json` 文件，用于查找Tool定义
- 正确配置的Python环境

### 安装步骤

ToolService作为项目的一部分，不需要单独安装。确保项目依赖已安装：

```bash
pip install -r requirements.txt
```

### 配置说明

ToolService需要访问项目根目录下的 `capabilities.json` 文件来获取Tool定义。

## 快速开始

```python
from interfaces import ToolCallRequest
from toolservices.service import ToolService

# 创建ToolService实例
tool_service = ToolService()

# 创建Tool调用请求
request = ToolCallRequest(
    tool_id="TestTools.hello",
    arguments={"name": "World"}
)

# 执行Tool
result = tool_service.run_tool(request)

# 处理结果
if result.status == "SUCCESS":
    print(f"Tool executed successfully: {result.output}")
else:
    print(f"Tool execution failed: {result.error_message}")
```

## API/接口文档

### ToolService 类

#### `run_tool(tool_call_request: ToolCallRequest) -> ToolResult`

执行指定的Tool。

**参数:**
- `tool_call_request`: ToolCallRequest对象，包含tool_id和arguments

**返回值:**
- `ToolResult`: 包含执行结果的标准化结果对象

**示例:**
```python
request = ToolCallRequest(
    tool_id="TestTools.calculator",
    arguments={"operation": "add", "a": 5, "b": 3}
)
result = tool_service.run_tool(request)
```

## 配置

### 配置项说明

ToolService依赖于 `capabilities.json` 文件中的Tool定义。

### 配置文件示例

```json
{
  "registries": {
    "tools": [
      {
        "id": "TestTools.hello",
        "implementation_path": "toolservices.test_tools.hello_tool",
        "parameters_schema": {
          "type": "object",
          "properties": {
            "name": {"type": "string"}
          },
          "required": ["name"]
        }
      }
    ]
  }
}
```

## 使用指南

### 常见场景的详细使用步骤

1. **添加新的Tool**:
   - 在 `capabilities.json` 中添加Tool定义
   - 实现Tool函数
   - 确保Tool函数可以通过定义的路径导入

2. **调用Tool**:
   - 创建 `ToolCallRequest` 对象
   - 调用 `ToolService.run_tool()` 方法
   - 处理返回的 `ToolResult`

### 最佳实践

- 为每个Tool定义清晰的参数Schema
- 在Tool函数中处理可能的异常
- 使用标准化的返回格式

## 架构/设计

### 高层架构图

```
+-------------------+
|   Central Graph   |
|      Engine       |
+-------------------+
          |
          v
+-------------------+
|   ToolService     |
|   (this module)   |
+-------------------+
          |
    +-----+-----+
    |     |     |
    v     v     v
+---+   +-+-+  +-+-+
|Loader| |Validator| |Executor|
+---+   +-+-+  +-+-+
```

### 核心组件说明

1. **ToolService**: 主服务类，提供 `run_tool` 接口
2. **ToolLoader**: 负责动态加载Tool函数
3. **ToolValidator**: 负责参数校验
4. **ToolExecutor**: 负责执行Tool函数

## 开发指南

### 如何构建

在项目根目录下运行：

```bash
python -m build
```

### 运行测试

```bash
python -m unittest toolservices/tests/test_service.py
```

或者运行所有测试：

```bash
python -m unittest discover toolservices/tests
```

### 贡献代码

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 故障排查

### 常见问题

1. **Tool not found**: 检查 `capabilities.json` 中是否正确定义了Tool
2. **Validation error**: 检查传入参数是否符合Schema定义
3. **Import error**: 检查Tool实现路径是否正确

### 错误信息及解决方案

- `TOOL_NOT_FOUND`: Tool ID在能力注册表中不存在
- `VALIDATION_ERROR`: 参数校验失败
- `TOOL_EXECUTION_ERROR`: Tool执行过程中发生异常

### 日志位置

日志通过 `LoggingService` 输出，具体位置取决于 `LoggingService` 的配置。

## 变更日志

### v1.0.0

- 初始版本
- 实现基本的Tool加载、校验和执行功能
- 支持标准化的结果返回格式

## 安全说明

**注意**: 当前版本为开发阶段的简化实现，所有Tool的`run`函数将直接在`ToolService`的进程中执行，**存在安全风险**。在生产环境中，应实现安全沙箱机制。

## "如何用/维护"

### 操作指南

1. 确保 `capabilities.json` 文件存在且格式正确
2. 实现Tool函数并确保可通过指定路径导入
3. 使用 `ToolService.run_tool()` 方法执行Tool

### 接口说明

主要接口为 `ToolService.run_tool()` 方法，接收 `ToolCallRequest` 参数，返回 `ToolResult`。

### 配置方法

通过 `capabilities.json` 文件配置Tool定义。

### 排错信息

查看日志输出以获取详细的错误信息。