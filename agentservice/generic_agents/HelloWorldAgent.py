"""
Hello World Agent

A simple agent that returns a hard-coded "Hello World!" response.
Used for testing and validating the Agent Service execution environment.
"""

from interfaces import AgentResult, FinalAnswer, AgentIntent

class HelloWorldAgent:
    def run(self, task_data):
        """
        Simple implementation that returns a hard-coded result.
        
        Args:
            task_data: Input data for the agent (unused in this simple implementation)
            
        Returns:
            AgentResult: A success result with a "Hello World!" final answer
        """
        intent = FinalAnswer(content="Hello World!")
        output = AgentIntent(
            thought="This is a simple Hello World agent for testing connectivity.",
            intent=intent
        )
        return AgentResult(status="SUCCESS", output=output)