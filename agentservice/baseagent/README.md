# Agents Module

## 模块简介

Agents 模块是 Synapse 平台的核心组件，负责提供 Agent 开发的 SDK 基础。`BaseAgent` 类是所有自定义 Agent 的基类，它封装了与系统交互的复杂性，让开发者可以专注于业务逻辑的实现。

## 主要功能

1. **标准化接口**：提供统一的 Agent 与系统交互接口
2. **重入处理**：自动处理 LLM 和工具调用的返回结果
3. **辅助方法**：提供便捷的方法来创建标准化的意图响应
4. **日志记录**：集成平台的日志系统，支持分布式追踪

## 核心组件

### BaseAgent 类

`BaseAgent` 是所有 Agent 的基类，提供了以下核心功能：

- **模板方法模式**：实现了标准的执行流程
- **重入逻辑**：自动判断是首次执行还是处理返回结果
- **辅助方法**：
  - `request_llm_call()`：请求 LLM 调用
  - `request_tool_call()`：请求工具调用
  - `create_final_answer()`：创建最终答案
  - `create_failure_response()`：创建失败响应
  - `get_last_llm_response()`：获取上次 LLM 响应
  - `get_last_tool_result()`：获取上次工具结果
  - `is_first_run()`：判断是否为首次执行

### 抽象方法

子类必须实现以下抽象方法：

- `_generate_dynamic_prompt()`：生成动态提示词
- `_handle_llm_response()`：处理 LLM 响应

## 使用指南

### 创建自定义 Agent

1. 继承 `BaseAgent` 类
2. 实现 `_generate_dynamic_prompt()` 方法
3. 实现 `_handle_llm_response()` 方法

示例：

```python
from agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def _generate_dynamic_prompt(self) -> str:
        # 生成与任务相关的动态提示词
        return f"Process this task: {self.task_data.get('input_data', {})}"
    
    def _handle_llm_response(self, llm_response: Dict) -> Dict:
        # 处理 LLM 响应并返回标准化结果
        return self.create_final_answer(
            thought="Processed the LLM response",
            content=llm_response.get("content", "")
        )
```

## API 文档

### BaseAgent 类方法

#### 核心执行方法
- `run()`：Agent 执行入口点

#### 抽象方法（需子类实现）
- `_generate_dynamic_prompt() -> str`：生成动态提示词
- `_handle_llm_response(llm_response: Dict) -> Dict`：处理 LLM 响应

#### 辅助方法
- `request_llm_call(prompt: str, tools: List = None) -> Dict`：创建 LLM 调用请求
- `request_tool_call(tool_id: str, arguments: Dict) -> Dict`：创建工具调用请求
- `create_final_answer(thought: str, content: Any) -> Dict`：创建最终答案
- `create_failure_response(type: str, message: str) -> Dict`：创建失败响应
- `get_last_llm_response() -> Optional[Dict]`：获取上次 LLM 响应
- `get_last_tool_result() -> Optional[Dict]`：获取上次工具结果
- `is_first_run() -> bool`：判断是否为首次执行

## 开发规范

1. 所有 Agent 必须继承自 `BaseAgent`
2. 不要在 Agent 中直接执行 I/O 操作
3. 所有外部调用必须通过工具请求完成
4. 使用提供的辅助方法创建标准化响应