import java.io.InputStream;
import java.lang.reflect.*;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

/**
 * JavaApiExplorer（支持 JSON 文档模式 + 反射模式）
 *
 * 模式1 — JSON 文档模式（默认）：
 *   java -cp ".:example/target/classes" JavaApiExplorer com.example.service.UserService
 *   当 classpath 中包含 api-doc.json 时自动使用。
 *
 * 模式2 — 反射模式（无需 JSON 文档）：
 *   java -cp ".:example/target/classes" JavaApiExplorer --reflect com.example.service.UserService
 *   java -cp ".:example/target/classes" JavaApiExplorer --reflect com.example.service.UserService.findUser
 *   直接通过 Java 反射获取类/方法信息。
 *
 * 模式3 — ClassGraph 包扫描模式（需要 ClassGraph 在 classpath 上）：
 *   java -cp ".:example/target/classes:lib/classgraph.jar" JavaApiExplorer --reflect com.example.service
 *   当 ClassGraph 可用时，支持包级别的类扫描。
 *
 * 通用用法：
 *   JavaApiExplorer [--reflect] <query>
 *   <query> 格式:
 *     package                  → 包级查询（列出包下所有类，需 JSON 文档或 ClassGraph）
 *     package.ClassName        → 类级查询
 *     package.ClassName.method → 方法级查询
 */
public class JavaApiExplorer {

    private static boolean reflectMode = false;

    public static void main(String[] args) {
        // Parse flags
        List<String> positional = new ArrayList<>();
        for (String arg : args) {
            if (arg.equals("--reflect") || arg.equals("-r")) {
                reflectMode = true;
            } else if (arg.equals("--help") || arg.equals("-h")) {
                printUsage();
                return;
            } else {
                positional.add(arg);
            }
        }

        if (positional.isEmpty()) {
            printUsage();
            return;
        }

        String input = positional.get(0);

        // Try JSON doc mode first (unless --reflect is forced)
        if (!reflectMode) {
            Map<String, Object> root = loadJson();
            if (root != null) {
                exploreFromJson(root, input);
                return;
            }
        }

        // Reflection mode
        exploreFromReflection(input);
    }

    private static void printUsage() {
        System.out.println("Usage:");
        System.out.println("  JavaApiExplorer [--reflect] <query>");
        System.out.println();
        System.out.println("Query formats:");
        System.out.println("  package                       List classes in package (JSON doc or ClassGraph)");
        System.out.println("  package.ClassName             Show class info");
        System.out.println("  package.ClassName.method      Show method details");
        System.out.println();
        System.out.println("Options:");
        System.out.println("  --reflect, -r    Force reflection mode (skip JSON doc lookup)");
        System.out.println("  --help, -h       Show this help message");
        System.out.println();
        System.out.println("Modes:");
        System.out.println("  1. JSON doc mode (default): uses api-doc.json from classpath");
        System.out.println("  2. Reflection mode: uses Java reflection to inspect classes");
        System.out.println("  3. ClassGraph mode: if ClassGraph is on classpath, supports package scanning");
    }

    // ==================== JSON 文档模式 ====================

    @SuppressWarnings("unchecked")
    private static void exploreFromJson(Map<String, Object> root, String input) {
        // First try to match the full input as a class name in the JSON
        List<Map<String, Object>> classes = getArray(root, "classes");
        if (classes != null) {
            // Try exact match against className in JSON
            for (Map<String, Object> cls : classes) {
                String cn = str(cls, "className");
                if (cn.equals(input)) {
                    // It's a class-level query
                    printJsonClass(cls, cn);
                    return;
                }
                // Check if input is className.methodName
                if (input.startsWith(cn + ".")) {
                    String methodName = input.substring(cn.length() + 1);
                    printJsonMethod(cls, methodName);
                    return;
                }
            }
        }

        // Fallback: split by "." and use the old logic for simple names
        String[] parts = input.split("\\.");

        if (parts.length == 1) {
            explorePackage(root, parts[0]);
        } else if (parts.length == 2) {
            exploreClass(root, parts[0] + "." + parts[1]);
        } else if (parts.length >= 3) {
            exploreMethod(root, parts[0] + "." + parts[1], parts[2]);
        }
    }

