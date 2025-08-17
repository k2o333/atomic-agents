"""
Tracing Integration for Persistence Service

This module provides helper functions for integrating with the Logging & Tracing Service.
"""

from typing import Dict, Any
from LoggingService.sdk import inject_trace_context, extract_trace_context, get_current_trace_id, get_current_span_id

def get_trace_context() -> Dict[str, str]:
    """Get the current trace context for propagation."""
    return inject_trace_context()

def set_trace_context(context_dict: Dict[str, str]) -> None:
    """Set the trace context from a dictionary."""
    extract_trace_context(context_dict)

def get_trace_ids() -> Dict[str, str]:
    """Get the current trace and span IDs."""
    return {
        "trace_id": get_current_trace_id() or "",
        "span_id": get_current_span_id() or ""
    }