
# Agentic AI: 运行时Java API doc 反射

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