    private static void printJsonClass(Map<String, Object> cls, String className) {
        System.out.println("Class: " + className);
        System.out.println("JavaDoc: " + str(cls, "comment"));

        System.out.println("\nMethods:");
        List<Map<String, Object>> methods = getArray(cls, "methods");
        if (methods == null) return;

        for (Map<String, Object> method : methods) {
            System.out.println("  " + str(method, "signature"));
            System.out.println("    JavaDoc: " + str(method, "comment"));

            List<Map<String, Object>> params = getArray(method, "parameters");
            if (params != null) {
                for (Map<String, Object> param : params) {
                    System.out.println("      param " +
                            str(param, "name") +
                            " (" + str(param, "type") + "): " +
                            str(param, "comment", ""));
                }
            }
        }
    }

    private static void printJsonMethod(Map<String, Object> cls, String methodName) {
        List<Map<String, Object>> methods = getArray(cls, "methods");
        if (methods == null) return;

        for (Map<String, Object> method : methods) {
            if (!str(method, "name").equals(methodName)) continue;

            System.out.println("Method Signature:");
            System.out.println("  " + str(method, "signature"));
            System.out.println("JavaDoc: " + str(method, "comment"));

            Map<String, Object> ret = getObject(method, "returns");
            if (ret != null) {
                System.out.println("Returns: " +
                        str(ret, "type") + " - " +
                        str(ret, "comment", ""));
            }

            List<Map<String, Object>> params = getArray(method, "parameters");
            if (params != null) {
                System.out.println("Parameters:");
                for (Map<String, Object> param : params) {
                    System.out.println("  " +
                            str(param, "name") +
                            " (" + str(param, "type") + "): " +
                            str(param, "comment", ""));
                }
            }
        }
    }

    /**
     * 加载 Doclet 生成的 JSON（纯 Java 手动解析）
     */
    @SuppressWarnings("unchecked")
    private static Map<String, Object> loadJson() {
        try (InputStream is =
                     JavaApiExplorer.class.getResourceAsStream("/api-doc.json")) {
            if (is == null) {
                return null;
            }
            byte[] bytes = is.readAllBytes();
            String json = new String(bytes, StandardCharsets.UTF_8);
            pos = 0;
            return parseObject(json);
        } catch (Exception e) {
            return null;
        }
    }

    // ==================== 反射模式 ====================

    private static void exploreFromReflection(String input) {
        String[] parts = input.split("\\.");

        // Try to load as a class first
        // Strategy: try progressively shorter prefixes as class names
        // e.g., "com.example.service.UserService.findUser"
        //   → try com.example.service.UserService.findUser (class)
        //   → try com.example.service.UserService (class), findUser (method)

        // Try the full input as a class name
        try {
            Class<?> cls = Class.forName(input);
            printClassInfo(cls);
            return;
        } catch (ClassNotFoundException ignored) {}

        // Try progressively shorter prefixes
        for (int i = parts.length - 1; i >= 1; i--) {
            String classPart = String.join(".", Arrays.copyOfRange(parts, 0, i));
            String[] memberParts = Arrays.copyOfRange(parts, i, parts.length);

            try {
                Class<?> cls = Class.forName(classPart);
                if (memberParts.length == 0) {
                    printClassInfo(cls);
                } else if (memberParts.length == 1) {
                    // Could be inner class or method
                    String memberName = memberParts[0];

                    // Try inner class first
                    try {
                        Class<?> innerCls = Class.forName(classPart + "$" + memberName);
                        printClassInfo(innerCls);
                        return;
                    } catch (ClassNotFoundException ignored) {}

                    // Try method
                    printMethodInfo(cls, memberName);
                } else if (memberParts.length == 2) {
                    // innerClass.method
                    try {
                        Class<?> innerCls = Class.forName(classPart + "$" + memberParts[0]);
                        printMethodInfo(innerCls, memberParts[1]);
                    } catch (ClassNotFoundException e) {
                        System.out.println("❌ Not found: " + input);
                    }
                }
                return;
            } catch (ClassNotFoundException ignored) {}
        }

        // If all class lookups fail, try as a package (with ClassGraph)
        explorePackageFromReflection(input);
    }

