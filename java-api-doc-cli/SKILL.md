```yaml
- name: Java API Doc Explorer CLI
- description: Query Java API documentation via JSON docs, runtime reflection, or JAR exploration. Supports package, class, and method level queries.
- version: "0.2.0"
```

## When to Use

- Explore a Java SDK/library you were not trained on
- Look up exact method signatures, parameters, return types, or Javadoc comments
- Discover what classes a package exports (via ClassGraph or `--jar`)
- Inspect JDK module APIs (via `--module-path`)
- Explore a JAR file's packages and classes (via `--jar`)

---

## CLI Usage

```bash
java -cp ".:<classpath>" JavaApiExplorer [--reflect] [--jar <path>] <query>
```

### Options

| Option | Description |
|--------|-------------|
| `--reflect`, `-r` | Force reflection mode (skip JSON doc lookup) |
| `--jar <path>`, `-j` | Explore a JAR file's packages/classes |
| `--help`, `-h` | Show help message |

### Auto-Fallback

If `api-doc.json` is not found on classpath, auto-falls back to reflection mode.

---

## Query Examples

### JSON Doc Mode (default, requires api-doc.json on classpath)

```bash
# Class level
java -cp ".:target/classes" JavaApiExplorer com.example.service.UserService

# Method level
java -cp ".:target/classes" JavaApiExplorer com.example.service.UserService.findUser

# Package level
java -cp ".:target/classes" JavaApiExplorer com.example.service
```

### Reflection Mode (--reflect)

```bash
# Class query
java -cp ".:target/classes" JavaApiExplorer --reflect com.example.service.UserService

# Method query
java -cp ".:target/classes" JavaApiExplorer --reflect com.example.service.UserService.findUser

# Enum query
java -cp ".:target/classes" JavaApiExplorer --reflect com.example.product.ProductCategory
```

### JAR Exploration Mode (--jar)

```bash
# Overview of a JAR
java -cp . JavaApiExplorer --jar lib/xxx.jar

# Specific package in a JAR
java -cp . JavaApiExplorer --jar lib/xxx.jar io.github.classgraph

# Sub-package navigation
java -cp . JavaApiExplorer --jar lib/xxx.jar io
```

### JDK Module Exploration (Linux)

```bash
JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(which java)")")")"
java -cp "." --module-path "$JAVA_HOME/jmods" --add-modules java.base \
  JavaApiExplorer --reflect java.lang.String
```

### Package Exploration (ClassGraph or jar tf)

```bash
# With ClassGraph (shows class types: interface/enum/abstract class)
java -cp ".:lib/classgraph-4.8.184.jar" JavaApiExplorer --reflect io.github.classgraph

# Without ClassGraph (jar tf fallback — class names only)
java -cp ".:target/classes" JavaApiExplorer --reflect com.example.service
```

---

## Prerequisite: Generate Documentation

See [Readme.md](Readme.md) for how to generate `api-doc.json` using custom Doclet + javadoc.

---

## Query Levels

| Level | Example | Returns |
|-------|---------|---------|
| Package | `com.example.service` | All classes in the package |
| Class | `com.example.service.UserService` | Doc + all member signatures |
| Method | `com.example.service.UserService.findUser` | Full signature, params, return type, doc |

If a specific query fails, **broaden it** (drop the method name) to discover what's available.
