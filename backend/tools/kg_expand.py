#!/usr/bin/env python
"""
A21 知识图谱大规模扩充脚本
==========================
从《船舶电气设备维护与修理》文本中提取故障知识三元组，生成 Cypher 导入脚本。

策略：字典规则匹配（主要）+ 正则模式匹配（补充）
覆盖设备：接触器、断路器、热继电器、电动机、发电机、变压器、起货机、锚机、舵机、锅炉、配电装置、报警系统

输出：data/kg_expanded.cypher
"""

import re
import os
import sys
from pathlib import Path
from collections import defaultdict

# 项目根目录 (tools/ → backend/ → A21_final/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================================================
# 一、领域词典定义
# ============================================================

# 设备名称 → [别名, 变体]
EQUIPMENT_DICT = {
    "接触器": ["接触器", "交流接触器", "直流接触器", "电磁接触器"],
    "断路器": ["断路器", "空气断路器", "万能式断路器", "塑壳断路器", "自动开关"],
    "热继电器": ["热继电器", "热保护继电器", "FR"],
    "电动机": ["电动机", "电机", "三相异步电动机", "异步电机", "直流电机", "船用电机", "三相电机", "交流电机"],
    "发电机": ["发电机", "直流发电机", "交流发电机", "同步发电机", "发电机组"],
    "变压器": ["变压器", "船用变压器", "照明变压器", "隔离变压器"],
    "起货机": ["起货机", "克令吊", "起重机", "电动起货机"],
    "锚机": ["锚机", "绞缆机", "绞盘机", "锚绞机"],
    "舵机": ["舵机", "电动舵机", "液压舵机", "舵机系统"],
    "锅炉": ["锅炉", "辅锅炉", "废气锅炉", "燃油锅炉"],
    "配电装置": ["配电装置", "配电板", "主配电板", "应急配电板", "配电屏", "配电箱"],
    "报警系统": ["报警装置", "火灾报警", "监测系统", "机舱监测", "报警系统"],
}

# 故障现象词典（手动收集常见故障表述）
SYMPTOM_DICT = {
    "接触器": {
        "不能吸合": ["不能吸合", "吸不上", "吸力不足", "不能闭合", "无法吸合", "不动作"],
        "噪声大": ["噪声大", "嗡鸣", "嗡嗡响", "振动噪声", "电磁噪声", "响声大"],
        "线圈过热": ["线圈过热", "线圈烧毁", "线圈烧损", "线圈发热", "冒烟", "线圈烧坏"],
        "不释放": ["不释放", "释放缓慢", "不能释放", "衔铁不释放", "断电后不释放"],
        "触头熔焊": ["触头熔焊", "触头焊住", "触头粘连", "触头粘接"],
        "触头过热": ["触头过热", "触头发热", "触头灼伤", "触头变色"],
        "触头磨损": ["触头磨损", "触头过度磨损", "触头损耗"],
    },
    "电动机": {
        "不能起动": ["不能起动", "不能启动", "无法起动", "无法启动", "打不着火", "不能转动"],
        "过热": ["过热", "发热", "冒烟", "温度过高", "温升过高", "烧毁", "冒黑烟"],
        "振动异常": ["振动异常", "振动大", "振动", "震动", "噪音大", "异响"],
        "转速异常": ["转速低", "转速不稳", "转速波动", "转速下降", "速度慢"],
        "绝缘降低": ["绝缘降低", "绝缘电阻低", "漏电", "对地短路"],
        "单相运行": ["单相运行", "缺相", "断相", "两相运行"],
    },
    "发电机": {
        "不能建压": ["不能建压", "不能建立电压", "无电压输出", "发不出电", "不发电"],
        "电压低": ["电压低", "电压偏低", "输出电压低", "电压不足"],
        "电压不稳": ["电压不稳", "电压波动", "电压振荡", "电压跳动"],
        "过热": ["过热", "温度高", "发热严重", "冒烟"],
        "异响": ["异响", "异常响声", "噪声大", "振动大"],
    },
    "变压器": {
        "过热": ["过热", "温度高", "发热", "冒烟", "烧毁"],
        "噪声大": ["噪声大", "嗡声", "嗡嗡响", "振动"],
        "绝缘降低": ["绝缘降低", "绝缘电阻低", "受潮", "绝缘老化"],
        "输出电压异常": ["输出电压异常", "电压不稳", "电压低", "无输出"],
    },
    "断路器": {
        "不能合闸": ["不能合闸", "合不上", "不能闭合", "合闸失败"],
        "不能分闸": ["不能分闸", "分不开", "不能断开", "跳不开"],
        "误跳闸": ["误跳闸", "误动作", "无故跳闸", "频繁跳闸"],
        "过热": ["过热", "发热", "接线端过热"],
    },
    "热继电器": {
        "误动作": ["误动作", "误跳", "不该跳时跳了"],
        "不动作": ["不动作", "不跳", "该跳时不跳", "拒动"],
        "动作不稳定": ["动作不稳定", "时跳时不跳", "动作值变化"],
    },
    "起货机": {
        "不能起动": ["不能起动", "无法起动", "不起动"],
        "不能调速": ["不能调速", "速度失控", "调速失灵"],
        "不能制动": ["不能制动", "制动失灵", "刹不住"],
        "提升力不足": ["提升力不足", "提不起", "无力", "起吊慢"],
    },
    "配电装置": {
        "不能合闸": ["不能合闸", "主开关合不上"],
        "电压异常": ["电压异常", "电压波动", "电压低"],
        "保护误动": ["保护误动", "误跳闸", "保护误动作"],
    },
}

