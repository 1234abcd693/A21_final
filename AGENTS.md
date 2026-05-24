# AGENTS.md - 船舶故障诊断系统

## 项目概要

船舶装备故障诊断智能问答系统。技术栈：Neo4j 知识图谱 + FastAPI + LangChain RAG + llama.cpp + Vue3 + Electron。

## 必读文件

生成任何代码前，先读取以下文件了解约束：
- `开发约束规范.md` — 编码/API/Git/测试/质量规范
- `知识图谱设计文档.md` — 本体结构、实体关系、溯源属性
- `SKILL.md` — 代码生成自查清单

## 知识图谱核心结构（v4.0）

7 节点：Symptom / Cause / Step / Equipment / SparePart / Tool / Precaution
7 关系：CAUSED_BY(priority在关系边) / FIXED_BY / NEXT_STEP / BELONGS_TO / USES_SPAREPART / REQUIRES_TOOL / HAS_PRECAUTION

查询路径：Symptom → CAUSED_BY → Cause → FIXED_BY → Step₁ → NEXT_STEP → Step₂

## 编码硬性规则

1. Python：类型注解、snake_case、`with driver.session()`、`os.getenv()` 读密码
2. Cypher：`$param` 参数化、MERGE 幂等、LIMIT 必须、禁止字符串拼接
3. API：先改 api-contract.md → 双方确认 → 再改代码
4. Git：feat/xxx 分支、`feat: 描述` 提交信息
