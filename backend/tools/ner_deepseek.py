"""
A21 知识图谱 NER 抽取 — DeepSeek API 版
========================================
使用 DeepSeek API 对《船舶电气设备维护与修理》文本进行实体关系抽取。
输出结构化三元组 → 生成 Cypher → 导入 Neo4j。

用法:
  1. 设置环境变量 DEEPSEEK_API_KEY 或在 .env 中配置
  2. python tools/ner_deepseek.py
  3. 产出 data/kg_ner_output.cypher
  4. cypher-shell 导入

抽取目标: 每段文本提取 (设备→故障现象→故障原因→维修步骤→注意事项) 五元组
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import httpx

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # tools/ → backend/ → A21_final/

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"  # 128K context, 价格便宜

# 处理参数
CHUNK_SIZE = 20000   # 每批字符数（~10K tokens，提高JSON质量）
MAX_RETRIES = 3

# 抽取 Prompt
EXTRACTION_PROMPT = """你是一位船舶电气设备故障知识工程师。请从以下船舶电气设备维护教材文本中，提取故障诊断相关知识，输出结构化 JSON。

提取规则：
1. 识别文本中提到的设备（Equipment）
2. 识别故障现象（Symptom）—— 设备不能正常工作、异常表现
3. 识别故障原因（Cause）—— 导致故障的根本原因
4. 识别维修步骤（Step）—— 维修操作、检查方法
5. 识别注意事项（Precaution）—— 安全提醒、特殊要求
6. 每个 Symptom 关联到对应的 Cause 和 Step

输出 JSON 格式（严格遵守）：
```json
[
  {
    "equipment": "接触器",
    "symptom": "线圈过热或烧损",
    "symptom_features": ["过热", "烧损", "冒烟"],
    "causes": [
      {"cause": "电源电压过高(>1.1UN)或过低(<0.85UN)", "priority": 1, "check_method": "measure"},
      {"cause": "线圈内部短路", "priority": 2, "check_method": "measure"}
    ],
    "steps": [
      "用万用表测量电源电压",
      "检查线圈引线与导线是否脱焊或断路",
      "若线圈内部短路需更换线圈"
    ],
    "tools": ["万用表"],
    "precautions": ["断电挂牌后方可操作"],
    "source_page": "第四章第二节"
  }
]
```

注意：
- 只提取文本中明确提到的内容，不要编造
- 每个 symptom、cause、step 的文本要精确，尽量用原文
- 如果文本没有明确的故障现象，返回空数组 []
- priority 越小表示越可能是主要原因

文本内容如下：

{text}

