# ToolService 测试文档

## 测试用例

### 1. 测试用例名称
成功执行Hello工具

### 测试用例描述
测试ToolService能否成功执行一个简单的问候工具

### 测试用例输入
```python
ToolCallRequest(
    tool_id="TestTools.hello",
    arguments={"name": "World"}
)
```

### 测试用例预期输出
```python
ToolResult(
    status="SUCCESS",
    output={"message": "Hello, World!", "tool": "hello_tool"}
)
```

### 测试用例实际输出
(在测试执行时填写)

### 测试用例结果
(在测试执行时填写)

### 测试用例备注
无

---

### 2. 测试用例名称
成功执行计算器工具

### 测试用例描述
测试ToolService能否成功执行计算器工具

### 测试用例输入
```python
ToolCallRequest(
    tool_id="TestTools.calculator",
    arguments={"operation": "add", "a": 5, "b": 3}
)
```

### 测试用例预期输出
```python
ToolResult(
    status="SUCCESS",
    output={
        "operation": "add",
        "operand_a": 5,
        "operand_b": 3,
        "result": 8
    }
)
```

### 测试用例实际输出
(在测试执行时填写)

### 测试用例结果
(在测试执行时填写)

### 测试用例备注
无

---

### 3. 测试用例名称
执行不存在的工具

### 测试用例描述
测试ToolService对不存在的工具的处理

### 测试用例输入
```python
ToolCallRequest(
    tool_id="NonExistentTool.test",
    arguments={}
)
```

### 测试用例预期输出
```python
ToolResult(
    status="FAILURE",
    error_type="TOOL_NOT_FOUND",
    error_message="Tool with id 'NonExistentTool.test' not found in capability registry"
)
```

### 测试用例实际输出
(在测试执行时填写)

### 测试用例结果
(在测试执行时填写)

### 测试用例备注
无

---

### 4. 测试用例名称
参数校验失败

### 测试用例描述
测试ToolService对参数校验失败的处理

### 测试用例输入
```python
ToolCallRequest(
    tool_id="TestTools.hello",
    arguments={}  # 缺少必需的"name"参数
)
```

### 测试用例预期输出
```python
ToolResult(
    status="FAILURE",
    error_type="VALIDATION_ERROR",
    error_message="Validation failed: ... at ..."
)
```

### 测试用例实际输出
(在测试执行时填写)

### 测试用例结果
(在测试执行时填写)

### 测试用例备注
无

---

### 5. 测试用例名称
工具执行异常

### 测试用例描述
测试ToolService对工具执行异常的处理

### 测试用例输入
```python
ToolCallRequest(
    tool_id="TestTools.failing",
    arguments={"message": "Test error message"}
)
```

### 测试用例预期输出
```python
ToolResult(
    status="FAILURE",
    error_type="TOOL_EXECUTION_ERROR",
    error_message="Test error message"
)
```

### 测试用例实际输出
(在测试执行时填写)

### 测试用例结果
(在测试执行时填写)

### 测试用例备注
无