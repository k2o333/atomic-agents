# interfaces.py
from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from uuid import UUID

# Import LoggingService SDK
try:
    from LoggingService.sdk import get_logger, TracerContextManager
    logger = get_logger(__name__)
except ImportError:
    # Fallback if LoggingService is not available
    import logging
    logger = logging.getLogger(__name__)
    # Mock TracerContextManager if not available
    class TracerContextManager:
        @staticmethod
        def start_trace(name: str):
            from contextlib import nullcontext
            return nullcontext()
        
        @staticmethod
        def start_span(name: str):
            from contextlib import nullcontext
            return nullcontext()

# --- FORWARD DECLARATIONS ---
# Pydantic v2 supports string forward references for self-referencing models
TaskDefinition = "TaskDefinition"

# --- 2.4. TASK DIRECTIVES ---
class Condition(BaseModel):
    evaluator: Literal['CEL']
    expression: str
    
    def __init__(self, **data):
        with TracerContextManager.start_span("Condition.__init__"):
            logger.info("Initializing Condition", extra={"evaluator": data.get("evaluator")})
            super().__init__(**data)
            logger.info("Condition initialized successfully", extra={"evaluator": self.evaluator})

class LoopDirective(BaseModel):
    type: Literal['PARALLEL_ITERATION', 'SERIAL_ITERATION']
    iteration_input_key: str
    input_source_task_id: str
    task_template: TaskDefinition
    max_iterations: Optional[int] = None
    
    def __init__(self, **data):
        with TracerContextManager.start_span("LoopDirective.__init__"):
            logger.info("Initializing LoopDirective", extra={"type": data.get("type")})
            super().__init__(**data)
            logger.info("LoopDirective initialized successfully", extra={"type": self.type})

class TaskDirectives(BaseModel):
    loop_directive: Optional[LoopDirective] = None
    on_failure: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[int] = None
    human_interaction: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        with TracerContextManager.start_span("TaskDirectives.__init__"):
            logger.info("Initializing TaskDirectives")
            super().__init__(**data)
            logger.info("TaskDirectives initialized successfully")

# --- 2.1. PLAN BLUEPRINT ---
class DataFlow(BaseModel):
    mappings: Dict[str, str]
    
    def __init__(self, **data):
        with TracerContextManager.start_span("DataFlow.__init__"):
            logger.info("Initializing DataFlow", extra={"mappings_count": len(data.get("mappings", {}))})
            super().__init__(**data)
            logger.info("DataFlow initialized successfully", extra={"mappings_count": len(self.mappings)})

class ContextOverrides(BaseModel):
    priority: Literal['NORMAL', 'HIGHEST'] = 'NORMAL'
    include_assets: Optional[List[Dict[str, Any]]] = None
    include_task_results: Optional[List[str]] = None
    ad_hoc_text: Optional[str] = None
    override_context_config: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        with TracerContextManager.start_span("ContextOverrides.__init__"):
            logger.info("Initializing ContextOverrides", extra={"priority": data.get("priority")})
            super().__init__(**data)
            logger.info("ContextOverrides initialized successfully", extra={"priority": self.priority})

class TaskDefinition(BaseModel):
    task_id: str
    parent_task_id: Optional[str] = None
    input_data: Dict[str, Any]
    assignee_id: str
    context_overrides: Optional[ContextOverrides] = None
    directives: Optional[TaskDirectives] = None
    
    def __init__(self, **data):
        with TracerContextManager.start_span("TaskDefinition.__init__"):
            logger.info("Initializing TaskDefinition", extra={
                "task_id": data.get("task_id"),
                "assignee_id": data.get("assignee_id")
            })
            super().__init__(**data)
            logger.info("TaskDefinition initialized successfully", extra={
                "task_id": self.task_id,
                "assignee_id": self.assignee_id
            })

class EdgeDefinition(BaseModel):
    source_task_id: str
    target_task_id: str
    condition: Optional[Condition] = None
    data_flow: Optional[DataFlow] = None
    
    def __init__(self, **data):
        with TracerContextManager.start_span("EdgeDefinition.__init__"):
            logger.info("Initializing EdgeDefinition", extra={
                "source_task_id": data.get("source_task_id"),
                "target_task_id": data.get("target_task_id")
            })
            super().__init__(**data)
            logger.info("EdgeDefinition initialized successfully", extra={
                "source_task_id": self.source_task_id,
                "target_task_id": self.target_task_id
            })

