import logging
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from .config import LLMConfig
from .interfaces import OpenAICompatibleRequest, OpenAICompatibleResponse
from .tokenizer import Tokenizer
from .tool_adapter import ToolAdapter
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# 配置日志
logger = logging.getLogger(__name__)


class LLMGatewayService:
    """LLM网关服务核心类"""
    
    def __init__(self):
        """初始化服务"""
        self.config = LLMConfig()
        self.tokenizer = Tokenizer()
        
        # 验证配置
        if not self.config.validate():
            raise ValueError("LLM配置验证失败")
            
        # 初始化HTTP客户端
        self.http_client = httpx.AsyncClient(
            base_url=self.config.get_openai_config()['base_url'],
            headers={
                'Authorization': f"Bearer {self.config.get_openai_config()['api_key']}",
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )
        
    async def chat_completion(self, request: OpenAICompatibleRequest) -> OpenAICompatibleResponse:
        """
        统一的聊天补全接口
        
        Args:
            request: OpenAI兼容的请求对象
            
        Returns:
            OpenAICompatibleResponse: OpenAI兼容的响应对象
        """
        # Token计数
        prompt_tokens = self.tokenizer.estimate_tokens(request)
        
        # 调用OpenAI API
        response_data = await self._call_openai_api(request)
        
        # 解析响应并添加Token使用量
        response = OpenAICompatibleResponse(**response_data)
        response.usage.prompt_tokens = prompt_tokens
        response.usage.completion_tokens = self.tokenizer.count_tokens_from_response(response)
        response.usage.total_tokens = response.usage.prompt_tokens + response.usage.completion_tokens
        
        return response
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException))
    )
    async def _call_openai_api(self, request: OpenAICompatibleRequest) -> Dict[str, Any]:
        """
        调用OpenAI API
        
        Args:
            request: OpenAI兼容的请求对象
            
        Returns:
            Dict[str, Any]: API响应数据
            
        Raises:
            httpx.HTTPStatusError: HTTP状态错误
            httpx.NetworkError: 网络错误
            httpx.TimeoutException: 超时错误
        """
        # 转换请求格式
        payload = {
            "model": request.model,
            "messages": [msg.dict(exclude_none=True) for msg in request.messages],
            "stream": request.stream
        }
        
        # 添加可选参数
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.tools:
            payload["tools"] = [tool.dict() for tool in request.tools]
        if request.tool_choice:
            payload["tool_choice"] = request.tool_choice
            
        try:
            # 发送请求
            response = await self.http_client.post("/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API调用失败: {e.response.status_code} - {e.response.text}")
            raise
        except (httpx.NetworkError, httpx.TimeoutException) as e:
            logger.error(f"OpenAI API网络错误: {str(e)}")
            raise