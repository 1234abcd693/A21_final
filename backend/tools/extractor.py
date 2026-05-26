"""
知识抽取模块 — 从非结构化文档中提取结构化知识
==================================================

混合方案（正则 70% + 1.5B few-shot 25% + 手工兜底 5%）：
  阶段 1 — 正则规则：匹配规范格式文本（"故障现象：...""故障原因：..."等）
  阶段 2 — 模型推理：正则未覆盖的部分，用 1.5B 模型 few-shot 抽取
  阶段 3 — 人工确认：前端图谱预览 → 用户确认/修正 → 入库

正则能覆盖的 70%：命题单位提供的数据格式规范（故障现象/原因/步骤/注意事项 明确标注）
模型可补充的 25%：文本有故障描述但格式不规范（如段落叙述式）
手工兜底的 5%： 极端非规范文本或专有名词识别失败

当前实现状态：
   ✅ extract_with_regex() — 正则提取已完成
   ✅ extract_with_model() — 1.5B few-shot 模型抽取已完成
"""

import asyncio
import json
import logging
import re
import uuid
from typing import Any


# ==================== 正则规则定义 ====================

# 匹配规范格式的知识文本模式
# 每条规则对应一种实体类型，每个类型可有多条正则（覆盖不同表述）
REGEX_PATTERNS = {
    "Symptom": [
        # "故障现象：接触器线圈烧毁" → 提取 Symptom
        re.compile(r"故障现象[：:]\s*(.+?)(?=\n|故障原因|维修步骤|注意事项|$)"),
        # "症状：电机发热" → 提取 Symptom
        re.compile(r"症状[：:]\s*(.+?)(?=\n|原因|处理|$)"),
    ],
    "Cause": [
        # "故障原因：电源电压过低" → 提取 Cause
        re.compile(r"故障原因[：:]\s*(.+?)(?=\n|维修步骤|注意事项|$)"),
        # "原因分析：线圈内部短路" → 提取 Cause
        re.compile(r"原因分析[：:]\s*(.+?)(?=\n|处理|$)"),
    ],
    "Step": [
        # "维修步骤：拆下灭弧罩，检查衔铁是否灵活" → 提取 Step
        re.compile(r"维修步骤[：:]\s*(.+?)(?=\n|注意事项|$)"),
        # "处理方法：更换线圈" → 提取 Step
        re.compile(r"处理方法[：:]\s*(.+?)(?=\n|$)"),
    ],
    "Precaution": [
        # "注意事项：断电挂牌后方可操作" → 提取 Precaution
        re.compile(r"注意事项[：:]\s*(.+?)(?=\n|$)"),
        # "安全提醒：电容放电2-3分钟后再操作" → 提取 Precaution
        re.compile(r"安全提醒[：:]\s*(.+?)(?=\n|$)"),
    ],
}


# ==================== 正则抽取 ====================

def extract_with_regex(text: str) -> list[dict[str, Any]]:
    """
    用正则规则提取知识实体（覆盖约 70% 的规范文本）。
    
    提取策略：
    1. 按 REGEX_PATTERNS 定义的规则逐类匹配
    2. 额外识别编号步骤（"1. 断开电源" "2. 拆卸外壳"）→ 生成 Step 实体
    3. 为连续步骤自动建立 NEXT_STEP 关系链
    
    参数：
        text: 从文档解析出的纯文本

    返回：
        list[dict]: 候选实体列表，每个包含：
            uid, type(Symptom/Cause/Step/Precaution), name,
            source("regex"), confidence("high"), relations[]
    """
    candidates: list[dict] = []

    # 阶段 1：按实体类型逐类匹配
    for entity_type, patterns in REGEX_PATTERNS.items():
        for pattern in patterns:
            matches = pattern.findall(text)
            for match in matches:
                match = match.strip()
                if match and len(match) > 1:  # 过滤空匹配和单字符噪声
                    candidates.append({
                        "uid": f"CAND_{uuid.uuid4().hex[:6]}",
                        "type": entity_type,
                        "name": match,
                        "source": "regex",         # 标记为规则抽取
                        "confidence": "high",      # 规则抽取置信度高（格式固定）
                        "relations": [],
                    })

    # 阶段 2：提取编号步骤（"1. xxx" "2. xxx" → 自动建立 NEXT_STEP 链）
    # 匹配形如 "1. 拆卸外壳" "2、清洗零件" "3 更换线圈" 的步骤
    step_pattern = re.compile(r"(\d+)[\.\、\s]\s*(.+?)(?=\n\d+[\.\、]|\n|$)")
    step_matches = step_pattern.findall(text)

    prev_uid = None  # 上一步的 UID，用于建立 NEXT_STEP 关系链
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
            # 与前一步建立 NEXT_STEP 关系（如步骤2→步骤1）
            if prev_uid:
                candidate["relations"].append({"type": "NEXT_STEP", "target": prev_uid})
            candidates.append(candidate)
            prev_uid = uid

    return candidates


