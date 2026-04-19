# solution/demo_client.py
from __future__ import annotations
#
# EXERCISE SOLUTION:
#   _pick_tool now uses regex to extract a city name directly from the
#   question, so users rarely need to type the city a second time.
#   It also handles the new get_forecast tool (asks how many days).
#
# Compare with src/demo_client.py to see what changed.

import os
import re
import sys

# Ensure this script always imports weather_data and weather_server from its
# own directory, regardless of how it is invoked or what PYTHONPATH is set to.
sys.path.insert(0, os.path.dirname(__file__))

import weather_server  # noqa: F401  (registers tools with FastMCP)
from weather_data import get_mock_forecast, get_mock_weather, list_cities

DIVIDER = "─" * 60


def _banner(step: int, title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  STEP {step}: {title}")
    print(DIVIDER)


def _discover_tools() -> list[dict]:
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
                    "city": {"type": "string", "description": "City name (case-insensitive)."}
                },
                "required": ["city"],
            },
        },
        {
            "name": "get_forecast",
            "description": (
                "Get a multi-day weather forecast for a city. "
                "Returns high/low temps and conditions for 1–5 days."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name (case-insensitive)."},
                    "days": {"type": "integer", "description": "Number of days (1–5). Default 3."},
                },
                "required": ["city"],
            },
        },
    ]


def _extract_city(question: str) -> str | None:
    """Try to extract a city name from the question using two strategies.

    Strategy A — exact match against the known city list (case-insensitive).
    Strategy B — look for "in <word(s)>" or "for <word(s)>" patterns and
                 check whether those words match a known city.

    Returns the matched city string, or None if nothing matched.
    """
    q_lower = question.lower()

    # Strategy A: scan every known city
    for city in list_cities():
        if city.lower() in q_lower:
            return city

    # Strategy B: "in San Francisco" / "for New York" etc.
    pattern = r"\b(?:in|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    match = re.search(pattern, question, re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
        for city in list_cities():
            if city.lower() == candidate.lower():
                return city

    return None


def _pick_tool(question: str, tools: list[dict]) -> tuple[str, dict] | None:
    """Decide which tool to call and what arguments to pass.

    Returns (tool_name, arguments) or None if no tool is needed.
    """
    q = question.lower()

    weather_keywords = {"weather", "temperature", "hot", "cold", "rain", "sunny", "wind"}
    forecast_keywords = {"forecast", "week", "tomorrow", "next", "days", "upcoming"}

    wants_forecast = any(kw in q for kw in forecast_keywords)
    wants_weather = any(kw in q for kw in weather_keywords) or wants_forecast

    if not wants_weather:
        return None

    # Try to pull the city name directly from the question
    city = _extract_city(question)
    if city is None:
        city = input("  Which city would you like weather for? ").strip()
    if not city:
        return None

    if wants_forecast:
        # Try to parse a day count from the question ("3 days", "5-day", etc.)
        day_match = re.search(r"\b([1-5])\s*-?\s*day", q)
        if day_match:
            days = int(day_match.group(1))
        else:
            days_input = input("  How many days of forecast? (1–5, default 3): ").strip()
            days = int(days_input) if days_input.isdigit() and 1 <= int(days_input) <= 5 else 3
        return ("get_forecast", {"city": city, "days": days})

    return ("get_weather", {"city": city})


def _call_tool(tool_name: str, arguments: dict) -> dict | list:
    if tool_name == "get_weather":
        weather = get_mock_weather(arguments["city"])
        if weather is None:
            raise ValueError(f"No data for city: '{arguments['city']}'")
        return weather

    if tool_name == "get_forecast":
        days = arguments.get("days", 3)
        forecast = get_mock_forecast(arguments["city"], days)
        if forecast is None:
            raise ValueError(f"No forecast data for city: '{arguments['city']}'")
        return forecast

    raise ValueError(f"Unknown tool: {tool_name}")


def _format_answer(question: str, tool_name: str, tool_result: dict | list) -> str:
    if tool_name == "get_weather":
        r = tool_result
        return (
            f"The current weather in {r['city']} is {r['temperature_f']}°F and "
            f"{r['condition'].lower()}, with {r['humidity_pct']}% humidity and "
            f"wind speeds of {r['wind_speed_mph']} mph."
        )

    if tool_name == "get_forecast":
        lines = []
        for day in tool_result:
            lines.append(
                f"  Day {day['day']}: High {day['high_f']}°F / Low {day['low_f']}°F — {day['condition']}"
            )
        return "Forecast:\n" + "\n".join(lines)

    return str(tool_result)


def run_demo() -> None:
    print("\n╔══════════════════════════════════════════════════╗")
    print("║     MCP Weather Demo — Solution Client           ║")
    print("╚══════════════════════════════════════════════════╝")

    _banner(1, "Client connects and discovers available tools")
    tools = _discover_tools()
    print(f"\n  Server advertises {len(tools)} tool(s):\n")
    for tool in tools:
        print(f"  • {tool['name']}")
        print(f"    {tool['description']}")

    _banner(2, "User sends a question")
    known = ", ".join(list_cities())
    print(f"\n  Cities with mock data: {known}")
    print()
    question = input("  Your question: ").strip()
    if not question:
        print("  (No question entered — exiting.)")
        sys.exit(0)

    _banner(3, "Model decides whether a tool call is needed")
    decision = _pick_tool(question, tools)
    if decision is None:
        print("\n  No tool call needed.")
        print(f'\n  Answer: I can only answer weather questions right now.')
        return

    tool_name, arguments = decision
    print(f"\n  → Calling tool '{tool_name}' with arguments: {arguments}")

    _banner(4, "Server executes the tool and returns structured data")
    try:
        result = _call_tool(tool_name, arguments)
    except ValueError as exc:
        print(f"\n  Tool returned an error: {exc}")
        return
    print(f"\n  Raw tool result:\n  {result}")

    _banner(5, "Client composes a natural-language answer")
    answer = _format_answer(question, tool_name, result)
    print(f'\n  Final answer: "{answer}"')
    print()


if __name__ == "__main__":
    run_demo()
