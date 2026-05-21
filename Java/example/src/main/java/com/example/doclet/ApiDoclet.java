package com.example.doclet;

import jdk.javadoc.doclet.Doclet;
import jdk.javadoc.doclet.DocletEnvironment;
import jdk.javadoc.doclet.Reporter;

import javax.lang.model.element.*;
import javax.lang.model.util.ElementFilter;
import javax.lang.model.type.TypeMirror;
import javax.lang.model.SourceVersion;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.*;

/**
 * ApiDoclet — 自定义 Javadoc Doclet，将 API 文档输出为 JSON 格式。
 *
 * <p>用法：在 pom.xml 中通过 maven-javadoc-plugin 的 doclet/docletPath 配置引用。</p>
 */
public class ApiDoclet implements Doclet {

    private static String outputPath = "api-doc.json";
    private Locale locale;
    private Reporter reporter;

    @Override
    public void init(Locale locale, Reporter reporter) {
        this.locale = locale;
        this.reporter = reporter;
    }

    @Override
    public String getName() {
        return "ApiDoclet";
    }

    @Override
    public Set<Doclet.Option> getSupportedOptions() {
        Set<Doclet.Option> options = new LinkedHashSet<>();
        options.add(new Doclet.Option() {
            @Override public boolean process(String opt, List<String> args) {
                if (args.size() > 0) outputPath = args.get(0);
                return true;
            }
            @Override public int getArgumentCount() { return 1; }
            @Override public String getDescription() { return "Output file path"; }
            @Override public Option.Kind getKind() { return Kind.STANDARD; }
            @Override public List<String> getNames() { return Collections.singletonList("-output"); }
            @Override public String getParameters() { return "<file>"; }
        });
        return options;
    }

    @Override
    public SourceVersion getSupportedSourceVersion() {
        return SourceVersion.latest();
    }

    @Override
    public boolean run(DocletEnvironment env) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");

        // 包名
        Set<? extends Element> specifiedElements = env.getSpecifiedElements();
        String pkgName = "";
        for (Element e : specifiedElements) {
            PackageElement pe = env.getElementUtils().getPackageOf(e);
            if (pe != null && !pe.isUnnamed()) {
                pkgName = pe.getQualifiedName().toString();
                break;
            }
        }
        if (!pkgName.isEmpty()) {
            sb.append("  \"package\": ").append(jsonStr(pkgName)).append(",\n");
        }

        sb.append("  \"classes\": [\n");
        List<TypeElement> allClasses = new ArrayList<>();

        for (Element e : env.getIncludedElements()) {
            if (e.getKind() == ElementKind.CLASS || e.getKind() == ElementKind.INTERFACE ||
                    e.getKind() == ElementKind.ENUM || e.getKind() == ElementKind.RECORD) {
                allClasses.add((TypeElement) e);
            }
        }

        for (int i = 0; i < allClasses.size(); i++) {
            buildClassJson(sb, env, allClasses.get(i));
            if (i < allClasses.size() - 1) sb.append(",");
            sb.append("\n");
        }

        sb.append("  ]\n");
        sb.append("}\n");

        try (OutputStream os = new FileOutputStream(outputPath)) {
            os.write(sb.toString().getBytes("UTF-8"));
            System.out.println("API documentation generated: " + outputPath);
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }

