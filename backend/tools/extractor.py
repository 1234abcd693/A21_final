"""
知识抽取（正则 + 1.5B few-shot 混合方案）
"""

import re
import uuid
from typing import Any


# 正则规则：匹配"故障现象：...""故障原因：...""维修步骤：..." 等模式
REGEX_PATTERNS = {
    "Symptom": [
        re.compile(r"故障现象[：:]\s*(.+?)(?=\n|故障原因|维修步骤|注意事项|$)"),
        re.compile(r"症状[：:]\s*(.+?)(?=\n|原因|处理|$)"),
    ],
    "Cause": [
        re.compile(r"故障原因[：:]\s*(.+?)(?=\n|维修步骤|注意事项|$)"),
        re.compile(r"原因分析[：:]\s*(.+?)(?=\n|处理|$)"),
    ],
    "Step": [
        re.compile(r"维修步骤[：:]\s*(.+?)(?=\n|注意事项|$)"),
        re.compile(r"处理方法[：:]\s*(.+?)(?=\n|$)"),
    ],
    "Precaution": [
        re.compile(r"注意事项[：:]\s*(.+?)(?=\n|$)"),
        re.compile(r"安全提醒[：:]\s*(.+?)(?=\n|$)"),
    ],
}


def extract_with_regex(text: str) -> list[dict[str, Any]]:
    """用正则规则提取实体"""
    candidates: list[dict] = []

    for entity_type, patterns in REGEX_PATTERNS.items():
        for pattern in patterns:
            matches = pattern.findall(text)
            for match in matches:
                match = match.strip()
                if match and len(match) > 1:
                    candidates.append({
                        "uid": f"CAND_{uuid.uuid4().hex[:6]}",
                        "type": entity_type,
                        "name": match,
                        "source": "regex",
                        "confidence": "high",
                        "relations": [],
                    })

    # 提取数字编号的步骤（"1. 拆卸..." "2. 清洗..."）
    step_pattern = re.compile(r"(\d+)[\.\、\s]\s*(.+?)(?=\n\d+[\.\、]|\n|$)")
    step_matches = step_pattern.findall(text)
    prev_uid = None
    for num, step_text in step_matches:
        step_text = step_text.strip()
        if step_text and len(step_text) > 1:
            uid = f"CAND_{uuid.uuid4().hex[:6]}"
            candidate = {
                "uid": uid,
                "type": "Step",
                "name": step_text,
                "source": "regex",
                "confidence": "high",
                "relations": [],
            }
            if prev_uid:
                candidate["relations"].append({"type": "NEXT_STEP", "target": prev_uid})
            candidates.append(candidate)
            prev_uid = uid

    return candidates


def extract_with_model(text: str) -> list[dict[str, Any]]:
    """
    用 1.5B few-shot 模型抽取。
    注意：此函数为占位实现，实际需要调用 llama-server。
    """
    # TODO: 实现 few-shot prompt + llama.cpp 调用
    return []


def extract_knowledge(text: str) -> dict[str, Any]:
    """
    混合抽取：正则优先，正则未覆盖的交给模型。
    """
    # 正则抽取
    regex_candidates = extract_with_regex(text)

    # 检查正则覆盖率（如果正则没抽到 Symptom 或 Cause，尝试模型）
    has_symptom = any(c["type"] == "Symptom" for c in regex_candidates)
    has_cause = any(c["type"] == "Cause" for c in regex_candidates)

    model_candidates = []
    if not has_symptom or not has_cause:
        model_candidates = extract_with_model(text)

    return {
        "candidates": regex_candidates + model_candidates,
        "regex_count": len(regex_candidates),
        "model_count": len(model_candidates),
    }
