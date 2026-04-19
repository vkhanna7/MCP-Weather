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
#
# ─── STUDENT EXERCISE ────────────────────────────────────────────────────────
# The _pick_tool function below uses a very naive keyword check to decide
# whether to call get_weather.  Real LLMs use the tool schema to make this
# decision.  Try improving _pick_tool so it also extracts the city name from
# the question automatically, e.g. with a regex or small parsing function.
# ─────────────────────────────────────────────────────────────────────────────

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# We import the server module directly here to keep the demo self-contained.
# In a real MCP client you would connect over stdio/HTTP and call
# `client.list_tools()` and `client.call_tool(name, arguments)` instead.
import weather_server  # noqa: F401  (registers the tools with FastMCP)
from weather_data import get_mock_weather, list_cities

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
                "Returns temperature (°F), weather condition, and humidity."
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
        }
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


def _call_tool(tool_name: str, arguments: dict) -> dict:
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

    raise ValueError(f"Unknown tool: {tool_name}")


def _format_answer(question: str, tool_result: dict) -> str:
    """Turn a structured tool result into a natural-language answer.

    In a real MCP client this step is handled by passing the tool result
    back into the model so it can write the final reply.
    """
    city = tool_result["city"]
    temp = tool_result["temperature_f"]
    cond = tool_result["condition"]
    hum = tool_result["humidity_pct"]

    return (
        f"The current weather in {city} is {temp}°F and {cond.lower()}, "
        f"with {hum}% humidity."
    )


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
    answer = _format_answer(question, result)
    print(f'\n  Final answer: "{answer}"')
    print()


if __name__ == "__main__":
    run_demo()
