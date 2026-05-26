"""
Prompt 构建 + LLM 生成 + 流式输出 + 格式后处理
==============================================
v2.2: 强制结构化输出 + 格式清洗
"""

import json
import re
import time
import uuid
from typing import Any, AsyncGenerator, Optional

from core.llm import generate_stream as llama_stream
from rag.retriever import hybrid_search


# ==================== 系统 Prompt（v2.2 — 带示例） ====================

SYSTEM_PROMPT = """你是一位船舶电气设备维修专家。根据参考资料，用专业规范的书面中文回答用户问题。

你必须严格按照以下 Markdown 格式输出，每个标题独占一行，标题后必须空一行：

## 故障分析
（列出2-3条最可能的故障原因）

## 维修建议
（给出具体可操作的检查与维修步骤）

## 注意事项
（列出安全提醒和所需工具）

格式要求：
- 每个 ## 标题独占一行，标题前后都有空行
- 使用 1. 2. 3. 写有序列表，不要用 . 开头
- 每个要点写完后换行
- 回答简洁、专业，不要重复"""


# ==================== 答案后处理 ====================

def _clean_answer(text: str) -> str:
    """后处理模型输出，仅修复确实有问题的格式。"""
    # 1. 修复 "## 标题内容在同一行"（标题后无换行，直接接正文）
    #    不会影响已正确换行的标题
    text = re.sub(
        r'^(## [^\n]+?)  +([^\n].+)$',
        r'\1\n\n\2',
        text,
        flags=re.MULTILINE,
    )

    # 2. 修复 ". 电源未接通" → "1. 电源未接通"
    lines = text.split('\n')
    fixed_lines = []
    counter = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('. ') and len(stripped) > 2:
            counter += 1
            line = line.replace('. ', f'{counter}. ', 1)
        elif stripped and stripped[0].isdigit() and '. ' in stripped[:4]:
            try:
                counter = int(stripped.split('.')[0])
            except ValueError:
                pass
        fixed_lines.append(line)
    text = '\n'.join(fixed_lines)

    # 3. 连续空行最多 2 个
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


# ==================== 图检索结果格式化 ====================

def _format_graph_results(graph_results: list[dict], max_chars: int = 300) -> str:
    """将图检索三元组格式化为简练的参考文本。"""
    if not graph_results:
        return ""

    lines = []
    for item in graph_results[:2]:
        parts = []

        symptom = item.get("symptom", "")
        if symptom:
            parts.append(f"故障现象：{symptom}")

        causes = item.get("causes", [])
        if causes:
            sorted_causes = sorted(causes, key=lambda x: x.get("priority", 99))
            cause_strs = [c.get("cause", "") for c in sorted_causes if c.get("cause")]
            if cause_strs:
                parts.append("可能原因：" + "、".join(cause_strs[:3]))

        steps = item.get("steps", [])
        if steps and steps[0]:
            valid_steps = [s for s in steps if s]
            if valid_steps:
                parts.append("维修步骤：" + "；".join(valid_steps[:3]))

        tools = item.get("tools", [])
        if tools and tools[0]:
            valid_tools = [t for t in tools if t]
            if valid_tools:
                parts.append("所需工具：" + "、".join(valid_tools[:5]))

        precautions = item.get("precautions", [])
        if precautions and precautions[0]:
            valid_p = [p for p in precautions if p]
            if valid_p:
                parts.append("注意事项：" + "、".join(valid_p[:3]))

        if parts:
            block = "\n".join(parts)
            if len(block) > max_chars:
                block = block[:max_chars] + "…"
            lines.append(block)

    if lines:
        return "【知识图谱参考资料】\n" + "\n\n".join(lines)
    return ""


# ==================== 文档片段格式化 ====================

def _format_chunks(chunks: list[dict], max_chars_per_chunk: int = 180) -> str:
    """格式化文档片段，每条截断。"""
    if not chunks:
        return ""

    lines = []
    for chunk in chunks[:3]:
        text = chunk.get("text", "")
        if not text:
            continue
        if len(text) > max_chars_per_chunk:
            text = text[:max_chars_per_chunk] + "…"
        lines.append(text)

    if lines:
        return "【技术文档参考资料】\n" + "\n\n".join(lines)
    return ""


# ==================== Prompt 构建 ====================

def build_prompt(
    question: str,
    chunks: list[dict],
    graph_results: list[dict],
    history: Optional[list[dict]] = None,
) -> str:
    """构建 Qwen2.5 chat 格式 Prompt。"""
    graph_text = _format_graph_results(graph_results)
    chunk_text = _format_chunks(chunks)

    reference = ""
    if graph_text:
        reference += graph_text + "\n"
    if chunk_text:
        reference += chunk_text + "\n"

    history_text = ""
    if history:
        history_text = "\n".join(
            f"{'用户' if m.get('role') == 'user' else '助手'}：{m.get('content', '')[:200]}"
            for m in history[-2:]
        )

    system_msg = f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>"
    user_msg = (
        f"<|im_start|>user\n"
        f"参考资料：\n{reference}\n"
        + (f"对话历史：\n{history_text}\n" if history_text else "")
        + f"问题：{question}\n"
        f"<|im_end|>"
        f"<|im_start|>assistant\n"
    )

    return system_msg + "\n" + user_msg


# ==================== 流式问答入口 ====================

async def ask_stream(
    question: str,
    mode: str = "chat",
    session_id: Optional[str] = None,
    context_nodes: Optional[list[str]] = None,
    history: Optional[list[dict]] = None,
) -> AsyncGenerator[dict, None]:
    """A21 核心问答流式生成入口。"""

    retrieval = hybrid_search(question)
    prompt = build_prompt(question, retrieval["chunks"], retrieval["graph_results"], history)

    full_answer = ""
    token_index = 0
    start_time = time.time()

    async for token in llama_stream(prompt, temperature=0.1, max_tokens=200):
        full_answer += token
        yield {"type": "token", "token": token, "index": token_index}
        token_index += 1

    # 后处理：修复模型格式问题
    full_answer = _clean_answer(full_answer)

    citations = []
    retrieved_chunks = []
    for i, chunk in enumerate(retrieval["chunks"], 1):
        citations.append({
            "num": i,
            "chunk_id": chunk.get("chunk_id", ""),
            "doc_name": chunk.get("doc_name", ""),
            "page": chunk.get("page", ""),
            "text_preview": chunk.get("text", "")[:120],
        })
        retrieved_chunks.append({
            "chunk_id": chunk.get("chunk_id", ""),
            "doc_name": chunk.get("doc_name", ""),
            "page": chunk.get("page", ""),
            "text": chunk.get("text", "")[:200],
        })

    for item in retrieval.get("graph_results", []):
        retrieved_chunks.append({
            "source": "knowledge_graph",
            "symptom": item.get("symptom", ""),
            "causes": [c.get("cause") for c in item.get("causes", [])],
            "steps": item.get("steps", []),
        })

    message_id = f"msg_{uuid.uuid4().hex[:8]}"
    thinking_time_ms = int((time.time() - start_time) * 1000)

    yield {
        "type": "metadata",
        "message_id": message_id,
        "citations": citations,
        "kg_results": retrieval.get("graph_results", []),
        "retrieved_chunks": json.dumps(retrieved_chunks, ensure_ascii=False),
        "answer_text": full_answer,
        "thinking_time_ms": thinking_time_ms,
    }
