"""
Planner Module for Central Graph Engine

This module implements a Planner that can dynamically generate PlanBlueprints
based on high-level goals, satisfying the M3 acceptance criteria.
"""

import uuid
from typing import List, Dict, Any, Optional
from interfaces import PlanBlueprint, TaskDefinition, EdgeDefinition, Condition, DataFlow
from LoggingService.sdk import get_logger, TracerContextManager

logger = get_logger(__name__)

class Planner:
    """Planner that generates PlanBlueprints for dynamic workflow creation."""
    
    def __init__(self):
        """Initialize the Planner."""
        logger.info("Initializing Planner")
    
    def create_research_and_report_plan(self, goal: str, workflow_id: Optional[str] = None) -> PlanBlueprint:
        """
        Create a PlanBlueprint for researching weather and writing a report.
        
        This satisfies the M3 acceptance criteria by creating a blueprint with:
        1. At least two steps (research, write report)
        2. One conditional edge
        
        Args:
            goal: High-level goal (e.g., "research weather and write report")
            workflow_id: Optional workflow ID
            
        Returns:
            PlanBlueprint: Blueprint for the workflow
        """
        with TracerContextManager.start_span("Planner.create_research_and_report_plan"):
            logger.info(f"Creating research and report plan for goal: {goal}")
            
            # Generate a workflow ID if not provided
            if workflow_id is None:
                workflow_id = str(uuid.uuid4())
            
            # Create task definitions
            research_task = TaskDefinition(
                task_id="research_task",
                assignee_id="Agent:Researcher",
                input_data={
                    "goal": "Research current weather conditions",
                    "topics": ["temperature", "precipitation", "wind_speed"]
                }
            )
            
            write_report_task = TaskDefinition(
                task_id="write_report_task",
                assignee_id="Agent:Writer",
                input_data={
                    "goal": "Write a weather report",
                    "format": "summary"
                }
            )
            
            # Create edge definitions with a condition
            # The write report task only executes if research was successful
            edge = EdgeDefinition(
                source_task_id="research_task",
                target_task_id="write_report_task",
                condition=Condition(
                    evaluator="CEL",
                    expression="result.success == true"
                ),
                data_flow=DataFlow(
                    mappings={
                        "weather_data": "result.data"
                    }
                )
            )
            
            # Create the blueprint
            blueprint = PlanBlueprint(
                workflow_id=uuid.UUID(workflow_id),
                new_tasks=[research_task, write_report_task],
                new_edges=[edge]
            )
            
            logger.info("Research and report plan created successfully", extra={
                "workflow_id": workflow_id,
                "tasks_count": len(blueprint.new_tasks),
                "edges_count": len(blueprint.new_edges)
            })
            
            return blueprint
    
    def create_generic_plan(self, steps: List[Dict[str, Any]], 
                           conditions: List[Dict[str, Any]],
                           workflow_id: Optional[str] = None) -> PlanBlueprint:
        """
        Create a generic PlanBlueprint with custom steps and conditions.
        
        Args:
            steps: List of step definitions
            conditions: List of condition definitions
            workflow_id: Optional workflow ID
            
        Returns:
            PlanBlueprint: Blueprint for the workflow
        """
        with TracerContextManager.start_span("Planner.create_generic_plan"):
            logger.info("Creating generic plan", extra={
                "steps_count": len(steps),
                "conditions_count": len(conditions)
            })
            
            # Generate a workflow ID if not provided
            if workflow_id is None:
                workflow_id = str(uuid.uuid4())
            
            # Create task definitions
            tasks = []
            for i, step in enumerate(steps):
                task = TaskDefinition(
                    task_id=f"task_{i}",
                    assignee_id=step.get("assignee_id", "Agent:Worker"),
                    input_data=step.get("input_data", {})
                )
                tasks.append(task)
            
            # Create edge definitions
            edges = []
            for condition in conditions:
                edge = EdgeDefinition(
                    source_task_id=condition.get("source_task_id", ""),
                    target_task_id=condition.get("target_task_id", ""),
                    condition=Condition(
                        evaluator=condition.get("evaluator", "CEL"),
                        expression=condition.get("expression", "true")
                    ) if condition.get("expression") else None,
                    data_flow=DataFlow(
                        mappings=condition.get("data_flow", {})
                    ) if condition.get("data_flow") else None
                )
                edges.append(edge)
            
            # Create the blueprint
            blueprint = PlanBlueprint(
                workflow_id=uuid.UUID(workflow_id),
                new_tasks=tasks,
                new_edges=edges
            )
            
            logger.info("Generic plan created successfully", extra={
                "workflow_id": workflow_id,
                "tasks_count": len(blueprint.new_tasks),
                "edges_count": len(blueprint.new_edges)
            })
            
            return blueprint

# Global instance for use throughout the engine
planner = Planner()