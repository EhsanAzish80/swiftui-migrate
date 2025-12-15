# swiftui-migrate

A Python CLI tool that scans Swift/SwiftUI code for deprecated APIs and fragile patterns.

## What It Does

Scans your Swift files using regex patterns and reports:

1. **Deprecated APIs** - Officially deprecated by Apple (iOS 14-17)
2. **Fragile Patterns** - Not deprecated, but known to cause issues

For each finding:
- File location (`file.swift:line:column`)
- What's wrong
- How to fix it
- Minimum iOS version for the fix

## Quick Start

```bash
# Install
pip install click rich
git clone https://github.com/EhsanAzish80/swiftui-migrate.git
cd swiftui-migrate
pip install -e .

# Scan a directory
swiftui-migrate scan Sources/

# Output as JSON for CI
swiftui-migrate scan Sources/ --json
```

## Example Output

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
Files scanned:    12
Total issues:     8
  Deprecated:     5
  Fragile:        3
────────────────────────────────────────────────────────────
```

## Documentation

**📚 Full documentation lives in the [Wiki](https://github.com/EhsanAzish80/swiftui-migrate/wiki)**

- [Installation](https://github.com/EhsanAzish80/swiftui-migrate/wiki/Installation)
- [CLI Usage](https://github.com/EhsanAzish80/swiftui-migrate/wiki/CLI-Usage)
- [Deprecated API Rules](https://github.com/EhsanAzish80/swiftui-migrate/wiki/Deprecated-API-Rules)
- [Fragile Pattern Rules](https://github.com/EhsanAzish80/swiftui-migrate/wiki/Fragile-Pattern-Rules)
- [Annotation Mode](https://github.com/EhsanAzish80/swiftui-migrate/wiki/Annotation-Mode) (--annotate flag)
- [CI Integration](https://github.com/EhsanAzish80/swiftui-migrate/wiki/CI-Integration)
- [Roadmap](https://github.com/EhsanAzish80/swiftui-migrate/wiki/Roadmap)

## Exit Codes

- **0** - No issues or only fragile patterns (warnings)
- **1** - Deprecated APIs found (fails CI by default)

Use `--fail-on-fragile` to fail CI on any issue.

## Philosophy

This tool is boring in the best possible way:

- No AI
- No magic
- No hype
- Just straightforward pattern matching

It does one thing: find deprecated and fragile SwiftUI code.

## License

MIT
