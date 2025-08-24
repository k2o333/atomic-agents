"""
Weather Agent

A custom Agent that can search for weather information.
"""

import json
from typing import Dict, Any
from agents.base_agent import BaseAgent
from interfaces import ToolCallRequest


class WeatherAgent(BaseAgent):
    """
    WeatherAgent is a custom agent that can search for weather information.
    
    It follows the standard agent pattern:
    1. Generate a dynamic prompt for the LLM
    2. Handle LLM responses to determine if tools need to be called
    3. Process tool results and generate final answers
    """
    
    def _generate_dynamic_prompt(self) -> str:
        """
        Generate a dynamic prompt for the LLM to determine if weather search is needed.
        
        Returns:
            str: The dynamic prompt string
        """
        task_goal = self.task_data.get('goal', 'Unknown task')
        
        prompt = f"""
You are a weather assistant. Your task is to help users get weather information.

Task: {task_goal}

Please analyze the task and determine if you need to search for weather information.
If you need to search for weather information, respond with a JSON object in this format:
{{"action": "search_weather", "city": "city_name"}}

If you can answer the question directly without searching, respond with a JSON object in this format:
{{"action": "final_answer", "content": "your_answer"}}

Examples:
1. For "What's the weather like in Beijing today?" -> {{"action": "search_weather", "city": "Beijing"}}
2. For "Is it raining in Shanghai?" -> {{"action": "search_weather", "city": "Shanghai"}}
3. For "How does weather search work?" -> {{"action": "final_answer", "content": "I can search for weather information for any city. Just ask me about the weather in a specific location."}}
"""
        return prompt
    
    def _handle_llm_response(self, llm_response: Dict) -> Dict:
        """
        Handle the LLM response to determine next action.
        
        Args:
            llm_response: The response from the LLM call
            
        Returns:
            Dict: An AgentResult dictionary
        """
        try:
            # Extract the content from the LLM response
            if isinstance(llm_response, dict) and 'content' in llm_response:
                response_content = llm_response['content']
            else:
                response_content = str(llm_response)
            
            # Try to parse the response as JSON
            try:
                response_json = json.loads(response_content)
            except json.JSONDecodeError:
                # If not valid JSON, treat as a direct answer
                return self.create_final_answer(
                    thought="LLM provided a direct answer",
                    content=response_content
                )
            
            action = response_json.get('action')
            
            if action == 'search_weather':
                city = response_json.get('city')
                if not city:
                    return self.create_failure_response(
                        type="VALIDATION_ERROR",
                        message="City name is required for weather search"
                    )
                
                # Request the weather search tool
                return self.request_tool_call(
                    tool_id="custom.search_weather",
                    arguments={"city": city}
                )
                
            elif action == 'final_answer':
                content = response_json.get('content', 'No answer provided')
                return self.create_final_answer(
                    thought="LLM provided a final answer",
                    content=content
                )
                
            else:
                return self.create_failure_response(
                    type="VALIDATION_ERROR",
                    message=f"Unknown action: {action}"
                )
                
        except Exception as e:
            return self.create_failure_response(
                type="AGENT_EXECUTION_ERROR",
                message=f"Failed to process LLM response: {str(e)}"
            )
    
    def _handle_reentry(self) -> Dict:
        """
        Handle re-entry after an LLM or Tool call.
        
        Returns:
            Dict: An AgentResult dictionary
        """
        # Check if we have a Tool result to process
        last_tool_result = self.get_last_tool_result()
        if last_tool_result:
            # Process the tool result and generate final answer
            try:
                tool_output = last_tool_result.get('output', {})
                if isinstance(tool_output, dict) and tool_output.get('status') == 'success':
                    weather_data = tool_output.get('data', {})
                    city = weather_data.get('city', 'Unknown')
                    temperature = weather_data.get('temperature', 'Unknown')
                    description = weather_data.get('description', 'Unknown')
                    humidity = weather_data.get('humidity', 'Unknown')
                    wind_speed = weather_data.get('wind_speed', 'Unknown')
                    
                    final_answer = f"{city} today's weather: {description}, Temperature: {temperature}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} km/h."
                    
                    return self.create_final_answer(
                        thought="Processed weather data from tool result",
                        content=final_answer
                    )
                else:
                    error_message = tool_output.get('message', 'Unknown error')
                    return self.create_final_answer(
                        thought="Tool execution failed",
                        content=f"Failed to get weather information: {error_message}"
                    )
            except Exception as e:
                return self.create_failure_response(
                    type="AGENT_EXECUTION_ERROR",
                    message=f"Failed to process tool result: {str(e)}"
                )
        
        # Check if we have an LLM response to process
        last_llm_response = self.get_last_llm_response()
        if last_llm_response:
            return self._handle_llm_response(last_llm_response)
        
        # If neither, this is unexpected - return failure
        return self.create_failure_response(
            type="REENTRY_ERROR",
            message="Re-entry detected but no LLM response or Tool result found."
        )