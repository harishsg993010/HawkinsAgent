"""Multi-agent system for planning a 4-day Chennai-Golden Triangle-Chennai trip"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import WebSearchTool, WeatherTool
from hawkins_agent.llm import LiteLLMProvider
import logging
import os
import asyncio
import json
from datetime import datetime, timedelta

# API keys setup
os.environ["OPENAI_API_KEY"]=""
os.environ["TAVILY_API_KEY"]=""

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TripFlow:
    """Flow manager for 4-day Chennai-Golden Triangle trip planning"""
    
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
    """Plan a 4-day trip (3 nights) from Chennai covering Golden Triangle within ₹50,000 for 4 people"""
    try:
        # Initialize tools
        logger.info("Initializing tools...")
        weather_tool = WeatherTool()
        search_tool = WebSearchTool(api_key=os.environ.get("TAVILY_API_KEY"))

        # Create travel agent for flight bookings
        travel_agent = (AgentBuilder("travel_agent")
                     .with_model("gpt-4o")
                     .with_provider(LiteLLMProvider, temperature=0.6)
                     .with_tool(search_tool)
                     .build())

        # Create research agent for destination info
        researcher = (AgentBuilder("destination_researcher")
                    .with_model("gpt-4o")
                    .with_provider(LiteLLMProvider, temperature=0.7)
                    .with_tool(search_tool)
                    .build())

        # Create activity planner agent with budget constraints
        activity_planner = (AgentBuilder("activity_planner")
                         .with_model("gpt-4o")
                         .with_provider(LiteLLMProvider, temperature=0.8)
                         .build())

        # Create logistics agent with focus on budget management
        logistics_agent = (AgentBuilder("logistics_planner")
                        .with_model("gpt-4o")
                        .with_provider(LiteLLMProvider, temperature=0.6)
                        .with_tool(weather_tool)
                        .build())

        async def plan_travel(input_data, previous_results):
            """Plan Chennai-Delhi-Chennai travel"""
            logger.info("Planning Chennai-Delhi travel arrangements...")
            
            response = await travel_agent.process(
                "Research and recommend flight options for 4 people:\n"
                "1. Chennai to Delhi (Day 1 early morning)\n"
                "2. Delhi to Chennai (Day 4 evening)\n"
                "Consider:\n"
                "- Budget airlines with best rates\n"
                "- Early morning arrival in Delhi on Day 1\n"
                "- Late evening departure from Delhi on Day 4\n"
                "- Airport transfers in both cities\n"
                "Total trip budget: ₹50,000 for 4 people"
            )
            
            return {
                'content': response.message,
                'travel_plan': response.metadata.get('travel_plan', {})
            }

        async def research_step(input_data, previous_results):
            """Research Golden Triangle destinations and key information"""
            logger.info("Researching Delhi, Agra, and Jaipur...")
            
            travel_info = previous_results['travel']['content']
            response = await researcher.process(
                f"Based on travel arrangements: {travel_info}\n"
                "Research for 3-night Golden Triangle tour for 4 people with rental cab:\n"
                "1. Must-visit monuments and attractions\n"
                "2. Car rental services in Delhi for Golden Triangle circuit\n"
                "3. Budget accommodation for 3 nights\n"
                "4. Local food recommendations\n"
                "5. Best driving routes: Delhi-Agra-Jaipur-Delhi\n"
                "6. Parking availability at hotels and attractions\n"
                "7. Toll charges and fuel costs estimation\n"
                "Consider remaining budget after flight bookings from total ₹50,000"
            )
            
            return {
                'content': response.message,
                'destinations': response.metadata.get('destinations', [])
            }

        async def plan_activities(input_data, previous_results):
            """Plan activities for 4 days within budget"""
            logger.info("Planning daily activities...")
            
            research = previous_results['research']['content']
            travel_info = previous_results['travel']['content']
            response = await activity_planner.process(
                f"Based on travel arrangements: {travel_info}\n"
                f"And research: {research}\n"
                "Create a detailed 4-day Golden Triangle itinerary with rental car:\n"
                "Day 1: - Early morning flight from Chennai to Delhi\n"
                "       - Pick up rental car from Delhi airport\n"
                "       - Delhi sightseeing by car (optimized route)\n"
                "       - Night in Delhi\n"
                "Day 2: - Early morning drive to Agra (via Yamuna Expressway)\n"
                "       - Taj Mahal and Agra Fort visits\n"
                "       - Optional evening visit to Mehtab Bagh\n"
                "       - Night in Agra\n"
                "Day 3: - Morning drive to Jaipur (via state highway)\n"
                "       - En-route stop at Fatehpur Sikri (optional)\n"
                "       - Afternoon/evening Jaipur sightseeing\n"
                "       - Night in Jaipur\n"
                "Day 4: - Morning sightseeing in Jaipur\n"
                "       - Post-lunch drive to Delhi Airport\n"
                "       - Return rental car\n"
                "       - Evening flight to Chennai\n"
                "Include:\n"
                "1. Optimal driving routes\n"
                "2. Parking locations\n"
                "3. Major toll points\n"
                "4. Fuel stops\n"
                "5. Budget-friendly activities and costs"
            )
            
            return {
                'content': response.message,
                'itinerary': response.metadata.get('itinerary', {})
            }

        async def plan_logistics(input_data, previous_results):
            """Plan accommodation, transportation, and budget allocation"""
            logger.info("Planning logistics and budget...")
            
            travel_info = previous_results['travel']['content']
            research = previous_results['research']['content']
            activities = previous_results['activities']['content']
            
            # Check weather for trip dates
            start_date = datetime.now() + timedelta(days=30)
            
            response = await logistics_agent.process(
                f"Based on travel arrangements: {travel_info}\n"
                f"Research information: {research}\n"
                f"And planned activities: {activities}\n"
                "Provide detailed logistics for 4 people, 4 days (3 nights) with rental cab:\n"
                "1. Budget breakdown for:\n"
                "   - Flights (Chennai-Delhi-Chennai)\n"
                "   - Rental car (4-day SUV/MPV rental)\n"
                "   - Fuel costs for entire circuit\n"
                "   - Toll charges\n"
                "   - 3 nights accommodation (Delhi, Agra, Jaipur)\n"
                "   - Food and drinks\n"
                "   - Entry tickets\n"
                "   - Driver allowance if required\n"
                "2. Recommended rental car services in Delhi\n"
                "3. Recommended budget hotels with parking\n"
                "4. Estimated driving times:\n"
                "   - Delhi Airport to hotel\n"
                "   - Delhi to Agra\n"
                "   - Agra to Jaipur\n"
                "   - Jaipur to Delhi Airport\n"
                "5. Money-saving strategies\n"
                "6. Essential packing list\n"
                "7. Parking and toll information\n"
                "Total budget: ₹50,000"
            )
            
            return {
                'content': response.message,
                'logistics': response.metadata.get('logistics', {})
            }

        # Configure flow
        flow = TripFlow()
        flow.add_step('travel', plan_travel)
        flow.add_step('research', research_step, ['travel'])
        flow.add_step('activities', plan_activities, ['travel', 'research'])
        flow.add_step('logistics', plan_logistics, ['travel', 'research', 'activities'])

        # Execute flow
        logger.info("\nStarting Chennai-Golden Triangle trip planning...")
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
