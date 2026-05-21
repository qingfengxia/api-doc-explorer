## TypeScript API Explorer

For TypeScript projects, the skill leverages **TypeDoc** to generate documentation in JSON format, which is then queried by the **`typescript-api-explorer`** CLI tool.

## How to Generate Docs for a TypeScript Project

Below is the step-by-step process for adding documentation to a TypeScript project that currently has none.

### 1. Install TypeDoc

```bash
npm install --save-dev typedoc
```

### 2. (Optional) Create `typedoc.json`

TypeDoc can discover many settings from your existing `tsconfig.json`, but for explicit control, create a `typedoc.json` in the project root:

```json
{
  "$schema": "https://typedoc.org/schema.json",
  "entryPoints": ["src/index.ts"],
  "out": "docs",
  "json": "docs/api-docs.json",
  "excludeInternal": true,
  "excludePrivate": true,
  "readme": "none"
}
```

| Field | Purpose |
|---|---|
| `entryPoints` | One or more entry files TypeDoc should analyze. Use a barrel file (e.g. `src/index.ts`) to capture all exports, or list multiple files. |
| `out` | Directory where the HTML documentation will be generated. |
| `json` | **(Required by this skill)** Path to the JSON output file that `typescript-api-explorer` will read. |
| `excludeInternal` | Skip symbols marked `@internal`. |
| `excludePrivate` | Skip `private` members. |

> **Tip**: If you don't create `typedoc.json`, TypeDoc will use sensible defaults based on `tsconfig.json` and generate HTML only (no JSON). To produce JSON output you must specify `--json <path>` or add the `"json"` field to `typedoc.json`.

### 3. Ensure `tsconfig.json` has the right `types`

TypeDoc performs full type-checking. If your source code uses Node.js APIs (`console`, `Buffer`, etc.), make sure `tsconfig.json` includes `"types": ["node"]` and `@types/node` is installed:

```json
{
  "compilerOptions": {
    "types": ["node"]
  }
}
```

```bash
npm install --save-dev @types/node
```

### 4. Add TypeDoc JSDoc Annotations

Document your public API using standard JSDoc tags. TypeDoc understands these annotations:

```typescript
/**
 * A brief description.
 *
 * @remarks
 * Detailed additional information.
 *
 * @param name - Description of the parameter.
 * @returns Description of the return value.
 * @throws {Error} When something goes wrong.
 * @example
 * ```ts
 * const result = myFunction("hello");
 * ```
 */
```

> **Note**: Members marked `private` are excluded by default. Use `@internal` to hide public-but-internal APIs with `"excludeInternal": true`.

### 5. Run TypeDoc

```bash
npx typedoc
```

This generates:
- `docs/api-docs.json` — the JSON file consumed by `typescript-api-explorer`
- `docs/index.html` and HTML pages — viewable in a browser

### 6. Query with api-explorer

```bash
node path/to/typescript-api-explorer.js --doc-path ./docs/ ClassName.methodName
```

### 7. package the docs

add this lines into project's package.json
```json
  "files": [
    "dist",
    "docs"  // 把 docs 目录加进来
  ],
```

## Example Project

A fully configured example is available at `typescript/example/`. It contains:

- **3 modules**: `UserService`, `LoggerService`, `ProductService` (in a subfolder `src/product/`)
- **`typedoc.json`** configured for multi-entry analysis
- **`package.json`** with `"docs": "typedoc"` script

To regenerate its docs:

```bash
cd typescript/example
npm install
npx typedoc
```

Then explore:

```bash
node ../typescript-api-explorer.js --doc-path ./docs/ UserService.findUser
node ../typescript-api-explorer.js --doc-path ./docs/ ProductService.createProduct
node ../typescript-api-explorer.js --doc-path ./docs/ LoggerService
```