# 故障原因词典
CAUSE_DICT = {
    "电气": [
        "电源电压过低", "电源电压过高", "电源缺相", "电源未接通",
        "线圈匝间短路", "线圈断路", "线圈内部短路",
        "绕组短路", "绕组断路", "绕组接地", "绕组受潮",
        "绝缘老化", "绝缘损坏", "绝缘电阻降低",
        "接触不良", "接线松动", "接线错误", "接线端子氧化",
        "触头接触不良", "触头压力不足", "触头弹簧失效",
        "短路环断裂", "短路环脱落",
        "电刷接触不良", "电刷磨损", "换向器表面不平",
        "励磁回路断路", "励磁电流不足",
        "熔断器熔断", "热元件烧断",
        "控制回路故障", "控制电源故障",
    ],
    "机械": [
        "机械卡阻", "转轴锈蚀", "轴承损坏", "轴承缺油",
        "弹簧反力过大", "弹簧失效", "弹簧断裂",
        "衔铁气隙过大", "衔铁歪斜", "铁心极面有异物",
        "运动部分卡死", "传动机构故障",
        "转子不平衡", "转子扫膛",
        "联轴器松动", "地脚螺栓松动",
        "风扇损坏", "风道堵塞",
    ],
    "环境": [
        "环境温度过高", "环境潮湿", "有腐蚀性气体",
        "灰尘过多", "通风不良", "散热条件差",
        "船体振动", "盐雾侵蚀",
    ],
    "操作": [
        "操作频率过高", "过载使用", "频繁起动",
        "负载过大", "堵转", "长期过载",
    ],
}

# 维修步骤词典（常见维修操作）
STEP_DICT = [
    "用万用表测量电源电压", "检查三相电源是否正常",
    "用绝缘电阻表测量绝缘电阻", "测量绕组直流电阻",
    "拆下检查线圈是否烧毁", "更换线圈",
    "清理触头表面氧化层", "调整触头压力",
    "打磨触头接触面", "更换触头",
    "检查并紧固接线端子", "重新接线",
    "检查短路环是否断裂", "更换短路环",
    "清洁铁心极面", "去除铁心极面油污",
    "调整衔铁气隙", "校正衔铁位置",
    "检查弹簧并更换", "调整弹簧压力",
    "检查轴承并更换", "添加润滑油",
    "检查风扇是否正常", "清理风道",
    "测量三相电流平衡", "检查是否缺相",
    "检查负载是否过大", "适当降低负载",
    "检查电刷并更换", "清洁换向器表面",
    "检查励磁回路", "调整励磁电流",
    "检查控制回路接线", "更换控制元件",
    "检查热继电器整定值", "重新整定热继电器",
    "停电检查主触头", "测量触头接触电阻",
    "用摇表测量对地绝缘", "干燥处理绕组",
    "断电挂牌", "确认断电后方可操作",
    "检查保护装置设定值", "核对保护定值",
    "检查熔断器", "更换熔断器",
]

# 注意事项词典
PRECAUTION_DICT = [
    "断电挂牌后方可操作", "确认电源已切断",
    "使用绝缘工具", "穿戴绝缘手套",
    "电容放电后再操作", "等待电容放电2-3分钟",
    "测量时注意量程选择", "使用合适的仪表量程",
    "更换元件时确保型号一致", "使用原厂配件",
    "注意操作顺序", "先检查后拆卸",
    "防止机械损伤", "轻拿轻放",
    "防止触电", "注意高压危险",
    "保持现场通风", "注意防火",
    "记录维修过程", "做好维修记录",
]


# ============================================================
# 二、正则模式匹配
# ============================================================

