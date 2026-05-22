# 双人开发工作流 Skill

> 本 Skill 强制约束本项目的所有代码生成行为。违反任一规则应立即修正。

## 核心原则

1. **先定义后实现**：API 格式 → `api-contract.md` 确认 → 再写代码
2. **一人一域**：A 不直接写 Neo4j Cypher，B 不碰前端和 LLM 调用
3. **每次运行前检查**：生成任何代码后立即自查以下清单

---

## Python 生成约束

```yaml
必须:
  - 所有函数有类型注解 (入参 + 返回值)
  - 命名: 函数 snake_case 动词开头, 类 PascalCase, 常量 UPPER_SNAKE
  - Neo4j session 用 "with driver.session() as session:"
  - 密码/密钥从 os.getenv() 读取
  - 外部调用用 try-except

禁止:
  - 单字母变量名
  - 硬编码密码
  - "import *"
  - session = driver.session() (不关闭)

示例:
  def get_symptoms(limit: int = 100) -> list[dict[str, str]]:
      with driver.session() as session:
          result = session.run("MATCH (s:Symptom) RETURN s.name LIMIT $lim", lim=limit)
          return [{"name": r["s.name"]} for r in result]
```

## Cypher 生成约束

```yaml
必须:
  - 参数化: 用 $param 占位符, 禁止字符串拼接
  - 写入用 MERGE (保证幂等)
  - 全量查询加 LIMIT
  - priority 在 CAUSED_BY 关系边上 (不是 Cause 节点属性)
  - uid 格式: 前缀_设备缩写_序号 (如 S_CONT_01)

禁止:
  - MATCH (n) RETURN n (无 LIMIT)
  - CREATE (除非明确需要幂等外的场景)
  - "MATCH ... WHERE name = '" + user_input + "'" (注入风险)

示例 - 正确:
  MATCH (s:Symptom {name: $name})-[r:CAUSED_BY]->(c:Cause)-[:FIXED_BY]->(st:Step)
  RETURN c.name, r.priority, st.name ORDER BY r.priority LIMIT $limit

示例 - 错误:
  MATCH (s:Symptom {name: '" + kw + "'}) RETURN s
```

## API 生成约束

```yaml
必须:
  - 接口格式严格按 api-contract.md
  - 列表接口返回 [{"id":..., "name":...}]
  - 错误码: 400/404/503
  - CORS 中间件已配置

禁止:
  - 先改代码后补文档
  - 返回格式与契约不一致
```

## Git 约束

```yaml
必须:
  - 分支: feat/xxx 或 fix/xxx
  - 提交信息: "feat: 描述" 或 "fix: 描述"
  - 提交前 git pull --rebase origin dev

禁止:
  - 直交 main/dev
  - 冲突盲合
```

## 知识图谱约束

```yaml
必须:
  - 导入前 Browser 试跑 Cypher
  - 导入后跑质量检查 (孤立/Source缺失/FIXED_BY缺失)
  - 大改前 Dump 备份

质量检查 CQL:
  # 孤立节点
  MATCH (n) WHERE NOT (n)--() RETURN labels(n), count(n)
  # Cause 无 FIXED_BY
  MATCH (c:Cause) WHERE NOT (c)-[:FIXED_BY]->() RETURN c.name
  # 缺 source_page
  MATCH (n) WHERE n.source_page IS NULL RETURN labels(n), count(n)
```

## 自查清单（每次生成代码后必须核对）

- [ ] 类型注解完整
- [ ] 无硬编码密码
- [ ] Cypher 用 `$param` 参数化
- [ ] Neo4j session 用 `with` 管理
- [ ] 有 try-except 处理外部调用
- [ ] API 格式与 api-contract.md 一致
- [ ] 变量命名规范 (snake_case/PascalCase)
- [ ] 写入操作用 MERGE
- [ ] 查询有 LIMIT
