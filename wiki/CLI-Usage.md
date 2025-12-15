# CLI Usage

## Commands

### scan

Scan Swift files for deprecated APIs and fragile patterns.

```bash
swiftui-migrate scan <paths>
```

### rules

List all available detection rules.

```bash
swiftui-migrate rules
```

## Basic Scanning

### Scan a file

```bash
swiftui-migrate scan MyView.swift
```

### Scan a directory

```bash
swiftui-migrate scan Sources/
```

### Scan multiple paths

```bash
swiftui-migrate scan Sources/ Tests/ Examples/
```

### Exclude directories

```bash
swiftui-migrate scan . --exclude Pods --exclude Build
```

## Output Modes

### Human-readable (default)

```bash
swiftui-migrate scan Sources/
```

Shows formatted output with colors, code snippets, and suggestions.

### JSON

```bash
swiftui-migrate scan Sources/ --json
```

Machine-readable output for CI/CD and tooling integration.

**JSON structure:**

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
      "message": "NavigationView is deprecated in iOS 16+.",
      "category": "deprecated",
      "severity": "warning"
    }
  ]
}
```

## Filtering

### By iOS version

```bash
# Only iOS 16+ issues
swiftui-migrate scan Sources/ --min-ios 16

# Only iOS 17+ issues
swiftui-migrate scan Sources/ --min-ios 17
```

### By category

```bash
# Only deprecated APIs
swiftui-migrate scan Sources/ --category deprecated

# Only fragile patterns
swiftui-migrate scan Sources/ --category fragile
```

### By severity

```bash
# Only errors
swiftui-migrate scan Sources/ --severity error

# Only warnings
swiftui-migrate scan Sources/ --severity warning
```

## Grouping

### By file (default)

```bash
swiftui-migrate scan Sources/
```

Shows findings organized by file.

### By rule

```bash
swiftui-migrate scan Sources/ --group-by rule
```

Shows which patterns appear most frequently.

### By category

```bash
swiftui-migrate scan Sources/ --group-by category
```

Separates deprecated APIs from fragile patterns.

### No grouping (flat)

```bash
swiftui-migrate scan Sources/ --group-by none
```

Simple list format, one issue per line.

## Exit Codes

| Scenario | Exit Code | Default Behavior |
|----------|-----------|------------------|
| No issues | 0 | Pass |
| Only fragile patterns | 0 | Pass (warnings) |
| Any deprecated APIs | 1 | Fail |
| Both types | 1 | Fail |

### Strict mode

Fail on any issue (including fragile patterns):

```bash
swiftui-migrate scan Sources/ --fail-on-fragile
```

## Annotation Mode

Write inline comments into Swift files (modifies files):

```bash
# Annotate files
swiftui-migrate scan Sources/ --annotate

# Create backups first
swiftui-migrate scan Sources/ --annotate --backup
```

See **[Annotation Mode](Annotation-Mode)** for details.

## Example Output

### Text format

```
swiftui-migrate v0.1.0

Sources/HomeView.swift
  15:8 NAV001: NavigationView is deprecated in iOS 16+.
  NavigationView {
  Suggestion: Replace with NavigationStack
  (Requires iOS 16.0+)

  42:12 FRAG001: NavigationLink with isActive: can cause issues
  NavigationLink(destination: DetailView(), isActive: $show) {
  Suggestion: Use NavigationStack with navigationDestination
  (Requires iOS 16.0+)

────────────────────────────────────────────────────────────
Summary
────────────────────────────────────────────────────────────
Files scanned:    12
Total issues:     8
  Deprecated:     5
  Fragile:        3
────────────────────────────────────────────────────────────
```

## Complete Flag Reference

```
Options:
  --json                          Output as JSON
  --min-ios N                     Only show iOS N+ issues
  --severity [warning|error|all]  Filter by severity
  --category [deprecated|fragile|all]  Filter by category
  --group-by [file|rule|category|none]  Group results
  --exclude PATTERN               Exclude directories (repeatable)
  --fail-on-fragile              Exit 1 on any issue
  --annotate                     Write comments into Swift files
  --backup                       Create .bak backups (requires --annotate)
  --help                         Show help message
```
