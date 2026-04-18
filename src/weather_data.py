# weather_data.py
#
# A tiny in-memory weather store so the demo runs without any API key.
# In a real app you would replace `get_mock_weather` with a call to
# OpenWeatherMap, WeatherAPI, or similar.
#
# ─── STUDENT EXERCISE ────────────────────────────────────────────────────────
# 1. Add a few more cities to WEATHER_DB.
# 2. Add a "wind_speed_mph" field to every entry and return it from
#    get_mock_weather so the server can expose it.
# ─────────────────────────────────────────────────────────────────────────────

WEATHER_DB: dict[str, dict] = {
    "san francisco": {
        "city": "San Francisco",
        "temperature_f": 62,
        "condition": "Foggy",
        "humidity_pct": 85,
    },
    "new york": {
        "city": "New York",
        "temperature_f": 55,
        "condition": "Partly Cloudy",
        "humidity_pct": 60,
    },
    "miami": {
        "city": "Miami",
        "temperature_f": 88,
        "condition": "Sunny",
        "humidity_pct": 75,
    },
    "chicago": {
        "city": "Chicago",
        "temperature_f": 45,
        "condition": "Windy",
        "humidity_pct": 55,
    },
    "seattle": {
        "city": "Seattle",
        "temperature_f": 50,
        "condition": "Rainy",
        "humidity_pct": 90,
    },
    "austin": {
        "city": "Austin",
        "temperature_f": 78,
        "condition": "Clear",
        "humidity_pct": 40,
    },
}


def get_mock_weather(city: str) -> dict | None:
    """Return mock weather for *city*, or None if the city is not in the DB.

    The lookup is case-insensitive so "San Francisco" and "san francisco"
    both work.
    """
    return WEATHER_DB.get(city.lower().strip())


def list_cities() -> list[str]:
    """Return the canonical city names the mock DB knows about."""
    return [entry["city"] for entry in WEATHER_DB.values()]
