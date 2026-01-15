import logging
import os
import json

from langchain_core.tools import tool
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from phoenix.otel import register
from phoenix.trace.langchain import LangChainInstrumentor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

tracer_provider = register(auto_instrument=True)
LangChainInstrumentor().instrument()

@tool
def get_weather(city: str) -> str:
    """Useful for getting the current weather in a specific city."""
    # 1. Clean the input: remove whitespace and punctuation like '??' or '.'
    clean_city = city.strip("?!. ").title() 
    
    logger.info(f"Tool Call: get_weather | Original: '{city}' | Cleaned: '{clean_city}'")
    
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        weather = OpenWeatherMapAPIWrapper(openweathermap_api_key=api_key)
        data = weather.run(clean_city)
        
        logger.info(f"Weather data retrieved for {clean_city}")
        return data
        
    except Exception as e:
        # If the API still can't find it, provide a graceful fallback
        logger.error(f"Error in get_weather tool: {str(e)}")
        return f"I'm sorry, I couldn't find weather information for '{clean_city}'. Please check the spelling."

@tool
def get_calendar(principal: float, rate: float, years: int) -> str:
    """Calculates compound interest for an investment."""
    amount = principal * (1 + (rate / 100)) ** years
    return f"After {years} years, your investment will be worth {amount:.2f}."

# Create a dictionary for easy access in the router
TOOLS = {
    "weather": get_weather,
    "calendar": get_calendar
}