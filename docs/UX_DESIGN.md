# CLI UX Design Document

## Design Goals

### 1. Professional and Calm

**Problem**: Many linters use aggressive, emoji-heavy output that creates alert fatigue.

**Solution**: 
- No emojis in output
- No alarmist language ("ERROR!", "CRITICAL!", etc.)
- Neutral, informative messaging
- Clean typography using standard characters

**Before** (emoji-heavy):
```
🔧 FRAGILE PATTERNS 🔧
⚠️ WARNING Line 15: NavigationLink...
```

**After** (professional):
```
Fragile Patterns
────────────────────────────────────────────────────────────
  15:8 FRAG001: NavigationLink with isActive: can cause...
```

### 2. Clear File:Line Format

**Problem**: Inconsistent location formats make it hard to jump to issues in IDEs.

**Solution**: Standard `file:line:column` format, clickable in most terminals and IDEs.

**Format**:
```
/path/to/file.swift:15:8 RULE_ID: Message
```

**Benefits**:
- CMD+click works in most terminals
- Grep-friendly
- IDE-friendly (Xcode, VS Code, etc.)
- Consistent with compiler output

### 3. Summary-First Information Architecture

**Problem**: Users need quick answers: "How many issues? What categories?"

**Solution**: Clear summary at the end of every scan.

```
────────────────────────────────────────────────────────────
Summary
────────────────────────────────────────────────────────────
Files scanned:    42
Total issues:     15
  Deprecated:     10
  Fragile:        5
────────────────────────────────────────────────────────────
```

**Key metrics**:
1. Files scanned (scope awareness)
2. Total issues (high-level health)
3. Category breakdown (deprecated vs fragile)

### 4. CI-Friendly JSON Mode

**Problem**: CI/CD pipelines need structured, parseable output.

**Solution**: `--json` flag outputs clean JSON with no terminal formatting.

**Structure**:
```json
{
  "version": "0.1.0",
  "files_scanned": 42,
  "summary": {
    "total": 15,
    "deprecated": 10,
    "fragile": 5
  },
  "findings": [
    {
      "rule_id": "NAV001",
      "file_path": "/path/to/file.swift",
      "line_number": 15,
      "column": 8,
      "message": "...",
      "category": "deprecated"
    }
  ]
}
```

## Output Modes

### Text Mode (Default)

**Use case**: Daily development, terminal usage

**Features**:
- Readable formatting with Rich library
- Grouped by file (default) or rule/category
- Inline code snippets
- Migration suggestions
- Summary section

**Example**:
```
swiftui-migrate v0.1.0

Sources/MyView.swift
  15:8 NAV001: NavigationView is deprecated in iOS 16+.
  NavigationView {
  Suggestion: Replace with NavigationStack
  (Requires iOS 16.0+)

────────────────────────────────────────────────────────────
Summary
────────────────────────────────────────────────────────────
Files scanned:    1
Total issues:     1
  Deprecated:     1
  Fragile:        0
────────────────────────────────────────────────────────────
```

### JSON Mode

**Use case**: CI/CD, tooling integration

**Features**:
- No terminal formatting
- Structured data
- Includes version for compatibility
- Summary object for quick metrics

**Activation**:
```bash
swiftui-migrate scan Sources/ --json
```

## Grouping Options

### By File (Default)

**Best for**: Fixing issues file-by-file

```
Sources/ViewA.swift
  10:4 NAV001: NavigationView is deprecated
  15:8 FRAG001: NavigationLink isActive pattern

Sources/ViewB.swift
  20:12 ENV001: presentationMode is deprecated
```

### By Rule

**Best for**: Understanding which patterns are most common

```
NAV001 NavigationView deprecated
  Sources/ViewA.swift:10:4
  Sources/ViewB.swift:5:8
  Sources/ViewC.swift:30:12

FRAG001 NavigationLink isActive pattern
  Sources/ViewA.swift:15:8
```

### By Category

**Best for**: Separating deprecated vs fragile issues

```
Deprecated APIs
────────────────────────────────────────────────────────────
Sources/ViewA.swift
  10:4 NAV001: NavigationView is deprecated

Fragile Patterns
────────────────────────────────────────────────────────────
Sources/ViewA.swift
  15:8 FRAG001: NavigationLink isActive pattern
```

### None (Flat)

**Best for**: Grep/parsing, minimal output

```
Sources/ViewA.swift:10:4 NAV001: NavigationView is deprecated
Sources/ViewA.swift:15:8 FRAG001: NavigationLink isActive...
Sources/ViewB.swift:20:12 ENV001: presentationMode...
```

## Exit Code Behavior

### Default Mode (Developer-Friendly)

**Philosophy**: Don't block development for informational warnings.

| Findings | Exit Code | Reason |
|----------|-----------|--------|
| None | 0 | All clear |
| Fragile only | 0 | Warnings, not blockers |
| Deprecated only | 1 | Requires action |
| Both | 1 | Deprecated triggers failure |

