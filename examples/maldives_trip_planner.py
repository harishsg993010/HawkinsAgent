"""Multi-agent system for planning a Maldives trip"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import WebSearchTool, WeatherTool
from hawkins_agent.llm import LiteLLMProvider
import logging
import os
import asyncio
import json
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TripFlow:
    """Simple flow manager for trip planning"""
    
    def __init__(self):
        self.steps = []
        
    def add_step(self, name, func, requires=None):
        self.steps.append({
            'name': name,
            'func': func,
            'requires': requires or []
        })
        
    async def execute(self, input_data):
        results = {}
        for step in self.steps:
            try:
                # Check requirements
                for req in step['requires']:
                    if req not in results:
                        raise Exception(f"Required step {req} not completed")
                
                # Execute step
                logger.info(f"Executing step: {step['name']}")
                result = await step['func'](input_data, results)
                results[step['name']] = result
                
            except Exception as e:
                logger.error(f"Error in step {step['name']}: {str(e)}")
                results[step['name']] = {'error': str(e)}
                
        return results

async def main():
    """Plan a 5-day Maldives trip using multiple specialized agents"""
    try:
        # Initialize tools
        logger.info("Initializing tools...")
        weather_tool = WeatherTool()
        search_tool = WebSearchTool(api_key=os.environ.get("TAVILY_API_KEY"))

        # Create research agent for destination info
        logger.info("Creating agents...")
        researcher = (AgentBuilder("destination_researcher")
                    .with_model("gpt-4o")
                    .with_provider(LiteLLMProvider, temperature=0.7)
                    .with_tool(search_tool)
                    .build())

        # Create activity planner agent
        activity_planner = (AgentBuilder("activity_planner")
                         .with_model("gpt-4o")
                         .with_provider(LiteLLMProvider, temperature=0.8)
                         .build())

        # Create logistics agent
        logistics_agent = (AgentBuilder("logistics_planner")
                        .with_model("gpt-4o")
                        .with_provider(LiteLLMProvider, temperature=0.6)
                        .with_tool(weather_tool)
                        .build())

        async def research_step(input_data, previous_results):
            """Research Maldives destinations and key information"""
            logger.info("Researching Maldives destinations...")
            
            response = await researcher.process(
                "Research the best areas to stay in Maldives for a 5-day trip, "
                "including popular resorts, must-visit locations, and travel tips. "
                "Focus on practical information for trip planning."
            )
            
            return {
                'content': response.message,
                'destinations': response.metadata.get('destinations', [])
            }

        async def plan_activities(input_data, previous_results):
            """Plan daily activities for 5 days"""
            logger.info("Planning daily activities...")
            
            research = previous_results['research']['content']
            response = await activity_planner.process(
                f"Based on this research: {research}\n"
                "Create a detailed 5-day itinerary for the Maldives with specific "
                "activities for each day. Include water sports, relaxation time, "
                "and cultural experiences. Format as a day-by-day schedule."
            )
            
            return {
                'content': response.message,
                'itinerary': response.metadata.get('itinerary', {})
            }

        async def plan_logistics(input_data, previous_results):
            """Plan accommodation and transportation"""
            logger.info("Planning logistics...")
            
            research = previous_results['research']['content']
            activities = previous_results['activities']['content']
            
            # Check weather for trip dates
            start_date = datetime.now() + timedelta(days=30)  # Plan for next month
            weather_query = f"Male,MV"  # Capital city as reference
            
            response = await logistics_agent.process(
                f"Based on the research: {research}\n"
                f"And planned activities: {activities}\n"
                "Provide detailed logistics planning including:\n"
                "1. Recommended resorts/hotels\n"
                "2. Transportation between islands\n"
                "3. Estimated costs\n"
                "4. Booking tips"
            )
            
            return {
                'content': response.message,
                'logistics': response.metadata.get('logistics', {})
            }

        # Configure flow
        flow = TripFlow()
        flow.add_step('research', research_step)
        flow.add_step('activities', plan_activities, ['research'])
        flow.add_step('logistics', plan_logistics, ['research', 'activities'])

        # Execute flow
        logger.info("\nStarting Maldives trip planning...")
        logger.info("=" * 50)

        results = await flow.execute({})

        # Display results
        logger.info("\nTrip Planning Results:")
        logger.info("=" * 50)

        for step_name, result in results.items():
            logger.info(f"\n{step_name.upper()}:")
            logger.info("-" * 40)
            if 'error' in result:
                logger.error(f"Error in {step_name}: {result['error']}")
            else:
                logger.info(result['content'])

    except Exception as e:
        logger.error(f"Error in trip planning: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
