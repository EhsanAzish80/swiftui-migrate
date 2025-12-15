# CLI Usage Guide

## Design Principles

The swiftui-migrate CLI is designed for:

- **Calm, professional output** - No emojis, no alarmist language
- **Clear file:line formatting** - Easy to parse and click in IDEs
- **CI-friendly** - Clean JSON mode, predictable exit codes
- **Daily developer use** - Fast scanning, focused output

## Commands

### scan

Scan Swift/SwiftUI files for deprecated APIs and fragile patterns.

```bash
swiftui-migrate scan <path> [options]
```

#### Basic Usage

```bash
# Scan a single file
swiftui-migrate scan MyView.swift

# Scan a directory
swiftui-migrate scan Sources/

# Scan multiple paths
swiftui-migrate scan Sources/ Tests/
```

#### Options

##### `--json`
Output as JSON for CI/CD integration.

```bash
swiftui-migrate scan Sources/ --json
```

JSON output structure:
```json
{
  "version": "0.1.0",
  "files_scanned": 42,
  "summary": {
    "total": 15,
    "deprecated": 10,
    "fragile": 5
  },
  "findings": [...]
}
```

##### `--min-ios <version>`
Only show issues for iOS versions >= specified version.

```bash
# Only show iOS 16+ issues
swiftui-migrate scan Sources/ --min-ios 16

# Only show iOS 17+ issues
swiftui-migrate scan Sources/ --min-ios 17
```

##### `--category <deprecated|fragile|all>`
Filter by issue category.

```bash
# Show only deprecated APIs
swiftui-migrate scan Sources/ --category deprecated

# Show only fragile patterns
swiftui-migrate scan Sources/ --category fragile

# Show both (default)
swiftui-migrate scan Sources/
```

##### `--group-by <file|rule|category|none>`
Control output grouping.

```bash
# Group by file (default)
swiftui-migrate scan Sources/ --group-by file

# Group by rule type
swiftui-migrate scan Sources/ --group-by rule

# Group by category (deprecated vs fragile)
swiftui-migrate scan Sources/ --group-by category

# No grouping (flat list)
swiftui-migrate scan Sources/ --group-by none
```

##### `--severity <warning|error|all>`
Filter by severity level.

```bash
# Show only errors
swiftui-migrate scan Sources/ --severity error

# Show only warnings
swiftui-migrate scan Sources/ --severity warning
```

##### `--exclude <pattern>`
Exclude directories (can be used multiple times).

```bash
# Exclude build artifacts
swiftui-migrate scan Sources/ --exclude Build --exclude DerivedData

# Exclude tests
swiftui-migrate scan . --exclude Tests
```

##### `--fail-on-fragile`
Exit with error code if fragile patterns found.

```bash
# Strict mode: fail on any issues
swiftui-migrate scan Sources/ --fail-on-fragile
```

### rules

List all available detection rules.

```bash
swiftui-migrate rules
```

Output:
```
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Rule ID  ┃ Name                         ┃ Category   ┃ iOS        ┃ Message             ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ NAV001   │ NavigationView deprecated    │ Deprecated │ iOS 16     │ NavigationView...  │
│ ENV001   │ presentationMode deprecated  │ Deprecated │ iOS 15     │ @Environment...    │
│ FRAG001  │ NavigationLink isActive      │ Fragile    │ iOS 16     │ NavigationLink...  │
└──────────┴──────────────────────────────┴────────────┴────────────┴─────────────────────┘

Total rules: 10
```

## Output Formats

### Human-Readable (Default)

Clean, scannable output with file:line formatting:

```
swiftui-migrate v0.1.0

Sources/MyView.swift
  15:8 NAV001: NavigationView is deprecated in iOS 16+.
  NavigationView {
  Suggestion: Replace with NavigationStack for simple navigation
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

Structured output for CI/CD pipelines:

```bash
swiftui-migrate scan Sources/ --json | jq '.summary'
```

```json
{
  "total": 15,
  "deprecated": 10,
  "fragile": 5
}
```

## Exit Codes

| Scenario | Default Exit Code | With `--fail-on-fragile` |
|----------|------------------|-------------------------|
| No issues | 0 | 0 |
| Only fragile patterns | 0 | 1 |
| Only deprecated APIs | 1 | 1 |
| Both found | 1 | 1 |

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Scan SwiftUI code
  run: |
    swiftui-migrate scan Sources/ --json > scan-results.json
    
    # Fail build on deprecated APIs only
    # (fragile patterns are warnings)
    swiftui-migrate scan Sources/
```

For strict enforcement of fragile patterns:

```yaml
- name: Scan SwiftUI code (strict)
  run: swiftui-migrate scan Sources/ --fail-on-fragile
```

## Common Workflows

### Pre-commit Hook

Scan only changed files:

```bash
# .git/hooks/pre-commit
#!/bin/bash
git diff --cached --name-only --diff-filter=ACM | \
  grep '\.swift$' | \
  xargs swiftui-migrate scan --category deprecated
```

### Migration Planning

Find iOS 16+ migration work:

```bash
swiftui-migrate scan Sources/ --min-ios 16 --group-by rule
```

### Focus on High-Priority Issues

Show only deprecated APIs (ignore fragile patterns):

```bash
swiftui-migrate scan Sources/ --category deprecated
```

### Generate Migration Report

```bash
swiftui-migrate scan Sources/ --json | \
  jq -r '.findings[] | "\(.file_path):\(.line_number) - \(.rule_id)"' | \
  sort | uniq -c | sort -nr
```

## Tips

1. **Use `--min-ios` during incremental migrations** to focus on one iOS version at a time
2. **Use `--category fragile` to audit code quality** without failing CI
3. **Use `--json` in CI** for structured output and better integration with reporting tools
4. **Use `--group-by category`** to see deprecated vs fragile issues separately
5. **Add `--fail-on-fragile`** when your team is ready for strict enforcement

## Examples

```bash
# Daily development: Quick check
swiftui-migrate scan MyView.swift

# Pre-release: Full scan
swiftui-migrate scan Sources/ --group-by category

# CI/CD: JSON output for reporting
swiftui-migrate scan Sources/ --json > results.json

# Migration project: Focus on iOS 17
swiftui-migrate scan Sources/ --min-ios 17

# Code review: Check fragile patterns
swiftui-migrate scan Sources/ --category fragile

# Strict mode: Fail on everything
swiftui-migrate scan Sources/ --fail-on-fragile
```