请只输出 JSON 数组，不要输出其他内容。"""


def split_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """将文本按段落边界分块，每块不超过 chunk_size 字符"""
    # 先按双换行分段
    paragraphs = text.split('\n\n')
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) > chunk_size and current:
            chunks.append(current.strip())
            current = para
        else:
            current += "\n\n" + para if current else para
    if current.strip():
        chunks.append(current.strip())
    return chunks


def clean_text(text: str) -> str:
    """清洗文本：去掉图片标记、目录、页眉等"""
    text = re.sub(r'\[Image:.*?\]', '', text)
    text = re.sub(r'\[目录\].*?(?=\n第|\n\n第|\Z)', '', text, flags=re.DOTALL)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


async def extract_chunk(client: httpx.AsyncClient, text: str) -> list[dict]:
    """调用 DeepSeek API 抽取单个文本块"""
    prompt = EXTRACTION_PROMPT.replace("{text}", text[:CHUNK_SIZE])

    for attempt in range(MAX_RETRIES):
        try:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": "你是一个精确的知识抽取助手。只输出JSON，不输出其他内容。确保JSON格式正确，所有逗号、括号匹配。"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 4096,
                },
                timeout=120.0,
            )

            if response.status_code != 200:
                print(f"  API error {response.status_code}: {response.text[:200]}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(3 * (attempt + 1))
                    continue
                return []

            content = response.json()["choices"][0]["message"]["content"]

            # 提取 JSON 数组
            json_match = re.search(r'\[[\s\S]*\]', content)
            if not json_match:
                print(f"  No JSON found: {content[:200]}")
                return []

            json_str = json_match.group()

            # 尝试多种解析方式
            data = _robust_json_parse(json_str, content)
            return data

        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(3 * (attempt + 1))

    return []


def _robust_json_parse(json_str: str, full_content: str) -> list[dict]:
    """容错 JSON 解析：尝试标准解析 → 修复常见错误 → 逐对象解析"""
    # 方法1：标准解析
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # 方法2：修复常见 JSON 错误（缺少逗号、多余逗号等）
    fixed = json_str
    # 修复：对象之间缺少逗号 (}\s*{ → },{)
    fixed = re.sub(r'\}\s*\{', '},{', fixed)
    # 修复：数组之间缺少逗号 (]\s*[ → ],[)
    fixed = re.sub(r'\]\s*\[', '],[', fixed)
    # 修复：尾随逗号 (,\s*] 或 ,\s*})
    fixed = re.sub(r',\s*\]', ']', fixed)
    fixed = re.sub(r',\s*\}', '}', fixed)

    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"  Fixed JSON also failed at line {e.lineno}: {e.msg}")

    # 方法3：逐对象提取（正则匹配每个 {...} 单独解析）
    objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', fixed)
    results = []
    for obj_str in objects:
        try:
            results.append(json.loads(obj_str))
        except json.JSONDecodeError:
            # 尝试修复单对象
            obj_fixed = re.sub(r',\s*\}', '}', obj_str)
            try:
                results.append(json.loads(obj_fixed))
            except json.JSONDecodeError:
                continue

    if results:
        print(f"  Recovered {len(results)} objects via regex extraction")
    return results


def merge_triples(all_triples: list[dict]) -> list[dict]:
    """去重合并三元组（同一设备+症状名去重）"""
    seen = set()
    merged = []
    for t in all_triples:
        key = (t.get("equipment", ""), t.get("symptom", ""))
        if key not in seen:
            seen.add(key)
            merged.append(t)
    return merged


def generate_cypher(triples: list[dict], output_path: str) -> dict:
    """生成 Cypher 导入脚本"""
    lines = [
        "// A21 NER抽取数据 — DeepSeek API",
        f"// 三元组数: {len(triples)}",
        "// 自动生成于 " + time.strftime("%Y-%m-%d %H:%M"),
        "",
    ]

    equip_uid_map = {
        "接触器": "E_CONTACTOR", "断路器": "E_BREAKER",
        "热继电器": "E_THERMAL_RELAY", "电动机": "E_ASYNCH_MOTOR",
        "电机": "E_ASYNCH_MOTOR", "三相异步电动机": "E_ASYNCH_MOTOR",
        "直流电机": "E_DC_MOTOR", "发电机": "E_GENERATOR",
        "变压器": "E_TRANSFORMER", "船用变压器": "E_TRANSFORMER",
        "起货机": "E_WINCH", "锚机": "E_ANCHOR", "绞缆机": "E_ANCHOR",
        "舵机": "E_STEER", "锅炉": "E_BOILER", "辅锅炉": "E_BOILER",
        "配电装置": "E_PDIST", "配电板": "E_PDIST",
        "报警装置": "E_FIRE_ALARM", "火灾报警": "E_FIRE_ALARM",
        "监测系统": "E_MONITOR", "机舱监测": "E_MONITOR",
        "PLC": "E_PLC",
    }

    cause_idx = 8000
    step_idx = 9000
    prec_idx = 10000
    tool_idx = 11000
    symp_idx = 2000

    used_causes = {}
    counts = {"symptoms": 0, "causes": 0, "steps": 0, "precautions": 0, "tools": 0, "relationships": 0}

    def esc(s):
        return s.replace("'", "\\'").replace('"', '\\"')

    for t in triples:
        equip = t.get("equipment", "")
        symptom = t.get("symptom", "")
        if not equip or not symptom:
            continue

        symp_uid = f"S_DEEP_{symp_idx}"
        symp_idx += 1
        lines.append(f"// --- {equip}: {symptom} ---")

        # Symptom
        features = json.dumps(t.get("symptom_features", []), ensure_ascii=False)
        source_page = esc(t.get("source_page", ""))
        lines.append(
            f"MERGE (s_{symp_uid}:Symptom {{uid: '{symp_uid}'}}) "
            f"SET s_{symp_uid}.name='{esc(symptom)}', "
            f"s_{symp_uid}.primary_features={features}, "
            f"s_{symp_uid}.source_doc='船舶电气设备维护与修理', "
            f"s_{symp_uid}.source_page='{source_page}', "
            f"s_{symp_uid}.created_at=timestamp()"
        )
        counts["symptoms"] += 1

        # BELONGS_TO
        equip_uid = equip_uid_map.get(equip)
        if equip_uid:
            lines.append(
                f"MATCH (e:Equipment {{uid: '{equip_uid}'}}) "
                f"MERGE (s_{symp_uid})-[:BELONGS_TO]->(e)"
            )
            counts["relationships"] += 1

        # Causes
        causes = t.get("causes", [])
        for i, c in enumerate(causes[:5], 1):
            cause_name = c.get("cause", "")
            if not cause_name:
                continue
            if cause_name not in used_causes:
                cid = f"C_DEEP_{cause_idx}"
                cause_idx += 1
                used_causes[cause_name] = cid
                lines.append(
                    f"MERGE (c_{cid}:Cause {{uid: '{cid}'}}) "
                    f"SET c_{cid}.name='{esc(cause_name)}', "
                    f"c_{cid}.check_method='{c.get('check_method', '')}', "
                    f"c_{cid}.created_at=timestamp()"
                )
                counts["causes"] += 1
            lines.append(
                f"MERGE (s_{symp_uid})-[:CAUSED_BY {{priority: {i}}}]->(c_{used_causes[cause_name]})"
            )
            counts["relationships"] += 1

        # Steps
        steps = t.get("steps", [])
        prev_step_uid = None
        for i, step_name in enumerate(steps[:5]):
            if not step_name:
                continue
            sid = f"ST_DEEP_{step_idx}"
            step_idx += 1
            lines.append(
                f"MERGE (st_{sid}:Step {{uid: '{sid}'}}) "
                f"SET st_{sid}.name='{esc(step_name)}', "
                f"st_{sid}.created_at=timestamp()"
            )
            counts["steps"] += 1

            if i == 0 and causes:
                first_cause = causes[0].get("cause", "")
                if first_cause in used_causes:
                    lines.append(
                        f"MERGE (c_{used_causes[first_cause]})-[:FIXED_BY]->(st_{sid})"
                    )
                    counts["relationships"] += 1

            if prev_step_uid:
                lines.append(f"MERGE (st_{prev_step_uid})-[:NEXT_STEP]->(st_{sid})")
                counts["relationships"] += 1
            prev_step_uid = sid

        # Precautions
        precs = t.get("precautions", [])
        for prec_name in precs[:3]:
            if not prec_name:
                continue
            pid = f"P_DEEP_{prec_idx}"
            prec_idx += 1
            lines.append(
                f"MERGE (p_{pid}:Precaution {{uid: '{pid}'}}) "
                f"SET p_{pid}.name='{esc(prec_name)}', "
                f"p_{pid}.created_at=timestamp()"
            )
            counts["precautions"] += 1
            if prev_step_uid:
                lines.append(f"MERGE (st_{prev_step_uid})-[:HAS_PRECAUTION]->(p_{pid})")
                counts["relationships"] += 1

        # Tools
        tools = t.get("tools", [])
        for tool_name in tools[:5]:
            if not tool_name:
                continue
            tid = f"T_DEEP_{tool_idx}"
            tool_idx += 1
            lines.append(
                f"MERGE (t_{tid}:Tool {{uid: '{tid}'}}) "
                f"SET t_{tid}.name='{esc(tool_name)}', "
                f"t_{tid}.created_at=timestamp()"
            )
            counts["tools"] += 1
            if prev_step_uid:
                lines.append(f"MERGE (st_{prev_step_uid})-[:REQUIRES_TOOL]->(t_{tid})")
                counts["relationships"] += 1

        lines.append("")

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return counts


async def main():
    if not DEEPSEEK_API_KEY:
        print("=" * 60)
        print("ERROR: 请设置 DEEPSEEK_API_KEY 环境变量")
        print("  Windows: $env:DEEPSEEK_API_KEY='sk-xxx'")
        print("  Linux:   export DEEPSEEK_API_KEY='sk-xxx'")
        print("=" * 60)
        sys.exit(1)

    data_file = BASE_DIR / "data" / "raw" / "船舶电气设备维护与修理_增强.txt"
    if not data_file.exists():
        print(f"ERROR: Data file not found: {data_file}")
        sys.exit(1)

    with open(data_file, 'r', encoding='utf-8') as f:
        text = f.read()

    text = clean_text(text)
    print(f"Total text: {len(text)} chars (~{len(text)//2} tokens)")

    # 分块
    chunks = split_text(text, CHUNK_SIZE)
    print(f"Split into {len(chunks)} chunks")

    # 批量抽取
    all_triples = []
    async with httpx.AsyncClient() as client:
        for i, chunk in enumerate(chunks):
            print(f"\n[{i+1}/{len(chunks)}] Processing chunk ({len(chunk)} chars)...")
            triples = await extract_chunk(client, chunk)
            print(f"  Extracted {len(triples)} triples")
            all_triples.extend(triples)

            if i < len(chunks) - 1:
                time.sleep(1)  # rate limit

    # 去重
    merged = merge_triples(all_triples)
    print(f"\n{'='*40}")
    print(f"Total raw triples: {len(all_triples)}")
    print(f"After dedup: {len(merged)}")

    # 生成 Cypher
    output_path = BASE_DIR / "data" / "kg_ner_output.cypher"
    counts = generate_cypher(merged, str(output_path))

    print(f"\n=== 将导入 Neo4j ===")
    print(f"Symptoms: {counts['symptoms']}")
    print(f"Causes: {counts['causes']}")
    print(f"Steps: {counts['steps']}")
    print(f"Precautions: {counts['precautions']}")
    print(f"Tools: {counts['tools']}")
    print(f"Total entities: {sum(v for k,v in counts.items() if k != 'relationships')}")
    print(f"Relationships: {counts['relationships']}")
    print(f"\nOutput: {output_path}")
    print(f"\n导入命令:")
    print(f"  cypher-shell -u neo4j -p a21password -f data/kg_ner_output.cypher")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
