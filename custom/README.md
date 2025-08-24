# Custom Weather Agent and Tool

This directory contains a custom implementation of a Weather Agent and a weather search tool for the Synapse platform.

## Components

### 1. search_weather.py
A simple tool that can call a public weather API to get weather information.
- **Function**: `search_weather(city: str)`
- **Parameters**: 
  - `city`: The city name to search for weather information
- **Returns**: A dictionary with weather information

### 2. WeatherAgent.py
A custom Agent that inherits from BaseAgent and can search for weather information.
- **Class**: `WeatherAgent`
- **Key Methods**:
  - `_generate_dynamic_prompt()`: Generates a dynamic prompt for the LLM
  - `_handle_llm_response()`: Handles LLM responses to determine if tools need to be called
  - `_handle_reentry()`: Handles re-entry after tool calls to process results

### 3. capabilities.json
Updated to register:
- `custom.search_weather` tool
- `WeatherAgent` agent

## Implementation Details

The WeatherAgent follows the standard agent pattern:
1. Generate a dynamic prompt for the LLM
2. Handle LLM responses to determine if tools need to be called
3. Process tool results and generate final answers

## Testing

Run the test script to verify the implementation:
```bash
/root/projects/atom_agents/myenv311/bin/python custom/test_weather_agent.py
```

## Usage

The WeatherAgent can be assigned to tasks with goals like "北京今天天气怎么样？" (How is the weather in Beijing today?). It will:
1. Request an LLM call to analyze the task
2. Parse the LLM response to determine if a weather search is needed
3. Call the search_weather tool if needed
4. Process the tool results and generate a final natural language answer