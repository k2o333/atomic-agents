"""
Tool Arguments Validator

This module provides functionality to validate tool arguments against
their defined JSON schema.
"""

from typing import Dict, Any
from dataclasses import dataclass
import jsonschema
from LoggingService.sdk import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Validation result."""
    is_valid: bool
    error_message: str = ""


class ToolValidator:
    """Tool arguments validator."""
    
    @staticmethod
    def validate_arguments(arguments: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """
        校验参数是否符合schema定义。
        
        Args:
            arguments: 要校验的参数字典
            schema: JSON Schema定义
            
        Returns:
            ValidationResult: 校验结果
        """
        logger.info("Validating tool arguments", extra={
            "arguments_keys": list(arguments.keys()),
            "schema_keys": list(schema.get("properties", {}).keys()) if isinstance(schema, dict) else []
        })
        
        try:
            # 如果没有定义schema，则认为校验通过
            if not schema:
                logger.info("No schema defined, validation passed")
                return ValidationResult(is_valid=True)
            
            # 使用jsonschema进行校验
            jsonschema.validate(instance=arguments, schema=schema)
            logger.info("Arguments validation passed")
            return ValidationResult(is_valid=True)
            
        except jsonschema.ValidationError as e:
            error_message = f"Validation failed: {e.message} at {e.json_path}"
            logger.error("Arguments validation failed", extra={"error": error_message})
            return ValidationResult(is_valid=False, error_message=error_message)
            
        except Exception as e:
            error_message = f"Validation error: {str(e)}"
            logger.error("Arguments validation error", extra={"error": error_message})
            return ValidationResult(is_valid=False, error_message=error_message)


# 全局函数，方便调用
def validate_arguments(arguments: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
    """全局函数，用于校验参数"""
    return ToolValidator.validate_arguments(arguments, schema)