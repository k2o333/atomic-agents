"""
Hello World Agent

A simple agent that returns a hard-coded "Hello World!" response.
Used for testing and validating the Agent Service execution environment.
"""

from agentservice.baseagent.base_agent import BaseAgent
from interfaces import AgentResult, FinalAnswer, AgentIntent


class HelloWorldAgent(BaseAgent):
    def __init__(self, agent_config=None, task_data=None, group_config=None):
        """
        Initialize the HelloWorldAgent.
        
        Args:
            agent_config: The agent's configuration from capabilities.json
            task_data: The current task data including context
            group_config: Optional group configuration for Planner agents
        """
        # Call the parent constructor if config is provided
        if agent_config is not None:
            super().__init__(agent_config, task_data or {}, group_config)
    
    def _generate_dynamic_prompt(self) -> str:
        """
        Generate a dynamic prompt for the agent.
        
        Returns:
            str: The dynamic prompt
        """
        return "Return a simple 'Hello World!' response."
    
    def _handle_llm_response(self, llm_response: dict) -> dict:
        """
        Handle the LLM response.
        
        Args:
            llm_response: The response from the LLM call
            
        Returns:
            dict: An AgentResult dictionary
        """
        return self.create_final_answer(
            thought="Handled LLM response for HelloWorld agent.",
            content="Hello World!"
        )
    
    def run(self, task_data=None):
        """
        Simple implementation that returns a hard-coded result.
        
        Args:
            task_data: Input data for the agent (unused in this simple implementation)
            
        Returns:
            AgentResult: A success result with a "Hello World!" final answer
        """
        # If called directly (not through the AgentService), use the simple implementation
        if task_data is None and not hasattr(self, 'agent_config'):
            intent = FinalAnswer(content="Hello World!")
            output = AgentIntent(
                thought="This is a simple Hello World agent for testing connectivity.",
                intent=intent
            )
            return AgentResult(status="SUCCESS", output=output)
        
        # If called through the AgentService, use the parent implementation
        return super().run()