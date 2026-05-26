# 知识图谱 NER 抽取技术文档

> 版本: v2.0 | 日期: 2026-05-26

---

## 一、抽取策略

A21 系统使用两种方式从《船舶电气设备维护与修理》教材文本中抽取故障知识三元组：

### 1.1 词典规则匹配（`kg_expand.py`）

```
源文本 → 设备词典(12类) → 症状词典(60+关键词) → 原因词典(40+) 
       → 步骤词典(20+) → 注意事项词典(10+) → 三元组
```

**覆盖**: 约30%的规范文本（标题明确、格式固定）

### 1.2 NER 模型抽取（`ner_deepseek.py`）

```
源文本 → 清洗 → 分块(20K chars) → DeepSeek API → JSON解析 
       → 容错修复 → 三元组
```

**覆盖**: 约70%的非规范文本（段落叙述式、混合描述）

### 抽取 Prompt 设计

```json
{
  "equipment": "接触器",
  "symptom": "线圈过热或烧损",
  "causes": [
    {"cause": "电源电压过高(>1.1UN)或过低(<0.85UN)", "priority": 1},
    {"cause": "线圈内部短路", "priority": 2}
  ],
  "steps": ["用万用表测量电源电压", "检查线圈引线"],
  "tools": ["万用表"],
  "precautions": ["断电挂牌后方可操作"]
}
```

---

## 二、容错JSON解析

DeepSeek API 返回的JSON常有格式错误（缺少逗号、尾随逗号等）。使用三级容错：

```
1. 标准 json.loads()
     ↓ 失败
2. 正则修复({}\s*{ → },{ 等) → json.loads()
     ↓ 失败
3. 逐对象正则提取 → 单个parse
```

---

## 三、切换到本地LLM

`ner_deepseek.py` 设计为与LLM无关。切换到本地LLM只需修改3行：

```python
# 当前: DeepSeek API
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"

# 切换: 本地 llama-server
LLAMA_BASE_URL = "http://127.0.0.1:8082/v1/chat/completions"
MODEL = "local"  # llama-server 不需要 model 参数

# 即: 将 httpx.post(url) 的 url 和 headers 改为本地地址即可
```

### 本地LLM限制

- Qwen2.5-1.5B 的 JSON 输出质量不如 DeepSeek，更多容错处理
- 上下文窗口 2048 tokens，需要更小的分块（~5000 chars）
- 可以通过设置 `DEEPSEEK_API_KEY=""` 强制使用本地 LLM（需修改代码适配）

---

## 四、产出统计

| 指标 | 词典匹配 | NER抽取 | 合并去重 |
|------|:--:|:--:|:--:|
| Symptom | 30 | 127 | 127 |
| Cause | 23 | 362 | 362 |
| Step | 8 | 397 | 397 |
| Precaution | 0 | 46 | 46 |
| Tool | 0 | 98 | 98 |
| **总实体** | 61 | 1030 | **1066** |
| 关系 | - | 958 | **958** |

---

## 五、文件说明

| 文件 | 用途 |
|------|------|
| `tools/kg_expand.py` | 词典规则匹配（无需API，可离线） |
| `tools/ner_deepseek.py` | NER API抽取（需要API Key） |
| `data/kg_ner_output.cypher` | NER产出 → 直接导入Neo4j |
| `data/kg_bulk.cypher` | 手动编写的批量故障数据 |

---

## 六、版本记录

| 日期 | 变更 |
|------|------|
| 2026-05-26 | v2.0: NER API抽取 + 容错JSON + 1066实体 |
| 2026-05-26 | v1.0: 词典规则匹配 61实体 |
