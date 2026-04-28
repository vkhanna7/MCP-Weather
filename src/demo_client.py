# demo_client.py
from __future__ import annotations
#
# A mock MCP client that walks through the full tool-call lifecycle without
# needing a real LLM or API key.
#
# The five steps below mirror what a real MCP client (e.g. Claude Desktop or
# the MCP Python client SDK) does every time a user asks a question:
#
#   Step 1 — Client connects and discovers available tools
#   Step 2 — User sends a question
#   Step 3 — Model (or mock logic) decides a tool call is needed
#   Step 4 — Client calls the server tool and gets structured data back
#   Step 5 — Client composes a natural-language answer from the tool result

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# We import the server module directly here to keep the demo self-contained.
# In a real MCP client you would connect over stdio/HTTP and call
# `client.list_tools()` and `client.call_tool(name, arguments)` instead.
import weather_server  # noqa: F401  (registers the tools with FastMCP)
from weather_data import get_mock_forecast, get_mock_weather, list_cities

DIVIDER = "─" * 60


def _banner(step: int, title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  STEP {step}: {title}")
    print(DIVIDER)


def _discover_tools() -> list[dict]:
    """Return a hand-written schema for each tool the server exposes.

    In a real MCP client this list comes from the server via list_tools().
    We hard-code it here so the demo has no network dependency.
    """
    return [
        {
            "name": "get_weather",
            "description": (
                "Get the current weather for a city. "
                "Returns temperature (°F), condition, humidity, and wind speed."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city (case-insensitive).",
                    }
                },
                "required": ["city"],
            },
        },
        # TODO (Exercise 1 — after adding get_forecast to weather_server.py):
        # Add the get_forecast schema here so Step 1 advertises both tools.
        # Copy the entry above as a template and change:
        #   - "name"        → "get_forecast"
        #   - "description" → describe the multi-day forecast it returns
        #   - add a second property "days" with type "integer" (not required,
        #     default 3) alongside the existing "city" property
        #
        # Example schema for the new entry:
        # {
        #     "name": "get_forecast",
        #     "description": (
        #         "Get a multi-day weather forecast for a city. "
        #         "Returns high/low temps and conditions for 1–5 days."
        #     ),
        #     "inputSchema": {
        #         "type": "object",
        #         "properties": {
        #             "city": {
        #                 "type": "string",
        #                 "description": "City name (case-insensitive).",
        #             },
        #             "days": {
        #                 "type": "integer",
        #                 "description": "Number of days (1–5). Default 3.",
        #             },
        #         },
        #         "required": ["city"],
        #     },
        # },
    ]


def _pick_tool(question: str, tools: list[dict]) -> tuple[str, dict] | None:
    """Decide which tool to call and what arguments to pass.

    This simulates the decision a model makes when it sees available tool
    schemas.  A real model uses the schema descriptions to choose; here we
    use a simple keyword check.

    Returns (tool_name, arguments) or None if no tool is needed.
    """
    q = question.lower()

    # Does the question seem to be about weather?
    weather_keywords = {"weather", "temperature", "forecast", "hot", "cold", "rain"}
    if not any(kw in q for kw in weather_keywords):
        return None

    # Try to extract a city name from the question.
    for city in list_cities():
        if city.lower() in q:
            return ("get_weather", {"city": city})

    # Ask the user to clarify if we found a weather question but no city.
    city = input("  Which city would you like weather for? ").strip()
    if city:
        return ("get_weather", {"city": city})

    return None

    # TODO (Exercise 2): Improve _pick_tool in two ways:
    #
    # A) Detect forecast intent and call get_forecast instead of get_weather.
    #    Add a forecast_keywords set (e.g. {"forecast", "week", "tomorrow",
    #    "next", "days"}) and check it against `q`. When matched, ask the user
    #    how many days and return ("get_forecast", {"city": ..., "days": ...}).
    #
    # B) Extract the city with a regex so patterns like "forecast for Denver"
    #    work without prompting the user. Write a helper _extract_city(question)
    #    that first scans list_cities() for a substring match, then falls back
    #    to re.search(r"\b(?:in|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", ...).
    #
    # See solution/demo_client.py → _extract_city() and _pick_tool() for the
    # full implementation.


