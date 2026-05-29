

# Agentic AI: 运行时Java API doc explorer CLI

jakarta.json-api在 Java 17+ 中是标准 API，无需额外下载运行时库。



## Supported Languages & Mechanisms

This skill uses a "bring your own docs" model, where documentation is generated via standard tooling and then queried by the agent.



#### How `api-doc.json`is Generated (Java)

The `api-doc.json`file is the cornerstone of the Java exploration capability. It is generated directly from your Java source code comments using a custom Doclet.

1. **Doclet Implementation**: A special Java class (`ApiDoclet.java`) implements the `Doclet`interface. This class is compiled into a `.class`file.
2. **Execution**: The standard `javadoc`tool is invoked with a specific configuration to use this custom Doclet.
3. **Output**: The Doclet parses the source code and writes a single `api-doc.json`file containing a structured representation of your API.

**Key Generation Features:**

- Extracts class-level and method-level Javadoc comments.
- Captures method signatures, including parameter names and types.
- Preserves `@param`and `@return`descriptions.
- Operates entirely within the Java standard library (`javax.json`).

For complete details, setup instructions, and usage examples, please refer to the dedicated document:

## Javadoc的doclet机制
A `doclet` is a program written in Java that uses the doclet API to specify the content and format of the output of the Javadoc tool. Java 9


## 流程
```
Java 源码
   ↓
javadoc + Doclet
   ↓
api-doc.json   ← 核心资产
   ↓
JavaApiExplorer（CLI）
   ↓
终端输出 API 信息
```

`java JavaApiExplorer com.example.UserService.createUser`

## 三种运行模式

### 模式1: JSON 文档模式（默认）
当 classpath 中包含 `api-doc.json` 时自动使用：
```bash
java -cp ".:example/target/classes" JavaApiExplorer com.example.service.UserService
java -cp ".:example/target/classes" JavaApiExplorer com.example.service.UserService.findUser
```

### 模式2: 反射模式（无需 JSON 文档）
使用 `--reflect` 强制使用 Java 反射，直接从类文件获取信息：
```bash
java -cp ".:example/target/classes" JavaApiExplorer --reflect com.example.service.UserService
java -cp ".:example/target/classes" JavaApiExplorer --reflect com.example.service.UserService.findUser
```

当 classpath 中没有 `api-doc.json` 时，也会自动回退到反射模式。

### 模式3: ClassGraph 包扫描模式
当 ClassGraph JAR 在 classpath 上时，支持包级别的类扫描（含类类型标注）：
```bash
java -cp ".:lib/classgraph-4.8.184.jar" JavaApiExplorer --reflect io.github.classgraph
```

安装 ClassGraph：
```bash
mvn dependency:get -Dartifact=io.github.classgraph:classgraph:4.8.184:jar
cp ~/.m2/repository/io/github/classgraph/classgraph/4.8.184/classgraph-4.8.184.jar lib/
```

### 模式4: JAR 探索模式（--jar）
通过 `--jar` 直接解析 JAR 文件内容，列出包和类，无需 ClassGraph：
```bash
# 查看 JAR 概览（顶层包和类计数）
java -cp . JavaApiExplorer --jar lib/classgraph-4.8.184.jar

# 查看指定包下的类
java -cp . JavaApiExplorer --jar lib/classgraph-4.8.184.jar io.github.classgraph

# 逐层导航子包
java -cp . JavaApiExplorer --jar lib/classgraph-4.8.184.jar io
```

**包探索优先级**：ClassGraph > jar tf 解析（ClassGraph 可区分 interface/enum/abstract class，jar tf 仅列出类名）

### 自动回退
- 若 `api-doc.json` 不在 classpath 中，自动回退到反射模式
- 包查询时，若 ClassGraph 不可用，自动使用 jar tf 解析 classpath 上的 JAR 和目录

## JDK Module 探索（--module-path）

在 Java 9+ 模块系统中，JDK 的类打包在模块化的 JMOD 文件中，不能通过普通 `-cp` 加载。
**必须使用 `--module-path` 指向 JDK 的 `jmods` 目录**，并通过 `--add-modules` 添加目标模块。

### Ubuntu/Linux 下探索 JDK 模块

```bash
# 定位 JDK jmods 目录
JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(which java)")")")"

# 探索 java.base 模块中的类（如 java.lang.String）
java -cp "." \
  --module-path "$JAVA_HOME/jmods" \
  --add-modules java.base \
  JavaApiExplorer --reflect java.lang.String

# 探索 java.sql 模块
java -cp "." \
  --module-path "$JAVA_HOME/jmods" \
  --add-modules java.sql \
  JavaApiExplorer --reflect java.sql.Connection

# 探索 java.net.http 模块（HttpClient 等）
java -cp "." \
  --module-path "$JAVA_HOME/jmods" \
  --add-modules java.net.http \
  JavaApiExplorer --reflect java.net.http.HttpClient
```

