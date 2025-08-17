import tiktoken
from typing import List, Union
from .interfaces import OpenAICompatibleRequest, OpenAICompatibleResponse


class Tokenizer:
    """Token计数器"""
    
    def __init__(self):
        """初始化Tokenizer"""
        # 初始化tiktoken编码器
        self.encoders = {
            "gpt-4": tiktoken.encoding_for_model("gpt-4"),
            "gpt-4o": tiktoken.encoding_for_model("gpt-4o"),
            "gpt-4o-mini": tiktoken.encoding_for_model("gpt-4o-mini"),
            "gpt-3.5-turbo": tiktoken.encoding_for_model("gpt-3.5-turbo"),
        }
        
    def _get_encoder(self, model: str):
        """
        获取指定模型的编码器
        
        Args:
            model: 模型名称
            
        Returns:
            tiktoken.Encoding: 编码器
        """
        # 尝试精确匹配
        if model in self.encoders:
            return self.encoders[model]
            
        # 尝试前缀匹配
        for model_prefix, encoder in self.encoders.items():
            if model.startswith(model_prefix):
                return encoder
                
        # 默认使用gpt-4o-mini编码器
        return self.encoders["gpt-4o-mini"]
        
    def estimate_tokens(self, request: OpenAICompatibleRequest) -> int:
        """
        估算请求中的Token数量
        
        Args:
            request: OpenAI兼容的请求对象
            
        Returns:
            int: 估算的Token数量
        """
        encoder = self._get_encoder(request.model)
        token_count = 0
        
        # 计算消息中的Token
        for message in request.messages:
            # 角色Token
            token_count += len(encoder.encode(message.role))
            
            # 内容Token
            if isinstance(message.content, str):
                token_count += len(encoder.encode(message.content))
            elif isinstance(message.content, list):
                # 处理多模态内容
                for content_item in message.content:
                    if content_item.get("type") == "text":
                        token_count += len(encoder.encode(content_item.get("text", "")))
                        
        # 计算工具定义中的Token（如果存在）
        if request.tools:
            for tool in request.tools:
                function_def = tool.function
                # 函数名
                token_count += len(encoder.encode(function_def.get("name", "")))
                # 函数描述
                token_count += len(encoder.encode(function_def.get("description", "")))
                # 参数定义
                if "parameters" in function_def:
                    token_count += len(encoder.encode(str(function_def["parameters"])))
                    
        # 添加额外的Token（角色标记、分隔符等）
        token_count += 3  # 每条消息大约需要3个额外Token
        token_count += len(request.messages) * 5  # 每条消息额外增加5个Token
        
        return token_count
        
    def count_tokens_from_response(self, response: OpenAICompatibleResponse) -> int:
        """
        从响应中计算完成部分的Token数量
        
        Args:
            response: OpenAI兼容的响应对象
            
        Returns:
            int: 完成部分的Token数量
        """
        encoder = self._get_encoder(response.model)
        token_count = 0
        
        # 计算完成内容中的Token
        for choice in response.choices:
            if "message" in choice:
                message = choice["message"]
                if "content" in message and message["content"]:
                    token_count += len(encoder.encode(message["content"]))
                # 计算工具调用的Token
                if "tool_calls" in message:
                    for tool_call in message["tool_calls"]:
                        token_count += len(encoder.encode(str(tool_call)))
            elif "delta" in choice:
                delta = choice["delta"]
                if "content" in delta and delta["content"]:
                    token_count += len(encoder.encode(delta["content"]))
                    
        return token_count