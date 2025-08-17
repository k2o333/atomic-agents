"""
Base Agent Class

This is the base class that all custom Agents should inherit from.
It provides common functionality and interfaces for Agent development.
"""

import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from interfaces import AgentResult, FinalAnswer, ToolCallRequest, AgentIntent


class BaseAgent(ABC):
    """
    BaseAgent is the foundation for all Agent implementations in the Synapse platform.
    
    It provides:
    1. Standard interfaces for Agent-System interactions
    2. Re-entry handling for LLM/Tool responses
    3. Helper methods for creating standardized intents
    """
    
    def __init__(self, agent_config: Dict[str, Any], task_data: Dict[str, Any], 
                 group_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the BaseAgent with configuration and task data.
        
        Args:
            agent_config: The agent's configuration from capabilities.json
            task_data: The current task data including context
            group_config: Optional group configuration for Planner agents
        """
        self.agent_config = agent_config
        self.task_data = task_data
        self.group_config = group_config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def run(self) -> Dict:
        """
        Main execution entry point for the agent.
        
        This method implements a template pattern:
        - On first run: generates prompt and requests LLM call
        - On re-entry: handles LLM/Tool responses
        
        Returns:
            Dict: An AgentResult dictionary conforming to the specification
        """
        self.logger.info("Agent execution started.")
        try:
            # Determine if this is the first run or a re-entry
            if self.is_first_run():
                # First execution: generate dynamic prompt and request LLM call
                dynamic_prompt = self._generate_dynamic_prompt()
                result = self.request_llm_call(dynamic_prompt)
            else:
                # Re-entry: handle LLM or Tool response
                result = self._handle_reentry()
            
            self.logger.info("Agent execution finished successfully.")
            return result
            
        except Exception as e:
            self.logger.error("Agent execution failed.", exc_info=True)
            return self.create_failure_response(
                type="AGENT_EXECUTION_ERROR", 
                message=str(e)
            )
    
    def _handle_reentry(self) -> Dict:
        """
        Handle re-entry after an LLM or Tool call.
        
        Returns:
            Dict: An AgentResult dictionary
        """
        # Check if we have an LLM response to process
        last_llm_response = self.get_last_llm_response()
        if last_llm_response:
            return self._handle_llm_response(last_llm_response)
        
        # Check if we have a Tool result to process
        last_tool_result = self.get_last_tool_result()
        if last_tool_result:
            # For now, we'll treat tool results similar to LLM responses
            # In a more complex implementation, we might have separate handling
            return self._handle_llm_response(last_tool_result)
        
        # If neither, this is unexpected - return failure
        return self.create_failure_response(
            type="REENTRY_ERROR",
            message="Re-entry detected but no LLM response or Tool result found."
        )
    
    @abstractmethod
    def _generate_dynamic_prompt(self) -> str:
        """
        Abstract method to generate the dynamic part of the prompt.
        
        This method must be implemented by subclasses to create
        agent-specific dynamic prompts based on task data.
        
        Returns:
            str: The dynamic prompt string
        """
        pass
    
    @abstractmethod
    def _handle_llm_response(self, llm_response: Dict) -> Dict:
        """
        Abstract method to handle LLM responses.
        
        This method must be implemented by subclasses to process
        LLM outputs and determine the next action.
        
        Args:
            llm_response: The response from the LLM call
            
        Returns:
            Dict: An AgentResult dictionary
        """
        pass
    
    def request_llm_call(self, prompt: str, tools: List = None) -> Dict:
        """
        Helper method to create a ToolCallRequest for System.LLM.invoke.
        
        Args:
            prompt: The prompt to send to the LLM
            tools: Optional list of tools to make available to the LLM
            
        Returns:
            Dict: An AgentResult dictionary with ToolCallRequest intent
        """
        arguments = {
            "prompt": prompt
        }
        
        if tools:
            arguments["tools"] = tools
            
        intent = ToolCallRequest(
            tool_id="System.LLM.invoke",
            arguments=arguments
        )
        
        output = AgentIntent(
            thought="Requesting LLM call to process the task.",
            intent=intent
        )
        
        return AgentResult(
            status="SUCCESS",
            output=output
        ).model_dump()
    
    def request_tool_call(self, tool_id: str, arguments: Dict) -> Dict:
        """
        Helper method to create a ToolCallRequest for any tool.
        
        Args:
            tool_id: The ID of the tool to call
            arguments: The arguments to pass to the tool
            
        Returns:
            Dict: An AgentResult dictionary with ToolCallRequest intent
        """
        intent = ToolCallRequest(
            tool_id=tool_id,
            arguments=arguments
        )
        
        output = AgentIntent(
            thought=f"Requesting tool call for {tool_id}.",
            intent=intent
        )
        
        return AgentResult(
            status="SUCCESS",
            output=output
        ).model_dump()
    
    def create_final_answer(self, thought: str, content: Any) -> Dict:
        """
        Helper method to create a FinalAnswer intent.
        
        Args:
            thought: The agent's reasoning/thought process
            content: The final answer content
            
        Returns:
            Dict: An AgentResult dictionary with FinalAnswer intent
        """
        intent = FinalAnswer(content=content)
        
        output = AgentIntent(
            thought=thought,
            intent=intent
        )
        
        return AgentResult(
            status="SUCCESS",
            output=output
        ).model_dump()
    
    def create_failure_response(self, type: str, message: str) -> Dict:
        """
        Helper method to create a standardized failure response.
        
        Args:
            type: The type of failure
            message: The failure message
            
        Returns:
            Dict: An AgentResult dictionary with FAILURE status
        """
        from interfaces import FailureDetails
        
        intent = FinalAnswer(content=f"Agent execution failed: {message}")
        
        output = AgentIntent(
            thought="Agent encountered an error during execution.",
            intent=intent
        )
        
        failure_details = FailureDetails(
            type=type,
            message=message
        )
        
        return AgentResult(
            status="FAILURE",
            output=output,
            failure_details=failure_details
        ).model_dump()
    
    def get_last_llm_response(self) -> Optional[Dict]:
        """
        Get the last LLM response from the task context.
        
        Returns:
            Optional[Dict]: The last LLM response or None if not available
        """
        context = self.task_data.get('context', {})
        return context.get('last_llm_response')
    
    def get_last_tool_result(self) -> Optional[Dict]:
        """
        Get the last tool result from the task context.
        
        Returns:
            Optional[Dict]: The last tool result or None if not available
        """
        context = self.task_data.get('context', {})
        return context.get('last_tool_result')
    
    def is_first_run(self) -> bool:
        """
        Determine if this is the first run of the agent.
        
        Returns:
            bool: True if this is the first run, False otherwise
        """
        # If there's no context or no previous results, it's the first run
        context = self.task_data.get('context', {})
        return not (context.get('last_llm_response') or context.get('last_tool_result'))