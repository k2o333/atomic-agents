# Agent Service

## Module Overview

The Agent Service is a core component responsible for instantiating and executing Agent scripts. It acts as the execution environment for all Agent logic, dynamically loading and running Agent implementations based on capability definitions.

## HelloWorldAgent

A simple agent that returns a hard-coded "Hello World!" response for testing connectivity.

### Usage

The HelloWorldAgent can be executed through the Agent Service by referencing its capability ID `hello_world_agent`.

### Expected Output

When executed, the agent will return:
```json
{
  "status": "SUCCESS",
  "output": {
    "thought": "This is a simple Hello World agent for testing connectivity.",
    "intent": {
      "content": "Hello World!"
    }
  }
}
```