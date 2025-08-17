# LLM网关服务 (LLM Gateway Service)

## 模块介绍

LLM网关服务是Synapse平台与所有大型语言模型（LLM）进行交互的唯一、集中的、受控的出口。它为平台的所有上游服务提供了一个统一、可靠、经济、可观测的LLM能力接口。

## 模块功能

1. **统一接口与适配层**: 提供与OpenAI `v1/chat/completions` API规范严格兼容的内部REST API端点，并能正确处理OpenAI格式的`tools`定义。

2. **可靠性与弹性**: 为所有外部API调用实现基于指数退避的自动重试机制。

3. **成本与用量控制**: 通过调用前Token估算和调用后成本核算，最大限度地降低LLM使用成本。

4. **Token计数**: 集成tiktoken库，在调用API前后准确计算Token使用量。

5. **工具调用适配**: 支持原生Tool Calling模型和不支持Tool Calling模型的模拟实现。

## 模块接口如何调用

### 主要类: LLMGatewayService

#### 初始化
```python
from llmgateway.service import LLMGatewayService

# 创建服务实例
service = LLMGatewayService()
```

#### 核心方法: chat_completion

```python
async def chat_completion(request: OpenAICompatibleRequest) -> OpenAICompatibleResponse:
    """
    统一的聊天补全接口
    
    Args:
        request: OpenAI兼容的请求对象
        
    Returns:
        OpenAICompatibleResponse: OpenAI兼容的响应对象
    """
```

##### 参数说明

- `request` (OpenAICompatibleRequest): 包含以下字段：
  - `model` (str): 模型名称
  - `messages` (List[OpenAICompatibleMessage]): 消息列表
  - `stream` (bool, optional): 是否流式输出，默认为False
  - `temperature` (float, optional): 温度参数
  - `max_tokens` (int, optional): 最大Token数
  - `tools` (List[OpenAICompatibleTool], optional): 工具列表
  - `tool_choice` (Union[str, Dict[str, Any]], optional): 工具选择策略

##### 返回值说明

- `OpenAICompatibleResponse`: 包含以下字段：
  - `id` (str): 响应ID
  - `object` (str): 对象类型
  - `created` (int): 创建时间戳
  - `model` (str): 模型名称
  - `choices` (List[Dict[str, Any]]): 选择列表
  - `usage` (OpenAICompatibleUsage): 用量信息
  - `system_fingerprint` (str, optional): 系统指纹

##### 使用示例

```python
from llmgateway.interfaces import OpenAICompatibleRequest, OpenAICompatibleMessage

# 创建请求
request = OpenAICompatibleRequest(
    model="gpt-4o-mini",
    messages=[
        OpenAICompatibleMessage(role="user", content="Hello, world!")
    ]
)

# 调用接口
response = await service.chat_completion(request)

# 处理响应
print(f"Response: {response.choices[0]['message']['content']}")
print(f"Token usage: {response.usage}")
```