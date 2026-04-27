"""LLM 摘要生成器

将爬取并清洗后的原始文本整理为适合 RAG 检索的 Markdown 格式知识库。

LLM 配置复用项目已有约定：
  - 环境变量 LLM_API_KEY 或 OPENAI_API_KEY
  - 环境变量 LLM_BASE_URL（可选，不设置则使用 OpenAI 默认）
  - 环境变量 LLM_MODEL_ID（可选，默认 gpt-4o）
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# ── 分类专属指令 ──────────────────────────────────────────────────────────────

_CATEGORY_INSTRUCTIONS: dict[str, str] = {
    "attractions": """
整理该城市的核心景点知识库，格式要求：
- 每个景点作为独立二级标题（## 景点名）
- 每个景点下包含：基本信息、适合人群、建议游览时长、行程组合建议、注意事项
- 如资料未提及票价或预约要求，不要编造
- 不要列出太多景点，优先覆盖最具代表性的 5-8 个
""",
    "food": """
整理该城市的特色餐饮知识库，格式要求：
- 先概述地方菜系风格
- 每类特色食物或餐饮区域作为独立二级标题
- 每项包含：食物特点、推荐餐厅或区域、预算参考、适合人群、避坑建议
- 如资料未提及具体价格，不要编造数字
""",
    "routes": """
整理该城市的行程路线知识库，格式要求：
- 提供一日游、二日游、三日游方案
- 针对不同群体（亲子、老人、摄影、低强度）给出变体建议
- 雨天/高温替代方案
- 公共交通建议
- 不要编造具体实时交通耗时、票价和距离；若资料未提及则不写
- 路线内容只能基于输入资料中提到的景点和区域关系整理
""",
    "tips": """
整理该城市的旅行实用注意事项，格式要求：
- 分节覆盖：景点预约、交通出行、季节天气、节假日建议、预算参考、安全注意、亲子/老人特别提示
- 使用简短条目，适合快速查找
- 如资料未提及具体数字或规定，不要编造
""",
}

_BASE_PROMPT = """你是一位专业旅行知识库编辑。请根据以下从公开网页采集的原始资料，为城市「{city_name}」整理「{category_label}」类别的旅行知识库 Markdown 文档。

**严格要求（必须遵守）：**
1. 只能基于提供的输入资料整理，禁止编造任何未提及的事实（包括票价、耗时、距离、评分等）。
2. 如果资料中未提及某项信息，直接省略，不要用"暂无"或"待补充"占位。
3. 输出纯中文 Markdown，不要输出代码块（``` 包裹的代码块）。
4. 文档开头使用以下固定格式的元数据头：

# {city_name}{category_label}知识库

city: {city_name}
category: {category_slug}
tags: {tags}

5. 段落简洁，标题清晰，适合 RAG 检索（避免长篇连续段落）。
6. 文档末尾必须添加「## 资料来源」小节，列出所有参考 URL（格式：- 来源名称：URL）。

{category_instructions}

---

以下是原始资料（共 {source_count} 条）：

{raw_content}

---

请直接输出 Markdown 内容，不要有任何额外说明或包裹。"""

_CATEGORY_LABELS = {
    "attractions": "核心景点",
    "food": "特色餐饮",
    "routes": "行程路线",
    "tips": "旅行贴士",
}

_CATEGORY_TAGS = {
    "attractions": "景点, 旅游, 观光, 打卡",
    "food": "美食, 餐饮, 特色菜, 小吃",
    "routes": "行程, 路线, 一日游, 二日游, 三日游",
    "tips": "攻略, 实用, 预约, 交通, 天气, 预算",
}


def _build_prompt(city_name: str, category: str, raw_texts: list[dict]) -> str:
    raw_content_parts: list[str] = []
    for i, item in enumerate(raw_texts, 1):
        part = (
            f"### 资料 {i}：{item.get('source_name', '未知来源')}\n"
            f"来源 URL：{item.get('url', '')}\n\n"
            f"{item.get('text', '').strip()}"
        )
        raw_content_parts.append(part)

    return _BASE_PROMPT.format(
        city_name=city_name,
        category_label=_CATEGORY_LABELS.get(category, category),
        category_slug=category,
        tags=_CATEGORY_TAGS.get(category, ""),
        category_instructions=_CATEGORY_INSTRUCTIONS.get(category, ""),
        source_count=len(raw_texts),
        raw_content="\n\n---\n\n".join(raw_content_parts),
    )


def _get_llm():
    """复用项目 LLM 配置创建 ChatOpenAI 实例。"""
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    base_url: Optional[str] = os.getenv("LLM_BASE_URL") or None
    model = os.getenv("LLM_MODEL_ID") or "gpt-4o"

    kwargs: dict = {"model": model, "api_key": api_key, "temperature": 0.2}
    if base_url:
        kwargs["base_url"] = base_url

    return ChatOpenAI(**kwargs)


def summarize_to_markdown(
    city_name: str,
    category: str,
    raw_texts: list[dict],
) -> str:
    """
    调用 LLM 将原始文本整理为 Markdown 知识库文档。

    Args:
        city_name: 城市中文名，如"上海"
        category: 分类，attractions / food / routes / tips
        raw_texts: 原始文本列表，每项包含 source_name、url、text

    Returns:
        Markdown 字符串
    """
    if not raw_texts:
        raise ValueError(f"raw_texts 为空，无法生成 {city_name}/{category} 知识库")

    prompt = _build_prompt(city_name, category, raw_texts)
    logger.info("调用 LLM 生成 %s/%s 知识库（原始资料 %d 条）", city_name, category, len(raw_texts))

    llm = _get_llm()
    response = llm.invoke(prompt)

    content = response.content if hasattr(response, "content") else str(response)
    return content.strip()