    /**
     * Print class information via reflection.
     */
    private static void printClassInfo(Class<?> cls) {
        String qualifiedName = cls.getName();

        System.out.println("\n✅ Found: " + qualifiedName);
        System.out.println("=".repeat(60));
        System.out.println("📌 Name:       " + cls.getSimpleName());
        System.out.println("🏷️  Kind:       " + getClassKind(cls));
        System.out.println("📦 Package:    " + cls.getPackage().getName());

        if (cls.getSuperclass() != null && cls.getSuperclass() != Object.class) {
            System.out.println("🔗 Extends:    " + cls.getSuperclass().getName());
        }

        // Interfaces
        Class<?>[] interfaces = cls.getInterfaces();
        if (interfaces.length > 0) {
            System.out.println("🔗 Implements: " + Arrays.stream(interfaces)
                    .map(Class::getName).reduce((a, b) -> a + ", " + b).orElse(""));
        }

        // Constructors
        Constructor<?>[] constructors = cls.getConstructors();
        if (constructors.length > 0) {
            System.out.println("\n📦 Constructors (" + constructors.length + "):");
            for (Constructor<?> c : constructors) {
                System.out.println("   ▸ " + formatExecutable(c));
            }
        }

        // Public methods
        List<Method> publicMethods = Arrays.stream(cls.getDeclaredMethods())
                .filter(m -> Modifier.isPublic(m.getModifiers()))
                .toList();
        if (!publicMethods.isEmpty()) {
            System.out.println("\n📦 Methods (" + publicMethods.size() + "):");
            for (Method m : publicMethods) {
                String staticMark = Modifier.isStatic(m.getModifiers()) ? "static " : "";
                System.out.println("   ▸ " + staticMark + formatExecutable(m));
            }
        }

        // Public fields
        List<Field> publicFields = Arrays.stream(cls.getDeclaredFields())
                .filter(f -> Modifier.isPublic(f.getModifiers()))
                .toList();
        if (!publicFields.isEmpty()) {
            System.out.println("\n📦 Fields (" + publicFields.size() + "):");
            for (Field f : publicFields) {
                String staticMark = Modifier.isStatic(f.getModifiers()) ? "static " : "";
                System.out.println("   ▸ " + staticMark + f.getType().getSimpleName() + " " + f.getName());
            }
        }

        // Enum constants
        if (cls.isEnum()) {
            Object[] enumConstants = cls.getEnumConstants();
            if (enumConstants != null && enumConstants.length > 0) {
                System.out.println("\n📦 Enum Values (" + enumConstants.length + "):");
                for (Object ec : enumConstants) {
                    System.out.println("   ▸ " + ((Enum<?>) ec).name());
                }
            }
        }

        System.out.println("=".repeat(60));
    }

    /**
     * Print method information via reflection.
     */
    private static void printMethodInfo(Class<?> cls, String methodName) {
        List<Method> matching = Arrays.stream(cls.getDeclaredMethods())
                .filter(m -> Modifier.isPublic(m.getModifiers()))
                .filter(m -> m.getName().equals(methodName))
                .toList();

        if (matching.isEmpty()) {
            System.out.println("❌ Method not found: " + cls.getName() + "." + methodName);
            System.out.println("   Available methods:");
            Arrays.stream(cls.getDeclaredMethods())
                    .filter(m -> Modifier.isPublic(m.getModifiers()))
                    .forEach(m -> System.out.println("     - " + m.getName()));
            return;
        }

        String qualifiedName = cls.getName() + "." + methodName;

        for (Method m : matching) {
            System.out.println("\n✅ Found: " + qualifiedName);
            System.out.println("=".repeat(60));
            System.out.println("📌 Name:       " + m.getName());
            System.out.println("🏷️  Kind:       " + (Modifier.isStatic(m.getModifiers()) ? "static method" : "method"));

            System.out.println("\n🔧 Signature:  " + formatExecutable(m));

            // Parameters
            Parameter[] params = m.getParameters();
            if (params.length > 0) {
                System.out.println("   Parameters:");
                for (Parameter p : params) {
                    String pType = p.getParameterizedType() != null
                            ? p.getParameterizedType().getTypeName()
                            : p.getType().getName();
                    System.out.println("     - " + p.getName() + ": " + simplifyType(pType));
                }
            }

            // Return type
            System.out.println("   ↩️  Returns:    " + simplifyType(m.getGenericReturnType().getTypeName()));

            // Exceptions
            Class<?>[] exceptions = m.getExceptionTypes();
            if (exceptions.length > 0) {
                System.out.println("   ⚠️  Throws:     " + Arrays.stream(exceptions)
                        .map(Class::getSimpleName).reduce((a, b) -> a + ", " + b).orElse(""));
            }

            System.out.println("=".repeat(60));
        }
    }

