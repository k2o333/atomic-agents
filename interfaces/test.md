# interfaces模块测试用例

## 1. PlanBlueprint模型测试用例

### 测试用例1: PlanBlueprint基本结构验证
- **测试用例描述**: 验证PlanBlueprint模型能否正确处理基本字段
- **测试用例输入**: 
  ```json
  {
    "workflow_id": "123e4567-e89b-12d3-a456-426614174000",
    "new_tasks": [],
    "new_edges": [],
    "update_tasks": []
  }
  ```
- **测试用例预期输出**: 成功创建PlanBlueprint实例，所有字段正确赋值
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

### 测试用例2: PlanBlueprint包含新任务
- **测试用例描述**: 验证PlanBlueprint模型能否正确处理包含新任务的情况
- **测试用例输入**: 
  ```json
  {
    "new_tasks": [
      {
        "task_id": "task1",
        "input_data": {"goal": "test goal"},
        "assignee_id": "Agent:1"
      }
    ]
  }
  ```
- **测试用例预期输出**: 成功创建PlanBlueprint实例，new_tasks列表包含一个TaskDefinition
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

## 2. AgentResult模型测试用例

### 测试用例3: AgentResult成功状态验证
- **测试用例描述**: 验证AgentResult模型在成功状态下的正确性
- **测试用例输入**: 
  ```json
  {
    "status": "SUCCESS",
    "output": {
      "thought": "Task completed successfully",
      "intent": {
        "content": "Final result"
      }
    }
  }
  ```
- **测试用例预期输出**: 成功创建AgentResult实例，status为SUCCESS，output包含正确的AgentIntent
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

### 测试用例4: AgentResult失败状态验证
- **测试用例描述**: 验证AgentResult模型在失败状态下的正确性
- **测试用例输入**: 
  ```json
  {
    "status": "FAILURE",
    "output": {
      "thought": "Task failed",
      "intent": {
        "content": "Error occurred"
      }
    },
    "failure_details": {
      "type": "LLM_REFUSAL",
      "message": "LLM refused to execute"
    }
  }
  ```
- **测试用例预期输出**: 成功创建AgentResult实例，status为FAILURE，包含failure_details
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

## 3. ContextBuildConfig模型测试用例

### 测试用例5: ContextBuildConfig基本结构验证
- **测试用例描述**: 验证ContextBuildConfig模型的基本字段处理
- **测试用例输入**: 
  ```json
  {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "include_metadata": true,
    "include_tool_list": true
  }
  ```
- **测试用例预期输出**: 成功创建ContextBuildConfig实例，基本字段正确赋值
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

### 测试用例6: ContextBuildConfig包含配置选项
- **测试用例描述**: 验证ContextBuildConfig模型处理各种配置选项
- **测试用例输入**: 
  ```json
  {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "conversation_history_config": {"last_n": 5},
    "task_list_config": {"status_in": ["COMPLETED"]},
    "artifact_config": {"asset_id": "asset123", "mode": "SUMMARY"}
  }
  ```
- **测试用例预期输出**: 成功创建ContextBuildConfig实例，所有配置选项正确赋值
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

## 4. TaskDirectives模型测试用例

### 测试用例7: TaskDirectives基本结构验证
- **测试用例描述**: 验证TaskDirectives模型的基本字段处理
- **测试用例输入**: 
  ```json
  {
    "timeout_seconds": 300,
    "on_failure": {"type": "GOTO", "target_task_id": "task2"}
  }
  ```
- **测试用例预期输出**: 成功创建TaskDirectives实例，基本字段正确赋值
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

### 测试用例8: TaskDirectives包含循环指令
- **测试用例描述**: 验证TaskDirectives模型处理循环指令
- **测试用例输入**: 
  ```json
  {
    "loop_directive": {
      "type": "PARALLEL_ITERATION",
      "iteration_input_key": "items",
      "input_source_task_id": "task1",
      "task_template": {
        "task_id": "subtask",
        "input_data": {"item": "{{item}}"},
        "assignee_id": "Agent:1"
      }
    }
  }
  ```
- **测试用例预期输出**: 成功创建TaskDirectives实例，包含正确的LoopDirective
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

## 5. InterventionRequest模型测试用例

### 测试用例9: InterventionRequest基本结构验证
- **测试用例描述**: 验证InterventionRequest模型的基本字段处理
- **测试用例输入**: 
  ```json
  {
    "intervention_type": "PAUSE",
    "target_task_id": "123e4567-e89b-12d3-a456-426614174000",
    "comment": "Pausing for review"
  }
  ```
- **测试用例预期输出**: 成功创建InterventionRequest实例，基本字段正确赋值
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

### 测试用例10: InterventionRequest回滚并修改
- **测试用例描述**: 验证InterventionRequest模型处理回滚并修改操作
- **测试用例输入**: 
  ```json
  {
    "intervention_type": "ROLLBACK_AND_MODIFY",
    "target_task_id": "123e4567-e89b-12d3-a456-426614174000",
    "rollback_to_version": 1,
    "new_input_data": {"updated_goal": "new goal"},
    "new_assignee_id": "Agent:2",
    "comment": "Rolling back and updating task"
  }
  ```
- **测试用例预期输出**: 成功创建InterventionRequest实例，包含所有回滚和修改字段
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

## 6. 日志功能测试用例

### 测试用例11: 模型初始化日志记录
- **测试用例描述**: 验证模型实例化时是否正确记录初始化日志
- **测试用例输入**: 
  ```python
  from interfaces import PlanBlueprint
  blueprint = PlanBlueprint(workflow_id="123e4567-e89b-12d3-a456-426614174000")
  ```
- **测试用例预期输出**: 在日志输出中应包含PlanBlueprint初始化的相关日志信息，包括"Initializing PlanBlueprint"和"PlanBlueprint initialized successfully"
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 需要mock或捕获日志输出进行验证

### 测试用例12: 模型字段验证日志记录
- **测试用例描述**: 验证模型字段验证失败时是否记录相应的错误日志
- **测试用例输入**: 
  ```python
  from interfaces import AgentResult
  # 尝试创建一个字段验证失败的实例
  result = AgentResult(status="INVALID_STATUS", output={"thought": "test", "intent": {"content": "test"}})
  ```
- **测试用例预期输出**: 应该记录字段验证错误的日志信息
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 

### 测试用例13: 分布式追踪功能验证
- **测试用例描述**: 验证模型实例化时是否正确创建分布式追踪span
- **测试用例输入**: 
  ```python
  from LoggingService.sdk import TracerContextManager
  from interfaces import ContextBuildConfig
  import uuid
  
  with TracerContextManager.start_trace("test_trace"):
      config = ContextBuildConfig(task_id=uuid.uuid4(), include_metadata=True)
  ```
- **测试用例预期输出**: 在追踪输出中应能看到ContextBuildConfig实例化对应的span信息
- **测试用例实际输出**: 
- **测试用例结果**: 
- **测试用例备注**: 需要验证追踪上下文的正确传播