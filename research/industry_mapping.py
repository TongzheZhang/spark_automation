"""
期货品种 → Alpha派股票行业名称映射
- 为 Alpha派 Mode 11（行业一页纸）提供行业名称输入
- 支持品种→行业、行业→品种双向查询
"""

from typing import List, Dict, Set, Optional


# 期货品种代码 → Alpha派行业名称映射
# Alpha派 Mode 11 需要股票行业名称，此处建立映射关系
COMMODITY_TO_INDUSTRY: Dict[str, str] = {
    # === 黑色系 ===
    "RB": "钢铁",
    "HC": "钢铁",
    "I": "钢铁",
    "J": "煤炭",
    "JM": "煤炭",
    # === 有色金属 ===
    "CU": "有色金属",
    "AL": "有色金属",
    "ZN": "有色金属",
    "NI": "有色金属",
    "SN": "有色金属",
    "PB": "有色金属",
    "AO": "有色金属",
    "SS": "有色金属",
    "BC": "有色金属",
    # === 贵金属 ===
    "AU": "贵金属",
    "AG": "贵金属",
    # === 能源化工 ===
    "SC": "石油石化",
    "BU": "石油石化",
    "LU": "石油石化",
    "PG": "石油石化",
    "TA": "化工",
    "MA": "化工",
    "L": "化工",
    "PP": "化工",
    "V": "化工",
    "EG": "化工",
    "EB": "化工",
    "FG": "化工",
    "SA": "化工",
    "UR": "化工",
    "SH": "化工",
    "PX": "化工",
    "PF": "化工",
    "RU": "化工",
    "NR": "化工",
    "BR": "化工",
    "SP": "轻工制造",
    # === 农产品 ===
    "M": "农林牧渔",
    "C": "农林牧渔",
    "CS": "农林牧渔",
    "CF": "农林牧渔",
    "P": "农林牧渔",
    "Y": "农林牧渔",
    "OI": "农林牧渔",
    "RM": "农林牧渔",
    "SR": "农林牧渔",
    "JD": "农林牧渔",
    "AP": "农林牧渔",
    "LH": "农林牧渔",
    "PK": "农林牧渔",
    "CJ": "农林牧渔",
    # === 铁合金 ===
    "SM": "钢铁",
    "SF": "钢铁",
    # === 新能源 ===
    "SI": "电力设备与新能源",
    "LC": "电力设备与新能源",
}

# 去重后的行业列表（用于批量调用 Alpha派）
UNIQUE_INDUSTRIES: List[str] = sorted(set(COMMODITY_TO_INDUSTRY.values()))

# 行业 → 品种列表反向映射（运行时计算）
INDUSTRY_TO_COMMODITIES: Dict[str, List[str]] = {}


def _build_reverse_mapping():
    """构建行业→品种反向映射"""
    global INDUSTRY_TO_COMMODITIES
    INDUSTRY_TO_COMMODITIES = {}
    for code, industry in COMMODITY_TO_INDUSTRY.items():
        INDUSTRY_TO_COMMODITIES.setdefault(industry, []).append(code)
    # 去重并排序
    for industry in INDUSTRY_TO_COMMODITIES:
        INDUSTRY_TO_COMMODITIES[industry] = sorted(
            set(INDUSTRY_TO_COMMODITIES[industry])
        )


_build_reverse_mapping()


def get_industry_by_commodity(code: str) -> Optional[str]:
    """根据品种代码获取所属行业"""
    return COMMODITY_TO_INDUSTRY.get(code.upper())


def get_commodities_by_industry(industry: str) -> List[str]:
    """根据行业名称获取包含的品种列表"""
    return INDUSTRY_TO_COMMODITIES.get(industry, [])


def get_all_industries() -> List[str]:
    """获取所有去重后的行业列表"""
    return UNIQUE_INDUSTRIES.copy()


def get_mapped_commodities() -> List[str]:
    """获取已映射的所有品种代码"""
    return sorted(COMMODITY_TO_INDUSTRY.keys())


def get_unmapped_commodities(monitored: List[str]) -> List[str]:
    """获取监控列表中尚未映射的品种"""
    mapped = set(COMMODITY_TO_INDUSTRY.keys())
    return [c for c in monitored if c.upper() not in mapped]


def get_industry_summary() -> Dict[str, Dict[str, any]]:
    """获取行业汇总信息"""
    return {
        industry: {
            "commodity_count": len(codes),
            "commodities": codes,
        }
        for industry, codes in INDUSTRY_TO_COMMODITIES.items()
    }
