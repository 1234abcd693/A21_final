"""
答案验证（防幻觉）

两层验证：
1. 引用完整性：检查 [N] 是否在检索结果范围内
2. 事实一致性：关键名词是否在源文档中出现
"""

import re

from rag.entity_extractor import extract_keywords


def validate_answer(
    answer_text: str,
    citations: list[dict],
    retrieved_chunks: list[dict],
) -> dict:
    """
    验证答案的可靠性。
    返回: {
        references_in_range: bool,
        keywords_matched: int,
        keywords_total: int,
        confidence: "green" | "yellow" | "red"
    }
    """

    # 1. 引用完整性：提取答案中的 [N] 引用
    refs_in_answer = set()
    for match in re.finditer(r"\[(\d+)\]", answer_text):
        refs_in_answer.add(int(match.group(1)))

    max_citation = max((c["num"] for c in citations), default=0)
    references_in_range = all(1 <= n <= max_citation for n in refs_in_answer) if refs_in_answer else False

    # 2. 事实一致性：提取关键词，检查在源文档中出现
    keywords = extract_keywords(answer_text)

    all_chunk_texts = " ".join(c.get("text", "") for c in retrieved_chunks)
    keywords_total = len(keywords)
    keywords_matched = sum(1 for kw in keywords if kw in all_chunk_texts) if keywords_total > 0 else 0

    # 3. 综合判定
    if references_in_range and keywords_matched == keywords_total:
        confidence = "green"
    elif not references_in_range and keywords_matched == 0:
        confidence = "red"
    else:
        confidence = "yellow"

    return {
        "references_in_range": references_in_range,
        "keywords_matched": keywords_matched,
        "keywords_total": keywords_total,
        "confidence": confidence,
    }


def format_warning(confidence: str) -> str:
    """根据可信度返回警告文本"""
    if confidence == "red":
        return "⚠️⚠️ 此回答无法验证，请谨慎参考。"
    elif confidence == "yellow":
        return "⚠️ 部分信息未经源文档确认，请参考原始资料。"
    return ""
