"""文本清洗器

清理多余空行、空格、HTML 残留字符，保留段落结构。
"""

import re


def clean_text(text: str) -> str:
    """
    清理抽取的正文文本：
    - 替换 &nbsp; 及全角空格
    - 合并连续空白行（保留最多一个空行）
    - 去除行首行尾多余空格
    - 去除零宽字符
    """
    # 零宽字符
    text = re.sub(r"[​‌‍﻿]", "", text)

    # HTML 实体
    text = text.replace("&nbsp;", " ").replace("\xa0", " ")

    # 行处理
    lines = text.splitlines()
    cleaned_lines: list[str] = []
    blank_count = 0

    for line in lines:
        line = line.strip()
        if not line:
            blank_count += 1
            if blank_count <= 1:
                cleaned_lines.append("")
        else:
            blank_count = 0
            # 合并行内多余空格
            line = re.sub(r" {2,}", " ", line)
            cleaned_lines.append(line)

    # 去掉首尾空行
    while cleaned_lines and not cleaned_lines[0]:
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1]:
        cleaned_lines.pop()

    return "\n".join(cleaned_lines)
