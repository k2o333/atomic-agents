"""
Generic Planner Agent

A generic planner agent that can be configured via capabilities.json to generate plan blueprints.
"""

from agentservice.baseagent.base_agent import BaseAgent
from interfaces import PlanBlueprint, TaskDefinition, EdgeDefinition
from typing import Dict, Any, List


class GenericPlannerAgent(BaseAgent):
    """
    A generic planner agent that generates workflow plans based on user requests.
    """
    
    def _generate_dynamic_prompt(self) -> str:
        """
        Generate a dynamic prompt for the planner based on task data.
        
        Returns:
            str: The dynamic prompt for the planner
        """
        user_request = self.task_data.get('input_data', {}).get('request', 'No request provided')
        group_config = self.group_config or {}
        planner_prompt_template = group_config.get('planner_prompt_template', 
                                                  'Please create a plan for: {user_request}')
        
        # Format the prompt template with the user request
        return planner_prompt_template.format(
            user_request=user_request,
            team_list=self._get_available_teams()
        )
    
    def _get_available_teams(self) -> str:
        """
        Get a list of available teams from the group configuration.
        
        Returns:
            str: A formatted string of available teams
        """
        group_config = self.group_config or {}
        # In a real implementation, this would come from the system
        return "Research Team, Development Team, QA Team, Deployment Team"
    
    def _handle_llm_response(self, llm_response: Dict) -> Dict:
        """
        Handle the LLM response and convert it to a plan blueprint.
        
        Args:
            llm_response: The response from the LLM call
            
        Returns:
            Dict: An AgentResult dictionary with FinalAnswer intent
        """
        # In a real implementation, we would parse the LLM response
        # and convert it to a structured PlanBlueprint
        content = llm_response.get('content', 'Plan generated successfully')
        return self.create_final_answer(
            thought="Planner agent processed the LLM response and generated a plan.",
            content=content
        )
    
    def _generate_plan_blueprint(self) -> PlanBlueprint:
        """
        Generate a plan blueprint based on the user request.
        
        Returns:
            PlanBlueprint: The generated plan blueprint
        """
        # Extract the user request from task data
        user_request = self.task_data.get('input_data', {}).get('request', 'No request provided')
        
        # Create a simple plan with one task
        task = TaskDefinition(
            task_id="planned_task_1",
            input_data={"request": user_request},
            assignee_id="generic_worker"
        )
        
        # Create a plan blueprint with the task
        return PlanBlueprint(
            new_tasks=[task],
            new_edges=[]
        )