# Logging & Tracing Service SDK

from typing import Generator, Dict, Optional
import logging
import contextvars
import uuid
from contextlib import contextmanager

# --- 1. Context Management (Simplified M1 Version) ---
# M1阶段，tracer.py 可以简化为 ContextVar 的封装
_trace_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("trace_id", default=None)
_span_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("span_id", default=None)

def generate_id() -> str:
    """生成一个唯一的ID，不带连字符，符合W3C Trace Context标准"""
    return str(uuid.uuid4()).replace('-', '')

def get_current_trace_id() -> Optional[str]:
    """获取当前上下文中的 trace_id"""
    return _trace_id_ctx.get()

def get_current_span_id() -> Optional[str]:
    """获取当前上下文中的 span_id"""
    return _span_id_ctx.get()

# --- 2. Tracer Context Manager (Simple Implementation for M1) ---
class TracerContextManager:
    """
    一个简单的追踪上下文管理器，用于M1阶段。
    为每个追踪和跨度生成唯一的ID，并管理其生命周期。
    """
    @staticmethod
    @contextmanager
    def start_trace(name: str) -> Generator[None, None, None]:
        """
        开始一个新的分布式追踪。
        """
        trace_id = generate_id()
        token = _trace_id_ctx.set(trace_id)
        # 对于新的 trace，span_id 也从头开始
        span_token = _span_id_ctx.set(trace_id) # 根 span 的 id 通常与 trace_id 相同或相关
        try:
            logger = get_logger(__name__)
            logger.info(f"Trace '{name}' started", extra={"event": "trace_start"})
            yield
        finally:
            logger.info(f"Trace '{name}' ended", extra={"event": "trace_end"})
            _span_id_ctx.reset(span_token)
            _trace_id_ctx.reset(token)

    @staticmethod
    @contextmanager
    def start_span(name: str) -> Generator[None, None, None]:
        """
        在当前追踪下开始一个新的跨度 (Span)。
        """
        span_id = generate_id()
        parent_span_id = get_current_span_id()
        token = _span_id_ctx.set(span_id)
        try:
            logger = get_logger(__name__)
            logger.info(f"Span '{name}' started", extra={"event": "span_start", "parent_span_id": parent_span_id})
            yield
        finally:
            logger.info(f"Span '{name}' ended", extra={"event": "span_end"})
            _span_id_ctx.reset(token)

# --- 3. Trace Context Propagation (M1 Implementation) ---
def inject_trace_context() -> Dict[str, str]:
    """
    将当前的追踪上下文 (trace_id, span_id) 序列化为一个字典。
    遵循简化版的 W3C Trace Context 格式。
    """
    trace_id = get_current_trace_id()
    span_id = get_current_span_id()
    
    if trace_id and span_id:
        # 简化版的 traceparent 格式: "00-{trace_id}-{span_id}-01"
        # 版本-跟踪ID-父ID-追踪标识
        # trace_id 和 span_id 必须是不带'-'的十六进制字符串
        traceparent = f"00-{trace_id}-{span_id}-01"
        return {"traceparent": traceparent}
    return {}

def extract_trace_context(context_dict: Dict[str, str]) -> None:
    """
    从一个字典中提取追踪上下文 (trace_id, span_id) 并设置到当前的ContextVar中。
    期望输入格式: {"traceparent": "00-{trace_id}-{span_id}-01"}
    其中 trace_id 和 span_id 是不带'-'的十六进制字符串。
    """
    traceparent = context_dict.get("traceparent")
    if traceparent:
        try:
            # 限制分割次数为3，这样 parts[1] 是完整的 trace_id, parts[2] 是完整的 span_id
            parts = traceparent.split('-', 3)
            if len(parts) >= 4 and parts[0] == "00": # 检查版本
                trace_id = parts[1]
                span_id = parts[2]
                # 设置上下文
                _trace_id_ctx.set(trace_id)
                _span_id_ctx.set(span_id)
        except (IndexError, ValueError):
            # 如果解析失败，忽略或记录警告
            # logger.warning(f"Failed to parse trace context from {traceparent}")
            pass

# --- 4. Structured Logger with Trace ID Injection ---
from pythonjsonlogger import jsonlogger

class TraceInjectingJsonFormatter(jsonlogger.JsonFormatter):
    """
    自定义的 JSON 格式化器，自动注入 trace_id 和 span_id。
    """
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        # 注入 trace_id 和 span_id
        log_record['trace_id'] = get_current_trace_id() or ""
        log_record['span_id'] = get_current_span_id() or ""

def get_logger(name: str) -> logging.Logger:
    """
    获取一个已配置为输出结构化JSON日志并自动注入追踪ID的Logger实例。
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加 handler
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        
        # 创建并设置自定义格式化器
        formatter = TraceInjectingJsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
    return logger