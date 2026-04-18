# solution/weather_data.py
#
# EXERCISE SOLUTIONS:
#   1. Added Denver, Los Angeles, Boston, Phoenix to WEATHER_DB
#   2. Added "wind_speed_mph" to every entry
#   3. Added FORECAST_DB for the get_forecast exercise in weather_server.py

WEATHER_DB: dict[str, dict] = {
    "san francisco": {
        "city": "San Francisco",
        "temperature_f": 62,
        "condition": "Foggy",
        "humidity_pct": 85,
        "wind_speed_mph": 12,
    },
    "new york": {
        "city": "New York",
        "temperature_f": 55,
        "condition": "Partly Cloudy",
        "humidity_pct": 60,
        "wind_speed_mph": 8,
    },
    "miami": {
        "city": "Miami",
        "temperature_f": 88,
        "condition": "Sunny",
        "humidity_pct": 75,
        "wind_speed_mph": 10,
    },
    "chicago": {
        "city": "Chicago",
        "temperature_f": 45,
        "condition": "Windy",
        "humidity_pct": 55,
        "wind_speed_mph": 22,
    },
    "seattle": {
        "city": "Seattle",
        "temperature_f": 50,
        "condition": "Rainy",
        "humidity_pct": 90,
        "wind_speed_mph": 7,
    },
    "austin": {
        "city": "Austin",
        "temperature_f": 78,
        "condition": "Clear",
        "humidity_pct": 40,
        "wind_speed_mph": 9,
    },
    # ── Added cities ──────────────────────────────────────────────────────────
    "denver": {
        "city": "Denver",
        "temperature_f": 52,
        "condition": "Sunny",
        "humidity_pct": 30,
        "wind_speed_mph": 14,
    },
    "los angeles": {
        "city": "Los Angeles",
        "temperature_f": 75,
        "condition": "Clear",
        "humidity_pct": 45,
        "wind_speed_mph": 6,
    },
    "boston": {
        "city": "Boston",
        "temperature_f": 48,
        "condition": "Cloudy",
        "humidity_pct": 70,
        "wind_speed_mph": 16,
    },
    "phoenix": {
        "city": "Phoenix",
        "temperature_f": 98,
        "condition": "Sunny",
        "humidity_pct": 10,
        "wind_speed_mph": 5,
    },
}

