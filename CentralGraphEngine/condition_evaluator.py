"""
Condition Evaluator for Central Graph Engine

This module provides a ConditionEvaluator that can evaluate Edge conditions
using a safe expression evaluation library.
"""

from typing import Dict, Any, Optional
from simpleeval import simple_eval
from interfaces import Condition
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class ConditionEvaluator:
    """Evaluator for Edge conditions using CEL-like expressions."""
    
    def __init__(self):
        """Initialize the ConditionEvaluator with safe evaluation settings."""
        logger.info("ConditionEvaluator initialized")
    
    def evaluate(self, condition: Optional[Condition], context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition against the provided context.
        
        Args:
            condition: The condition to evaluate (can be None)
            context: The context data to evaluate against
            
        Returns:
            bool: True if condition is satisfied or if no condition is provided, False otherwise
        """
        # If no condition is provided, default to True (always pass)
        if condition is None:
            logger.debug("No condition provided, returning True")
            return True
            
        # Only handle CEL evaluator type for now
        if condition.evaluator != 'CEL':
            logger.warning(f"Unsupported evaluator type: {condition.evaluator}")
            return False
            
        try:
            # Prepare the evaluation context
            # Allow access to the 'result' variable by wrapping the context
            eval_context = context.copy() if context else {}
            
            # If the context has a 'result' key, make it accessible as 'result'
            # Otherwise, if the context itself represents the result, wrap it
            if 'result' not in eval_context and context:
                eval_context['result'] = context
            
            # Add boolean constants for CEL-like expressions
            eval_context['true'] = True
            eval_context['false'] = False
            
            # Use simple_eval to safely evaluate the expression
            # The context is passed as names that can be referenced in the expression
            result = simple_eval(condition.expression, names=eval_context)
            
            # Convert result to boolean
            bool_result = bool(result)
            logger.debug(f"Condition '{condition.expression}' evaluated to {bool_result}")
            return bool_result
            
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition.expression}': {str(e)}")
            # In case of evaluation error, default to False for safety
            return False

# Global instance for use throughout the engine
condition_evaluator = ConditionEvaluator()