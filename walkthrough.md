# MCP Weather Demo — Walkthrough

This document is a step-by-step companion to the code in `src/`. Read it alongside the files to understand how MCP works from first principles.

---

## What problem does MCP solve?

Large language models know a lot, but they do not know what the weather is right now. That information lives outside the model — in an API, a database, or a live service. To get it, the model needs to call a tool.

The problem is: how does a model know what tools exist, what arguments they expect, and how to call them safely?

**MCP (Model Context Protocol)** solves this by defining a standard interface. Instead of every LLM framework inventing its own tool-calling format, MCP gives you:

- a standard way for a **server** to advertise tools (with names, descriptions, and schemas)
- a standard way for a **client** to discover those tools and call them
- a standard way for the **server** to validate inputs and return results

This demo shows that lifecycle end to end using a simple weather example.

---

## The three components

```
┌──────────────┐        list_tools()        ┌──────────────────┐
│              │ ──────────────────────────▶ │                  │
│  MCP Client  │                             │   MCP Server     │
│ (demo_client)│ ◀────────────────────────── │ (weather_server) │
│              │    [{name, description,     │                  │
└──────────────┘      inputSchema}]          └──────────────────┘
       │                                             │
       │  call_tool("get_weather", {city: "..."})    │
       │ ──────────────────────────────────────────▶ │
       │                                             │
       │  {temperature_f, condition, humidity_pct}   │  calls
       │ ◀────────────────────────────────────────── │ ────────▶ weather_data.py
       │                                             │
       ▼
  Final answer to user
```

---

## Walking through each file

### `src/weather_data.py` — the data layer

This file contains a plain Python dictionary (`WEATHER_DB`) that stands in for a real weather API. Using mock data means:

- no API key is needed on day one
- the output is deterministic, so the demo is easy to debug
- readers can focus on the protocol, not the networking

The two public functions are `get_mock_weather(city)` and `list_cities()`. The server imports both.

---

### `src/weather_server.py` — the MCP server

This is the most important file. Open it and look for the three numbered comments.

#### 1. Creating the server

```python
mcp = FastMCP("WeatherDemo")
```

`FastMCP` is the high-level entry point from the MCP Python SDK. The string `"WeatherDemo"` is the server's display name — it appears in tool listings and client logs.

#### 2. Exposing a tool

```python
@mcp.tool()
def get_weather(city: str) -> dict:
    """Get the current weather for a city. ..."""
```

The `@mcp.tool()` decorator does three things automatically:

1. Registers `get_weather` as a callable tool on this server.
2. Uses the Python type hints (`city: str`) to generate a JSON Schema for the `inputSchema` field that clients see.
3. Uses the docstring as the human-readable `description` field.

When a client or model calls `list_tools`, it receives:

```json
{
  "name": "get_weather",
  "description": "Get the current weather for a city...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "city": { "type": "string" }
    },
    "required": ["city"]
  }
}
```

This is the schema the model reads to know *when* and *how* to call the tool.

#### 3. Validation and return

```python
if not city or not city.strip():
    raise ValueError("city must be a non-empty string")
```

Validation lives inside the tool function. A `ValueError` becomes a structured error response the client can inspect.

The return value is a plain dict — JSON-serialisable and ready for the client to use.

---

### `src/demo_client.py` — the mock client

This file simulates the five steps a real MCP client performs:

| Step | What happens |
|------|-------------|
| 1 | Client connects to server and calls `list_tools` |
| 2 | User sends a question |
| 3 | Model (or mock logic) decides a tool call is needed |
| 4 | Client calls `call_tool` with the chosen arguments |
| 5 | Client formats the tool result into a final answer |

In a production app, steps 1 and 4 are network calls managed by the MCP SDK. Here we call the underlying Python functions directly so you can see every value without any infrastructure.

---

## Running the demo

```bash
# activate the environment
source .venv/bin/activate

# run the mock client
python src/demo_client.py
```

Try asking:

- `What's the weather in San Francisco?`
- `Is it hot in Miami today?`
- `What's the weather in Tokyo?`  ← triggers the error path

---

## Exercises — going from src/ to solution/

The data layer (`src/weather_data.py`) is already complete — 10 cities, wind speeds, and a full forecast database. Your job is to wire those up through the server and client.

Work through these two exercises in order. Each one changes only the files listed. When you finish both, `src/` will behave identically to `solution/`.

---

### Exercise 1 — add a second tool: `get_forecast`

**Files to change:** `src/weather_server.py`, `src/demo_client.py`

**Goal:** expose `get_forecast` as a second MCP tool so clients can request multi-day forecasts. This demonstrates multi-tool discovery — the client receives both schemas from `list_tools` and can choose between them.

**Step 1 — add `get_forecast` to `weather_server.py`**

Open `src/weather_server.py` and find the `TODO (Exercise 1)` block. Add the tool below `get_weather`. The data function `get_mock_forecast` is already imported — you just need to expose it. Use `get_weather` directly above as your template:

```python
@mcp.tool()
def get_forecast(city: str, days: int = 3) -> list[dict]:
    """Get a multi-day weather forecast for a city.

    Returns a list of daily forecasts with high/low temperatures (°F)
    and weather condition. Supports 1 to 5 days ahead.

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
        raise ValueError(f"No forecast data for '{city}'. Known cities: {known}")

    return forecast
```

Notice: FastMCP reads `days: int = 3` and automatically marks `days` as optional with a default of 3 in the JSON Schema. You don't write any schema by hand.

**Step 2 — add the `get_forecast` schema to `_discover_tools` in `demo_client.py`**

Find `TODO (Exercise 1)` inside `_discover_tools`. Uncomment the example schema that's already there. This is the schema the client advertises at Step 1.

**Step 3 — handle `get_forecast` in `_call_tool`**

Find `TODO (Exercise 1)` in `_call_tool`. Add a branch for the new tool:

```python
if tool_name == "get_forecast":
    days = arguments.get("days", 3)
    forecast = get_mock_forecast(arguments["city"], days)
    if forecast is None:
        raise ValueError(f"No forecast data for city: '{arguments['city']}'")
    return forecast
```

**Step 4 — format forecast results in `_format_answer`**

Find `TODO (Exercise 1)` in `_format_answer`. The forecast result is a `list`, not a `dict`, so it needs its own branch:

```python
if tool_name == "get_forecast":
    lines = [
        f"  Day {d['day']}: High {d['high_f']}°F / Low {d['low_f']}°F — {d['condition']}"
        for d in tool_result
    ]
    return "Forecast:\n" + "\n".join(lines)
```

**Check your work:**

```bash
python src/demo_client.py
# Ask: What's the weather in Chicago?
# Step 1 should now list 2 tools.
# The answer should include wind speed.

python src/demo_client.py
# Ask: Give me a forecast for Miami
# Step 3 will still pick get_weather (forecast intent detection comes in Exercise 2).
# But _call_tool and _format_answer for get_forecast are now wired up.
```

---

### Exercise 2 — smarter tool selection in the client

**Files to change:** `src/demo_client.py`

**Goal:** `_pick_tool` currently always returns `get_weather`. Improve it so it detects forecast intent and extracts city names from natural-sounding questions automatically.

**Step 1 — add `import re` at the top of `demo_client.py`**

**Step 2 — write an `_extract_city` helper above `_pick_tool`**

The current loop works for exact city names but misses patterns like *"weather for New York"*. Add a helper that tries two strategies:

```python
def _extract_city(question: str) -> str | None:
    q_lower = question.lower()

    # Strategy A: exact substring match against known city list
    for city in list_cities():
        if city.lower() in q_lower:
            return city

    # Strategy B: "in Denver" / "for New York" patterns
    match = re.search(
        r"\b(?:in|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", question, re.IGNORECASE
    )
    if match:
        candidate = match.group(1).strip()
        for city in list_cities():
            if city.lower() == candidate.lower():
                return city

    return None
```

**Step 3 — rewrite `_pick_tool` to use `_extract_city` and detect forecast intent**

Find `TODO (Exercise 2)` in `_pick_tool`. Replace the body of the function (after the `weather_keywords` check) with:

```python
forecast_keywords = {"forecast", "week", "tomorrow", "next", "days", "upcoming"}
wants_forecast = any(kw in q for kw in forecast_keywords)

city = _extract_city(question)
if city is None:
    city = input("  Which city would you like weather for? ").strip()
if not city:
    return None

if wants_forecast:
    days_input = input("  How many days of forecast? (1–5, default 3): ").strip()
    days = int(days_input) if days_input.isdigit() and 1 <= int(days_input) <= 5 else 3
    return ("get_forecast", {"city": city, "days": days})

return ("get_weather", {"city": city})
```

**Check your work:**

```bash
python src/demo_client.py
# Ask: Give me a 3-day forecast for Denver
# Step 3 should pick get_forecast with days=3, no clarifying prompt.

python src/demo_client.py
# Ask: Is it going to rain in Chicago this week?
# Step 3 should pick get_forecast and auto-extract Chicago.
```

---

## What a real MCP client looks like

Once you understand this mock flow, you can swap `demo_client.py` for a real MCP client. The Anthropic Python SDK example looks like this:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(StdioServerParameters(command="python", args=["src/weather_server.py"])) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # Step 1: discover tools
        tools = await session.list_tools()

        # Step 4: call a tool
        result = await session.call_tool("get_weather", {"city": "Seattle"})
        print(result)
```

The server does not change at all — the same `weather_server.py` works with the mock client and the real one.

---

## Extending further

| Extension | What it teaches |
|-----------|----------------|
| Add a read-only resource (`weather://current/{city}`) | How resources differ from tools |
| Add a reusable prompt template | How MCP servers can expose prompts |
| Wire in a real LLM | The full end-to-end production pattern |

---

## Key takeaway

> This repo is not a weather app. It is a protocol demo. The goal is to help you see how MCP gives models a structured path to discover tools, call them safely, and turn the result into useful output.

The weather data is throwaway. The protocol pattern is what you are learning.