# Simple multi-day forecast data (used by get_forecast in weather_server.py)
FORECAST_DB: dict[str, list[dict]] = {
    "san francisco": [
        {"day": 1, "high_f": 63, "low_f": 55, "condition": "Foggy"},
        {"day": 2, "high_f": 65, "low_f": 54, "condition": "Partly Cloudy"},
        {"day": 3, "high_f": 68, "low_f": 56, "condition": "Sunny"},
        {"day": 4, "high_f": 60, "low_f": 52, "condition": "Foggy"},
        {"day": 5, "high_f": 62, "low_f": 53, "condition": "Partly Cloudy"},
    ],
    "new york": [
        {"day": 1, "high_f": 56, "low_f": 45, "condition": "Partly Cloudy"},
        {"day": 2, "high_f": 52, "low_f": 42, "condition": "Rainy"},
        {"day": 3, "high_f": 49, "low_f": 39, "condition": "Cloudy"},
        {"day": 4, "high_f": 55, "low_f": 44, "condition": "Sunny"},
        {"day": 5, "high_f": 58, "low_f": 47, "condition": "Clear"},
    ],
    "miami": [
        {"day": 1, "high_f": 89, "low_f": 78, "condition": "Sunny"},
        {"day": 2, "high_f": 87, "low_f": 76, "condition": "Partly Cloudy"},
        {"day": 3, "high_f": 84, "low_f": 75, "condition": "Thunderstorm"},
        {"day": 4, "high_f": 88, "low_f": 77, "condition": "Sunny"},
        {"day": 5, "high_f": 90, "low_f": 79, "condition": "Sunny"},
    ],
    "chicago": [
        {"day": 1, "high_f": 46, "low_f": 35, "condition": "Windy"},
        {"day": 2, "high_f": 42, "low_f": 33, "condition": "Rainy"},
        {"day": 3, "high_f": 44, "low_f": 34, "condition": "Cloudy"},
        {"day": 4, "high_f": 50, "low_f": 38, "condition": "Partly Cloudy"},
        {"day": 5, "high_f": 53, "low_f": 40, "condition": "Sunny"},
    ],
    "seattle": [
        {"day": 1, "high_f": 51, "low_f": 44, "condition": "Rainy"},
        {"day": 2, "high_f": 49, "low_f": 42, "condition": "Rainy"},
        {"day": 3, "high_f": 53, "low_f": 45, "condition": "Cloudy"},
        {"day": 4, "high_f": 55, "low_f": 46, "condition": "Partly Cloudy"},
        {"day": 5, "high_f": 58, "low_f": 47, "condition": "Sunny"},
    ],
    "austin": [
        {"day": 1, "high_f": 79, "low_f": 62, "condition": "Clear"},
        {"day": 2, "high_f": 82, "low_f": 64, "condition": "Sunny"},
        {"day": 3, "high_f": 77, "low_f": 60, "condition": "Partly Cloudy"},
        {"day": 4, "high_f": 74, "low_f": 58, "condition": "Rainy"},
        {"day": 5, "high_f": 76, "low_f": 59, "condition": "Cloudy"},
    ],
    "denver": [
        {"day": 1, "high_f": 53, "low_f": 35, "condition": "Sunny"},
        {"day": 2, "high_f": 48, "low_f": 30, "condition": "Snowy"},
        {"day": 3, "high_f": 55, "low_f": 36, "condition": "Partly Cloudy"},
        {"day": 4, "high_f": 60, "low_f": 40, "condition": "Clear"},
        {"day": 5, "high_f": 58, "low_f": 38, "condition": "Sunny"},
    ],
    "los angeles": [
        {"day": 1, "high_f": 76, "low_f": 62, "condition": "Clear"},
        {"day": 2, "high_f": 78, "low_f": 63, "condition": "Sunny"},
        {"day": 3, "high_f": 74, "low_f": 61, "condition": "Partly Cloudy"},
        {"day": 4, "high_f": 72, "low_f": 60, "condition": "Cloudy"},
        {"day": 5, "high_f": 75, "low_f": 62, "condition": "Clear"},
    ],
    "boston": [
        {"day": 1, "high_f": 49, "low_f": 40, "condition": "Cloudy"},
        {"day": 2, "high_f": 45, "low_f": 37, "condition": "Rainy"},
        {"day": 3, "high_f": 47, "low_f": 38, "condition": "Partly Cloudy"},
        {"day": 4, "high_f": 52, "low_f": 42, "condition": "Sunny"},
        {"day": 5, "high_f": 54, "low_f": 44, "condition": "Clear"},
    ],
    "phoenix": [
        {"day": 1, "high_f": 99, "low_f": 82, "condition": "Sunny"},
        {"day": 2, "high_f": 101, "low_f": 84, "condition": "Sunny"},
        {"day": 3, "high_f": 97, "low_f": 80, "condition": "Partly Cloudy"},
        {"day": 4, "high_f": 95, "low_f": 79, "condition": "Cloudy"},
        {"day": 5, "high_f": 98, "low_f": 81, "condition": "Sunny"},
    ],
}


def get_mock_weather(city: str) -> dict | None:
    return WEATHER_DB.get(city.lower().strip())


def get_mock_forecast(city: str, days: int) -> list[dict] | None:
    forecast = FORECAST_DB.get(city.lower().strip())
    if forecast is None:
        return None
    return forecast[:days]


def list_cities() -> list[str]:
    return [entry["city"] for entry in WEATHER_DB.values()]