**要点：**
- `--module-path` 指向 `$JAVA_HOME/jmods`，这是 JDK 模块化 JAR 的存放位置
- `--add-modules <module>` 是必需的，否则模块不会被解析，类无法加载
- 常用模块：`java.base`（核心类）、`java.sql`、`java.net.http`、`java.nio.file` 等
- 与 ClassGraph 结合使用时，ClassGraph 也可以扫描模块路径中的包

### macOS 下探索 JDK 模块

```bash
JAVA_HOME="$(/usr/libexec/java_home)"
java -cp "." --module-path "$JAVA_HOME/jmods" --add-modules java.base \
  JavaApiExplorer --reflect java.lang.String
```

## Javadoc HTML 探索可行性分析

### 现状
当前 JavaApiExplorer 支持三种信息源：JSON 文档（Doclet 生成）、Java 反射、ClassGraph 包扫描。
Javadoc HTML（`index.html` + 帧/搜索式 API 文档）是另一种潜在信息源。

### 安装 Javadoc HTML
- **Ubuntu**: `sudo apt install openjdk-<version>-doc`（如 `openjdk-21-doc`），文档安装在 `/usr/share/doc/openjdk-<version>-doc/api/`
- **手动下载**: 从 https://docs.oracle.com/en/java/javase/下载对应版本的 API 文档 ZIP
- **Maven 依赖**: `mvn dependency:resolve -Dclassifier=javadoc` 可下载依赖库的 javadoc JAR

### 探索可行性总结

| 方案 | 可行性 | 优势 | 劣势 |
|------|--------|------|------|
| 解析 Javadoc HTML | ⚠️ 可行但复杂 | 无需源码/编译，信息最完整（含注释） | HTML 结构复杂且版本间不稳定，解析成本高 |
| 使用 Doclet 生成 JSON | ✅ 已实现 | 结构化输出，信息完整 | 需要源码和 javadoc 工具 |
| Java 反射 | ✅ 已实现 | 无需任何文档，运行时可用 | 无注释，仅公开 API |
| ClassGraph 扫描 | ✅ 已实现 | 支持包级别发现 | 无注释，需额外 JAR |

**结论**：Javadoc HTML 解析在技术上可行（可使用 jsoup 等库解析），但性价比不高。推荐的做法是：
1. 有源码时：使用 Doclet 生成 `api-doc.json`（当前已实现）
2. 无源码有 JAR 时：使用反射 + ClassGraph（当前已实现）
3. 仅需查看文档时：直接让 Agent 读取 Javadoc HTML 页面本身，而非结构化解析

## javap 与 Java 反射对比

`javap` 是 JDK 自带的反汇编工具，可以查看 class 文件的签名信息。与 JavaApiExplorer 的反射模式效果相近但有差异：

| 特性 | `javap -public` | JavaApiExplorer 反射模式 |
|------|----------------|------------------------|
| 输出格式 | 纯文本，JDK 标准格式 | 结构化，带 emoji 图标和分组 |
| 公共方法签名 | ✅ | ✅ |
| 返回类型 | ✅ | ✅ |
| 参数名 | ✅（编译时 `-parameters`） | ✅（运行时自动获取） |
| 泛型签名 | ❌（显示擦除类型） | ✅（`getGenericReturnType` 保留泛型） |
| 构造函数 | ✅ | ✅ |
| 字段 | ✅ | ✅（仅 public） |
| enum 值 | ✅ | ✅ |
| 继承关系 | `-verbose` 时可见 | ✅（直接显示 extends/implements） |
| 异常声明 | ✅ | ✅ |
| 注解 | `-verbose` 时可见 | ❌（当前未实现） |
| 私有成员 | `-private` 时可见 | ❌（仅 public） |
| 无需类在 classpath | ✅（直接读 .class） | ❌（需要 Class.forName 加载） |
| 包级别探索 | ❌ | ✅（ClassGraph/jar tf） |
| 方法级别查询 | ❌（只能查整个类） | ✅（精确查询单个方法） |

**总结**：
- `javap` 更适合快速查看类签名，不需要类在运行时 classpath 上（可直接读 `.class` 文件）
- JavaApiExplorer 反射模式提供更结构化的输出、泛型保留、包级探索和精确方法查询
- 两者信息源相同（都是 class 文件元数据），但反射模式的运行时信息更丰富