    /**
     * Explore a package using ClassGraph (if available) or list from classpath.
     */
    private static void explorePackageFromReflection(String packageName) {
        // Try ClassGraph first
        try {
            Class<?> classGraphClass = Class.forName("io.github.classgraph.ClassGraph");
            explorePackageWithClassGraph(packageName);
            return;
        } catch (ClassNotFoundException ignored) {
            // ClassGraph not available
        } catch (Exception e) {
            System.out.println("⚠️  ClassGraph scan failed: " + e.getMessage());
        }

        // Fallback: try to find classes from classpath using simple heuristics
        System.out.println("\n⚠️  Package exploration requires ClassGraph on the classpath.");
        System.out.println("   Current mode: class-level and method-level reflection only.");
        System.out.println();
        System.out.println("   To enable package scanning, add ClassGraph:");
        System.out.println("   java -cp \".:<your-jar>:lib/classgraph-4.8.jar\" JavaApiExplorer --reflect " + packageName);
        System.out.println();
        System.out.println("   Alternatively, query a specific class:");
        System.out.println("   JavaApiExplorer --reflect " + packageName + ".<ClassName>");
    }

    /**
     * Use ClassGraph to scan a package and list its classes.
     */
    private static void explorePackageWithClassGraph(String packageName) {
        try {
            // Use ClassGraph via reflection to avoid compile-time dependency
            Class<?> classGraphClass = Class.forName("io.github.classgraph.ClassGraph");
            Class<?> scanResultClass = Class.forName("io.github.classgraph.ScanResult");
            Class<?> classInfoClass = Class.forName("io.github.classgraph.ClassInfo");

            // new ClassGraph().enableClassInfo().acceptPackages(pkg).scan()
            Object classGraph = classGraphClass.getDeclaredConstructor().newInstance();
            classGraphClass.getMethod("enableClassInfo").invoke(classGraph);
            classGraphClass.getMethod("acceptPackages", String.class).invoke(classGraph, packageName);
            Object scanResult = classGraphClass.getMethod("scan").invoke(classGraph);

            // scanResult.getAllClasses()
            @SuppressWarnings("unchecked")
            Iterable<Object> allClasses = (Iterable<Object>) scanResultClass.getMethod("getAllClasses").invoke(scanResult);

            List<String> classNames = new ArrayList<>();
            for (Object classInfo : allClasses) {
                String name = (String) classInfoClass.getMethod("getName").invoke(classInfo);
                String simpleName = (String) classInfoClass.getMethod("getSimpleName").invoke(classInfo);
                boolean isInterface = (boolean) classInfoClass.getMethod("isInterface").invoke(classInfo);
                boolean isEnum = (boolean) classInfoClass.getMethod("isEnum").invoke(classInfo);
                boolean isAbstract = (boolean) classInfoClass.getMethod("isAbstract").invoke(classInfo);

                String kind = isEnum ? "enum" : isInterface ? "interface" : isAbstract ? "abstract class" : "class";
                classNames.add(simpleName + " (" + kind + ") — " + name);
            }

            scanResultClass.getMethod("close").invoke(scanResult);

            if (classNames.isEmpty()) {
                System.out.println("\n❌ No classes found in package: " + packageName);
                return;
            }

            System.out.println("\n✅ Found: " + packageName);
            System.out.println("=".repeat(60));
            System.out.println("🏷️  Kind:       package");
            System.out.println("📊 Class Count: " + classNames.size());
            System.out.println("\n📦 Children (" + classNames.size() + "):");
            for (String cn : classNames) {
                System.out.println("   ▸ " + cn);
            }
            System.out.println("=".repeat(60));

        } catch (ClassNotFoundException e) {
            System.out.println("❌ ClassGraph not found on classpath. Package scanning unavailable.");
            System.out.println("   Download: https://github.com/classgraph/classgraph");
        } catch (Exception e) {
            System.out.println("❌ ClassGraph scan failed: " + e.getMessage());
        }
    }

