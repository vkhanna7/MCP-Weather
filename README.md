# MCP Weather Demo

A tiny,  repository that shows how an MCP server works end to end using a beginner-friendly weather example. MCP is an open protocol for connecting AI applications to tools, data sources, and workflows through a standardized interface.[1][2]

This repo is designed to teach the flow, not impress with infrastructure. It includes a small Python server that exposes a `get_weather` tool, a simple mock client that simulates the tool-call lifecycle, and optional notes for connecting a real LLM client later.[3][4]

## What this demo teaches

By running this project, readers can see:

- how a server exposes a tool with a name, description, and input schema.[5][3]
- how a client discovers available tools before sending a query to a model.[3]
- how structured tool calls are validated and executed by the server.[5][3]
- why MCP is useful when LLM apps need a standard way to interact with external systems.[1][2]

## Repo structure

```text
mcp-weather-demo/
├── README.md
├── pyproject.toml
├── .env.example
├── src/
│   ├── weather_server.py
│   ├── demo_client.py
│   └── weather_data.py
└── walkthrough.md
```

## Why weather?

Weather is a great teaching example because the reader instantly understands why a model needs a tool: current weather is external and time-sensitive data.[4][1] It keeps the protocol visible without forcing beginners to deal with databases, OAuth, or heavy app setup on day one.[4][3]

## What MCP is doing here

In this demo, the **client** handles the user question, the **MCP server** exposes the weather tool and validates inputs, and the underlying weather function returns structured data.[5][3][1] That mirrors the MCP architecture described in the official docs, where clients connect to servers and servers expose capabilities such as tools, resources, and prompts.[6][7][1]

## Quick start

### 1) Install `uv`

If you do not already have `uv`, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2) Create the project environment

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 3) Run the local walkthrough client

```bash
python src/demo_client.py
```

This client does **not** require an API key. It prints the lifecycle clearly so readers can understand what is happening at each step.

### 4) Optional: connect a real LLM client later

The MCP docs provide a Python client tutorial that connects an LLM-powered chatbot to an MCP server and passes tool definitions into the model for tool use.[3] Once readers understand the mock flow in this repo, they can swap the walkthrough client for a real MCP client.

## How the demo works

### Step 1: The server advertises a tool

The tool is exposed with a machine-readable schema, including the required `city` argument. MCP documentation emphasizes that clients discover available tools from the server and pass those schemas into the model so tool use is grounded in explicit definitions rather than guesswork.[5][3]

### Step 2: The client asks a question

A user enters a prompt like: `What's the weather in San Francisco?`

### Step 3: A model or orchestrator decides a tool is needed

In a production MCP client, the model sees the available tool schemas and emits a structured tool call when it decides external data is needed.[3] In this demo, the mock client simulates that decision so readers can inspect the request and response flow without needing a model API key.

### Step 4: The server executes the tool

The server validates input, routes execution, and returns structured JSON-like data, which is the core behavior MCP servers provide when exposing external capabilities.[5][3][1]

### Step 5: The final answer is composed

The tool result is then turned into a natural language answer for the user. The official MCP client flow follows this same pattern: discover tools, let the model choose, call the tool through the server, then produce a final response.[3]

## Files

### `src/weather_data.py`

This file contains a tiny in-memory weather data store so the first run is deterministic and beginner-friendly. Starting with mocked data is useful because it keeps the reader focused on MCP itself rather than API keys and network issues.[4][3]

### `src/weather_server.py`

This is the main teaching artifact. It shows:

- the tool definition
- the input schema
- validation rules
- execution logic
- structured return values

### `src/demo_client.py`

This file simulates the client side of the lifecycle. It lists tools, accepts a user question, chooses the weather tool based on a simple parser, calls the server function, and formats the final answer. It is intentionally transparent so the protocol flow is easy to see.

### `walkthrough.md`

This is a blog-ready walkthrough you can adapt directly into a post or tutorial.

## Next upgrades

Once readers finish the basic version, extend the repo with one of these:

- add a second tool such as `get_forecast` to show multi-tool discovery.[4]
- add a read-only resource to demonstrate how resources differ from tools.[7]
- add a reusable prompt to show that MCP servers can expose prompts too.[6]
- connect a real LLM client using the MCP Python client tutorial.[3]

## Notes for your blog post

A clean way to position this repo is:

> This repo is not a weather app. It is a protocol demo. The goal is to help you see how MCP gives models a structured path to discover tools, call them safely, and turn the result into useful output.[1][2]