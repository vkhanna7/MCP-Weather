# solution/weather_server.py
#
# EXERCISE SOLUTION:
#   Added get_forecast(city, days) as a second tool.
#
# Compare with src/weather_server.py to see what changed.

import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP

from weather_data import get_mock_forecast, get_mock_weather, list_cities

mcp = FastMCP("WeatherDemo")


@mcp.tool()
def get_weather(city: str) -> dict:
    """Get the current weather for a city.

    Returns temperature (°F), weather condition, humidity, and wind speed
    for the requested city.

    Args:
        city: The name of the city to look up (case-insensitive).
    """
    if not city or not city.strip():
        raise ValueError("city must be a non-empty string")

    weather = get_mock_weather(city)
    if weather is None:
        known = ", ".join(list_cities())
        raise ValueError(
            f"No weather data for '{city}'. Known cities are: {known}"
        )
    return weather


# ── New tool: get_forecast ────────────────────────────────────────────────────
#
# Adding a second tool shows two important MCP concepts:
#
#   1. Multi-tool discovery — the client receives both tool schemas from
#      list_tools() and the model can choose between them.
#
#   2. Array return types — the tool returns a list of dicts rather than a
#      single dict.  MCP handles JSON-serialisable return types automatically.
#
@mcp.tool()
def get_forecast(city: str, days: int = 3) -> list[dict]:
    """Get a multi-day weather forecast for a city.

    Returns a list of daily forecasts, each with high/low temperatures (°F)
    and a weather condition. Supports 1 to 5 days ahead.

    Args:
        city: The name of the city to look up (case-insensitive).
        days: Number of days to forecast (1–5). Defaults to 3.
    """
    if not city or not city.strip():
        raise ValueError("city must be a non-empty string")

    if not 1 <= days <= 5:
        raise ValueError("days must be between 1 and 5")

    forecast = get_mock_forecast(city, days)
    if forecast is None:
        known = ", ".join(list_cities())
        raise ValueError(
            f"No forecast data for '{city}'. Known cities are: {known}"
        )
    return forecast


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
