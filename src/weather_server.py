# weather_server.py
#
# This is the core teaching file for the MCP demo.
#
# What you will see here:
#   1. How to create an MCP server with FastMCP.
#   2. How to expose a tool with a name, description, and typed input schema.
#   3. How the server validates input and returns structured data.
#
# The MCP Python SDK handles the protocol layer (JSON-RPC over stdio) for you.
# Your job is only to define tools and their logic.

import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP

from weather_data import get_mock_forecast, get_mock_weather, list_cities

# ── 1. Create the server ──────────────────────────────────────────────────────
#
# FastMCP is a high-level wrapper around the lower-level MCP server primitives.
# The string you pass here is the server's display name — it shows up when
# a client calls `list_tools` or inspects the server manifest.
#
mcp = FastMCP("WeatherDemo")


# ── 2. Expose a tool ──────────────────────────────────────────────────────────
#
# The @mcp.tool() decorator does three things automatically:
#   a) registers the function as a callable tool
#   b) uses the function's type hints to build the JSON input schema
#   c) uses the docstring as the human-readable tool description
#
# When a client (or a model using an MCP client) calls `list_tools`, it
# receives the tool name, description, and schema — exactly what the model
# needs to decide *when* and *how* to call the tool.
#
@mcp.tool()
def get_weather(city: str) -> dict:
    """Get the current weather for a city.

    Returns temperature (°F), weather condition, humidity, and wind speed
    for the requested city.

    Args:
        city: The name of the city to look up (case-insensitive).
    """
    # ── 3. Validate input ────────────────────────────────────────────────────
    #
    # Input validation happens here, inside the tool function.
    # If validation fails we raise a ValueError — the MCP SDK converts
    # that into a structured error response the client can inspect.
    #
    if not city or not city.strip():
        raise ValueError("city must be a non-empty string")

    # ── 4. Execute and return structured data ────────────────────────────────
    #
    # The return value must be JSON-serialisable. Returning a plain dict is
    # the simplest approach. The client (or model) receives this dict and
    # can use any field to compose a final answer.
    #
    weather = get_mock_weather(city)

    if weather is None:
        known = ", ".join(list_cities())
        raise ValueError(
            f"No weather data for '{city}'. "
            f"Known cities are: {known}"
        )

    return weather


# ── TODO (Exercise 1) ─────────────────────────────────────────────────────────
#
# Add a second tool: get_forecast
#
# The data layer is already ready — get_mock_forecast(city, days) is imported
# above and returns a list of daily forecast dicts from weather_data.py.
#
# Your job is to expose it as an MCP tool. Use get_weather above as a template:
#
#   1. Add @mcp.tool() decorator
#   2. Write the function signature: get_forecast(city: str, days: int = 3) -> list[dict]
#   3. Write a docstring — FastMCP uses it as the tool description clients see
#   4. Validate: raise ValueError if city is empty or days is not between 1 and 5
#   5. Call get_mock_forecast(city, days) and raise ValueError if it returns None
#   6. Return the result
#
# When you're done, run: python src/demo_client.py
# Step 1 should print TWO tools instead of one.
#
# Stuck? See solution/weather_server.py for the full implementation.


# ── Entry point ───────────────────────────────────────────────────────────────
#
# `mcp.run()` starts the server and listens on stdio.
# Claude Desktop, the MCP Inspector, or any MCP-compatible client
# can connect by launching this process.
#
def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
