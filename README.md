# HelloAgents 智能旅行助手 🌍✈️

在 [HelloAgents](https://github.com/jjyaoao/HelloAgents) 框架基础上二次开发的智能旅行规划助手。项目在保留原有 HelloAgents 多 Agent 架构的基础上，逐步引入 **LangChain / LangGraph**、**RAG 知识库检索**和**城市知识库爬虫**，构建一个能够结合实时地图数据与本地旅行知识的 AI 旅行规划系统。

---

## ✨ 功能特点

- 🤖 **多 Agent 并行规划**：基于 HelloAgents `SimpleAgent`，景点、天气、住宿三个 Agent 并行调用，由规划 Agent 综合输出完整行程
- 🗺️ **高德地图实时数据**：通过 MCP 协议接入 `amap-mcp-server`，支持景点搜索、路线规划、天气查询等 16 项工具
- 🔗 **LangChain ReAct Agent**：基于 LangGraph `create_react_agent` + ChatOpenAI 构建的第二套 Agent 层，支持灵活扩展
- 📚 **RAG 旅行知识库**：20 座热门城市的本地 Markdown 知识库，通过 FAISS + BGE 向量检索为规划提供背景知识
- 🕷️ **知识库爬虫**：自动从公开网页（Wikipedia 等）抓取资料，经 LLM 整理后生成标准化 Markdown，支持批量扩充城市
- 🎨 **现代化前端**：Vue 3 + TypeScript + Ant Design Vue，含高德地图 JS API 可视化展示

---

## 🏗️ 系统架构

```
用户请求
  │
  ▼
FastAPI
  ├── POST /api/trip/plan  ──────────────────────────────────────────────────┐
  │     MultiAgentTripPlanner (HelloAgents)                                   │
  │       ├── attraction_agent: SimpleAgent + MCPTool(amap)  ─┐              │
  │       ├── weather_agent:    SimpleAgent + MCPTool(amap)   ├─ 并行执行     │
  │       ├── hotel_agent:      SimpleAgent + MCPTool(amap)  ─┘              │
  │       └── planner_agent:    SimpleAgent（综合上述结果）                    │
  │                                                                           │
  ├── POST /debug/langchain-agent/invoke                                      │
  │     LangChain ReAct Agent (LangGraph + ChatOpenAI + Amap MCP)            │
  │                                                                           │
  ├── POST /debug/rag/search / context                                        │
  │     RAG 检索（FAISS + BGE-large-zh-v1.5）                                 │
  │       └── knowledge_base/{city}/*.md → 向量化 → 相似度检索                │
  │                                                                           │
  └── GET/POST /api/map/* /api/poi/*                                          │
        AmapService + UnsplashService（直接调用高德/Unsplash HTTP API）        │
```

---

## 🛠️ 技术栈

| 层次 | 技术 |
|------|------|
| **Agent 框架（基础层）** | HelloAgents `SimpleAgent` + `HelloAgentsLLM` + `MCPTool` |
| **Agent 框架（扩展层）** | LangChain · LangGraph `create_react_agent` · langchain-mcp-adapters |
| **LLM** | 兼容 OpenAI API（阿里 DashScope / DeepSeek / OpenAI 等均可） |
| **RAG 检索** | FAISS · HuggingFace `BAAI/bge-large-zh-v1.5` · LangChain Community |
| **知识库爬虫** | httpx · trafilatura · BeautifulSoup4 · robots.txt 合规检查 |
| **后端** | FastAPI · Pydantic v2 · uvicorn |
| **MCP 工具** | amap-mcp-server（via `uvx`，stdio 传输） |
| **前端** | Vue 3 · TypeScript · Vite · Ant Design Vue · 高德地图 JS API |

---

## 📁 项目结构

```
helloagents-trip-planner_LangChain/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── trip_planner_agent.py        # HelloAgents 多 Agent 规划器（主路径）
│   │   │   └── langchain_amap_agent.py      # LangChain ReAct Agent（扩展层）
│   │   ├── api/
│   │   │   ├── main.py                      # FastAPI 入口，注册所有路由
│   │   │   └── routes/
│   │   │       ├── trip.py                  # POST /api/trip/plan
│   │   │       ├── map.py                   # GET  /api/map/*
│   │   │       ├── poi.py                   # GET  /api/poi/*
│   │   │       ├── langchain_agent.py       # POST /debug/langchain-agent/invoke
│   │   │       ├── langchain_trip.py        # POST /debug/langchain-trip/plan
│   │   │       ├── debug_mcp.py             # GET  /debug/mcp/tools 等
│   │   │       └── debug_rag.py             # GET  /debug/rag/health|cities; POST /debug/rag/search|context
│   │   ├── rag/
│   │   │   ├── knowledge_base/              # 本地 Markdown 知识库（20 城市）
│   │   │   │   ├── beijing/                 # attractions.md food.md routes.md tips.md
│   │   │   │   ├── shanghai/
│   │   │   │   ├── chengdu/
│   │   │   │   └── ...（共 20 个城市）
│   │   │   ├── crawler/                     # 知识库爬虫模块
│   │   │   │   ├── city_config.py           # 20 城市 seed URL 配置
│   │   │   │   ├── fetcher.py               # httpx 抓取 + robots.txt 检查 + HTML 缓存
│   │   │   │   ├── parser.py                # trafilatura → BeautifulSoup 正文抽取
│   │   │   │   ├── cleaner.py               # 文本清洗
│   │   │   │   ├── summarizer.py            # LLM 整理为 Markdown 知识库
│   │   │   │   ├── markdown_writer.py       # 写入 knowledge_base/{slug}/{category}.md
│   │   │   │   ├── crawl_city.py            # 单城市 CLI（--city --categories --rebuild-index）
│   │   │   │   └── crawl_all_cities.py      # 批量 CLI（--fix-missing --check --inter-city-delay）
│   │   │   ├── build_index.py               # 构建/重建 FAISS 索引
│   │   │   ├── document_loader.py
│   │   │   ├── splitter.py
│   │   │   ├── embeddings.py
│   │   │   ├── vector_store.py
│   │   │   ├── retriever.py
│   │   │   ├── city_alias.py                # 城市别名映射（"北京" → "beijing"）
│   │   │   └── config.py                    # RAG 参数配置
│   │   ├── tools/
│   │   │   └── langchain_mcp_tools.py       # LangChain MCP 工具管理器（单例）
│   │   ├── services/
│   │   │   ├── amap_service.py
│   │   │   └── unsplash_service.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   └── config.py                        # 全局配置（pydantic-settings）
│   ├── storage/
│   │   ├── faiss_index/                     # FAISS 向量索引（index.faiss + index.pkl）
│   │   └── rag_crawler_cache/               # 爬虫 HTML 缓存
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── views/                           # Home.vue（表单） Result.vue（地图+行程）
│   │   ├── components/
│   │   ├── services/
│   │   │   └── api.ts                       # Axios 客户端（代理到 :8000）
│   │   └── types/
│   │       └── index.ts                     # TypeScript 类型（镜像 schemas.py）
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## 🚀 快速开始

### 前提条件

- Python 3.10+（推荐 conda 环境）
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) 已安装（用于启动 amap-mcp-server）
- 高德地图 API Key（Web 服务 API + Web 端 JS API 两种类型）
- 兼容 OpenAI API 的 LLM Key（阿里 DashScope / DeepSeek / OpenAI 等）

### 1. 克隆项目

```bash
git clone <repo-url>
cd helloagents-trip-planner_LangChain
```

### 2. 后端配置

```bash
cd backend

# 安装依赖（推荐 conda env: agent, Python 3.10）
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
```

编辑 `backend/.env`，填入以下关键配置：

```env
# LLM（以阿里 DashScope 为例）
LLM_MODEL_ID=qwen3.6-plus
LLM_API_KEY=sk-xxxxxxxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 高德地图
AMAP_API_KEY=your_amap_key

# 本地 Embedding 模型路径（或 HuggingFace 模型名）
EMBEDDING_MODEL_NAME=E:\path\to\bge-large-zh-v1.5
```

### 3. 构建 RAG 知识库索引

知识库 Markdown 文件已内置（`app/rag/knowledge_base/` 下 20 个城市），首次运行需构建向量索引：

```bash
cd backend
python -m app.rag.build_index
```

> 首次运行会加载 Embedding 模型，约需 1-2 分钟。后续启动直接读取缓存索引，无需重复构建。

### 4. 启动后端

```bash
python run.py
# 或
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/docs` 查看完整 API 文档。

### 5. 前端配置与启动

```bash
cd frontend
npm install

# 配置高德地图 JS API Key
cp .env.example .env
# 编辑 .env 填入 VITE_AMAP_KEY

npm run dev
```

访问 `http://localhost:5173`

---

## 📚 RAG 知识库

### 已内置城市（20 个）

| 区域 | 城市 |
|------|------|
| 华北 | 北京 |
| 华东 | 上海、杭州、南京、苏州 |
| 华南 | 广州、深圳、厦门、桂林、三亚 |
| 西南 | 成都、重庆、丽江、拉萨 |
| 西北 | 西安、乌鲁木齐 |
| 华中 | 武汉 |
| 华东山地 | 黄山、张家界 |
| 华北沿海 | 青岛 |

每个城市包含 4 个分类文件：`attractions.md` / `food.md` / `routes.md` / `tips.md`

### 扩充城市知识库（爬虫）

```bash
cd backend

# 检查哪些城市文件缺失
python -m app.rag.crawler.crawl_all_cities --check

# 补全所有缺失文件（HTML 已缓存，只重新调用 LLM）
python -m app.rag.crawler.crawl_all_cities --fix-missing --inter-city-delay 5

# 爬取单个城市（全量）
python -m app.rag.crawler.crawl_city --city chengdu --rebuild-index

# 新增城市：先在 city_config.py 添加配置，再运行
python -m app.rag.crawler.crawl_city --city newcity --rebuild-index
```

**爬虫合规说明**：强制检查 robots.txt（不允许则跳过）；默认使用维基百科公开页面；请求间隔 ≥ 2 秒；禁止递归抓站。

---

## 🔌 主要 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/trip/plan` | HelloAgents 多 Agent 旅行规划（主路径） |
| `GET` | `/api/map/poi` | POI 搜索 |
| `GET` | `/api/map/weather` | 天气查询 |
| `POST` | `/debug/langchain-agent/invoke` | LangChain ReAct Agent 调试 |
| `POST` | `/debug/langchain-trip/plan` | LangChain 旅行规划（扩展层） |
| `GET` | `/debug/mcp/tools` | 查看可用 MCP 工具列表 |
| `POST` | `/debug/mcp/call` | 直接调用单个 MCP 工具 |
| `GET` | `/debug/rag/health` | RAG 索引加载状态 |
| `GET` | `/debug/rag/cities` | 知识库已有城市列表 |
| `POST` | `/debug/rag/search` | RAG 向量检索（返回 chunks） |
| `POST` | `/debug/rag/context` | RAG 检索并格式化上下文 |

---

## 🔧 核心实现

### HelloAgents 多 Agent 规划（主路径）

```python
# app/agents/trip_planner_agent.py
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import MCPTool
from concurrent.futures import ThreadPoolExecutor

amap_tool = MCPTool(
    name="amap",
    server_command=["uvx", "amap-mcp-server"],
    env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
    auto_expand=True   # 展开为 16 个独立工具
)

# 景点、天气、住宿 Agent 并行调用，规划 Agent 综合结果
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {
        executor.submit(attraction_agent.run, prompt): "attraction",
        executor.submit(weather_agent.run, prompt):    "weather",
        executor.submit(hotel_agent.run, prompt):      "hotel",
    }
```

### LangChain ReAct Agent（扩展层）

```python
# app/agents/langchain_amap_agent.py
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(model=model, api_key=api_key, base_url=base_url)
tools = await get_langchain_mcp_tool_manager().get_tools()
agent = create_react_agent(llm, tools, prompt=system_prompt)
```

### RAG 检索

```python
# 构建索引（一次性）
python -m app.rag.build_index

# 检索使用
from app.rag.retriever import get_destination_rag_retriever
retriever = get_destination_rag_retriever()
docs = retriever.retrieve(query="西安 三日游 历史", city="西安", top_k=5)
```

---

## 🌐 环境变量说明

```env
# LLM（必填）
LLM_MODEL_ID=qwen3.6-plus           # 或 gpt-4o / deepseek-chat 等
LLM_API_KEY=sk-xxxxxxxx
LLM_BASE_URL=https://...            # OpenAI 兼容接口，留空则用 OpenAI 官方

# 高德地图（必填）
AMAP_API_KEY=your_key               # 后端 Web 服务 API Key
# 前端使用 VITE_AMAP_KEY（填入 frontend/.env）

# Embedding 模型（必填，用于 RAG）
EMBEDDING_MODEL_NAME=BAAI/bge-large-zh-v1.5   # 或本地绝对路径
HF_HOME=D:\models                             # HuggingFace 缓存目录（可选）

# 可选
UNSPLASH_ACCESS_KEY=...             # 景点图片（可留空）
AGENT_BACKEND=legacy                # legacy=HelloAgents / langchain=LangChain
```

---

## 🤝 贡献指南

欢迎提交 Pull Request 或 Issue。

新增城市知识库时，在 `backend/app/rag/crawler/city_config.py` 中添加城市配置，运行爬虫脚本后重建索引即可。

## 📜 开源协议

CC BY-NC-SA 4.0

## 🙏 致谢

- [HelloAgents 框架](https://github.com/jjyaoao/HelloAgents) — 本项目二次开发的基础框架
- [Hello-Agents 教程](https://github.com/datawhalechina/Hello-Agents) — 智能体学习资料
- [高德地图开放平台](https://lbs.amap.com/) — 地图与 POI 数据服务
- [amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) — 高德地图 MCP 服务器
- [LangChain](https://github.com/langchain-ai/langchain) / [LangGraph](https://github.com/langchain-ai/langgraph) — Agent 扩展框架
- [BAAI/bge-large-zh-v1.5](https://huggingface.co/BAAI/bge-large-zh-v1.5) — 中文向量 Embedding 模型

---

**HelloAgents 智能旅行助手** — 让旅行计划变得简单而智能 🌈
