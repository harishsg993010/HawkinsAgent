"""Flow control module for managing agent interactions"""

from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
import logging
from .agent import Agent
from .types import AgentResponse

logger = logging.getLogger(__name__)

@dataclass
class FlowStep:
    """Represents a step in the agent workflow
    
    Attributes:
        name: Name of the step
        agent: Agent responsible for this step
        process: Function to process the step's input
        requires: List of step names that must complete before this step
    """
    name: str
    agent: Agent
    process: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    requires: List[str] = None

class FlowManager:
    """Manages workflow between multiple agents
    
    This class handles:
    - Step dependencies and execution order
    - Data passing between steps
    - Error handling and recovery
    """
    
    def __init__(self):
        """Initialize the flow manager"""
        self.steps: Dict[str, FlowStep] = {}
        self.results: Dict[str, Dict[str, Any]] = {}
        
    def add_step(self, step: FlowStep) -> "FlowManager":
        """Add a step to the workflow
        
        Args:
            step: Step configuration to add
            
        Returns:
            Self for chaining
        """
        self.steps[step.name] = step
        return self
        
    async def execute(self, initial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the complete workflow
        
        Args:
            initial_data: Initial data to pass to the first step
            
        Returns:
            Combined results from all steps
        """
        try:
            self.results = {}
            data = initial_data or {}
            
            # Find steps with no dependencies
            available = [
                name for name, step in self.steps.items()
                if not step.requires
            ]
            
            while available:
                # Execute available steps
                for step_name in available[:]:
                    step = self.steps[step_name]
                    
                    try:
                        logger.info(f"Executing step: {step_name}")
                        result = await step.process(data)
                        self.results[step_name] = result
                        data.update(result)
                        available.remove(step_name)
                        
                    except Exception as e:
                        logger.error(f"Error in step {step_name}: {str(e)}")
                        raise
                        
                # Find newly available steps
                for name, step in self.steps.items():
                    if (name not in self.results and  # Not completed
                        name not in available and    # Not already queued
                        step.requires and           # Has dependencies
                        all(req in self.results for req in step.requires)):  # All deps met
                        available.append(name)
                        
            return self.results
            
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            raise
