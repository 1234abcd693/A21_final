"""
Tests for ``rag/generator.py`` — prompt building and graph formatting.

``build_prompt``, ``build_keyword_prompt``, and ``_format_graph_results`` are
pure functions and are tested without mocking.  ``ask_stream`` (async) is not
tested here as it requires mocking ``llama_stream`` and ``hybrid_search``.
"""

import pytest

from rag.generator import build_prompt, build_keyword_prompt, _format_graph_results


# ======================================================================
# _format_graph_results
# ======================================================================


class TestFormatGraphResults:
    """``_format_graph_results()`` — KG triple → LLM-readable text."""

    def test_empty(self):
        """Empty graph list → empty string."""
        assert _format_graph_results([]) == ""

    def test_with_full_data(self, sample_graph_results):
        """All sections rendered: symptom, causes, steps, tools, precautions."""
        text = _format_graph_results(sample_graph_results)
        assert "【知识图谱检索结果】" in text
        assert "接触器线圈烧毁" in text
        assert "电源电压过低" in text
        assert "线圈内部短路" in text
        assert "维修步骤" in text
        assert "所需工具" in text
        assert "注意事项" in text
        # Verify priority ordering: voltage (priority 1) before short circuit (2)
        assert text.index("电源电压过低") < text.index("线圈内部短路")

    def test_minimal_result(self):
        """Symptom with no causes/steps/tools/precautions."""
        data = [{
            "symptom": "简单故障", "causes": [], "steps": [], "tools": [],
            "precautions": [], "source_doc": "", "source_page": "",
        }]
        text = _format_graph_results(data)
        assert "简单故障" in text
        assert "维修步骤" not in text
        assert "所需工具" not in text

    def test_missing_keys(self):
        """Result dict missing optional keys should not crash."""
        data = [{"symptom": "部分数据"}]  # no causes, steps, etc.
        # Should not raise KeyError
        text = _format_graph_results(data)
        assert "部分数据" in text

    def test_multiple_results(self, sample_graph_results):
        """Multiple graph results are each rendered sequentially."""
        second = {
            "symptom": "电机过热",
            "causes": [{"cause": "轴承磨损", "priority": 1,
                        "check_method": "目视", "check_time": "5分钟",
                        "requires_shutdown": True}],
            "steps": ["更换轴承"],
            "tools": ["扳手"],
            "precautions": ["停机冷却"],
            "source_doc": "电机维护手册",
            "source_page": "P10",
        }
        text = _format_graph_results(sample_graph_results + [second])
        assert "接触器线圈烧毁" in text
        assert "电机过热" in text
        # Positioning: first result appears before second
        assert text.index("接触器线圈烧毁") < text.index("电机过热")


# ======================================================================
# build_prompt — chat mode
# ======================================================================


class TestBuildPrompt:
    """``build_prompt()`` — chat-mode prompt construction."""

    def test_basic(self, sample_chunks, sample_graph_results):
        """Prompt includes system prompt, KG results, references, and question."""
        prompt = build_prompt(
            question="接触器线圈烧毁怎么办？",
            chunks=sample_chunks,
            graph_results=sample_graph_results,
        )
        assert "船舶电气设备维修专家" in prompt       # SYSTEM_PROMPT
        assert "【知识图谱检索结果】" in prompt
        assert "参考资料" in prompt
        assert "用户问题" in prompt
        assert "接触器线圈烧毁怎么办？" in prompt
        assert "[1]" in prompt
        assert "[2]" in prompt
        assert "[3]" in prompt

    def test_with_history(self, sample_chunks):
        """History messages appear under '对话历史'."""
        history = [
            {"role": "user", "content": "第一个问题"},
            {"role": "assistant", "content": "第一个回答"},
            {"role": "user", "content": "当前问题"},
        ]
        prompt = build_prompt(
            question="当前问题",
            chunks=sample_chunks[:1],
            graph_results=[],
            history=history,
        )
        assert "对话历史" in prompt
        assert "第一个问题" in prompt
        assert "第一个回答" in prompt

    def test_history_truncated_to_last_4(self, sample_chunks):
        """Only the most recent 4 history entries are included."""
        history = [{"role": "user", "content": f"问题{i}"} for i in range(10)]
        prompt = build_prompt(
            question="最后问题",
            chunks=sample_chunks[:1],
            graph_results=[],
            history=history,
        )
        assert "问题6" in prompt
        assert "问题9" in prompt
        assert "问题0" not in prompt
        assert "问题4" not in prompt

    def test_no_chunks(self):
        """With empty chunks, '参考资料：' section header is omitted."""
        prompt = build_prompt("测试问题", [], [])
        # The SYSTEM_PROMPT itself contains the word "参考资料" — check for
        # the section header "参考资料：" which is only added when chunks exist.
        assert "参考资料：" not in prompt
        assert "测试问题" in prompt

    def test_no_graph_results(self, sample_chunks):
        """With empty graph_results, KG section is omitted."""
        prompt = build_prompt("测试问题", sample_chunks[:1], [])
        assert "【知识图谱检索结果】" not in prompt
        assert "参考资料" in prompt

    def test_empty_chunks_and_graph(self):
        """Only system prompt + question when both are empty."""
        prompt = build_prompt("仅此一问", [], [])
        assert prompt.startswith("你是一位经验丰富的船舶电气设备维修专家")
        assert "仅此一问" in prompt
        # No extra section headers (SYSTEM_PROMPT mentions "参考资料" in text)
        assert "参考资料：" not in prompt
        assert "【知识图谱检索结果】" not in prompt

    def test_history_empty(self, sample_chunks):
        """None history → no '对话历史' section."""
        prompt = build_prompt("问题", sample_chunks[:1], [], history=None)
        assert "对话历史" not in prompt


# ======================================================================
# build_keyword_prompt — keyword mode
# ======================================================================


class TestBuildKeywordPrompt:
    """``build_keyword_prompt()`` — keyword-mode prompt construction."""

    def test_basic(self, sample_chunks, sample_graph_results):
        """Prompt includes system, KG, keyword results, and summary instruction."""
        prompt = build_keyword_prompt("接触器", sample_chunks, sample_graph_results)
        assert "船舶电气设备维修专家" in prompt
        assert "【知识图谱检索结果】" in prompt
        assert "接触器" in prompt
        assert "总结分析" in prompt

    def test_no_chunks(self, sample_graph_results):
        """With empty chunks, document list section is omitted."""
        prompt = build_keyword_prompt("测试", [], sample_graph_results)
        assert "总结分析" in prompt
        # Graph section still present
        assert "【知识图谱检索结果】" in prompt

    def test_no_graph(self, sample_chunks):
        """With empty graph_results, KG section omitted."""
        prompt = build_keyword_prompt("线圈", sample_chunks[:1], [])
        assert "【知识图谱检索结果】" not in prompt
        assert "线圈" in prompt

    def test_text_truncation(self):
        """Chunk text longer than 300 chars is truncated."""
        long_text = "A" * 500
        chunks = [{"chunk_id": "c1", "text": long_text,
                   "doc_name": "doc", "page": "P1"}]
        prompt = build_keyword_prompt("测试", chunks, [])
        assert "A" * 300 in prompt
        # The truncated version shouldn't have the full 500 chars
        assert "A" * 500 not in prompt
