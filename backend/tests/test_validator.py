"""
Tests for ``rag/validator.py`` — answer validation and confidence levels.

All tests are pure-logic; the only external dependency (``extract_keywords``
from ``rag.entity_extractor``) is mocked.
"""

import pytest
from unittest.mock import patch

from rag.validator import validate_answer, format_warning


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _chunks(*texts):
    """Build retrieved_chunks list from text strings."""
    return [{"text": t} for t in texts]


# ======================================================================
# validate_answer — confidence levels
# ======================================================================


class TestValidateGreen:
    """Confidence ``green`` — all refs in range + all keywords matched."""

    def test_green_all_refs_and_keywords(self):
        """All [N] references valid and every keyword found in source texts."""
        with patch("rag.validator.extract_keywords", return_value=["接触器", "线圈", "电压"]):
            result = validate_answer(
                answer_text="根据资料[1]，接触器线圈烧毁原因是电源电压过低[2]。",
                citations=[{"num": 1}, {"num": 2}],
                retrieved_chunks=_chunks(
                    "接触器线圈烧毁检查电源电压",
                    "线圈烧毁原因电压过低处理",
                ),
            )
        assert result["confidence"] == "green"
        assert result["references_in_range"] is True
        assert result["keywords_matched"] == result["keywords_total"] == 3

    def test_green_single_ref(self):
        """Single valid reference with full keyword match."""
        with patch("rag.validator.extract_keywords", return_value=["线圈"]):
            result = validate_answer(
                answer_text="见[1]。线圈故障。",
                citations=[{"num": 1}],
                retrieved_chunks=_chunks("线圈故障维修"),
            )
        assert result["confidence"] == "green"


class TestValidateYellow:
    """Confidence ``yellow`` — partial pass (either refs or keywords)."""

    def test_yellow_refs_ok_keywords_partial(self):
        """Refs valid but some keywords missing from source → yellow."""
        with patch("rag.validator.extract_keywords", return_value=["接触器", "电压"]):
            result = validate_answer(
                answer_text="根据[1]，检查电压。",
                citations=[{"num": 1}],
                retrieved_chunks=_chunks("检查电源电压是否正常"),
            )
        assert result["confidence"] == "yellow"
        assert result["references_in_range"] is True
        assert result["keywords_matched"] == 1  # "电压" found, "接触器" missing
        assert result["keywords_total"] == 2

    def test_yellow_keywords_ok_refs_bad(self):
        """Keywords matched but refs out of range → yellow."""
        with patch("rag.validator.extract_keywords", return_value=["接触器", "线圈"]):
            result = validate_answer(
                answer_text="参见[5]。接触器线圈故障。",
                citations=[{"num": 1}],  # max=1, ref=5 OOB
                retrieved_chunks=_chunks("接触器线圈故障维修"),
            )
        assert result["confidence"] == "yellow"
        assert result["references_in_range"] is False
        assert result["keywords_matched"] == 2


class TestValidateRed:
    """Confidence ``red`` — no valid refs + no keywords matched."""

    def test_red_no_refs_no_keywords(self):
        """No references and no keywords found in source → red."""
        with patch("rag.validator.extract_keywords", return_value=["编造", "回答"]):
            result = validate_answer(
                answer_text="这是一个完全编造的回答。",
                citations=[],
                retrieved_chunks=_chunks("关于船舶电气的真实资料"),
            )
        assert result["confidence"] == "red"
        assert result["references_in_range"] is False
        assert result["keywords_matched"] == 0

    def test_red_empty_answer(self):
        """Empty answer text → no refs, no keywords → red."""
        result = validate_answer("", [], [])
        assert result["confidence"] == "red"
        assert result["references_in_range"] is False


class TestValidateEdgeCases:
    """Edge cases for validate_answer()."""

    def test_no_citations(self):
        """No citations provided → references_in_range is False."""
        with patch("rag.validator.extract_keywords", return_value=["资料"]):
            result = validate_answer(
                answer_text="根据资料分析[1]。",
                citations=[],
                retrieved_chunks=_chunks("分析资料"),
            )
        assert result["references_in_range"] is False

    def test_ref_out_of_range_yellow(self):
        """Citation [3] exceeds max=2 → ref invalid, keywords match → yellow."""
        with patch("rag.validator.extract_keywords", return_value=["描述"]):
            result = validate_answer(
                answer_text="参见[3]的描述。",
                citations=[{"num": 1}, {"num": 2}],
                retrieved_chunks=_chunks("相关描述"),
            )
        assert result["references_in_range"] is False
        assert result["confidence"] == "yellow"

    def test_multiple_refs_all_valid(self):
        """All [1], [2], [3] within citation range → references_in_range True."""
        with patch("rag.validator.extract_keywords", return_value=["文本"]):
            result = validate_answer(
                answer_text="见[1]和[2]和[3]。",
                citations=[{"num": 1}, {"num": 2}, {"num": 3}],
                retrieved_chunks=_chunks("文本一", "文本二", "文本三"),
            )
        assert result["references_in_range"] is True

    def test_zero_keywords_found(self):
        """When no keywords extracted but refs valid: ref matches → green."""
        with patch("rag.validator.extract_keywords", return_value=[]):
            result = validate_answer(
                answer_text="简单回答[1]。",  # [1] must appear in answer text
                citations=[{"num": 1}],
                retrieved_chunks=_chunks("一些内容"),
            )
        # refs OK (1 in range), keywords_total=0, matched=0
        # → references_in_range AND (0==0) → green
        assert result["confidence"] == "green"
        assert result["keywords_total"] == 0
        assert result["keywords_matched"] == 0

    def test_no_text_in_chunks(self):
        """Chunks with empty text still work; keywords not found."""
        with patch("rag.validator.extract_keywords", return_value=["线圈"]):
            result = validate_answer(
                answer_text="线圈故障[1]。",
                citations=[{"num": 1}],
                retrieved_chunks=[{"text": ""}],
            )
        assert result["keywords_matched"] == 0


# ======================================================================
# format_warning
# ======================================================================


class TestFormatWarning:
    """``format_warning()`` — user-facing warning text by confidence."""

    def test_green(self):
        assert format_warning("green") == ""

    def test_yellow(self):
        msg = format_warning("yellow")
        assert "未经源文档确认" in msg

    def test_red(self):
        msg = format_warning("red")
        assert "无法验证" in msg
