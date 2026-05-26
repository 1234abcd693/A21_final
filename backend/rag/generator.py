"""
Prompt 构建 + LLM 生成 + 流式输出
"""

import json
import time
import uuid
from typing import Any, AsyncGenerator, Optional

from core.llm import generate_stream as llama_stream
from rag.retriever import hybrid_search


SYSTEM_PROMPT = """你是一位船舶电气设备维修专家。请严格根据以下资料回答问题，使用 Markdown 格式输出。

格式要求：
- 用 ### 标题分组
- 用 **粗体** 强调关键信息
- 用有序列表或无序列表组织内容
- 引用来源标注为 [N]

输出结构：
### 故障可能原因（按优先级排列）
1. **原因名称** — 检查方法：XXX，预计耗时：XXX
2. ...

### 维修步骤
1. 步骤一
2. 步骤二

### ⚠️ 安全注意事项
- 注意事项一
- 注意事项二

如果资料中没有相关信息，直接回答"未找到相关信息"。
"""


def _format_graph_results(graph_results: list[dict]) -> str:
    """格式化图检索结果为 LLM 可读文本"""
    if not graph_results:
        return ""

    lines = ["\n【知识图谱检索结果】\n"]
    for i, item in enumerate(graph_results, 1):
        lines.append(f"故障现象: {item.get('symptom', '')}")
        lines.append(f"来源: {item.get('source_doc', '')}，{item.get('source_page', '')}\n")

        causes = item.get("causes", [])
        if causes:
            lines.append("可能原因（按优先级排列）：")
            sorted_causes = sorted(causes, key=lambda x: x.get("priority", 99))
            for j, cause in enumerate(sorted_causes, 1):
                shutdown = "需停机检查" if cause.get("requires_shutdown") else ""
                lines.append(
                    f"  {j}. {cause.get('cause', '')} "
                    f"[检查方法: {cause.get('check_method', '未知')}, "
                    f"预计耗时: {cause.get('check_time', '未知')}] {shutdown}"
                )

        steps = item.get("steps", [])
        if steps and steps[0]:
            lines.append("\n维修步骤：")
            for j, step in enumerate(steps, 1):
                if step:
                    lines.append(f"  {j}. {step}")

        tools = item.get("tools", [])
        if tools and tools[0]:
            lines.append(f"\n所需工具: {', '.join(t for t in tools if t)}")

        precautions = item.get("precautions", [])
        if precautions and precautions[0]:
            lines.append(f"\n⚠️ 注意事项: {', '.join(p for p in precautions if p)}")

        lines.append("")

    return "\n".join(lines)


def build_prompt(
    question: str,
    chunks: list[dict],
    graph_results: list[dict],
    history: Optional[list[dict]] = None,
) -> str:
    """构建最终 Prompt"""
    parts = [SYSTEM_PROMPT]

    # 图结果
    graph_text = _format_graph_results(graph_results)
    if graph_text:
        parts.append(graph_text)

    # 文档片段
    if chunks:
        parts.append("\n参考资料：")
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"\n[{i}] 来源: {chunk.get('doc_name', '未知')}，"
                f"{chunk.get('page', '')}"
                f"\n{chunk.get('text', '')}"
            )

    # 历史对话
    if history:
        parts.append("\n对话历史：")
        for msg in history[-4:]:  # 只保留最近 4 轮
            role = "用户" if msg.get("role") == "user" else "系统"
            parts.append(f"{role}: {msg.get('content', '')}")

    parts.append(f"\n用户问题：{question}")
    return "\n".join(parts)


def build_keyword_prompt(keyword: str, chunks: list[dict], graph_results: list[dict]) -> str:
    """关键词检索模式的 Prompt（侧重文档列表展示）"""
    parts = [SYSTEM_PROMPT]

    graph_text = _format_graph_results(graph_results)
    if graph_text:
        parts.append(graph_text)

    if chunks:
        parts.append(f"\n关键词「{keyword}」的检索结果：")
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"\n[{i}] 《{chunk.get('doc_name', '')}》{chunk.get('page', '')}"
                f"\n{chunk.get('text', '')[:300]}..."
            )

    parts.append(f"\n请根据以上检索结果，对关键词「{keyword}」相关内容进行总结分析。")
    return "\n".join(parts)


async def ask_stream(
    question: str,
    mode: str = "chat",
    session_id: Optional[str] = None,
    context_nodes: Optional[list[str]] = None,
    history: Optional[list[dict]] = None,
) -> AsyncGenerator[dict, None]:
    """
    核心问答（流式 SSE）。
    yield 字典: {"type": "token", "token": "...", "index": N}
    完成后 yield: {"type": "metadata", ...}
    """

    # 1. 检索
    retrieval = hybrid_search(question)

    # 2. 构建 prompt
    if mode == "keyword":
        prompt = build_keyword_prompt(question, retrieval["chunks"], retrieval["graph_results"])
    else:
        prompt = build_prompt(question, retrieval["chunks"], retrieval["graph_results"], history)

    # 3. 流式生成
    full_answer = ""
    token_index = 0
    start_time = time.time()

    async for token in llama_stream(prompt):
        full_answer += token
        yield {"type": "token", "token": token, "index": token_index}
        token_index += 1

    # 4. 构建溯源元数据
    citations = []
    retrieved_chunks = []
    for i, chunk in enumerate(retrieval["chunks"], 1):
        citations.append({
            "num": i,
            "chunk_id": chunk.get("chunk_id", ""),
            "doc_name": chunk.get("doc_name", ""),
            "page": chunk.get("page", ""),
            "graph_nodes": chunk.get("graph_entities", []),
        })
        retrieved_chunks.append({
            "chunk_id": chunk.get("chunk_id", ""),
            "doc_name": chunk.get("doc_name", ""),
            "page": chunk.get("page", ""),
            "text": chunk.get("text", "")[:200],
            "graph_nodes": chunk.get("graph_entities", []),
        })

    message_id = f"msg_{uuid.uuid4().hex[:8]}"
    thinking_time_ms = int((time.time() - start_time) * 1000)

    yield {
        "type": "metadata",
        "message_id": message_id,
        "citations": citations,
        "traceability": {
            "references_in_range": len(citations) > 0,
            "keywords_matched": 0,
            "keywords_total": 0,
            "confidence": "green" if citations else "yellow",
        },
        "retrieved_chunks": json.dumps(retrieved_chunks, ensure_ascii=False),
        "answer_text": full_answer,
        "thinking_time_ms": thinking_time_ms,
    }
