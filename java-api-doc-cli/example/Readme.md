## Java API Explorer — Example Project

This is a Maven-based example Java project that demonstrates how to generate `api-doc.json` from Javadoc comments using a custom **Doclet** (`ApiDoclet.java`), then explore the resulting JSON with the `JavaApiExplorer` CLI tool.

## Project Structure

```
example/
├── pom.xml                              # Maven build config
├── Readme.md
└── src/main/java/com/example/
    ├── doclet/ApiDoclet.java            # Custom Javadoc Doclet → JSON generator
    ├── model/User.java                  # User entity with Javadoc
    ├── service/UserService.java         # User service (CRUD, singleton)
    ├── logger/LogLevel.java             # Log level enum
    ├── logger/LoggerService.java        # Logger service with LogEntry
    └── product/
        ├── ProductCategory.java         # Product category enum
        ├── Product.java                 # Product entity
        └── ProductService.java          # Product service (CRUD, stock)
```

## How to Build and Generate `api-doc.json`

### Prerequisites

- Java 17+ (tested with JDK 21 and 25)
- Apache Maven 3.6+

### Build

```bash
cd java-api-doc-cli/example
mvn clean package -DskipTests
```

During the `prepare-package` phase, the `exec-maven-plugin` runs `javadoc` with the custom `ApiDoclet`, which generates:

- **`target/classes/api-doc.json`** — the JSON documentation file (also bundled inside the JAR)

### Where to Find the JSON After Build

| Location | Description |
|---|---|
| `target/classes/api-doc.json` | Available immediately after `mvn package` |
| `target/example-1.0.0.jar` (inside: `api-doc.json`) | Bundled in the JAR after `mvn package` |
| `~/.m2/repository/com/example/example/1.0.0/example-1.0.0.jar` (inside: `api-doc.json`) | After `mvn install`, the JAR is in your local Maven repo |

## How to Explore with `JavaApiExplorer`

The `JavaApiExplorer` CLI tool is in the parent `java-api-doc-cli/` directory. It reads `api-doc.json` from the classpath.

### 1. Compile the Explorer

```bash
cd java-api-doc-cli
javac --release 17 -d . JavaApiExplorer.java
```

### 2. Explore the Generated JSON

Use the `-cp` flag to include both the explorer classes and the example's JSON:

```bash
# Explore a package (list classes)
java -cp ".:example/target/classes" JavaApiExplorer com.example

# View a class and its methods
java -cp ".:example/target/classes" JavaApiExplorer UserService

# View a method signature
java -cp ".:example/target/classes" JavaApiExplorer UserService.findUser
```

> **Note**: The tool matches class names without full packages. Use the simple class name (e.g., `UserService`) as the query.

### 3. Explore from the Installed JAR

After `mvn install`:

```bash
# Explore from the local Maven repo
java -cp ".:$HOME/.m2/repository/com/example/example/1.0.0/example-1.0.0.jar" \
  JavaApiExplorer UserService
```

## Alternative: Explore with `javascript-api-explorer`

Since `api-doc.json` is standard JSON, you can also explore it with the JavaScript explorer (which supports `--doc-path`):

```bash
# From the java/example directory:
node ../../javascript-api-doc-cli/javascript-api-explorer.js --doc-path ./target/classes/ UserService
node ../../javascript-api-doc-cli/javascript-api-explorer.js --doc-path ./target/classes/ UserService.findUser
node ../../javascript-api-doc-cli/javascript-api-explorer.js --doc-path ./target/classes/ ProductService.createProduct
```

## How Javadoc + ApiDoclet Works

### Standard Javadoc Tags

Use standard Javadoc tags in your Java source. `ApiDoclet` extracts them into JSON:

```java
/**
 * A brief description.
 *
 * <p>Detailed description with HTML.</p>
 *
 * @param name description of the parameter
 * @return description of the return value
 * @throws IllegalArgumentException when validation fails
 * @see OtherClass
 */
public Result doSomething(String name) { ... }
```

### The `ApiDoclet` JSON Output

```json
{
  "package": "com.example.service",
  "classes": [
    {
      "className": "com.example.service.UserService",
      "kind": "class",
      "comment": "用户服务类...\n\n <p>这是一个单例服务...</p>\n\n @author example\n @see User",
      "methods": [
        {
          "name": "findUser",
          "signature": "User findUser(String id)",
          "comment": "根据 ID 查找用户。\n\n @param id 要查找的用户 ID...\n @return 用户对象...",
          "parameters": [
            { "name": "id", "type": "java.lang.String",
              "comment": "要查找的用户 ID，不能为 null 或空" }
          ],
          "returns": {
            "type": "com.example.model.User",
            "comment": "用户对象，如果未找到则返回 null"
          }
        }
      ]
    }
  ]
}
```

### How It's Wired in Maven

The `pom.xml` uses `exec-maven-plugin` to call the standard `javadoc` CLI tool with a custom doclet:

1. **Compile phase**: `ApiDoclet.java` is compiled as part of the project
2. **prepare-package phase**: `exec-maven-plugin` runs `javadoc -doclet com.example.doclet.ApiDoclet -docletpath target/classes ...`
3. The doclet's `run()` method parses the Javadoc AST and outputs JSON
4. The JSON ends up in `target/classes/api-doc.json`, which gets bundled into the JAR
