# BaseAgent Test Cases

## 测试用例 1: BaseAgent 初始化测试

### 测试用例描述
测试 BaseAgent 类的初始化功能，确保能够正确接收和存储配置参数。

### 测试用例输入
```python
agent_config = {"name": "test_agent", "version": "1.0"}
task_data = {"task_id": "123", "input_data": {"query": "test"}, "context": {}}
group_config = {"group_name": "test_group"}
```

### 测试用例预期输出
BaseAgent 实例成功创建，所有配置参数正确存储。

### 测试用例实际输出
(待执行后填写)

### 测试用例结果
(待执行后填写)

### 测试用例备注
验证 BaseAgent 的基本初始化功能。

## 测试用例 2: 首次运行检测测试

### 测试用例描述
测试 `is_first_run()` 方法在不同上下文条件下的正确性。

### 测试用例输入
```python
# 首次运行场景
task_data_no_context = {"task_id": "123", "input_data": {"query": "test"}}

# 非首次运行场景 - 有 LLM 响应
task_data_with_llm = {
    "task_id": "123", 
    "input_data": {"query": "test"},
    "context": {"last_llm_response": {"content": "response"}}
}
```

### 测试用例预期输出
- 首次运行场景：`is_first_run()` 返回 `True`
- 非首次运行场景：`is_first_run()` 返回 `False`

### 测试用例实际输出
(待执行后填写)

### 测试用例结果
(待执行后填写)

### 测试用例备注
验证首次运行检测逻辑的正确性。

## 测试用例 3: LLM 响应获取测试

### 测试用例描述
测试 `get_last_llm_response()` 方法能否正确从上下文中获取 LLM 响应。

### 测试用例输入
```python
task_data_with_response = {
    "task_id": "123",
    "input_data": {"query": "test"},
    "context": {"last_llm_response": {"content": "test response"}}
}
```

### 测试用例预期输出
返回 `{"content": "test response"}`

### 测试用例实际输出
(待执行后填写)

### 测试用例结果
(待执行后填写)

### 测试用例备注
验证 LLM 响应获取功能。

## 测试用例 4: 工具结果获取测试

### 测试用例描述
测试 `get_last_tool_result()` 方法能否正确从上下文中获取工具结果。

### 测试用例输入
```python
task_data_with_tool_result = {
    "task_id": "123",
    "input_data": {"query": "test"},
    "context": {"last_tool_result": {"status": "success", "data": "result"}}
}
```

### 测试用例预期输出
返回 `{"status": "success", "data": "result"}`

### 测试用例实际输出
(待执行后填写)

### 测试用例结果
(待执行后填写)

### 测试用例备注
验证工具结果获取功能。

## 测试用例 5: LLM 调用请求创建测试

### 测试用例描述
测试 `request_llm_call()` 方法能否正确创建 LLM 调用请求。

### 测试用例输入
```python
prompt = "What is the weather today?"
```

### 测试用例预期输出
返回符合 AgentResult 规范的字典，包含 ToolCallRequest 意图，tool_id 为 "System.LLM.invoke"

### 测试用例实际输出
(待执行后填写)

### 测试用例结果
(待执行后填写)

### 测试用例备注
验证 LLM 调用请求创建功能。

## 测试用例 6: 工具调用请求创建测试

### 测试用例描述
测试 `request_tool_call()` 方法能否正确创建工具调用请求。

### 测试用例输入
```python
tool_id = "Calculator.add"
arguments = {"a": 1, "b": 2}
```

### 测试用例预期输出
返回符合 AgentResult 规范的字典，包含 ToolCallRequest 意图，tool_id 为 "Calculator.add"

### 测试用例实际输出
(待执行后填写)

### 测试用例结果
(待执行后填写)

### 测试用例备注
验证工具调用请求创建功能。

## 测试用例 7: 最终答案创建测试

### 测试用例描述
测试 `create_final_answer()` 方法能否正确创建最终答案。

### 测试用例输入
```python
thought = "The calculation is complete."
content = {"result": 3}
```

### 测试用例预期输出
返回符合 AgentResult 规范的字典，包含 FinalAnswer 意图

### 测试用例实际输出
(待执行后填写)

### 测试用例结果
(待执行后填写)

### 测试用例备注
验证最终答案创建功能。

## 测试用例 8: 失败响应创建测试

### 测试用例描述
测试 `create_failure_response()` 方法能否正确创建失败响应。

### 测试用例输入
```python
type = "TEST_ERROR"
message = "This is a test error"
```

### 测试用例预期输出
返回符合 AgentResult 规范的字典，status 为 "FAILURE"，包含 FailureDetails

### 测试用例实际输出
(待执行后填写)

### 测试用例结果
(待执行后填写)

### 测试用例备注
验证失败响应创建功能。