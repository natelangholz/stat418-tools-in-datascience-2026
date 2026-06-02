from __future__ import annotations

import requests
from fastmcp import FastMCP


mcp = FastMCP("demo-tools")

PRODUCTS = [
    {"id": 1, "name": "Laptop Pro 14", "category": "laptop", "price": 1499},
    {"id": 2, "name": "Notebook Air 13", "category": "laptop", "price": 999},
    {"id": 3, "name": "Study Tablet", "category": "tablet", "price": 599},
    {"id": 4, "name": "Campus Phone", "category": "phone", "price": 799},
]

USERS = {
    "alice": {
        "name": "Alice",
        "plan": "premium",
        "email": "alice@example.com",
        "city": "Los Angeles",
    },
    "bob": {
        "name": "Bob",
        "plan": "free",
        "email": "bob@example.com",
        "city": "San Francisco",
    },
}


def _lookup_coordinates(city: str) -> tuple[float, float, str]:
    geocode_response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=30,
    )
    geocode_response.raise_for_status()
    geocode_data = geocode_response.json()
    results = geocode_data.get("results", [])
    if not results:
        raise ValueError(f"Could not find coordinates for city: {city}")

    first_match = results[0]
    return (
        first_match["latitude"],
        first_match["longitude"],
        first_match["name"],
    )


def _weather_code_to_description(code: int) -> str:
    weather_map = {
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
        80: "slight rain showers",
        81: "moderate rain showers",
        82: "violent rain showers",
        95: "thunderstorm",
    }
    return weather_map.get(code, f"weather code {code}")


@mcp.tool
def search_database(query: str, limit: int = 10) -> list[dict]:
    """Search a tiny in-memory product database by product name or category."""
    normalized = query.strip().lower()
    return [
        product
        for product in PRODUCTS
        if normalized in product["name"].lower() or normalized in product["category"].lower()
    ][:limit]


@mcp.tool
def get_user_info(username: str) -> dict:
    """Get information about a known demo user, including their city."""
    normalized = username.strip().lower()
    if normalized not in USERS:
        raise ValueError(f"Unknown user: {username}")
    return USERS[normalized]


@mcp.tool
def get_weather(city: str) -> dict:
    """Get current weather for a city using the Open-Meteo API."""
    latitude, longitude, resolved_city = _lookup_coordinates(city)

    forecast_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m,weather_code",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
        },
        timeout=30,
    )
    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()
    current = forecast_data["current"]

    return {
        "city": resolved_city,
        "temperature_f": current["temperature_2m"],
        "wind_speed_mph": current["wind_speed_10m"],
        "conditions": _weather_code_to_description(current["weather_code"]),
    }


@mcp.tool
def send_notification(username: str, message: str) -> dict:
    """Simulate sending a notification to a known demo user."""
    normalized = username.strip().lower()
    if normalized not in USERS:
        raise ValueError(f"Unknown user: {username}")

    return {
        "status": "sent",
        "username": normalized,
        "message": message,
        "delivery_target": USERS[normalized]["email"],
    }


if __name__ == "__main__":
    mcp.run()