def extract_by_patterns(text: str) -> list[dict]:
    """用正则匹配结构化故障描述"""
    triples = []
    uid_counter = 1000

    # 模式1：序号+故障现象+原因+处理方法（最标准格式）
    pattern1 = re.compile(
        r'(?:^|\n)\s*(?:\d+[\.\、\)）]\s*)?'
        r'(?:故障现象[：:]\s*)?'
        r'(.{4,30}?)(?:故障|现象|，)'
        r'.{0,50}?'
        r'(?:故障原因|原因)[：:]\s*(.{10,100}?)(?:\n|故障现象|维修|处理|$)',
        re.MULTILINE
    )

    # 模式2：表格式（数字序号开头 + 设备名）
    pattern2 = re.compile(
        r'(?:^|\n)\s*\d+[\.\、]\s*'
        r'([\u4e00-\u9fff]{2,15}(?:不能|无法|不|异常|过大|过低|过高|烧|断|坏|损|卡)[\u4e00-\u9fff]{0,15})'
        r'.{0,200}?'
        r'([\u4e00-\u9fff]{2,4}(?:电压|流|阻|断|路|短|损|坏|卡|锈|潮|尘|热|频|载|磨|老|触)[\u4e00-\u9fff]{0,20})',
        re.MULTILINE
    )

    # 模式3：表X-X 故障表
    pattern3 = re.compile(
        r'表\d+[-—]\d+\s*.{0,30}?(?:故障|常见故障)',
        re.IGNORECASE
    )

    return triples


# ============================================================
# 三、词典匹配提取（主要方法）
# ============================================================

def extract_by_dictionary(text: str) -> list[dict]:
    """用词典匹配提取故障三元组"""
    triples = []
    uid_counter = 1000

    # 去掉无关内容（图片标记、目录等）
    cleaned = re.sub(r'\[Image:.*?\]', '', text)
    cleaned = re.sub(r'\[目录\].*?(?=\n\n|\n第)', '', cleaned, flags=re.DOTALL)

    for equip_name, aliases in EQUIPMENT_DICT.items():
        symptoms = SYMPTOM_DICT.get(equip_name, {})
        if not symptoms:
            continue

        for symp_name, keywords in symptoms.items():
            for kw in keywords:
                # 在文本中搜索关键词
                for m in re.finditer(re.escape(kw), cleaned):
                    start = max(0, m.start() - 200)
                    end = min(len(cleaned), m.end() + 500)
                    context = cleaned[start:end]

                    # 在上下文中查找原因关键词
                    found_causes = []
                    for cat, causes in CAUSE_DICT.items():
                        for cause in causes:
                            if cause in context and cause not in [c["cause"] for c in found_causes]:
                                found_causes.append({"cause": cause, "category": cat})

                    # 在上下文中查找步骤关键词
                    found_steps = []
                    for step in STEP_DICT:
                        if step in context and step not in found_steps:
                            found_steps.append(step)

                    # 在上下文中查找注意事项
                    found_precautions = []
                    for prec in PRECAUTION_DICT:
                        if prec in context and prec not in found_precautions:
                            found_precautions.append(prec)

                    if found_causes:
                        uid_counter += 1
                        triples.append({
                            "uid": f"EXP_{uid_counter:04d}",
                            "equipment": equip_name,
                            "symptom": symp_name,
                            "symptom_keyword": kw,
                            "causes": found_causes[:5],
                            "steps": found_steps[:5],
                            "precautions": found_precautions[:3],
                            "context": context[:200],
                        })
                        break  # 每个症状只取第一次匹配

    return triples


# ============================================================
# 四、生成 Cypher 导入脚本
# ============================================================

def c(s):
    """Escape single quotes for Cypher strings."""
    return s.replace("'", "\\'")