### Strict Mode (`--fail-on-fragile`)

**Philosophy**: Enforce code quality standards.

| Findings | Exit Code |
|----------|-----------|
| None | 0 |
| Any issue | 1 |

**Use case**: Teams with strict coding standards, pre-release checks.

```bash
swiftui-migrate scan Sources/ --fail-on-fragile
```

## Filtering

### By iOS Version (`--min-ios`)

**Use case**: Incremental migration planning.

```bash
# Focus on iOS 16 migration
swiftui-migrate scan Sources/ --min-ios 16

# Only iOS 17 issues
swiftui-migrate scan Sources/ --min-ios 17
```

**Behavior**: Filters rules by their `ios_version` field. Only shows issues for iOS >= specified version.

### By Category (`--category`)

**Use case**: Focus on specific issue types.

```bash
# Only deprecated APIs (hard blockers)
swiftui-migrate scan Sources/ --category deprecated

# Only fragile patterns (code quality)
swiftui-migrate scan Sources/ --category fragile
```

### By Severity (`--severity`)

**Use case**: Future-proofing for error vs warning rules.

```bash
# Only errors
swiftui-migrate scan Sources/ --severity error
```

## Typography and Formatting

### Rules

1. **No emojis** - Professional environments may filter them
2. **Use ASCII box drawing** - `─` (U+2500) instead of `═` for compatibility
3. **Bold for emphasis** - Headers, rule IDs
4. **Dim for metadata** - Code snippets, helper text
5. **Standard spacing** - 2-space indentation for clarity

### Color Palette

- **Bold** - Headers, important info
- **Dim** - Metadata, less important info
- No red/yellow severity colors - avoid anxiety

### Layout

```
<header>

<grouped findings>
  <file or rule>
    <line:col rule_id: message>
    <code snippet (dim)>
    <suggestion>
    <metadata (dim)>

<separator line>
<summary>
  <key metrics>
<separator line>
```

## Information Hierarchy

### Primary Information
1. File path
2. Line:column
3. Rule ID
4. Message

### Secondary Information
1. Code snippet
2. Migration suggestion
3. iOS version requirement

### Tertiary Information
1. Summary metrics
2. Version number

## Example Outputs

### Clean Success

```
swiftui-migrate v0.1.0

No issues found.
```

### Single File Scan

```
swiftui-migrate v0.1.0

Sources/MyView.swift
  15:8 NAV001: NavigationView is deprecated in iOS 16+.
  NavigationView {
  Suggestion: Replace with NavigationStack
  (Requires iOS 16.0+)

────────────────────────────────────────────────────────────
Summary
────────────────────────────────────────────────────────────
Files scanned:    1
Total issues:     1
  Deprecated:     1
  Fragile:        0
────────────────────────────────────────────────────────────
```

### Category Grouping

```
swiftui-migrate v0.1.0

Deprecated APIs
────────────────────────────────────────────────────────────

Sources/ViewA.swift
  10:4 NAV001: NavigationView is deprecated in iOS 16+.
  NavigationView {
  Suggestion: Replace with NavigationStack

Fragile Patterns
────────────────────────────────────────────────────────────

Sources/ViewA.swift
  15:8 FRAG001: NavigationLink with isActive: can cause issues
  NavigationLink(destination: X, isActive: $show) {
  Suggestion: Use NavigationStack with navigationDestination

────────────────────────────────────────────────────────────
Summary
────────────────────────────────────────────────────────────
Files scanned:    2
Total issues:     2
  Deprecated:     1
  Fragile:        1
────────────────────────────────────────────────────────────
```

## Design Decisions

### Why No Emojis?

1. **Professionalism** - Corporate environments prefer clean output
2. **Accessibility** - Screen readers struggle with emojis
3. **Consistency** - Emoji rendering varies by terminal
4. **Compatibility** - Some CI systems strip emojis

### Why file:line:column Format?

1. **IDE Integration** - Clickable in terminals
2. **Industry Standard** - Matches compiler output
3. **Grep-Friendly** - Easy to parse
4. **Universal** - Works across all platforms

### Why Summary at End?

1. **Scanability** - Users can quickly check health
2. **CI Parsing** - Last lines are easy to extract
3. **Context** - Shows scope of scan (files scanned)

### Why Two Categories?

1. **Different Actions** - Deprecated = must fix, Fragile = should fix
2. **CI Strategy** - Block on deprecated, warn on fragile
3. **Team Flexibility** - Different enforcement levels

## Accessibility

- **No color-only information** - All info available in text
- **Clear hierarchy** - Indentation and formatting create structure
- **Consistent formatting** - Patterns are predictable
- **Screen reader friendly** - No emoji clutter

## Future Enhancements

1. **Markdown output** - For PR comments
2. **SARIF format** - For GitHub Code Scanning
3. **HTML report** - For documentation
4. **Watch mode** - Real-time scanning
5. **Interactive mode** - Apply fixes interactively