# ==================== 模型抽取 ====================

logger = logging.getLogger(__name__)

# 最大输入文本长度（字符），避免超出模型上下文窗口（Qwen2.5-1.5B: 2048 tokens）
MAX_INPUT_LENGTH = 500

# few-shot 示例：船舶故障非规范文本 → 结构化实体
_FEWSHOT_EXAMPLES = [
    {
        "input": (
            "电机最近老是打不着火，检查发现线圈有点发黑，"
            "应该是线圈短路了。需要拆下灭弧罩，检查衔铁是否灵活，然后更换线圈。"
        ),
        "output": [
            {"type": "Symptom", "name": "电机打不着火"},
            {"type": "Symptom", "name": "线圈发黑"},
            {"type": "Cause", "name": "线圈短路"},
            {"type": "Step", "name": "拆下灭弧罩"},
            {"type": "Step", "name": "检查衔铁是否灵活"},
            {"type": "Step", "name": "更换线圈"},
        ],
    },
    {
        "input": (
            "空压机启动后震动很大，还有异常响声，检查发现地脚螺栓松动了。"
            "需要紧固地脚螺栓，同时注意检查各连接部位是否牢固。"
        ),
        "output": [
            {"type": "Symptom", "name": "空压机启动后震动大"},
            {"type": "Symptom", "name": "异常响声"},
            {"type": "Cause", "name": "地脚螺栓松动"},
            {"type": "Step", "name": "紧固地脚螺栓"},
            {"type": "Precaution", "name": "检查各连接部位是否牢固"},
        ],
    },
]


def _build_fewshot_prompt(text: str) -> str:
    """
    构造 few-shot extraction prompt（Qwen2.5 chat 格式）。

    模板结构：
      system message → 角色设定 + 实体类型说明
      user message   → few-shot 示例 + 实际输入文本
      assistant prefix → 触发模型生成
    """
    prompt = (
        "<|im_start|>system\n"
        "你是一个船舶故障知识抽取助手。从输入的故障描述文本中提取知识实体，"
        "只返回JSON格式的实体列表。\n\n"
        "实体类型：\n"
        "- Symptom: 故障现象\n"
        "- Cause: 故障原因\n"
        "- Step: 维修步骤\n"
        "- Precaution: 注意事项\n\n"
        "只输出JSON数组，不要输出任何解释。\n"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        "参考以下示例，从输入文本中抽取知识实体：\n\n"
    )

    for i, ex in enumerate(_FEWSHOT_EXAMPLES, 1):
        output_json = json.dumps(ex["output"], ensure_ascii=False, indent=2)
        prompt += (
            f"示例{i}：\n"
            f"输入：{ex['input']}\n"
            f"输出：\n{output_json}\n\n"
        )

    prompt += (
        f"现在请抽取以下文本：\n"
        f"输入：{text}\n"
        f"输出：\n"
        f"<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    return prompt


def _parse_model_response(response: str) -> list[dict[str, Any]]:
    """
    解析模型返回的文本，提取 JSON 实体列表。

    处理模型可能输出的多种格式：
    - ```json ... ``` 代码块包裹
    - 纯 JSON 数组
    - 文本前后缀 + JSON 数组

    返回：统一格式的实体列表，每个含 uid/type/name/source/confidence/relations
    """
    # 步骤1：提取 JSON 代码块（如果存在）
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response)
    text = json_match.group(1) if json_match else response

    # 步骤2：定位 JSON 数组边界
    try:
        start = text.index("[")
        end = text.rindex("]")
        json_str = text[start : end + 1]
        data = json.loads(json_str)
    except (ValueError, json.JSONDecodeError) as e:
        logger.warning("Failed to parse model JSON response: %s", e)
        return []

    # 步骤3：校验字段并统一格式
    entities: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        entity_type = item.get("type", "")
        name = item.get("name", "").strip()
        if not entity_type or not name:
            continue
        if entity_type not in ("Symptom", "Cause", "Step", "Precaution"):
            logger.debug("Skipping unknown entity type from model: %s", entity_type)
            continue

        entities.append({
            "uid": f"CAND_{uuid.uuid4().hex[:6]}",
            "type": entity_type,
            "name": name,
            "source": "model",
            "confidence": "medium",
            "relations": [],
        })

    return entities


