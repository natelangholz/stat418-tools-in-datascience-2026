from __future__ import annotations

from typing import Any

import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODE_LABELS = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    80: "rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    95: "thunderstorm",
}


PRODUCTS = [
    {"name": "Laptop Pro 14", "category": "laptop", "price": 1499},
    {"name": "Notebook Air 13", "category": "laptop", "price": 999},
    {"name": "Noise Canceling Headphones", "category": "audio", "price": 299},
    {"name": "Mechanical Keyboard", "category": "accessory", "price": 129},
]


def get_weather(location: str) -> dict[str, Any]:
    """Get live weather data for a city using the Open-Meteo geocoding and forecast APIs."""
    geo_response = requests.get(
        GEOCODING_URL,
        params={"name": location, "count": 1, "language": "en", "format": "json"},
        timeout=30,
    )
    geo_response.raise_for_status()
    geo_payload = geo_response.json()

    results = geo_payload.get("results", [])
    if not results:
        raise ValueError(f"Could not geocode location: {location}")

    match = results[0]
    latitude = match["latitude"]
    longitude = match["longitude"]

    forecast_response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
        },
        timeout=30,
    )
    forecast_response.raise_for_status()
    forecast_payload = forecast_response.json()

    current = forecast_payload.get("current", {})
    weather_code = current.get("weather_code")
    wind_speed_mph = current.get("wind_speed_10m")

    return {
        "location": match["name"],
        "region": match.get("admin1"),
        "country": match.get("country"),
        "temp_f": current.get("temperature_2m"),
        "conditions": WEATHER_CODE_LABELS.get(weather_code, f"weather code {weather_code}"),
        "wind_speed_mph": wind_speed_mph,
    }


def search_database(query: str) -> list[dict[str, Any]]:
    """Search a tiny in-memory product catalog."""
    normalized = query.strip().lower()
    return [
        product
        for product in PRODUCTS
        if normalized in product["name"].lower() or normalized in product["category"].lower()
    ]


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city using a live weather API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name to look up"},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search a small product database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term"},
                },
                "required": ["query"],
            },
        },
    },
]


TOOLS = {
    "get_weather": get_weather,
    "search_database": search_database,
}

