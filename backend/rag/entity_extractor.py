"""
实体识别和查询改写

从用户自然语言问题中提取实体，支持同义词扩展。
"""

import re
from typing import Optional

import jieba


# 船舶领域术语字典
ENTITY_DICT = {
    "设备": [
        "发动机", "电机", "电动机", "接触器", "断路器", "发电机", "变压器",
        "起货机", "锚机", "舵机", "锅炉", "配电装置", "PLC",
        "三相异步电动机", "直流电机", "船用变压器", "船舶电器",
        "热继电器", "火灾报警装置", "机舱监测系统",
    ],
    "零件": [
        "燃油泵", "密封圈", "叶轮", "线圈", "触头", "弹簧",
        "接线端子", "定子绕组", "转子", "轴承", "电刷", "液压泵",
    ],
    "故障": [
        "漏油", "过热", "短路", "烧毁", "振动", "异响",
        "无法启动", "不能起动", "不能启动", "压力异常", "绝缘降低",
        "冒烟", "冒黑烟", "打不着火", "嗡嗡响", "噪音",
    ],
}

# 同义词映射（用户口语 → 数据库正式名称）
SYNONYM_MAP: dict[str, list[str]] = {
    "发动机": ["船用电机", "柴油机"],
    "打不着火": ["不能起动", "无法启动", "启动失败"],
    "漏油": ["油封泄漏", "管路漏油", "渗油"],
    "嗡嗡响": ["异常振动", "噪音过大"],
    "冒黑烟": ["排气异常", "燃烧不充分"],
    "无法启动": ["不能起动"],
}


def extract_entities(question: str) -> dict[str, list[str]]:
    """
    从用户问题中提取实体。
    返回 {"设备": [...], "零件": [...], "故障": [...]}
    """
    result: dict[str, list[str]] = {"设备": [], "零件": [], "故障": []}
    for category, terms in ENTITY_DICT.items():
        for term in terms:
            if term in question:
                result[category].append(term)
    return result


def extract_keywords(question: str, top_n: int = 10) -> list[str]:
    """
    用 jieba 提取关键词（用于 BM25 和答案验证）。
    过滤停用词。
    """
    stopwords = {"怎么办", "怎么", "如何", "什么", "为什么", "吗", "呢", "吧", "的", "了", "是", "在"}
    words = jieba.lcut(question)
    keywords = [w for w in words if w.strip() and w not in stopwords and len(w) > 1]
    return keywords[:top_n]


def expand_entity(entity_name: str) -> list[str]:
    """同义词扩展：把用户说的词扩展为数据库可能的名字"""
    candidates = [entity_name]
    for user_word, db_words in SYNONYM_MAP.items():
        if user_word in entity_name:
            candidates.extend(db_words)
    return candidates


def is_question_like(text: str) -> bool:
    """判断输入是否为自然语言问题（而非关键词）"""
    question_markers = ["?", "？", "吗", "怎么", "如何", "什么", "为什么", "怎么办"]
    return any(m in text for m in question_markers)
