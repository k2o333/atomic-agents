"""
Weather Search Tool

A simple tool that can call a public weather API to get weather information.
"""

import requests
import os
from typing import Dict, Any


def search_weather(city: str) -> Dict[str, Any]:
    """
    Search for weather information for a given city.
    
    Args:
        city: The city name to search for weather information
        
    Returns:
        A dictionary with weather information
    """
    try:
        # For demonstration purposes, we'll return mock data
        # In a real implementation, you would call an actual weather API
        # like OpenWeatherMap, WeatherAPI, etc.
        
        # Mock weather data
        weather_data = {
            "city": city,
            "temperature": 25,  # degrees Celsius
            "description": "Sunny",
            "humidity": 60,  # percentage
            "wind_speed": 10,  # km/h
        }
        
        return {
            "status": "success",
            "data": weather_data,
            "message": f"Weather information for {city} retrieved successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve weather information: {str(e)}"
        }