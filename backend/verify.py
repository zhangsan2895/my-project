"""
Phase 1 + Phase 2 验收测试脚本

用法（在 backend/ 目录下运行，服务器必须已启动）：
    python verify.py

或者单独运行某一项：
    python verify.py imports   # 仅静态导入检查（不需要服务器）
    python verify.py server    # 服务器基础检查
    python verify.py phase1    # Phase 1 MCP 工具检查
    python verify.py phase2    # Phase 2 LangChain 规划（耗时较长）
    python verify.py legacy    # 原有接口回归检查（耗时较长）
"""

import sys
import json
import time
import textwrap
from typing import Any

# ── 颜色输出 ─────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):    print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg):  print(f"  {RED}✗{RESET} {msg}"); return False
def warn(msg):  print(f"  {YELLOW}△{RESET} {msg}")
def info(msg):  print(f"  {CYAN}·{RESET} {msg}")
def header(msg): print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}\n{BOLD}  {msg}{RESET}\n{'─'*60}")

BASE_URL = "http://localhost:8000"
TIMEOUT  = 120  # 秒，Agent 调用耗时较长

# ─────────────────────────────────────────────────────────────────────────────
# 1. 静态导入检查（不需要服务器）
# ─────────────────────────────────────────────────────────────────────────────

def check_imports() -> bool:
    header("CHECK 1 — 静态导入（不需要服务器）")
    passed = True

    checks = [
        ("langchain_mcp_adapters.client", "MultiServerMCPClient"),
        ("langchain_openai",              "ChatOpenAI"),
        ("langgraph.prebuilt",            "create_react_agent"),
        ("langchain_core.tools",          "BaseTool"),
        ("langchain_core.messages",       "SystemMessage"),
    ]

    for module, symbol in checks:
        try:
            mod = __import__(module, fromlist=[symbol])
            getattr(mod, symbol)
            ok(f"{module}.{symbol}")
        except Exception as e:
            fail(f"{module}.{symbol}  →  {e}")
            passed = False

    # 检查项目内部模块（需要在 backend/ 目录下运行）
    sys.path.insert(0, ".")
    internal = [
        ("app.utils.json_utils",                          "loads_json, extract_json_text"),
        ("app.agents.langchain.base",                     "BaseLangChainAgent, build_chat_openai"),
        ("app.agents.langchain.attraction_agent",         "AttractionSearchAgent"),
        ("app.agents.langchain.weather_agent",            "WeatherQueryAgent"),
        ("app.agents.langchain.hotel_agent",              "HotelSearchAgent"),
        ("app.agents.langchain.planner_agent",            "PlannerAgent"),
        ("app.agents.langchain.trip_planner_agent",       "LangChainTripPlannerAgent, get_langchain_trip_planner_agent"),
        ("app.api.routes.langchain_trip",                 "router"),
        ("app.tools.langchain_mcp_tools",                 "get_langchain_mcp_tool_manager"),
    ]
    for module, symbols in internal:
        try:
            mod = __import__(module, fromlist=symbols.split(","))
            for sym in [s.strip() for s in symbols.split(",")]:
                getattr(mod, sym)
            ok(f"{module}  [{symbols}]")
        except Exception as e:
            fail(f"{module}  →  {e}")
            passed = False

    return passed


# ─────────────────────────────────────────────────────────────────────────────
# 2. 服务器基础检查
# ─────────────────────────────────────────────────────────────────────────────