def generate_cypher(triples: list[dict], output_path: str):
    """从三元组生成 Cypher MERGE 语句"""
    lines = [
        "// A21 KG Expanded Data",
        f"// Triples: {len(triples)}",
        "",
    ]

    seen_symptoms = set()
    unique_triples = []
    for t in triples:
        key = (t["equipment"], t["symptom"])
        if key not in seen_symptoms:
            seen_symptoms.add(key)
            unique_triples.append(t)

    cause_idx = 5000
    step_idx = 6000
    prec_idx = 7000
    used_causes = {}
    used_steps = {}
    used_precs = {}

    equip_uid_map = {
        "接触器": "E_CONTACTOR", "断路器": "E_BREAKER",
        "热继电器": "E_THERMAL_RELAY", "电动机": "E_ASYNCH_MOTOR",
        "发电机": "E_GENERATOR", "变压器": "E_TRANSFORMER",
        "起货机": "E_WINCH", "锚机": "E_ANCHOR",
        "舵机": "E_STEER", "锅炉": "E_BOILER",
        "配电装置": "E_PDIST", "报警系统": "E_FIRE_ALARM",
    }

    for t in unique_triples:
        equip = t["equipment"]
        symp = t["symptom"]
        uid = t["uid"]

        lines.append(f"// --- {equip}: {symp} ---")

        # Symptom
        name_safe = c(equip + symp)
        lines.append(
            f"MERGE (s_{uid}:Symptom {{uid: '{uid}'}}) "
            f"SET s_{uid}.name='{name_safe}', "
            f"s_{uid}.source_doc='船舶电气设备维护与修理', "
            f"s_{uid}.created_at=timestamp()"
        )

        # BELONGS_TO
        equip_uid = equip_uid_map.get(equip)
        if equip_uid:
            lines.append(
                f"MATCH (e:Equipment {{uid: '{equip_uid}'}}) "
                f"MERGE (s_{uid})-[:BELONGS_TO]->(e)"
            )

        # Causes
        for i, cause in enumerate(t["causes"][:5], 1):
            cause_name = c(cause["cause"])
            if cause_name not in used_causes:
                cid = f"C_{cause_idx}"
                used_causes[cause_name] = cid
                lines.append(
                    f"MERGE (c_{cid}:Cause {{uid: '{cid}'}}) "
                    f"SET c_{cid}.name='{cause_name}', "
                    f"c_{cid}.created_at=timestamp()"
                )
                cause_idx += 1
            lines.append(
                f"MERGE (s_{uid})-[:CAUSED_BY {{priority: {i}}}]->"
                f"(c_{used_causes[cause_name]})"
            )

        # Steps
        prev_step_uid = None
        for i, step_name in enumerate(t["steps"][:4], 1):
            step_name_safe = c(step_name)
            if step_name not in used_steps:
                sid = f"ST_{step_idx}"
                used_steps[step_name] = sid
                lines.append(
                    f"MERGE (st_{sid}:Step {{uid: '{sid}'}}) "
                    f"SET st_{sid}.name='{step_name_safe}', "
                    f"st_{sid}.created_at=timestamp()"
                )
                step_idx += 1

            if i == 1 and t["causes"]:
                first_cause = c(t["causes"][0]["cause"])
                if first_cause in used_causes:
                    lines.append(
                        f"MERGE (c_{used_causes[first_cause]})-[:FIXED_BY]->"
                        f"(st_{used_steps[step_name]})"
                    )

            if prev_step_uid:
                lines.append(
                    f"MERGE (st_{prev_step_uid})-[:NEXT_STEP]->"
                    f"(st_{used_steps[step_name]})"
                )
            prev_step_uid = used_steps[step_name]

        # Precautions
        for prec_name in t["precautions"][:3]:
            prec_safe = c(prec_name)
            if prec_name not in used_precs:
                pid = f"P_{prec_idx}"
                used_precs[prec_name] = pid
                lines.append(
                    f"MERGE (p_{pid}:Precaution {{uid: '{pid}'}}) "
                    f"SET p_{pid}.name='{prec_safe}', "
                    f"p_{pid}.created_at=timestamp()"
                )
                prec_idx += 1
            if prev_step_uid:
                lines.append(
                    f"MERGE (st_{prev_step_uid})-[:HAS_PRECAUTION]->"
                    f"(p_{used_precs[prec_name]})"
                )

        lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return len(unique_triples), cause_idx - 5000, step_idx - 6000, prec_idx - 7000


# ============================================================
# 五、主流程
# ============================================================

def main():
    data_file = BASE_DIR / "data" / "raw" / "船舶电气设备维护与修理_增强.txt"
    if not data_file.exists():
        print(f"ERROR: Data file not found at {data_file}")
        sys.exit(1)

    print(f"Loading data: {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Text size: {len(text)} chars")

    # 词典匹配提取
    print("Extracting triples by dictionary matching...")
    triples = extract_by_dictionary(text)
    print(f"Extracted {len(triples)} triples")

    # 生成 Cypher
    output_path = BASE_DIR / "data" / "kg_expanded.cypher"
    n_symptoms, n_causes, n_steps, n_precs = generate_cypher(triples, str(output_path))

    print(f"\n=== Generation Summary ===")
    print(f"Symptoms: {n_symptoms}")
    print(f"New Causes: {n_causes}")
    print(f"New Steps: {n_steps}")
    print(f"New Precautions: {n_precs}")
    print(f"Total new entities: {n_symptoms + n_causes + n_steps + n_precs}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
