

## **LLM网关服务 (LLM Gateway Service) 产品与开发文档 (V1.0 务实版)**

**文档版本**: 1.1 (Focused MVP)

### **1. 产品概述 (Product Overview)**

#### **1.1. 职责 (Responsibility)**
LLM网关服务 (以下简称`LLMGateway`) 是Synapse平台与所有大型语言模型（LLM）进行交互的**唯一、集中的、受控的**出口。它旨在为平台的所有上游服务提供一个**统一、可靠、经济、可观测**的LLM能力接口。

#### **1.2. 核心价值 (Core Value Proposition for V1.0)**
*   **统一性 (Unity)**: 屏蔽底层不同LLM供应商的API差异。
*   **经济性 (Economy)**: 通过**调用前Token估算**、**调用后成本核算**和**请求缓存**，最大限度地降低LLM使用成本。
*   **可靠性 (Reliability)**: 通过**自动重试**和**规则化的故障切换**，确保LLM服务的最高可用性。
*   **可控性 (Control)**: 通过**严格的、多时间窗口的配额管理**，防止资源滥用，并为超限情况提供明确的反馈。

### **2. V1.0 核心功能需求 (Core Functional Requirements for V1.0)**

#### **FR-1: 统一接口与适配层**
*   **FR-1a (接口标准化)**: 必须提供一个与**OpenAI `v1/chat/completions` API规范严格兼容**的内部REST API端点。
*   **FR-1b (Tool Calling抽象)**: 必须能正确处理OpenAI格式的`tools`定义，包括为不支持的模型进行**模拟实现**。

#### **FR-2: 可靠性与弹性**
*   **FR-2a (自动重试)**: 必须为所有外部API调用，实现基于**指数退避**的自动重试机制。
*   **FR-2b (规则化故障切换 - Fallback)**:
    *   必须支持在`capabilities.json`或数据库中，为每个主模型配置一个**有序的备用模型列表（Fallback Chain）**。
    *   当主模型连续调用失败达到阈值时，必须**按顺序**尝试调用备用模型列表中的下一个模型。

#### **FR-3: 成本与用量控制 (核心)**
*   **FR-3a (调用前Token估算)**:
    *   在向LLM发送请求**之前**，必须使用`tiktoken`等库，根据请求的`messages`和`tools`，**预估**出`prompt_tokens`的数量。
*   **FR-3b (Max Token超限反馈)**:
    *   必须能从模型配置中获知其`max_context_window`。
    *   如果**调用前估算的Token数**超过了模型的`max_context_window`，**必须立即拒绝请求**，并返回一个特定的、可被机器解析的错误（例如，HTTP 413 Payload Too Large），响应体中需包含`{"error": "max_token_exceeded", "estimated_tokens": ..., "limit": ...}`。
*   **FR-3c (调用后成本核算)**:
    *   在调用API**之后**，必须根据LLM返回的精确用量，结合可配置的“价目表”，计算出本次调用的**实际成本**。
    *   所有用量和成本信息，必须被**异步地**记录到`llm_usage_logs`数据库表中。


#### **FR-4: 配额管理与队列等待**
*   **FR-4a (配额定义)**: 必须支持为不同的实体（`workflow_id`, `group_id`等）设置基于**Token数量**和**调用次数**的、**多时间窗口（分钟/小时/天）**的配额。
*   **FR-4b (配额检查)**: 在每次API调用**之前**，必须**原子性地**检查所有相关配额。
*   **FR-4c (超限处理策略)**:
    *   当配额超限时，**必须**支持**两种可配置的**处理策略：
        1.  **`REJECT` (默认)**: 立即拒绝请求，返回HTTP 429 Too Many Requests。
        2.  **`QUEUE_AND_WAIT`**: 将请求放入一个**Redis延迟队列**中，并挂起HTTP连接（或返回一个“处理中”的响应）。当配额窗口刷新后，由一个后台工作者从队列中取出请求并执行。必须为此模式设置一个最大等待超时时间。



### **4. 模块结构与核心处理流程 (微调)**

模块结构保持不变，但核心处理流程会变得更加丰富。

**`LLMGatewayService.handle_chat_completion` 伪代码 (V1.1版):**
```python
def handle_chat_completion(request):
    # 1. 认证 & 授权
    # ...

    # 2. 【新增】调用前Token估算
    estimated_tokens = self.estimate_tokens(request)
    target_model_config = self.get_model_config(request.model)
    if estimated_tokens > target_model_config['max_tokens']:
        raise MaxTokenExceededError(estimated_tokens, target_model_config['max_tokens'])

    # 3. 检查配额
    quota_status = self.check_quotas(request.user_id, estimated_tokens)
    if quota_status.is_exceeded:
        # 【新增】处理超限策略
        if quota_status.policy == 'REJECT':
            raise QuotaExceededError()
        elif quota_status.policy == 'QUEUE_AND_WAIT':
            return self.enqueue_request(request)

    # 4. 检查缓存
    # ... (逻辑不变)

    # 5. 【修改】规则路由 (使用Fallback Chain)
    #    主循环会遍历配置好的模型列表
    for model_to_try in target_model_config['fallback_chain']:
        try:
            # 6. API调用 (带重试)
            response = self.call_llm_api_with_retry(request, model_to_try)
            
            # 7. 调用成功，处理响应并跳出循环
            final_response = self.parse_response(response)
            
            # 8. 【新增】调用后成本核算
            usage_data = self.calculate_usage_and_cost(request, final_response, model_to_try)
            self.log_usage_async(usage_data)
            self.update_quota_usage_async(request.user_id, usage_data)
            
            # 9. 更新缓存 & 返回
            self.update_cache(request, final_response)
            return final_response
            
        except APIError as e:
            # 如果API调用失败，记录日志，循环会继续尝试下一个备用模型
            self.log_fallback_attempt(model_to_try, e)
            continue
    
    # 如果所有模型都尝试失败
    raise AllModelsFailedError()
```

### **5. API接口 (`/v1/chat/completions`) 响应体增强**

*   **Error Response `413 Payload Too Large`**:
    ```json
    {
      "error": {
        "type": "tokens_exceeded",
        "message": "The estimated prompt tokens (4500) exceed the model's maximum context window (4096).",
        "estimated_tokens": 4500,
        "limit": 4096
      }
    }
    ```
*   **Error Response `429 Too Many Requests`**:
    ```json
    {
      "error": {
        "type": "quota_exceeded",
        "message": "You have exceeded your quota for this time window. Please try again later.",
        "retry_after_seconds": 3600 // 告知客户端何时可以重试
      }
    }
    ```

---