def check_server() -> bool:
    import urllib.request, urllib.error
    header("CHECK 2 — 服务器基础")
    passed = True

    endpoints = [
        ("GET", "/",                 None),
        ("GET", "/health",           None),
        ("GET", "/api/trip/health",  None),
    ]

    for method, path, _ in endpoints:
        url = BASE_URL + path
        try:
            req = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                ok(f"{method} {path}  →  {data}")
        except Exception as e:
            fail(f"{method} {path}  →  {e}")
            passed = False

    # 确认 Phase 2 路由已注册
    try:
        req = urllib.request.Request(f"{BASE_URL}/openapi.json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            spec = json.loads(resp.read())
        paths = list(spec.get("paths", {}).keys())
        required_paths = [
            "/api/debug/mcp/tools",
            "/api/debug/mcp/call",
            "/api/debug/langchain-trip/plan",
            "/api/trip/plan",
        ]
        for p in required_paths:
            if p in paths:
                ok(f"路由已注册: {p}")
            else:
                fail(f"路由缺失: {p}")
                passed = False
    except Exception as e:
        fail(f"OpenAPI spec 读取失败: {e}")
        passed = False

    return passed


# ─────────────────────────────────────────────────────────────────────────────
# 3. Phase 1 — MCP 工具检查
# ─────────────────────────────────────────────────────────────────────────────

def _post(path: str, body: dict, timeout: int = TIMEOUT) -> Any:
    import urllib.request
    url = BASE_URL + path
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _get(path: str, timeout: int = 15) -> Any:
    import urllib.request
    url = BASE_URL + path
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read())


def check_phase1() -> bool:
    header("CHECK 3 — Phase 1 MCP 工具")
    passed = True

    # 3a. 工具列表
    try:
        result = _get("/api/debug/mcp/tools")
        total = result.get("total", 0)
        tools = [t["name"] for t in result.get("tools", [])]
        if total > 0:
            ok(f"GET /api/debug/mcp/tools  →  {total} 个工具加载成功")
        else:
            fail("GET /api/debug/mcp/tools  →  未加载到任何工具")
            passed = False

        # 验证关键工具存在
        key_tools = {"maps_text_search": False, "maps_weather": False}
        for name in tools:
            for key in key_tools:
                if key in name or name == key:
                    key_tools[key] = True
        for key, found in key_tools.items():
            if found:
                ok(f"  关键工具存在: {key}")
            else:
                # 模糊搜索
                substr = key.split("_")[-1]  # text_search 或 weather
                fuzzy = [t for t in tools if substr in t]
                if fuzzy:
                    warn(f"  精确工具 '{key}' 未找到，但有模糊匹配: {fuzzy}")
                else:
                    fail(f"  关键工具缺失: {key}  可用工具: {tools}")
                    passed = False

        info(f"  工具列表: {tools}")

    except Exception as e:
        fail(f"GET /api/debug/mcp/tools  →  {e}")
        passed = False
        return passed  # 工具都没加载，后续无法继续

    # 3b. 直接调用工具
    try:
        result = _post("/api/debug/mcp/call", {
            "name": "maps_text_search",
            "arguments": {"keywords": "故宫", "city": "北京"},
        })
        if result.get("success"):
            snippet = str(result.get("result", ""))[:150]
            ok(f"POST /api/debug/mcp/call maps_text_search  →  {snippet}…")
        else:
            fail(f"POST /api/debug/mcp/call  →  success=False: {result}")
            passed = False
    except Exception as e:
        fail(f"POST /api/debug/mcp/call  →  {e}")
        passed = False

    return passed


# ─────────────────────────────────────────────────────────────────────────────
# 4. Phase 2 — LangChain 旅行规划
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_REQUEST = {
    "city": "大连",
    "start_date": "2026-04-27",
    "end_date": "2026-04-27",
    "travel_days": 1,
    "transportation": "公共交通",
    "accommodation": "经济型酒店",
    "preferences": ["自然风光"],
    "free_text_input": "",
}


