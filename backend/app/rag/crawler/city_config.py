"""城市爬虫 Seed URL 配置

数据源选取原则：
1. 维基百科（zh.wikipedia.org）— robots.txt 明确允许 User-agent: *
2. 官方文旅局/政府网站 — 如已确认 robots.txt 允许则保留，否则留空
3. 禁止使用马蜂窝、小红书、大众点评等强反爬或 UGC 平台

已配置城市（20 个）：
  beijing, shanghai, chengdu, xian, hangzhou, guangzhou, shenzhen,
  chongqing, suzhou, guilin, xiamen, sanya, lijiang, urumqi,
  zhangjiajie, huangshan, wuhan, nanjing, qingdao, lasa

如需新增城市，在此文件补充配置；如某 category 暂无可靠来源，保留空列表。
"""

CITY_CONFIGS: dict = {

    # ── 北京 ──────────────────────────────────────────────────────────────────
    "beijing": {
        "name": "北京",
        "slug": "beijing",
        "sources": {
            "attractions": [
                {"name": "维基百科·故宫博物院", "url": "https://zh.wikipedia.org/wiki/%E6%95%85%E5%AE%AB%E5%8D%9A%E7%89%A9%E9%99%A2", "type": "wiki"},
                {"name": "维基百科·颐和园", "url": "https://zh.wikipedia.org/wiki/%E9%A2%90%E5%92%8C%E5%9B%AD", "type": "wiki"},
                {"name": "维基百科·天坛", "url": "https://zh.wikipedia.org/wiki/%E5%A4%A9%E5%9D%9B", "type": "wiki"},
                {"name": "维基百科·中国国家博物馆", "url": "https://zh.wikipedia.org/wiki/%E4%B8%AD%E5%9B%BD%E5%9B%BD%E5%AE%B6%E5%8D%9A%E7%89%A9%E9%A6%86", "type": "wiki"},
                {"name": "维基百科·长城", "url": "https://zh.wikipedia.org/wiki/%E9%95%BF%E5%9F%8E", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·北京烤鸭", "url": "https://zh.wikipedia.org/wiki/%E5%8C%97%E4%BA%AC%E7%83%A4%E9%B8%AD", "type": "wiki"},
                {"name": "维基百科·京菜", "url": "https://zh.wikipedia.org/wiki/%E4%BA%AC%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·北京", "url": "https://zh.wikipedia.org/wiki/%E5%8C%97%E4%BA%AC", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·北京地铁", "url": "https://zh.wikipedia.org/wiki/%E5%8C%97%E4%BA%AC%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 上海 ──────────────────────────────────────────────────────────────────
    "shanghai": {
        "name": "上海",
        "slug": "shanghai",
        "sources": {
            "attractions": [
                {"name": "维基百科·外滩", "url": "https://zh.wikipedia.org/wiki/%E5%A4%96%E6%BB%A9", "type": "wiki"},
                {"name": "维基百科·豫园", "url": "https://zh.wikipedia.org/wiki/%E8%B1%AB%E5%9B%AD", "type": "wiki"},
                {"name": "维基百科·上海迪士尼乐园", "url": "https://zh.wikipedia.org/wiki/%E4%B8%8A%E6%B5%B7%E8%BF%AA%E5%A3%AB%E5%B0%BC%E4%B9%90%E5%9B%AD", "type": "wiki"},
                {"name": "维基百科·东方明珠广播电视塔", "url": "https://zh.wikipedia.org/wiki/%E4%B8%9C%E6%96%B9%E6%98%8E%E7%8F%A0%E5%A1%94", "type": "wiki"},
                {"name": "维基百科·上海博物馆", "url": "https://zh.wikipedia.org/wiki/%E4%B8%8A%E6%B5%B7%E5%8D%9A%E7%89%A9%E9%A6%86", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·本帮菜", "url": "https://zh.wikipedia.org/wiki/%E6%9C%AC%E5%B8%AE%E8%8F%9C", "type": "wiki"},
                {"name": "维基百科·南翔小笼包", "url": "https://zh.wikipedia.org/wiki/%E5%8D%97%E7%BF%94%E5%B0%8F%E7%AC%BC%E5%8C%85", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·上海", "url": "https://zh.wikipedia.org/wiki/%E4%B8%8A%E6%B5%B7", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·上海轨道交通", "url": "https://zh.wikipedia.org/wiki/%E4%B8%8A%E6%B5%B7%E8%BD%A8%E9%81%93%E4%BA%A4%E9%80%9A", "type": "wiki"},
            ],
        },
    },

    # ── 成都 ──────────────────────────────────────────────────────────────────
    "chengdu": {
        "name": "成都",
        "slug": "chengdu",
        "sources": {
            "attractions": [
                {"name": "维基百科·成都大熊猫繁育研究基地", "url": "https://zh.wikipedia.org/wiki/%E6%88%90%E9%83%BD%E5%A4%A7%E7%86%8A%E7%8C%AB%E7%B9%81%E8%82%B2%E7%A0%94%E7%A9%B6%E5%9F%BA%E5%9C%B0", "type": "wiki"},
                {"name": "维基百科·宽窄巷子", "url": "https://zh.wikipedia.org/wiki/%E5%AE%BD%E7%AA%84%E5%B7%B7%E5%AD%90", "type": "wiki"},
                {"name": "维基百科·武侯祠（成都）", "url": "https://zh.wikipedia.org/wiki/%E6%88%90%E9%83%BD%E6%AD%A6%E4%BE%AF%E7%A5%A0", "type": "wiki"},
                {"name": "维基百科·杜甫草堂", "url": "https://zh.wikipedia.org/wiki/%E6%9D%9C%E7%94%AB%E8%8D%89%E5%A0%82", "type": "wiki"},
                {"name": "维基百科·青城山", "url": "https://zh.wikipedia.org/wiki/%E9%9D%92%E5%9F%8E%E5%B1%B1", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·川菜", "url": "https://zh.wikipedia.org/wiki/%E5%B7%9D%E8%8F%9C", "type": "wiki"},
                {"name": "维基百科·火锅", "url": "https://zh.wikipedia.org/wiki/%E7%81%AB%E9%94%85", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·成都", "url": "https://zh.wikipedia.org/wiki/%E6%88%90%E9%83%BD", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·成都地铁", "url": "https://zh.wikipedia.org/wiki/%E6%88%90%E9%83%BD%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 西安 ──────────────────────────────────────────────────────────────────
    "xian": {
        "name": "西安",
        "slug": "xian",
        "sources": {
            "attractions": [
                {"name": "维基百科·兵马俑", "url": "https://zh.wikipedia.org/wiki/%E5%85%B5%E9%A9%AC%E4%BF%91", "type": "wiki"},
                {"name": "维基百科·大雁塔", "url": "https://zh.wikipedia.org/wiki/%E5%A4%A7%E9%9B%81%E5%A1%94", "type": "wiki"},
                {"name": "维基百科·西安城墙", "url": "https://zh.wikipedia.org/wiki/%E8%A5%BF%E5%AE%89%E5%9F%8E%E5%A2%99", "type": "wiki"},
                {"name": "维基百科·陕西历史博物馆", "url": "https://zh.wikipedia.org/wiki/%E9%99%95%E8%A5%BF%E5%8E%86%E5%8F%B2%E5%8D%9A%E7%89%A9%E9%A6%86", "type": "wiki"},
                {"name": "维基百科·华清池", "url": "https://zh.wikipedia.org/wiki/%E5%8D%8E%E6%B8%85%E6%B1%A0", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·肉夹馍", "url": "https://zh.wikipedia.org/wiki/%E8%82%89%E5%A4%B9%E9%A6%8D", "type": "wiki"},
                {"name": "维基百科·凉皮", "url": "https://zh.wikipedia.org/wiki/%E5%87%89%E7%9A%AE", "type": "wiki"},
                {"name": "维基百科·陕菜", "url": "https://zh.wikipedia.org/wiki/%E9%99%95%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·西安", "url": "https://zh.wikipedia.org/wiki/%E8%A5%BF%E5%AE%89", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·西安地铁", "url": "https://zh.wikipedia.org/wiki/%E8%A5%BF%E5%AE%89%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 杭州 ──────────────────────────────────────────────────────────────────
    "hangzhou": {
        "name": "杭州",
        "slug": "hangzhou",
        "sources": {
            "attractions": [
                {"name": "维基百科·西湖", "url": "https://zh.wikipedia.org/wiki/%E8%A5%BF%E6%B9%96", "type": "wiki"},
                {"name": "维基百科·灵隐寺", "url": "https://zh.wikipedia.org/wiki/%E7%81%B5%E9%9A%90%E5%AF%BA", "type": "wiki"},
                {"name": "维基百科·西溪国家湿地公园", "url": "https://zh.wikipedia.org/wiki/%E8%A5%BF%E6%BA%AA%E5%9B%BD%E5%AE%B6%E6%B9%BF%E5%9C%B0%E5%85%AC%E5%9B%AD", "type": "wiki"},
                {"name": "维基百科·雷峰塔", "url": "https://zh.wikipedia.org/wiki/%E9%9B%B7%E5%B3%B0%E5%A1%94", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·浙菜", "url": "https://zh.wikipedia.org/wiki/%E6%B5%99%E8%8F%9C", "type": "wiki"},
                {"name": "维基百科·龙井茶", "url": "https://zh.wikipedia.org/wiki/%E9%BE%99%E4%BA%95%E8%8C%B6", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·杭州", "url": "https://zh.wikipedia.org/wiki/%E6%9D%AD%E5%B7%9E", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·杭州地铁", "url": "https://zh.wikipedia.org/wiki/%E6%9D%AD%E5%B7%9E%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 广州 ──────────────────────────────────────────────────────────────────
    "guangzhou": {
        "name": "广州",
        "slug": "guangzhou",
        "sources": {
            "attractions": [
                {"name": "维基百科·广州塔", "url": "https://zh.wikipedia.org/wiki/%E5%B9%BF%E5%B7%9E%E5%A1%94", "type": "wiki"},
                {"name": "维基百科·白云山（广州）", "url": "https://zh.wikipedia.org/wiki/%E7%99%BD%E4%BA%91%E5%B1%B1_(%E5%B9%BF%E5%B7%9E)", "type": "wiki"},
                {"name": "维基百科·广州陈家祠", "url": "https://zh.wikipedia.org/wiki/%E5%B9%BF%E5%B7%9E%E9%99%88%E5%AE%B6%E7%A5%A0", "type": "wiki"},
                {"name": "维基百科·广州博物馆", "url": "https://zh.wikipedia.org/wiki/%E5%B9%BF%E5%B7%9E%E5%8D%9A%E7%89%A9%E9%A6%86", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·粤菜", "url": "https://zh.wikipedia.org/wiki/%E7%B2%A4%E8%8F%9C", "type": "wiki"},
                {"name": "维基百科·广式早茶", "url": "https://zh.wikipedia.org/wiki/%E5%B9%BF%E5%BC%8F%E6%97%A9%E8%8C%B6", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·广州", "url": "https://zh.wikipedia.org/wiki/%E5%B9%BF%E5%B7%9E", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·广州地铁", "url": "https://zh.wikipedia.org/wiki/%E5%B9%BF%E5%B7%9E%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 深圳 ──────────────────────────────────────────────────────────────────
    "shenzhen": {
        "name": "深圳",
        "slug": "shenzhen",
        "sources": {
            "attractions": [
                {"name": "维基百科·世界之窗（深圳）", "url": "https://zh.wikipedia.org/wiki/%E4%B8%96%E7%95%8C%E4%B9%8B%E7%AA%97_(%E6%B7%B1%E5%9C%B3)", "type": "wiki"},
                {"name": "维基百科·深圳湾公园", "url": "https://zh.wikipedia.org/wiki/%E6%B7%B1%E5%9C%B3%E6%B9%BE%E5%85%AC%E5%9B%AD", "type": "wiki"},
                {"name": "维基百科·大鹏所城", "url": "https://zh.wikipedia.org/wiki/%E5%A4%A7%E9%B9%8F%E6%89%80%E5%9F%8E", "type": "wiki"},
                {"name": "维基百科·深圳", "url": "https://zh.wikipedia.org/wiki/%E6%B7%B1%E5%9C%B3", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·粤菜", "url": "https://zh.wikipedia.org/wiki/%E7%B2%A4%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·深圳", "url": "https://zh.wikipedia.org/wiki/%E6%B7%B1%E5%9C%B3", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·深圳地铁", "url": "https://zh.wikipedia.org/wiki/%E6%B7%B1%E5%9C%B3%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 重庆 ──────────────────────────────────────────────────────────────────
    "chongqing": {
        "name": "重庆",
        "slug": "chongqing",
        "sources": {
            "attractions": [
                {"name": "维基百科·洪崖洞", "url": "https://zh.wikipedia.org/wiki/%E6%B4%AA%E5%B4%96%E6%B4%9E", "type": "wiki"},
                {"name": "维基百科·磁器口", "url": "https://zh.wikipedia.org/wiki/%E7%A3%81%E5%99%A8%E5%8F%A3", "type": "wiki"},
                {"name": "维基百科·大足石刻", "url": "https://zh.wikipedia.org/wiki/%E5%A4%A7%E8%B6%B3%E7%9F%B3%E5%88%BB", "type": "wiki"},
                {"name": "维基百科·武隆喀斯特", "url": "https://zh.wikipedia.org/wiki/%E6%AD%A6%E9%9A%86%E5%96%80%E6%96%AF%E7%89%B9", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·重庆火锅", "url": "https://zh.wikipedia.org/wiki/%E9%87%8D%E5%BA%86%E7%81%AB%E9%94%85", "type": "wiki"},
                {"name": "维基百科·渝菜", "url": "https://zh.wikipedia.org/wiki/%E6%B8%9D%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·重庆", "url": "https://zh.wikipedia.org/wiki/%E9%87%8D%E5%BA%86", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·重庆轨道交通", "url": "https://zh.wikipedia.org/wiki/%E9%87%8D%E5%BA%86%E8%BD%A8%E9%81%93%E4%BA%A4%E9%80%9A", "type": "wiki"},
            ],
        },
    },

    # ── 苏州 ──────────────────────────────────────────────────────────────────
    "suzhou": {
        "name": "苏州",
        "slug": "suzhou",
        "sources": {
            "attractions": [
                {"name": "维基百科·拙政园", "url": "https://zh.wikipedia.org/wiki/%E6%8B%99%E6%94%BF%E5%9B%AD", "type": "wiki"},
                {"name": "维基百科·留园", "url": "https://zh.wikipedia.org/wiki/%E7%95%99%E5%9B%AD", "type": "wiki"},
                {"name": "维基百科·虎丘", "url": "https://zh.wikipedia.org/wiki/%E8%99%8E%E4%B8%98", "type": "wiki"},
                {"name": "维基百科·苏州园林", "url": "https://zh.wikipedia.org/wiki/%E8%8B%8F%E5%B7%9E%E5%9B%AD%E6%9E%97", "type": "wiki"},
                {"name": "维基百科·周庄", "url": "https://zh.wikipedia.org/wiki/%E5%91%A8%E5%BA%84%E9%95%87", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·苏菜", "url": "https://zh.wikipedia.org/wiki/%E8%8B%8F%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·苏州", "url": "https://zh.wikipedia.org/wiki/%E8%8B%8F%E5%B7%9E", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·苏州轨道交通", "url": "https://zh.wikipedia.org/wiki/%E8%8B%8F%E5%B7%9E%E8%BD%A8%E9%81%93%E4%BA%A4%E9%80%9A", "type": "wiki"},
            ],
        },
    },

    # ── 桂林 ──────────────────────────────────────────────────────────────────
    "guilin": {
        "name": "桂林",
        "slug": "guilin",
        "sources": {
            "attractions": [
                {"name": "维基百科·漓江", "url": "https://zh.wikipedia.org/wiki/%E6%BC%93%E6%B1%9F", "type": "wiki"},
                {"name": "维基百科·象鼻山", "url": "https://zh.wikipedia.org/wiki/%E8%B1%A1%E9%BC%BB%E5%B1%B1", "type": "wiki"},
                {"name": "维基百科·阳朔县", "url": "https://zh.wikipedia.org/wiki/%E9%98%B3%E6%9C%94%E5%8E%BF", "type": "wiki"},
                {"name": "维基百科·龙脊梯田", "url": "https://zh.wikipedia.org/wiki/%E9%BE%99%E8%84%8A%E6%A2%AF%E7%94%B0", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·桂林米粉", "url": "https://zh.wikipedia.org/wiki/%E6%A1%82%E6%9E%97%E7%B1%B3%E7%B2%89", "type": "wiki"},
                {"name": "维基百科·桂菜", "url": "https://zh.wikipedia.org/wiki/%E6%A1%82%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·桂林", "url": "https://zh.wikipedia.org/wiki/%E6%A1%82%E6%9E%97", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·桂林", "url": "https://zh.wikipedia.org/wiki/%E6%A1%82%E6%9E%97", "type": "wiki"},
            ],
        },
    },

    # ── 厦门 ──────────────────────────────────────────────────────────────────
    "xiamen": {
        "name": "厦门",
        "slug": "xiamen",
        "sources": {
            "attractions": [
                {"name": "维基百科·鼓浪屿", "url": "https://zh.wikipedia.org/wiki/%E9%BC%93%E6%B5%AA%E5%B1%BF", "type": "wiki"},
                {"name": "维基百科·南普陀寺", "url": "https://zh.wikipedia.org/wiki/%E5%8D%97%E6%99%AE%E9%99%80%E5%AF%BA", "type": "wiki"},
                {"name": "维基百科·厦门大学", "url": "https://zh.wikipedia.org/wiki/%E5%8E%A6%E9%97%A8%E5%A4%A7%E5%AD%A6", "type": "wiki"},
                {"name": "维基百科·集美学村", "url": "https://zh.wikipedia.org/wiki/%E9%9B%86%E7%BE%8E%E5%AD%A6%E6%9D%91", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·闽菜", "url": "https://zh.wikipedia.org/wiki/%E9%97%BD%E8%8F%9C", "type": "wiki"},
                {"name": "维基百科·沙茶面", "url": "https://zh.wikipedia.org/wiki/%E6%B2%99%E8%8C%B6%E9%9D%A2", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·厦门", "url": "https://zh.wikipedia.org/wiki/%E5%8E%A6%E9%97%A8", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·厦门地铁", "url": "https://zh.wikipedia.org/wiki/%E5%8E%A6%E9%97%A8%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 三亚 ──────────────────────────────────────────────────────────────────
    "sanya": {
        "name": "三亚",
        "slug": "sanya",
        "sources": {
            "attractions": [
                {"name": "维基百科·亚龙湾", "url": "https://zh.wikipedia.org/wiki/%E4%BA%9A%E9%BE%99%E6%B9%BE", "type": "wiki"},
                {"name": "维基百科·天涯海角", "url": "https://zh.wikipedia.org/wiki/%E5%A4%A9%E6%B6%AF%E6%B5%B7%E8%A7%92", "type": "wiki"},
                {"name": "维基百科·蜈支洲岛", "url": "https://zh.wikipedia.org/wiki/%E8%9C%88%E6%94%AF%E6%B4%B2%E5%B2%9B", "type": "wiki"},
                {"name": "维基百科·南山文化旅游区", "url": "https://zh.wikipedia.org/wiki/%E5%8D%97%E5%B1%B1%E6%96%87%E5%8C%96%E6%97%85%E6%B8%B8%E5%8C%BA", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·海南菜", "url": "https://zh.wikipedia.org/wiki/%E7%90%BC%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·三亚", "url": "https://zh.wikipedia.org/wiki/%E4%B8%89%E4%BA%9A", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·三亚", "url": "https://zh.wikipedia.org/wiki/%E4%B8%89%E4%BA%9A", "type": "wiki"},
            ],
        },
    },

    # ── 丽江 ──────────────────────────────────────────────────────────────────
    "lijiang": {
        "name": "丽江",
        "slug": "lijiang",
        "sources": {
            "attractions": [
                {"name": "维基百科·丽江古城", "url": "https://zh.wikipedia.org/wiki/%E4%B8%BD%E6%B1%9F%E5%8F%A4%E5%9F%8E", "type": "wiki"},
                {"name": "维基百科·玉龙雪山", "url": "https://zh.wikipedia.org/wiki/%E7%8E%89%E9%BE%99%E9%9B%AA%E5%B1%B1", "type": "wiki"},
                {"name": "维基百科·泸沽湖", "url": "https://zh.wikipedia.org/wiki/%E6%B3%B8%E6%B2%BD%E6%B9%96", "type": "wiki"},
                {"name": "维基百科·纳西族", "url": "https://zh.wikipedia.org/wiki/%E7%BA%B3%E8%A5%BF%E6%97%8F", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·纳西族", "url": "https://zh.wikipedia.org/wiki/%E7%BA%B3%E8%A5%BF%E6%97%8F", "type": "wiki"},
                {"name": "维基百科·云南菜", "url": "https://zh.wikipedia.org/wiki/%E6%BB%87%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·丽江市", "url": "https://zh.wikipedia.org/wiki/%E4%B8%BD%E6%B1%9F%E5%B8%82", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·丽江市", "url": "https://zh.wikipedia.org/wiki/%E4%B8%BD%E6%B1%9F%E5%B8%82", "type": "wiki"},
            ],
        },
    },

    # ── 乌鲁木齐 ──────────────────────────────────────────────────────────────
    "urumqi": {
        "name": "乌鲁木齐",
        "slug": "urumqi",
        "sources": {
            "attractions": [
                {"name": "维基百科·天山天池", "url": "https://zh.wikipedia.org/wiki/%E5%A4%A9%E5%B1%B1%E5%A4%A9%E6%B1%A0", "type": "wiki"},
                {"name": "维基百科·新疆维吾尔自治区博物馆", "url": "https://zh.wikipedia.org/wiki/%E6%96%B0%E7%96%86%E7%BB%B4%E5%90%BE%E5%B0%94%E8%87%AA%E6%B2%BB%E5%8C%BA%E5%8D%9A%E7%89%A9%E9%A6%86", "type": "wiki"},
                {"name": "维基百科·乌鲁木齐", "url": "https://zh.wikipedia.org/wiki/%E4%B9%8C%E9%B2%81%E6%9C%A8%E9%BD%90", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·新疆菜", "url": "https://zh.wikipedia.org/wiki/%E6%96%B0%E7%96%86%E8%8F%9C", "type": "wiki"},
                {"name": "维基百科·手抓饭", "url": "https://zh.wikipedia.org/wiki/%E6%8A%93%E9%A5%AD", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·乌鲁木齐", "url": "https://zh.wikipedia.org/wiki/%E4%B9%8C%E9%B2%81%E6%9C%A8%E9%BD%90", "type": "wiki"},
                {"name": "维基百科·天山", "url": "https://zh.wikipedia.org/wiki/%E5%A4%A9%E5%B1%B1", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·乌鲁木齐地铁", "url": "https://zh.wikipedia.org/wiki/%E4%B9%8C%E9%B2%81%E6%9C%A8%E9%BD%90%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 张家界 ────────────────────────────────────────────────────────────────
    "zhangjiajie": {
        "name": "张家界",
        "slug": "zhangjiajie",
        "sources": {
            "attractions": [
                {"name": "维基百科·张家界国家森林公园", "url": "https://zh.wikipedia.org/wiki/%E5%BC%A0%E5%AE%B6%E7%95%8C%E5%9B%BD%E5%AE%B6%E6%A3%AE%E6%9E%97%E5%85%AC%E5%9B%AD", "type": "wiki"},
                {"name": "维基百科·天门山（张家界）", "url": "https://zh.wikipedia.org/wiki/%E5%A4%A9%E9%97%A8%E5%B1%B1_(%E5%BC%A0%E5%AE%B6%E7%95%8C)", "type": "wiki"},
                {"name": "维基百科·武陵源", "url": "https://zh.wikipedia.org/wiki/%E6%AD%A6%E9%99%B5%E6%BA%90%E9%A3%8E%E6%99%AF%E5%90%8D%E8%83%9C%E5%8C%BA%E6%9A%A8%E5%BC%A0%E5%AE%B6%E7%95%8C%E5%9B%BD%E5%AE%B6%E6%A3%AE%E6%9E%97%E5%85%AC%E5%9B%AD", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·湘菜", "url": "https://zh.wikipedia.org/wiki/%E6%B9%98%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·张家界市", "url": "https://zh.wikipedia.org/wiki/%E5%BC%A0%E5%AE%B6%E7%95%8C%E5%B8%82", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·张家界市", "url": "https://zh.wikipedia.org/wiki/%E5%BC%A0%E5%AE%B6%E7%95%8C%E5%B8%82", "type": "wiki"},
            ],
        },
    },

    # ── 黄山 ──────────────────────────────────────────────────────────────────
    "huangshan": {
        "name": "黄山",
        "slug": "huangshan",
        "sources": {
            "attractions": [
                {"name": "维基百科·黄山", "url": "https://zh.wikipedia.org/wiki/%E9%BB%84%E5%B1%B1", "type": "wiki"},
                {"name": "维基百科·宏村", "url": "https://zh.wikipedia.org/wiki/%E5%AE%8F%E6%9D%91", "type": "wiki"},
                {"name": "维基百科·西递村", "url": "https://zh.wikipedia.org/wiki/%E8%A5%BF%E9%80%92%E6%9D%91", "type": "wiki"},
                {"name": "维基百科·皖南古村落", "url": "https://zh.wikipedia.org/wiki/%E7%9A%96%E5%8D%97%E5%8F%A4%E6%9D%91%E8%90%BD", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·徽菜", "url": "https://zh.wikipedia.org/wiki/%E5%BE%BD%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·黄山市", "url": "https://zh.wikipedia.org/wiki/%E9%BB%84%E5%B1%B1%E5%B8%82", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·黄山", "url": "https://zh.wikipedia.org/wiki/%E9%BB%84%E5%B1%B1", "type": "wiki"},
            ],
        },
    },

    # ── 武汉 ──────────────────────────────────────────────────────────────────
    "wuhan": {
        "name": "武汉",
        "slug": "wuhan",
        "sources": {
            "attractions": [
                {"name": "维基百科·黄鹤楼", "url": "https://zh.wikipedia.org/wiki/%E9%BB%84%E9%B9%A4%E6%A5%BC", "type": "wiki"},
                {"name": "维基百科·东湖（武汉）", "url": "https://zh.wikipedia.org/wiki/%E4%B8%9C%E6%B9%96_(%E6%AD%A6%E6%B1%89)", "type": "wiki"},
                {"name": "维基百科·武汉大学", "url": "https://zh.wikipedia.org/wiki/%E6%AD%A6%E6%B1%89%E5%A4%A7%E5%AD%A6", "type": "wiki"},
                {"name": "维基百科·湖北省博物馆", "url": "https://zh.wikipedia.org/wiki/%E6%B9%96%E5%8C%97%E7%9C%81%E5%8D%9A%E7%89%A9%E9%A6%86", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·热干面", "url": "https://zh.wikipedia.org/wiki/%E7%83%AD%E5%B9%B2%E9%9D%A2", "type": "wiki"},
                {"name": "维基百科·湖北菜", "url": "https://zh.wikipedia.org/wiki/%E6%B9%96%E5%8C%97%E8%8F%9C", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·武汉", "url": "https://zh.wikipedia.org/wiki/%E6%AD%A6%E6%B1%89", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·武汉地铁", "url": "https://zh.wikipedia.org/wiki/%E6%AD%A6%E6%B1%89%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 南京 ──────────────────────────────────────────────────────────────────
    "nanjing": {
        "name": "南京",
        "slug": "nanjing",
        "sources": {
            "attractions": [
                {"name": "维基百科·中山陵", "url": "https://zh.wikipedia.org/wiki/%E4%B8%AD%E5%B1%B1%E9%99%B5", "type": "wiki"},
                {"name": "维基百科·南京夫子庙", "url": "https://zh.wikipedia.org/wiki/%E5%A4%AB%E5%AD%90%E5%BA%99_(%E5%8D%97%E4%BA%AC)", "type": "wiki"},
                {"name": "维基百科·明孝陵", "url": "https://zh.wikipedia.org/wiki/%E6%98%8E%E5%AD%9D%E9%99%B5", "type": "wiki"},
                {"name": "维基百科·秦淮河", "url": "https://zh.wikipedia.org/wiki/%E7%A7%A6%E6%B7%AE%E6%B2%B3", "type": "wiki"},
                {"name": "维基百科·南京博物院", "url": "https://zh.wikipedia.org/wiki/%E5%8D%97%E4%BA%AC%E5%8D%9A%E7%89%A9%E9%99%A2", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·淮扬菜", "url": "https://zh.wikipedia.org/wiki/%E6%B7%AE%E6%89%AC%E8%8F%9C", "type": "wiki"},
                {"name": "维基百科·盐水鸭", "url": "https://zh.wikipedia.org/wiki/%E7%9B%90%E6%B0%B4%E9%B8%AD", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·南京", "url": "https://zh.wikipedia.org/wiki/%E5%8D%97%E4%BA%AC", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·南京地铁", "url": "https://zh.wikipedia.org/wiki/%E5%8D%97%E4%BA%AC%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 青岛 ──────────────────────────────────────────────────────────────────
    "qingdao": {
        "name": "青岛",
        "slug": "qingdao",
        "sources": {
            "attractions": [
                {"name": "维基百科·崂山", "url": "https://zh.wikipedia.org/wiki/%E5%B4%82%E5%B1%B1", "type": "wiki"},
                {"name": "维基百科·青岛啤酒博物馆", "url": "https://zh.wikipedia.org/wiki/%E9%9D%92%E5%B2%9B%E5%95%A4%E9%85%92%E5%8D%9A%E7%89%A9%E9%A6%86", "type": "wiki"},
                {"name": "维基百科·栈桥（青岛）", "url": "https://zh.wikipedia.org/wiki/%E6%A0%88%E6%A1%A5_(%E9%9D%92%E5%B2%9B)", "type": "wiki"},
                {"name": "维基百科·八大关（青岛）", "url": "https://zh.wikipedia.org/wiki/%E5%85%AB%E5%A4%A7%E5%85%B3_(%E9%9D%92%E5%B2%9B)", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·鲁菜", "url": "https://zh.wikipedia.org/wiki/%E9%B2%81%E8%8F%9C", "type": "wiki"},
                {"name": "维基百科·青岛啤酒", "url": "https://zh.wikipedia.org/wiki/%E9%9D%92%E5%B2%9B%E5%95%A4%E9%85%92", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·青岛", "url": "https://zh.wikipedia.org/wiki/%E9%9D%92%E5%B2%9B", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·青岛地铁", "url": "https://zh.wikipedia.org/wiki/%E9%9D%92%E5%B2%9B%E5%9C%B0%E9%93%81", "type": "wiki"},
            ],
        },
    },

    # ── 拉萨 ──────────────────────────────────────────────────────────────────
    "lasa": {
        "name": "拉萨",
        "slug": "lasa",
        "sources": {
            "attractions": [
                {"name": "维基百科·布达拉宫", "url": "https://zh.wikipedia.org/wiki/%E5%B8%83%E8%BE%BE%E6%8B%89%E5%AE%AB", "type": "wiki"},
                {"name": "维基百科·大昭寺", "url": "https://zh.wikipedia.org/wiki/%E5%A4%A7%E6%98%AD%E5%AF%BA", "type": "wiki"},
                {"name": "维基百科·纳木错", "url": "https://zh.wikipedia.org/wiki/%E7%BA%B3%E6%9C%A8%E9%94%99", "type": "wiki"},
                {"name": "维基百科·色拉寺", "url": "https://zh.wikipedia.org/wiki/%E8%89%B2%E6%8B%89%E5%AF%BA", "type": "wiki"},
            ],
            "food": [
                {"name": "维基百科·藏餐", "url": "https://zh.wikipedia.org/wiki/%E8%97%8F%E9%A4%90", "type": "wiki"},
                {"name": "维基百科·酥油茶", "url": "https://zh.wikipedia.org/wiki/%E9%85%A5%E6%B2%B9%E8%8C%B6", "type": "wiki"},
            ],
            "routes": [
                {"name": "维基百科·拉萨", "url": "https://zh.wikipedia.org/wiki/%E6%8B%89%E8%90%A8", "type": "wiki"},
            ],
            "tips": [
                {"name": "维基百科·高原病", "url": "https://zh.wikipedia.org/wiki/%E9%AB%98%E5%B1%B1%E7%97%85", "type": "wiki"},
                {"name": "维基百科·拉萨", "url": "https://zh.wikipedia.org/wiki/%E6%8B%89%E8%90%A8", "type": "wiki"},
            ],
        },
    },
}
