# APOC 插件

## 一句话解释

APOC = Neo4j 的"瑞士军刀"插件，提供了几百个 Neo4j 官方没带的实用功能。

## 全称

**A**wesome **P**rocedures **O**n **C**ypher —— "Cypher 上的超棒过程"。

## 类比

Neo4j 自带的功能 = iPhone 自带的应用（电话、短信、相机）
APOC = App Store 里的第三方应用（修图、扫描、翻译）

官方的 Cypher 只能做基本的增删改查。APOC 扩展了大量工具功能。

## 我们用了 APOC 的什么？

**数据导出** —— 这是我们唯一需要 APOC 的地方。

```cypher
// 把整个数据库导出为一个 .cypher 文件
CALL apoc.export.cypher.all('neo4j_dump.cypher', {format: 'cypher-shell'})
```

没有 APOC 的话，你得手动写脚本遍历每个节点和关系导出。APOC 一行搞定。

## APOC 还提供了什么（我们可能用到的）

| 功能 | Cypher 命令 | 用途 |
|------|------------|------|
| JSON 处理 | `apoc.convert.toJson()` | 把查询结果转 JSON |
| 批量导入 | `apoc.load.json()` | 从 JSON 文件批量导入 |
| 文本处理 | `apoc.text.*` | 正则匹配、分词 |
| 定时任务 | `apoc.periodic.*` | 定时执行 Cypher（我们不用） |
| 图算法 | `apoc.algo.*` | 最短路径、PageRank 等（我们不用） |

## 安装和启用

你已经有了 `apoc-2026.02.3-core.jar` 在 `plugins/` 目录。

还需要在 `conf/neo4j.conf` 里加一行：

```ini
dbms.security.procedures.unrestricted=apoc.*
```

这行的意思是"信任 APOC 的所有过程，允许它们做任何操作"（导出需要写文件权限）。

## 为什么叫这么奇怪的名字？

APOC 这个名字来自电影《黑客帝国》里的角色 Apoc，同时也是 "Awesome Procedures On Cypher" 的缩写。Neo4j 的另一个插件叫 ALGO（图算法），合起来就是 APOC + ALGO = Apocalypse（启示录）——开发团队的恶趣味。
