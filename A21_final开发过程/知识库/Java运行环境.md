# Java 运行环境（JRE vs JDK）

## 一句话解释

Neo4j 是 Java 写的，需要 Java 运行环境才能启动。你开发时电脑上有 JDK 26，但用户的电脑没有——所以必须把 Java 打进程序包里。

## JDK vs JRE

| | JDK | JRE |
|------|-----|-----|
| 全称 | Java Development Kit | Java Runtime Environment |
| 用途 | 写 Java 代码、编译 | 运行 Java 程序 |
| 谁需要 | 程序员 | 普通用户 |
| 大小 | ~300 MB | ~50 MB（精简后） |

Neo4j 只需要 JRE，不需要 JDK。我们要把 JRE 打进程序包。

## 怎么做

```
A21_final/resources/
├── neo4j/                    ← Neo4j 绿色版
│   ├── jre/                  ← 精简 JRE（~50 MB）
│   │   ├── bin/
│   │   │   └── java.exe      ← Neo4j 用这个启动
│   │   └── ...
│   └── ...
```

启动时告诉 Neo4j 用我们自带的 Java：

```batch
# neo4j.bat 里设置
set JAVA_HOME=%~dp0jre
set PATH=%JAVA_HOME%\bin;%PATH%
```

## 精简 JRE

用 `jlink` 命令从 JDK 里裁剪出一个最小的 JRE：

```powershell
# 从你已安装的 JDK 26 生成精简 JRE
jlink --add-modules java.base,java.logging,java.xml,java.management,java.naming,java.sql --output jre
```

只包含 Neo4j 需要的模块，砍掉不需要的（GUI、CORBA 等），从 300MB 精简到 ~50MB。

## 对打包的影响

程序包增加 ~50MB。8GB 内存预算中，JRE 本身只占 ~30MB 运行时内存。