def _call_tool(tool_name: str, arguments: dict) -> dict | list:
    """Execute the named tool and return the result.

    In a production MCP client this would be:
        result = await client.call_tool(tool_name, arguments)
    Here we call the underlying function directly.
    """
    if tool_name == "get_weather":
        city = arguments.get("city", "")
        weather = get_mock_weather(city)
        if weather is None:
            raise ValueError(f"No data for city: '{city}'")
        return weather

    # TODO (Exercise 1): Add a branch for "get_forecast" once you have added
    # that tool to weather_server.py. get_mock_forecast is already imported
    # at the top of this file — call it with arguments["city"] and
    # arguments.get("days", 3), then raise ValueError if it returns None.

    raise ValueError(f"Unknown tool: {tool_name}")


def _format_answer(question: str, tool_result: dict | list, tool_name: str = "get_weather") -> str:
    """Turn a structured tool result into a natural-language answer.

    In a real MCP client this step is handled by passing the tool result
    back into the model so it can write the final reply.
    """
    if tool_name == "get_weather":
        city = tool_result["city"]
        temp = tool_result["temperature_f"]
        cond = tool_result["condition"]
        hum  = tool_result["humidity_pct"]
        wind = tool_result["wind_speed_mph"]
        return (
            f"The current weather in {city} is {temp}°F and {cond.lower()}, "
            f"with {hum}% humidity and wind speeds of {wind} mph."
        )

    # TODO (Exercise 1): Add a branch for "get_forecast".
    # tool_result will be a list of dicts when get_forecast was called.
    # Format each day on its own line, e.g.:
    #   Day 1: High 89°F / Low 78°F — Sunny
    #   Day 2: High 87°F / Low 76°F — Partly Cloudy
    # Return the formatted string (don't print inside this function).

    return str(tool_result)


def run_demo() -> None:
    print("\n╔══════════════════════════════════════════════════╗")
    print("║        MCP Weather Demo — Mock Client            ║")
    print("╚══════════════════════════════════════════════════╝")
    print("\nThis walkthrough simulates the five steps of the MCP tool-call")
    print("lifecycle without requiring an API key or a running LLM.\n")

    # ── STEP 1: Discover tools ────────────────────────────────────────────────
    _banner(1, "Client connects and discovers available tools")
    tools = _discover_tools()
    print(f"\n  Server advertises {len(tools)} tool(s):\n")
    for tool in tools:
        print(f"  • {tool['name']}")
        print(f"    {tool['description']}")
        props = tool["inputSchema"]["properties"]
        for param, meta in props.items():
            print(f"    └─ param '{param}': {meta['description']}")

    # ── STEP 2: User sends a question ─────────────────────────────────────────
    _banner(2, "User sends a question")
    known = ", ".join(list_cities())
    print(f"\n  Cities with mock data: {known}")
    print()
    question = input("  Your question: ").strip()
    if not question:
        print("  (No question entered — exiting.)")
        sys.exit(0)

    # ── STEP 3: Decide whether a tool call is needed ──────────────────────────
    _banner(3, "Model decides whether a tool call is needed")
    decision = _pick_tool(question, tools)

    if decision is None:
        print("\n  No tool call needed — answering from general knowledge.")
        print(f'\n  Answer: "{question}" — sorry, I can only answer weather questions right now.')
        return

    tool_name, arguments = decision
    print(f"\n  → Calling tool '{tool_name}' with arguments: {arguments}")

    # ── STEP 4: Server executes the tool ──────────────────────────────────────
    _banner(4, "Server executes the tool and returns structured data")
    try:
        result = _call_tool(tool_name, arguments)
    except ValueError as exc:
        print(f"\n  Tool returned an error: {exc}")
        return

    print(f"\n  Raw tool result (JSON):\n  {result}")

    # ── STEP 5: Compose the final answer ──────────────────────────────────────
    _banner(5, "Client composes a natural-language answer")
    answer = _format_answer(question, result, tool_name)
    print(f'\n  Final answer: "{answer}"')
    print()


if __name__ == "__main__":
    run_demo()
