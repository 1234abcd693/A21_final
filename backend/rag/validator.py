"""
答案验证模块 — 防幻觉机制
===============================

A21 系统的两道防火墙，在 LLM 生成回答后执行：
  验证层 1：引用完整性 — 答案中的 [N] 引用是否在检索结果范围内？
  验证层 2：事实一致性 — 答案中的关键名词是否在源文档中出现？

输出三级可信度：
  - 🟢 green:  引用完整 + 关键词全部匹配 → 可靠
  - 🟡 yellow: 部分通过 → 存疑（标记"部分信息未经源文档确认"）
  - 🔴 red:    全部未通过 → 高风险（标记"此回答无法验证，请谨慎参考"）
"""

import re

from rag.entity_extractor import extract_keywords


def validate_answer(
    answer_text: str,
    citations: list[dict],
    retrieved_chunks: list[dict],
) -> dict:
    """
    验证 LLM 生成答案的可靠性 — 两层验证。
    
    验证层 1 — 引用完整性：
      - 从答案文本中提取所有 [N] 格式的引用编号
      - 检查每个引用编号是否在 citations 范围内（1 ≤ N ≤ max_citation）
      - 如果答案引用了 [3]，但检索只返回了 2 条 → 引用不完整
      - 这主要检查 LLM 是否"编造"了不存在的引用
    
    验证层 2 — 事实一致性：
      - 用 jieba 提取答案中的关键名词和术语
      - 在检索到的原始文档片段中搜索这些关键词
      - 如果关键词在源文档中出现 → 事实可追溯
      - 如果关键词不在任何源文档中 → LLM 可能在"脑补"

    参数：
        answer_text:      LLM 生成的完整回答文本
        citations:        引用列表 [{num: 1, chunk_id: "...", ...}, ...]
        retrieved_chunks: 检索到的原始文档片段列表 [{text: "...", ...}, ...]

    返回：
        {
            references_in_range: bool,    # 所有引用 [N] 是否在有效范围内
            keywords_matched: int,        # 在源文档中找到的关键词数
            keywords_total: int,          # 答案中提取的总关键词数
            confidence: "green"|"yellow"|"red"  # 综合可信度等级
        }
    """

    # ========== 验证层 1：引用完整性 ==========
    # 从答案文本中提取所有 [N] 引用
    refs_in_answer = set()
    for match in re.finditer(r"\[(\d+)\]", answer_text):
        refs_in_answer.add(int(match.group(1)))

    # 检查每个引用是否在有效范围内（1 ≤ N ≤ 最大引用编号）
    max_citation = max((c["num"] for c in citations), default=0)
    references_in_range = (
        all(1 <= n <= max_citation for n in refs_in_answer)
        if refs_in_answer
        else False  # 答案中没有任何 [N] 引用 → 视为未通过
    )

    # ========== 验证层 2：事实一致性 ==========
    # 用 jieba 提取答案中的关键词（通常是设备名、故障术语等）
    keywords = extract_keywords(answer_text)

    # 将所有检索到的文档片段合并为一个文本池
    all_chunk_texts = " ".join(c.get("text", "") for c in retrieved_chunks)
    
    # 统计有多少关键词在源文档中出现
    keywords_total = len(keywords)
    keywords_matched = (
        sum(1 for kw in keywords if kw in all_chunk_texts)
        if keywords_total > 0
        else 0
    )

    # ========== 综合判定 ==========
    # 三层判定逻辑：
    #   green:  引用完整 AND 关键词全部可追溯 → 答案可靠
    #   red:    引用异常 AND 关键词无一匹配 → 严重幻觉风险
    #   yellow: 其他情况（部分通过）→ 需要人工判断
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
    """
    根据可信度等级生成用户可见的警告文本。
    
    - green:  不显示警告（信任答案）
    - yellow: 显示"部分信息未经源文档确认" — 弱警告
    - red:    显示"此回答无法验证，请谨慎参考" — 强警告
    """
    if confidence == "red":
        return "⚠️⚠️ 此回答无法验证，请谨慎参考。"
    elif confidence == "yellow":
        return "⚠️ 部分信息未经源文档确认，请参考原始资料。"
    return ""  # green 等级：无警告
