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

**Student exercise:** Add a few more cities. Add a `wind_speed_mph` field.

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

**Student exercise:** The `_pick_tool` function uses a naive keyword search. Improve it to extract the city name automatically from the question.

---

## Running the demo

```bash
# 1. Install dependencies
uv venv
source .venv/bin/activate
uv pip install -e .

# 2. Run the mock client
python src/demo_client.py
```

You should see the five steps printed in sequence. Try asking:

- `What's the weather in San Francisco?`
- `Is it hot in Miami today?`
- `Tell me about Chicago weather`

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

## Extending the demo

| Extension | What it teaches |
|-----------|----------------|
| Add `get_forecast(city, days)` | Multi-tool discovery; array return types |
| Add a read-only resource (`weather://current/{city}`) | How resources differ from tools |
| Add a reusable prompt template | How MCP servers can expose prompts |
| Wire in a real LLM | The full end-to-end production pattern |

---

## Key takeaway

> This repo is not a weather app. It is a protocol demo. The goal is to help you see how MCP gives models a structured path to discover tools, call them safely, and turn the result into useful output.

The weather data is throwaway. The protocol pattern is what you are learning.