    // ==================== 辅助方法 ====================

    private static String getClassKind(Class<?> cls) {
        if (cls.isEnum()) return "enum";
        if (cls.isInterface()) return "interface";
        if (cls.isAnnotation()) return "annotation";
        if (Modifier.isAbstract(cls.getModifiers())) return "abstract class";
        if (cls.isRecord()) return "record";
        return "class";
    }

    private static String formatExecutable(Executable exec) {
        StringBuilder sb = new StringBuilder();
        sb.append(exec.getName());
        sb.append("(");

        Parameter[] params = exec.getParameters();
        for (int i = 0; i < params.length; i++) {
            if (i > 0) sb.append(", ");
            String pType = params[i].getParameterizedType() != null
                    ? params[i].getParameterizedType().getTypeName()
                    : params[i].getType().getName();
            sb.append(simplifyType(pType)).append(" ").append(params[i].getName());
        }

        sb.append(")");

        if (exec instanceof Method) {
            Method m = (Method) exec;
            sb.append(" → ").append(simplifyType(m.getGenericReturnType().getTypeName()));
        }

        return sb.toString();
    }

    /**
     * Simplify type names: remove "java.lang.", shorten common types.
     */
    private static String simplifyType(String typeName) {
        if (typeName == null) return "void";
        return typeName
                .replace("java.lang.", "")
                .replace("java.util.", "")
                .replace("java.io.", "")
                .replace("java.nio.", "")
                .replace("java.time.", "");
    }

    // ==================== JSON 业务逻辑（文档模式） ====================

    @SuppressWarnings("unchecked")
    private static List<Map<String, Object>> getArray(Map<String, Object> obj, String key) {
        Object val = obj.get(key);
        return val == null ? null : (List<Map<String, Object>>) val;
    }

    private static String str(Map<String, Object> obj, String key) {
        Object v = obj.get(key);
        return v == null ? "" : v.toString();
    }