        return true;
    }

    private static void buildClassJson(StringBuilder sb, DocletEnvironment env, TypeElement classElem) {
        String className = classElem.getQualifiedName().toString();
        String comment = getComment(env, classElem);
        String kind = getKindString(classElem.getKind());

        sb.append("    {\n");
        sb.append("      \"className\": ").append(jsonStr(className)).append(",\n");
        sb.append("      \"kind\": ").append(jsonStr(kind)).append(",\n");
        sb.append("      \"comment\": ").append(jsonStr(comment)).append(",\n");
        sb.append("      \"methods\": [\n");

        List<ExecutableElement> methods = ElementFilter.methodsIn(classElem.getEnclosedElements());
        for (int i = 0; i < methods.size(); i++) {
            buildMethodJson(sb, env, methods.get(i));
            if (i < methods.size() - 1) sb.append(",");
            sb.append("\n");
        }

        sb.append("      ]\n");
        sb.append("    }");
    }

    private static void buildMethodJson(StringBuilder sb, DocletEnvironment env, ExecutableElement method) {
        String name = method.getSimpleName().toString();
        String signature = buildSignature(env, method);
        String comment = getComment(env, method);

        sb.append("        {\n");
        sb.append("          \"name\": ").append(jsonStr(name)).append(",\n");
        sb.append("          \"signature\": ").append(jsonStr(signature)).append(",\n");
        sb.append("          \"comment\": ").append(jsonStr(comment)).append(",\n");

        // 参数
        sb.append("          \"parameters\": [");
        List<? extends VariableElement> params = method.getParameters();
        List<String> paramComments = extractParamComments(comment);

        for (int i = 0; i < params.size(); i++) {
            VariableElement param = params.get(i);
            String paramName = param.getSimpleName().toString();
            String paramType = param.asType().toString();
            String pComment = (i < paramComments.size()) ? paramComments.get(i) : "";

            sb.append("\n            {\n");
            sb.append("              \"name\": ").append(jsonStr(paramName)).append(",\n");
            sb.append("              \"type\": ").append(jsonStr(paramType)).append(",\n");
            sb.append("              \"comment\": ").append(jsonStr(pComment)).append("\n");
            sb.append("            }");
            if (i < params.size() - 1) sb.append(",");
        }
        if (!params.isEmpty()) sb.append("\n          ");
        sb.append("],\n");

        // 返回值
        TypeMirror returnType = method.getReturnType();
        String returnComment = extractReturnComment(comment);

        sb.append("          \"returns\": {\n");
        sb.append("            \"type\": ").append(jsonStr(returnType.toString())).append(",\n");
        sb.append("            \"comment\": ").append(jsonStr(returnComment)).append("\n");
        sb.append("          }\n");

        sb.append("        }");
    }

    private static String buildSignature(DocletEnvironment env, ExecutableElement method) {
        StringBuilder sb = new StringBuilder();
        TypeMirror returnType = method.getReturnType();
        sb.append(typeSimpleName(returnType)).append(" ");
        sb.append(method.getSimpleName().toString()).append("(");
        List<? extends VariableElement> params = method.getParameters();
        for (int i = 0; i < params.size(); i++) {
            sb.append(typeSimpleName(params.get(i).asType()));
            sb.append(" ").append(params.get(i).getSimpleName().toString());
            if (i < params.size() - 1) sb.append(", ");
        }
        sb.append(")");
        return sb.toString();
    }

    private static String typeSimpleName(TypeMirror type) {
        String s = type.toString();
        int dot = s.lastIndexOf('.');
        return dot >= 0 ? s.substring(dot + 1) : s;
    }

    private static String getKindString(ElementKind kind) {
        switch (kind) {
            case CLASS:    return "class";
            case INTERFACE: return "interface";
            case ENUM:     return "enum";
            case RECORD:   return "record";
            default:       return "class";
        }
    }

    private static String getComment(DocletEnvironment env, Element element) {
        String doc = env.getElementUtils().getDocComment(element);
        return doc != null ? doc.trim() : "";
    }

    private static List<String> extractParamComments(String doc) {
        List<String> comments = new ArrayList<>();
        if (doc == null) return comments;
        for (String line : doc.split("\n")) {
            line = line.trim();
            if (line.startsWith("@param ")) {
                String rest = line.substring(7).trim();
                int spaceIdx = rest.indexOf(' ');
                comments.add(spaceIdx > 0 ? rest.substring(spaceIdx + 1).trim() : "");
            }
        }
        return comments;
    }

    private static String extractReturnComment(String doc) {
        if (doc == null) return "";
        for (String line : doc.split("\n")) {
            line = line.trim();
            if (line.startsWith("@return ") || line.startsWith("@returns ")) {
                return line.substring(line.indexOf(' ') + 1).trim();
            }
        }
        return "";
    }

    private static String jsonStr(String s) {
        if (s == null) return "\"\"";
        StringBuilder sb = new StringBuilder().append("\"");
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"':  sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:   sb.append(c);
            }
        }
        return sb.append("\"").toString();
    }
}
