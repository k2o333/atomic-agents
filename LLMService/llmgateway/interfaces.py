from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class OpenAICompatibleMessage(BaseModel):
    """OpenAI兼容的消息格式"""
    role: str
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None
    tool_call_id: Optional[str] = None


class OpenAICompatibleTool(BaseModel):
    """OpenAI兼容的工具格式"""
    type: str = "function"
    function: Dict[str, Any]


class OpenAICompatibleRequest(BaseModel):
    """OpenAI兼容的请求格式"""
    model: str
    messages: List[OpenAICompatibleMessage]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tools: Optional[List[OpenAICompatibleTool]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None


class OpenAICompatibleUsage(BaseModel):
    """OpenAI兼容的用量格式"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OpenAICompatibleResponse(BaseModel):
    """OpenAI兼容的响应格式"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: OpenAICompatibleUsage
    system_fingerprint: Optional[str] = None