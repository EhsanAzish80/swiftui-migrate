# CLI Quick Reference

## Commands

```bash
# Scan files
swiftui-migrate scan <path> [options]

# List all rules
swiftui-migrate rules
```

## Essential Options

| Option | Description | Example |
|--------|-------------|---------|
| `--json` | Output as JSON for CI | `scan Sources/ --json` |
| `--min-ios N` | Only show iOS N+ issues | `scan Sources/ --min-ios 16` |
| `--category TYPE` | Filter: deprecated\|fragile\|all | `scan Sources/ --category deprecated` |
| `--group-by MODE` | Group: file\|rule\|category\|none | `scan Sources/ --group-by category` |
| `--fail-on-fragile` | Fail CI on fragile patterns | `scan Sources/ --fail-on-fragile` |
| `--exclude PATTERN` | Exclude directories | `scan . --exclude Pods` |

## Common Workflows

### Daily Development
```bash
# Quick check
swiftui-migrate scan MyView.swift

# Pre-commit
git diff --cached --name-only | grep '\.swift$' | xargs swiftui-migrate scan
```

### Migration Planning
```bash
# iOS 16 migration
swiftui-migrate scan Sources/ --min-ios 16 --group-by rule

# iOS 17 migration
swiftui-migrate scan Sources/ --min-ios 17
```

### CI/CD
```bash
# GitHub Actions
swiftui-migrate scan Sources/ --json > results.json

# Check deprecated APIs only
swiftui-migrate scan Sources/ --category deprecated

# Strict mode (fail on everything)
swiftui-migrate scan Sources/ --fail-on-fragile
```

### Code Quality
```bash
# Audit fragile patterns (won't fail)
swiftui-migrate scan Sources/ --category fragile

# See both categories separately
swiftui-migrate scan Sources/ --group-by category
```

## Output Formats

### Human-Readable (Default)
```
swiftui-migrate v0.1.0

/path/to/file.swift
  15:8 NAV001: NavigationView is deprecated in iOS 16+.
  NavigationView {
  Suggestion: Replace with NavigationStack
  (Requires iOS 16.0+)

────────────────────────────────────────────────────────────
Summary
────────────────────────────────────────────────────────────
Files scanned:    42
Total issues:     15
  Deprecated:     10
  Fragile:        5
────────────────────────────────────────────────────────────
```

### JSON (for CI)
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

## Exit Codes

| Scenario | Exit Code |
|----------|-----------|
| No issues | 0 |
| Fragile only | 0 |
| Deprecated found | 1 |
| With --fail-on-fragile | 1 (if any issues) |

## Examples

```bash
# Scan current directory
swiftui-migrate scan .

# Scan with exclusions
swiftui-migrate scan . --exclude Pods --exclude Build

# JSON output
swiftui-migrate scan Sources/ --json

# Filter iOS 16+ issues
swiftui-migrate scan Sources/ --min-ios 16

# Show only deprecated APIs
swiftui-migrate scan Sources/ --category deprecated

# Group by category (deprecated vs fragile)
swiftui-migrate scan Sources/ --group-by category

# Group by rule type
swiftui-migrate scan Sources/ --group-by rule

# Strict mode (fail on fragile too)
swiftui-migrate scan Sources/ --fail-on-fragile

# Multiple filters combined
swiftui-migrate scan Sources/ --min-ios 16 --category deprecated --group-by rule
```

## Parsing JSON Output

```bash
# Extract summary
swiftui-migrate scan Sources/ --json | jq '.summary'

# Count deprecated APIs
swiftui-migrate scan Sources/ --json | jq '.summary.deprecated'

# List all affected files
swiftui-migrate scan Sources/ --json | jq -r '.findings[].file_path' | sort -u

# Group by rule
swiftui-migrate scan Sources/ --json | jq -r '.findings[] | "\(.rule_id): \(.message)"' | sort | uniq -c

# Find specific rule
swiftui-migrate scan Sources/ --json | jq '.findings[] | select(.rule_id == "NAV001")'
```

## CI Integration Examples

### GitHub Actions
```yaml
- name: SwiftUI Scan
  run: swiftui-migrate scan Sources/ --json > results.json

- name: Check Results
  run: |
    DEPRECATED=$(jq '.summary.deprecated' results.json)
    [ "$DEPRECATED" -gt 0 ] && exit 1 || exit 0
```

### GitLab CI
```yaml
swiftui-check:
  script:
    - swiftui-migrate scan Sources/ --json > results.json
  artifacts:
    paths:
      - results.json
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
git diff --cached --name-only --diff-filter=ACM | \
  grep '\.swift$' | \
  xargs swiftui-migrate scan --category deprecated
```

## Tips

1. Use `--min-ios` during incremental migrations
2. Use `--category fragile` for code quality audits
3. Use `--json` in CI for structured output
4. Use `--group-by category` to separate concerns
5. Add `--fail-on-fragile` when ready for strict enforcement
6. Exclude build artifacts with `--exclude Build --exclude Pods`