    private static String str(Map<String, Object> obj, String key, String fallback) {
        Object v = obj.get(key);
        return v == null ? fallback : v.toString();
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> getObject(Map<String, Object> obj, String key) {
        return (Map<String, Object>) obj.get(key);
    }

    private static void explorePackage(Map<String, Object> root, String pkg) {
        System.out.println("Package: " + pkg);
        System.out.println("Classes:");

        List<Map<String, Object>> classes = getArray(root, "classes");
        if (classes == null) return;

        for (Map<String, Object> cls : classes) {
            String className = str(cls, "className");
            if (className.startsWith(pkg)) {
                System.out.println("  " + className);
            }
        }
    }

    private static void exploreClass(Map<String, Object> root, String className) {
        List<Map<String, Object>> classes = getArray(root, "classes");
        if (classes == null) return;

        boolean found = false;
        for (Map<String, Object> cls : classes) {
            String cn = str(cls, "className");
            // Match exact or simple name
            String simpleName = className.contains(".") ?
                    className.substring(className.lastIndexOf('.') + 1) : className;
            if (!cn.equals(className) && !cn.equals(simpleName)) continue;
            found = true;
            printJsonClass(cls, cn);
        }

        if (!found) {
            // Fallback to reflection
            exploreFromReflection(className);
        }
    }

    private static void exploreMethod(Map<String, Object> root,
                                      String className,
                                      String methodName) {
        List<Map<String, Object>> classes = getArray(root, "classes");
        if (classes == null) { exploreFromReflection(className + "." + methodName); return; }

        boolean found = false;
        for (Map<String, Object> cls : classes) {
            String cn = str(cls, "className");
            String simpleName = className.contains(".") ?
                    className.substring(className.lastIndexOf('.') + 1) : className;
            if (!cn.equals(className) && !cn.equals(simpleName)) continue;
            found = true;
            printJsonMethod(cls, methodName);
        }

        if (!found) {
            exploreFromReflection(className + "." + methodName);
        }
    }

    // ==================== 简易 JSON 解析器 ====================

    private static int pos;

    private static Map<String, Object> parseObject(String s) {
        skipSpace(s);
        if (s.charAt(pos) != '{') throw new RuntimeException("Expected {");
        pos++;
        Map<String, Object> map = new LinkedHashMap<>();
        skipSpace(s);
        if (s.charAt(pos) == '}') { pos++; return map; }
        while (true) {
            skipSpace(s);
            String key = parseString(s);
            skipSpace(s);
            expectChar(s, ':');
            skipSpace(s);
            Object val = parseValue(s);
            map.put(key, val);
            skipSpace(s);
            if (s.charAt(pos) == '}') { pos++; break; }
            expectChar(s, ',');
        }
        return map;
    }

    private static List<Object> parseArray(String s) {
        pos++;
        List<Object> list = new ArrayList<>();
        skipSpace(s);
        if (s.charAt(pos) == ']') { pos++; return list; }
        while (true) {
            skipSpace(s);
            list.add(parseValue(s));
            skipSpace(s);
            if (s.charAt(pos) == ']') { pos++; break; }
            expectChar(s, ',');
        }
        return list;
    }

    private static Object parseValue(String s) {
        skipSpace(s);
        char c = s.charAt(pos);
        if (c == '"') return parseString(s);
        if (c == '{') return parseObject(s);
        if (c == '[') return parseArray(s);
        if (c == 't' || c == 'f') return parseBool(s);
        if (c == 'n') return parseNull(s);
        if (c == '-' || Character.isDigit(c)) return parseNumber(s);
        throw new RuntimeException("Unexpected char: " + c + " at pos " + pos);
    }

    private static String parseString(String s) {
        expectChar(s, '"');
        StringBuilder sb = new StringBuilder();
        while (s.charAt(pos) != '"') {
            char ch = s.charAt(pos++);
            if (ch == '\\') {
                char esc = s.charAt(pos++);
                switch (esc) {
                    case '"': sb.append('"'); break;
                    case '\\': sb.append('\\'); break;
                    case '/': sb.append('/'); break;
                    case 'n': sb.append('\n'); break;
                    case 'r': sb.append('\r'); break;
                    case 't': sb.append('\t'); break;
                    default: sb.append(esc); break;
                }
            } else {
                sb.append(ch);
            }
        }
        pos++;
        return sb.toString();
    }

    private static String parseNumber(String s) {
        int start = pos;
        if (s.charAt(pos) == '-') pos++;
        while (pos < s.length() && Character.isDigit(s.charAt(pos))) pos++;
        if (pos < s.length() && s.charAt(pos) == '.') {
            pos++;
            while (pos < s.length() && Character.isDigit(s.charAt(pos))) pos++;
        }
        if (pos < s.length() && (s.charAt(pos) == 'e' || s.charAt(pos) == 'E')) {
            pos++;
            if (pos < s.length() && (s.charAt(pos) == '+' || s.charAt(pos) == '-')) pos++;
            while (pos < s.length() && Character.isDigit(s.charAt(pos))) pos++;
        }
        return s.substring(start, pos);
    }

    private static boolean parseBool(String s) {
        if (s.startsWith("true", pos)) { pos += 4; return true; }
        if (s.startsWith("false", pos)) { pos += 5; return false; }
        throw new RuntimeException("Invalid bool at pos " + pos);
    }

    private static Void parseNull(String s) {
        if (s.startsWith("null", pos)) { pos += 4; return null; }
        throw new RuntimeException("Invalid null at pos " + pos);
    }

    private static void skipSpace(String s) {
        while (pos < s.length() && Character.isWhitespace(s.charAt(pos))) pos++;
    }

    private static void expectChar(String s, char expected) {
        if (s.charAt(pos) != expected)
            throw new RuntimeException("Expected '" + expected + "' but got '" + s.charAt(pos) + "' at pos " + pos);
        pos++;
    }
}
