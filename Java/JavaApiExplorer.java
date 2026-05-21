import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * JavaApiExplorer（纯 Java 原生 JSON 版，零依赖）
 *
 * 用法：
 *   JavaApiExplorer package
 *   JavaApiExplorer package.class
 *   JavaApiExplorer package.class.method
 */
public class JavaApiExplorer {

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage:");
            System.out.println("  JavaApiExplorer package");
            System.out.println("  JavaApiExplorer package.class");
            System.out.println("  JavaApiExplorer package.class.method");
            return;
        }

        Map<String, Object> root = loadJson();
        if (root == null) {
            System.out.println("Failed to load api-doc.json");
            return;
        }

        String input = args[0];
        String[] parts = input.split("\\.");

        if (parts.length == 1) {
            explorePackage(root, parts[0]);
        } else if (parts.length == 2) {
            exploreClass(root, parts[0] + "." + parts[1]);
        } else if (parts.length >= 3) {
            exploreMethod(root, parts[0] + "." + parts[1], parts[2]);
        } else {
            System.out.println("Invalid argument format.");
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
            e.printStackTrace();
            return null;
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
        pos++; // skip [
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
        pos++; // skip closing "
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

    // ==================== 辅助方法 ====================

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

    // ==================== 业务逻辑 ====================

    /**
     * 列举包下所有类
     */
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

    /**
     * 查看类信息
     */
    private static void exploreClass(Map<String, Object> root, String className) {
        List<Map<String, Object>> classes = getArray(root, "classes");
        if (classes == null) return;

        for (Map<String, Object> cls : classes) {
            String cn = str(cls, "className");
            // 精确匹配 或 输入以 ".简单名" 结尾（兼容 无包名/包名.类名 两种输入）
            String simpleName = className.contains(".") ?
                    className.substring(className.lastIndexOf('.') + 1) : className;
            if (!cn.equals(className) && !cn.equals(simpleName)) continue;

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
    }

    /**
     * 查看方法签名
     */
    private static void exploreMethod(Map<String, Object> root,
                                      String className,
                                      String methodName) {
        List<Map<String, Object>> classes = getArray(root, "classes");
        if (classes == null) return;

        for (Map<String, Object> cls : classes) {
            String cn = str(cls, "className");
            String simpleName = className.contains(".") ?
                    className.substring(className.lastIndexOf('.') + 1) : className;
            if (!cn.equals(className) && !cn.equals(simpleName)) continue;

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
    }
}
