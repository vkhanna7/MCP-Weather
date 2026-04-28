# MCP Weather Demo — Recording Script

**Format:** screen recording with voiceover  
**Runtime:** ~12 minutes  
**Setup before recording:** terminal open in project root, `.venv` active, VS Code open with the repo

---

## [0:00] Hook

> "If you've ever wondered how ChatGPT or Claude can look things up, run code, or call an API — the answer is tools. And MCP is the open standard that makes tools work the same way across every AI system. In the next twelve minutes I'm going to show you exactly how it works, from scratch, using a weather example simple enough to fit in three files."

*Show: the repo in VS Code, nothing else yet.*

---

## [0:30] What problem are we solving?

> "A language model knows a lot, but it does not know what the weather is right now. That data lives outside the model. So how does the model get it?"

> "The naive answer is: hardcode a weather API call into your app. But then every AI framework invents its own way to do it, every tool has a different format, and nothing is reusable."

> "MCP — Model Context Protocol — fixes this. It defines a standard way for a server to advertise tools, and a standard way for a client to discover and call them. Same protocol, any model, any framework."

*Show: draw or reveal this diagram on screen*

```
User question
     ↓
  MCP Client  →  list_tools()   →  MCP Server
  MCP Client  →  call_tool()    →  MCP Server
                                        ↓
                                   weather data
                                        ↓
  MCP Client  ←  structured result  ←──┘
     ↓
Final answer
```

---

## [1:30] Repo tour — 30 seconds

> "The whole demo lives in three files. Let me show you each one before we run anything."

*Open file tree in VS Code. Click through each file as you name it.*

> "`weather_data.py` — a tiny in-memory weather store. No API key, completely deterministic."

> "`weather_server.py` — this is the MCP server. One tool, about forty lines of code."

> "`demo_client.py` — a mock client that prints every step of the protocol lifecycle so you can see exactly what's happening."

---
 
## [2:00] File 1 — weather_data.py

*Open `src/weather_data.py`*

> "The data layer is just a Python dictionary. Six cities, each with temperature, condition, and humidity."

*Scroll to `get_mock_weather`*

> "Two functions: `get_mock_weather` does a case-insensitive lookup and returns the dict or `None`. `list_cities` returns the canonical names. That's it — no network calls, no surprises."

> "In a real app you'd swap this for an API call. The rest of the code doesn't change."

---

## [2:45] File 2 — weather_server.py ← **the important one**

*Open `src/weather_server.py`*

> "This is the file that matters. Everything else is plumbing — this is where MCP lives."

*Highlight `mcp = FastMCP("WeatherDemo")`*

> "Line one: create the server. `FastMCP` is the high-level wrapper from the MCP Python SDK. The string is the display name clients see."

*Highlight `@mcp.tool()`*

> "Line two: expose a tool. This decorator does three things automatically."

> "First — it registers the function. Second — it reads the type hint `city: str` and generates a JSON Schema for the input. Third — it uses the docstring as the description."

> "That's what a client receives when it calls `list_tools`:"

*Show this block on screen (paste into terminal or show in slides):*

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

> "The model reads this schema to decide *when* to call the tool and *what to pass*. It's not guessing — it has an explicit contract."

*Highlight the `ValueError` lines*

> "Validation lives inside the function. A `ValueError` becomes a structured error response the client can inspect."

*Highlight `mcp.run()`*

> "And at the bottom: `mcp.run()` starts the server listening on stdio. Claude Desktop, the MCP Inspector, any MCP-compatible client can connect just by launching this process."

---

## [4:30] File 3 — demo_client.py

*Open `src/demo_client.py`*

> "The client file simulates what a real MCP client does. I've broken it into five labeled steps so you can follow along."

*Scroll through the five function stubs — just name them:*

> "Step 1 — discover tools. Step 2 — user asks a question. Step 3 — decide if a tool is needed. Step 4 — call the tool and get data back. Step 5 — turn the data into a natural-language answer."

> "In production, steps 1 and 4 are network calls handled by the SDK. Here we call the Python functions directly so every value is visible."

---

## [5:15] Run it — student version

*Switch to terminal*

```bash
python src/demo_client.py
```

*When the prompt appears, type:*
```
What's the weather in San Francisco?
```

*As each step prints, narrate it:*

> "Step 1 — the client lists the available tools and prints the schema. This is exactly what the model would receive."

> "Step 2 — we enter our question."

> "Step 3 — the mock client spots the word 'weather' and the city name and decides to call `get_weather`. A real model uses the schema description to make this call."

> "Step 4 — the server validates the input, looks up San Francisco, and returns a dict. Raw, structured, JSON-serialisable."

> "Step 5 — that dict becomes a sentence. In production this step is the model writing the final reply."

---

## [7:00] Run it again — unknown city

*Run again, this time type:*
```
What's the weather in Tokyo?
```

> "The server has no data for Tokyo, so it raises a `ValueError`. Watch what the client gets back — a clean error, not a crash. The client can handle it gracefully."

---

## [8:00] Show the solution — two tools

*Switch to solution version:*

```bash
python solution/demo_client.py
```

> "The solution folder shows where you'd take this next. We've added a second tool — `get_forecast` — and the client now has ten cities and smarter city extraction."

*Type:*
```
Give me a 3-day forecast for Denver
```

> "Two things to notice. One — the client auto-extracts 'Denver' from the sentence without asking. Two — it picks `get_forecast` over `get_weather` because the question contained the word 'forecast'. A real model makes this choice using the tool descriptions."

*Watch the output print the forecast list.*

> "The server returned an array this time. MCP handles any JSON-serialisable return type — dicts, lists, strings — automatically."

---

## [9:30] What a real client looks like

> "Everything you just saw used a mock client. Swapping in a real one is a ten-line change."

*Show this code snippet on screen (don't run it — just display):*

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(
    StdioServerParameters(command="python", args=["solution/weather_server.py"])
) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        tools = await session.list_tools()       # Step 1
        result = await session.call_tool(         # Step 4
            "get_weather", {"city": "Seattle"}
        )
        print(result)
```

> "Same server. Same tool. The only difference is the transport — now it's real JSON-RPC over stdio instead of a direct Python call."

---

## [10:30] The three things to remember

> "Let me leave you with three sentences."

> "One — MCP servers expose tools with a name, a description, and a schema. That's the contract."

> "Two — MCP clients discover those tools and let the model choose which one to call. The model is not guessing — it's reading a spec."

> "Three — the server validates input and returns structured data. The client turns that data into an answer."

> "Weather is throwaway. The pattern is what you're learning."

---

## [11:15] What's next

> "From here you can go three directions."

> "Add a second tool — `get_forecast` is already in the solution. Adding more tools teaches multi-tool discovery."

> "Add a resource — MCP servers can expose read-only data sources, not just callable tools. The walkthrough file has notes on this."

> "Wire in a real LLM — swap the mock client for an Anthropic or OpenAI client and watch the model make real tool-call decisions."

*Show the repo one more time — file tree visible.*

> "All the code is in the repo. The `walkthrough.md` goes deeper on every file. Start with `python src/demo_client.py` and go from there."

---

## Recording tips

- **Font size:** bump terminal and VS Code to at least 18pt before recording
- **Theme:** use a high-contrast theme (dark background) so code is readable in video compression
- **Pause after each step prints:** give viewers time to read the output before you narrate it
- **Don't scroll while talking:** finish the sentence, then move
- **Re-run if you mistype:** it's a demo, clean takes are worth it
