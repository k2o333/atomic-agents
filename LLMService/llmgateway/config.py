import os
from typing import Optional


class LLMConfig:
    """LLM服务配置管理类"""
    
    def __init__(self):
        """初始化配置，从环境变量加载"""
        # OpenAI配置
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
        self.openai_base_url: str = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        
        # 默认模型配置
        self.default_model: str = os.getenv('DEFAULT_LLM_MODEL', 'gpt-4o-mini')
        
    def validate(self) -> bool:
        """
        验证必要配置是否完整
        
        Returns:
            bool: 配置是否有效
        """
        # 检查OpenAI API Key
        if not self.openai_api_key:
            return False
            
        return True
        
    def get_openai_config(self) -> dict:
        """
        获取OpenAI配置
        
        Returns:
            dict: OpenAI配置字典
        """
        return {
            'api_key': self.openai_api_key,
            'base_url': self.openai_base_url
        }