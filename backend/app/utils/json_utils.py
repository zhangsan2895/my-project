"""JSON 解析工具

提供从 LLM 文本输出中提取并解析 JSON 的工具函数，
支持被 Markdown 代码块包裹的 JSON，以及裸 JSON object / array。
"""

import json
import re
from typing import Any


def extract_json_text(text: str) -> str:
    """从 LLM 输出文本中提取 JSON 字符串。

    按优先级尝试：
    1. ```json ... ``` 代码块
    2. ``` ... ``` 代码块（无语言标注）
    3. 最外层 JSON object  { ... }
    4. 最外层 JSON array   [ ... ]

    Args:
        text: LLM 输出的原始文本。

    Returns:
        提取到的 JSON 字符串。

    Raises:
        ValueError: 未找到任何 JSON 结构时。
    """
    # 1. ```json ... ``` 或 ``` ... ```
    match = re.search(r"```(?:json)?\s*([\[\{][\s\S]*?[\]\}])\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 2. 最外层 JSON object（贪婪匹配从第一个 { 到最后一个 }）
    obj_start = text.find("{")
    obj_end = text.rfind("}")
    if obj_start != -1 and obj_end > obj_start:
        candidate = text[obj_start : obj_end + 1]
        # 快速验证（不做完整解析）
        if _looks_like_json(candidate):
            return candidate

    # 3. 最外层 JSON array
    arr_start = text.find("[")
    arr_end = text.rfind("]")
    if arr_start != -1 and arr_end > arr_start:
        candidate = text[arr_start : arr_end + 1]
        if _looks_like_json(candidate):
            return candidate

    raise ValueError(
        f"在文本中未找到 JSON 结构。文本片段（前 300 字符）: {text[:300]!r}"
    )


def loads_json(text: str) -> Any:
    """从 LLM 输出文本中提取并解析 JSON。

    Args:
        text: LLM 输出的原始文本。

    Returns:
        解析后的 Python 对象（dict 或 list）。

    Raises:
        ValueError: 提取失败或 JSON 格式错误时，消息包含原始输出片段。
    """
    json_text = extract_json_text(text)
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON 解析失败: {exc}\n"
            f"提取的内容（前 400 字符）: {json_text[:400]!r}"
        ) from exc


def _looks_like_json(text: str) -> bool:
    """粗略判断字符串是否像 JSON（用于过滤误匹配）。"""
    stripped = text.strip()
    return (stripped.startswith("{") and stripped.endswith("}")) or (
        stripped.startswith("[") and stripped.endswith("]")
    )
