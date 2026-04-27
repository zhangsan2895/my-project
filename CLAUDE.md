# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HelloAgents智能旅行助手 — a multi-agent AI travel planning app. The backend uses the `hello_agents` framework with `SimpleAgent` instances connected to a High-De (Amap) map MCP server via stdio. The frontend is Vue 3 + TypeScript.

## Commands

### Backend (run from `backend/`)
```bash
# Start backend
python run.py
# or directly:
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# Install deps (conda env: agent, Python 3.10)
pip install -r requirements.txt
```

### Frontend (run from `frontend/`)
```bash
npm install
npm run dev       # dev server at http://localhost:5173
npm run build     # vue-tsc type check + vite build
```

### MCP Server prerequisite
```bash
# The backend spawns this automatically via uvx
uvx amap-mcp-server   # requires uv installed
```

## Architecture

### Backend layer stack

```
FastAPI (app/api/main.py)
  ├── /api/trip/plan  →  MultiAgentTripPlanner  (app/agents/trip_planner_agent.py)
  │     ├── attraction_agent: SimpleAgent + MCPTool (amap)
  │     ├── weather_agent:    SimpleAgent + MCPTool (amap)
  │     ├── hotel_agent:      SimpleAgent + MCPTool (amap)   ← run in parallel via ThreadPoolExecutor
  │     └── planner_agent:    SimpleAgent (no tools, synthesizes results from above 3)
  ├── /api/map/*      →  AmapService  (app/services/amap_service.py)
  └── /api/poi/*      →  AmapService + UnsplashService
```

### Key patterns

**MCP tool per agent:** Each `SimpleAgent` receives the same `MCPTool(name="amap", server_command=["uvx", "amap-mcp-server"])`. The `auto_expand=True` flag expands it into 16 individual tools. Each agent call spawns+destroys the MCP process (stdio transport).

**Env var naming split:** The `.env` file uses `AMAP_API_KEY`, but the MCPTool subprocess receives it as `AMAP_MAPS_API_KEY`. The mapping happens in `trip_planner_agent.py`: `env={"AMAP_MAPS_API_KEY": settings.amap_api_key}`.

**LLM config:** `HelloAgentsLLM` reads from `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_ID` env vars (not `OPENAI_*`). The `.env.example` shows these keys. Current deployment uses DashScope-compatible endpoint with `qwen3.6-flash`.

**Singleton pattern:** Both `MultiAgentTripPlanner` (`get_trip_planner_agent()`) and the LLM (`get_llm()`) use module-level globals as singletons.

**Parallel execution:** Steps 1–3 (attraction/weather/hotel agents) run concurrently via `ThreadPoolExecutor(max_workers=3)` in `plan_trip()`. Step 4 (planner) runs after all three complete.

### Frontend
- `src/views/Home.vue` — trip request form
- `src/views/Result.vue` — renders `TripPlan` with map (Amap JS API) + day-by-day itinerary
- `src/services/api.ts` — Axios client, proxied to `http://localhost:8000`
- `src/types/index.ts` — TypeScript types mirroring `app/models/schemas.py`

### Config loading order
`app/config.py` loads `backend/.env` first (absolute path), then optionally `../../../../HelloAgents/.env` without override. `Settings` (pydantic-settings) reads remaining env vars. `validate_config()` is called at FastAPI startup.

## LangChain upgrade layer (Phase 1)

A second agent layer is being added alongside the existing HelloAgents layer:

```
app/tools/langchain_mcp_tools.py   — LangChainMCPToolManager singleton
app/agents/langchain_amap_agent.py — create_react_agent (langgraph) + ChatOpenAI
app/api/routes/debug_mcp.py        — GET /debug/mcp/tools, POST /debug/mcp/call
app/api/routes/langchain_agent.py  — POST /debug/langchain-agent/invoke
```

The new layer uses `langchain_mcp_adapters.client.MultiServerMCPClient` with the **same** `uvx amap-mcp-server` command and `AMAP_MAPS_API_KEY` env var. The original `POST /api/trip/plan` is not affected.