class TaskUpdate(BaseModel):
    task_id: UUID
    new_input_data: Optional[Dict[str, Any]] = None
    new_status: Optional[str] = None
    
    def __init__(self, **data):
        with TracerContextManager.start_span("TaskUpdate.__init__"):
            logger.info("Initializing TaskUpdate", extra={"task_id": str(data.get("task_id"))})
            super().__init__(**data)
            logger.info("TaskUpdate initialized successfully", extra={"task_id": str(self.task_id)})

class PlanBlueprint(BaseModel):
    workflow_id: Optional[UUID] = None
    new_tasks: List[TaskDefinition] = []
    new_edges: List[EdgeDefinition] = []
    update_tasks: List[TaskUpdate] = []
    
    def __init__(self, **data):
        with TracerContextManager.start_span("PlanBlueprint.__init__"):
            logger.info("Initializing PlanBlueprint", extra={"data": data})
            super().__init__(**data)
            logger.info("PlanBlueprint initialized successfully", extra={"workflow_id": self.workflow_id})

# --- 2.2. AGENT RESULT ---
class FinalAnswer(BaseModel):
    content: Any

class ToolCallRequest(BaseModel):
    tool_id: str
    arguments: Dict[str, Any]

class AgentIntent(BaseModel):
    thought: str
    intent: Union[FinalAnswer, ToolCallRequest, PlanBlueprint]

class FailureDetails(BaseModel):
    type: Literal['LLM_REFUSAL', 'TOOL_EXECUTION_FAILED', 'VALIDATION_ERROR', 'RESOURCE_UNAVAILABLE']
    message: str

class ToolResult(BaseModel):
    status: Literal['SUCCESS', 'FAILURE']
    output: Optional[Any] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    post_execution_plan: Optional[PlanBlueprint] = None

class AgentResult(BaseModel):
    status: Literal['SUCCESS', 'FAILURE']
    output: AgentIntent
    failure_details: Optional[FailureDetails] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        with TracerContextManager.start_span("AgentResult.__init__"):
            logger.info("Initializing AgentResult", extra={"status": data.get("status")})
            super().__init__(**data)
            logger.info("AgentResult initialized successfully", extra={"status": self.status})

# --- 2.3. CONTEXT BUILD CONFIG ---
class ContextBuildConfig(BaseModel):
    task_id: UUID
    include_metadata: bool = True
    include_tool_list: bool = True
    conversation_history_config: Optional[Dict[str, Any]] = None
    task_list_config: Optional[Dict[str, Any]] = None
    artifact_config: Optional[Dict[str, Any]] = None
    experience_config: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        with TracerContextManager.start_span("ContextBuildConfig.__init__"):
            logger.info("Initializing ContextBuildConfig", extra={"task_id": str(data.get("task_id"))})
            super().__init__(**data)
            logger.info("ContextBuildConfig initialized successfully", extra={"task_id": str(self.task_id)})

# --- 2.5. HUMAN INTERVENTION ---
class InterventionRequest(BaseModel):
    intervention_type: Literal['ROLLBACK_AND_MODIFY', 'PAUSE', 'RESUME']
    target_task_id: UUID
    rollback_to_version: Optional[int] = None
    new_input_data: Optional[Dict[str, Any]] = None
    new_assignee_id: Optional[str] = None
    comment: str
    
    def __init__(self, **data):
        with TracerContextManager.start_span("InterventionRequest.__init__"):
            logger.info("Initializing InterventionRequest", extra={
                "intervention_type": data.get("intervention_type"),
                "target_task_id": str(data.get("target_task_id"))
            })
            super().__init__(**data)
            logger.info("InterventionRequest initialized successfully", extra={
                "intervention_type": self.intervention_type,
                "target_task_id": str(self.target_task_id)
            })

# Pydantic v2 needs this for self-referencing models
TaskDefinition.model_rebuild()
LoopDirective.model_rebuild()