def extract_with_model(text: str) -> list[dict[str, Any]]:
    """
    用 1.5B few-shot 模型抽取非规范文本中的知识（覆盖约 25% 的文本）。

    实现思路：
    1. 构造 few-shot prompt：包含 2 个抽取示例（船舶故障文本 → 结构化实体）
    2. 通过新事件桥调用 core/llm.generate() 非流式生成
    3. 解析 JSON 输出，标记 source="model", confidence="medium"

    参数：
        text: 非规范格式的故障描述文本（如段落叙述式 "电机最近老是打不着火…"）

    返回：
        list[dict]: 候选实体列表，格式与 extract_with_regex() 一致：
            uid, type, name, source="model", confidence="medium", relations=[]

    注意：本函数同步阻塞，内部创建临时事件循环调用异步 generate()。
          extract_with_regex() 和 extract_knowledge() 不受影响。
    """
    if not text or not text.strip():
        return []

    # 截断过长输入，避免超出模型上下文窗口
    if len(text) > MAX_INPUT_LENGTH:
        text = text[:MAX_INPUT_LENGTH]
        logger.info("Input text truncated to %d characters", MAX_INPUT_LENGTH)

    # 1. 构造 few-shot prompt
    prompt = _build_fewshot_prompt(text)

    # 2. 调用 llama-server 非流式生成（async → sync 桥接）
    #    core/llm.generate() 是 async，通过新事件循环同步调用
    from core.llm import generate

    try:
        loop = asyncio.new_event_loop()
        try:
            response = loop.run_until_complete(
                generate(prompt, temperature=0.1, max_tokens=512)
            )
        finally:
            loop.close()
    except Exception as e:
        logger.exception("Model extraction failed: %s", e)
        return []

    if not response or not response.strip():
        logger.warning("Model returned empty response for text: %.50s...", text[:50])
        return []

    # 3. 解析响应
    entities = _parse_model_response(response)
    if not entities:
        logger.warning(
            "Parsed zero entities from model response. text=%.50s... response=%.100s...",
            text[:50],
            response[:100],
        )

    logger.info(
        "Model extraction: input=%d chars → %d entities",
        len(text),
        len(entities),
    )
    return entities


# ==================== 混合抽取入口 ====================

def extract_knowledge(text: str) -> dict[str, Any]:
    """
    混合知识抽取 — 对外统一入口。
    
    策略：正则优先，正则未覆盖的交给模型补充。
    
    判断逻辑：
    - 如果正则已经抽取到了 Symptom 和 Cause → 模型跳过（节省推理时间）
    - 如果正则未抽取到 Symptom 或 Cause → 启动模型补充（非规范文本）

    参数：
        text: 从文档解析出的纯文本

    返回：
        {
            "candidates": [...],     # 全部候选实体（正则 + 模型）
            "regex_count": int,      # 正则抽取到的数量
            "model_count": int,      # 模型抽取到的数量（当前始终为 0）
        }
    """
    # 正则抽取（主路径，覆盖 70% 文本）
    regex_candidates = extract_with_regex(text)

    # 检查正则覆盖率：是否抽到了 Symptom 和 Cause？
    has_symptom = any(c["type"] == "Symptom" for c in regex_candidates)
    has_cause = any(c["type"] == "Cause" for c in regex_candidates)

    # 正则未覆盖 → 启动模型补充（覆盖 25% 文本）
    # 注意：extract_with_model 当前是占位实现，始终返回 []
    model_candidates = []
    if not has_symptom or not has_cause:
        model_candidates = extract_with_model(text)

    return {
        "candidates": regex_candidates + model_candidates,
        "regex_count": len(regex_candidates),
        "model_count": len(model_candidates),
    }
