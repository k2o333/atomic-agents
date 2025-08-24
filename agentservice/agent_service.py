"""
Agent Service

This module provides the core functionality for executing Agents in the Synapse platform.
It handles agent loading, context building, execution, and result validation.
"""

import importlib
import logging
from typing import Dict, Any, Optional
from interfaces import AgentResult, PlanBlueprint
from agentservice.base_agent import BaseAgent


class ContextBuilder:
    """
    Context Builder component responsible for pre-building context for agents.
    
    This component implements the complete context building lifecycle:
    1. Parses agent's context_config
    2. Pulls data from underlying services (PersistenceService, etc.)
    3. Executes prompt fusion
    4. Injects global constraints
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def build_context(self, agent_config: Dict[str, Any], task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build context for an agent based on its configuration.
        
        Args:
            agent_config: The agent's configuration from capabilities.json
            task_data: The current task data
            
        Returns:
            Dict[str, Any]: The built context
        """
        self.logger.info("Building context for agent")
        
        # Extract context config
        context_config = agent_config.get('context_config', {})
        
        # Build the context (this is a simplified implementation)
        context = {
            'agent_config': agent_config,
            'task_data': task_data,
            'context_config': context_config
        }
        
        # In a full implementation, this would:
        # 1. Pull data from PersistenceService based on context_config
        # 2. Apply global constraints
        # 3. Prepare assets and artifacts
        # 4. Build conversation history
        
        self.logger.info("Context built successfully")
        return context


class AgentService:
    """
    Agent Service - The execution runtime for all Agents in the Synapse platform.
    
    Responsibilities:
    1. Dynamic Agent loading based on capabilities.json
    2. Context building before agent execution
    3. Agent execution
    4. Result validation and standardization
    5. Planner agent support
    6. Prompt fusion strategy implementation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.context_builder = ContextBuilder()
        self.agent_factory = AgentFactory()
    
    def execute_agent(self, agent_id: str, task_data: Dict[str, Any], 
                     agent_registry: Dict[str, Any]) -> AgentResult:
        """
        Execute an agent by its ID with the provided task data.
        
        Args:
            agent_id: The ID of the agent to execute
            task_data: The task data to pass to the agent
            agent_registry: The registry of available agents
            
        Returns:
            AgentResult: The result of the agent execution
        """
        self.logger.info(f"Executing agent: {agent_id}")
        
        try:
            # 1. Look up agent configuration
            agent_config = self._get_agent_config(agent_id, agent_registry)
            if not agent_config:
                raise ValueError(f"Agent with ID '{agent_id}' not found in registry")
            
            # 2. Check for context_config and build context if needed
            context_config = agent_config.get('context_config')
            if context_config:
                self.logger.info("Building context for agent")
                built_context = self.context_builder.build_context(agent_config, task_data)
                # Merge the built context with task_data
                task_data_with_context = {**task_data, 'context': built_context}
            else:
                task_data_with_context = task_data
            
            # 3. Create agent instance
            agent_instance = self.agent_factory.create_agent(agent_config, task_data_with_context)
            
            # 4. Execute agent
            result_dict = agent_instance.run()
            
            # 5. Validate and convert result
            result = self._validate_and_convert_result(result_dict, agent_config)
            
            # 6. Additional validation for Planner agents
            if agent_config.get('role') == 'PLANNER':
                self._validate_planner_result(result, agent_config)
            
            self.logger.info(f"Agent {agent_id} executed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
            # Return a standardized failure result
            return AgentResult(
                status="FAILURE",
                output={
                    "thought": "Agent service encountered an error during execution.",
                    "intent": {
                        "content": f"Agent execution failed: {str(e)}"
                    }
                },
                failure_details={
                    "type": "VALIDATION_ERROR",
                    "message": str(e)
                }
            )
    
    def _get_agent_config(self, agent_id: str, agent_registry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get agent configuration from the registry.
        
        Args:
            agent_id: The ID of the agent
            agent_registry: The registry of available agents
            
        Returns:
            Optional[Dict[str, Any]]: The agent configuration or None if not found
        """
        # Handle both formats: with 'capabilities' key and without
        if 'capabilities' in agent_registry:
            agents = agent_registry['capabilities']
        else:
            agents = agent_registry.get('agents', [])
        
        for agent in agents:
            if agent.get('id') == agent_id:
                return agent
        return None
    
    def _validate_and_convert_result(self, result_dict: Dict, agent_config: Dict[str, Any]) -> AgentResult:
        """
        Validate and convert the result dictionary to an AgentResult object.
        
        Args:
            result_dict: The result dictionary from the agent
            agent_config: The agent configuration
            
        Returns:
            AgentResult: The validated and converted result
        """
        # Convert dict to AgentResult object
        if isinstance(result_dict, dict):
            return AgentResult(**result_dict)
        elif isinstance(result_dict, AgentResult):
            return result_dict
        else:
            raise ValueError("Agent result must be a dict or AgentResult object")
    
    def _validate_planner_result(self, result: AgentResult, agent_config: Dict[str, Any]) -> None:
        """
        Validate that a Planner agent's result is valid.
        
        Args:
            result: The AgentResult from the planner
            agent_config: The agent configuration
            
        Raises:
            ValueError: If the result is invalid for a Planner agent
        """
        # Check that only Planner agents can return PlanBlueprint intents
        if agent_config.get('role') != 'PLANNER':
            if hasattr(result.output.intent, 'new_tasks') or hasattr(result.output.intent, 'new_edges'):
                raise ValueError("Only Planner agents (role: PLANNER) can return PlanBlueprint intents")


class AgentFactory:
    """
    Agent Factory responsible for creating Agent instances based on capability definitions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_agent(self, agent_config: Dict[str, Any], task_data: Dict[str, Any]) -> BaseAgent:
        """
        Create an agent instance based on its configuration.
        
        Args:
            agent_config: The agent's configuration from capabilities.json
            task_data: The task data to pass to the agent
            
        Returns:
            BaseAgent: An instance of the agent
        """
        implementation_path = agent_config.get('implementation_path')
        if not implementation_path:
            raise ValueError("Agent configuration must include 'implementation_path'")
        
        # Split the implementation path to get module and class names
        module_path, class_name = implementation_path.rsplit('.', 1)
        
        try:
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the class
            agent_class = getattr(module, class_name)
            
            # Create an instance of the agent
            # Check if it's a Planner agent that might need group_config
            group_config = task_data.get('group_config')
            if agent_config.get('role') == 'PLANNER' and group_config:
                return agent_class(agent_config, task_data, group_config)
            else:
                return agent_class(agent_config, task_data)
                
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to load agent from {implementation_path}: {str(e)}")