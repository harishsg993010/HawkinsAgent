"""Weather data tool implementation using OpenWeatherMap API"""

import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import os
from .base import BaseTool
from ..types import ToolResponse

logger = logging.getLogger(__name__)

class WeatherTool(BaseTool):
    """Tool for fetching weather data using OpenWeatherMap API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the weather tool

        Args:
            api_key: OpenWeatherMap API key. If not provided, will try to get from environment.
        """
        super().__init__(name="weather")
        self.api_key = api_key or os.environ.get("OPENWEATHERMAP_API_KEY")
        if not self.api_key:
            logger.warning("No OpenWeatherMap API key provided")
        self.BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Get current weather data for specified city"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate weather query parameters

        Args:
            params: Dictionary containing query parameters

        Returns:
            True if parameters are valid, False otherwise
        """
        if not isinstance(params.get('query'), str):
            logger.error("Query must be a string")
            return False

        # Query should be in format: "city_name,country_code"
        parts = params['query'].split(',')
        if len(parts) != 2:
            logger.error("Query must be in format: city_name,country_code")
            return False

        if not self.api_key:
            logger.error("OpenWeatherMap API key not provided")
            return False

        return True

    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the weather query

        Args:
            **kwargs: Must include query parameter with format:
                     "city_name,country_code"
                     Example: "London,GB" or "Paris,FR"

        Returns:
            ToolResponse containing weather data or error
        """
        try:
            # Extract and validate parameters
            query = kwargs.get("query", "")
            logger.info(f"Processing weather query: {query}")

            if not self.validate_params({"query": query}):
                return ToolResponse(
                    success=False,
                    error="Invalid parameters or missing API key. Required format: city_name,country_code (e.g. London,GB)",
                    result=None
                )

            # Parse query parameters
            city_name, country_code = [part.strip() for part in query.split(',')]

            logger.info(f"Fetching weather data for {city_name}, {country_code}")
            logger.debug(f"Using API key: {'*' * 4}{self.api_key[-4:]}")

            # Make API request
            try:
                response = requests.get(
                    self.BASE_URL,
                    params={
                        "q": f"{city_name},{country_code}",
                        "units": "metric",  # Use metric units
                        "appid": self.api_key
                    },
                    timeout=10  # Add timeout
                )

                response.raise_for_status()  # Raise exception for bad status codes

            except requests.exceptions.RequestException as e:
                error_msg = f"Weather API request failed: {str(e)}"
                logger.error(error_msg)
                return ToolResponse(
                    success=False,
                    error=error_msg,
                    result=None
                )

            # Parse response
            data = response.json()
            logger.debug(f"Received weather data: {data}")

            # Extract relevant information
            try:
                weather_info = {
                    "temperature": round(data["main"]["temp"], 1),  # Celsius
                    "humidity": data["main"]["humidity"],  # Percentage
                    "description": data["weather"][0]["description"],
                    "wind_speed": round(data["wind"]["speed"], 1),  # meters/sec
                    "feels_like": round(data["main"]["feels_like"], 1),  # Celsius
                    "pressure": data["main"]["pressure"],  # hPa
                }

                logger.info(f"Successfully retrieved weather data for {city_name}")
                logger.debug(f"Processed weather info: {weather_info}")

                return ToolResponse(
                    success=True,
                    result=weather_info,
                    error=None
                )

            except KeyError as e:
                error_msg = f"Invalid response format from weather API: {str(e)}"
                logger.error(error_msg)
                return ToolResponse(
                    success=False,
                    result=None,
                    error=error_msg
                )

        except Exception as e:
            error_msg = f"Weather query failed: {str(e)}"
            logger.error(error_msg)
            return ToolResponse(
                success=False,
                result=None,
                error=error_msg
            )