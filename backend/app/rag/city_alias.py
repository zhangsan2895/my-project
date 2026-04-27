"""城市别名映射，用于 RAG 检索时过滤结果"""

CITY_ALIASES: dict[str, list[str]] = {
    "beijing": ["北京", "beijing", "bj"],
    "shanghai": ["上海", "shanghai", "sh"],
    "chengdu": ["成都", "chengdu", "cd"],
    "xian": ["西安", "xian", "xi'an", "xi an"],
    "guangzhou": ["广州", "guangzhou", "gz"],
    "shenzhen": ["深圳", "shenzhen", "sz"],
    "hangzhou": ["杭州", "hangzhou", "hz"],
    "chongqing": ["重庆", "chongqing", "cq"],
    "nanjing": ["南京", "nanjing", "nj"],
    "suzhou": ["苏州", "suzhou"],
    "guilin": ["桂林", "guilin"],
    "lijiang": ["丽江", "lijiang"],
}


def get_city_aliases(city: str) -> list[str]:
    """返回城市的所有别名（含原始输入）。

    先尝试精确匹配 key，再扫描所有 value 列表，找不到时返回原始城市名。
    """
    city_lower = city.strip().lower()

    # 直接匹配 key
    if city_lower in CITY_ALIASES:
        return CITY_ALIASES[city_lower]

    # 扫描 value 列表
    for canonical, aliases in CITY_ALIASES.items():
        if city_lower in [a.lower() for a in aliases]:
            return CITY_ALIASES[canonical]

    # 未找到，返回原始值，让调用方降级处理
    return [city]