def check_phase2() -> bool:
    header("CHECK 4 — Phase 2 LangChain 旅行规划（耗时较长，请耐心等待）")
    passed = True

    info("发送请求到 POST /api/debug/langchain-trip/plan ...")
    t0 = time.time()
    try:
        result = _post("/api/debug/langchain-trip/plan", SAMPLE_REQUEST, timeout=300)
        elapsed = time.time() - t0

        if not result.get("success"):
            fail(f"success=False: {result.get('message', result)}")
            return False

        ok(f"请求成功，耗时 {elapsed:.1f}s")

        data = result.get("data", {})

        # 校验顶层字段
        for field in ["city", "start_date", "end_date", "days", "weather_info", "overall_suggestions"]:
            if field in data:
                ok(f"  字段存在: {field} = {str(data[field])[:80]}")
            else:
                fail(f"  缺少字段: {field}")
                passed = False

        # 校验 days 结构
        days = data.get("days", [])
        if days:
            day0 = days[0]
            for f in ["date", "day_index", "attractions", "meals", "transportation", "accommodation"]:
                if f in day0:
                    ok(f"  days[0].{f} 存在")
                else:
                    fail(f"  days[0].{f} 缺失")
                    passed = False

            # 校验 attraction.location 必填字段
            attractions = day0.get("attractions", [])
            if attractions:
                loc = attractions[0].get("location", {})
                if "longitude" in loc and "latitude" in loc:
                    ok(f"  attraction.location = {loc}")
                else:
                    fail(f"  attraction.location 格式错误: {loc}")
                    passed = False
            else:
                warn("  days[0].attractions 为空（可能是 LLM 未搜到坐标）")

            # 校验 meals
            meals = day0.get("meals", [])
            meal_types = {m.get("type") for m in meals}
            for t in ["breakfast", "lunch", "dinner"]:
                if t in meal_types:
                    ok(f"  meals 包含 {t}")
                else:
                    warn(f"  meals 缺少 {t}")

        # weather_info
        weather = data.get("weather_info", [])
        if weather:
            ok(f"  weather_info[0] = {weather[0]}")
        else:
            warn("  weather_info 为空（工具可能超出预报范围）")

    except Exception as e:
        elapsed = time.time() - t0
        fail(f"POST /api/debug/langchain-trip/plan 失败 ({elapsed:.1f}s): {e}")
        passed = False

    return passed


# ─────────────────────────────────────────────────────────────────────────────
# 5. 原有接口回归检查（legacy 后端）
# ─────────────────────────────────────────────────────────────────────────────

def check_legacy() -> bool:
    header("CHECK 5 — 原有 /api/trip/plan 回归（legacy 后端，耗时较长）")
    passed = True

    info("发送请求到 POST /api/trip/plan (AGENT_BACKEND=legacy) ...")
    t0 = time.time()
    try:
        result = _post("/api/trip/plan", SAMPLE_REQUEST, timeout=300)
        elapsed = time.time() - t0

        if result.get("success"):
            city = result.get("data", {}).get("city", "?")
            ok(f"原有接口正常，city={city}，耗时 {elapsed:.1f}s")
        else:
            fail(f"success=False: {result}")
            passed = False

    except Exception as e:
        elapsed = time.time() - t0
        fail(f"POST /api/trip/plan 失败 ({elapsed:.1f}s): {e}")
        passed = False

    return passed


# ─────────────────────────────────────────────────────────────────────────────
# 主函数
# ─────────────────────────────────────────────────────────────────────────────

CHECKS = {
    "imports": check_imports,
    "server":  check_server,
    "phase1":  check_phase1,
    "phase2":  check_phase2,
    "legacy":  check_legacy,
}

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    if target == "all":
        selected = list(CHECKS.keys())
    elif target in CHECKS:
        selected = [target]
    else:
        print(f"未知参数: {target}，可选: {list(CHECKS.keys())} 或 all")
        sys.exit(1)

    results = {}
    for name in selected:
        try:
            results[name] = CHECKS[name]()
        except Exception as e:
            print(f"\n{RED}CHECK {name} 抛出未捕获异常: {e}{RESET}")
            results[name] = False

    # 汇总
    print(f"\n{'='*60}")
    print(f"{BOLD}  验收结果汇总{RESET}")
    print(f"{'='*60}")
    all_pass = True
    for name, passed in results.items():
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  {status}  {name}")
        if not passed:
            all_pass = False

    print()
    if all_pass:
        print(f"{GREEN}{BOLD}  ✅ 所有检查通过！{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}  ❌ 有检查项未通过，请查看上方详情。{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
